import geopandas as gpd
import folium

grid = gpd.read_file("data/processed/chennai_grid.geojson")

center = [grid.geometry.centroid.y.mean(), grid.geometry.centroid.x.mean()]
m = folium.Map(location=center, zoom_start=11)

folium.GeoJson(grid).add_to(m)

m.save("grid_map.html")
print("Map saved as grid_map.html")
