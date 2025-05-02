import os
import pandas as pd

# Load the full dataset (modify this path to your actual dataset)
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


# Iterate through each pitcher and process their data
for pitcher in pitchers:
    # Filter data for the current pitcher
    pitcher_data = data[data['Pitcher'] == pitcher]

    # Create a sanitized folder name for the pitcher and create the folder
    sanitized_pitcher_name = sanitize_name(pitcher)
    pitcher_folder = os.path.join(output_dir, sanitized_pitcher_name)
    os.makedirs(pitcher_folder, exist_ok=True)

    # Extract the necessary columns
    pitch_type = pitcher_data['TaggedPitchType']  # Column for pitch type
    pitch_called = pitcher_data['PitchCall']  # Column for pitch outcome

    # Initialize a list to store the previous pitch data before each strike
    previous_pitch_tally = []

    # Loop through the data starting from the second row to compare with the previous row
    for i in range(1, len(pitcher_data)):
        # Check if the current pitch resulted in a strike swinging or strike called
        if pitch_called.iloc[i] in ['StrikeSwinging', 'StrikeCalled']:
            # Append the previous pitch type and current pitch type to the tally
            previous_pitch_tally.append({
                'PreviousPitch': pitch_type.iloc[i - 1],  # Previous pitch type
                'CurrentPitch': pitch_type.iloc[i],  # Current pitch type that was a strike
                'StrikeType': pitch_called.iloc[i]  # Whether it was swinging or called
            })

    # Convert the list of tallies into a DataFrame
    previous_pitch_df = pd.DataFrame(previous_pitch_tally)

    # Group by previous and current pitch to tally occurrences
    pitch_tally = previous_pitch_df.groupby(['PreviousPitch', 'CurrentPitch', 'StrikeType']).size().unstack(
        fill_value=0)

    # Save the tally to a CSV file in the respective pitcher folder
    output_file_path = os.path.join(pitcher_folder, f'{sanitized_pitcher_name}_previous_pitch_tally_before_strikes.csv')
    pitch_tally.to_csv(output_file_path)

    print(f"Pitch tally before strikes saved to {output_file_path}")
