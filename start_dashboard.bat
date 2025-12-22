@echo off
REM Start Training Dashboard Server
REM This will open a web-based live monitoring dashboard

echo ========================================
echo YOLOV8 TRAINING DASHBOARD
echo ========================================
echo.
echo Starting web server...
echo.
echo The dashboard will open in your browser automatically
echo.

REM Start the server
start http://localhost:8000
python dashboard_server.py

pause
