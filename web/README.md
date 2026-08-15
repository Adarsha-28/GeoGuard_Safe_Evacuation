# GeoGuard Web Application

## 🚀 How to Run

### Option 1: Using Python HTTP Server (Recommended)

1. Open Command Prompt or Terminal
2. Navigate to the web directory:
   ```
   cd c:\Users\ADARSHA\Desktop\GeoGuard\web
   ```
3. Run the server:
   ```
   python server.py
   ```
4. Open your browser and go to: http://localhost:8000/web/index.html

### Option 2: Using Python's Built-in Server

1. Open Command Prompt or Terminal
2. Navigate to the GeoGuard directory:
   ```
   cd c:\Users\ADARSHA\Desktop\GeoGuard
   ```
3. Run Python's HTTP server:
   ```
   python -m http.server 8000
   ```
4. Open your browser and go to: http://localhost:8000/web/index.html

### Option 3: Using VS Code Live Server

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

## 📁 File Structure

```
GeoGuard/
├── web/
│   ├── index.html      # Main HTML file
│   ├── style.css       # Styling
│   ├── app.js          # JavaScript logic
│   └── server.py       # Simple HTTP server
└── data/
    └── processed/
        └── chennai_flood_risk_with_water.geojson
```

## 🔧 Troubleshooting

**Problem**: Data not loading / CORS error

**Solution**: You must use a local server (Option 1 or 2 above). Browsers block direct file access for security reasons.

**Problem**: Port 8000 already in use

**Solution**: Change the PORT number in server.py to 8001, 8080, or any available port.

## 🎯 Features

- Interactive map with color-coded flood risk zones
- Real-time statistics dashboard
- Emergency contact information
- Hover and click interactions on map zones
- Responsive design
