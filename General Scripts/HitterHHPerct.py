import pandas as pd

# Load the CSV file (replace 'input.csv' with your actual CSV filename)
df = pd.read_csv('../Game Reports/Stevens Home Games/Stevens25_Home_Games-Xwoba.csv')

HARD_HIT_THRESHOLD = 85

# Function to determine if a ball is hard hit based on exit velocity
def is_hard_hit(exit_speed):
    if exit_speed >= HARD_HIT_THRESHOLD:
        return 1  # Hard Hit
    else:
        return 0  # Not Hard Hit

# Apply the function to create a 'Hard Hit' column
df['Hard Hit'] = df['ExitSpeed'].apply(is_hard_hit)

# Filter for balls in play (assuming 'PitchCall' column indicates 'InPlay' status)
balls_in_play = df[df['PitchCall'] == 'InPlay']
print(balls_in_play)

# Calculate the hard hit stats for each hitter
hit_stats = balls_in_play.groupby('Pitcher').agg(
    TotalBallsInPlay=('PitchCall', 'size'),   # Total balls in play
    HardHitBalls=('Hard Hit', 'sum')          # Total hard hit balls
).reset_index()

# Add the hard hit percentage column
hit_stats['Hard Hit %'] = (hit_stats['HardHitBalls'] / hit_stats['TotalBallsInPlay']) * 100

# Save the results to a new CSV file
hit_stats.to_csv('Stevens Home Games/PitcherHHPerctStevens.csv', index=False)

print("Hard hit stats (total balls in play, hard hit balls, and hard hit percentage) calculated and saved to Hitter_HardHit_Stats.csv")
