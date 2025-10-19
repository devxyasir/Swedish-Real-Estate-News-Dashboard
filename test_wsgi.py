"""
Test script to verify WSGI configuration works
Run this in PythonAnywhere console to test
"""

import sys
import os

# Add the project directory to Python path
project_dir = '/home/plazza12/Swedish-Real-Estate-News-Dashboard'
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Set environment variable
os.environ['HTTP_HOST'] = 'plazza12.pythonanywhere.com'

try:
    # Import the main app module
    import app
    print("✅ App module imported successfully")
    
    # Check if Eel is initialized
    print(f"✅ Eel initialized: {app.eel}")
    
    # Check if Flask app exists
    flask_app = app.eel._eel._flask_app
    print(f"✅ Flask app found: {flask_app}")
    
    # Test a simple route
    with flask_app.test_client() as client:
        response = client.get('/')
        print(f"✅ Root route works: {response.status_code}")
        
    print("🎉 WSGI configuration is working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
