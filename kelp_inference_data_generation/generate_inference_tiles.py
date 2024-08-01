# pip install xarray numpy matplotlib rioxarray geopandas shapely pyproj planetary-computer pystac-client requests ipython pandas rasterio branca boto3 botocore
import re
import xarray as xr
import copy
import numpy as np
from matplotlib.ticker import ScalarFormatter
import rioxarray
from geopandas import GeoSeries
from shapely.geometry import Point
import pyproj
from pyproj import Transformer
import math
import geopandas as gpd
from shapely.geometry import shape
import planetary_computer
import pystac_client
from pystac_client import Client
import planetary_computer, requests
# import rich.table
import pandas as pd
import matplotlib.pyplot as plt
from rasterio.enums import Resampling
from branca.colormap import LinearColormap
import boto3
from botocore.exceptions import NoCredentialsError
import os
import gc
import argparse

session = boto3.Session()

s3_client = session.client('s3')

# s3 bucket name
bucket = 'kelpwatch2'
# s3_folder_name = 'inference-data/2024-05'


def clean_folder_name(folder_name, part_remove):
    """
    Clean and format the folder name by removing specified parts.
    
    :param folder_name: The original folder name
    :param part_remove: The part of the folder name to remove
    :return: The cleaned folder name
    """
    # Escape special characters in part_remove
    part_remove_pattern = re.escape(part_remove + '/')
    # Remove part_remove from the start of the folder name
    folder_name = re.sub(r'^' + part_remove_pattern, '', folder_name)
    # Remove '.tif' from the end of the folder name
    folder_name = re.sub(r'\.tif/?$', '', folder_name)
    return folder_name

def check_file_exists_s3(s3_client, bucket_name, file_key):
    """
    Check if a file exists in an S3 bucket.
    
    :param s3_client: boto3 S3 client
    :param bucket_name: Name of the S3 bucket
    :param file_key: Key of the file in the S3 bucket
    :return: True if the file exists, False otherwise
    """
    try:
        # Try to get the file's metadata
        s3_client.head_object(Bucket=bucket_name, Key=file_key)
        return True
    except Exception:
        # If any exception occurs (e.g., file not found), return False
        return False

def list_objects_in_folder(bucket_name, prefix):
    """
    List all objects in a specific S3 folder.

    :param bucket_name: Name of the S3 bucket
    :param prefix: Prefix (folder path) to list objects from
    :return: List of object keys in the specified folder
    """
    paginator = s3_client.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    
    all_keys = []
    for response in response_iterator:
        if 'Contents' in response:
            for obj in response['Contents']:
                all_keys.append(obj['Key'])

    return all_keys

