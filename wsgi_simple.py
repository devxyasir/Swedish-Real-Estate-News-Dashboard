"""
Simple WSGI configuration for PythonAnywhere
This is a backup WSGI file that should work reliably
"""

import sys
import os

# Add the project directory to Python path
project_dir = '/home/plazza12/Swedish-Real-Estate-News-Dashboard'
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Set environment variable
os.environ['HTTP_HOST'] = 'plazza12.pythonanywhere.com'

# Import Flask and create a simple app
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Create Flask app
app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)

# Simple routes
@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('web', filename)

# API routes
@app.route('/api/check_for_new_articles', methods=['POST'])
def check_articles():
    try:
        # Import here to avoid circular imports
        from app import check_for_new_articles
        result = check_for_new_articles()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_articles', methods=['GET'])
def get_articles_api():
    try:
        from app import get_articles
        source = request.args.get('source', 'all')
        page = int(request.args.get('page', 1))
        search = request.args.get('search', '')
        result = get_articles(source, page, search)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_data_location', methods=['GET'])
def get_data_location_api():
    try:
        from app import get_data_location
        result = get_data_location()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# PythonAnywhere looks for 'application' variable
application = app
