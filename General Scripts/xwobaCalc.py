import pandas as pd

# Load the CSV file (replace with your actual CSV filename)
df = pd.read_csv('../All Game CSVs/AllGameData 4-8-2025 xwoba.csv')

# Ensure xwOBA is a numeric column (in case of any non-numeric entries)
df['xwOBA'] = pd.to_numeric(df['xwOBA'], errors='coerce')

# Group by 'Batter' and calculate the average xwOBA for each batter
average_xwOBA_per_batter = df.groupby('Batter')['xwOBA'].mean().reset_index()

# Rename the column for clarity
average_xwOBA_per_batter.rename(columns={'xwOBA': 'Average_xwOBA'}, inplace=True)

# Save the result to a new CSV file
average_xwOBA_per_batter.to_csv('All Game CSVs/Analytics/Hitters xwoba 4-8-2025.csv', index=False)

print("Average xwOBA for each batter has been saved to 'average_xwOBA_per_batter.csv'")
