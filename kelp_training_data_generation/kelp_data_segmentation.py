import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from geopandas import GeoSeries
import os
import pystac_client
from pystac_client import Client
import planetary_computer, requests
import pandas as pd
import math
import glob
from datetime import datetime
import argparse

def calculate_bbox(lon, lat, shift_meters=30):
    """
    Calculate the bounding box for a given point with a specified shift in meters.

    Args:
        lon (float): Longitude of the point.
        lat (float): Latitude of the point.
        shift_meters (int): Shift distance in meters. Default is 30 meters.

    Returns:
        list: Bounding box coordinates [min_lon, min_lat, max_lon, max_lat].
    """
    # Convert latitude shift to degrees
    lat_shift_deg = shift_meters / 111000  # 111 km in meters

    # Convert longitude shift to degrees, accounting for the latitude
    lon_shift_deg = shift_meters / (111000 * math.cos(math.radians(lat)))

    # Construct the bounding box with a 30-meter shift
    bbox = [lon - lon_shift_deg, lat - lat_shift_deg, lon + lon_shift_deg, lat + lat_shift_deg]

    return bbox

def get_quarter_range(sdate):
    """
    Get the quarterly time range for a given date.

    Args:
        sdate (str): Start date in 'YYYY-MM-DD' format.

    Returns:
        str: Time range in 'YYYY-MM-DD/YYYY-MM-DD' format for the quarter.
    """
    # Convert the start date string to datetime object
    start_date = datetime.strptime(sdate, '%Y-%m-%d')
    
    # Determine the quarter
    quarter = (start_date.month - 1) // 3 + 1
    
    # Calculate the quarterly time range based on the quarter
    if quarter == 1:
        # Q1: January 1 to March 31
        time_range = f"{start_date.year}-01-01/{start_date.year}-03-31"
    elif quarter == 2:
        # Q2: April 1 to June 30
        time_range = f"{start_date.year}-04-01/{start_date.year}-06-30"
    elif quarter == 3:
        # Q3: July 1 to September 30
        time_range = f"{start_date.year}-07-01/{start_date.year}-09-30"
    elif quarter == 4:
        # Q4: October 1 to December 31
        time_range = f"{start_date.year}-10-01/{start_date.year}-12-31"
    else:
        # Handle edge case (though this should not happen with valid dates)
        raise ValueError("Invalid date provided.")
    
    return time_range

def process_point(data_kelp, rowNum, directory):
    """
    Process a single point to filter and save relevant kelp biomass data.

    Args:
        data_kelp (DataFrame): DataFrame containing kelp data.
        rowNum (int): Row number of the point to process.
        directory (str): Directory to save the filtered CSV files.

    Returns:
        None
    """
    # Extract latitude and longitude of the point at row 'rowNum'
    lat = data_kelp.iloc[rowNum]["latitude"]
    lon = data_kelp.iloc[rowNum]["longitude"]
    print(f"Processing Q {data_kelp.iloc[rowNum]["quarter"]} {data_kelp.iloc[rowNum]["year"]}  point at row {rowNum}: lon={lon}, lat={lat}")

    # Define the time range for the search
    time_range = get_quarter_range(data_kelp.iloc[0]['time'])

    # Calculate the bounding box for the given latitude and longitude with a 300m buffer
    bbox = calculate_bbox(lon, lat, 300)

    # Search the Sentinel-2 L2A collection for items within the bounding box and time range
    search = catalog.search(collections=["sentinel-2-l2a"], bbox=bbox, datetime=time_range)
    items = search.item_collection()

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
    selected_item = items[selected_item_ID]

    # Extract the bounding box coordinates of the selected item
    min_lon, min_lat, max_lon, max_lat = selected_item.bbox

    # Filter the kelp data to include only points within the selected bounding box
    filtered_kelp_data = data_kelp[(data_kelp['latitude'] >= min_lat) &
                                   (data_kelp['latitude'] <= max_lat) &
                                   (data_kelp['longitude'] >= min_lon) &
                                   (data_kelp['longitude'] <= max_lon)].copy()

    print(filtered_kelp_data.shape)
    # Mark the filtered data as processed
    filtered_kelp_data['proccessed_flag'] = 1
    filtered_kelp_data['asset'] = selected_item.id

    # Construct the file path for the CSV file
    file_path = f"{directory}/{selected_item.id}.csv"

    # Save the filtered data to a CSV file
    filtered_kelp_data.to_csv(file_path, index=False)

    # Update the processed flag in the original dataset
    data_kelp.loc[filtered_kelp_data.index, 'proccessed_flag'] = 1

def main(nc_segmented_data_dir='kelp_nc_segmented_data', kelp_tiles_dir='kelp_tiles_segmented_data'):
    """
    Main function to process kelp data and save filtered results to CSV files.

    Args:
        nc_segmented_data_dir (str): Directory containing the segmented NetCDF data as CSV files.
        kelp_tiles_dir (str): Directory to save the filtered kelp data tiles.

    Returns:
        None
    """
    # Create the output directory if it doesn't exist
    os.makedirs(kelp_tiles_dir, exist_ok=True)

    # Get the list of all CSV files in the directory
    csv_files = glob.glob(os.path.join(nc_segmented_data_dir, '*.csv'))

    for c in csv_files:
        # Load the data
        data_kelp = pd.read_csv(c)
        data_kelp['proccessed_flag'] = 0
        data_kelp['ID'] = range(1, len(data_kelp) + 1)

        csv_dir = os.path.splitext(os.path.basename(c))[0]
        csv_dir = f"{kelp_tiles_dir}/{csv_dir}" 
        os.makedirs(csv_dir, exist_ok=True)

        # Iterate until all points are processed
        while True:
            # Find indices of unprocessed rows
            unprocessed_indices = data_kelp[data_kelp['proccessed_flag'] == 0].index
            # Break the loop if all points are processed
            if len(unprocessed_indices) == 0:
                break
            # Process the first unprocessed point
            rowNum = unprocessed_indices[0]
            process_point(data_kelp, rowNum, csv_dir)
            # Update the processed flag for the current point
            data_kelp.loc[rowNum, 'proccessed_flag'] = 1

        print(f"{csv_dir} All points processed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process kelp data and save filtered results to CSV files.')
    parser.add_argument('--nc_segmented_data_dir', type=str, default='kelp_nc_segmented_data', help='Directory containing the segmented NetCDF data as CSV files.')
    parser.add_argument('--kelp_tiles_dir', type=str, default='kelp_tiles_segmented_data', help='Directory to save the filtered kelp data tiles.')
    args = parser.parse_args()

    # Open the STAC catalog
    global catalog
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    main(args.nc_segmented_data_dir, args.kelp_tiles_dir)
