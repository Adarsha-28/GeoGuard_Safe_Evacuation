@echo off
echo ========================================
echo   GeoGuard - Chennai Flood Monitor
echo ========================================
echo.
echo Starting local server...
echo.
echo Server will start in the GeoGuard directory
echo.
cd /d "%~dp0.."
echo Current directory: %CD%
echo.
echo Open your browser and go to:
echo http://localhost:8000/web/index.html
echo.
echo Press Ctrl+C to stop the server
echo.
python -m http.server 8000
pause
