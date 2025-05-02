import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load the full dataset
file_path = '../Fall/AllFallCSV/FallScrimmageCSV/AllFallScrimmageData-Xwoba.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Define output directory
output_dir = 'AggregatedPitcherHeatMaps'
os.makedirs(output_dir, exist_ok=True)

# Filter rows where xwOBA has a valid value
valid_xwOBA = data['xwOBA'].notnull()

# Function to generate a heatmap based on xwOBA
def create_xwOBA_heatmap(df, condition, output_path, title, cmap='coolwarm'):
    plt.figure(figsize=(6, 6))
    sns.kdeplot(
        x=df['PlateLocSide'][condition],
        y=df['PlateLocHeight'][condition],
        weights=df['xwOBA'][condition],  # Use xwOBA values as weights
        cmap=cmap,
        fill=True,
        levels=100,
        thresh=0
    )
    plt.title(title)
    plt.xlabel('Plate Location Side')
    plt.ylabel('Plate Location Height')
    plt.xlim(-2, 2)
    plt.ylim(-2, 6)

    # Draw strike zone
    plt.gca().add_patch(plt.Rectangle(
        (-0.83, 1.5), 1.66, 2.5, fill=False, color='red', linestyle='--'
    ))
    plt.grid(True)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig(output_path)
    print(f"Heatmap saved to {output_path}")
    plt.close()

# Create the xwOBA heatmap
create_xwOBA_heatmap(
    data,
    valid_xwOBA,
    os.path.join(output_dir, 'xwOBA_Heatmap.pdf'),
    title='xwOBA Heat Map'
)
