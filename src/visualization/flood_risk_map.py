import geopandas as gpd
import matplotlib.pyplot as plt

grid = gpd.read_file("data/processed/chennai_flood_risk_with_water.geojson")

fig, ax = plt.subplots(figsize=(10,10))

grid.plot(
    column="flood_risk_score",
    cmap="RdYlBu_r",
    legend=True,
    ax=ax
)

plt.title("Flood Risk Map - Chennai")
plt.show()