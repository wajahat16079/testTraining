#!/bin/bash

# Default parameters
nc_file=""
output_dir="kelp_nc_segmented_data"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --nc-file)
      nc_file="$2"
      shift
      shift
      ;;
    --output-dir)
      output_dir="$2"
      shift
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [ -z "$nc_file" ]; then
  echo "Error: --nc-file is required."
  exit 1
fi

# Run the Python script
python3 kelp_data_read.py \
  --nc_file "$nc_file" \
  --output_dir "$output_dir"
