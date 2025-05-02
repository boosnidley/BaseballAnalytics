import os
import math
import pandas as pd
import numpy as np
import sys
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
import joypy
import webbrowser
import tempfile

## -- LOAD REPORT -- ##
script_dir = os.path.dirname(os.path.abspath(__file__))

# Prompt user for Trackman file
trackman_file = "../../Game Reports/StevensScoutingReport/Gonzalez_Joe.csv"

OUTPUT_PDF_PATH = "../../Game Reports/StevensScoutingReport/Pitcher Reports/Gonzalez2025-PitchingReport1.pdf"

# if not trackman_file:  # If no file entered, use the default in the script's directory
#     trackman_file = os.path.join(script_dir, "../../Game Reports/KingsGames/LVC_Pitchers/Williams_Michael.csv")
#
#     print(f"Default file selected: {trackman_file}")
# else:
#     trackman_file = os.path.abspath(trackman_file)  # Ensure full absolute path
#     print(f"Trackman File selected: {trackman_file}")

# Validate if the file exists before proceeding
if not os.path.exists(trackman_file):
    print(f"Error: File not found at {trackman_file}")
    sys.exit(1)

# Convert Excel to CSV if needed
if trackman_file.lower().endswith((".xlsx", ".xls")):
    print("Detected Excel file. Converting to CSV...")

    # Load the Excel file
    try:
        excel_data = pd.read_excel(trackman_file)
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        sys.exit(1)

    # If 'Tilt' column exists, ensure it is formatted correctly from HH:MM:SS to HH:MM
    if "Tilt" in excel_data.columns:

        def fix_tilt_format(value):
            """Convert HH:MM:SS to HH:MM by removing seconds."""
            if pd.isna(value) or not isinstance(value, str):
                return value  # Keep NaN values unchanged
            parts = value.split(":")
            if len(parts) == 3:  # HH:MM:SS format detected
                return f"{parts[0]}:{parts[1]}"  # Keep only HH:MM
            return value  # Already in HH:MM


        # Apply function to Tilt column
        excel_data["Tilt"] = excel_data["Tilt"].astype(str).apply(fix_tilt_format)

    # Convert to CSV in the same directory
    csv_path = trackman_file.rsplit(".", 1)[0] + ".csv"
    excel_data.to_csv(csv_path, index=False)

    print(f"Converted and saved CSV file at: {csv_path}")

    # Use the converted CSV file for further processing
    trackman_file = csv_path


## -- FUNCTIONS -- ##
def tilt_to_minutes(tilt_time):
    """Converts a tilt time in HH:MM format to total minutes on a 12-hour modular clock."""
    if tilt_time is None or not isinstance(tilt_time, str) or ":" not in tilt_time:
        return None  # Handle invalid inputs

    hours, minutes = map(int, tilt_time.split(":"))

    # Convert 12-hour format to "modular minutes"
    hours = 0 if hours == 12 else hours  # Convert 12:XX → 0:XX
    total_minutes = hours * 60 + minutes

    return total_minutes


def minutes_to_tilt(total_minutes):
    """Converts total minutes back to a tilt time in HH:MM format."""
    if total_minutes is None:
        return None  # Handle invalid inputs

    hours = (total_minutes // 60) % 12  # Modulo 12-hour clock
    minutes = total_minutes % 60

    # Convert 0 to 12 for the clock display
    tilt_time = f"{12 if hours == 0 else hours}:{minutes:02d}"

    return tilt_time


def average_tilt(tilt_values):
    """Computes the correct average tilt using circular statistics to avoid truncation issues."""
    angles = []

    for tilt in tilt_values:
        minutes = tilt_to_minutes(tilt)
        if minutes is not None:
            angle = (minutes / (12 * 60)) * 360  # Convert minutes to degrees (mod 360)
            angles.append(np.deg2rad(angle))  # Convert degrees to radians

    if not angles:
        return None  # No valid tilt values

    # Compute vector sum to find circular mean
    mean_x = np.mean(np.cos(angles))
    mean_y = np.mean(np.sin(angles))
    avg_angle = np.arctan2(mean_y, mean_x)  # Compute the mean angle

    if avg_angle < 0:
        avg_angle += 2 * np.pi  # Ensure angle is positive

    # Convert back to total minutes on the modular clock
    avg_minutes = (np.rad2deg(avg_angle) / 360) * (12 * 60)
    avg_minutes_rounded = int(round(avg_minutes / 15.0) * 15)

    return minutes_to_tilt(round(avg_minutes_rounded))


def get_pitch_color_map_and_types(data):
    """
    Determines whether there is sufficient tagged pitch data,
    assigns pitch types accordingly, and returns:
      1) color_map (dict)
      2) updated DataFrame with 'MappedPitchType' column

    Parameters:
        data (pd.DataFrame): The DataFrame containing pitch data.

    Returns:
        tuple: (color_map, data)
               - color_map (dict): A dictionary mapping pitch types to colors.
               - data (pd.DataFrame): The updated DataFrame with a 'MappedPitchType' column.
    """
    # Pitch classification
    sufficient_tagged_data, pitch_types = classify_pitch_types(data)

    # Assign color map
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
            lambda row: map_pitch_to_category(row["TaggedPitchType"])
            if row["TaggedPitchType"] != "Other"
            else map_pitch_to_category(row["AutoPitchType"]),
            axis=1
        )

    return color_map, data


