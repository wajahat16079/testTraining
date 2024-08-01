import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from geopandas import GeoSeries
import os
import pystac_client
from pystac_client import Client
import planetary_computer
import pandas as pd
import math
import glob
from datetime import datetime
import argparse

def calculate_bbox(lon, lat, shift_meters=30):
    """
    Calculate a bounding box around a given point (longitude, latitude) with a specified buffer in meters.

    Args:
        lon (float): Longitude of the center point.
        lat (float): Latitude of the center point.
        shift_meters (int): Buffer distance in meters.

    Returns:
        list: Bounding box coordinates [lon_min, lat_min, lon_max, lat_max].
    """
    # Convert latitude shift to degrees
    lat_shift_deg = shift_meters / 111000  # 111 km in meters

    # Convert longitude shift to degrees, accounting for the latitude
    lon_shift_deg = shift_meters / (111000 * math.cos(math.radians(lat)))

    # Calculate adjusted longitude values to ensure they are within valid range
    lon_min = lon - lon_shift_deg
    lon_max = lon + lon_shift_deg

    # Adjust longitude if it goes beyond the valid range
    if lon_min < -180:
        lon_min = -180
    if lon_max > 180:
        lon_max = 180

    # Calculate adjusted latitude values to ensure they are within valid range
    lat_min = lat - lat_shift_deg
    lat_max = lat + lat_shift_deg

    # Adjust latitude if it goes beyond the valid range
    if lat_min < -90:
        lat_min = -90
    if lat_max > 90:
        lat_max = 90

    # Construct the bounding box with adjusted values
    bbox = [lon_min, lat_min, lon_max, lat_max]

    return bbox

def process_point(catalog, data_kelp_temp, rowNum, directory, cloud_threshold, date_range):
    """
    Process a single data point to find and save Sentinel-2 imagery data within the bounding box.

    Args:
        catalog (sentinel instance): API
        data_kelp_temp (DataFrame): DataFrame containing the kelp coordinates.
        rowNum (int): Row number of the point to process.
        directory (str): Directory to save the output CSV files.
        cloud_threshold (float): Cloud cover threshold to filter the imagery.
        date_range (str): Time range to query Sentinel-2 imagery.
    """
    # Extract latitude and longitude of the point at row 'rowNum'
    lat = data_kelp_temp.iloc[rowNum]["Latitude"]
    lon = data_kelp_temp.iloc[rowNum]["Longitude"]

    print(f"Processing point at row {rowNum}: lon={lon}, lat={lat}")

    # Calculate the bounding box for the given latitude and longitude with a 300m buffer
    bbox = calculate_bbox(lon, lat, 300)

    # Search the Sentinel-2 L2A collection for items within the bounding box and time range
    search = catalog.search(collections=["sentinel-2-l2a"], bbox=bbox, datetime=date_range)
    items = search.item_collection()

    if len(items.to_dict()['features']) == 0:
        print("No features found.")
        data_kelp_temp.loc[rowNum, 'processed_flag'] = 1
        return

    # Convert the search results to a GeoDataFrame
    df_NC = gpd.GeoDataFrame.from_features(items.to_dict(), crs="epsg:4326")
    df_NC = df_NC.assign(item_ID=range(0, len(df_NC)))
    df_NC = df_NC.sort_values("eo:cloud_cover", ascending=True)
    df_NC_BB = df_NC["geometry"].bounds

    # Calculate the centrality of each bounding box relative to the point
    point = Point(lon, lat)
    projected_crs = "EPSG:32610"
    df_NC_BB['centroid'] = GeoSeries(df_NC["geometry"]).to_crs(projected_crs).centroid
    df_NC_BB['centrality'] = df_NC_BB['centroid'].apply(lambda c: point.distance(c))
    df_NC_BB['eo:cloud_cover'] = df_NC['eo:cloud_cover']
    df_NC_BB['item_ID'] = df_NC['item_ID']

    # Sort the bounding boxes by cloud cover and centrality to find the best match
    df_NC_BB_sorted = df_NC_BB.sort_values(by=['eo:cloud_cover', 'centrality'])
    selected_item_ID = df_NC_BB_sorted['item_ID'].iloc[0]
    cloud_cover = df_NC_BB_sorted['eo:cloud_cover'].iloc[0]
    selected_item = items[selected_item_ID]
    minx = df_NC_BB_sorted['minx'].iloc[0]
    maxx = df_NC_BB_sorted['maxx'].iloc[0]
    miny = df_NC_BB_sorted['miny'].iloc[0]
    maxy = df_NC_BB_sorted['maxy'].iloc[0]

    # Extract the bounding box coordinates of the selected item
    min_lon, min_lat, max_lon, max_lat = selected_item.bbox

    # Filter the kelp data to include only points within the selected bounding box
    filtered_kelp_data = data_kelp_temp[(data_kelp_temp['Latitude'] >= min_lat) &
                                   (data_kelp_temp['Latitude'] <= max_lat) &
                                   (data_kelp_temp['Longitude'] >= min_lon) &
                                   (data_kelp_temp['Longitude'] <= max_lon)].copy()

    print(filtered_kelp_data.shape)

    # Mark the filtered data as processed
    filtered_kelp_data['processed_flag'] = 1
    filtered_kelp_data['asset'] = selected_item.id
    filtered_kelp_data['cloud_cover'] = cloud_cover
    filtered_kelp_data['minx'] = minx
    filtered_kelp_data['maxx'] = maxx
    filtered_kelp_data['miny'] = miny
    filtered_kelp_data['maxy'] = maxy

    # Construct the file path for the CSV file
    file_path = f"{directory}/{selected_item.id}.csv"

    filtered_kelp_data.to_csv(file_path, index=False)

    # Update the processed flag in the original dataset
    data_kelp_temp.loc[filtered_kelp_data.index, 'processed_flag'] = 1

