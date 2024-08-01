#!/bin/bash

# Ensure the script is executable
chmod +x run_create-coastline-coordinate-data.sh

# Define paths for input and output files
geojson_path="earth-coastlines-1m.geo.json"
output_csv_path="coastline-coordinate-data.csv"

# Run the Python script with specified arguments
python3 create-coastline-coordinate-data.py --geojson-path "$geojson_path" --output-path "$output_csv_path"
