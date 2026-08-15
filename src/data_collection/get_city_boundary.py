import osmnx as ox
import geopandas as gpd

place = "Chennai Metropolitan Area, Tamil Nadu, India"

gdf = ox.geocode_to_gdf(place)

print("Boundary bounds:", gdf.total_bounds)

gdf.to_file("data/raw/chennai_boundary.geojson", driver="GeoJSON")

print("Chennai metro boundary downloaded successfully!")

print(gdf.total_bounds)