def draw_home_plate(ax):
    """
    Draws a home plate outline beneath the strike zone, with a white fill.
    """
    # Shifted plate for aesthetic to document, do not change order!
    home_plate_coords = [
        (-0.71, 0.78),  # Left Top corner
        (-0.83, 0.6),  # Bottom Left corner
        (0.83, 0.6),  # Bottom Right corner
        (0.71, 0.78),  # Right Top corner
        (0.0, 0.9)  # Point
    ]
    # LT -> Point -> RT -> BR -> BL -> LT

    # Create a polygon (white fill, black edge)
    home_plate = patches.Polygon(
        home_plate_coords, closed=True,
        edgecolor="black", facecolor="white", linewidth=2
    )
    ax.add_patch(home_plate)


def draw_strike_zone(ax):
    """
    Draws the strike zone on the provided Axes object with a 9-grid layout,
    including two shadow layers:
      1) A small drop shadow (alpha=0.1) directly behind the zone.
      2) A larger outer shadow (alpha=0.05) extending 2 inches on each side.
    """
    # Strike zone dimensions
    zone_x = -0.83
    zone_y = 1.5    #.83
    zone_width = 1.66
    zone_height = 2.0   #3.5

    # Shadow in zone
    shadow_offset_x = 0.03  # Shift right by 0.03 ft
    shadow_offset_y = -0.03  # Shift down by 0.03 ft
    small_shadow_rect = patches.Rectangle(
        (zone_x + shadow_offset_x, zone_y + shadow_offset_y),
        zone_width, zone_height,
        fill=True,
        color="black",
        alpha=0.1,
        zorder=1  # behind the main zone
    )
    ax.add_patch(small_shadow_rect)

    # Shadow outsize of zone, 2 inches
    outer_shadow_expand = 0.1667
    large_shadow_rect = patches.Rectangle(
        (zone_x - outer_shadow_expand, zone_y - outer_shadow_expand),
        zone_width + 2 * outer_shadow_expand,
        zone_height + 2 * outer_shadow_expand,
        fill=True,
        color="black",
        alpha=0.05,
        zorder=0  # behind small shadow & main zone
    )
    ax.add_patch(large_shadow_rect)

    # Strike zone border
    strike_zone = patches.Rectangle(
        (zone_x, zone_y),
        zone_width, zone_height,
        fill=False,
        edgecolor='black',
        linewidth=2,
        zorder=2
    )
    ax.add_patch(strike_zone)

    # Gridlines
    for i in range(1, 3):
        x = zone_x + i * (zone_width / 3)  # Vertical grid lines
        y = zone_y + i * (zone_height / 3)  # Horizontal grid lines

        # vertical dashed line
        ax.plot(
            [x, x], [zone_y, zone_y + zone_height],
            color='gray', linestyle='--', linewidth=1,
            zorder=3
        )
        # horizontal dashed line
        ax.plot(
            [zone_x, zone_x + zone_width], [y, y],
            color='gray', linestyle='--', linewidth=1,
            zorder=3
        )


def classify_pitch_types(data):
    """
    Determines if there is sufficient tagged pitch data and classifies pitch types accordingly.

    Parameters:
    - data (pd.DataFrame): The dataset containing pitch information.

    Returns:
    - sufficient_tagged_data (bool): True if at least 90% of pitches have TaggedPitchType.
    - pitch_types (set or dict): If sufficient data, returns a set of unique pitch types.
                                 Otherwise, returns a dictionary grouping pitch types.
    """

    total_pitches = len(data)
    tagged_pitches = data[data["TaggedPitchType"] != "Other"].shape[0]
    sufficient_tagged_data = (tagged_pitches / total_pitches) >= 0.90

    if sufficient_tagged_data:
        pitch_types = set(data["TaggedPitchType"].unique()) - {"Other"}  # Auto-detect unique pitch types
    else:
        pitch_types = {
            "Fastball": {"Four-Seam", "Two-Seam", "Fastball", "Cutter", "Sinker"},
            "Offspeed": {"Splitter", "Changeup", "Forkball", "Screwball"},
            "Breaking": {"Slider", "Curveball", "Knuckleball", "Sweeper", "Slurve", "Other"}
        }

    return sufficient_tagged_data, pitch_types


def generate_pitch_color_legend(data):
    """
    Generates and saves a standalone legend image of color-coded pitch types,
    based on whether the data has sufficient tagged pitches or not.

    Parameters:
        data (pd.DataFrame): The DataFrame containing pitch data.

    Returns:
        str: Path to the temporary legend image.
    """
    # Check if required columns exist
    required_columns = {"TaggedPitchType", "AutoPitchType"}
    if not required_columns.issubset(data.columns):
        print("Error: Required columns not found in dataset.")
        return None

    color_map, data = get_pitch_color_map_and_types(data)

    # Get only the pitch types that actually appear in this dataset
    pitches_in_data = data["MappedPitchType"].unique()

    # Create a small figure purely for the legend
    fig, ax = plt.subplots(figsize=(1, 2.5))

    # Loop through pitch types that appear in data, plot invisible points for the legend
    for pitch_type in pitches_in_data:
        color = color_map.get(pitch_type, "black")
        ax.scatter([], [], color=color, label=pitch_type)

    # Create the legend in the center
    ax.legend(title="Pitch Type", loc="center", fontsize=8)
    ax.axis("off")

    # Save to a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)

    return temp_file.name


