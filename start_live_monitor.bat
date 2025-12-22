@echo off
REM Live Training Monitor - Auto-updating every 10 seconds
REM Press Ctrl+C to stop monitoring

echo ========================================
echo STARTING LIVE TRAINING MONITOR
echo ========================================
echo.
echo This will show real-time updates every 10 seconds
echo Press Ctrl+C to stop monitoring
echo.
pause

python live_monitor.py
