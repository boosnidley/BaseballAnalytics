import pandas as pd


def split_csv_by_pitcher(input_file):
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Group by pitcher and save each group as a separate CSV file
    for pitcher, pitcher_df in df.groupby("Pitcher"):
        # Create a valid filename by replacing spaces and commas
        safe_filename = pitcher.replace(" ", "_").replace(",", "") + ".csv"
        pitcher_df.to_csv(f"../../{safe_filename}", index=False)
        print(f"Saved: {safe_filename}")


input_file = "../../Stevens- AC - 3Games.csv"
split_csv_by_pitcher(input_file)
