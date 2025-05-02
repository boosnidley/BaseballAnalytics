import pandas as pd

# Step 1: Read the CSV file
# Replace 'your_file.csv' with the path to your actual file
df = pd.read_csv('../All Game CSVs/AllGameData 4-8-2025 xwoba.csv')

# Step 2: Group the data by the pitcher and calculate the mean xwOBA for each pitcher
# Assuming 'pitcher' is the name of the pitcher column and 'xwOBA' is the xwOBA column
pitcher_xwOBA = df.groupby('Pitcher')['xwOBA'].mean().reset_index()

# Rename the columns to make it clear
pitcher_xwOBA.columns = ['Pitcher', 'Avg_xwOBA']

# Step 3: Display the result
print(pitcher_xwOBA)

# Optionally, save to a new CSV file
pitcher_xwOBA.to_csv('All Game CSVs/Analytics/Pitchers xwoba 4-8-2025 xwoba.csv', index=False)
