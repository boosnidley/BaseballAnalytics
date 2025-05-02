import pandas as pd

# Load the CSV file (replace 'input.csv' with your actual CSV filename)
df = pd.read_csv('../Fall/AllFallCSV/FallScrimmageCSV/AllFallScrimmageData-Xwoba.csv')


# Function to determine hit hardness based on exit velocity
def is_hard_hit(exit_speed):
    return exit_speed >= 85


# Function to calculate the hard hit percentage for each pitcher
def calculate_hard_hit_percentage(group):
    # Only consider balls in play
    in_play = group[group['PitchCall'] == 'InPlay']

    # Count the number of hard-hit balls
    hard_hit_count = in_play[in_play['ExitSpeed'].apply(is_hard_hit)].shape[0]

    # Calculate the hard hit percentage
    if in_play.shape[0] > 0:  # Avoid division by zero
        return (hard_hit_count / in_play.shape[0]) * 100
    else:
        return None


# Group the data by Pitcher and calculate hard-hit percentage
hard_hit_percentages = df.groupby('Pitcher').apply(calculate_hard_hit_percentage).reset_index(name='HardHit%')

# Save the updated CSV file with hard-hit percentages
hard_hit_percentages.to_csv('FallBreakdown/Scrimmage/PitcherHHPerctScrimmage.csv', index=False)

print("Hard-hit percentages calculated and saved to PitcherHardHitPercentages.csv")
