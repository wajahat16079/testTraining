import pandas as pd
import glob
import os
import pandas as pd


# this step is added to ensure that we fiter out the coordinates which are not coverd by the santinel
#  this saves time when we are gnearting tiles for each month

# Get the absolute path of the current script
current_file_path = os.path.abspath(__file__)

# Get the directory of the current script
current_directory = os.path.dirname(current_file_path)

# Set the working directory to the current directory
os.chdir(current_directory)

print(f"Working directory set to: {os.getcwd()}")

## path to the actual csv generated from the geojson
data_coast_points = pd.read_csv("coastal_points_extraction_from_geojson/coastline-coordinate-data.csv")
print(data_coast_points.shape)

## path of all the csv files generated for june 2024
folder_path = 'world_monthly_inference_tiles/coastal_tiles_world_2024_06'

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
print(combined_df.shape)
unique_coords_tiles = combined_df[['Latitude', 'Longitude']]
unique_coords_tiles = unique_coords_tiles.drop_duplicates(subset=['Latitude', 'Longitude'])
print(unique_coords_tiles.shape)

unique_coords_tiles.to_csv('unique_coords_tiles.csv', index=False)
