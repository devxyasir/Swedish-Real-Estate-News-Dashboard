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

# Import the main application
from app import app

# PythonAnywhere will look for 'application' variable
application = app

# Alternative: If you want to use the Eel app directly
# from app import eel
# application = eel.app
