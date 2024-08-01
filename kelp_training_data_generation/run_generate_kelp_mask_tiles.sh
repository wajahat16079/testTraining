#!/bin/bash

# Default parameters
kelp_tiles_directory="kelp_tiles_segmented_data"
bucket="kelpwatch2"
bucket_folder="training/full-tiles"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --kelp_tiles_directory)
      kelp_tiles_directory="$2"
      shift
      shift
      ;;
    --bucket)
      bucket="$2"
      shift
      shift
      ;;
    --bucket_folder)
      bucket_folder="$2"
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
python3 generate_kelp_mask_tiles.py \
  --kelp_tiles_directory "$kelp_tiles_directory" \
  --bucket "$bucket" \
  --bucket_folder "$bucket_folder"
