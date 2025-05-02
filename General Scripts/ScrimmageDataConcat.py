import pandas as pd

# Replace 'file1.csv' and 'file2.csv' with your actual file names
file1 = 'AllFallCSV/FallBatPracCSV/9.1 Batting Practice.csv'
file2 = 'AllFallCSV/FallBatPracCSV/9.6 Batting Practice.csv'
file3 = 'AllFallCSV/FallBatPracCSV/9.13 Batting Practice.csv'
file4 = 'AllFallCSV/FallBatPracCSV/9.20 Batting Practice.csv'
file5 = 'AllFallCSV/FallBatPracCSV/10.18 Batting Practice.csv'
# file6 = 'AllFallCSV/FallScrimmageCSV/10.25 Scrimmage.csv'


# Read the CSV files into DataFrames
df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)
df3 = pd.read_csv(file3)
df4 = pd.read_csv(file4)
df5 = pd.read_csv(file5)
# df6 = pd.read_csv(file6)



# Concatenate the two DataFrames
concatenated_df = pd.concat([df1, df2, df3, df4, df5])

# Write the concatenated DataFrame to a new CSV file
concatenated_df.to_csv('AllFallCSV/FallBatPracCSV/AllFallBattingPracticeData.csv', index=False)

print("Files have been concatenated and saved as ... ")
