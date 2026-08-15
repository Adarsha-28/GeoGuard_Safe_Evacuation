import geopandas as gpd
import requests

API_KEY = "2efc6badb1e0f099f544e8e84a4fc440"

# Chennai center coordinates
lat = 13.0827
lon = 80.2707

url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

response = requests.get(url)
data = response.json()

rainfall = 0
if "rain" in data and "1h" in data["rain"]:
    rainfall = data["rain"]["1h"]

print("Current Rainfall:", rainfall)

# Load grid
grid = gpd.read_file("data/processed/chennai_grid_with_coords.geojson")

# Assign rainfall to all grids
grid["rainfall_mm"] = rainfall

# Save output
grid.to_file("data/processed/chennai_grid_rainfall.geojson", driver="GeoJSON")

print("Rainfall added to all grids successfully!")