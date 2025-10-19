"""
WSGI configuration for PythonAnywhere deployment using Eel
This file is required for PythonAnywhere to serve the application
"""

import sys
import os

# Add the project directory to Python path
project_dir = '/home/plazza12/Swedish-Real-Estate-News-Dashboard'
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Set environment variable
os.environ['HTTP_HOST'] = 'plazza12.pythonanywhere.com'

# Import Eel and create the application
import eel

# Initialize Eel
eel.init('web')

# Get the Flask app from Eel
application = eel.app
