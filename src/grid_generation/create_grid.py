import geopandas as gpd
from shapely.geometry import box

def create_grid(boundary_path, output_path, cell_size=500):
    boundary = gpd.read_file(boundary_path)
    boundary = boundary.to_crs(epsg=32644)  # UTM Zone 44N for Chennai
    
    bounds = boundary.total_bounds
    xmin, ymin, xmax, ymax = bounds
    
    cells = []
    x = xmin
    while x < xmax:
        y = ymin
        while y < ymax:
            cell = box(x, y, x + cell_size, y + cell_size)
            if boundary.intersects(cell).any():
                cells.append(cell)
            y += cell_size
        x += cell_size
    
    grid = gpd.GeoDataFrame({'geometry': cells}, crs=boundary.crs)
    grid = grid.to_crs(epsg=4326)
    grid.to_file(output_path, driver='GeoJSON')
    print(f"Grid created with {len(grid)} cells")

if __name__ == "__main__":
    create_grid(
        "data/raw/chennai_boundary.geojson",
        "data/processed/chennai_grid.geojson"
    )