def generate_pitch_summary_table(data):
    """
    Processes pitch data and generates a summary table in a DataFrame format.

    Parameters:
    - data (pd.DataFrame): The input dataset containing pitch metrics.

    Returns:
    - pd.DataFrame: A cleaned and structured pitch summary table.
    """

    # Call the pitch classification function
    sufficient_tagged_data, pitch_types = classify_pitch_types(data)

    # Define mapping of CSV column headers to table column names
    column_mapping = {
        "RelSpeed": ["Max Velo", "Avg Velo"],
        "SpinRate": ["Spin Rate"],
        "InducedVertBreak": ["Max IVB", "Avg IVB"],
        "HorzBreak": ["Max HB", "Avg HB"],
        "Tilt": ["Tilt"],
        "Extension": ["Extension"],
        "VertApprAngle": ["VAA"]
    }

    # Initialize a dictionary to store stats for each pitch type
    pitch_stats = {pitch: {"Count": 0} for pitch in (pitch_types if sufficient_tagged_data else pitch_types.keys())}

    for table_col in sum(column_mapping.values(), []):  # Flatten the mapping values
        for pitch in pitch_stats:
            pitch_stats[pitch][table_col] = None

    # Ensure relevant columns are numeric (EXCLUDE Tilt)
    for csv_col in column_mapping.keys():
        if csv_col != "Tilt":  # Skip Tilt to prevent conversion to NaN
            data[csv_col] = pd.to_numeric(data[csv_col], errors="coerce")

    # Loop through data and compute values per pitch type
    for _, row in data.iterrows():
        # Determine pitch type based on tagging mode
        if sufficient_tagged_data:
            pitch_type = row["TaggedPitchType"]
        else:
            pitch_type = row["TaggedPitchType"] if row["TaggedPitchType"] != "Other" else row["AutoPitchType"]
            for category, pitch_set in pitch_types.items():
                if pitch_type in pitch_set:
                    pitch_type = category
                    break

        if pitch_type not in pitch_stats:
            continue  # Skip unknown pitch types

        # Increment count
        pitch_stats[pitch_type]["Count"] += 1

        # Collect numerical data for calculations
        for csv_col, table_cols in column_mapping.items():
            value = row[csv_col]
            if pd.notna(value):  # Ignore NaNs
                for table_col in table_cols:
                    if pitch_stats[pitch_type][table_col] is None:
                        pitch_stats[pitch_type][table_col] = []
                    pitch_stats[pitch_type][table_col].append(value)

    # Process collected stats
    for pitch, stats in pitch_stats.items():
        for csv_col, table_cols in column_mapping.items():
            for table_col in table_cols:
                if isinstance(stats[table_col], list) and stats[table_col]:  # If values were collected
                    if "Max" in table_col:
                        pitch_stats[pitch][table_col] = round(max(stats[table_col], key=abs),
                                                              1)  # Fix: Use absolute max
                    elif "Tilt" in table_col:
                        pitch_stats[pitch][table_col] = average_tilt(stats[table_col])
                    else:
                        pitch_stats[pitch][table_col] = round(sum(stats[table_col]) / len(stats[table_col]),
                                                              1)  # Fix: Ensure avg calculation

    # Convert dictionary to DataFrame
    df_pitch_summary = pd.DataFrame.from_dict(pitch_stats, orient="index").reset_index()
    df_pitch_summary.rename(columns={"index": "Pitch Type"}, inplace=True)

    # Define the desired column order for readability
    column_order = [
        "Pitch Type", "Count", "Max Velo", "Avg Velo", "Spin Rate",
        "Max IVB", "Max HB", "Avg IVB", "Avg HB", "Tilt", "Extension", "VAA"
    ]

    # Reorder DataFrame columns and sort by Count
    df_pitch_summary = df_pitch_summary[column_order]
    df_pitch_summary.sort_values(by="Count", ascending=False, inplace=True)

    # Round all numerical columns to 1 decimal place
    numeric_cols = df_pitch_summary.select_dtypes(include=['float64']).columns
    df_pitch_summary[numeric_cols] = df_pitch_summary[numeric_cols].round(1)

    return df_pitch_summary


def generate_pitch_location_plot(data):
    """
    Generates and saves a scatter plot of pitch locations with color-coded pitch types.

    Parameters:
        data (pd.DataFrame): The DataFrame containing pitch data.

    Returns:
        save_path (str): Temporary file at the end of function returned
    """
    # Check if required columns exist
    required_columns = {"PlateLocHeight", "PlateLocSide", "TaggedPitchType", "AutoPitchType"}
    if not required_columns.issubset(data.columns):
        print("Error: Required columns not found in dataset.")
        return None

    color_map, data = get_pitch_color_map_and_types(data)
    data = data.dropna(
        subset=["PlateLocHeight", "PlateLocSide"])  # Remove rows where PlateLocHeight and PlateLocSide are missing

    # Extract pitch locations and processed pitch types
    pitch_x = data["PlateLocSide"]
    pitch_y = data["PlateLocHeight"]
    pitch_types = data["MappedPitchType"]

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(6, 6))

    # Scatter plot with color-coded pitches
    for pitch_type in pitch_types.unique():
        mask = pitch_types == pitch_type
        ax.scatter(pitch_x[mask], pitch_y[mask], color=color_map.get(pitch_type, "black"),
                   label=pitch_type, alpha=1.0, edgecolors="black", s=70)

    # Draw the strike zone with grid
    draw_strike_zone(ax)

    # Draw home plate outline
    draw_home_plate(ax)

    # Formatting
    ax.set_xlim(-2, 2)
    ax.set_ylim(0.5, 4.5)
    ax.set_title("Pitch Locations", fontweight="bold", fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])

    # Create a temporary file for the image
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)

    return temp_file.name  # Return the temporary file path


