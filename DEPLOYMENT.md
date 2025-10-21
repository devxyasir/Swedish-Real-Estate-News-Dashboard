# 🚀 Netlify Deployment Guide

## Quick Deploy to Netlify

### Method 1: Netlify CLI (Recommended)
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy from current directory
netlify deploy --prod --dir=dist
```

### Method 2: Git Integration
1. Push code to GitHub/GitLab
2. Connect repository to Netlify
3. Set build command: `npm run build`
4. Set publish directory: `dist`
5. Deploy!

### Method 3: Drag & Drop
1. Run `npm run build`
2. Drag the `dist` folder to Netlify dashboard

## Build Configuration
- **Build Command**: `npm run build`
- **Publish Directory**: `dist`
- **Node Version**: 18

## Environment Variables (if needed)
- No environment variables required for basic deployment

## Features
- ✅ Real-time news scraping
- ✅ 6 news sources
- ✅ Swedish to English translation
- ✅ Local data storage (IndexedDB)
- ✅ Search and filtering
- ✅ Responsive design
