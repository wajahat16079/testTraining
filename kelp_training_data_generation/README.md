# Kelpwatch to Sentinel Mask Pipeline

## Step 1

Script: kelp_data_read.py

Description: Reads data from Kelpwatch NetCDF files.

Tasks:

  Reads NetCDF file from Kelpwatch.
  Selects specific quarter/period of interest (dates after January 1, 2018).
  Saves relevant data as CSV files, filtering for locations with kelp biomass.

Run the script from the command line:

With a specified output directory:

  python kelp_data_read.py <path_to_nc_file> --output_dir <output_directory>
  python kelp_data_read.py LandsatKelpBiomass_2024_Q1_withmetadata.nc --output_dir kelp_data_output

Without specifying an output directory (default is kelp_nc_segmented_data):

  python kelp_data_read.py LandsatKelpBiomass_2024_Q1_withmetadata.nc 

LandsatKelpBiomass_2024_Q1_withmetadata.nc is the path to the NetCDF file.
kelp_data_output is the directory where the CSV files will be saved. If not provided, the default directory kelp_nc_segmented_data will be used.


## Step 2

Script: kelp_data_segmentation.py
Description: Segments data for Sentinel tile retrieval.

Tasks:

Reads CSV files from Step 1 containing kelp biomass locations.
Retrieves Sentinel tile data for each location.
Saves Sentinel tile points with item IDs in new CSV files.

Run the script from the command line:


Default:
python kelp_data_segmentation.py 
The CSV files will be saved in the default output directory: kelp_tiles_segmented_data, and the script will read from the default segmented data directory: kelp_nc_segmented_data.

Custom:
python kelp_data_segmentation.py --nc_segmented_data_dir kelp_nc_segmented_data --kelp_tiles_dir kelp_tiles_segmented_data

--nc_segmented_data_dir kelp_nc_segmented_data specifies the directory containing the segmented NetCDF data as CSV files.
--kelp_tiles_dir kelp_tiles_segmented_data specifies the directory to save the filtered Sentinel tile data.

## Step 3

  Script: generate_kelp_mask_tiles.py
  
  Description: Executes main algorithm for processing Sentinel data and generating biomass masks.
  
  Tasks:
  
    Loads CSV files from Step 2 containing item IDs (Sentinel tile information).
    
    Retrieves 10 bands of Sentinel data for each tile.
    
    Build a mask around the coordinates from Kelp CSV.
    
    Apply the mask on (NRI - Red)/ (NRI + Red).
    
    Keep values greater than 0 and calculating the 20th percentile.
    
    Keep values greater than 20th percentile.
    
    Computes biomass sum in the tile and assigns values to each pixel based on band intensity.
    
    Stacks 10 bands plus biomass mask into a single TIF file.
    
    Uploads the TIF file to S3 along with the corresponding CSV file.

Run the script from the command line:

Default
python generate_kelp_mask_tiles.py 

Custom:
python generate_kelp_mask_tiles.py --kelp_tiles_directory "my_tiles" --bucket "my-bucket" --bucket_folder "my-folder"

Options
--kelp_tiles_directory: Directory containing folders with CSV files (default: kelp_tiles_segmented_data).
--bucket: Name of the S3 bucket (default: kelpwatch2).
--bucket_folder: S3 bucket folder for storing results (default: training/full-tiles).
--s3_client: Optional. Boto3 S3 client configuration as a string. If not provided, uses default initialization.



