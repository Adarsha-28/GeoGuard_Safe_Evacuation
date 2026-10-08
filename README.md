# GeoGuard V6: Flood Scenario Simulation, Adaptive Evacuation & Resilience Intelligence

GeoGuard is an enterprise predictive geospatial disaster management, scenario simulation, and evacuation resilience platform designed for Chennai, Tamil Nadu.

* **GeoGuard V1**: Foundational architecture (HTML/CSS/JS frontend, Python backend, SQLite, deterministic flood risk scoring, shelter discovery, OSRM routing).
* **GeoGuard V2**: Enterprise geospatial backend with **FastAPI**, **PostgreSQL 18**, **PostGIS 3.6**, **SQLAlchemy 2.0**, **GeoAlchemy2**, **Pydantic v2**, and **Alembic** migrations.
* **GeoGuard V3**: Verifiable, empirical **Machine Learning flood-risk prediction pipeline** using real historical inundation survey records (OpenCity) and meteorological reanalysis (Open-Meteo ERA5), benchmarked directly against the V2 deterministic baseline.
* **GeoGuard V4**: Automated **Near-Real-Time Operational Flood Intelligence** continuously collecting live Open-Meteo weather data, engineering rolling rainfall features, executing batch ML inference across all 34 monitored sectors, tracking spatial risk transitions, dispatching calibrated emergency advisories, and protecting operational scheduling with non-blocking concurrency guards.
* **GeoGuard V5**: **Predictive Flood Intelligence & Decision Support Platform** introducing multi-horizon forecasting (`nowcast`, `6h`, `12h`, `24h`), prediction change detection and temporal delta intelligence, calibrated confidence reporting, model-supported explainable feature attribution, operational sector triage prioritization, shelter suitability, route hazard exposure, and an operational command center event timeline.
* **GeoGuard V6**: **Flood Scenario Simulation, Adaptive Evacuation & Resilience Intelligence Platform** introducing non-destructive rainfall stress simulation (+25%, +50%, +75%, +100%, custom), PostGIS spatial risk propagation (`ST_Touches`/`ST_DWithin`), shelter capacity stress testing (1.0x, 1.25x, 1.5x, 2.0x), multi-path route resilience (Primary, Alt 1, Alt 2), transparent 5-factor municipal resilience scoring ($R_{system} = 0.25 R_s + 0.25 R_r + 0.15 R_d + 0.15 R_m + 0.20 R_o$), 6 controlled failure simulations, and an interactive V6 Scenario Lab command center.

---

## 🚀 1. Core Capabilities of V6

* **Flood Scenario Simulation Engine**: Multi-horizon rainfall surge modeling (+25%, +50%, +75%, +100%, custom multiplier) modifying feature vectors with zero model retraining; outputs $\Delta P$, risk transitions, and mandatory disclaimer `"SIMULATED SCENARIO — NOT OBSERVED FLOOD DATA"`.
* **PostGIS Spatial Risk Propagation**: Distinguishes direct flood hazard from neighbor-influenced buffer hazard using topological spatial boundaries (`ST_Touches` and `ST_DWithin`).
* **Adaptive Evacuation Planner**: Triage prioritization and dynamic allocation of primary and backup relief shelters.
* **Shelter Capacity Stress Testing**: Evaluates facility headroom under surge demand factors (1.0x - 2.0x), classifying facilities into `NORMAL`, `STRESSED`, or `OVERLOADED` and identifying relief center alternatives.
* **Route Resilience & Alternatives**: Evaluates multi-path alternatives (Primary, Alternative 1, Alternative 2) with status badges (`AVAILABLE`, `CAUTION`, `UNSAFE`, `BLOCKED_BY_SIMULATION`).
* **Mathematical Resilience Index ($R_{system}$)**: Quantifies municipal disaster resilience on a transparent $[0, 100]$ scale across shelter, route, data, model, and operational dimensions.
* **Controlled Failure & Fallback Doubles**: 6 controlled test doubles verifying automatic fallback activation for weather API outages, stale observations, ML corruption, database failure, OSRM outage, and scheduler crashes.
* **Interactive Scenario Lab & Decision Audit**: Dynamic simulation interface with persistent warning banner, side-by-side baseline comparisons, and chronological audit ledger (`GET /api/v6/decision-log`).
* **100% Automated Test Suite**: 117 automated unit, API, and integration tests passing 100% with zero regressions.


---

