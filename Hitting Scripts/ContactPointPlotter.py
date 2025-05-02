#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Plot a 2D scatter of the hitter's point of contact (ContactPositionX vs. ContactPositionY) "
                    "from a TrackMan dataset."
    )
    parser.add_argument(
        "csvfile",
        help="Path to the CSV file containing the TrackMan data"
    )
    parser.add_argument(
        "--colx",
        default="ContactPositionX",
        help="Column name for the horizontal axis (default: 'ContactPositionX')"
    )
    parser.add_argument(
        "--coly",
        default="ContactPositionY",
        help="Column name for the vertical axis (default: 'ContactPositionY')"
    )
    args = parser.parse_args()

    # Load the CSV file
    try:
        df = pd.read_csv(args.csvfile)
    except Exception as e:
        sys.exit(f"Error reading CSV file: {e}")

    # Verify that the specified columns exist
    for col in [args.coly, args.colx]:
        if col not in df.columns:
            sys.exit(
                f"Column '{col}' not found in dataset. Available columns are: {', '.join(df.columns)}"
            )

    # Drop rows with missing values in the contact columns
    df = df.dropna(subset=[args.coly, args.colx])

    # Create a 2D scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(
        df[args.coly],
        df[args.colx],
        alpha=0.7,
        edgecolors='black',
        linewidth=0.5
    )
    plt.title("Hitter's 2D Point of Contact")
    plt.xlabel(args.coly)
    plt.ylabel(args.colx)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
