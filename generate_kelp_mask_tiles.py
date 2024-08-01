import argparse
import re
import copy
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
from rasterio.enums import Resampling
import rioxarray
import geopandas as gpd
from shapely.geometry import Point
from geopandas import GeoSeries
import pyproj
from pyproj import Transformer
import math
import planetary_computer
import pystac_client
from pystac_client import Client
import boto3
from botocore.exceptions import NoCredentialsError
import os

def clean_folder_name(folder_name):
    """
    Clean the folder name by removing 'training/' prefix and '_label' suffix.
    
    Args:
        folder_name (str): The original folder name.
        
    Returns:
        str: The cleaned folder name.
    """
    folder_name = re.sub(r'^training/', '', folder_name)  # Remove 'training/' at the start
    folder_name = re.sub(r'_label/$', '', folder_name)     # Remove '_label' at the end
    return folder_name

def calculate_bbox(lon, lat, shift_meters=30):
    """
    Calculate a bounding box around the specified coordinates with a given shift in meters.
    
    Args:
        lon (float): Longitude of the center point.
        lat (float): Latitude of the center point.
        shift_meters (int): The shift distance in meters to create the bounding box.
        
    Returns:
        list: Bounding box coordinates [min_lon, min_lat, max_lon, max_lat].
    """
    lat_shift_deg = shift_meters / 111000  # Convert latitude shift to degrees
    lon_shift_deg = shift_meters / (111000 * math.cos(math.radians(lat)))  # Convert longitude shift to degrees

    bbox = [lon - lon_shift_deg, lat - lat_shift_deg, lon + lon_shift_deg, lat + lat_shift_deg]
    return bbox


def list_s3_folders(s3_client, bucket, prefix):
    """
    List all folders with a given prefix in an S3 bucket, handling pagination.
    """
    folders = []
    continuation_token = None

    while True:
        list_kwargs = {
            'Bucket': bucket,
            'Prefix': prefix,
            'Delimiter': '/'
        }
        
        if continuation_token:
            list_kwargs['ContinuationToken'] = continuation_token

        response = s3_client.list_objects_v2(**list_kwargs)
        
        # Collect folders from the response
        folders.extend([content['Prefix'] for content in response.get('CommonPrefixes', [])])
        
        # Check if there's more data to fetch
        if response.get('IsTruncated'):  # if response is truncated, more pages exist
            continuation_token = response.get('NextContinuationToken')
        else:
            break

    return folders

def clean_folder_name(folder_name):
    """
    Extract the last delimited element and remove '_label' suffix.
    """
    # Split the folder name by '/' to get the last part
    last_element = folder_name.split('/')[-2]
    
    # Remove the '_label' suffix if present
    if last_element.endswith('_label'):
        last_element = last_element[:-6]  # Remove '_label'
    
    return last_element

