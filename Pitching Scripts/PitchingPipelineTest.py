import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the full dataset
file_path = '../Fall/AllFallCSV/FallScrimmageCSV/AllFallScrimmageData-Xwoba.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# List of pitchers to process (you can modify this to read dynamically from the data)
pitchers = data['Pitcher'].unique()

# Define directory for saving output
output_dir = 'PitcherData-Copy-Original'
os.makedirs(output_dir, exist_ok=True)

# Function to sanitize file/folder names
def sanitize_name(name):
    return name.replace(',', '').replace(' ', '')

# Function to get quadrant based on plate location
def get_quadrant(side, height):
    if side < 0 and height > 2.75:
        return 'A'  # Top Left
    elif side >= 0 and height > 2.75:
        return 'B'  # Top Right
    elif side < 0 and height <= 2.75:
        return 'C'  # Bottom Left
    else:
        return 'D'  # Bottom Right

# Function to plot scatter for given data and save to PNG
def plot_pitches(data, pitcher_folder, file_suffix, marker, title):
    fig, ax = plt.subplots(figsize=(6, 6))

    colors = {'Fastball': 'red', 'Curveball': 'blue', 'Slider': 'yellow', 'Changeup': 'green'}
    pitch_colors = [colors.get(pitch, 'gray') for pitch in data['TaggedPitchType']]
    sizes = np.where(pd.isna(data['ExitSpeed']), 50, np.sqrt(data['ExitSpeed']) * 1)
    hard_hit_marker = data['ExitSpeed'] > 85
    sizes[hard_hit_marker] = 200

    ax.scatter(data['PlateLocSide'][marker], data['PlateLocHeight'][marker],
               c=np.array(pitch_colors)[marker], s=sizes[marker], alpha=0.7, edgecolors='black')

    ax.set_xlabel('Plate Location Side')
    ax.set_ylabel('Plate Location Height')
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 6)
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True)

    # Draw strike zone
    strike_zone = plt.Rectangle((-0.83, 1.5), 1.66, 2.5, fill=False, color='red', linestyle='--')
    ax.add_patch(strike_zone)

    ax.set_title(title)

    # Save plot
    plot_file = os.path.join(pitcher_folder, f'{file_suffix}.pdf')
    plt.savefig(plot_file)
    print(f"Plot saved to {plot_file}")
    plt.close()

# Iterate through each pitcher and process their data
for pitcher in pitchers:
    # Filter data for the current pitcher
    pitcher_data = data[data['Pitcher'] == pitcher]

    # Create a sanitized folder name for the pitcher and create the folder
    sanitized_pitcher_name = sanitize_name(pitcher)
    pitcher_folder = os.path.join(output_dir, sanitized_pitcher_name)
    os.makedirs(pitcher_folder, exist_ok=True)

    # Save the filtered data to a CSV
    pitcher_csv_path = os.path.join(pitcher_folder, f'{sanitized_pitcher_name}_FallPitching.csv')
    pitcher_data.to_csv(pitcher_csv_path, index=False)
    print(f"CSV saved to {pitcher_csv_path}")

    # Extract necessary columns for plotting
    plate_loc_height = pitcher_data['PlateLocHeight']
    plate_loc_side = pitcher_data['PlateLocSide']
    exit_speed = pitcher_data['ExitSpeed']
    pitch_type = pitcher_data['TaggedPitchType']
    pitch_called = pitcher_data['PitchCall']

    # Define markers for different conditions
    hard_hit_marker = exit_speed > 85
    ball_called = pitch_called == 'BallCalled'
    strike_swinging = pitch_called == 'StrikeSwinging'
    strike_called = pitch_called == 'StrikeCalled'
    normal_hit_ball = exit_speed < 85

    # Generate and save scatter plots for different pitch categories
    plot_pitches(pitcher_data, pitcher_folder, 'NormalPitches', normal_hit_ball, 'Normal Pitches')
    plot_pitches(pitcher_data, pitcher_folder, 'HardHitPitches', hard_hit_marker, 'Hard Hit Pitches')
    plot_pitches(pitcher_data, pitcher_folder, 'BallCalled', ball_called, 'Ball Called')
    plot_pitches(pitcher_data, pitcher_folder, 'StrikeSwinging', strike_swinging, 'Strike Swinging')
    plot_pitches(pitcher_data, pitcher_folder, 'StrikeCalled', strike_called, 'Strike Called')

    # Add quadrant information
    pitcher_data['Quadrant'] = pitcher_data.apply(
        lambda row: get_quadrant(row['PlateLocSide'], row['PlateLocHeight']), axis=1
    )

    # Update HardHit condition to only include balls in play (PitchCall == 'InPlay')
    pitcher_data['HardHit'] = (pitcher_data['ExitSpeed'] > 85) & (pitcher_data['PitchCall'] == 'InPlay')

    # Update Outcome to include 'Hard Hit' for those pitches
    pitcher_data['Outcome'] = np.where(pitcher_data['HardHit'], 'Hard Hit', pitcher_data['PitchCall'])

    # Tally outcomes by quadrant
    outcome_tally = pitcher_data.groupby(['Quadrant', 'Outcome']).size().unstack(fill_value=0)

    # Calculate totals and additional statistics
    total_pitches = outcome_tally.sum(axis=1)

    # Adjust "Ball in Play" to include Hard Hits
    outcome_tally['Balls in Play'] = outcome_tally.get('InPlay', 0) + outcome_tally.get('Hard Hit', 0)

    # Calculate percentages
    outcome_tally['Called Strike %'] = (outcome_tally.get('StrikeCalled', 0) / total_pitches) * 100
    outcome_tally['Strike Swinging %'] = (outcome_tally.get('StrikeSwinging', 0) / total_pitches) * 100
    outcome_tally['Ball in Play %'] = (outcome_tally['Balls in Play'] / total_pitches) * 100
    outcome_tally['Ball %'] = (outcome_tally.get('BallCalled', 0) / total_pitches) * 100
    outcome_tally['Hard Hit %'] = (
                                          outcome_tally.get('Hard Hit', 0) / outcome_tally['Balls in Play']
                                  ) * 100  # Avoid division by zero

    # Save outcome tally to CSV
    tally_csv_path = os.path.join(pitcher_folder, f'{sanitized_pitcher_name}_PitchOutcomeTally.csv')
    outcome_tally.to_csv(tally_csv_path)
    print(f"Outcome tally with additional stats saved to {tally_csv_path}")
