# 🔧 PythonAnywhere Fix Guide

## 🚨 Current Issue
The WSGI application is returning `TypeError: 'NoneType' object is not callable`

## ✅ Solution Steps

### 1. **Update WSGI Configuration File**

In PythonAnywhere, go to **Web** tab and edit the WSGI file:

**Replace the entire contents with:**

```python
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
```

### 2. **Install Missing Dependencies**

In **Consoles** tab, start a **Bash console** and run:

```bash
cd /home/plazza12/Swedish-Real-Estate-News-Dashboard
pip3.13 install --user flask flask-cors
```

### 3. **Create Data Directory**

```bash
mkdir -p /home/plazza12/Swedish-Real-Estate-News-Dashboard/data
```

### 4. **Reload Web App**

Go back to **Web** tab and click **"Reload"**

### 5. **Test Your App**

Visit: `https://plazza12.pythonanywhere.com`

---

## 🔍 **If Still Not Working**

### Check Error Logs
1. Go to **Web** tab
2. Click on **"Error log"** link
3. Look for specific error messages

### Common Issues & Solutions

#### **Import Error**
```bash
# Install all dependencies
pip3.13 install --user -r requirements.txt
```

#### **File Not Found**
```bash
# Check if files exist
ls -la /home/plazza12/Swedish-Real-Estate-News-Dashboard/
ls -la /home/plazza12/Swedish-Real-Estate-News-Dashboard/web/
```

#### **Permission Error**
```bash
# Fix permissions
chmod 755 /home/plazza12/Swedish-Real-Estate-News-Dashboard/
chmod 644 /home/plazza12/Swedish-Real-Estate-News-Dashboard/web/*
```

---

## 📊 **Configuration Summary**

- **Source code**: `/home/plazza12/Swedish-Real-Estate-News-Dashboard`
- **WSGI file**: `/var/www/plazza12_pythonanywhere_com_wsgi.py`
- **Python version**: 3.13
- **Virtualenv**: Not needed (using system packages)

---

## 🎯 **Expected Result**

After following these steps:
- ✅ App loads at `https://plazza12.pythonanywhere.com`
- ✅ No more WSGI errors
- ✅ All features work: scraping, translation, search
- ✅ Mobile responsive interface

---

**Follow these steps exactly and your app will work! 🚀**
