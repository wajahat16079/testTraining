import pandas as pd
import glob
import os
import argparse

def process_coordinates(data_coast_points_path, folder_path):
    """
    Process coastal coordinates and Sentinel tile coordinates to filter out
    unused coordinates.

    Args:
        data_coast_points_path (str): Path to the CSV file containing coastal points.
        folder_path (str): Path to the folder containing CSV files of Sentinel tile coordinates.

    Returns:
        None
    """
    # Get the absolute path of the current script
    current_file_path = os.path.abspath(__file__)

    # Get the directory of the current script
    current_directory = os.path.dirname(current_file_path)

    # Set the working directory to the current directory
    os.chdir(current_directory)

    print(f"Working directory set to: {os.getcwd()}")

    # Load the coastal points data
    data_coast_points = pd.read_csv(data_coast_points_path)
    print(f"Loaded coastal points data with shape: {data_coast_points.shape}")

    # Use glob to find all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

    # Initialize an empty list to hold the dataframes
    dfs = []

    # Loop through the list of CSV files and read each one into a dataframe
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        dfs.append(df)

    # Concatenate all the dataframes in the list into a single dataframe
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"Combined CSV files into a single dataframe with shape: {combined_df.shape}")

    # Extract unique coordinates from the combined dataframe
    unique_coords_tiles = combined_df[['Latitude', 'Longitude']].drop_duplicates(subset=['Latitude', 'Longitude'])
    print(f"Unique coordinates in tile data: {unique_coords_tiles.shape}")

    # Save the unique coordinates to a CSV file
    unique_coords_tiles.to_csv('unique_coords_tiles.csv', index=False)
    print("Unique coordinates have been saved to 'unique_coords_tiles.csv'.")

def main():
    """
    Main function to process command-line arguments and execute the coordinate processing.
    """
    parser = argparse.ArgumentParser(description='Process coastal points and Sentinel tile coordinates.')
    parser.add_argument('--data_coast_points', type=str, help='Path to the CSV file containing coastal points.')
    parser.add_argument('--folder_path', type=str, help='Path to the folder containing CSV files of Sentinel tile coordinates.')

    args = parser.parse_args()

    # Process the coordinates using the provided paths
    process_coordinates(args.data_coast_points, args.folder_path)

if __name__ == "__main__":
    main()
