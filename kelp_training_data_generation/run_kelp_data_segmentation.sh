#!/bin/bash

# Default parameters
nc_segmented_data_dir="kelp_nc_segmented_data"
kelp_tiles_dir="kelp_tiles_segmented_data"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --nc-segmented-data-dir)
      nc_segmented_data_dir="$2"
      shift
      shift
      ;;
    --kelp-tiles-dir)
      kelp_tiles_dir="$2"
      shift
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Run the Python script
python3 kelp_data_segmentation.py \
  --nc_segmented_data_dir "$nc_segmented_data_dir" \
  --kelp_tiles_dir "$kelp_tiles_dir"
