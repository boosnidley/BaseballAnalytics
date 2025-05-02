import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV file
df = pd.read_csv('EndOfFallData/AllFallScrimmageData.csv')

# Function to determine hit hardness based on exit velocity
def is_hard_hit(exit_speed):
    return exit_speed >= 85

# Function to determine hit type based on launch angle
def determine_hit_type(angle):
    if angle >= 45:
        return 'Pop Up'
    elif angle >= 30:
        return 'Fly Ball'
    elif angle >= 0:
        return 'Line Drive'
    else:
        return 'Ground Ball'

# Calculate the percentages for each hit type, including total balls in play
def calculate_hit_percentages(group):
    in_play = group[group['PitchCall'] == 'InPlay']
    hard_hit_count = in_play[in_play['ExitSpeed'].apply(is_hard_hit)].shape[0]
    ground_ball_count = in_play[in_play['Angle'].apply(determine_hit_type) == 'Ground Ball'].shape[0]
    pop_up_count = in_play[in_play['Angle'].apply(determine_hit_type) == 'Pop Up'].shape[0]
    total_in_play = in_play.shape[0]

    return pd.Series({
        'HardHit%': (hard_hit_count / total_in_play) * 100 if total_in_play > 0 else 0,
        'GroundBall%': (ground_ball_count / total_in_play) * 100 if total_in_play > 0 else 0,
        'PopUp%': (pop_up_count / total_in_play) * 100 if total_in_play > 0 else 0,
        'TotalInPlay': total_in_play,
        'TotalHardHits': hard_hit_count
    })

# Calculate percentages for each pitch type and role (Pitcher or Batter)
def calculate_for_pitch_type_and_role(df, role='Pitcher'):
    if role not in ['Pitcher', 'Batter']:
        raise ValueError("Invalid role! Choose either 'Pitcher' or 'Batter'.")

    # Group by role and TaggedPitchType
    percentages = df.groupby([role, 'TaggedPitchType']).apply(calculate_hit_percentages).reset_index()

    # Create stacked bar chart
    plt.figure(figsize=(12, 6))
    ax = percentages.set_index([role, 'TaggedPitchType'])[['GroundBall%', 'PopUp%', 'HardHit%']].plot(
        kind='bar', stacked=True, figsize=(10, 6)
    )
    plt.title(f'Hit Type Percentages for {role} by Pitch Type')
    plt.ylabel('Percentage (%)')
    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

    # Heatmap for pitch locations (assuming 'PlateLocX' and 'PlateLocY' columns for pitch coordinates)
    if 'PlateLocX' in df.columns and 'PlateLocY' in df.columns:
        plt.figure(figsize=(8, 6))
        pitch_loc_data = df[df['PitchCall'] == 'InPlay']  # Filter for pitches in play
        heatmap_data = pitch_loc_data.pivot_table(index='PlateLocY', columns='PlateLocX', aggfunc='size', fill_value=0)
        sns.heatmap(heatmap_data, cmap='coolwarm', annot=False, cbar=True)
        plt.title(f'Heatmap of Pitch Locations for {role}')
        plt.xlabel('Plate Location X')
        plt.ylabel('Plate Location Y')
        plt.show()

    # Save the updated CSV file with the calculated percentages
    output_file = f'{role}_PitchType_HitTypePercentages_Heatmaps.csv'
    percentages.to_csv(output_file, index=False)
    print(f"Percentages calculated and saved to {output_file}")

# Run for both Pitchers and Batters
calculate_for_pitch_type_and_role(df, 'Pitcher')
calculate_for_pitch_type_and_role(df, 'Batter')
