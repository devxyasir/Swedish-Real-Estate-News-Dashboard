#!/bin/bash
# News Dashboard Web Server Startup Script for Linux/VPS

echo "========================================"
echo "🚀 Starting News Dashboard Web Server"
echo "========================================"

# Set environment variables for server mode
export SERVER_MODE=true
export HOST=0.0.0.0
export PORT=8080

# Allow custom host/port via command line
if [ ! -z "$1" ]; then
    export HOST="$1"
fi
if [ ! -z "$2" ]; then
    export PORT="$2"
fi

echo "🌐 Server will be accessible at: http://$HOST:$PORT"
echo "📡 Host: $HOST"
echo "🔌 Port: $PORT"
echo "🌍 External access: http://YOUR_VPS_IP:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"

# Start the server
python3 start_server.py
