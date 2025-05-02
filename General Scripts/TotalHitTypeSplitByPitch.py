import pandas as pd

# Step 1: Read the CSV file into a DataFrame
df = pd.read_csv('../Fall/AllFallCSV/FallScrimmageCSV/AllFallScrimmageData.csv')

# Step 2: Filter for rows where PitchCall is 'InPlay'
df_inplay = df[df['PitchCall'] == 'InPlay']

# Step 3: Define a function to calculate hit type counts grouped by player and pitch type
def calculate_hit_type_counts(df, player_col):
    # Group by player and TaggedPitchType, then count TaggedHitType occurrences
    player_pitch_hit_type_counts = df.groupby([player_col, 'TaggedPitchType', 'TaggedHitType']).size().unstack(fill_value=0)

    # Ensure all hit types are present even if they are missing
    for hit_type in ['Groundball', 'Linedrive', 'Flyball', 'Popup']:
        if hit_type not in player_pitch_hit_type_counts:
            player_pitch_hit_type_counts[hit_type] = 0

    # Calculate total balls in play for each player and pitch type
    player_pitch_hit_type_counts['TotalBallsInPlay'] = player_pitch_hit_type_counts[['Groundball', 'Linedrive', 'Flyball', 'Popup']].sum(axis=1)

    # Reorder columns for output
    player_pitch_hit_type_counts = player_pitch_hit_type_counts[['Groundball', 'Linedrive', 'Flyball', 'Popup', 'TotalBallsInPlay']]

    return player_pitch_hit_type_counts.reset_index()

# Step 4: Calculate counts for pitchers, grouped by TaggedPitchType
pitcher_pitch_hit_type_counts = calculate_hit_type_counts(df_inplay, 'Pitcher')

# Step 5: Calculate counts for batters, grouped by TaggedPitchType
batter_pitch_hit_type_counts = calculate_hit_type_counts(df_inplay, 'Batter')

# Step 6: Save the results to CSV files
pitcher_pitch_hit_type_counts.to_csv('pitcher_pitchtype_ball_in_play_counts.csv', index=False)
batter_pitch_hit_type_counts.to_csv('batter_pitchtype_ball_in_play_counts.csv', index=False)

# Optional: To display the first few rows of the DataFrames
print(pitcher_pitch_hit_type_counts.head())
print(batter_pitch_hit_type_counts.head())
