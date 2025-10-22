@echo off
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║    SMART DESK MONITOR - POSTURE ^& FOCUS TRACKER          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo Starting the monitor...
echo Press Ctrl+C to stop this script (then press Q in the app window)
echo.

cd /d "%~dp0"
python smart_desk_monitor_simple.py

echo.
echo Application closed. Check for session reports in this folder!
pause