def generate_pitch_movement_plot(data):
    """
    Generates and saves a scatter plot of pitch movements with color-coded pitch types.

    Parameters:
        data (pd.DataFrame): The DataFrame containing pitch data.

    Returns:
        save_path (str): Temporary file at the end of function returned
    """
    # Check if required columns exist
    required_columns = {"InducedVertBreak", "HorzBreak", "TaggedPitchType", "AutoPitchType"}
    if not required_columns.issubset(data.columns):
        print("Error: Required columns not found in dataset.")
        return None

    color_map, data = get_pitch_color_map_and_types(data)
    data = data.dropna(
        subset=["InducedVertBreak", "HorzBreak"])  # Remove rows where InducedVertBreak and HorzBreak are missing

    # Extract pitch movements and processed pitch types
    pitch_x = data["HorzBreak"]
    pitch_y = data["InducedVertBreak"]
    pitch_types = data["MappedPitchType"]

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(6, 6))

    # Add X and Y Axes with Tick Marks**
    ax.axhline(0, color="black", linewidth=1.2)  # Horizontal axis
    ax.axvline(0, color="black", linewidth=1.2)  # Vertical axis
    ax.set_xticks(np.arange(-30, 35, 5))  # Tick marks every 5 inches
    ax.set_yticks(np.arange(-30, 35, 5))

    # Make tick labels bold
    for label in ax.get_xticklabels():
        label.set_fontweight("bold")

    for label in ax.get_yticklabels():
        label.set_fontweight("bold")

    ax.set_xlabel("Horizontal Break (inches)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Vertical Break (inches)", fontsize=12, fontweight="bold")

    # Dashed gray grid lines behind
    ax.set_axisbelow(True)
    ax.grid(which='major', color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

    # Define a mapping of pitch types to valid colormaps (for heatmaps)
    cmap_map = {
        "Fastball": "Reds",
        "Slider": "YlOrBr",
        "Curveball": "Blues",
        "Changeup": "Greens",
        "Cutter": "Purples",
        "Sinker": "Oranges",
        "Splitter": "PuBu",
        "Knuckleball": "BuPu",
        "Sweeper": "YlGnBu",
        "Slurve": "Reds",
        "Forkball": "PuRd",
        "Screwball": "RdPu",
        "Breaking": "Blues",
        "Offspeed": "Greens",
        "Other": "Greys"
    }

    # Generate heatmaps with corrected colormap names
    for pitch_type in pitch_types.unique():
        mask = pitch_types == pitch_type
        sns.kdeplot(x=pitch_x[mask], y=pitch_y[mask], ax=ax,
                    cmap=cmap_map.get(pitch_type, "Greys"),  # Use valid cmap names
                    fill=True, alpha=0.4, levels=10)

    # Scatter Plot with Color Coding**
    for pitch_type in pitch_types.unique():
        mask = pitch_types == pitch_type
        ax.scatter(pitch_x[mask], pitch_y[mask], color=color_map.get(pitch_type, "black"),
                   label=pitch_type, alpha=1.0, edgecolors="black", s=70)

    # Calculate dynamic x-axis limits
    max_horz_break = max(abs(data["HorzBreak"].dropna()))  # Get max absolute HorzBreak
    x_limit = math.ceil(max_horz_break) + 1 if max_horz_break > 20 else 20  # Round up if needed

    # Calculate dynamic y-axis limits
    max_vert_break = max(abs(data["InducedVertBreak"].dropna()))  # Get max absolute InducedVertBreak
    y_limit = math.ceil(max_vert_break) + 1 if max_vert_break > 20 else 20  # Round up if needed

    # Apply the calculated limits to the plot
    ax.set_xlim(-x_limit, x_limit)
    ax.set_ylim(-y_limit, y_limit)
    ax.set_title("Pitch Movements", fontweight="bold", fontsize=12)

    # Create a Temporary File for the Image**
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)

    return temp_file.name  # Return the temporary file path


