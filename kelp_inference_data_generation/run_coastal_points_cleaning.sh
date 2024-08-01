#!/bin/bash

# This script processes coastal points and Sentinel tile coordinates.
# Usage: ./run_process_coordinates.sh --data-coast-points "path/to/coastline-coordinate-data.csv" --folder-path "path/to/folder/with/tile/csvs"

# Define default values for the arguments
DATA_COAST_POINTS="coastal_points_extraction_from_geojson/coastline-coordinate-data.csv"
FOLDER_PATH="world_monthly_inference_tiles/coastal_tiles_world_2024_06"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --data-coast-points)
      DATA_COAST_POINTS="$2"
      shift
      shift
      ;;
    --folder-path)
      FOLDER_PATH="$2"
      shift
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# Run the Python script with the specified arguments
python3 coastal_points_cleaning.py --data_coast_points "$DATA_COAST_POINTS" --folder_path "$FOLDER_PATH"
