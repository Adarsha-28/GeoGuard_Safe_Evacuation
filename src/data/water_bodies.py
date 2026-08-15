"""
Feature 7: Water Body Analysis for GeoGuard Flood Risk Prediction
===================================================================
This module handles water body analysis for Chennai city, including:
- Downloading water bodies from OpenStreetMap using OSMnx
- Computing distance from each grid cell to nearest water body
- Normalizing distance values
- Updating flood risk score formula
"""

import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union
import os


def download_water_bodies(place_name: str = "Chennai, Tamil Nadu, India", 
                          water_types: list = None) -> gpd.GeoDataFrame:
    if water_types is None:
        water_types = ['water', 'river', 'lake', 'reservoir', 'canal', 'stream', 'pond', 'wetland']
    
    print(f"Downloading water bodies for {place_name}...")
    
    # Download all water-related features using the correct OSMnx API
    water_bodies = ox.features_from_place(
        place_name,
        tags={'water': True, 'river': True, 'lake': True, 'reservoir': True, 
              'canal': True, 'stream': True, 'pond': True, 'wetland': True}
    )
    
    if len(water_bodies) == 0:
        print("Warning: No water bodies found. Trying alternative approach...")
        # Try downloading with different tags
        water_bodies = ox.features_from_place(
            place_name,
            tags={'natural': 'water'}
        )
    
    # Filter to keep only polygon geometries (actual water bodies)
    if len(water_bodies) > 0:
        water_bodies = water_bodies[water_bodies.geometry.type.isin(['Polygon', 'MultiPolygon'])]
        
        # Convert to GeoDataFrame with proper CRS
        water_gdf = gpd.GeoDataFrame(geometry=water_bodies.geometry, crs="EPSG:4326")
        
        # Dissolve all water bodies into a single geometry for distance calculation
        if len(water_gdf) > 0:
            water_gdf = water_gdf.dissolve()
            
        print(f"Downloaded {len(water_bodies)} water body features")
        return water_gdf
    else:
        print("Warning: No water bodies could be downloaded")
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")


def load_grid_data(grid_path: str = "data/processed/chennai_grid_rainfall_elevation.geojson") -> gpd.GeoDataFrame:
    print(f"Loading grid data from {grid_path}...")
    grid = gpd.read_file(grid_path)
    print(f"Loaded {len(grid)} grid cells")
    return grid


def ensure_same_crs(grid: gpd.GeoDataFrame, water_bodies: gpd.GeoDataFrame) -> tuple:
    # Get CRS from grid (typically EPSG:4326 for GeoJSON)
    grid_crs = grid.crs
    water_crs = water_bodies.crs
    
    if grid_crs != water_crs:
        print(f"Converting water bodies from {water_crs} to {grid_crs}")
        water_bodies = water_bodies.to_crs(grid_crs)
    
    return grid, water_bodies


def convert_to_metric_crs(grid: gpd.GeoDataFrame, water_bodies: gpd.GeoDataFrame, 
                          target_crs: str = "EPSG:3857") -> tuple:
    """
    Convert both datasets to a metric CRS for distance calculations.
    
    Parameters:
    -----------
    grid : gpd.GeoDataFrame
        Grid GeoDataFrame
    water_bodies : gpd.GeoDataFrame
        Water bodies GeoDataFrame
    target_crs : str
        Target CRS (default: EPSG:3857 - Web Mercator)
    
    Returns:
    --------
    tuple
        (grid, water_bodies) converted to metric CRS
    """
    print(f"Converting to metric CRS: {target_crs}")
    grid_metric = grid.to_crs(target_crs)
    water_metric = water_bodies.to_crs(target_crs)
    
    return grid_metric, water_metric


