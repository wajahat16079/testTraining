import xarray as xr
import pandas as pd
import os
import numpy as np
import argparse

def main(nc_file, output_dir='kelp_nc_segmented_data'):
    """
    Process NetCDF file to filter biomass data and save it to CSV files.

    Args:
        nc_file (str): Path to the NetCDF file.
        output_dir (str, optional): Directory to save the CSV files. Defaults to 'kelp_nc_segmented_data'.

    Returns:
        None
    """
    
    # Open the NetCDF file as an xarray Dataset
    data = xr.open_dataset(nc_file)
    
    # Extract the time values from the dataset
    list_time = data.time
    
    # Convert the string date to a numpy datetime64 object
    date_threshold = np.datetime64('2018-01-01')
    
    # Filter the time values greater than the date threshold
    filtered_time = list_time.where(list_time > date_threshold, drop=True)
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    for t in filtered_time:
        filter_time = t.dt.strftime('%Y-%m-%d').values.tolist()
        specific_time_data = data.sel(time=filter_time)
        
        # Convert the selected data to a pandas DataFrame
        data_df = specific_time_data.to_dataframe()
        
        # Filter the DataFrame to include only rows where the biomass value is greater than 0
        data_df_biomass = data_df.query('biomass > 0')
        
        file_name = f'{output_dir}/data_df_biomass_{filter_time}.csv'
        
        # Save the filtered DataFrame to a CSV file
        data_df_biomass.to_csv(file_name, index=True)  
        
        # Print a confirmation message
        print(f"{file_name} has been saved")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process NetCDF file to filter biomass data and save to CSV.')
    parser.add_argument('--nc_file', type=str, help='Path to the NetCDF file.')
    parser.add_argument('--output_dir', type=str, default='kelp_nc_segmented_data', help='Directory to save the CSV files.')

    args = parser.parse_args()
    
    main(args.nc_file, args.output_dir)