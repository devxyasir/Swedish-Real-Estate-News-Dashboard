"""
WSGI configuration for PythonAnywhere deployment
This file is required for PythonAnywhere to serve the application
"""

import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Set environment variable to indicate we're on PythonAnywhere
os.environ['HTTP_HOST'] = 'plazza12.pythonanywhere.com'

# Import and create the Flask application
from app import create_app

# Create the Flask app
application = create_app()