def calculate_distance_to_water(grid: gpd.GeoDataFrame, water_bodies: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calculate distance from each grid cell centroid to the nearest water body.
    
    Parameters:
    -----------
    grid : gpd.GeoDataFrame
        Grid GeoDataFrame (should be in metric CRS)
    water_bodies : gpd.GeoDataFrame
        Water bodies GeoDataFrame (should be in metric CRS)
    
    Returns:
    --------
    gpd.GeoDataFrame
        Grid with distance_to_water column added (in meters)
    """
    print("Calculating distance to nearest water body for each grid cell...")
    
    # If there are no water bodies, set distance to a large value
    if len(water_bodies) == 0:
        print("Warning: No water bodies available. Setting distance to maximum.")
        grid['distance_to_water'] = 50000.0  # 50km as default max distance
        return grid
    
    # Get the union of all water body geometries for distance calculation
    try:
        water_union = unary_union(water_bodies.geometry.values)
    except Exception as e:
        print(f"Warning: Could not union water bodies: {e}")
        grid['distance_to_water'] = 50000.0
        return grid
    
    # Calculate distance from each grid cell centroid to nearest water body
    distances = []
    for idx, row in grid.iterrows():
        centroid = row.geometry.centroid
        distance = centroid.distance(water_union)
        distances.append(distance)
    
    grid['distance_to_water'] = distances
    
    # Print statistics
    print(f"Distance to water statistics (in meters):")
    print(f"  Min: {grid['distance_to_water'].min():.2f}")
    print(f"  Max: {grid['distance_to_water'].max():.2f}")
    print(f"  Mean: {grid['distance_to_water'].mean():.2f}")
    print(f"  Median: {grid['distance_to_water'].median():.2f}")
    
    return grid


def normalize_water_distance(grid: gpd.GeoDataFrame, column: str = 'distance_to_water',
                             new_column: str = 'water_norm') -> gpd.GeoDataFrame:
    """
    Normalize distance to water into a value between 0 and 1.
    Areas closer to water have higher values (more flood risk).
    
    Parameters:
    -----------
    grid : gpd.GeoDataFrame
        Grid GeoDataFrame with distance_to_water column
    column : str
        Name of the distance column to normalize
    new_column : str
        Name of the new normalized column
    
    Returns:
    --------
    gpd.GeoDataFrame
        Grid with normalized water distance column
    """
    print(f"Normalizing {column} to {new_column}...")
    
    min_dist = grid[column].min()
    max_dist = grid[column].max()
    
    if max_dist == min_dist:
        grid[new_column] = 0.5  # If all distances are the same, use middle value
    else:
        # Inverse normalization: closer = higher value
        # Formula: (max_dist - dist) / (max_dist - min_dist)
        grid[new_column] = (max_dist - grid[column]) / (max_dist - min_dist)
    
    print(f"Water normalization complete:")
    print(f"  Min: {grid[new_column].min():.4f}")
    print(f"  Max: {grid[new_column].max():.4f}")
    print(f"  Mean: {grid[new_column].mean():.4f}")
    
    return grid


def update_flood_risk_score(grid: gpd.GeoDataFrame, 
                             rain_weight: float = 0.5,
                             elev_weight: float = 0.25,
                             water_weight: float = 0.25) -> gpd.GeoDataFrame:
    """
    Update flood risk score formula using rainfall, elevation, and water proximity.
    
    The updated formula combines:
    - Rainfall (normalized): Higher rainfall = higher risk
    - Elevation (normalized, inverted): Lower elevation = higher risk  
    - Water proximity (normalized): Closer to water = higher risk
    
    Parameters:
    -----------
    grid : gpd.GeoDataFrame
        Grid GeoDataFrame with rain_norm, elev_norm, and water_norm columns
    rain_weight : float
        Weight for rainfall factor (default: 0.5)
    elev_weight : float
        Weight for elevation factor (default: 0.25)
    water_weight : float
        Weight for water proximity factor (default: 0.25)
    
    Returns:
    --------
    gpd.GeoDataFrame
        Grid with updated flood_risk_score and flood_risk columns
    """
    print("Updating flood risk score with water proximity factor...")
    
    # Check if required columns exist, create if missing
    if 'rain_norm' not in grid.columns:
        # Calculate rainfall normalization
        rain_range = grid["rainfall_mm"].max() - grid["rainfall_mm"].min()
        if rain_range > 0:
            grid["rain_norm"] = (grid["rainfall_mm"] - grid["rainfall_mm"].min()) / rain_range
        else:
            grid["rain_norm"] = 0
    
    if 'elev_norm' not in grid.columns:
        # Calculate elevation normalization (inverted - lower = higher risk)
        elev_range = grid["elevation_m"].max() - grid["elevation_m"].min()
        if elev_range > 0:
            grid["elev_norm"] = (grid["elevation_m"].max() - grid["elevation_m"]) / elev_range
        else:
            grid["elev_norm"] = 0
    
    if 'water_norm' not in grid.columns:
        print("Warning: water_norm column not found. Calculating...")
        grid = normalize_water_distance(grid)
    
    # Ensure weights sum to 1
    total_weight = rain_weight + elev_weight + water_weight
    rain_weight = rain_weight / total_weight
    elev_weight = elev_weight / total_weight
    water_weight = water_weight / total_weight
    
    print(f"Using weights - Rainfall: {rain_weight:.2f}, Elevation: {elev_weight:.2f}, Water: {water_weight:.2f}")
    
    # Calculate new flood risk score
    grid["flood_risk_score"] = (
        rain_weight * grid["rain_norm"] +
        elev_weight * grid["elev_norm"] +
        water_weight * grid["water_norm"]
    )
    
    # Classify risk levels
    def classify_risk(score):
        if score < 0.3:
            return "Low"
        elif score < 0.6:
            return "Medium"
        else:
            return "High"
    
    grid["flood_risk"] = grid["flood_risk_score"].apply(classify_risk)
    
    # Print statistics
    print(f"Flood risk score statistics:")
    print(f"  Min: {grid['flood_risk_score'].min():.4f}")
    print(f"  Max: {grid['flood_risk_score'].max():.4f}")
    print(f"  Mean: {grid['flood_risk_score'].mean():.4f}")
    
    risk_counts = grid['flood_risk'].value_counts()
    print(f"Risk distribution:")
    for risk_level, count in risk_counts.items():
        print(f"  {risk_level}: {count} cells ({count/len(grid)*100:.1f}%)")
    
    return grid


def analyze_water_bodies(place_name: str = "Chennai, Tamil Nadu, India",
                        grid_path: str = "data/processed/chennai_grid_rainfall_elevation.geojson",
                        output_path: str = "data/processed/chennai_flood_risk_with_water.geojson",
                        rain_weight: float = 0.5,
                        elev_weight: float = 0.25,
                        water_weight: float = 0.25) -> gpd.GeoDataFrame:
    """
    Main function to perform complete water body analysis.
    
    Parameters:
    -----------
    place_name : str
        Name of the place for water body download
    grid_path : str
        Path to input grid data
    output_path : str
        Path to save output GeoJSON
    rain_weight : float
        Weight for rainfall in risk calculation
    elev_weight : float
        Weight for elevation in risk calculation
    water_weight : float
        Weight for water proximity in risk calculation
    
    Returns:
    --------
    gpd.GeoDataFrame
        Updated GeoDataFrame with water analysis
    """
    print("=" * 60)
    print("Starting Water Body Analysis for GeoGuard")
    print("=" * 60)
    
    # Step 1: Download water bodies
    water_bodies = download_water_bodies(place_name)
    
    # Step 2: Load grid data
    grid = load_grid_data(grid_path)
    
    # Step 3: Ensure same CRS
    grid, water_bodies = ensure_same_crs(grid, water_bodies)
    
    # Step 4: Convert to metric CRS
    grid_metric, water_metric = convert_to_metric_crs(grid, water_bodies)
    
    # Step 5: Calculate distance to water
    grid_metric = calculate_distance_to_water(grid_metric, water_metric)
    
    # Step 6: Normalize distance
    grid_metric = normalize_water_distance(grid_metric)
    
    # Step 7: Update flood risk score
    grid_metric = update_flood_risk_score(
        grid_metric, 
        rain_weight=rain_weight,
        elev_weight=elev_weight,
        water_weight=water_weight
    )
    
    # Step 8: Convert back to original CRS for output
    grid_final = grid_metric.to_crs(grid.crs)
    
    # Step 9: Save output
    print(f"Saving results to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    grid_final.to_file(output_path, driver="GeoJSON")
    
    print("=" * 60)
    print("Water Body Analysis Complete!")
    print("=" * 60)
    
    return grid_final


# =============================================================================
# Test Example
# =============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GeoGuard - Water Body Analysis Test")
    print("=" * 60 + "\n")
    
    # Run the water body analysis
    result = analyze_water_bodies(
        place_name="Chennai, Tamil Nadu, India",
        grid_path="data/processed/chennai_grid_rainfall_elevation.geojson",
        output_path="data/processed/chennai_flood_risk_with_water.geojson"
    )
    
    # Display first few rows
    print("\n" + "=" * 60)
    print("First 10 rows of output:")
    print("=" * 60)
    
    # Select relevant columns to display
    display_cols = ['latitude', 'longitude', 'rainfall_mm', 'elevation_m', 
                    'distance_to_water', 'water_norm', 'flood_risk_score', 'flood_risk']
    
    # Filter to columns that exist
    display_cols = [col for col in display_cols if col in result.columns]
    
    print(result[display_cols].head(10).to_string())
    
    print("\n" + "=" * 60)
    print("Analysis Summary:")
    print("=" * 60)
    print(f"Total grid cells: {len(result)}")
    print(f"Output saved to: data/processed/chennai_flood_risk_with_water.geojson")

