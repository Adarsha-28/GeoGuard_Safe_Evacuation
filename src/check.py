import geopandas as gpd

grid = gpd.read_file("data/processed/chennai_flood_risk_with_water.geojson")

print(grid.columns)