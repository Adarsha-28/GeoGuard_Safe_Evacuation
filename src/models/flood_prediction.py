"""
Rainfall Prediction System for GeoGuard
======================================
This module provides functionality for:
- Fetching real-time rainfall data from OpenWeather API
- Simulating rainfall scenarios
- Recalculating flood risk scores
- Generating updated flood risk maps

Libraries required:
- requests
- geopandas
- pandas
- folium
- matplotlib
"""

import requests
import geopandas as gpd
import pandas as pd
import folium
import matplotlib.pyplot as plt
import os
from typing import Optional, Dict, Any


# OpenWeather API configuration
# Note: Users should replace with their own API key
OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


# Default rainfall scenarios for simulation
RAINFALL_SCENARIOS = {
    'Light Rain': 40,
    'Moderate Rain': 80,
    'Heavy Rain': 120,
    'Extreme Rain': 200
}


def fetch_current_rainfall(
    city: str = "Chennai",
    api_key: str = None,
    country_code: str = "IN"
) -> Dict[str, Any]:
    """
    Fetch current weather data including rainfall from OpenWeather API.
    
    Parameters:
    -----------
    city : str
        Name of the city (default: Chennai)
    api_key : str
        OpenWeather API key. If None, uses default API key
    country_code : str
        Country code (default: IN for India)
    
    Returns:
    --------
    dict
        Dictionary containing weather data including rainfall
    
    Raises:
    -------
    requests.RequestException
        If API request fails
    """
    if api_key is None:
        api_key = OPENWEATHER_API_KEY
    
    if api_key == "YOUR_API_KEY_HERE":
        print("Warning: Using default API key. Please replace with your own OpenWeather API key.")
        print("Get a free API key at: https://openweathermap.org/api")
    
    params = {
        'q': f"{city},{country_code}",
        'appid': api_key,
        'units': 'metric'
    }
    
    print(f"Fetching weather data for {city}, {country_code}...")
    
    try:
        response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract rainfall data (rainfall in last 1h or 3h, in mm)
        rainfall_mm = 0.0
        if 'rain' in data:
            if '1h' in data['rain']:
                rainfall_mm = data['rain']['1h']
            elif '3h' in data['rain']:
                rainfall_mm = data['rain']['3h']
        
        result = {
            'city': city,
            'country': country_code,
            'temperature': data.get('main', {}).get('temp', 0),
            'humidity': data.get('main', {}).get('humidity', 0),
            'description': data.get('weather', [{}])[0].get('description', 'No description'),
            'rainfall_mm': rainfall_mm,
            'latitude': data.get('coord', {}).get('lat', 0),
            'longitude': data.get('coord', {}).get('lon', 0)
        }
        
        print(f"Current rainfall in {city}: {rainfall_mm} mm")
        return result
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("Error: Invalid API key. Please provide a valid OpenWeather API key.")
        print(f"HTTP Error: {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        raise


def load_flood_data(
    geojson_path: str = "data/processed/chennai_flood_risk_with_water.geojson"
) -> gpd.GeoDataFrame:
    """
    Load the flood risk GeoJSON file.
    
    Parameters:
    -----------
    geojson_path : str
        Path to the GeoJSON file
    
    Returns:
    --------
    gpd.GeoDataFrame
        GeoDataFrame with flood risk data
    """
    print(f"Loading flood data from {geojson_path}...")
    grid = gpd.read_file(geojson_path)
    print(f"Loaded {len(grid)} grid cells")
    return grid


def simulate_rainfall_scenario(
    grid: gpd.GeoDataFrame,
    rainfall_mm: float,
    scenario_name: str = None
) -> gpd.GeoDataFrame:
    """
    Simulate a rainfall scenario by updating rainfall values for all grid cells.
    
    Parameters:
    -----------
    grid : gpd.GeoDataFrame
        GeoDataFrame with grid cells
    rainfall_mm : float
        Rainfall amount in mm to simulate
    scenario_name : str
        Optional name for the scenario
    
    Returns:
    --------
    gpd.GeoDataFrame
        Updated GeoDataFrame with new rainfall values
    """
    if scenario_name:
        print(f"Simulating '{scenario_name}' scenario with {rainfall_mm} mm rainfall...")
    else:
        print(f"Simulating rainfall scenario with {rainfall_mm} mm...")
    
    # Create a copy to avoid modifying original
    grid = grid.copy()
    
    # Update rainfall for all grid cells
    # In real scenario, this could vary based on location
    # For simplicity, we apply uniform rainfall across the city
    grid['rainfall_mm'] = rainfall_mm
    
    print(f"Updated rainfall for {len(grid)} grid cells")
    
    return grid


def recalculate_flood_risk(
    grid: gpd.GeoDataFrame,
    rain_weight: float = 0.5,
    elev_weight: float = 0.25,
    water_weight: float = 0.25
) -> gpd.GeoDataFrame:
    """
    Recalculate flood risk scores with updated rainfall data.
    
    Parameters:
    -----------
    grid : gpd.GeoDataFrame
        GeoDataFrame with grid cells (must have rainfall_mm, elevation_m, water_norm)
    rain_weight : float
        Weight for rainfall factor (default: 0.5)
    elev_weight : float
        Weight for elevation factor (default: 0.25)
    water_weight : float
        Weight for water proximity factor (default: 0.25)
    
    Returns:
    --------
    gpd.GeoDataFrame
        Updated GeoDataFrame with new flood risk scores
    """
    print("Recalculating flood risk scores...")
    
    # Create a copy
    grid = grid.copy()
    
    # Calculate rainfall normalization
    rain_range = grid["rainfall_mm"].max() - grid["rainfall_mm"].min()
    if rain_range > 0:
        grid["rain_norm"] = (grid["rainfall_mm"] - grid["rainfall_mm"].min()) / rain_range
    else:
        grid["rain_norm"] = 0
    
    # Calculate elevation normalization (inverted - lower = higher risk)
    elev_range = grid["elevation_m"].max() - grid["elevation_m"].min()
    if elev_range > 0:
        grid["elev_norm"] = (grid["elevation_m"].max() - grid["elevation_m"]) / elev_range
    else:
        grid["elev_norm"] = 0
    
    # Ensure water_norm exists
    if 'water_norm' not in grid.columns:
        # Calculate water normalization if not present
        if 'distance_to_water' in grid.columns:
            min_dist = grid['distance_to_water'].min()
            max_dist = grid['distance_to_water'].max()
            if max_dist > min_dist:
                grid['water_norm'] = (max_dist - grid['distance_to_water']) / (max_dist - min_dist)
            else:
                grid['water_norm'] = 0.5
        else:
            grid['water_norm'] = 0
    
    # Normalize weights to sum to 1
    total_weight = rain_weight + elev_weight + water_weight
    rain_weight = rain_weight / total_weight
    elev_weight = elev_weight / total_weight
    water_weight = water_weight / total_weight
    
    print(f"Using weights - Rainfall: {rain_weight:.2f}, Elevation: {elev_weight:.2f}, Water: {water_weight:.2f}")
    
    # Calculate flood risk score
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
    print(f"\nFlood Risk Statistics:")
    print(f"  Min Score: {grid['flood_risk_score'].min():.4f}")
    print(f"  Max Score: {grid['flood_risk_score'].max():.4f}")
    print(f"  Mean Score: {grid['flood_risk_score'].mean():.4f}")
    
    risk_counts = grid['flood_risk'].value_counts()
    print(f"\nRisk Distribution:")
    for risk_level in ['Low', 'Medium', 'High']:
        count = risk_counts.get(risk_level, 0)
        percentage = count / len(grid) * 100
        print(f"  {risk_level}: {count} cells ({percentage:.1f}%)")
    
    return grid


def create_flood_risk_map(
    grid: gpd.GeoDataFrame,
    output_path: str = "output/flood_risk_prediction_map.html",
    title: str = "Flood Risk Prediction Map"
) -> folium.Map:
    """
    Create an interactive flood risk map using Folium.
    
    Parameters:
    -----------
    grid : gpd.GeoDataFrame
        GeoDataFrame with flood risk data
    output_path : str
        Path to save the HTML map
    title : str
        Title for the map
    
    Returns:
    --------
    folium.Map
        The created Folium map
    """
    print(f"Creating flood risk map: {title}")
    
    # Get center of Chennai
    center_lat = 13.0827
    center_lon = 80.2707
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='cartodbpositron'
    )
    
    # Add title
    title_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 50%; transform: translateX(-50%);
                z-index: 9999; font-size: 20px; font-weight: bold;
                background-color: white; padding: 10px 20px;
                border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        🌧️ {title}
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Color mapping
    def get_color(risk):
        colors = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'}
        return colors.get(risk, '#95a5a6')
    
    # Add polygons
    for idx, row in grid.iterrows():
        geometry = row.geometry
        flood_risk = row.get('flood_risk', 'Unknown')
        risk_score = row.get('flood_risk_score', 0)
        color = get_color(flood_risk)
        
        # Create popup content
        popup_html = f"""
        <div style="width: 200px;">
            <h4 style="color: {color};">Risk: {flood_risk}</h4>
            <p><b>Score:</b> {risk_score:.4f}</p>
            <p><b>Rainfall:</b> {row.get('rainfall_mm', 'N/A')} mm</p>
            <p><b>Elevation:</b> {row.get('elevation_m', 'N/A')} m</p>
            <p><b>Distance to Water:</b> {row.get('distance_to_water', 'N/A'):.0f} m</p>
        </div>
        """
        
        if geometry.geom_type == 'Polygon':
            coords = list(geometry.exterior.coords)
            folium.Polygon(
                locations=[(lat, lon) for lon, lat in coords],
                popup=folium.Popup(popup_html, max_width=250),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                weight=1
            ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 150px; height: 110px; 
                border: 2px solid grey; z-index: 9999; font-size: 14px;
                background-color: white; padding: 10px;
                border-radius: 5px;">
        <p style="margin: 0 0 10px 0; font-weight: bold; text-align: center;">
            Risk Legend
        </p>
        <p><span style="background: #2ecc71; padding: 2px 8px;">&nbsp;</span> Low</p>
        <p><span style="background: #f39c12; padding: 2px 8px;">&nbsp;</span> Medium</p>
        <p><span style="background: #e74c3c; padding: 2px 8px;">&nbsp;</span> High</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    m.save(output_path)
    
    print(f"Map saved to: {output_path}")
    
    return m


def create_static_map(
    grid: gpd.GeoDataFrame,
    output_path: str = "output/flood_risk_prediction.png",
    title: str = "Flood Risk Prediction Map"
) -> None:
    """
    Create a static matplotlib flood risk map.
    
    Parameters:
    -----------
    grid : gpd.GeoDataFrame
        GeoDataFrame with flood risk data
    output_path : str
        Path to save the PNG image
    title : str
        Title for the map
    """
    print(f"Creating static flood risk map: {title}")
    
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Create custom colormap
    from matplotlib.colors import LinearSegmentedColormap
    colors = ['#2ecc71', '#f39c12', '#e74c3c']  # Low, Medium, High
    cmap = LinearSegmentedColormap.from_list('risk', colors)
    
    # Plot
    grid.plot(
        column='flood_risk_score',
        cmap=cmap,
        legend=True,
        ax=ax,
        edgecolor='black',
        linewidth=0.1
    )
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Static map saved to: {output_path}")


def run_prediction_scenario(
    scenario_name: str,
    rainfall_mm: float,
    input_path: str = "data/processed/chennai_flood_risk_with_water.geojson",
    output_dir: str = "output/predictions"
) -> gpd.GeoDataFrame:
    """
    Run a complete prediction scenario.
    
    Parameters:
    -----------
    scenario_name : str
        Name of the scenario
    rainfall_mm : float
        Rainfall amount in mm
    input_path : str
        Path to input GeoJSON
    output_dir : str
        Directory to save output files
    
    Returns:
    --------
    gpd.GeoDataFrame
        Updated GeoDataFrame with new flood risk
    """
    print("\n" + "=" * 60)
    print(f"Running Rainfall Scenario: {scenario_name}")
    print(f"Rainfall: {rainfall_mm} mm")
    print("=" * 60)
    
    # Load data
    grid = load_flood_data(input_path)
    
    # Apply rainfall scenario
    grid = simulate_rainfall_scenario(grid, rainfall_mm, scenario_name)
    
    # Recalculate flood risk
    grid = recalculate_flood_risk(grid)
    
    # Create output paths
    os.makedirs(output_dir, exist_ok=True)
    base_name = scenario_name.lower().replace(' ', '_')
    
    # Save updated GeoJSON
    geojson_path = os.path.join(output_dir, f"{base_name}_flood_risk.geojson")
    grid.to_file(geojson_path, driver="GeoJSON")
    print(f"Saved GeoJSON to: {geojson_path}")
    
    # Create interactive map
    map_path = os.path.join(output_dir, f"{base_name}_interactive_map.html")
    create_flood_risk_map(
        grid, 
        map_path,
        f"Chennai Flood Risk - {scenario_name}"
    )
    
    # Create static map
    static_path = os.path.join(output_dir, f"{base_name}_map.png")
    create_static_map(
        grid,
        static_path,
        f"Chennai Flood Risk - {scenario_name}"
    )
    
    print("\n" + "=" * 60)
    print(f"Scenario '{scenario_name}' completed successfully!")
    print("=" * 60)
    
    return grid


def fetch_and_predict(
    api_key: str = None,
    input_path: str = "data/processed/chennai_flood_risk_with_water.geojson"
) -> gpd.GeoDataFrame:
    """
    Fetch real-time rainfall and update flood risk predictions.
    
    Parameters:
    -----------
    api_key : str
        OpenWeather API key
    input_path : str
        Path to input GeoJSON
    
    Returns:
    --------
    gpd.GeoDataFrame
        Updated GeoDataFrame with real-time flood risk
    """
    print("\n" + "=" * 60)
    print("Fetching Real-Time Rainfall Data")
    print("=" * 60)
    
    # Fetch current rainfall
    weather_data = fetch_current_rainfall(city="Chennai", api_key=api_key)
    
    rainfall_mm = weather_data['rainfall_mm']
    
    if rainfall_mm == 0:
        print("\nNote: No current rainfall detected in Chennai.")
        print("Using dry weather conditions for prediction.")
    
    # Run prediction
    grid = run_prediction_scenario(
        scenario_name=f"Real_Time_Prediction",
        rainfall_mm=rainfall_mm,
        input_path=input_path,
        output_dir="output/real_time"
    )
    
    return grid


# =============================================================================
# Example Usage
# =============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GeoGuard - Rainfall Prediction System")
    print("=" * 60 + "\n")
    
    # Option 1: Run predefined rainfall scenarios
    print("Available Rainfall Scenarios:")
    print("-" * 40)
    for name, mm in RAINFALL_SCENARIOS.items():
        print(f"  - {name}: {mm} mm")
    print()
    
    # Run each scenario
    for scenario_name, rainfall_mm in RAINFALL_SCENARIOS.items():
        run_prediction_scenario(
            scenario_name=scenario_name,
            rainfall_mm=rainfall_mm,
            input_path="data/processed/chennai_flood_risk_with_water.geojson",
            output_dir="output/predictions"
        )
    
    # Option 2: Fetch real-time data (requires API key)
    # Uncomment the following lines and add your API key:
    # fetch_and_predict(api_key="YOUR_OPENWEATHER_API_KEY")
    
    print("\n" + "=" * 60)
    print("All scenarios completed!")
    print("=" * 60)
    print("\nOutput files saved to:")
    print("  - output/predictions/")
    print("\nTo view interactive maps, open the HTML files in a browser.")