def main(data_kelp_path, date_range, csv_dir):
    """
    Main function to process kelp data and extract Sentinel-2 imagery.

    Args:
        data_kelp_path (str): Path to the CSV file containing kelp data points.
        date_range (str): Time range for querying Sentinel-2 imagery.
        csv_dir (str): Directory to save the output CSV files.
    """
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    # Load kelp data from CSV file
    data_kelp = pd.read_csv(data_kelp_path)
    print(data_kelp.shape)

    # Define the bounding box to filter out unnecessary points
    minX = -106.5653984
    minY = 54.0504964
    maxX = -104.8472467
    maxY = 55.0468902

    # Remove points that fall within the bounding box
    data_kelp = data_kelp[~((data_kelp['Latitude'] >= minY) & (data_kelp['Latitude'] <= maxY) & 
                            (data_kelp['Longitude'] >= minX) & (data_kelp['Longitude'] <= maxX))]
    data_kelp = data_kelp.reset_index(drop=True)

    # Add necessary columns
    data_kelp['processed_flag'] = 0
    data_kelp['ID'] = range(1, len(data_kelp) + 1)

    print(data_kelp.shape)

    os.makedirs(csv_dir, exist_ok=True)

    # Process each point in the data
    while True:
        # Find indices of unprocessed rows
        unprocessed_indices = data_kelp[data_kelp['processed_flag'] == 0].index
        # Break the loop if all points are processed
        if len(unprocessed_indices) == 0:
            break

        # Process the first unprocessed point
        rowNum = unprocessed_indices[0]
        process_point(catalog, data_kelp, rowNum, csv_dir, 100, date_range)
        # Update the processed flag for the current point
        data_kelp.loc[rowNum, 'processed_flag'] = 1

    print(f"{csv_dir} All points processed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process kelp data and extract Sentinel-2 imagery.")
    parser.add_argument('--data_kelp', type=str, required=True, help="Path to the CSV file containing kelp data points.")
    parser.add_argument('--date_range', type=str, required=True, help="Time range for querying Sentinel-2 imagery.")
    parser.add_argument('--csv_dir', type=str, required=True, help="Directory to save the output CSV files.")
    
    args = parser.parse_args()
    main(args.data_kelp, args.date_range, args.csv_dir)
