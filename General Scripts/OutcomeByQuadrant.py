import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load the data from a CSV file
file_path = 'SchreierGavenFallPitching.csv'  # Replace with the actual path to your CSV file
data = pd.read_csv(file_path)

# Extract the necessary columns
plate_loc_height = data['PlateLocHeight']
plate_loc_side = data['PlateLocSide']
pitch_type = data['TaggedPitchType']
pitch_called = data['PitchCall']  # Column for pitch outcome
exit_speed = data['ExitSpeed']  # Exit speed for identifying hard-hit balls

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

# Identify hard-hit balls (ExitSpeed > 85)
data['HardHit'] = data['ExitSpeed'] > 85

# Combine pitch outcomes with hard-hit condition for tally
data['Outcome'] = np.where(data['HardHit'], 'Hard Hit', data['PitchCall'])

# Tally the outcomes for each quadrant, including hard hits
outcome_tally = data.groupby(['Quadrant', 'Outcome']).size().unstack(fill_value=0)

# Save the outcome tally to a CSV file
output_file_path = 'GavenSchreierPitching/GavenSchreierpitch_outcome_tally_by_quadrant.csv'  # Specify your desired output path
outcome_tally.to_csv(output_file_path)
print(f"Outcome tally (including hard hits) saved to {output_file_path}")

# Plot a scatter plot to show pitch locations and quadrants
def plot_quadrants():
    fig, ax = plt.subplots(figsize=(6, 6))

    # Plot the pitches with different markers for each quadrant
    quadrants = ['Top Left', 'Top Right', 'Bottom Left', 'Bottom Right']
    colors = ['red', 'blue', 'green', 'purple']

    for quadrant, color in zip(quadrants, colors):
        mask = data['Quadrant'] == quadrant
        ax.scatter(data['PlateLocSide'][mask], data['PlateLocHeight'][mask], label=quadrant, color=color, alpha=0.6)

    # Set axis labels and limits to represent the strike zone
    ax.set_xlabel('Plate Location Side (Horizontal)')
    ax.set_ylabel('Plate Location Height (Vertical)')
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 6)
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True)

    # Draw the strike zone
    strike_zone = plt.Rectangle((-0.83, 1.5), 1.66, 2.5, fill=False, color='red', linestyle='--')
    ax.add_patch(strike_zone)

    # Add a title and legend
    ax.set_title('Pitch Locations and Strike Zone Quadrants')
    ax.legend()

    # Display the plot
    plt.show()

# Display the tally of outcomes by quadrant, including hard hits
print(outcome_tally)

# Plot the quadrant scatter plot
plot_quadrants()
