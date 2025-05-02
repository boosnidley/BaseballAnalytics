#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PitcherReport.py
----------------

This script generates a two‐page PDF report for pitcher analysis. Page 1 contains the
primary summary charts and tables, and Page 2 includes additional charts (Swings,
Called Strikes, Whiffs, and Hard Hits over 85 mph) derived from ideas in dashboard.R.
"""

import os
import sys
import math
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge
from matplotlib.lines import Line2D
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import io
import tempfile
import webbrowser

## -----------------------------
## FILE LOADING AND CONVERSION
## -----------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))

# Prompt for Trackman data file
trackman_file = input("Enter Trackman File Path (press Enter for default): ").strip()
if not trackman_file:
    trackman_file = os.path.join(script_dir, "../../All Game CSVs/MalDukaAddColTesting.csv")
    print(f"Default file selected: {trackman_file}")
else:
    trackman_file = os.path.abspath(trackman_file)
    print(f"Trackman File selected: {trackman_file}")

if not os.path.exists(trackman_file):
    print(f"Error: File not found at {trackman_file}")
    sys.exit(1)

# Convert Excel file to CSV if needed
if trackman_file.lower().endswith((".xlsx", ".xls")):
    print("Detected Excel file. Converting to CSV...")
    try:
        excel_data = pd.read_excel(trackman_file)
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        sys.exit(1)
    if "Tilt" in excel_data.columns:
        def fix_tilt_format(value):
            if pd.isna(value) or not isinstance(value, str):
                return value
            parts = value.split(":")
            if len(parts) == 3:
                return f"{parts[0]}:{parts[1]}"
            return value
        excel_data["Tilt"] = excel_data["Tilt"].astype(str).apply(fix_tilt_format)
    csv_path = trackman_file.rsplit(".", 1)[0] + ".csv"
    excel_data.to_csv(csv_path, index=False)
    print(f"Converted and saved CSV file at: {csv_path}")
    trackman_file = csv_path

# Load the data
data = pd.read_csv(trackman_file)

## ----------------------------------------
## UTILITY FUNCTIONS (from original script)
## ----------------------------------------

def tilt_to_minutes(tilt_time):
    if tilt_time is None or not isinstance(tilt_time, str) or ":" not in tilt_time:
        return None
    hours, minutes = map(int, tilt_time.split(":"))
    hours = 0 if hours == 12 else hours
    total_minutes = hours * 60 + minutes
    return total_minutes

def minutes_to_tilt(total_minutes):
    if total_minutes is None:
        return None
    hours = (total_minutes // 60) % 12
    minutes = total_minutes % 60
    return f"{12 if hours == 0 else hours}:{minutes:02d}"

def average_tilt(tilt_values):
    angles = []
    for tilt in tilt_values:
        minutes = tilt_to_minutes(tilt)
        if minutes is not None:
            angle = (minutes / (12 * 60)) * 360
            angles.append(np.deg2rad(angle))
    if not angles:
        return None
    mean_x = np.mean(np.cos(angles))
    mean_y = np.mean(np.sin(angles))
    avg_angle = np.arctan2(mean_y, mean_x)
    if avg_angle < 0:
        avg_angle += 2 * np.pi
    avg_minutes = (np.rad2deg(avg_angle) / 360) * (12 * 60)
    avg_minutes_rounded = int(round(avg_minutes / 15.0) * 15)
    return minutes_to_tilt(round(avg_minutes_rounded))

def classify_pitch_types(data):
    total_pitches = len(data)
    tagged_pitches = data[data["TaggedPitchType"] != "Other"].shape[0]
    sufficient_tagged_data = (tagged_pitches / total_pitches) >= 0.90
    if sufficient_tagged_data:
        pitch_types = set(data["TaggedPitchType"].unique()) - {"Other"}
    else:
        pitch_types = {
            "Fastball": {"Four-Seam", "Two-Seam", "Fastball", "Cutter", "Sinker"},
            "Offspeed": {"Splitter", "Changeup", "Forkball", "Screwball"},
            "Breaking": {"Slider", "Curveball", "Knuckleball", "Sweeper", "Slurve", "Other"}
        }
    return sufficient_tagged_data, pitch_types

def get_pitch_color_map_and_types(data):
    sufficient_tagged_data, pitch_types = classify_pitch_types(data)
    if sufficient_tagged_data:
        color_map = {
            "Fastball": "red",
            "Slider": "yellow",
            "Curveball": "blue",
            "Changeup": "green",
            "Cutter": "mediumorchid",
            "Sinker": "orange",
            "Splitter": "cyan",
            "Knuckleball": "purple",
            "Sweeper": "brown",
            "Slurve": "lime",
            "Forkball": "darkblue",
            "Screwball": "magenta",
            "Other": "gray"
        }
        data["MappedPitchType"] = data["TaggedPitchType"]
    else:
        color_map = {
            "Fastball": "red",
            "Offspeed": "green",
            "Breaking": "blue",
            "Other": "gray"
        }
        def map_pitch_to_category(pitch):
            for category, pitch_set in pitch_types.items():
                if pitch in pitch_set:
                    return category
            return "Other"
        data["MappedPitchType"] = data.apply(
            lambda row: map_pitch_to_category(row["TaggedPitchType"]) if row["TaggedPitchType"] != "Other"
            else map_pitch_to_category(row["AutoPitchType"]),
            axis=1
        )
    return color_map, data

def draw_home_plate(ax):
    home_plate_coords = [
        (-0.71, 0.78),
        (-0.83, 0.6),
        (0.83, 0.6),
        (0.71, 0.78),
        (0.0, 0.9)
    ]
    home_plate = patches.Polygon(home_plate_coords, closed=True,
                                 edgecolor="black", facecolor="white", linewidth=2)
    ax.add_patch(home_plate)

def draw_strike_zone(ax):
    zone_x = -0.83
    zone_y = 1.5
    zone_width = 1.66
    zone_height = 2.0
    shadow_offset_x = 0.03
    shadow_offset_y = -0.03
    small_shadow_rect = patches.Rectangle(
        (zone_x + shadow_offset_x, zone_y + shadow_offset_y),
        zone_width, zone_height,
        fill=True, color="black", alpha=0.1, zorder=1)
    ax.add_patch(small_shadow_rect)
    outer_shadow_expand = 0.1667
    large_shadow_rect = patches.Rectangle(
        (zone_x - outer_shadow_expand, zone_y - outer_shadow_expand),
        zone_width + 2 * outer_shadow_expand,
        zone_height + 2 * outer_shadow_expand,
        fill=True, color="black", alpha=0.05, zorder=0)
    ax.add_patch(large_shadow_rect)
    strike_zone = patches.Rectangle(
        (zone_x, zone_y),
        zone_width, zone_height,
        fill=False, edgecolor='black', linewidth=2, zorder=2)
    ax.add_patch(strike_zone)
    # Draw gridlines
    for i in range(1, 3):
        x = zone_x + i * (zone_width / 3)
        y = zone_y + i * (zone_height / 3)
        ax.plot([x, x], [zone_y, zone_y + zone_height],
                color='gray', linestyle='--', linewidth=1, zorder=3)
        ax.plot([zone_x, zone_x + zone_width], [y, y],
                color='gray', linestyle='--', linewidth=1, zorder=3)

def generate_pitch_color_legend(data):
    required_columns = {"TaggedPitchType", "AutoPitchType"}
    if not required_columns.issubset(data.columns):
        print("Error: Required columns not found in dataset.")
        return None
    color_map, data = get_pitch_color_map_and_types(data)
    pitches_in_data = data["MappedPitchType"].unique()
    fig, ax = plt.subplots(figsize=(1, 2.5))
    for pitch_type in pitches_in_data:
        color = color_map.get(pitch_type, "black")
        ax.scatter([], [], color=color, label=pitch_type)
    ax.legend(title="Pitch Type", loc="center", fontsize=8)
    ax.axis("off")
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return temp_file.name

def generate_pitch_summary_table(data):
    sufficient_tagged_data, pitch_types = classify_pitch_types(data)
    column_mapping = {
        "RelSpeed": ["Max Velo", "Avg Velo"],
        "SpinRate": ["Spin Rate"],
        "InducedVertBreak": ["Max IVB", "Avg IVB"],
        "HorzBreak": ["Max HB", "Avg HB"],
        "Tilt": ["Tilt"],
        "Extension": ["Extension"],
        "VertApprAngle": ["VAA"]
    }
    pitch_stats = {pitch: {"Count": 0} for pitch in (pitch_types if sufficient_tagged_data else pitch_types.keys())}
    for table_col in sum(column_mapping.values(), []):
        for pitch in pitch_stats:
            pitch_stats[pitch][table_col] = None
    for csv_col in column_mapping.keys():
        if csv_col != "Tilt":
            data[csv_col] = pd.to_numeric(data[csv_col], errors="coerce")
    for _, row in data.iterrows():
        if sufficient_tagged_data:
            pitch_type = row["TaggedPitchType"]
        else:
            pitch_type = row["TaggedPitchType"] if row["TaggedPitchType"] != "Other" else row["AutoPitchType"]
            for category, pitch_set in pitch_types.items():
                if pitch_type in pitch_set:
                    pitch_type = category
                    break
        if pitch_type not in pitch_stats:
            continue
        pitch_stats[pitch_type]["Count"] += 1
        for csv_col, table_cols in column_mapping.items():
            value = row[csv_col]
            if pd.notna(value):
                for table_col in table_cols:
                    if pitch_stats[pitch_type][table_col] is None:
                        pitch_stats[pitch_type][table_col] = []
                    pitch_stats[pitch_type][table_col].append(value)
    for pitch, stats in pitch_stats.items():
        for csv_col, table_cols in column_mapping.items():
            for table_col in table_cols:
                if isinstance(stats[table_col], list) and stats[table_col]:
                    if "Max" in table_col:
                        pitch_stats[pitch][table_col] = round(max(stats[table_col], key=abs), 1)
                    elif "Tilt" in table_col:
                        pitch_stats[pitch][table_col] = average_tilt(stats[table_col])
                    else:
                        pitch_stats[pitch][table_col] = round(sum(stats[table_col]) / len(stats[table_col]), 1)
    df_pitch_summary = pd.DataFrame.from_dict(pitch_stats, orient="index").reset_index()
    df_pitch_summary.rename(columns={"index": "Pitch Type"}, inplace=True)
    column_order = ["Pitch Type", "Count", "Max Velo", "Avg Velo", "Spin Rate",
                    "Max IVB", "Max HB", "Avg IVB", "Avg HB", "Tilt", "Extension", "VAA"]
    df_pitch_summary = df_pitch_summary[column_order]
    df_pitch_summary.sort_values(by="Count", ascending=False, inplace=True)
    numeric_cols = df_pitch_summary.select_dtypes(include=['float64']).columns
    df_pitch_summary[numeric_cols] = df_pitch_summary[numeric_cols].round(1)
    return df_pitch_summary

def generate_pitch_location_plot(data):
    required_columns = {"PlateLocHeight", "PlateLocSide", "TaggedPitchType", "AutoPitchType"}
    if not required_columns.issubset(data.columns):
        print("Error: Required columns not found in dataset.")
        return None
    color_map, data = get_pitch_color_map_and_types(data)
    data = data.dropna(subset=["PlateLocHeight", "PlateLocSide"])
    fig, ax = plt.subplots(figsize=(6, 6))
    for pitch_type in data["MappedPitchType"].unique():
        mask = data["MappedPitchType"] == pitch_type
        ax.scatter(data.loc[mask, "PlateLocSide"], data.loc[mask, "PlateLocHeight"],
                   color=color_map.get(pitch_type, "black"), label=pitch_type,
                   alpha=1.0, edgecolors="black", s=70)
    draw_strike_zone(ax)
    draw_home_plate(ax)
    ax.set_xlim(-2, 2)
    ax.set_ylim(0.5, 4.5)
    ax.set_title("Pitch Locations")
    ax.set_xticks([])
    ax.set_yticks([])
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return temp_file.name

def generate_pitch_movement_plot(data):
    required_columns = {"InducedVertBreak", "HorzBreak", "TaggedPitchType", "AutoPitchType"}
    if not required_columns.issubset(data.columns):
        print("Error: Required columns not found in dataset.")
        return None
    color_map, data = get_pitch_color_map_and_types(data)
    data = data.dropna(subset=["InducedVertBreak", "HorzBreak"])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axhline(0, color="black", linewidth=1.2)
    ax.axvline(0, color="black", linewidth=1.2)
    ax.set_xticks(np.arange(-30, 35, 5))
    ax.set_yticks(np.arange(-30, 35, 5))
    for label in ax.get_xticklabels():
        label.set_fontweight("bold")
    for label in ax.get_yticklabels():
        label.set_fontweight("bold")
    ax.set_xlabel("Horizontal Break (inches)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Vertical Break (inches)", fontsize=12, fontweight="bold")
    ax.set_axisbelow(True)
    ax.grid(which='major', color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    for pitch_type in data["MappedPitchType"].unique():
        mask = data["MappedPitchType"] == pitch_type
        sns.kdeplot(x=data.loc[mask, "HorzBreak"], y=data.loc[mask, "InducedVertBreak"], ax=ax,
                    cmap="Blues", fill=True, alpha=0.4, levels=10)
    for pitch_type in data["MappedPitchType"].unique():
        mask = data["MappedPitchType"] == pitch_type
        ax.scatter(data.loc[mask, "HorzBreak"], data.loc[mask, "InducedVertBreak"],
                   color=color_map.get(pitch_type, "black"), label=pitch_type,
                   alpha=1.0, edgecolors="black", s=70)
    max_horz_break = max(abs(data["HorzBreak"].dropna()))
    x_limit = math.ceil(max_horz_break) + 1 if max_horz_break > 20 else 20
    max_vert_break = max(abs(data["InducedVertBreak"].dropna()))
    y_limit = math.ceil(max_vert_break) + 1 if max_vert_break > 20 else 20
    ax.set_xlim(-x_limit, x_limit)
    ax.set_ylim(-y_limit, y_limit)
    ax.set_title("Pitch Movements", fontweight="bold", fontsize=12)
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return temp_file.name

def generate_release_point(data):
    required_columns = {"RelHeight", "RelSide", "TaggedPitchType", "AutoPitchType"}
    if not required_columns.issubset(data.columns):
        print("Error: Required columns not found in dataset.")
        return None
    color_map, data = get_pitch_color_map_and_types(data)
    data = data.dropna(subset=["RelHeight", "RelSide"])
    pitch_x = data["RelSide"]
    pitch_y = data["RelHeight"]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axhline(0, color="black", linewidth=1.2, zorder=1)
    ax.axvline(0, color="black", linewidth=1.2, zorder=1)
    ax.set_xticks(np.arange(-5, 5.1, 0.2))
    ax.set_yticks(np.arange(0, 10.1, 0.1))
    for label in ax.get_xticklabels():
        label.set_fontweight("bold")
    for label in ax.get_yticklabels():
        label.set_fontweight("bold")
    ax.set_axisbelow(True)
    ax.grid(which='major', color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_xlabel("Release Side (ft)", fontsize=20, fontweight="bold")
    ax.set_ylabel("Release Height (ft)", fontsize=20, fontweight="bold")
    pad = 0.05
    x_lower = pitch_x.min() - pad
    x_upper = pitch_x.max() + pad
    y_lower = pitch_y.min() - pad
    y_upper = pitch_y.max() + pad
    ax.set_xlim(x_lower, x_upper)
    ax.set_ylim(y_lower, y_upper)
    ax.set_title("Pitch Release Points", fontweight="bold", fontsize=20)
    for pitch_type in data["MappedPitchType"].unique():
        mask = data["MappedPitchType"] == pitch_type
        ax.scatter(pitch_x[mask], pitch_y[mask],
                   color=color_map.get(pitch_type, "black"), alpha=1.0,
                   edgecolors="black", s=150, zorder=3)
    mean_x = pitch_x.mean()
    mean_y = pitch_y.mean()
    ax.scatter(mean_x, mean_y, color="black", marker="D", s=250,
               edgecolors="black", linewidth=0.8, zorder=5)
    ax.axhline(mean_y, color="black", linewidth=0.8, linestyle="-", zorder=4)
    ax.axvline(mean_x, color="black", linewidth=0.8, linestyle="-", zorder=4)
    avg_label = f"Side = {mean_x:.1f}\nHeight = {mean_y:.1f}"
    diamond_handle = Line2D([], [], color="black", marker="D", linestyle="None",
                              markersize=10, label=avg_label)
    ax.legend(handles=[diamond_handle], loc="upper right", fontsize=14)
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return temp_file.name

## -----------------------------------------------
## NEW FUNCTIONS: ADDITIONAL CHARTS (from dashboard.R)
## -----------------------------------------------

def generate_swings_plot(data):
    # Filter to include only pitches where a swing occurred.
    if "swing" not in data.columns:
        print("Column 'swing' not found in data.")
        return None
    swings = data[data['swing'] == 1]
    if swings.empty:
        print("No swing data available.")
        return None
    color_map, _ = get_pitch_color_map_and_types(data)
    fig, ax = plt.subplots(figsize=(6,6))
    for pt in swings['MappedPitchType'].unique():
        mask = swings['MappedPitchType'] == pt
        ax.scatter(swings.loc[mask, 'PlateLocSide'], swings.loc[mask, 'PlateLocHeight'],
                   color=color_map.get(pt, "black"), label=pt, alpha=1.0, edgecolors="black", s=70)
    draw_strike_zone(ax)
    draw_home_plate(ax)
    ax.set_xlim(-2, 2)
    ax.set_ylim(0.5, 4.5)
    ax.set_title("Swings")
    ax.set_xticks([])
    ax.set_yticks([])
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return temp_file.name

def generate_called_strikes_plot(data):
    # Assume that called strikes are marked by PitchCall == "CalledStrike"
    if "PitchCall" not in data.columns:
        print("Column 'PitchCall' not found in data.")
        return None
    called = data[data['PitchCall'] == "CalledStrike"]
    if called.empty:
        print("No called strike data available.")
        return None
    color_map, _ = get_pitch_color_map_and_types(data)
    fig, ax = plt.subplots(figsize=(6,6))
    for pt in called['MappedPitchType'].unique():
        mask = called['MappedPitchType'] == pt
        ax.scatter(called.loc[mask, 'PlateLocSide'], called.loc[mask, 'PlateLocHeight'],
                   color=color_map.get(pt, "black"), label=pt, alpha=1.0, edgecolors="black", s=70)
    draw_strike_zone(ax)
    draw_home_plate(ax)
    ax.set_xlim(-2, 2)
    ax.set_ylim(0.5, 4.5)
    ax.set_title("Called Strikes")
    ax.set_xticks([])
    ax.set_yticks([])
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return temp_file.name

def generate_whiffs_plot(data):
    # Filter for whiffs by selecting pitches where PitchCall is "StrikeSwinging"
    if "PitchCall" not in data.columns:
        print("Column 'PitchCall' not found in data.")
        return None
    whiffs = data[data['PitchCall'] == "StrikeSwinging"]
    if whiffs.empty:
        print("No whiff data available.")
        return None
    color_map, _ = get_pitch_color_map_and_types(data)
    fig, ax = plt.subplots(figsize=(6,6))
    for pt in whiffs['MappedPitchType'].unique():
        mask = whiffs['MappedPitchType'] == pt
        ax.scatter(whiffs.loc[mask, 'PlateLocSide'], whiffs.loc[mask, 'PlateLocHeight'],
                   color=color_map.get(pt, "black"), label=pt, alpha=1.0, edgecolors="black", s=70)
    draw_strike_zone(ax)
    draw_home_plate(ax)
    ax.set_xlim(-2, 2)
    ax.set_ylim(0.5, 4.5)
    ax.set_title("Whiffs")
    ax.set_xticks([])
    ax.set_yticks([])
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return temp_file.name

def generate_hard_hits_plot(data):
    # Filter for hard hits defined as in-play pitches with ExitSpeed >= 85 mph.
    if "ExitSpeed" not in data.columns or "PitchCall" not in data.columns:
        print("Required columns for hard hits not found in data.")
        return None
    hard_hits = data[(data['ExitSpeed'] >= 85) & (data['PitchCall'] == "InPlay")]
    if hard_hits.empty:
        print("No hard hit data available.")
        return None
    color_map, _ = get_pitch_color_map_and_types(data)
    fig, ax = plt.subplots(figsize=(6,6))
    for pt in hard_hits['MappedPitchType'].unique():
        mask = hard_hits['MappedPitchType'] == pt
        ax.scatter(hard_hits.loc[mask, 'PlateLocSide'], hard_hits.loc[mask, 'PlateLocHeight'],
                   color=color_map.get(pt, "black"), label=pt, alpha=1.0, edgecolors="black", s=70)
    draw_strike_zone(ax)
    draw_home_plate(ax)
    ax.set_xlim(-2, 2)
    ax.set_ylim(0.5, 4.5)
    ax.set_title("Hard Hits (ExitSpeed >= 85 mph)")
    ax.set_xticks([])
    ax.set_yticks([])
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return temp_file.name

## -----------------------------------
## MAIN REPORT GENERATION (PDF)
## -----------------------------------

# Update the data with pitch mapping
color_map, data = get_pitch_color_map_and_types(data)

# Generate primary plots and summaries (Page 1 content)
location_plot = generate_pitch_location_plot(data)
movement_plot = generate_pitch_movement_plot(data)
release_plot = generate_release_point(data)
summary_table = generate_pitch_summary_table(data)  # (This could be incorporated in text/table form)
legend_image = generate_pitch_color_legend(data)

# Generate additional charts (Page 2 content)
swings_img = generate_swings_plot(data)
called_strikes_img = generate_called_strikes_plot(data)
whiffs_img = generate_whiffs_plot(data)
hard_hits_img = generate_hard_hits_plot(data)

# Create the PDF report with two pages
output_pdf = os.path.join(script_dir, "PitcherReport.pdf")
c = canvas.Canvas(output_pdf, pagesize=letter)
width, height = letter

# --- Page 1: Original Report Content ---
c.setFont("Helvetica-Bold", 16)
c.drawString(1*inch, height - 1*inch, "Pitcher Report - Summary")
# For illustration, include two main charts side by side
if location_plot:
    c.drawImage(location_plot, 1*inch, height - 4*inch, width=3*inch, height=3*inch)
if movement_plot:
    c.drawImage(movement_plot, 4.5*inch, height - 4*inch, width=3*inch, height=3*inch)
# (Additional content such as tables or release point plot could be added here.)
c.showPage()

# --- Page 2: Additional Charts from dashboard.R ------------------
c.setFont("Helvetica-Bold", 16)
c.drawString(1*inch, height - 1*inch, "Additional Charts")
# Arrange the four extra charts in a 2 x 2 grid
img_width = 3*inch
img_height = 3*inch
if swings_img:
    c.drawImage(swings_img, 0.5*inch, height - 3.5*inch, width=img_width, height=img_height)
if called_strikes_img:
    c.drawImage(called_strikes_img, 4.5*inch, height - 3.5*inch, width=img_width, height=img_height)
if whiffs_img:
    c.drawImage(whiffs_img, 0.5*inch, height - 7*inch, width=img_width, height=img_height)
if hard_hits_img:
    c.drawImage(hard_hits_img, 4.5*inch, height - 7*inch, width=img_width, height=img_height)
c.showPage()
c.save()

print(f"Pitcher report generated: {output_pdf}")
webbrowser.open(f'file://{output_pdf}')
