import sqlite3
import os
import json
from shapely.geometry import Point, Polygon

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'shelters.db')
GEOJSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'chennai_flood_risk_with_water.geojson')

# Demo shelters from shelters.js
SHELTERS_DATA = [
    {"name": "Corporation Primary School, T. Nagar", "lat": 13.0418, "lng": 80.2341, "capacity": 500, "address": "T. Nagar, Chennai", "contact": "044-2434-5678", "facilities": "Water, Food, Medical"},
    {"name": "Anna Nagar Community Hall", "lat": 13.0850, "lng": 80.2101, "capacity": 300, "address": "Anna Nagar, Chennai", "contact": "044-2615-4321", "facilities": "Water, Food, Toilets"},
    {"name": "Nungambakkam High School", "lat": 13.0569, "lng": 80.2425, "capacity": 400, "address": "Nungambakkam, Chennai", "contact": "044-2827-9876", "facilities": "Water, Food, Medical, Toilets"},
    {"name": "Egmore Relief Center", "lat": 13.0732, "lng": 80.2609, "capacity": 350, "address": "Egmore, Chennai", "contact": "044-2819-5432", "facilities": "Water, Food, Medical"},
    {"name": "Adyar Kalyana Mandapam", "lat": 13.0067, "lng": 80.2570, "capacity": 600, "address": "Adyar, Chennai", "contact": "044-2441-2345", "facilities": "Water, Food, Medical, Toilets"},
    {"name": "Velachery Community Center", "lat": 12.9750, "lng": 80.2210, "capacity": 450, "address": "Velachery, Chennai", "contact": "044-2266-7890", "facilities": "Water, Food, Toilets"},
    {"name": "Guindy Marriage Hall", "lat": 13.0067, "lng": 80.2206, "capacity": 500, "address": "Guindy, Chennai", "contact": "044-2235-4567", "facilities": "Water, Food, Medical"},
    {"name": "Mylapore Temple Hall", "lat": 13.0339, "lng": 80.2619, "capacity": 400, "address": "Mylapore, Chennai", "contact": "044-2464-8901", "facilities": "Water, Food, Toilets"},
    {"name": "Kotturpuram School", "lat": 13.0200, "lng": 80.2450, "capacity": 300, "address": "Kotturpuram, Chennai", "contact": "044-2441-3456", "facilities": "Water, Food"},
    {"name": "Thiruvanmiyur Relief Camp", "lat": 12.9820, "lng": 80.2590, "capacity": 350, "address": "Thiruvanmiyur, Chennai", "contact": "044-2441-7890", "facilities": "Water, Food, Medical"},
    {"name": "Besant Nagar Community Hall", "lat": 13.0001, "lng": 80.2668, "capacity": 400, "address": "Besant Nagar, Chennai", "contact": "044-2445-6789", "facilities": "Water, Food, Medical, Toilets"},
    {"name": "Sholinganallur Relief Center", "lat": 12.9010, "lng": 80.2279, "capacity": 500, "address": "Sholinganallur, Chennai", "contact": "044-2450-1234", "facilities": "Water, Food, Medical"},
    {"name": "Neelankarai School", "lat": 12.9490, "lng": 80.2590, "capacity": 300, "address": "Neelankarai, Chennai", "contact": "044-2449-5678", "facilities": "Water, Food"},
    {"name": "Porur Community Center", "lat": 13.0381, "lng": 80.1570, "capacity": 400, "address": "Porur, Chennai", "contact": "044-2476-2345", "facilities": "Water, Food, Medical, Toilets"},
    {"name": "Ashok Nagar Marriage Hall", "lat": 13.0358, "lng": 80.2101, "capacity": 350, "address": "Ashok Nagar, Chennai", "contact": "044-2489-6789", "facilities": "Water, Food, Toilets"},
    {"name": "KK Nagar Relief Camp", "lat": 13.0381, "lng": 80.2020, "capacity": 300, "address": "KK Nagar, Chennai", "contact": "044-2474-3456", "facilities": "Water, Food"},
    {"name": "Vadapalani Temple Hall", "lat": 13.0504, "lng": 80.2121, "capacity": 450, "address": "Vadapalani, Chennai", "contact": "044-2480-7890", "facilities": "Water, Food, Medical"},
    {"name": "Perambur Relief Center", "lat": 13.1143, "lng": 80.2378, "capacity": 500, "address": "Perambur, Chennai", "contact": "044-2662-1234", "facilities": "Water, Food, Medical, Toilets"},
    {"name": "Madhavaram Community Hall", "lat": 13.1482, "lng": 80.2314, "capacity": 400, "address": "Madhavaram, Chennai", "contact": "044-2552-5678", "facilities": "Water, Food, Toilets"},
    {"name": "Ambattur School", "lat": 13.1143, "lng": 80.1548, "capacity": 450, "address": "Ambattur, Chennai", "contact": "044-2656-9012", "facilities": "Water, Food, Medical"},
    {"name": "Avadi Relief Camp", "lat": 13.1067, "lng": 80.1018, "capacity": 350, "address": "Avadi, Chennai", "contact": "044-2666-3456", "facilities": "Water, Food"},
    {"name": "Tambaram Corporation School", "lat": 12.9249, "lng": 80.1000, "capacity": 600, "address": "Tambaram, Chennai", "contact": "044-2226-7890", "facilities": "Water, Food, Medical, Toilets"},
    {"name": "Chromepet Community Center", "lat": 12.9516, "lng": 80.1462, "capacity": 400, "address": "Chromepet, Chennai", "contact": "044-2235-1234", "facilities": "Water, Food, Toilets"},
    {"name": "Pallikaranai Relief Center", "lat": 12.9450, "lng": 80.2050, "capacity": 350, "address": "Pallikaranai, Chennai", "contact": "044-2266-5678", "facilities": "Water, Food, Medical"},
    {"name": "Perungudi School", "lat": 12.9610, "lng": 80.2440, "capacity": 300, "address": "Perungudi, Chennai", "contact": "044-2496-9012", "facilities": "Water, Food"}
]