def generate_release_point(data):
    """
    Generates and saves a scatter plot of pitch release points with color-coded pitch types.

    Parameters:
        data (pd.DataFrame): The DataFrame containing pitch data.

    Returns:
        save_path (str): Temporary file path to the saved PNG image.
    """
    # Check if required columns exist
    required_columns = {"RelHeight", "RelSide", "TaggedPitchType", "AutoPitchType"}
    if not required_columns.issubset(data.columns):
        print("Error: Required columns not found in dataset.")
        return None

    # Get color map & classify pitches
    color_map, data = get_pitch_color_map_and_types(data)
    data = data.dropna(subset=["RelHeight", "RelSide"])  # Remove rows where RelHeight and RelSide are missing

    # Extract release side, release height, mapped pitch types
    pitch_x = data["RelSide"]
    pitch_y = data["RelHeight"]
    pitch_types = data["MappedPitchType"]

    # Calculate axis limits with 0.25 ft padding
    pad = 0.05
    x_min, x_max = pitch_x.min(), pitch_x.max()
    y_min, y_max = pitch_y.min(), pitch_y.max()

    x_lower = x_min - pad
    x_upper = x_max + pad
    y_lower = y_min - pad
    y_upper = y_max + pad

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(6, 6))

    # Horizontal & vertical reference axes
    ax.axhline(0, color="black", linewidth=1.2, zorder=1)
    ax.axvline(0, color="black", linewidth=1.2, zorder=1)

    # Ticks at 0.2 intervals
    ax.set_xticks(np.arange(-5, 5.1, 0.2))
    ax.set_yticks(np.arange(0, 10.1, 0.1))

    # Adjust tick label font size
    ax.tick_params(axis="x", labelsize=16)  # Change X-axis tick label size
    ax.tick_params(axis="y", labelsize=16)  # Change Y-axis tick label size

    # Make tick labels bold
    for label in ax.get_xticklabels():
        label.set_fontweight("bold")

    for label in ax.get_yticklabels():
        label.set_fontweight("bold")

    # Dashed gray grid lines behind
    ax.set_axisbelow(True)
    ax.grid(which='major', color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

    ax.set_xlabel("Release Side (ft)", fontsize=20, fontweight="bold")
    ax.set_ylabel("Release Height (ft)", fontsize=20, fontweight="bold")

    # Apply the auto-calculated limits
    ax.set_xlim(x_lower, x_upper)
    ax.set_ylim(y_lower, y_upper)
    ax.set_title("Pitch Release Points", fontweight="bold", fontsize=20)

    # Scatter plot with color-coded pitches
    for pitch_type in pitch_types.unique():
        mask = pitch_types == pitch_type
        ax.scatter(
            pitch_x[mask],
            pitch_y[mask],
            color=color_map.get(pitch_type, "black"),
            alpha=1.0,
            edgecolors="black",
            s=150,  # Marker size
            zorder=3
        )

    # Mean release side & height
    mean_x = pitch_x.mean()
    mean_y = pitch_y.mean()

    # Plot black diamond at the mean
    ax.scatter(
        mean_x, mean_y,
        color="black", marker="D", s=250,
        edgecolors="black", linewidth=0.8, zorder=5
    )

    # Draw black cross lines at the mean (vertical & horizontal)
    ax.axhline(mean_y, color="black", linewidth=0.8, alpha=1, linestyle="-", zorder=4)
    ax.axvline(mean_x, color="black", linewidth=0.8, alpha=1, linestyle="-", zorder=4)

    # Legend entry, using diamond as only marker
    avg_label = f"Side = {mean_x:.1f}\nHeight = {mean_y:.1f}"
    diamond_handle = Line2D(
        [], [],
        color="black", marker="D", linestyle="None", markersize=10,
        label=avg_label
    )

    # Display this legend in the top-right corner
    ax.legend(handles=[diamond_handle], loc="upper right", fontsize=14)

    # Save figure to a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)

    return temp_file.name  # Return the temporary file path


def generate_pitch_usage(data):
    """
    Generates and saves a pie chart of pitch usage percentage with color-coded pitch types.

    Parameters:
        data (pd.DataFrame): The DataFrame containing pitch data.

    Returns:
        save_path (str): Temporary file path to the saved PNG image.
    """
    # Check if required columns exist
    required_columns = {"TaggedPitchType", "AutoPitchType"}
    if not required_columns.issubset(data.columns):
        print("Error: Required columns not found in dataset.")
        return None

    # Get color map & classify pitches
    color_map, data = get_pitch_color_map_and_types(data)
    pitch_types = data["MappedPitchType"]

    # Calculate pitch usage percentages
    pitch_counts = pitch_types.value_counts()
    pitch_labels = pitch_counts.index
    pitch_sizes = pitch_counts.values
    pitch_colors = [color_map.get(pitch, "gray") for pitch in pitch_labels]  # Assign colors

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(6, 6))

    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        pitch_sizes,
        labels=pitch_labels,
        autopct="%1.1f%%",
        colors=pitch_colors,
        startangle=140,  # Rotate for better alignment
        wedgeprops={"edgecolor": "black", "alpha": 0.5}
    )

    # Style the text labels
    for text in texts:
        text.set_fontsize(12)
        text.set_fontweight("bold")

    for autotext in autotexts:
        autotext.set_fontsize(14)
        autotext.set_fontweight("bold")
        autotext.set_color("black")  # Improve contrast

    # Title formatting
    ax.set_title("Pitch Usage %", fontsize=20, fontweight="bold")

    # Save figure to a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)

    return temp_file.name  # Return the temporary file path


