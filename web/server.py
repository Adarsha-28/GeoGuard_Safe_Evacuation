import http.server
import socketserver
from concurrent.futures import ThreadPoolExecutor
import os
import json
import sqlite3
import sys
import urllib.parse
import urllib.request
import math
from shapely.geometry import Point, Polygon

# Ensure database is seeded
sys.path.append(r'c:\Users\ADARSHA\Desktop\GeoGuard')
from web.database import init_db, DB_PATH, GEOJSON_PATH, get_risk_level

# Initialize database
init_db()

# Change to the GeoGuard directory
os.chdir(r'c:\Users\ADARSHA\Desktop\GeoGuard')

PORT = 8000

# Load OSRM URL from .env
OSRM_URL = "https://router.project-osrm.org"
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.strip().startswith("OSRM_URL="):
                OSRM_URL = line.strip().split("=", 1)[1].strip()

# Load GeoJSON flood risk polygons globally
print("Loading GeoJSON risk polygons...")
with open(GEOJSON_PATH, "r") as f:
    GEOJSON_DATA = json.load(f)
print("GeoJSON risk polygons loaded!")

# Cache polygons for quick shapely queries
POLYGONS_CACHE = []
for feature in GEOJSON_DATA.get('features', []):
    geom = feature.get('geometry', {})
    if geom.get('type') == 'Polygon':
        poly = Polygon(geom['coordinates'][0])
        risk = feature['properties'].get('flood_risk', 'Low')
        minx, miny, maxx, maxy = poly.bounds
        POLYGONS_CACHE.append((poly, risk, minx, miny, maxx, maxy))

# Global in-memory cache for OSRM routes
ROUTE_CACHE = {}
# Global in-memory cache for coordinate risk checks
COORD_RISK_CACHE = {}
# Global in-memory cache for fully evaluated routes (geometry and calculated risk safety scores)
EVALUATED_ROUTE_CACHE = {}

