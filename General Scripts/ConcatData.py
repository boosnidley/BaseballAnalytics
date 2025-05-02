import pandas as pd
import glob

# Define the path and file type (e.g., all CSV files in a folder)
path = '../Game Reports/Stevens Home Games'  # Replace with the folder path where your files are located
file_extension = '*.csv'  # You can change this to *.txt or other file types if needed
all_files = "../All Game CSVs/Game Files/Stevens25G1.csv" , "../All Game CSVs/Game Files/Stevens25G2.csv", "../All Game CSVs/Game Files/Stevens2024Game.csv"

# Use a list comprehension to read and concatenate all files into one DataFrame
df = pd.concat([pd.read_csv(file) for file in all_files], ignore_index=True)

# Now 'df' contains the concatenated data from all the CSV files
print(df.head())  # Display the first few rows

# Optionally save to a new CSV file
df.to_csv('../All Game CSVs/StevensGamesConcat.csv', index=False)
