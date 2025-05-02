import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the full dataset
file_path = '../Fall/AllFallCSV/FallScrimmageCSV/AllFallScrimmageData-Xwoba.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Define output directory
output_dir = 'AggregatedPitcherCirclePlots'
os.makedirs(output_dir, exist_ok=True)


# Function to calculate densities and plot circles
def create_density_circle_plot(df, condition, output_path, title):
    filtered_data = df[condition]

    # Bin the data
    x_bins = np.linspace(-2, 2, 50)  # Adjust the number of bins as needed
    y_bins = np.linspace(-2, 6, 50)
    heatmap, x_edges, y_edges = np.histogram2d(
        filtered_data['PlateLocSide'], filtered_data['PlateLocHeight'], bins=[x_bins, y_bins]
    )

    # Normalize heatmap for circle sizes
    max_density = heatmap.max()
    if max_density > 0:
        heatmap = heatmap / max_density  # Normalize to [0, 1]

    # Plot circles
    plt.figure(figsize=(6, 6))
    ax = plt.gca()
    for i in range(len(x_edges) - 1):
        for j in range(len(y_edges) - 1):
            density = heatmap[i, j]
            if density > 0:
                # Calculate circle position (center of the bin) and size
                x_center = (x_edges[i] + x_edges[i + 1]) / 2
                y_center = (y_edges[j] + y_edges[j + 1]) / 2
                circle_size = density * 20  # Scale circle size as needed
                ax.scatter(x_center, y_center, s=circle_size, color='blue', alpha=0.6, edgecolor='black')

    # Add strike zone
    strike_zone = plt.Rectangle((-0.83, 1.5), 1.66, 2.5, fill=False, color='red', linestyle='--')
    ax.add_patch(strike_zone)

    # Set plot limits and labels
    plt.title(title)
    plt.xlabel('Plate Location Side')
    plt.ylabel('Plate Location Height')
    plt.xlim(-2, 2)
    plt.ylim(-2, 6)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)

    # Save plot
    plt.savefig(output_path)
    print(f"Circle plot saved to {output_path}")
    plt.close()


# Define conditions for different categories
conditions = {
    'Hard Hit': (data['ExitSpeed'] > 85) & (data['PitchCall'] == 'InPlay'),
    'Ball Called': data['PitchCall'] == 'BallCalled',
    'Strike Swinging': data['PitchCall'] == 'StrikeSwinging',
    'Strike Called': data['PitchCall'] == 'StrikeCalled',
    'Normal Pitches': data['ExitSpeed'] <= 85
}

# Generate circle plots for each category
for category, condition in conditions.items():
    create_density_circle_plot(
        data,
        condition,
        os.path.join(output_dir, f'{category.replace(" ", "")}_CirclePlot.pdf'),
        title=f'{category} Circle Plot'
    )
