import os
import sys
import pandas as pd
from SplitCSVbyPitcher import split_csv_by_pitcher
from PitcherReport import generate_trackman_report, generate_pitch_summary_table, generate_pitch_location_plot, generate_pitch_color_legend, generate_pitch_movement_plot, generate_release_point, velocity_ridgeline_plot, generate_pitch_usage, generate_tilt_range

## -- CONFIGURATION -- ##
# Set your input file and output directories here
INPUT_FILE = "20250401-McGillField-1_unverified.csv"  # The Trackman CSV file to process
OUTPUT_BASE_DIR = "../Game Reports/MessiahGame"  # Base directory for all outputs
CSV_OUTPUT_DIR = "Pitchers-CSV"  # Subdirectory for split CSV files
PDF_OUTPUT_DIR = "Pitchers-Reports"  # Subdirectory for PDF reports

def ensure_output_directory():
    """Ensure the output directory for PDFs exists."""
    output_dir = os.path.join(OUTPUT_BASE_DIR, PDF_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def process_all_pitchers(input_file):
    """
    Process a Trackman CSV file by splitting it by pitcher and generating reports for each.
    
    Args:
        input_file (str): Path to the input Trackman CSV file
    """
    # Get the directory of the input file
    input_dir = os.path.dirname(os.path.abspath(input_file))
    
    # Ensure output directory exists
    output_dir = ensure_output_directory()
    
    # Split the CSV file by pitcher
    print(f"\nSplitting {input_file} by pitcher...")
    split_csv_by_pitcher(input_file)
    
    # Get all CSV files in the output directory
    csv_dir = os.path.join(OUTPUT_BASE_DIR, CSV_OUTPUT_DIR)
    pitcher_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    
    if not pitcher_files:
        print("No pitcher files found after splitting!")
        return
    
    print(f"\nFound {len(pitcher_files)} pitcher files to process.")
    
    # Process each pitcher file
    for pitcher_file in pitcher_files:
        try:
            print(f"\nProcessing {pitcher_file}...")
            pitcher_path = os.path.join(csv_dir, pitcher_file)
            
            # Load the CSV file
            data = pd.read_csv(pitcher_path)
            
            # Check if all rows have the same pitcher name and throwing hand
            unique_pitchers = data['Pitcher'].unique()
            unique_hands = data['PitcherThrows'].unique()
            
            if len(unique_pitchers) == 1 and len(unique_hands) == 1:
                # Extract values
                pitcher_name = unique_pitchers[0]
                pitcher_hand = unique_hands[0]
                
                # Map "Right" → "RHP", "Left" → "LHP"
                hand_map = {"Right": "RHP", "Left": "LHP"}
                hand_abbreviation = hand_map.get(pitcher_hand, pitcher_hand)
                
                # Reformat name from "Lastname, Firstname" to "Firstname Lastname"
                last_name, first_name = pitcher_name.split(", ")
                formatted_name = f"{first_name} {last_name}"
                
                # Create a unique PDF filename
                pdf_filename = f"{last_name}_{first_name}-PitchingReport.pdf"
                pdf_path = os.path.join(output_dir, pdf_filename)
                
                # Generate all the plots and data
                print("Generating plots and data...")
                df_pitch_summary = generate_pitch_summary_table(data)
                pitch_location_path = generate_pitch_location_plot(data)
                legend_path = generate_pitch_color_legend(data)
                pitch_movement_path = generate_pitch_movement_plot(data)
                release_point_path = generate_release_point(data)
                velocity_ridgeline_path = velocity_ridgeline_plot(data)
                pitch_usage_path = generate_pitch_usage(data)
                tilt_range_path = generate_tilt_range(data)
                
                # Generate the report
                print(f"Generating PDF report: {pdf_filename}")
                generate_trackman_report(
                    hand_abbreviation, 
                    formatted_name, 
                    df_pitch_summary, 
                    pitch_location_path, 
                    pitch_movement_path,
                    legend_path, 
                    release_point_path, 
                    velocity_ridgeline_path, 
                    pitch_usage_path, 
                    tilt_range_path,
                    pdf_path  # Pass the PDF path to the function
                )
                
                print(f"Successfully processed {pitcher_file}")
            else:
                print(f"Error: Multiple pitchers or throwing hands detected in {pitcher_file}")
                
        except Exception as e:
            print(f"Error processing {pitcher_file}: {str(e)}")
            continue

if __name__ == "__main__":
    # Use the configured input file
    trackman_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), INPUT_FILE)
    print(f"Processing file: {trackman_file}")
    
    # Validate if the file exists before proceeding
    if not os.path.exists(trackman_file):
        print(f"Error: File not found at {trackman_file}")
        sys.exit(1)
    
    # Process all pitchers
    process_all_pitchers(trackman_file) 