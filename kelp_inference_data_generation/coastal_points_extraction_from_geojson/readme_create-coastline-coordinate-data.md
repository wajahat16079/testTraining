# GeoJSON Coordinate Extractor

This program parses a GeoJSON file to extract coordinates from MultiPolygon geometries and saves the extracted coordinates to a CSV file.

## Prerequisites

- Python 3.x



## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/YourUsername/geojson-coordinate-extractor.git
    cd kelp_inference_data_generation//coastal_points_extraction_from_geojson/
    ```

2. Install the required Python packages (recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html)):

    ```bash
    pip install json csv
    ```

## Usage

### Using the Bash Script

1. Make the script executable:

    ```bash
    chmod +x run_create-coastline-coordinate-data.sh
    ```

2. Run the script:

    ```bash
    ./run_create-coastline-coordinate-data.sh
    ```

### Using Python Directly

Run the Python script from the command line with the required arguments:

```bash
python3 create-coastline-coordinate-data.py --geojson-path earth-coastlines-1m.geo.json --output-path coastline-coordinate-data.csv
```
