#!/bin/bash

# Default values
DEFAULT_BUCKET_NAME="kelpwatch2"
DEFAULT_TILES_FILE="path/to/default_tiles_file.csv"
DEFAULT_S3_FOLDER_NAME="inference-data/default"

# Parse command-line arguments
while getopts ":b:t:f:" opt; do
    case ${opt} in
        b )
            BUCKET_NAME=$OPTARG
            ;;
        t )
            TILES_FILE=$OPTARG
            ;;
        f )
            S3_FOLDER_NAME=$OPTARG
            ;;
        \? )
            echo "Usage: $0 [-b bucket-name] [-t tiles-file] [-f s3-folder-name]"
            exit 1
            ;;
    esac
done

# If any argument is missing, use the default value
BUCKET_NAME=${BUCKET_NAME:-$DEFAULT_BUCKET_NAME}
TILES_FILE=${TILES_FILE:-$DEFAULT_TILES_FILE}
S3_FOLDER_NAME=${S3_FOLDER_NAME:-$DEFAULT_S3_FOLDER_NAME}

# Run the Python script with the provided or default arguments
python3 generate_inference_tiles.py --bucket "$BUCKET_NAME" --tiles-file "$TILES_FILE" --s3-folder-name "$S3_FOLDER_NAME"
