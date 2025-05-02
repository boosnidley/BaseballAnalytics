import pandas as pd

df = pd.read_csv('All Game CSVs/Analytics/Pitchers xwoba 4-8-2025 xwoba.csv')


# Define a function to calculate xERA
def calculate_xera(xwOBA, league_wOBA=0.320, league_ERA=4.20):
    return (xwOBA - league_wOBA) * 12 + league_ERA

# Apply the function to calculate xERA for each pitcher
df['xERA'] = df['Avg_xwOBA'].apply(calculate_xera)

# Display the results
print(df)

df.to_csv('All Game CSVs/Analytics/Pitchers xERA 4-8-2025.csv', index=False)