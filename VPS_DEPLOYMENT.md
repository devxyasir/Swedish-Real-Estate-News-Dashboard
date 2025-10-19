# 🚀 VPS Deployment Guide - News Dashboard

## 🌟 **Why Move to VPS?**
- ✅ **Full scraping**: No proxy restrictions
- ✅ **All 6 sources**: Complete functionality
- ✅ **Real-time updates**: Live scraping
- ✅ **Custom domain**: Professional URL
- ✅ **Better performance**: Faster servers

---

## 🎯 **Recommended VPS Options:**

### **1. 🚀 Railway (Best Choice)**
- **Free**: $5 credit monthly
- **Setup**: 5 minutes
- **Features**: Auto-deploy, custom domain, no restrictions
- **Best for**: Quick deployment

### **2. 🌊 Render**
- **Free**: 750 hours/month
- **Setup**: 10 minutes
- **Features**: Reliable, custom domain, no restrictions
- **Best for**: Stable hosting

### **3. 🔥 Heroku**
- **Free**: 550-1000 hours/month
- **Setup**: 15 minutes
- **Features**: Popular, custom domain, sleep mode
- **Best for**: Learning

---

## 🚀 **Railway Deployment (Recommended):**

### **Step 1: Prepare Your Code**
```bash
# Make sure all files are ready
ls -la
# Should see: app.py, wsgi.py, requirements.txt, web/, etc.
```

### **Step 2: Create GitHub Repository**
```bash
# Initialize git
git init
git add .
git commit -m "News Dashboard - Ready for VPS deployment"

# Create GitHub repo (go to github.com and create new repo)
# Then connect:
git remote add origin https://github.com/yourusername/news-dashboard.git
git push -u origin main
```

### **Step 3: Deploy to Railway**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects Python and deploys
6. Your app will be live at: `https://your-app-name.railway.app`

### **Step 4: Set Environment Variables**
In Railway dashboard:
- `HOST=0.0.0.0`
- `PORT=8080`
- `SERVER_MODE=true`

---

## 🌊 **Render Deployment:**

### **Step 1: Create GitHub Repository** (same as above)

### **Step 2: Deploy to Render**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click **"New Web Service"**
4. Connect your repository
5. Set **Build Command**: `pip install -r requirements.txt`
6. Set **Start Command**: `python app.py`
7. Your app will be live at: `https://your-app-name.onrender.com`

---

## 🔧 **VPS Configuration:**

### **Update app.py for VPS:**
```python
# The app.py is already configured for VPS deployment
# It will automatically detect the environment and use web mode
```

### **Environment Variables:**
```bash
HOST=0.0.0.0          # Bind to all interfaces
PORT=8080             # Server port
SERVER_MODE=true      # Enable web server mode
```

---

## 📱 **What You'll Get:**

### ✅ **Full Functionality**
- **6 News Sources**: All scrapers working
- **Auto-Translation**: Swedish → English
- **Real-time Scraping**: Live updates
- **Search & Filter**: Complete functionality
- **Mobile Responsive**: Works on all devices

### ✅ **Professional Features**
- **Custom Domain**: `https://yourdomain.com`
- **HTTPS**: Automatic SSL certificate
- **Fast Loading**: Optimized servers
- **Global CDN**: Fast worldwide access

---

## 🎯 **Deployment Checklist:**

- [ ] ✅ Code ready (all files uploaded)
- [ ] ✅ GitHub repository created
- [ ] ✅ VPS account created (Railway/Render)
- [ ] ✅ App deployed successfully
- [ ] ✅ Environment variables set
- [ ] ✅ App accessible via URL
- [ ] ✅ Scraping working (test all 6 sources)
- [ ] ✅ Custom domain configured (optional)

---

## 🚀 **Benefits of VPS:**

### **vs PythonAnywhere:**
- ✅ **No restrictions**: Full internet access
- ✅ **Better performance**: Faster servers
- ✅ **Custom domain**: Professional URL
- ✅ **More resources**: Better limits

### **vs Local Development:**
- ✅ **24/7 availability**: Always online
- ✅ **Global access**: Anyone can use it
- ✅ **No maintenance**: Managed hosting
- ✅ **Automatic updates**: Git-based deployment

---

## 📞 **Support:**

### **Railway Issues:**
- [Railway Docs](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)

### **Render Issues:**
- [Render Docs](https://render.com/docs)
- [Render Support](https://render.com/support)

---

**Your News Dashboard will have full functionality on VPS! 🌐🚀**
