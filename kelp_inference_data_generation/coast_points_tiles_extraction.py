import pandas as pd
import glob
import os
import argparse

def process_tiles(folder_path, output_csv_path):
    """
    Process CSV files from a specified folder to find unique coastal tiles and save them to a new CSV file.

    Args:
        folder_path (str): Path to the folder containing the input CSV files.
        output_csv_path (str): Path to the output CSV file where unique tiles will be saved.
    """
    # Get the absolute path of the current script
    current_file_path = os.path.abspath(__file__)

    # Get the directory of the current script
    current_directory = os.path.dirname(current_file_path)

    # Set the working directory to the current directory
    os.chdir(current_directory)

    print(f"Working directory set to: {os.getcwd()}")

    # Use glob to find all CSV files in the specified folder
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

    # Initialize an empty list to hold the dataframes
    dfs = []

    # Loop through the list of CSV files and read each one into a dataframe
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        dfs.append(df)

    # Concatenate all the dataframes in the list into a single dataframe
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"Combined DataFrame shape: {combined_df.shape}")

    # Drop duplicate rows based on specific columns to find unique coastal tiles
    unique_tiles = combined_df.drop_duplicates(subset=['asset', 'minx', 'maxx', 'miny', 'maxy', 'cloud_cover'])

    print(f"Unique tiles shape: {unique_tiles.shape}")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    # Save the unique tiles to the specified output CSV file
    unique_tiles.to_csv(output_csv_path, index=False)
    print(f"Unique tiles saved to: {output_csv_path}")

def main():
    """
    Main function to handle command-line arguments and invoke the processing function.
    """
    parser = argparse.ArgumentParser(description="Process coastal tiles to find unique entries and save to a CSV file.")
    parser.add_argument('--folder-path', type=str, required=True, help="Path to the folder containing the input CSV files.")
    parser.add_argument('--output-csv', type=str, required=True, help="Path to the output CSV file where unique tiles will be saved.")
    
    args = parser.parse_args()
    
    process_tiles(args.folder_path, args.output_csv)

if __name__ == "__main__":
    main()
