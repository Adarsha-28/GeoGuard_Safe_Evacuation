import geopandas as gpd

grid = gpd.read_file("data/processed/chennai_grid_rainfall_elevation.geojson")

print("Calculating flood risk...")

# Safe rainfall normalization
rain_range = grid["rainfall_mm"].max() - grid["rainfall_mm"].min()

if rain_range == 0:
    grid["rain_norm"] = 0
else:
    grid["rain_norm"] = (
        grid["rainfall_mm"] - grid["rainfall_mm"].min()
    ) / rain_range


# Safe elevation normalization
elev_range = grid["elevation_m"].max() - grid["elevation_m"].min()

if elev_range == 0:
    grid["elev_norm"] = 0
else:
    grid["elev_norm"] = (
        grid["elevation_m"].max() - grid["elevation_m"]
    ) / elev_range


# Flood score
grid["flood_risk_score"] = (
    0.7 * grid["rain_norm"] +
    0.3 * grid["elev_norm"]
)

# Risk category
def classify_risk(score):
    if score < 0.3:
        return "Low"
    elif score < 0.6:
        return "Medium"
    else:
        return "High"

grid["flood_risk"] = grid["flood_risk_score"].apply(classify_risk)

grid.to_file(
    "data/processed/chennai_flood_risk.geojson",
    driver="GeoJSON"
)

print("Flood risk model completed!")