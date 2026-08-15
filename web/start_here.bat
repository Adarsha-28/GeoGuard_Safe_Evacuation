@echo off
echo ========================================
echo   GeoGuard - Chennai Flood Monitor
echo ========================================
echo.
echo Starting server from web directory...
echo.
echo Open your browser and go to:
echo http://localhost:8000/index.html
echo.
echo Press Ctrl+C to stop the server
echo.
python -m http.server 8000
pause
