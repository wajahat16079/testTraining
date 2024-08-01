import json
import csv

def parse_geojson(geojson_path):
    """
    Parse a GeoJSON file to extract coordinates from MultiPolygon geometries.

    Args:
    geojson_path (str): Path to the GeoJSON file.

    Returns:
    list: A list of coordinates (longitude, latitude).
    """
    coordinates = []
    with open(geojson_path, 'r') as file:
        data = json.load(file)  # Load the entire GeoJSON file

    # Iterate through the geometries in the GeoJSON file
    for geometry in data['geometries']:
        if geometry['type'] == 'MultiPolygon':
            # Iterate through each polygon in the MultiPolygon
            for polygon in geometry['coordinates']:
                # Extract coordinates from the first polygon (assuming the first is desired)
                for coord in polygon[0]:
                    coordinates.append(coord)
    return coordinates

def save_coordinates_to_csv(coordinates, output_path):
    """
    Save a list of coordinates to a CSV file.

    Args:
    coordinates (list): List of coordinates to be saved.
    output_path (str): Path to the output CSV file.
    """
    with open(output_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Longitude', 'Latitude'])
        # Write each coordinate to the CSV file
        for coord in coordinates:
            writer.writerow(coord)

def main():
    """
    Main function to parse GeoJSON file and save the extracted coordinates to a CSV file.
    """
    # Define paths for input GeoJSON file and output CSV file
    geojson_path = 'earth-coastlines-1m.geo.json'
    output_csv_path = 'coastline-coordinate-data.csv'
    
    # Parse the GeoJSON file to get coastline coordinates
    coastline_coordinates = parse_geojson(geojson_path)
    
    # Save the extracted coordinates to a CSV file
    save_coordinates_to_csv(coastline_coordinates, output_csv_path)

if __name__ == "__main__":
    main()
