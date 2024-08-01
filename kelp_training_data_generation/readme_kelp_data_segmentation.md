# Kelp Data Processor

This program processes kelp biomass data from CSV files derived from NetCDF files. It filters the data based on bounding boxes and time ranges, then saves the filtered results to CSV files. The script utilizes `geopandas` for geospatial operations and `pandas` for data manipulation.

## Prerequisites

- Python 3.x
- Required Python packages: `geopandas`, `shapely`, `matplotlib`, `pandas`, `numpy`, `pystac_client`, `planetary_computer`

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/YourUsername/your-repo.git
    cd your-repo
    ```

2. Install the required Python packages (recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html)):

    ```bash
    pip install geopandas shapely matplotlib pandas numpy pystac_client planetary_computer
    ```

## Usage

The Kelp Data Processor can be run using the provided bash script or directly with Python.

### Using the Bash Script

1. Create the bash script file and make it executable:

    ```bash
    chmod +x run_kelp_data_segmentation.sh
    ```

    If there are any syntax errors due to Windows line endings, convert the script to Unix format:

    ```bash
    sed -i 's/\r$//' run_kelp_data_segmentation.sh
    ```

2. Run the script with default parameters:

    ```bash
    ./run_kelp_data_segmentation.sh
    ```

3. Or customize the parameters:

    ```bash
    ./run_kelp_data_segmentation.sh --nc-segmented-data-dir "path/to/segmented_data" --kelp-tiles-dir "path/to/output_directory"
    ```

4. Or open the script and edit the default values for the parameters.

### Using Python Directly

Run the Python script from the command line with the required arguments:

```bash
python3 kelp_data_segmentation.py --nc_segmented_data_dir path/to/segmented_data --kelp_tiles_dir path/to/output_directory
 ```