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

# Function to calculate HardHit% by pitch type and quadrant
def calculate_hard_hit_percentages_by_pitch_and_quadrant(df):
    # Add a column for the quadrant of the strike zone
    df['StrikeZoneQuadrant'] = df.apply(lambda row: determine_quadrant(row['PlateLocHeight'], row['PlateLocSide']), axis=1)

    # Only consider balls in play
    in_play = df[df['PitchCall'] == 'InPlay']

    # Count total and hard-hit balls by pitch type and quadrant
    hard_hit_by_pitch_quadrant = in_play[in_play['ExitSpeed'].apply(is_hard_hit)].groupby(['TaggedPitchType', 'StrikeZoneQuadrant']).size()
    total_by_pitch_quadrant = in_play.groupby(['TaggedPitchType', 'StrikeZoneQuadrant']).size()

    # Calculate HardHit% by pitch type and quadrant
    hard_hit_percentages = (hard_hit_by_pitch_quadrant / total_by_pitch_quadrant) * 100

    # Convert to DataFrame and save to CSV
    hard_hit_percentages = hard_hit_percentages.reset_index(name='HardHit%')
    hard_hit_percentages.to_csv('HardHitPercentagesByPitchAndQuadrant.csv', index=False)

    print("HardHit% by pitch type and quadrant calculated and saved to HardHitPercentagesByPitchAndQuadrant.csv")

# Run the program
calculate_hard_hit_percentages_by_pitch_and_quadrant(df)