def generate_tilt_range(data):
    """
    Generates and saves a clock image of tilt range with color-coded pitch types,
    oriented so that 12:00 is at the top and angles increase clockwise.
    """

    # Ensure required columns are present
    required_columns = {"Tilt", "TaggedPitchType", "AutoPitchType"}
    if not required_columns.issubset(data.columns):
        print("Error: Required columns not found in dataset.")
        return None

    # Get pitch color mapping and ensure valid Tilt values
    color_map, data = get_pitch_color_map_and_types(data)
    data = data.dropna(subset=["Tilt"])

    # Compute tilt info for each pitch type
    pitch_types_info = {}
    pitch_type_groups = data.groupby("MappedPitchType")["Tilt"]

    for p_type, tilts in pitch_type_groups:
        tilt_values = [t for t in tilts if t and ":" in t]
        avg_str = average_tilt(tilt_values)

        # Convert each tilt to degrees (0° for 12:00, 90° for 3:00, etc.)
        tilt_degs = []
        for t in tilt_values:
            minutes = tilt_to_minutes(t)
            if minutes is not None:
                deg = (minutes / (12 * 60)) * 360
                tilt_degs.append(deg % 360)

        if tilt_degs:
            raw_min_deg = min(tilt_degs)
            raw_max_deg = max(tilt_degs)

            # Check if the range straddles midnight
            if (raw_min_deg <= 60) and (raw_max_deg >= 270):
                # Split tilt_degs into two groups: 6:00–11:45 and 12:00–5:45
                groupA = [x for x in tilt_degs if 180 <= x <= 352.5]
                groupB = [x for x in tilt_degs if 0 <= x <= 172.5]

                if groupA and groupB:
                    new_min_deg = min(groupA)
                    new_max_deg = max(groupB)
                else:
                    new_min_deg = raw_min_deg
                    new_max_deg = raw_max_deg
            else:
                new_min_deg = raw_min_deg
                new_max_deg = raw_max_deg
        else:
            new_min_deg = None
            new_max_deg = None

        pitch_types_info[p_type] = {
            "tilt_degs": tilt_degs,
            "avg_tilt": avg_str,
            "min_deg": new_min_deg,
            "max_deg": new_max_deg,
        }

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title("Tilt Consistency", fontsize=20, fontweight="bold")
    ax.set_aspect("equal")
    ax.axis("off")

    # Draw outer circle
    circle = Circle((0, 0), 1.0, edgecolor="black", facecolor="whitesmoke", linewidth=2)
    ax.add_patch(circle)

    # Draw minor ticks for every 15 minutes
    for minute_mark in range(0, 12 * 60, 15):
        clock_deg = (minute_mark / 720) * 360
        polar_deg = (90 - clock_deg) % 360
        angle_rad = math.radians(polar_deg)
        x_in = 0.95 * math.cos(angle_rad)
        y_in = 0.95 * math.sin(angle_rad)
        x_out = 1.00 * math.cos(angle_rad)
        y_out = 1.00 * math.sin(angle_rad)
        ax.plot([x_in, x_out], [y_in, y_out], color="black", linewidth=1)

    # Label hours 1 through 12
    for hour in range(1, 13):
        clock_deg = (hour % 12) * 30
        polar_deg = (90 - clock_deg) % 360
        angle_rad = math.radians(polar_deg)
        x_label = 0.85 * math.cos(angle_rad)
        y_label = 0.85 * math.sin(angle_rad)
        ax.text(x_label, y_label, str(hour),
                ha="center", va="center", fontsize=14, fontweight="bold")

    # Draw pitch arcs and average tilt lines
    for p_type, info in pitch_types_info.items():
        if not info["tilt_degs"]:
            continue

        c = color_map.get(p_type, "gray")
        min_deg = info["min_deg"]
        max_deg = info["max_deg"]
        avg_str = info["avg_tilt"]

        # Convert average tilt to clock degrees
        avg_minutes = tilt_to_minutes(avg_str)
        avg_deg_clock = (avg_minutes / (12 * 60)) * 360 if avg_minutes is not None else None

        # Draw shadow arc from min_deg to max_deg
        if min_deg is not None and max_deg is not None:
            arc_start = (90 - min_deg) % 360
            arc_end = (90 - max_deg) % 360
            if arc_start > arc_end:
                arc_start, arc_end = arc_end, arc_start

            wedge = Wedge(center=(0, 0), r=0.95,
                          theta1=arc_start, theta2=arc_end,
                          facecolor=c, alpha=0.15, edgecolor=None)
            ax.add_patch(wedge)

        # Draw a line for average tilt
        if avg_deg_clock is not None:
            polar_deg_avg = (90 - avg_deg_clock) % 360
            avg_rad = math.radians(polar_deg_avg)
            x_end = 0.95 * math.cos(avg_rad)
            y_end = 0.95 * math.sin(avg_rad)
            ax.plot([0, x_end], [0, y_end], color=c, linewidth=2)

            # Label near the tip of the line
            x_label = 1.15 * math.cos(avg_rad)
            y_label = 1.15 * math.sin(avg_rad)
            ax.text(x_label, y_label, p_type, color="black",
                    fontsize=12, fontweight="bold", ha="center", va="center")

    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)

    return temp_file.name


