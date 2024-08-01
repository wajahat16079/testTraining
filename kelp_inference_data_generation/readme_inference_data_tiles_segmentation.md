# Sentinel-2 Inference Data Tiles Segmentation

This program processes coastal coordinates from a CSV file to segment and filter Sentinel-2 imagery based on a specified date range. The resulting segmented data is saved into CSV files.

## Prerequisites

- Python 3.x
- Required Python packages (installable via `requirements.txt`):
  - `geopandas`
  - `shapely`
  - `matplotlib`
  - `pystac-client`
  - `planetary-computer`
  - `requests`
  - `pandas`
  - `math`
  - `glob`
  - `datetime`

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/YourUsername/inference-data-tiles-segmentation.git
    cd inference-data-tiles-segmentation
    ```

2. Install the required Python packages (recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html)):

    ```bash
    pip install geopandas shapely matplotlib pystac-client planetary-computer requests pandas
    ```

## Usage

### Using the Bash Script

1. Make the script executable:

    ```bash
    chmod +x run_inference_data_tiles_segmentation.sh
    ```

2. Run the script with optional arguments:

    ```bash
    ./run_inference_data_tiles_segmentation.sh [--data-kelp <path>] [--date-range <range>] [--csv-dir <directory>]
    ```

   - `--data-kelp <path>`: Path to the CSV file containing kelp data points (default: `unique_coords_tiles.csv`).
   - `--date-range <range>`: Time range for querying Sentinel-2 imagery (default: `2023-01-01/2023-01-31`).
   - `--csv-dir <directory>`: Directory to save the output CSV files (default: `world_monthly_inference_tiles_new`).

### Using Python Directly

Run the Python script from the command line with the required arguments:

```bash
python3 inference_data_tiles_segmentation.py --data_kelp unique_coords_tiles.csv --date_range 2023-01-01/2023-01-31 --csv_dir world_monthly_inference_tiles_new
 ```