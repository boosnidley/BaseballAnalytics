import pandas as pd

# Load the data from the CSV file
file_path = '../Fall/AllFallCSV/FallScrimmageCSV/AllFallScrimmageData-Xwoba.csv'  # Replace with the path to your CSV file
data = pd.read_csv(file_path)

# Set the pitcher's name to filter by
pitcher_name = 'Schreier, Gaven'  # Replace 'X' with the name of the pitcher you want to filter

# Filter the rows where the 'Pitcher' column matches the specified name
filtered_data = data[data['Pitcher'] == pitcher_name]

# Save the filtered rows to a new CSV file
output_file_path = 'SchreierGavenFallPitching.csv'  # Output file path
filtered_data.to_csv(output_file_path, index=False)

print(f"Filtered data saved to {output_file_path}")
