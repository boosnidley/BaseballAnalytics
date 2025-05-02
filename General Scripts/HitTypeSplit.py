import pandas as pd

# Define the function to determine hit type based on angle
def determine_hit_type(angle):
    if angle >= 45:
        return 'Pop Up'
    elif angle >= 30:
        return 'Fly Ball'
    elif angle >= 0:
        return 'Line Drive'
    else:
        return 'Ground Ball'

# Load the CSV file into a DataFrame
df = pd.read_csv('../Fall/AllFallCSV/FallScrimmageCSV/AllFallScrimmageData-Xwoba.csv')

# Filter out rows where PlayResult is undefined, irrelevant, or fouls
# Assuming undefined or foul plays are represented by 'undefined', 'FoulBall', or similar
valid_play_results = df['PlayResult'].notna() & (df['PlayResult'] != 'Undefined')
df_filtered = df[valid_play_results]

# Apply the determine_hit_type function to the 'angle' column to create a new 'HitType' column
df_filtered['HitType'] = df_filtered['Angle'].apply(determine_hit_type)

# Group by 'Pitcher' and 'HitType', then count occurrences of each hit type
hit_counts = df_filtered.groupby(['Pitcher', 'HitType']).size().reset_index(name='HitCount')

# Calculate total hits (balls in play) allowed by each pitcher
total_hits = df_filtered.groupby('Pitcher').size().reset_index(name='TotalBIP')  # Total Balls In Play (BIP)

# Merge hit counts with total hits to get both in one DataFrame
merged_df = pd.merge(hit_counts, total_hits, on='Pitcher')

# Calculate the percentage of each HitType
merged_df['HitPercentage'] = (merged_df['HitCount'] / merged_df['TotalBIP']) * 100

# Display the result with total balls in play
print(merged_df[['Pitcher', 'HitType', 'HitCount', 'HitPercentage', 'TotalBIP']])

# Optionally, export the results to a CSV file
merged_df[['Pitcher', 'HitType', 'HitCount', 'HitPercentage', 'TotalBIP']].to_csv('FallBreakdown/Scrimmage/PitcherHitTypeSplit.csv', index=False)
