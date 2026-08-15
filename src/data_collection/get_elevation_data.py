import geopandas as gpd
import requests
import json

# Load grid
grid = gpd.read_file("data/processed/chennai_grid_rainfall.geojson")

coords = []

for index, row in grid.iterrows():
    coords.append({
        "latitude": row["latitude"],
        "longitude": row["longitude"]
    })

# API endpoint
url = "https://api.open-elevation.com/api/v1/lookup"

# Send all coordinates in one request
response = requests.post(url, json={"locations": coords})

data = response.json()

elevations = [item["elevation"] for item in data["results"]]

# Add elevation column
grid["elevation_m"] = elevations

# Save output
grid.to_file(
    "data/processed/chennai_grid_rainfall_elevation.geojson",
    driver="GeoJSON"
)

print("Elevation data added successfully!")