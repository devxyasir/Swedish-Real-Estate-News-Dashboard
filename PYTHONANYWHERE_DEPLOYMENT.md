# 🐍 News Dashboard - PythonAnywhere Deployment Guide

Deploy your News Dashboard on PythonAnywhere for free web hosting!

## 🚀 Quick Start

### 1. Create PythonAnywhere Account
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for a **Beginner** account (free)
3. Verify your email

### 2. Upload Your Code
```bash
# Method 1: Upload via Files tab in PythonAnywhere dashboard
# - Go to Files tab
# - Create folder: /home/yourusername/news-dashboard/
# - Upload all your files

# Method 2: Use Git (if you have a repository)
git clone your-repo-url /home/yourusername/news-dashboard/
```

### 3. Install Dependencies
1. Go to **Consoles** tab
2. Start a **Bash console**
3. Run:
```bash
cd /home/yourusername/news-dashboard/
pip3.10 install --user -r requirements.txt
```

### 4. Configure Web App
1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **Python 3.10**
5. Set **Source code**: `/home/yourusername/news-dashboard/`
6. Set **WSGI file**: `/home/yourusername/news-dashboard/wsgi.py`

### 5. Configure WSGI File
In the **Web** tab, edit the WSGI file:
```python
import sys
path = '/home/yourusername/news-dashboard'
if path not in sys.path:
    sys.path.append(path)

from wsgi import application
```

### 6. Reload Web App
Click **"Reload"** button in the Web tab

### 7. Access Your App
Your app will be available at:
**`https://yourusername.pythonanywhere.com`**

---

## 📁 File Structure on PythonAnywhere

```
/home/yourusername/news-dashboard/
├── app.py                    # Main application
├── wsgi.py                   # WSGI configuration
├── config.py                 # Configuration
├── fastighetsvarlden_scraper.py
├── cision_scraper.py
├── lokalguiden_scraper.py
├── di_scraper.py
├── fastighetsnytt_scraper.py
├── nordicpropertynews_scraper.py
├── web/
│   ├── index.html
│   └── app.js
├── requirements.txt
└── news.png
```

---

## 🔧 Configuration Details

### WSGI Configuration (`wsgi.py`)
```python
import os
import sys

# Add project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Import the main application
from app import app

# PythonAnywhere looks for 'application' variable
application = app
```

### Flask App Configuration
The app automatically detects PythonAnywhere environment and switches to Flask mode.

---

## 📊 Data Storage

### Local Development
- Data saved to: `Documents/News Dashboard Data/`

### PythonAnywhere
- Data saved to: `/home/yourusername/news-dashboard/data/`
- Create the directory:
```bash
mkdir -p /home/yourusername/news-dashboard/data
```

---

## 🔄 Scheduled Tasks (Auto-Scraping)

### 1. Go to Tasks Tab
1. Click **"Tasks"** tab in PythonAnywhere dashboard
2. Click **"Add a new task"**

### 2. Create Scraping Task
```bash
# Command to run
cd /home/yourusername/news-dashboard && python3.10 -c "from app import check_for_new_articles; check_for_new_articles()"

# Schedule: Every hour
0 * * * *

# Or every 6 hours
0 */6 * * *
```

### 3. Alternative: Always-On Task
For **Paid accounts**, you can run a background task:
```bash
cd /home/yourusername/news-dashboard && python3.10 app.py
```

---

## 🌐 Custom Domain (Paid Accounts)

### 1. Upgrade to Paid Account
- **Hacker**: $5/month
- **Web Developer**: $20/month

### 2. Configure Custom Domain
1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Set **Domain**: `yourdomain.com`
5. Configure DNS to point to PythonAnywhere

---

## 📱 Mobile Access

Your app is fully responsive and works on:
- ✅ Desktop browsers
- ✅ Mobile phones
- ✅ Tablets
- ✅ Any device with internet

---

## 🔍 Troubleshooting

### App Won't Load
1. Check **Web** tab for errors
2. Check **Tasks** tab for console output
3. Verify all files are uploaded correctly

### Import Errors
```bash
# Check if all dependencies are installed
pip3.10 list

# Reinstall requirements
pip3.10 install --user -r requirements.txt
```

### Data Not Saving
```bash
# Create data directory
mkdir -p /home/yourusername/news-dashboard/data

# Check permissions
chmod 755 /home/yourusername/news-dashboard/data
```

### Scraping Not Working
1. Check **Tasks** tab for error logs
2. Verify internet connectivity
3. Check if websites are accessible

---

## 📈 Performance Tips

### 1. Optimize Scraping
- Use scheduled tasks instead of always-on
- Limit scraping frequency
- Monitor CPU usage

### 2. Data Management
- Regularly clean old data
- Monitor disk usage
- Backup important data

### 3. Free Account Limits
- **CPU seconds**: 100 per day
- **Disk space**: 1GB
- **Always-on tasks**: Not available

---

## 🎯 PythonAnywhere Account Types

### Beginner (Free)
- ✅ 1 web app
- ✅ 1 always-on task
- ✅ 100 CPU seconds/day
- ✅ 1GB disk space
- ❌ Custom domains
- ❌ SSH access

### Hacker ($5/month)
- ✅ 1 web app
- ✅ 1 always-on task
- ✅ 1000 CPU seconds/day
- ✅ 1GB disk space
- ✅ Custom domains
- ✅ SSH access

### Web Developer ($20/month)
- ✅ 2 web apps
- ✅ 2 always-on tasks
- ✅ 10,000 CPU seconds/day
- ✅ 5GB disk space
- ✅ Custom domains
- ✅ SSH access

---

## 🚀 Deployment Checklist

- [ ] ✅ PythonAnywhere account created
- [ ] ✅ All files uploaded to `/home/yourusername/news-dashboard/`
- [ ] ✅ Dependencies installed (`pip3.10 install --user -r requirements.txt`)
- [ ] ✅ Web app configured with correct WSGI file
- [ ] ✅ Data directory created (`/home/yourusername/news-dashboard/data/`)
- [ ] ✅ Web app reloaded
- [ ] ✅ App accessible at `https://yourusername.pythonanywhere.com`
- [ ] ✅ Scheduled scraping task created (optional)

---

## 📞 Support

### PythonAnywhere Support
- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [PythonAnywhere Forums](https://www.pythonanywhere.com/forums/)

### Common Issues
1. **Import errors**: Check all dependencies are installed
2. **File not found**: Verify file paths are correct
3. **Permission errors**: Check file permissions
4. **Scraping fails**: Check internet connectivity and website availability

---

## 🌟 Benefits of PythonAnywhere

- ✅ **Free hosting** for small projects
- ✅ **Easy deployment** with web interface
- ✅ **Automatic HTTPS** for all apps
- ✅ **Scheduled tasks** for automation
- ✅ **No server management** required
- ✅ **Python 3.10** support
- ✅ **Built-in console** for debugging

---

**🎉 Your News Dashboard is now live on PythonAnywhere! 🌐**

Access it at: `https://yourusername.pythonanywhere.com`