def query_risk_level(lat, lng):
    cache_key = (round(lat, 4), round(lng, 4))
    if cache_key in COORD_RISK_CACHE:
        return COORD_RISK_CACHE[cache_key]

    point = None
    for poly, risk, minx, miny, maxx, maxy in POLYGONS_CACHE:
        if minx <= lng <= maxx and miny <= lat <= maxy:
            if point is None:
                point = Point(lng, lat)
            if poly.contains(point):
                COORD_RISK_CACHE[cache_key] = risk
                return risk
    COORD_RISK_CACHE[cache_key] = 'Low'
    return 'Low'

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = math.sin(dlat / 2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == '/api/shelters/all':
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM shelters WHERE isActive = 1')
            shelters = [dict(s) for s in cursor.fetchall()]
            conn.close()
            self.send_json_response(shelters)
        elif parsed_url.path == '/api/shelters/nearby':
            query = urllib.parse.parse_qs(parsed_url.query)
            try:
                lat = float(query.get('lat', [0])[0])
                lng = float(query.get('lng', [0])[0])
                radius = float(query.get('radius', [5])[0])
            except ValueError:
                self.send_error_response(400, "Invalid coordinates or radius parameters")
                return

            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM shelters WHERE isActive = 1')
            shelters = cursor.fetchall()
            conn.close()

            nearby_shelters = []
            for s in shelters:
                dist = haversine(lat, lng, s['latitude'], s['longitude'])
                if dist <= radius:
                    s_dict = dict(s)
                    s_dict['distance'] = dist
                    nearby_shelters.append(s_dict)

            # Sort by distance
            nearby_shelters.sort(key=lambda x: x['distance'])

            self.send_json_response(nearby_shelters)
        else:
            super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == '/api/evacuation/start':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                shelter_id = int(data.get('shelter_id'))
            except (ValueError, KeyError, TypeError):
                self.send_error_response(400, "Invalid payload. 'shelter_id' is required as an integer.")
                return

            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch current capacity
            cursor.execute('SELECT * FROM shelters WHERE id = ? AND isActive = 1', (shelter_id,))
            shelter = cursor.fetchone()
            if not shelter:
                conn.close()
                self.send_error_response(404, "Shelter not found or is inactive.")
                return
            
            shelter = dict(shelter)
            current_avail = shelter['availableCapacity']
            if current_avail <= 0:
                conn.close()
                self.send_error_response(400, "Shelter is already at full capacity.")
                return
            
            # Decrement capacity
            new_avail = current_avail - 1
            cursor.execute('UPDATE shelters SET availableCapacity = ? WHERE id = ?', (new_avail, shelter_id))
            conn.commit()
            conn.close()
            
            shelter['availableCapacity'] = new_avail
            self.send_json_response({
                "message": "Evacuation started. Capacity updated successfully.",
                "shelter": shelter
            })
        elif parsed_url.path in ['/api/routes/safe', '/api/routes/recalculate']:
            import time
            t0 = time.time()
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                lat = float(data.get('latitude'))
                lng = float(data.get('longitude'))
            except (ValueError, KeyError, TypeError):
                self.send_error_response(400, "Invalid payload. 'latitude' and 'longitude' are required numbers.")
                return

            # Fetch active shelters with capacity > 0
            t1 = time.time()
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM shelters WHERE isActive = 1 AND availableCapacity > 0')
            shelters = [dict(s) for s in cursor.fetchall()]
            conn.close()
            t2 = time.time()
            print(f"[TIMING] DB fetch took: {t2 - t1:.4f}s")

            if not shelters:
                self.send_error_response(404, "No active shelters with available capacity found.")
                return

            # Sort shelters by straight-line (Haversine) distance and evaluate the top 3
            for shelter in shelters:
                shelter['haversine_dist'] = haversine(lat, lng, shelter['latitude'], shelter['longitude'])
            shelters.sort(key=lambda s: s['haversine_dist'])
            shelters = shelters[:3]

            candidate_routes = []
            uncached_shelters = []
            
            # Check EVALUATED_ROUTE_CACHE first
            for shelter in shelters:
                cache_key = (round(lat, 4), round(lng, 4), shelter['id'])
                if cache_key in EVALUATED_ROUTE_CACHE:
                    print(f"Evaluated Route Cache hit for shelter {shelter['name']}")
                    route_eval = EVALUATED_ROUTE_CACHE[cache_key]
                    
                    # Combine cached route evaluation with current database values (like availableCapacity)
                    candidate_routes.append({
                        "shelter": {
                            "id": shelter['id'],
                            "name": shelter['name'],
                            "distance": route_eval['dist_km'],
                            "capacity": shelter['capacity'],
                            "availableCapacity": shelter['availableCapacity'],
                            "riskLevel": shelter['riskLevel'],
                            "address": shelter['address'],
                            "facilities": shelter['facilities'],
                            "contact": shelter['contact']
                        },
                        "route": route_eval['route_data'],
                        "score": route_eval['score'],
                        "reason": route_eval['reason']
                    })
                else:
                    uncached_shelters.append(shelter)

            if uncached_shelters:
                def fetch_route(s):
                    cache_key = (round(lat, 4), round(lng, 4), s['id'])
                    if cache_key in ROUTE_CACHE:
                        return s, ROUTE_CACHE[cache_key]

                    print(f"Route Cache miss for shelter {s['name']}. Querying OSRM...")
                    osrm_req_url = f"{OSRM_URL}/route/v1/driving/{lng},{lat};{s['longitude']},{s['latitude']}?overview=full&geometries=geojson"
                    try:
                        req = urllib.request.Request(osrm_req_url, headers={'User-Agent': 'GeoGuard Evacuation System'})
                        with urllib.request.urlopen(req, timeout=5) as response:
                            res_data = json.loads(response.read().decode('utf-8'))
                        if res_data.get('code') == 'Ok' and res_data.get('routes'):
                            route = res_data['routes'][0]
                            ROUTE_CACHE[cache_key] = route
                            return s, route
                    except Exception as e:
                        print(f"OSRM routing failed for shelter {s['name']}: {e}")
                    return s, None

                # Query routes in parallel using ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=len(uncached_shelters)) as executor:
                    results = list(executor.map(fetch_route, uncached_shelters))

                for shelter, route_info in results:
                    if not route_info:
                        continue
                    geometry = route_info['geometry']
                    distance = route_info['distance'] # in meters
                    duration = route_info['duration'] # in seconds

                    # 2. Risk check along the route points
                    points = geometry.get('coordinates', [])
                    high_severe_count = 0
                    total_points = len(points)
                    max_risk = 'Low'
                    risk_levels_list = []

                    for pt in points:
                        pt_risk = query_risk_level(pt[1], pt[0])
                        risk_levels_list.append(pt_risk)
                        if pt_risk in ['High', 'Severe']:
                            high_severe_count += 1
                        if pt_risk == 'Severe':
                            max_risk = 'Severe'
                        elif pt_risk == 'High' and max_risk != 'Severe':
                            max_risk = 'High'
                        elif pt_risk == 'Moderate' and max_risk not in ['High', 'Severe']:
                            max_risk = 'Moderate'

                    # Calculate cumulative risk score (0.0 = safe, 1.0 = dangerous)
                    # We also penalize if the shelter itself is in a dangerous zone
                    shelter_risk = shelter['riskLevel']
                    shelter_risk_penalty = 1.0 if shelter_risk == 'Severe' else 0.8 if shelter_risk == 'High' else 0.2 if shelter_risk == 'Moderate' else 0.0

                    points_penalty = (high_severe_count / total_points) if total_points > 0 else 0.0
                    combined_risk = max(points_penalty, shelter_risk_penalty)

                    # Safety score (0.0 to 1.0)
                    safety_score = 1.0 - combined_risk

                    # Normalizations for scoring (higher is better)
                    dist_km = distance / 1000.0
                    distance_score = 1.0 / (1.0 + dist_km)

                    # Time score (1.0 = immediate, decays as time grows)
                    duration_mins = duration / 60.0
                    time_score = 1.0 / (1.0 + duration_mins)

                    # Route scoring weights: Safety = 50%, Distance = 30%, Time = 20%
                    route_score = (0.5 * safety_score) + (0.3 * distance_score) + (0.2 * time_score)

                    # Construct reason
                    reason = "Selected because it avoids high-risk flood zones and offers the safest path."
                    if shelter_risk in ['High', 'Severe']:
                        reason = f"Warning: Nearest shelter is located in a {shelter_risk.lower()} risk zone, but this path is optimized to be as safe as possible."
                    elif high_severe_count > 0:
                        reason = "Route passes briefly near moderate/high risk areas but remains the safest available choice."
                    
                    route_data = {
                        "distance": distance,
                        "duration": duration,
                        "riskScore": float(combined_risk),
                        "safetyScore": float(safety_score),
                        "geometry": geometry
                    }

                    # Store in EVALUATED_ROUTE_CACHE
                    cache_key = (round(lat, 4), round(lng, 4), shelter['id'])
                    EVALUATED_ROUTE_CACHE[cache_key] = {
                        "dist_km": dist_km,
                        "route_data": route_data,
                        "score": route_score,
                        "reason": reason
                    }

                    candidate_routes.append({
                        "shelter": {
                            "id": shelter['id'],
                            "name": shelter['name'],
                            "distance": dist_km,
                            "capacity": shelter['capacity'],
                            "availableCapacity": shelter['availableCapacity'],
                            "riskLevel": shelter['riskLevel'],
                            "address": shelter['address'],
                            "facilities": shelter['facilities'],
                            "contact": shelter['contact']
                        },
                        "route": route_data,
                        "score": route_score,
                        "reason": reason
                    })

            if not candidate_routes:
                self.send_error_response(404, "Unable to calculate any valid route to nearby shelters.")
                return

            # Select the route with the highest score
            candidate_routes.sort(key=lambda r: r['score'], reverse=True)
            best_choice = candidate_routes[0]

            print(f"[TIMING] Total safe route endpoint processing took: {time.time() - t0:.4f}s")
            self.send_json_response(best_choice)
        else:
            self.send_error_response(404, "Not Found")

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_error_response(self, status, message):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

Handler = MyHTTPRequestHandler

# Run server
with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
    print(f"Server running at http://localhost:{PORT}/")
    print(f"Open http://localhost:{PORT}/web/index.html in your browser")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()
