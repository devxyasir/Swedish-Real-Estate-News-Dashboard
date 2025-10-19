# 🐍 PythonAnywhere Eel Setup - Step by Step

## 🚨 **Current Issues Fixed:**
- ✅ **No Flask**: Pure Eel setup
- ✅ **No flask_cors**: Not needed
- ✅ **Eel.js 404**: Fixed with proper Eel setup
- ✅ **WSGI Errors**: Fixed with correct Eel app access

---

## 🚀 **Step-by-Step Setup:**

### **1. Install Dependencies**
In PythonAnywhere **Consoles** tab, start a **Bash console**:
```bash
cd /home/plazza12/Swedish-Real-Estate-News-Dashboard
pip3.13 install --user eel requests beautifulsoup4 lxml deep-translator
```

### **2. Create Data Directory**
```bash
mkdir -p /home/plazza12/Swedish-Real-Estate-News-Dashboard/data
```

### **3. Update WSGI File**
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

# Import and initialize Eel
import eel

# Initialize Eel
eel.init('web')

# Get the Flask app from Eel's internal Flask instance
application = eel._eel._flask_app
```

### **4. Reload Web App**
Click **"Reload"** in the Web tab

### **5. Test Your App**
Visit: `https://plazza12.pythonanywhere.com`

---

## 🔧 **What This Setup Does:**

### ✅ **Pure Eel**
- No Flask complexity
- Uses Eel's internal Flask app
- All your existing functions work

### ✅ **Static Files**
- Serves `web/index.html`
- Serves `web/app.js`
- Serves `web/eel.js` (automatically)

### ✅ **API Functions**
- `check_for_new_articles()` - Scraping
- `get_articles()` - Load articles
- `get_data_location()` - Data path
- `open_data_folder()` - Open folder

---

## 🎯 **Expected Result:**

After following these steps:
- ✅ **Dashboard loads**: No more 404 errors
- ✅ **Eel.js loads**: JavaScript works
- ✅ **Scraping works**: All 6 sources
- ✅ **Translation works**: Swedish → English
- ✅ **Search works**: Filter articles
- ✅ **Mobile responsive**: Works on phones

---

## 🐛 **If You Still Get Errors:**

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
chmod 644 /home/plazza12/Swedish-Real-Estate-News-Dashboard/web/*
```

---

## 📱 **Your App Will Have:**
- ✅ **Full Dashboard**: Same as desktop version
- ✅ **6 News Sources**: All scrapers working
- ✅ **Auto-Translation**: Swedish → English
- ✅ **Real-time Scraping**: Live updates
- ✅ **Search & Filter**: Complete functionality
- ✅ **Mobile Access**: Works on all devices

---

**This is the cleanest Eel setup for PythonAnywhere! 🚀**
