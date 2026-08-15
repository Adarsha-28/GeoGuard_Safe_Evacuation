import geopandas as gpd

# Load grid
grid = gpd.read_file("data/processed/chennai_grid.geojson")

# Get centroid of each grid
grid["latitude"] = grid.geometry.centroid.y
grid["longitude"] = grid.geometry.centroid.x

# Save updated grid
grid.to_file("data/processed/chennai_grid_with_coords.geojson", driver="GeoJSON")

print("Coordinates added to grid cells")