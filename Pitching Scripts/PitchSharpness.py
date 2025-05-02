import pandas as pd
import numpy as np

# Function to load CSV file
def load_csv_file(file_path):
    return pd.read_csv(file_path)

# Function to save the result to a CSV file
def save_to_csv(dataframe, output_path):
    dataframe.to_csv(output_path, index=False)

# Ask the user for a file path input
file_path = "../All Game CSVs/Game Files/FDU-AC.csv"

# Load the CSV data
shape_data = load_csv_file(file_path)

# Create the sharpness metric for each row using Boyle's formula
shape_data['PitchSharpness'] = (
    np.abs(np.abs(shape_data['VertApprAngle']) - np.abs(shape_data['VertRelAngle'])) +
    np.abs(np.abs(shape_data['HorzApprAngle']) - np.abs(shape_data['HorzRelAngle']))
) * 10

# Group by Pitcher and TaggedPitchType to get average sharpness
avg_sharpness_by_pitcher = shape_data.groupby(['Pitcher', 'TaggedPitchType'])['PitchSharpness'].mean().reset_index()
avg_sharpness_by_pitcher = avg_sharpness_by_pitcher.round(2)

# Ask the user for an output file path
output_file_path = "SampleSharpness.csv"

# Save the result as a CSV file
save_to_csv(avg_sharpness_by_pitcher, output_file_path)

print(f"The results have been saved to {output_file_path}")



# Pitch Type	        Ideal Sharpness Range	Elite Sharpness Range	💬 Notes
# Fastball	            35 – 55	                55 – 70	                Lower sharpness is normal. Focus is on carry (IVB), not break.
# Two-Seam Fastball	    45 – 60	                60 – 75	                More lateral movement than 4-seam. Sharpness still moderate.
# Changeup	            70 – 90	                90 – 110+	            Late drop/change of direction is key. Higher sharpness = more deception.
# Slider	            70 – 90	                90 – 120+	            Elite sliders snap late. Sharpness >100 often equals wipeout pitches.
# Curveball	            80 – 100	            100 – 120+	            Big drop, often with tighter spin. Elite sharpness = true 12-6 or hammer curves.