# Extract coastal coordinates for entire world

Script: create-coastline-coordinate-data.py

Description:

This script parses a GeoJSON file to extract coordinates from MultiPolygon geometries and saves the extracted coordinates to a CSV file.

Tasks:

Reads a GeoJSON file containing MultiPolygon geometries. 

Extracts coordinates (longitude, latitude) from the first polygon in each MultiPolygon.

Saves the extracted coordinates to a CSV file.

Run the script from the command line:

python create-coastline-coordinate-data.py

The GeoJSON file (earth-coastlines-1m.geo.json) will be read from the default input path, and the coordinates will be saved in the default output CSV file (coastline-coordinate-data.csv).

GeoJSON File Source:

The GeoJSON file used in this script can be obtained from the following source:
[Earth Coastlines GeoJSON](https://github.com/simonepri/geo-maps/blob/master/info/earth-coastlines.md)



