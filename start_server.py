#!/usr/bin/env python3
"""
News Dashboard Web Server
Starts the application in web server mode for VPS deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the News Dashboard as a web server"""
    print("=" * 70)
    print("🚀 Starting News Dashboard Web Server")
    print("=" * 70)
    
    # Set environment variables for server mode
    os.environ['SERVER_MODE'] = 'true'
    os.environ['HOST'] = '0.0.0.0'  # Bind to all interfaces
    os.environ['PORT'] = '8080'     # Default port
    
    # Allow custom host/port via command line
    if len(sys.argv) > 1:
        os.environ['HOST'] = sys.argv[1]
    if len(sys.argv) > 2:
        os.environ['PORT'] = sys.argv[2]
    
    host = os.environ['HOST']
    port = os.environ['PORT']
    
    print(f"🌐 Server will be accessible at: http://{host}:{port}")
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🌍 External access: http://YOUR_VPS_IP:{port}")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    
    try:
        # Import and run the main application
        from app import main
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
