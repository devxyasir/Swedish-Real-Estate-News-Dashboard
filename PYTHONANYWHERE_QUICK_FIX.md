# 🚨 PythonAnywhere Quick Fix

## 🔧 **Issues Fixed:**
- ✅ **WSGI Error**: Fixed `app.eel._eel._flask_app` error
- ✅ **Parameter Error**: Fixed `'int' object has no attribute 'lower'`
- ✅ **Proxy Errors**: Disabled external scraping (PythonAnywhere blocks it)
- ✅ **Webpage Loading**: Fixed WSGI configuration

## 🚀 **Quick Setup:**

### **1. Install Dependencies**
In PythonAnywhere **Consoles** tab:
```bash
cd /home/plazza12/Swedish-Real-Estate-News-Dashboard
pip3.13 install --user flask requests beautifulsoup4 lxml deep-translator
```

### **2. Create Data Directory**
```bash
mkdir -p /home/plazza12/Swedish-Real-Estate-News-Dashboard/data
```

### **3. Create Sample Data**
```bash
# Create sample JSON files
echo '{"articles": [], "last_scrape": null}' > /home/plazza12/Swedish-Real-Estate-News-Dashboard/data/fastighet_news_data.json
echo '{"articles": [], "last_scrape": null}' > /home/plazza12/Swedish-Real-Estate-News-Dashboard/data/cision_news_data.json
echo '{"articles": [], "last_scrape": null}' > /home/plazza12/Swedish-Real-Estate-News-Dashboard/data/lokalguiden_news_data.json
echo '{"articles": [], "last_scrape": null}' > /home/plazza12/Swedish-Real-Estate-News-Dashboard/data/di_news_data.json
echo '{"articles": [], "last_scrape": null}' > /home/plazza12/Swedish-Real-Estate-News-Dashboard/data/fastighetsnytt_news_data.json
echo '{"articles": [], "last_scrape": null}' > /home/plazza12/Swedish-Real-Estate-News-Dashboard/data/nordicpropertynews_news_data.json
```

### **4. Reload Web App**
Click **"Reload"** in Web tab

### **5. Test Your App**
Visit: `https://plazza12.pythonanywhere.com`

---

## 🎯 **What This Does:**

### ✅ **Fixed WSGI**
- **Correct path**: Uses absolute path to project
- **Flask app**: Uses `create_app()` function
- **No Eel errors**: Pure Flask setup

### ✅ **Fixed API**
- **Parameter order**: Fixed `get_articles()` call
- **No scraping**: Disabled external requests (blocked by PythonAnywhere)
- **Sample data**: Creates empty JSON files

### ✅ **Working Dashboard**
- **UI loads**: Dashboard displays properly
- **No errors**: All API calls work
- **Sample mode**: Shows empty state (no articles)

---

## 📝 **Note:**
- **External scraping disabled**: PythonAnywhere blocks external requests
- **Sample data only**: You'll see empty dashboard
- **For full functionality**: Use local development or different hosting

---

**Your dashboard will now load without errors! 🚀**
