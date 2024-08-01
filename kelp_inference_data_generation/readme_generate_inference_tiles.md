# Coast Points Tiles Extraction

This script processes CSV files to extract and consolidate unique coastal tiles information from the given folder path and saves the result to an output CSV file.

## Prerequisites

- Python 3.x
- Sentinel-2 tile data (CSV with tiles IDs)
- AWS S3 bucket

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/YourUsername/your-repository.git
    cd kelp_inference_data_generation/
    ```

2. Install the required Python packages (recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html)):

    ```bash
    pip install xarray numpy matplotlib rioxarray geopandas shapely pyproj planetary-computer pystac-client requests ipython pandas rasterio branca boto3 botocore
    ```

## Usage

### Using the Bash Script

1. Make the script executable:

    ```bash
    chmod +x run_generate_inference_tiles.sh
    ```

2. Run the script:

    ```bash
    ./run_generate_inference_tiles.sh
    ```

   By default, it will use:
   - DEFAULT_BUCKET_NAME="kelpwatch2"
   - DEFAULT_TILES_FILE="path/to/default_tiles_file.csv"
   - DEFAULT_S3_FOLDER_NAME="inference-data/default"


3. **To specify custom paths**:

    ```bash
    ./run_generate_inference_tiles.sh -b your_bucket_name -t path/to/your_tiles_file.csv -f your_s3_folder_name
    ```

### Using Python Directly

Run the Python script from the command line with the required arguments:

```bash
python3 generate_inference_tiles.py --bucket your_bucket_name --tiles-file path_to_your_tiles_file.csv --s3-folder-name your_s3_folder_name
 ```