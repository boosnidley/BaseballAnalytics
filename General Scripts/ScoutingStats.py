import pandas as pd


def load_data(file_path):
    """Loads the Excel file and reads the first sheet."""
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    return df


def calculate_stats(df):
    """Calculates hitting statistics from the dataset."""
    hitters_stats = {}
    seen_plate_appearances = set()

    for _, row in df.iterrows():
        player = row['Batter']  # Updated column name
        pa_identifier = (row['Batter'], row['PAofInning'])  # Unique PA Identifier

        if player not in hitters_stats:
            hitters_stats[player] = {
                "swings": 0, "takes": 0, "chase_swings": 0,
                "0-0_swings": 0, "take_1st_strike": 0,
                "ground_ball": 0, "line_drive": 0, "fly_ball": 0,
                "plate_appearances": 0
            }

        # Count plate appearance only once per at-bat
        if row['PitchofPA'] == 1:
            hitters_stats[player]["plate_appearances"] += 1

        # Detect swings from PitchCall
        swing_events = ["FoulBallNotFieldable", "SwingingStrike", "InPlay", "FoulBallFieldable"]
        if row['PitchCall'] in swing_events:
            hitters_stats[player]['swings'] += 1

            # Chase detection: Swung at pitches outside the strike zone
            # if row['PlateLocHeight'] < 1.5 or row['PlateLocHeight'] > 3.5 or abs(row['PlateLocSide']) > 0.85:
            #     hitters_stats[player]['chase_swings'] += 1

            # First-pitch swing
            if row['PitchofPA'] == 1:
                hitters_stats[player]['0-0_swings'] += 1
        else:
            hitters_stats[player]['takes'] += 1

            # First-pitch take for a strike
            if row['Strikes'] == 0 and row['PitchCall'] == 'StrikeCalled':
                hitters_stats[player]['take_1st_strike'] += 1

        # Batted ball classification
        if row['TaggedHitType'] == 'GroundBall':
            hitters_stats[player]['ground_ball'] += 1
        elif row['TaggedHitType'] == 'LineDrive':
            hitters_stats[player]['line_drive'] += 1
        elif row['TaggedHitType'] in ['FlyBall', 'PopUp']:
            hitters_stats[player]['fly_ball'] += 1

    # Compute percentages
    stats_list = []
    for player, stats in hitters_stats.items():
        total_pitches = stats["swings"] + stats["takes"]
        total_batted_balls = stats["ground_ball"] + stats["line_drive"] + stats["fly_ball"]

        stats["Total Swing %"] = (stats["swings"] / total_pitches) * 100 if total_pitches else 0
        stats["Chase %"] = (stats["chase_swings"] / stats["swings"]) * 100 if stats["swings"] else 0
        stats["0-0 Swing %"] = (stats["0-0_swings"] / stats["plate_appearances"]) * 100 if stats[
            "plate_appearances"] else 0
        stats["Take 1 Strike %"] = (stats["take_1st_strike"] / stats["plate_appearances"]) * 100 if stats[
            "plate_appearances"] else 0
        stats["Ground Ball %"] = (stats["ground_ball"] / total_batted_balls) * 100 if total_batted_balls else 0
        stats["Line Drive %"] = (stats["line_drive"] / total_batted_balls) * 100 if total_batted_balls else 0
        stats["Fly Ball %"] = (stats["fly_ball"] / total_batted_balls) * 100 if total_batted_balls else 0

        stats_list.append({"Batter": player, **stats})

    return stats_list


def export_to_csv(stats_list, output_file="hitter_stats v. Trey.csv"):
    """Exports the computed stats to a CSV file."""
    df = pd.DataFrame(stats_list)
    df.to_csv(output_file, index=False)
    print(f"Exported stats to {output_file}")


def main():
    file_path = "../Dianna_Trey.xlsx"  # Update with actual file path
    df = load_data(file_path)
    hitter_stats = calculate_stats(df)
    export_to_csv(hitter_stats)


if __name__ == "__main__":
    main()
