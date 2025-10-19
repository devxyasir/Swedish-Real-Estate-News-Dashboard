# 🐍 PythonAnywhere Setup Guide

## ✅ **Current Status**
Your app is now configured to use **Eel** on PythonAnywhere!

## 🚀 **Steps to Deploy:**

### 1. **Install Dependencies**
In PythonAnywhere **Consoles** tab, start a **Bash console**:
```bash
cd /home/plazza12/Swedish-Real-Estate-News-Dashboard
pip3.13 install --user -r requirements.txt
```

### 2. **Create Data Directory**
```bash
mkdir -p /home/plazza12/Swedish-Real-Estate-News-Dashboard/data
```

### 3. **Update WSGI File**
In PythonAnywhere **Web** tab, edit the WSGI file and replace ALL contents with:

```python
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
```

### 4. **Reload Web App**
Click **"Reload"** in the Web tab

### 5. **Test Your App**
Visit: `https://plazza12.pythonanywhere.com`

---

## 🎯 **What This Does:**

- ✅ **Uses Eel**: Your original app.js will work without changes
- ✅ **No Flask**: No need for flask_cors or complex API routes
- ✅ **Simple Setup**: Just Eel + your existing code
- ✅ **All Features**: Scraping, translation, search, filtering

---

## 🔧 **If You Get Errors:**

### **Import Error**
```bash
pip3.13 install --user eel
```

### **File Not Found**
```bash
ls -la /home/plazza12/Swedish-Real-Estate-News-Dashboard/web/
```

### **Permission Error**
```bash
chmod 755 /home/plazza12/Swedish-Real-Estate-News-Dashboard/
```

---

## 📱 **Your App Will Have:**
- ✅ **Eel Interface**: Same as desktop version
- ✅ **All 6 Sources**: Fastighetsvarlden, Cision, Lokalguiden, DI, Fastighetsnytt, Nordic Property News
- ✅ **Auto-Translation**: Swedish → English
- ✅ **Search & Filter**: Full functionality
- ✅ **Mobile Responsive**: Works on all devices

---

**This is the simplest approach - just Eel on PythonAnywhere! 🚀**
