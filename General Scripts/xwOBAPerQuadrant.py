import pandas as pd
import numpy as np

# Load the data from a CSV file
file_path = '../All Game CSVs/AllGameData 4-8-2025 xwoba.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Define strike zone boundaries
strike_zone_left = -0.83  # Left boundary
strike_zone_right = 0.83  # Right boundary
strike_zone_bottom = 1.5  # Bottom boundary (knees)
strike_zone_top = 4.0  # Top boundary (shoulders)

# Define quadrants within the strike zone
def get_quadrant(side, height):
    if side < 0 and height > 2.75:
        return 'Top Left'
    elif side >= 0 and height > 2.75:
        return 'Top Right'
    elif side < 0 and height <= 2.75:
        return 'Bottom Left'
    else:
        return 'Bottom Right'

# Apply the quadrant function to each pitch
data['Quadrant'] = data.apply(lambda row: get_quadrant(row['PlateLocSide'], row['PlateLocHeight']), axis=1)

# Filter out rows without valid xwOBA values
valid_xwOBA = data['xwOBA'].notnull()

# Calculate the average xwOBA for each quadrant
average_xwOBA = data[valid_xwOBA].groupby('Quadrant')['xwOBA'].mean()

# Convert the result to a DataFrame for better presentation
average_xwOBA_df = average_xwOBA.reset_index()
average_xwOBA_df.columns = ['Quadrant', 'Average xwOBA']

# Save the results to a CSV file
output_file_path = 'All Game CSVs/Analytics/xwoba by Quadrants.csv'  # Replace with your desired output path
average_xwOBA_df.to_csv(output_file_path, index=False)
print(f"Average xwOBA by quadrant saved to {output_file_path}")

# Display the result in the console
print("\nAverage xwOBA by Quadrant:")
print(average_xwOBA_df)
