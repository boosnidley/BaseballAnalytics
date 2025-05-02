import pandas as pd

# Load the CSV file (replace 'input.csv' with your actual CSV filename)
df = pd.read_csv('EndOfFallData/AllFallScrimmageData.csv')

# Function to determine hit hardness based on exit velocity
def is_hard_hit(exit_speed):
    return exit_speed >= 80

# Function to determine which quadrant the pitch was in based on PlateLocHeight and PlateLocSide
def determine_quadrant(height, side):
    if height >= 0 and side < 0:
        return 'Upper Left (High & Inside)'
    elif height >= 0 and side >= 0:
        return 'Upper Right (High & Outside)'
    elif height < 0 and side < 0:
        return 'Lower Left (Low & Inside)'
    else:
        return 'Lower Right (Low & Outside)'

# Function to calculate HardHit% by quadrant for both pitcher and hitter
def calculate_hard_hit_percentages_by_quadrant(df):
    # Add a column for the quadrant of the strike zone
    df['StrikeZoneQuadrant'] = df.apply(lambda row: determine_quadrant(row['PlateLocHeight'], row['PlateLocSide']), axis=1)

    # Only consider balls in play
    in_play = df[df['PitchCall'] == 'InPlay']

    # Group by Pitcher, Hitter, and StrikeZoneQuadrant
    grouped = in_play.groupby(['Pitcher', 'Batter', 'StrikeZoneQuadrant'])

    # Count total and hard-hit balls
    hard_hit_by_group = grouped.apply(lambda x: x[x['ExitSpeed'].apply(is_hard_hit)].shape[0])
    total_by_group = grouped.size()

    # Calculate HardHit% for each group
    hard_hit_percentages = (hard_hit_by_group / total_by_group) * 100

    # Convert to DataFrame and save to CSV
    result_df = hard_hit_percentages.reset_index(name='HardHit%')
    result_df.to_csv('HardHitPercentagesByQuadrant_Pitcher_Hitter.csv', index=False)

    print("HardHit% by quadrant calculated and saved to HardHitPercentagesByQuadrant_Pitcher_Hitter.csv")

# Run the program
calculate_hard_hit_percentages_by_quadrant(df)