## 🏛️ 3. System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│               Frontend Layer (Preserved V1 Contract)                    │
│   HTML5 / Vanilla CSS3 / JavaScript / Leaflet.js / Chart.js            │
│   Dashboard: /frontend/index.html   |   Admin: /frontend/admin.html     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST (JSON / GeoJSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       FastAPI Application Layer                        │
│   - CORS Middleware (configurable allowed origins)                     │
│   - Unified Exception Handlers (RequestValidationError, HTTPException) │
│   - Lifespan Context Manager (Background Weather Sync Worker)          │
│   - Automatic OpenAPI Documentation (/docs, /redoc)                    │
├────────────────────────────────────────────────────────────────────────┤
│   API Routers (/backend/api/):                                         │
│   ├── health.py   -> GET  /api/health                                  │
│   ├── grids.py    -> GET  /api/grids, GET /api/grids/{id}              │
│   ├── risk.py     -> GET  /api/risk/{id}, GET /api/risk/point          │
│   ├── shelters.py -> GET  /api/shelters, GET /api/shelters/nearby      │
│   ├── routes.py   -> POST /api/routes/safe, POST /api/evacuation/start │
│   ├── alerts.py   -> GET  /api/alerts, POST /api/alerts                │
│   └── weather.py  -> POST /api/weather/sync                            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Pydantic v2 Schemas & Validation
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Service Business Logic Layer                    │
│   ├── risk_service.py    -> Deterministic formula & PostGIS lookup     │
│   ├── shelter_service.py -> PostGIS ST_DWithin & atomic capacity locks │
│   ├── routing_service.py -> OSRM integration & polyline risk evaluation│
│   ├── weather_service.py -> Open-Meteo sync with fallback cache        │
│   └── alert_service.py   -> Emergency advisory bulletin transactions   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ SQLAlchemy 2.0 / GeoAlchemy2
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     PostgreSQL 16/18 + PostGIS 3.4/3.6                 │
│   - Connection Pool (pool_size=10, max_overflow=20, pool_pre_ping=True)│
│   - Alembic Database Migrations (alembic/versions/001_initial_schema)  │
│   - Spatial GiST Indexes (idx_shelters_location, idx_grids_geom)       │
│   - Integrity Constraints (CHECK capacity >= 0, CHECK severity IN (...))│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 4. Deterministic Risk Scoring Model

GeoGuard strictly preserves its deterministic multi-criteria flood hazard model based on physical spatial indicators:

1. **Precipitation Component** ($50\%$ weight):
   $$\text{RainfallScore} = \min\left(1.0, \frac{\text{rainfall\_mm}}{150.0}\right)$$
2. **Inverted Digital Elevation** ($25\%$ weight, lower ground = higher hazard):
   $$\text{ElevationScore} = \frac{\max(\text{Elevations}) - \text{elevation\_m}}{\max(\text{Elevations}) - \min(\text{Elevations})}$$
3. **Inverted Water Proximity** ($25\%$ weight, closer to water = higher hazard):
   $$\text{WaterProximityScore} = \frac{\max(\text{WaterDist}) - \text{distance\_to\_water\_m}}{\max(\text{WaterDist}) - \min(\text{WaterDist})}$$

### Composite Risk Formula:
$$\text{RiskScore} = (0.50 \cdot \text{RainfallScore}) + (0.25 \cdot \text{ElevationScore}) + (0.25 \cdot \text{WaterProximityScore})$$

### Categorical Action Thresholds:
| Classification | Score Range | Operational Disaster Stance |
|---|---|---|
| **LOW** | $0.00 \le \text{Score} < 0.30$ | Routine baseline monitoring |
| **MODERATE** | $0.30 \le \text{Score} < 0.60$ | Heightened awareness; alert field staff |
| **HIGH** | $0.60 \le \text{Score} < 0.85$ | Active flood alert; prepare relief shelters |
| **SEVERE** | $0.85 \le \text{Score} \le 1.00$ | Critical emergency; execute safe evacuations |

---

## 🌐 5. PostGIS Spatial Query Implementation

In V1, nearby shelter discovery evaluated the Haversine formula across every shelter in Python memory. In V2, spatial operations are pushed directly into the PostgreSQL database engine:

### 1. Spatial Distance & Radius Filter (`ST_DWithin` & `ST_Distance`):
```sql
SELECT 
    id, name, latitude, longitude, address, capacity, available_capacity,
    risk_level, is_active, facilities, contact,
    ST_Distance(location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) / 1000.0 AS dist_km
FROM shelters
WHERE is_active = true
  AND (:available_only = false OR available_capacity > 0)
  AND ST_DWithin(location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_meters)
ORDER BY dist_km ASC
LIMIT :limit;
```

### 2. Sector Polygon Containment (`ST_Contains`):
```sql
SELECT flood_risk 
FROM grids 
WHERE geom IS NOT NULL 
  AND ST_Contains(geom, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
LIMIT 1;
```

### 3. Spatial Index Inspection (`EXPLAIN ANALYZE`):
Empirical execution plan on the PostGIS GiST index:
```text
Bitmap Heap Scan on shelters (cost=4.31..239.57 rows=1 width=430) (actual time=0.046..0.155 rows=25 loops=1)
  Recheck Cond: (is_active AND (available_capacity > 0))
  Filter: st_dwithin((location)::geography, ...::geography, 20000, true)
  -> Bitmap Index Scan on idx_shelters_active_avail (cost=0.00..4.31 rows=17 width=0)
Planning Time: 0.221 ms | Execution Time: 0.209 ms
```

---

## 📦 6. Installation & Quickstart

### Prerequisites
- Python 3.10+
- PostgreSQL 16+ with PostGIS extension (or Docker)

### Option A: Docker Compose (Recommended for Containerized Environments)
```bash
docker compose up -d
```

### Option B: Local PostgreSQL Setup (Windows Standalone)
```bash
python scripts/setup_local_postgres.py
```

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env` and configure your database URL:
```ini
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/geoguard
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
PORT=8000
```

### Step 3: Run Database Migrations & Initial Data Loading
```bash
# Apply Alembic schema migrations
python -m alembic upgrade head

# Load Chennai geospatial grids, shelters, and baseline alerts
python scripts/init_db.py

# (Optional) Migrate legacy SQLite data if upgrading from V1
python scripts/migrate_v1_data.py
```

### Step 4: Run the Complete Automated Test Suite
```bash
python -m pytest tests/ -v
```
All 32 tests across `tests/unit/`, `tests/api/`, and `tests/integration/` should pass.

### Step 5: Start the GeoGuard V2 Server
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 6: Access Dashboards & Interactive API Documentation
* **Interactive Map Dashboard**: [http://localhost:8000/frontend/index.html](http://localhost:8000/frontend/index.html)
* **Administrative Command Center**: [http://localhost:8000/frontend/admin.html](http://localhost:8000/frontend/admin.html) *(Demo credentials: `admin` / `admin123`)*
* **Interactive OpenAPI Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Technical Specification**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## ⚡ 7. Performance Benchmark (V1 vs V2)

Run the empirical benchmark comparing application-level Haversine distance math against database-side PostGIS spatial indexing:
```bash
python scripts/benchmark_spatial.py
```

* **V1 Python In-Memory Haversine**: ~0.035 ms (fast for 25 points, but requires pulling entire dataset over network and scales as $O(N)$ with memory bloat).
* **V2 PostGIS GiST Index Spatial Query**: ~0.209 ms execution time (scales to 100,000+ points using R-tree bounding-box pruning, sub-millisecond execution, and zero application memory footprint).

---

## 📡 8. REST API Reference

| Method | Endpoint | Parameters / Payload | Description |
|---|---|---|---|
| `GET` | `/api/health` | None | System health, database connection, and risk counts |
| `GET` | `/api/grids` | `?model=ml` / `?model=deterministic` | GeoJSON FeatureCollection of all monitored sectors |
| `GET` | `/api/grids/{id}` | `id: int` | GeoJSON Feature for specific sector |
| `GET` | `/api/risk/point` | `lat: float, lng: float` | PostGIS polygon containment & KNN nearest sector |
| `GET` | `/api/risk/{id}` | `id: int` | Stored risk indicators for sector |
| `POST` | `/api/predictions/flood` | `{"latitude", "longitude", "rainfall_mm"}` | Empirical ML flood probability & feature attribution |
| `POST` | `/api/weather/sync` | None | Trigger live precipitation poll from Open-Meteo |
| `GET` | `/api/shelters` | None | All active relief shelters |
| `GET` | `/api/shelters/nearby` | `lat, lng, radius, limit` | PostGIS `ST_DWithin` nearest shelter discovery |
| `GET` | `/api/shelters/{id}` | `id: int` | Specific shelter accommodation details |
| `POST` | `/api/routes/safe` | `{"latitude": ..., "longitude": ...}` | OSRM road trajectory with PostGIS hazard evaluation |
| `POST` | `/api/evacuation/start` | `{"shelter_id": ...}` | Atomic transactional decrement of shelter capacity |
| `GET` | `/api/alerts` | None | Recent emergency advisory bulletins |
| `POST` | `/api/alerts` | `{"title", "severity", "zone", "message"}` | Publish new administrative emergency alert |

---

## 🧪 9. Test Suite Organization

```text
tests/
├── unit/
│   ├── test_ml_pipeline.py            # Anti-leakage chronological split & schema
│   ├── test_ml_prediction_service.py  # Model loading, bounds, determinism, fallback
│   ├── test_risk_service.py           # Deterministic scoring math & monotonicity
│   ├── test_shelter_service.py        # Haversine distance & coordinate validation
│   └── test_routing_service.py        # Route hazard penalties & scoring
├── api/
│   ├── test_ml_prediction_api.py      # /api/predictions/flood & model switching
│   ├── test_health_api.py             # /api/health contract & telemetry
│   ├── test_grids_api.py              # /api/grids GeoJSON schema
│   ├── test_risk_api.py               # /api/risk & point evaluation
│   ├── test_shelter_api.py            # /api/shelters & nearby PostGIS search
│   ├── test_routes_api.py             # /api/routes & atomic evacuation start
│   └── test_alerts_api.py             # /api/alerts CRUD & severity validation
└── integration/
    ├── test_database.py               # Connection pooling & check constraints
    ├── test_postgis.py                # PostGIS extension, GiST indexes, containment
    └── test_weather.py                # Open-Meteo live sync & fallback resilience
```
