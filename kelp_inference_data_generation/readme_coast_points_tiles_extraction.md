# Coast Points Tiles Extraction

This script processes CSV files to extract and consolidate unique coastal tiles information from the given folder path and saves the result to an output CSV file.

## Prerequisites

- Python 3.x
- Segmnted CSVs for the period

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/YourUsername/your-repository.git
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
    chmod +x run_coast_points_tiles_extraction.sh
    ```

2. Run the script:

    ```bash
    ./run_coast_points_tiles_extraction.sh
    ```

   By default, it will use:
   - Folder path: `world_monthly_inference_tiles_new/coastal_tiles_world_2023_01`
   - Output CSV path: `world_coastal_tiles/coastal_tiles_world_2023_01.csv`

3. **To specify custom paths**:

    ```bash
    ./run_coast_points_tiles_extraction.sh --folder-path custom_folder_path --output-csv custom_output_csv
    ```

### Using Python Directly

Run the Python script from the command line with the required arguments:

```bash
python3 coast_points_tiles_extraction.py --folder-path path_to_csv_files --output-csv path_to_output_csv
 ```