def velocity_ridgeline_plot(data):
    """
    Generates a velocity ridgeline plot, color-coded for each pitch type.

    Parameters:
        data (pd.DataFrame): The DataFrame containing pitch data.

    Returns:
        save_path (str): Temporary file path to the saved PNG image.
    """

    # Check if required columns exist
    required_columns = {"RelSpeed", "TaggedPitchType", "AutoPitchType"}
    if not required_columns.issubset(data.columns):
        print("Error: Required columns not found in dataset.")
        return None

    # Classify pitch types & get color map
    color_map, data = get_pitch_color_map_and_types(data)
    data = data.dropna(subset=["RelSpeed"])

    # Create a minimal DataFrame for joypy
    data_ridge = data[["MappedPitchType", "RelSpeed"]].rename(
        columns={"MappedPitchType": "PitchType", "RelSpeed": "Velocity"}
    )

    # Sort pitch types so the ridges appear in a consistent (alphabetical) order
    pitch_types_unique = sorted(data_ridge["PitchType"].unique())

    # Construct a color list in pitch type order
    color_list = [color_map.get(pt, "gray") for pt in pitch_types_unique]

    # Extend the velocity range before plotting
    min_velocity = data_ridge["Velocity"].min()
    max_velocity = data_ridge["Velocity"].max()
    velocity_extension = 3

    x_range = (min_velocity - velocity_extension, max_velocity + velocity_extension)

    fig, axes = joypy.joyplot(
        data_ridge,
        by="PitchType",
        column="Velocity",
        labels=pitch_types_unique,
        color=color_list,
        kind="kde",
        overlap=0.5,
        linewidth=1,
        linecolor="black",
        fill=True,
        alpha=0.5,
        range_style="all",  # Ensures a shared range
        x_range=x_range,  # **Ensures KDE does not get cut off**
        figsize=(36, 12),
    )

    # Dynamically adjust grid lines
    for ax in axes[:-1]:
        new_min, new_max = x_range  # Ensures proper limits
        ax.set_xlim(new_min, new_max)

        # Grid lines - Adjusting for 2.5 mph intervals
        grid_start = float(np.floor(new_min / 2.5) * 2.5)  # Round down to nearest 2.5
        grid_end = float(np.ceil(new_max / 2.5) * 2.5 + 2.5)  # Round up and extend by 2.5

        for x_val in np.arange(grid_start, grid_end, 2.5):
            ax.axvline(x_val, color='gray', linestyle='--', linewidth=0.7, alpha=0.7)

    # Label the x-axis on the bottom subplot
    axes[-1].set_xlabel("Velocity (mph)", fontsize=42, fontweight="bold")
    fig.suptitle("Velocity Consistency", fontsize=49, fontweight="bold")

    # Adjust tick label sizes for readability
    for ax in axes:
        ax.tick_params(axis="x", labelsize=35)
        ax.tick_params(axis="y", labelsize=35)

        # Make tick labels bold
        for label in ax.get_xticklabels():
            label.set_fontweight("bold")

        for label in ax.get_yticklabels():
            label.set_fontweight("bold")

    # Save figure to a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name, bbox_inches="tight", dpi=300)
    plt.close(fig)

    return temp_file.name


