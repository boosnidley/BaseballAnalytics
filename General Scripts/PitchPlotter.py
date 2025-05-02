import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load the data from a CSV file
file_path = 'SpaanAndrewFallPitching.csv'  # Replace with the actual path to your CSV file
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

# Create figure and axis
fig, ax = plt.subplots(figsize=(6, 6))

# Plot the points for normal pitches
scatter = ax.scatter(plate_loc_side[~hard_hit_marker & ~ball_marker & ~strike_swing_marker & ~strike_called_marker],
                     plate_loc_height[~hard_hit_marker & ~ball_marker & ~strike_swing_marker & ~strike_called_marker],
                     c=np.array(colors)[~hard_hit_marker & ~ball_marker & ~strike_swing_marker & ~strike_called_marker],
                     s=sizes[~hard_hit_marker & ~ball_marker & ~strike_swing_marker & ~strike_called_marker],
                     alpha=0.7, edgecolors='black', label="Normal Pitches")

# Plot hard-hit pitches separately
ax.scatter(plate_loc_side[hard_hit_marker], plate_loc_height[hard_hit_marker],
           c=np.array(colors)[hard_hit_marker], s=sizes[hard_hit_marker],
           alpha=0.9, edgecolors='black', marker='*', label="Hard Hit Pitches")

# Plot markers for BallCalled, StrikeSwinging, and StrikeCalled
ax.scatter(plate_loc_side[ball_marker], plate_loc_height[ball_marker],
           c=np.array(colors)[ball_marker], s=sizes[ball_marker],
           alpha=0.7, edgecolors='black', marker='x', label="Ball Called")

ax.scatter(plate_loc_side[strike_swing_marker], plate_loc_height[strike_swing_marker],
           c=np.array(colors)[strike_swing_marker], s=sizes[strike_swing_marker],
           alpha=0.7, edgecolors='black', marker='v', label="Strike Swinging")

ax.scatter(plate_loc_side[strike_called_marker], plate_loc_height[strike_called_marker],
           c=np.array(colors)[strike_called_marker], s=sizes[strike_called_marker],
           alpha=0.7, edgecolors='black', marker='s', label="Strike Called")

# Add labels
ax.set_xlabel('Plate Location Side (Horizontal)')
ax.set_ylabel('Plate Location Height (Vertical)')

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

# Add a legend for pitch types and pitch outcomes
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Normal Pitches'),
    plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='gray', markersize=10, label='Hard Hit Pitches'),
    plt.Line2D([0], [0], marker='x', color='w', markerfacecolor='gray', markersize=10, label='Ball Called'),
    plt.Line2D([0], [0], marker='v', color='w', markerfacecolor='gray', markersize=10, label='Strike Swinging'),
    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='gray', markersize=10, label='Strike Called')
]
ax.legend(handles=legend_elements, title='Pitch Outcome & Type')

# Add title
ax.set_title('Pitch Location Around the Strike Zone (Markers: Pitch Outcome, Color: Pitch Type, Size: Exit Speed)')

# Display the plot
plt.show()
