#!/bin/bash

# Default values for arguments
DEFAULT_DATA_KELP="unique_coords_tiles.csv"
DEFAULT_DATE_RANGE="2023-01-01/2023-01-31"
DEFAULT_CSV_DIR="world_monthly_inference_tiles_new"

# Function to display help message
usage() {
    echo "Usage: $0 [--data-kelp <path>] [--date-range <range>] [--csv-dir <directory>]"
    echo
    echo "Options:"
    echo "  --data-kelp <path>      Path to the CSV file containing kelp data points (default: $DEFAULT_DATA_KELP)."
    echo "  --date-range <range>    Time range for querying Sentinel-2 imagery (default: $DEFAULT_DATE_RANGE)."
    echo "  --csv-dir <directory>   Directory to save the output CSV files (default: $DEFAULT_CSV_DIR)."
    exit 1
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --data-kelp)
            DATA_KELP="$2"
            shift 2
            ;;
        --date-range)
            DATE_RANGE="$2"
            shift 2
            ;;
        --csv-dir)
            CSV_DIR="$2"
            shift 2
            ;;
        *)
            usage
            ;;
    esac
done

# Set default values if not provided
DATA_KELP="${DATA_KELP:-$DEFAULT_DATA_KELP}"
DATE_RANGE="${DATE_RANGE:-$DEFAULT_DATE_RANGE}"
CSV_DIR="${CSV_DIR:-$DEFAULT_CSV_DIR}"

# Print the configuration
echo "Configuration:"
echo "  Data Kelp:   $DATA_KELP"
echo "  Date Range:  $DATE_RANGE"
echo "  CSV Directory: $CSV_DIR"

# Run the Python script
python3 inference_data_tiles_segmentation.py \
    --data_kelp "$DATA_KELP" \
    --date_range "$DATE_RANGE" \
    --csv_dir "$CSV_DIR"