def generate_trackman_report(hand_abbreviation, formatted_name, df_pitch_summary, pitch_location_path,
                             pitch_movement_path, legend_path, release_point_path, velocity_ridgeline_path,
                             pitch_usage_path, tilt_range_path, pdf_path=None):
    """Generate a Trackman report PDF with the summary table, auto-centered."""
    # Create a memory buffer for the PDF
    buffer = io.BytesIO()

    # Page settings
    PAGE_WIDTH, PAGE_HEIGHT = letter

    # Create a new PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setTitle("Trackman Pitching Report")

    # Set fonts
    title_font = "Helvetica-Bold"
    title_size = 20
    name_font = "Helvetica"
    name_size = 16

    # Title text
    title_text = "Trackman Pitching Report"
    title_width = c.stringWidth(title_text, title_font, title_size)
    title_x = (PAGE_WIDTH - title_width) / 2

    # Pitcher Name & Handedness text
    name_text = f"{hand_abbreviation} {formatted_name}"
    name_width = c.stringWidth(name_text, name_font, name_size)
    name_x = (PAGE_WIDTH - name_width) / 2

    # Draw title
    c.setFont(title_font, title_size)
    c.drawString(title_x, 750, title_text)

    # Draw Pitcher Name & Handedness
    c.setFont(name_font, name_size)
    c.drawString(name_x, 725, name_text)

    # Convert DataFrame to a list of lists (ReportLab format)
    table_data = [df_pitch_summary.columns.tolist()] + df_pitch_summary.values.tolist()

    # Define column widths based on text size
    column_widths = [55] + [48] * (len(df_pitch_summary.columns) - 1)
    table_width = sum(column_widths)  # Total table width
    table_x = (PAGE_WIDTH - table_width) / 2  # Centered X position

    # Define table
    table = Table(table_data, colWidths=column_widths)

    # Apply table styling
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),  # Header background
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),  # Header text color
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Center-align text
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Bold headers
        ("FONTSIZE", (0, 0), (-1, -1), 10),  # Font size
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),  # Padding for header
        ("GRID", (0, 1), (-1, -1), 0.5, colors.black),  # Grid for data rows only
        ("BOX", (0, 0), (-1, 0), 1, colors.black),  # Border around the entire header (removes internal grid)
    ])

    # Add row coloring for alternating background
    for row in range(1, len(table_data), 2):  # Apply to odd rows (excluding header)
        style.add("BACKGROUND", (0, row), (-1, row), colors.lightgrey)

    # Apply table style
    table.setStyle(style)

    # Table Positioning - Ensure Fixed Distance from Top of Page
    table_top_y = 710  # Fixed Y-position for the top of the table
    table.wrapOn(c, PAGE_WIDTH, PAGE_HEIGHT)
    table_height = table._height  # Get actual table height after wrapping
    table_y = table_top_y - table_height  # Adjust Y to maintain top margin

    # Draw table on PDF
    table.drawOn(c, table_x, table_y)

    # **Draw Legend Image**
    if legend_path:
        image_width = 75
        image_height = 150  # Adjust height
        image_x = 25  # Align on edge of pitch location path
        image_top_y = table_y - 5  # Keep spacing below table
        image_y = image_top_y - image_height  # Adjust for top-left anchoring

        # Draw the image
        c.drawImage(legend_path, image_x, image_y, width=image_width, height=image_height)

    # **Draw Velocity Ridgeline Image**
    if velocity_ridgeline_path:
        image_width = 450  # Adjust width
        image_height = 150  # Adjust height
        image_x = PAGE_WIDTH - 25 - image_width  # Margin + legend image width + 12 points of space
        image_top_y = table_y - 5  # Keep spacing below table
        image_y = image_top_y - image_height  # Adjust for top-left anchoring

        # Draw the image
        c.drawImage(velocity_ridgeline_path, image_x, image_y, width=image_width, height=image_height)

    # **Draw Pitch Location Image**
    if pitch_location_path:
        image_width = 240  # Adjust width
        image_height = 240  # Adjust height
        image_x = 40  # Left Align
        image_top_y = table_y - 5 - 150 - 5  # Keep spacing below table and prior images
        image_y = image_top_y - image_height  # Adjust for top-left anchoring

        # Draw the image
        c.drawImage(pitch_location_path, image_x, image_y, width=image_width, height=image_height)

    # **Draw Pitch Movement Image**
    if pitch_movement_path:
        image_width = 240  # Adjust width
        image_height = 240  # Adjust height
        image_x = PAGE_WIDTH - 40 - image_width  # Align 25 points from the right edge of the page
        image_top_y = table_y - 5 - 150 - 5  # Keep spacing below table and prior images
        image_y = image_top_y - image_height  # Adjust for top-left anchoring

        # Draw the image
        c.drawImage(pitch_movement_path, image_x, image_y, width=image_width, height=image_height)

    # **Draw Release Point Image**
    if pitch_usage_path:
        image_width = 150  # Adjust width
        image_height = 150  # Adjust height
        image_x = 25  # Align 25 points from the right edge of the page
        image_top_y = table_y - 5 - 150 - 5 - 240 - 5  # Keep spacing below table and prior images
        image_y = image_top_y - image_height  # Adjust for top-left anchoring

        # Draw the image
        c.drawImage(pitch_usage_path, image_x, image_y, width=image_width, height=image_height)

    # **Draw Release Point Image**
    if release_point_path:
        image_width = 150  # Adjust width
        image_height = 150  # Adjust height
        image_x = PAGE_WIDTH / 2 - image_width / 2  # Align 25 points from the right edge of the page
        image_top_y = table_y - 5 - 150 - 5 - 240 - 5  # Keep spacing below table and prior images
        image_y = image_top_y - image_height  # Adjust for top-left anchoring

        # Draw the image
        c.drawImage(release_point_path, image_x, image_y, width=image_width, height=image_height)

        # **Draw Tilt Range Image**
    if tilt_range_path:
        image_width = 150  # Adjust width
        image_height = 150  # Adjust height
        image_x = PAGE_WIDTH - 25 - image_width  # Align 25 points from the right edge of the page
        image_top_y = table_y - 5 - 150 - 5 - 240 - 5  # Keep spacing below table and prior images
        image_y = image_top_y - image_height  # Adjust for top-left anchoring

        # Draw the image
        c.drawImage(tilt_range_path, image_x, image_y, width=image_width, height=image_height)

    # Save and display PDF
    c.showPage()
    c.save()

    buffer.seek(0)

    with open(pdf_path, "wb") as f:
        f.write(buffer.getvalue())


## -- Main Script -- ##
# Load the CSV file after all preprocessing
data = pd.read_csv(trackman_file)

# Check if all rows have the same pitcher name and throwing hand
unique_pitchers = data['Pitcher'].unique()
unique_hands = data['PitcherThrows'].unique()

if len(unique_pitchers) == 1 and len(unique_hands) == 1:
    # Extract values
    pitcher_name = unique_pitchers[0]
    pitcher_hand = unique_hands[0]

    # Map "Right" → "RHP", "Left" → "LHP"
    hand_map = {"Right": "RHP", "Left": "LHP"}
    hand_abbreviation = hand_map.get(pitcher_hand, pitcher_hand)  # Default to original if not mapped

    # Reformat name from "Lastname, Firstname" to "Firstname Lastname"
    last_name, first_name = pitcher_name.split(", ")
    formatted_name = f"{first_name} {last_name}"

else:
    print("\nError: Multiple pitchers or throwing hands detected in the file.")

# Run Functions for Report
df_pitch_summary = generate_pitch_summary_table(data)
pitch_location_path = generate_pitch_location_plot(data)
legend_path = generate_pitch_color_legend(data)
pitch_movement_path = generate_pitch_movement_plot(data)
release_point_path = generate_release_point(data)
velocity_ridgeline_path = velocity_ridgeline_plot(data)
pitch_usage_path = generate_pitch_usage(data)
tilt_range_path = generate_tilt_range(data)

# Create Report
generate_trackman_report(hand_abbreviation, formatted_name, df_pitch_summary, pitch_location_path, pitch_movement_path,
                         legend_path, release_point_path, velocity_ridgeline_path, pitch_usage_path, tilt_range_path, OUTPUT_PDF_PATH)