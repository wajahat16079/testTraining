# Coastal Coordinates Processor

This program processes coastal points and Sentinel tile coordinates to filter out coordinates that are not covered by Sentinel tiles. It extracts unique coordinates from Sentinel tile data and saves them to a CSV file.

## Prerequisites

- Python 3.x



## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/YourUsername/geojson-coordinate-extractor.git
    cd kelp_inference_data_generation/
    ```

2. Install the required Python packages (recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html)):

    ```bash
    pip install pandas
    ```

## Usage

### Using the Bash Script

1. Make the script executable:

    ```bash
    chmod +x run_coastal_points_cleaning.sh
    ```

2. Run the script:

    ```bash
    ./run_coastal_points_cleaning.sh
    ```

### Using Python Directly

Run the Python script from the command line with the required arguments:

```bash
python3 coastal_points_cleaning.py --data_coast_points "path/to/coastline-coordinate-data.csv" --folder_path "path/to/folder/with/tile/csvs"
```