def get_risk_level(lat, lng, geojson_data):
    point = Point(lng, lat)
    for feature in geojson_data.get('features', []):
        geom = feature.get('geometry', {})
        if geom.get('type') == 'Polygon':
            poly = Polygon(geom['coordinates'][0])
            if poly.contains(point):
                return feature['properties'].get('flood_risk', 'Low')
    return 'Low'

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create shelters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shelters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            latitude REAL,
            longitude REAL,
            address TEXT,
            capacity INTEGER,
            availableCapacity INTEGER,
            riskLevel TEXT,
            isActive INTEGER,
            facilities TEXT,
            contact TEXT
        )
    ''')
    
    # Check if already seeded
    cursor.execute('SELECT COUNT(*) FROM shelters')
    if cursor.fetchone()[0] == 0:
        print("Seeding shelters database...")
        # Load risk data
        geojson_data = {}
        if os.path.exists(GEOJSON_PATH):
            try:
                with open(GEOJSON_PATH, 'r') as f:
                    geojson_data = json.load(f)
            except Exception as e:
                print(f"Error loading geojson: {e}")
        
        for s in SHELTERS_DATA:
            risk = get_risk_level(s['lat'], s['lng'], geojson_data)
            # Seed realistic available capacity (e.g. 40% to 80% available)
            import random
            avail = int(s['capacity'] * random.uniform(0.4, 0.8))
            
            # Special case for testing full capacity
            if "Anna Nagar" in s['name']:
                avail = 0  # To demonstrate shelter full capacity
                
            cursor.execute('''
                INSERT OR IGNORE INTO shelters (name, latitude, longitude, address, capacity, availableCapacity, riskLevel, isActive, facilities, contact)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            ''', (s['name'], s['lat'], s['lng'], s['address'], s['capacity'], avail, risk, s['facilities'], s['contact']))
            
        conn.commit()
        print("Shelters database seeded successfully!")
    
    conn.close()

if __name__ == '__main__':
    init_db()
