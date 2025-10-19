@echo off
REM News Dashboard Web Server Startup Script for Windows
echo ========================================
echo Starting News Dashboard Web Server
echo ========================================

REM Set environment variables for server mode
set SERVER_MODE=true
set HOST=0.0.0.0
set PORT=8080

echo Server will be accessible at: http://localhost:8080
echo External access: http://YOUR_VPS_IP:8080
echo.
echo Press Ctrl+C to stop the server
echo ========================================

REM Start the server
python start_server.py

pause
