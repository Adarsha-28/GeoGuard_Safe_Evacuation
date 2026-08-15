"""
Interactive Flood Risk Map for GeoGuard
=======================================
This module creates an interactive Folium map where users can click
on any grid cell to see detailed flood risk information.

Requirements:
- geopandas
- folium
- branca
- pandas
"""

import geopandas as gpd
import folium
import pandas as pd
from branca.colormap import LinearColormap
import os


def load_flood_data(geojson_path: str = "data/processed/chennai_flood_risk_with_water.geojson") -> gpd.GeoDataFrame:
    """
    Load the flood risk GeoJSON file.
    
    Parameters:
    -----------
    geojson_path : str
        Path to the GeoJSON file containing flood risk data
    
    Returns:
    --------
    gpd.GeoDataFrame
        GeoDataFrame with flood risk data
    """
    print(f"Loading flood data from {geojson_path}...")
    grid = gpd.read_file(geojson_path)
    print(f"Loaded {len(grid)} grid cells")
    return grid


def get_risk_color(flood_risk: str) -> str:
    """
    Get color based on flood risk level.
    
    Parameters:
    -----------
    flood_risk : str
        Flood risk level ('Low', 'Medium', 'High')
    
    Returns:
    --------
    str
        Color hex code
    """
    risk_colors = {
        'Low': '#2ecc71',      # Green
        'Medium': '#f39c12',   # Yellow/Orange
        'High': '#e74c3c'      # Red
    }
    return risk_colors.get(flood_risk, '#95a5a6')  # Default gray


def create_popup_content(row: pd.Series) -> str:
    """
    Create HTML content for popup when clicking on a grid cell.
    
    Parameters:
    -----------
    row : pd.Series
        Row containing the grid cell data
    
    Returns:
    --------
    str
        HTML string for popup content
    """
    # Get values, handling missing data
    risk_level = row.get('flood_risk', 'N/A')
    risk_score = row.get('flood_risk_score', 'N/A')
    rainfall = row.get('rainfall_mm', 'N/A')
    elevation = row.get('elevation_m', 'N/A')
    distance_water = row.get('distance_to_water', 'N/A')
    water_norm = row.get('water_norm', 'N/A')
    
    # Format numeric values
    if isinstance(risk_score, (int, float)):
        risk_score = f"{risk_score:.4f}"
    if isinstance(distance_water, (int, float)):
        distance_water = f"{distance_water:.2f}"
    if isinstance(water_norm, (int, float)):
        water_norm = f"{water_norm:.4f}"
    
    # Get color for this risk level
    color = get_risk_color(risk_level)
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; width: 220px;">
        <h4 style="margin: 0 0 10px 0; color: {color}; border-bottom: 2px solid {color}; padding-bottom: 5px;">
            🚨 Flood Risk: {risk_level}
        </h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 8px; font-weight: bold; color: #555;">Flood Risk Score</td>
                <td style="padding: 8px; text-align: right; color: {color}; font-weight: bold;">{risk_score}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold; color: #555;">Rainfall</td>
                <td style="padding: 8px; text-align: right;">{rainfall} mm</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 8px; font-weight: bold; color: #555;">Elevation</td>
                <td style="padding: 8px; text-align: right;">{elevation} m</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold; color: #555;">Distance to Water</td>
                <td style="padding: 8px; text-align: right;">{distance_water} m</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 8px; font-weight: bold; color: #555;">Water Proximity Score</td>
                <td style="padding: 8px; text-align: right;">{water_norm}</td>
            </tr>
        </table>
    </div>
    """
    return html_content


def create_legend() -> folium.Element:
    """
    Create a legend for the flood risk levels.
    
    Returns:
    --------
    folium.Element
        HTML element containing the legend
    """
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 180px; height: 130px; 
                border: 2px solid grey; z-index: 9999; font-size: 14px;
                background-color: white; padding: 10px;
                border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 16px; 
                  text-align: center; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
            Flood Risk Legend
        </p>
        <p style="margin: 5px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; 
                         background-color: #2ecc71; margin-right: 8px; 
                         vertical-align: middle; border-radius: 3px;"></span>
            Low Risk
        </p>
        <p style="margin: 5px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; 
                         background-color: #f39c12; margin-right: 8px; 
                         vertical-align: middle; border-radius: 3px;"></span>
            Medium Risk
        </p>
        <p style="margin: 5px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; 
                         background-color: #e74c3c; margin-right: 8px; 
                         vertical-align: middle; border-radius: 3px;"></span>
            High Risk
        </p>
    </div>
    """
    return folium.Element(legend_html)


