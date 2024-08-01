# NetCDF Biomass Data Processor

This program processes NetCDF files to filter biomass data and saves the filtered data to CSV files. The script uses the `xarray` library for handling NetCDF data and `pandas` for data manipulation.

## Prerequisites

- Python 3.x
- Required Python packages: `xarray`, `pandas`, `numpy`, `argparse`

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/YourUsername/your-repo.git
    cd kelp_training_data_generation
    ```

2. Install the required Python packages (recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html)):

    ```bash
    pip install xarray pandas numpy
    ```

## Usage

The NetCDF Biomass Data Processor can be run using the provided bash script or directly with Python.

### Using the Bash Script

1. Make the script executable:

    ```bash
    chmod +x run_kelp_data_read.sh
    ```

    If there are any syntax errors due to Windows line endings, convert the script to Unix format:

    ```bash
    sed -i 's/\r$//' run_kelp_data_read.sh
    ```

2. Run the script with default parameters:

    ```bash
    ./run_kelp_data_read.sh --nc-file path/to/your/netcdf_file.nc
    ```

3. Or customize the parameters:

    ```bash
    ./run_kelp_data_read.sh --nc-file "path/to/your/netcdf_file.nc" --output-dir "path/to/output_directory"
    ```

4. Or open the script and edit the default values for the parameters.

### Using Python Directly

Run the Python script from the command line with the required arguments:

```bash
python3 kelp_data_read.py --nc_file path/to/your/netcdf_file.nc --output_dir path/to/output_directory
```