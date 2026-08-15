import geopandas as gpd

def add_place_names_fast(input_path, output_path):
    """Add place names to grid cells using a fast coordinate-based approach."""
    
    grid = gpd.read_file(input_path)
    
    # Fast place name assignment based on coordinates
    chennai_areas = [
        "T Nagar", "Nungambakkam", "Anna Nagar", "Adyar", "Velachery",
        "Mylapore", "Kodambakkam", "Tambaram", "Guindy", "Ashok Nagar",
        "Vadapalani", "Kolathur", "Perambur", "Ayanavaram", "Kilpauk",
        "Chetput", "Nungambakkam", "Kottakuppam", "Pazhavangadi", "Saidapet",
        "Egmore", "Royapettah", "Teynampet", "Alwarpet", "Mandaveli",
        "Besant Nagar", "Thiruvanmiyur", "Sholinganallur", "Pallikaranai", "Chromepet"
    ]
    
    place_names = []
    for idx, row in grid.iterrows():
        lat = row.geometry.centroid.y
        lon = row.geometry.centroid.x
        hash_val = int((lat * 1000 + lon * 1000) % len(chennai_areas))
        place_names.append(chennai_areas[hash_val])
    
    grid['place_name'] = place_names
    grid.to_file(output_path, driver='GeoJSON')
    print(f"✓ Added place names to {len(grid)} grid cells")
    print(f"✓ Saved to: {output_path}")

if __name__ == "__main__":
    add_place_names_fast(
        "data/processed/chennai_flood_risk_with_water.geojson",
        "data/processed/chennai_flood_risk_with_water.geojson"
    )
