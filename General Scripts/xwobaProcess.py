import pandas as pd

# Load the CSV file (replace 'input.csv' with your actual CSV filename)
df = pd.read_csv('../All Game CSVs/AllGameData 4-8-2025.csv')

# Define the xwOBA table based on your image
xwOBA_table = {
    'Pop Up': {'Hard Hit': 0.127, 'Medium Hit': 0.0455, 'Soft Hit': 0.0455},
    'Fly Ball': {'Hard Hit': 0.76575, 'Medium Hit': 0.0635, 'Soft Hit': 0.356},
    'Line Drive': {'Hard Hit': 1.1416, 'Medium Hit': 0.791, 'Soft Hit': 0.502},
    'Ground Ball': {'Hard Hit': 0.2415, 'Medium Hit': 0.0966, 'Soft Hit': 0.0455},
}

# Function to determine hit type based on angle
def determine_hit_type(angle):
    if angle >= 45:
        return 'Pop Up'
    elif angle >= 30:
        return 'Fly Ball'
    elif angle >= 0:
        return 'Line Drive'
    else:
        return 'Ground Ball'

# Function to determine hit hardness based on exit velocity
def determine_hit_hardness(exit_speed):
    if exit_speed >= 87:
        return 'Hard Hit'
    elif exit_speed >= 75:
        return 'Medium Hit'
    else:
        return 'Soft Hit'

# Function to calculate xwOBA
def calculate_xwOBA(row):
    # Check the KorBB column for Strikeout or Walk first
    if pd.notna(row['KorBB']):
        if row['KorBB'] == 'Strikeout':
            return 0
        elif row['KorBB'] == 'Walk':
            return 0.75
    
    # Only proceed to calculate xwOBA if PitchCalled is 'InPlay'
    if pd.notna(row['PitchCall']) and row['PitchCall'] == 'InPlay':
        if pd.notna(row['Angle']) and pd.notna(row['ExitSpeed']):
            hit_type = determine_hit_type(row['Angle'])
            hit_hardness = determine_hit_hardness(row['ExitSpeed'])
            return xwOBA_table[hit_type][hit_hardness]
    
    # If conditions are not met, return None
    return None

# Apply the function to each row to create a new xwOBA column
df['xwOBA'] = df.apply(calculate_xwOBA, axis=1)

# Save the updated CSV file
df.to_csv('All Game CSVs/AllGameData 4-8-2025 xwoba.csv', index=False)

print("xwOBA column added and saved to output_with_xwOBA.csv")
