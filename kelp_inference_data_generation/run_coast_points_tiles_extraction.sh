#!/bin/bash

# Default values for arguments
DEFAULT_FOLDER_PATH="world_monthly_inference_tiles_new"
DEFAULT_OUTPUT_CSV="world_coastal_tilesTemp/coastal_tiles_world_2023_01.csv"

# Print usage instructions
usage() {
    echo "Usage: $0 [--folder-path FOLDER_PATH] [--output-csv OUTPUT_CSV]"
    echo "  --folder-path FOLDER_PATH  Path to the folder containing the input CSV files (default: $DEFAULT_FOLDER_PATH)"
    echo "  --output-csv OUTPUT_CSV    Path to the output CSV file (default: $DEFAULT_OUTPUT_CSV)"
    exit 1
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --folder-path) FOLDER_PATH="$2"; shift ;;
        --output-csv) OUTPUT_CSV="$2"; shift ;;
        *) usage ;;
    esac
    shift
done

# Use default values if not provided
FOLDER_PATH="${FOLDER_PATH:-$DEFAULT_FOLDER_PATH}"
OUTPUT_CSV="${OUTPUT_CSV:-$DEFAULT_OUTPUT_CSV}"

# Print the values being used
echo "Using folder path: $FOLDER_PATH"
echo "Using output CSV path: $OUTPUT_CSV"

# Run the Python script with the specified or default arguments
python3 coast_points_tiles_extraction.py --folder-path "$FOLDER_PATH" --output-csv "$OUTPUT_CSV"
