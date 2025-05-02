import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load the data from a CSV file
file_path = 'SchreierGavenFallPitching.csv'  # Replace with the actual path to your CSV file
data = pd.read_csv(file_path)

# Extract the necessary columns
plate_loc_height = data['PlateLocHeight']
plate_loc_side = data['PlateLocSide']
exit_speed = data['ExitSpeed']
pitch_type = data['TaggedPitchType']
pitch_called = data['PitchCall']  # New column for pitch outcome

# Define colors for pitch types
pitch_colors = {'Fastball': 'red', 'Curveball': 'blue', 'Slider': 'yellow', 'Changeup': 'green'}  # Adjust pitch types if needed

# Map pitch types to colors
colors = [pitch_colors.get(pitch, 'gray') for pitch in pitch_type]  # Default to 'gray' if pitch type is not in pitch_colors

# Set default sizes and handle NaNs for exit speed
default_size = 50  # Small size for pitches with no exit speed
sizes = np.where(pd.isna(exit_speed), default_size, np.sqrt(exit_speed) * 1)  # Scale exit speed or set default

# Mark pitches with Exit Speed > 85 as larger and use special marker
hard_hit_marker = exit_speed > 85
sizes[hard_hit_marker] = 200  # Assign larger size for hard-hit pitches (over 85 mph)

# Define markers for pitch outcomes
ball_marker = pitch_called == 'BallCalled'
strike_swing_marker = pitch_called == 'StrikeSwinging'
strike_called_marker = pitch_called == 'StrikeCalled'

# Function to create scatter plot for each pitch category
def plot_pitches(marker, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(6, 6))

    # Plot the points for the selected category
    ax.scatter(plate_loc_side[marker], plate_loc_height[marker],
               c=np.array(colors)[marker], s=sizes[marker],
               alpha=0.7, edgecolors='black')

    # Add labels
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # Set limits to represent a typical strike zone
    ax.set_xlim(-2, 2)  # Side limits (-2 feet to 2 feet from the center)
    ax.set_ylim(-2, 6)  # Height limits (From knees (-2) to above the head (6))

    # Ensure the x and y axes have the same scale
    ax.set_aspect('equal', adjustable='box')  # 'equal' ensures 1:1 aspect ratio

    # Set grid with 0.5 step size
    ax.set_xticks([i * 0.5 for i in range(-4, 5)])  # X-axis ticks from -2 to 2 with 0.5 increments
    ax.set_yticks([i * 0.5 for i in range(-4, 13)])  # Y-axis ticks from -2 to 6 with 0.5 increments
    ax.grid(True)

    # Draw a rectangle representing the strike zone (approximate dimensions)
    strike_zone = plt.Rectangle((-0.83, 1.5), 1.66, 2.5, fill=False, color='red', linestyle='--')
    ax.add_patch(strike_zone)

    # Add title
    ax.set_title(title)

    # Display the plot
    plt.show()

# Plot individual graphs for each marker
plot_pitches(~hard_hit_marker & ~ball_marker & ~strike_swing_marker & ~strike_called_marker,
             'Normal Pitches', 'Plate Location Side (Horizontal)', 'Plate Location Height (Vertical)')

plot_pitches(hard_hit_marker,
             'Hard Hit Pitches', 'Plate Location Side (Horizontal)', 'Plate Location Height (Vertical)')

plot_pitches(ball_marker,
             'Ball Called', 'Plate Location Side (Horizontal)', 'Plate Location Height (Vertical)')

plot_pitches(strike_swing_marker,
             'Strike Swinging', 'Plate Location Side (Horizontal)', 'Plate Location Height (Vertical)')

plot_pitches(strike_called_marker,
             'Strike Called', 'Plate Location Side (Horizontal)', 'Plate Location Height (Vertical)')
