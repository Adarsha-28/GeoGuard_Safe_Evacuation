# 🛡️ GeoGuard: Chennai Flood Risk Monitor & Safe Evacuation System

GeoGuard is an agentic, data-driven web application designed to monitor flood risk levels across Chennai, locate nearby relief shelters, and calculate the safest, easiest evacuation routes avoiding high-risk zones.

---

## 🚀 Key Features

* **Interactive Flood Risk Map**: Visualizes Chennai zones classified by risk levels (Low, Moderate, High, Severe) overlayed using Leaflet.js.
* **Global Relief Shelters database**: Renders all active relief shelters on the map with details on available capacity, contact information, and facilities.
* **Safe Route Calculation**: An intelligent OSRM-based routing service that penalizes routes passing through high/severe flood-risk areas and computes the safest path to the nearest available shelter.
* **Google Maps Styling**: Beautiful, glowing route visualizations indicating the calculated path clearly.
* **Random Demo Location Generator**: One-click demo locator to test evacuation scenarios anywhere in Chennai.

---

## 🛠️ Project Architecture

* **Backend**: Python HTTP Server serving static files and API routing queries.
* **Routing Engine**: Project-OSRM (Open Source Routing Machine).
* **Database**: SQLite database (`data/shelters.db`) storing shelter availability, capacity, and status.
* **Frontend**: Vanilla HTML5, CSS3, and Leaflet.js with custom markers and styles.

---

## 📦 Setup & Installation

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Run Server
Run the local python server:
```bash
python web/server.py
```
Open **`http://localhost:8000/web/index.html`** in your browser.

---

## 📁 File Structure

```text
├── data/                    # SQLite database and GeoJSON maps
├── web/                     # Frontend dashboard and backend server script
│   ├── index.html           # Main dashboard
│   ├── app.js               # Frontend interactive logic
│   ├── server.py            # API server & safe route calculation
│   └── database.py          # Database seeding
├── requirements.txt         # Project package dependencies
└── .gitignore               # Ignored local venvs and build caches
```