def create_interactive_flood_map(
    geojson_path: str = "data/processed/chennai_flood_risk_with_water.geojson",
    output_path: str = "output/flood_risk_interactive_map.html",
    center_lat: float = 13.0827,
    center_lon: float = 80.2707,
    zoom_start: int = 11
) -> folium.Map:
    """
    Create an interactive flood risk map with clickable grid cells.
    
    Parameters:
    -----------
    geojson_path : str
        Path to the input GeoJSON file
    output_path : str
        Path to save the output HTML map
    center_lat : float
        Latitude to center the map on
    center_lon : float
        Longitude to center the map on
    zoom_start : int
        Initial zoom level
    
    Returns:
    --------
    folium.Map
        The created Folium map object
    """
    print("=" * 60)
    print("Creating Interactive Flood Risk Map")
    print("=" * 60)
    
    # Load the flood data
    grid = load_flood_data(geojson_path)
    
    # Create base map centered on Chennai
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles='cartodbpositron'
    )
    
    # Add title
    title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50%; transform: translateX(-50%);
                z-index: 9999; font-size: 20px; font-weight: bold;
                background-color: white; padding: 10px 20px;
                border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        🌊 GeoGuard - Chennai Flood Risk Interactive Map
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add each grid cell to the map
    print("Adding grid cells to map...")
    
    for idx, row in grid.iterrows():
        # Get the geometry and properties
        geometry = row.geometry
        flood_risk = row.get('flood_risk', 'Unknown')
        
        # Get color based on risk level
        color = get_risk_color(flood_risk)
        
        # Create popup content
        popup_content = create_popup_content(row)
        
        # Convert geometry to GeoJSON
        if geometry.geom_type == 'Polygon':
            # Get coordinates (outer ring only for polygons)
            coords = list(geometry.exterior.coords)
            # Create polygon with tooltip and popup
            folium.Polygon(
                locations=[(lat, lon) for lon, lat in coords],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"Click for details - {flood_risk} Risk",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                weight=1
            ).add_to(m)
            
        elif geometry.geom_type == 'MultiPolygon':
            # Handle multipolygons
            for polygon in geometry.geoms:
                coords = list(polygon.exterior.coords)
                folium.Polygon(
                    locations=[(lat, lon) for lon, lat in coords],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=f"Click for details - {flood_risk} Risk",
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.6,
                    weight=1
                ).add_to(m)
    
    print(f"Added {len(grid)} grid cells to the map")
    
    # Add legend
    legend = create_legend()
    m.get_root().html.add_child(legend)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the map
    print(f"Saving map to {output_path}...")
    m.save(output_path)
    
    print("=" * 60)
    print("Interactive Flood Risk Map Created Successfully!")
    print(f"Output saved to: {output_path}")
    print("=" * 60)
    
    return m


# =============================================================================
# Example Code to Run
# =============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GeoGuard - Interactive Flood Risk Map")
    print("=" * 60 + "\n")
    
    # Create the interactive map
    flood_map = create_interactive_flood_map(
        geojson_path="data/processed/chennai_flood_risk_with_water.geojson",
        output_path="output/flood_risk_interactive_map.html",
        center_lat=13.0827,  # Chennai center latitude
        center_lon=80.2707,   # Chennai center longitude
        zoom_start=11
    )
    
    print("\nTo view the interactive map:")
    print("1. Open 'output/flood_risk_interactive_map.html' in a web browser")
    print("2. Click on any grid cell to see flood risk details")
    print("3. Use the legend to understand risk levels")

