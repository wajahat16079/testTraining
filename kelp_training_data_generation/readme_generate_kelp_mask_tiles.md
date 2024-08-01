# Satellite Image Processor - Chipify

This program processes large satellite images (GeoTIFFs) stored in an S3 bucket. It segments these images into smaller chips and uploads the chips back to S3, utilizing multiprocessing for efficient processing.

## Prerequisites

- Python 3.x
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate S3 access permissions
-  kelp_tiles_segmented_data: Directory containing folders with CSV files for each tile

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/Coastal-Carbon/factory-seekelp.git
    cd kelp_training_data_generation
    ```

2. Install the required Python packages (recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html)):

    ```bash
    pip install boto3 rasterio xarray pandas matplotlib geopandas pyproj planetary_computer pystac_client rioxarray
    ```

## Usage

The tile generator can be run using the provided bash script or directly with Python.

### Using the Bash Script

1. Make the script executable:

    ```bash
    chmod +x gen_kelp_tiles.sh
    ```
    
    Run this if there are any synatx error
    ```bash
    sed -i 's/\r$//' gen_kelp_tiles.sh
    ```


2. Run the script with default parameters:

    ```bash
    ./gen_kelp_tiles.sh
    ```

3. Or customize the parameters:

    ```bash
    ./gen_kelp_tiles.sh --kelp-tiles-directory "your-directory" --bucket "your-bucket" --bucket-folder "your-folder" 
    ```

4. Or open the script and edit the default values for the parameters.

### Using Python Directly

Run the Python script from the command line with the required arguments:

```bash
python3 generate_kelp_mask_tiles.py --kelp-tiles-directory KELP_TILES_DIRECTORY --bucket BUCKET --bucket-folder BUCKET_FOLDER
```