import pandas as pd

# Load the CSV file (replace 'input.csv' with your actual CSV filename)
df = pd.read_csv('../Fall/AllFallCSV/FallScrimmageCSV/AllFallScrimmageData-Xwoba.csv')

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

# Function to calculate the percentages for each hit type, including total balls in play
def calculate_hit_percentages(group):
    # Only consider balls in play
    in_play = group[group['PitchCall'] == 'InPlay']

    # Count hard-hit balls
    hard_hit_count = in_play[in_play['ExitSpeed'].apply(is_hard_hit)].shape[0]

    # Count ground balls and pop-ups based on launch angle
    ground_ball_count = in_play[in_play['Angle'].apply(determine_hit_type) == 'Ground Ball'].shape[0]
    pop_up_count = in_play[in_play['Angle'].apply(determine_hit_type) == 'Pop Up'].shape[0]

    # Calculate total balls in play
    total_in_play = in_play.shape[0]

    if total_in_play > 0:
        hard_hit_percentage = (hard_hit_count / total_in_play) * 100
        ground_ball_percentage = (ground_ball_count / total_in_play) * 100
        pop_up_percentage = (pop_up_count / total_in_play) * 100
    else:
        hard_hit_percentage = ground_ball_percentage = pop_up_percentage = None

    # Return the percentages along with total balls in play
    return pd.Series({
        'HardHit%': hard_hit_percentage,
        'GroundBall%': ground_ball_percentage,
        'PopUp%': pop_up_percentage,
        'TotalInPlay': total_in_play,
        'TotalHardHits': hard_hit_count
    })

# Function to calculate percentages for each pitch type and player role (pitcher or hitter)
def calculate_for_pitch_type_and_role(df, role='Pitcher'):
    # Validate the role
    if role not in ['Pitcher', 'Batter']:
        raise ValueError("Invalid role! Choose either 'Pitcher' or 'Batter'.")

    # Group the data by the selected role and TaggedPitchType, and calculate percentages
    percentages = df.groupby([role, 'TaggedPitchType']).apply(calculate_hit_percentages).reset_index()

    # Save the updated CSV file with the calculated percentages
    output_file = f'FallBreakdown/Scrimmage/{role}_PitchType_HitTypePercentages.csv'
    percentages.to_csv(output_file, index=False)

    print(f"Percentages calculated and saved to {output_file}")

# Run for both pitchers and hitters, grouped by TaggedPitchType
calculate_for_pitch_type_and_role(df, 'Pitcher')
calculate_for_pitch_type_and_role(df, 'Batter')