def process_folders(kelp_tiles_directory, bucket,bucket_folder, s3_client, catalog):
    """
    Process each folder in the specified directory, downloading and processing Sentinel-2 data.
    
    Args:
        kelp_tiles_directory (str): Directory containing the folders with CSV files.
        bucket (str): S3 bucket name.
        s3_client (boto3.client): Boto3 S3 client.
        catalog (pystac_client.Catalog): STAC catalog for searching Sentinel-2 items.
    """

    # bucket = 'kelpwatch2'
    # kelp_tiles_directory = "kelp_tiles_segmented_data"
    # bucket_folder = "training/check"
    # bucket_folder = "training/full-tiles"
    # s3_client 
    # catalog

    folders = [f for f in os.listdir(kelp_tiles_directory) if os.path.isdir(os.path.join(kelp_tiles_directory, f))]

    for f in folders:
        print(f)
        directory = f"{kelp_tiles_directory}/{f}"
        df_list = []

        # Read all CSV files in the folder
        for filename in os.listdir(directory):
            if filename.endswith(".csv"):
                filepath = os.path.join(directory, filename)
                df = pd.read_csv(filepath)
                df_list.append(df)

        for df in df_list:
            print(df.shape)

            if len(df) < 1:
                print("No Data")
                continue

            data_kelp = df
            rowNum = 0

            lat = data_kelp.iloc[rowNum]["latitude"]
            lon = data_kelp.iloc[rowNum]["longitude"]
            itemID = data_kelp.iloc[rowNum]["asset"]
            # prefix = "training/"
            prefix = f'{bucket_folder}/'
            response = list_s3_folders(s3_client, bucket, prefix)
            cleaned_folders = [clean_folder_name(folder) for folder in response]

            if itemID in cleaned_folders:
                print(f"{itemID} already processed")
                continue

            bbox = calculate_bbox(lon, lat, 300)
            search = catalog.search(collections=["sentinel-2-l2a"], ids=[itemID])
            items = search.item_collection()
            df_NC = gpd.GeoDataFrame.from_features(items.to_dict(), crs="epsg:4326")
            df_NC = df_NC.assign(item_ID=range(0, len(df_NC)))
            df_NC = df_NC.sort_values("eo:cloud_cover", ascending=True)
            df_NC_BB = df_NC["geometry"].bounds
            point = Point(lon, lat)
            projected_crs = "EPSG:32610"
            df_NC_BB['centroid'] = GeoSeries(df_NC["geometry"]).to_crs(projected_crs).centroid
            df_NC_BB['centrality'] = df_NC_BB['centroid'].apply(lambda c: point.distance(c))
            df_NC_BB['eo:cloud_cover'] = df_NC['eo:cloud_cover']
            df_NC_BB['item_ID'] = df_NC['item_ID']
            df_NC_BB_sorted = df_NC_BB.sort_values(by=['eo:cloud_cover', 'centrality'])
            selected_item_ID = df_NC_BB_sorted['item_ID'].iloc[0]
            bbox_NC = df_NC.iloc[selected_item_ID]["geometry"].bounds
            selected_item = items[selected_item_ID]

            print("Asset Selection Complete")

            # Define target resolution and scale factor
            target_resolution = 10  # meters
            scale_factor = 20 / target_resolution

            # Open and reproject Sentinel-2 bands
            dsNRI = rioxarray.open_rasterio(selected_item.assets["B08"].href, overview_level=0)
            dsRed = rioxarray.open_rasterio(selected_item.assets["B04"].href, overview_level=0)
            dsNRI = dsNRI.rio.reproject("EPSG:4326")
            dsRed = dsRed.rio.reproject("EPSG:4326")

            dsB02 = rioxarray.open_rasterio(selected_item.assets["B02"].href, overview_level=0).rename("dsB02").rio.reproject("EPSG:4326")
            dsB03 = rioxarray.open_rasterio(selected_item.assets["B03"].href, overview_level=0).rename("dsB03").rio.reproject("EPSG:4326")
            dsB04 = rioxarray.open_rasterio(selected_item.assets["B04"].href, overview_level=0).rename("dsB04").rio.reproject("EPSG:4326")
            dsB05 = rioxarray.open_rasterio(selected_item.assets["B05"].href, overview_level=0).rename("dsB05")
            dsB05 = dsB05.rio.reproject(dsB05.rio.crs, shape=(int(dsB05.rio.height * scale_factor), int(dsB05.rio.width * scale_factor)), resampling=Resampling.bilinear)
            dsB05 = dsB05.rio.reproject("EPSG:4326")
            dsB06 = rioxarray.open_rasterio(selected_item.assets["B06"].href, overview_level=0).rename("dsB06")
            dsB06 = dsB06.rio.reproject(dsB06.rio.crs, shape=(int(dsB06.rio.height * scale_factor), int(dsB06.rio.width * scale_factor)), resampling=Resampling.bilinear)
            dsB06 = dsB06.rio.reproject("EPSG:4326")
            dsB07 = rioxarray.open_rasterio(selected_item.assets["B07"].href, overview_level=0).rename("dsB07")
            dsB07 = dsB07.rio.reproject(dsB07.rio.crs, shape=(int(dsB07.rio.height * scale_factor), int(dsB07.rio.width * scale_factor)), resampling=Resampling.bilinear)
            dsB07 = dsB07.rio.reproject("EPSG:4326")
            dsB8A = rioxarray.open_rasterio(selected_item.assets["B8A"].href, overview_level=0).rename("dsB8A")
            dsB8A = dsB8A.rio.reproject(dsB8A.rio.crs, shape=(int(dsB8A.rio.height * scale_factor), int(dsB8A.rio.width * scale_factor)), resampling=Resampling.bilinear)
            dsB8A = dsB8A.rio.reproject("EPSG:4326")
            dsB08 = rioxarray.open_rasterio(selected_item.assets["B08"].href, overview_level=0).rename("dsB08").rio.reproject("EPSG:4326")
            dsB11 = rioxarray.open_rasterio(selected_item.assets["B11"].href, overview_level=0).rename("dsB11")
            dsB11 = dsB11.rio.reproject(dsB11.rio.crs, shape=(int(dsB11.rio.height * scale_factor), int(dsB11.rio.width * scale_factor)), resampling=Resampling.bilinear)
            dsB11 = dsB11.rio.reproject("EPSG:4326")
            dsB12 = rioxarray.open_rasterio(selected_item.assets["B12"].href, overview_level=0).rename("dsB12")
            dsB12 = dsB12.rio.reproject(dsB12.rio.crs, shape=(int(dsB12.rio.height * scale_factor), int(dsB12.rio.width * scale_factor)), resampling=Resampling.bilinear)
            dsB12 = dsB12.rio.reproject("EPSG:4326")

            print("Assets Download Complete")

            # Create a binary mask for the NIR band
            dsNRI_mask_binary = copy.deepcopy(dsNRI)
            dsNRI_mask_binary.data[0, :, :] = 0

            # Define the bounding box shifts in meters
            extend_meters_left = 10
            extend_meters_right = 40
            extend_meters_down = 40
            extend_meters_up = 10

            tuning_per = 1.1
            lat_shift_deg_down = (extend_meters_down / 111000) * tuning_per
            lat_shift_deg_up = (extend_meters_up / 111000) * tuning_per
            lon_shift_deg_right = (extend_meters_right / (111000 * math.cos(math.radians(lat)))) * tuning_per
            lon_shift_deg_left = (extend_meters_left / (111000 * math.cos(math.radians(lat)))) * tuning_per

            # Process the binary mask with the calculated bounding box shifts
            for data_row in data_kelp.index:
                # Calculate the minimum and maximum longitude and latitude for the bounding box
                minx = data_kelp.loc[data_row, 'longitude'] - lon_shift_deg_left
                miny = data_kelp.loc[data_row, 'latitude'] - lat_shift_deg_down
                maxx = minx + lon_shift_deg_right
                maxy = data_kelp.loc[data_row, 'latitude'] + lat_shift_deg_up

                # Check if the bounding box provides sufficient area for clipping
                if minx != maxx and miny != maxy:
                    try:
                        # Clip the raster dataset based on the bounding box
                        ds_32610_clipped_loop = dsNRI_mask_binary.rio.clip_box(minx=minx, miny=miny, maxx=maxx, maxy=maxy)
                        # Loop through the clipped coordinates to update the binary mask
                        for lonX_clipped in ds_32610_clipped_loop.coords['x'].values:
                            for latY_clipped in ds_32610_clipped_loop.coords['y'].values:
                                # Find the indices of the clipped coordinates in the original dataset
                                x_index = np.where(dsNRI_mask_binary.coords['x'].values == lonX_clipped)[0]
                                y_index = np.where(dsNRI_mask_binary.coords['y'].values == latY_clipped)[0]
                                # Update the binary mask with ones at the clipped coordinate indices
                                dsNRI_mask_binary.data[0, int(y_index), int(x_index)] = 1
                    except Exception as e:
                        # Print an error message and skip the current row if an exception occurs
                        print(f"Skipping row {data_row} due to error: {e}")
                else:
                    # Print a message and skip the current row if the bounding box is insufficient
                    print(f"Skipping row {data_row} due to insufficient area for clipping.")

            # Print a confirmation message
            print("Binary Mask Complete")


            # Convert the data of dsNRI_mask_binary and dsRed to float for calculations
            dsNRI_mask_binary.data = np.array(dsNRI_mask_binary.data, dtype=float)
            dsRed.data = np.array(dsRed.data, dtype=float)

            # Create a mask for NRI - RED
            ds_NRI_Red_mask_binary = copy.deepcopy(dsRed)
            # Compute the normalized difference between dsNRI and dsRed
            ds_NRI_Red_mask_binary.data = (dsNRI.data - ds_NRI_Red_mask_binary.data) / (dsNRI.data + ds_NRI_Red_mask_binary.data + 1e-12)

            # Apply the binary mask to the normalized difference
            ds_NRI_Red_mask_binary.data = ds_NRI_Red_mask_binary.data * dsNRI_mask_binary.data  

            # Flatten the data and consider only non-zero values for percentile calculation
            data = ds_NRI_Red_mask_binary.data.flatten()
            data = data[data > 0]
            if len(data) < 1:
                print("No Data")
                continue

            # Calculate the 20th percentile of the data
            threshold_NRI = np.percentile(data, [20])[0]
            
            percentile_label = '20th'

            # Create a copy of the mask for thresholding
            mask_NRI_copy = copy.deepcopy(ds_NRI_Red_mask_binary)

            # Apply the threshold to create a binary mask
            mask_NRI_copy.data[0, :, :][mask_NRI_copy.data[0, :, :] < threshold_NRI] = 0

            # Sum the values of the masked data
            sum_band = np.sum(mask_NRI_copy.data)

            # Calculate the total biomass from the data_kelp DataFrame
            total_biomass = data_kelp['biomass'].sum(axis=0)

            # Normalize the masked data to the total biomass
            mask_NRI_copy.data[0, :, :] = (mask_NRI_copy.data[0, :, :] / sum_band) * total_biomass

            # Print confirmation message for the completion of the biomass mask
            print("Biomass Mask Complete")

            # Rename the mask to "dsBioMass"
            mask_NRI_copy = mask_NRI_copy.rename("dsBioMass")

            # Convert the data to uint16 for saving
            mask_NRI_copy.data = np.array(mask_NRI_copy.data, dtype=np.uint16)

            # Stack the bands into a single dataset
            data_arrays = [dsB02, dsB03, dsB04, dsB05, dsB06, dsB07, dsB8A, dsB08, dsB11, dsB12, mask_NRI_copy]
            stacked = xr.concat(data_arrays, dim='band')
            stacked = stacked.assign_coords(band=['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B8A', 'B08', 'B11', 'B12', 'mask_biomass'])
            stacked.rio.write_crs("EPSG:4326", inplace=True)  

            # Define the raster file name and save it
            raster_file = f"{itemID}.tif"
            stacked.rio.to_raster(raster_file)

            # Print confirmation message for the completion of band merging and saving
            print("Bands Merge Complete and Saved")

            # Define the subfolder name for S3
            sub_folder_name = f"{itemID}_label"
            object_name = f"{bucket_folder}/{sub_folder_name}/{raster_file}"

            # Upload the raster file to S3
            s3_client.upload_file(raster_file, bucket, object_name)

            # Define the CSV file name and save the DataFrame
            csv_file = f"{itemID}.csv"
            data_kelp.to_csv(csv_file, index=False)

            # Upload the CSV file to S3
            object_name = f"{bucket_folder}/{sub_folder_name}/{csv_file}"
            s3_client.upload_file(csv_file, bucket, object_name)

            # Print confirmation message for the completion of S3 upload
            print("S3 Upload Complete")

            # Remove the local copies of the CSV and raster files
            os.remove(csv_file)
            os.remove(raster_file)


if __name__ == "__main__":
    print("incode")
    parser = argparse.ArgumentParser(description="Process Sentinel-2 imagery and generate binary masks.")
    parser.add_argument("--kelp_tiles_directory", type=str, default="kelp_tiles_segmented_data", help="Directory containing folders with CSV files.")
    parser.add_argument("--bucket", type=str, default="kelpwatch2", help="S3 bucket.")
    parser.add_argument("--bucket_folder", type=str, default="training/full-tiles", help="S3 bucket folder.")  
    args = parser.parse_args()

    session = boto3.Session()

    s3_client = session.client('s3')

    # Initialize STAC catalog
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    # Process folders
    process_folders(args.kelp_tiles_directory, args.bucket, args.bucket_folder, s3_client, catalog)


