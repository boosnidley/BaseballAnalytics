import pandas as pd

# Load the data from a CSV file
file_path = 'SchreierGavenFallPitching.csv'  # Replace with the actual path to your CSV file
data = pd.read_csv(file_path)

# Extract the necessary columns
pitch_type = data['TaggedPitchType']  # Column for pitch type
pitch_called = data['PitchCall']      # Column for pitch outcome

# Initialize a list to store the previous pitch data before each strike
previous_pitch_tally = []

# Loop through the data starting from the second row to compare with the previous row
for i in range(1, len(data)):
    # Check if the current pitch resulted in a strike swinging or strike called
    if pitch_called[i] in ['StrikeSwinging', 'StrikeCalled']:
        # Append the previous pitch type and current pitch type to the tally
        previous_pitch_tally.append({
            'PreviousPitch': pitch_type[i-1],  # Previous pitch type
            'CurrentPitch': pitch_type[i],     # Current pitch type that was a strike
            'StrikeType': pitch_called[i]      # Whether it was swinging or called
        })

# Convert the list of tallies into a DataFrame
previous_pitch_df = pd.DataFrame(previous_pitch_tally)

# Group by previous and current pitch to tally occurrences
pitch_tally = previous_pitch_df.groupby(['PreviousPitch', 'CurrentPitch', 'StrikeType']).size().unstack(fill_value=0)

# Display the tally of previous pitches before strike swings/calls
print(pitch_tally)

# Save the tally to a CSV file
output_file_path = 'GavenSchreierPitching/GavenSchreierprevious_pitch_tally_before_strikes.csv'  # Specify your desired output path
pitch_tally.to_csv(output_file_path)
print(f"Pitch tally before strikes saved to {output_file_path}")