def get_bands(selected_item, catalog):
    """
    Retrieve Sentinel-2 bands from a selected item, rescale bands to 10m resolution where applicable, 
    and stack them into a single xarray.Dataset.

    :param selected_item: ID of the Sentinel-2 item to retrieve bands from
    :param catalog: Sentinel-2 instance
    :return: An xarray.Dataset containing the stacked Sentinel-2 bands
    """
    target_resolution = 10  # Target resolution in meters
    scale_factor = 20 / target_resolution  # Scale factor for resampling to 10m resolution

    # Search for the selected item in the Sentinel-2 collection
    search = catalog.search(collections=["sentinel-2-l2a"], ids=[selected_item])
    selected_item = search.item_collection()
    selected_item = selected_item[0]

    # Retrieve and reproject each band from the selected item
    dsB02 = rioxarray.open_rasterio(selected_item.assets["B02"].href, overview_level=0).rename("dsB02")
    dsB02 = dsB02.rio.reproject("EPSG:4326")

    dsB03 = rioxarray.open_rasterio(selected_item.assets["B03"].href, overview_level=0).rename("dsB03")
    dsB03 = dsB03.rio.reproject("EPSG:4326")

    dsB04 = rioxarray.open_rasterio(selected_item.assets["B04"].href, overview_level=0).rename("dsB04")
    dsB04 = dsB04.rio.reproject("EPSG:4326")

    # For bands that need resampling, calculate new dimensions and reproject
    dsB05 = rioxarray.open_rasterio(selected_item.assets["B05"].href, overview_level=0).rename("dsB05")
    new_height = int(dsB05.rio.height * scale_factor)
    new_width = int(dsB05.rio.width * scale_factor)
    dsB05 = dsB05.rio.reproject(dsB05.rio.crs, shape=(new_height, new_width), resampling=Resampling.bilinear)
    dsB05 = dsB05.rio.reproject("EPSG:4326")

    dsB06 = rioxarray.open_rasterio(selected_item.assets["B06"].href, overview_level=0).rename("dsB06")
    new_height = int(dsB06.rio.height * scale_factor)
    new_width = int(dsB06.rio.width * scale_factor)
    dsB06 = dsB06.rio.reproject(dsB06.rio.crs, shape=(new_height, new_width), resampling=Resampling.bilinear)
    dsB06 = dsB06.rio.reproject("EPSG:4326")

    dsB07 = rioxarray.open_rasterio(selected_item.assets["B07"].href, overview_level=0).rename("dsB07")
    new_height = int(dsB07.rio.height * scale_factor)
    new_width = int(dsB07.rio.width * scale_factor)
    dsB07 = dsB07.rio.reproject(dsB07.rio.crs, shape=(new_height, new_width), resampling=Resampling.bilinear)
    dsB07 = dsB07.rio.reproject("EPSG:4326")

    dsB8A = rioxarray.open_rasterio(selected_item.assets["B8A"].href, overview_level=0).rename("dsB8A")
    new_height = int(dsB8A.rio.height * scale_factor)
    new_width = int(dsB8A.rio.width * scale_factor)
    dsB8A = dsB8A.rio.reproject(dsB8A.rio.crs, shape=(new_height, new_width), resampling=Resampling.bilinear)
    dsB8A = dsB8A.rio.reproject("EPSG:4326")

    dsB08 = rioxarray.open_rasterio(selected_item.assets["B08"].href, overview_level=0).rename("dsB08")
    dsB08 = dsB08.rio.reproject("EPSG:4326")

    dsB11 = rioxarray.open_rasterio(selected_item.assets["B11"].href, overview_level=0).rename("dsB11")
    new_height = int(dsB11.rio.height * scale_factor)
    new_width = int(dsB11.rio.width * scale_factor)
    dsB11 = dsB11.rio.reproject(dsB11.rio.crs, shape=(new_height, new_width), resampling=Resampling.bilinear)
    dsB11 = dsB11.rio.reproject("EPSG:4326")

    dsB12 = rioxarray.open_rasterio(selected_item.assets["B12"].href, overview_level=0).rename("dsB12")
    new_height = int(dsB12.rio.height * scale_factor)
    new_width = int(dsB12.rio.width * scale_factor)
    dsB12 = dsB12.rio.reproject(dsB12.rio.crs, shape=(new_height, new_width), resampling=Resampling.bilinear)
    dsB12 = dsB12.rio.reproject("EPSG:4326")

    dsSCL = rioxarray.open_rasterio(selected_item.assets["SCL"].href, overview_level=0).rename("dsSCL")
    new_height = int(dsSCL.rio.height * scale_factor)
    new_width = int(dsSCL.rio.width * scale_factor)
    dsSCL = dsSCL.rio.reproject(dsSCL.rio.crs, shape=(new_height, new_width), resampling=Resampling.bilinear)
    dsSCL = dsSCL.rio.reproject("EPSG:4326")

    dsWVP = rioxarray.open_rasterio(selected_item.assets["WVP"].href, overview_level=0).rename("dsWVP")
    dsWVP = dsWVP.rio.reproject("EPSG:4326")

    dsAOT = rioxarray.open_rasterio(selected_item.assets["AOT"].href, overview_level=0).rename("dsAOT")
    dsAOT = dsAOT.rio.reproject("EPSG:4326")

    # Stack all bands into a single xarray.Dataset
    data_arrays = [dsB02, dsB03, dsB04, dsB05, dsB06, dsB07, dsB8A, dsB08, dsB11, dsB12, dsSCL, dsWVP, dsAOT]
    stacked = xr.concat(data_arrays, dim='band')
    stacked = stacked.assign_coords(band=['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B8A', 'B08', 'B11', 'B12', 'SCL', 'WVP', 'AOT'])

    print("Assets Download and Stack Complete")

    return stacked



def main(bucket, tiles_file, s3_folder_name):
    """
    Main function to process tiles and upload them to S3.

    :param bucket: S3 bucket name
    :param tiles_file: Path to the CSV file containing tile information
    :param s3_folder_name: Folder path in the S3 bucket where results will be uploaded
    """


    catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
    )


    # Set the working directory to the current directory
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    os.chdir(current_directory)
    print(f"Working directory set to: {os.getcwd()}")

    # Read tile information from CSV file
    tiles_df = pd.read_csv(tiles_file)
    print(f"Total tiles for month: {len(tiles_df)}")

    # List and clean existing tiles in S3
    s3_tiles = list_objects_in_folder(bucket, s3_folder_name)
    s3_tiles = [clean_folder_name(folder, s3_folder_name) for folder in s3_tiles]
    print(f"Tiles already processed: {len(s3_tiles)}")

    # Filter out already processed tiles
    tiles_df = tiles_df[~tiles_df['asset'].isin(s3_tiles)]
    tiles_df = tiles_df.reset_index(drop=True)
    print(f"Total tiles to be processed for month: {len(tiles_df)}")
    tiles_df = tiles_df.sample(frac=1).reset_index(drop=True)

    # Process and upload tiles
    for i in range(len(tiles_df)):
        tile = tiles_df['asset'].iloc[i]
        print(f"Tiles left: {len(tiles_df) - i}")
        print(f"Estimated time of completion: {(len(tiles_df) - i) / 60:.2f} hrs")
        print(f"Processing tile number: {i} {tile}")

        raster_file = f"{tile}.tif"
        object_name = f"{s3_folder_name}/{raster_file}"

        if check_file_exists_s3(s3_client, bucket, object_name):
            print(f"{tile} already processed: {len(s3_tiles)}")
            continue

        # Download and stack bands, then save as a raster file
        stacked = get_bands(tile, catalog)
        stacked.rio.to_raster(raster_file)
        print("Bands Merge Complete and Saved")
        del stacked

        # Upload the raster file to S3
        s3_client.upload_file(raster_file, bucket, object_name)
        print("S3 Upload Complete")
        gc.collect()
        os.remove(raster_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Sentinel-2 tiles and upload to S3.")
    parser.add_argument("--bucket", type=str, required=True, help="S3 bucket name")
    parser.add_argument("--tiles-file", type=str, required=True, help="Path to CSV file containing tile information")
    parser.add_argument("--s3-folder-name", type=str, required=True, help="Folder path in S3 bucket where results will be uploaded")

    args = parser.parse_args()
    main(args.bucket, args.tiles_file, args.s3_folder_name)