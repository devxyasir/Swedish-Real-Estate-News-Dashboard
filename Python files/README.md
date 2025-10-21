# Real Estate News Hub - Vite.js Version

A modern web application that scrapes real estate news from 6 sources, translates Swedish content to English, and provides a beautiful dashboard interface.

## Features

- 🔄 **Auto-scraping**: Automatically checks for new articles on startup
- 🌐 **6 News Sources**: Fastighetsvarlden, Cision, Lokalguiden, DI, Fastighetsnytt, Nordic Property News
- 🔤 **Auto-translation**: Swedish titles translated to English
- 💾 **Local Storage**: Data stored in browser using IndexedDB
- 🎨 **Modern UI**: Built with React, Tailwind CSS, and Lucide icons
- 📱 **Responsive**: Works on desktop and mobile
- 🔍 **Search & Filter**: Find articles by source or search query
- 📄 **Pagination**: Navigate through articles easily

## Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   - Navigate to `http://localhost:3000`
   - The app will automatically start scraping on first load

### Production Build

```bash
npm run build
npm run preview
```

## News Sources

| Source | Language | Translation | Color |
|--------|----------|-------------|-------|
| Fastighetsvarlden | Swedish | ✅ | Blue |
| Cision | English | ❌ | Green |
| Lokalguiden | Swedish | ✅ | Purple |
| DI | Swedish | ✅ | Orange |
| Fastighetsnytt | Swedish | ✅ | Red |
| Nordic Property News | English | ❌ | Yellow |

## How It Works

### 1. **Automatic Scraping**
- Runs on first app load
- Checks all 6 sources for new articles
- Skips duplicate articles
- Shows real-time progress

### 2. **Data Storage**
- Uses IndexedDB for local storage
- Articles stored with metadata (source, date, translation)
- Persistent across browser sessions

### 3. **Translation**
- Swedish titles automatically translated to English
- Uses Google Translate API (free tier)
- Caches translations for performance

### 4. **User Interface**
- Clean, modern design with Tailwind CSS
- Dark/light mode support
- Responsive layout
- Real-time search and filtering

## Project Structure

```
src/
├── components/          # React components
│   ├── Header.jsx
│   ├── Sidebar.jsx
│   ├── ArticleList.jsx
│   └── ScrapingProgress.jsx
├── lib/                # Core functionality
│   ├── config.js       # Configuration
│   ├── database.js     # IndexedDB operations
│   ├── translation.js  # Translation service
│   ├── scraper-manager.js # Main scraper orchestrator
│   └── scrapers/       # Individual scrapers
│       ├── base-scraper.js
│       ├── fastighetsvarlden-scraper.js
│       ├── cision-scraper.js
│       ├── lokalguiden-scraper.js
│       ├── di-scraper.js
│       ├── fastighetsnytt-scraper.js
│       └── nordicpropertynews-scraper.js
├── App.jsx            # Main app component
├── main.jsx          # App entry point
└── index.css         # Global styles
```

## Configuration

Edit `src/lib/config.js` to modify:
- Scraping settings (rate limits, timeouts)
- Source URLs and settings
- UI preferences
- Translation settings

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Adding New Sources

1. Create a new scraper in `src/lib/scrapers/`
2. Extend `BaseScraper` class
3. Add source to `CONFIG.SOURCES` in `config.js`
4. Register scraper in `scraper-manager.js`

## Troubleshooting

### Common Issues

1. **CORS Errors**: Some news sites may block direct browser requests
   - Solution: Use a CORS proxy or server-side scraping

2. **Translation Failures**: Google Translate API may be rate-limited
   - Solution: Implement caching and retry logic

3. **Storage Issues**: IndexedDB may have size limits
   - Solution: Implement data cleanup and pagination

### Debug Mode

Enable console logging by setting:
```javascript
localStorage.setItem('debug', 'true');
```

## License

MIT License - Feel free to use and modify as needed.

## Support

For issues or questions, please check the browser console for error messages and ensure all dependencies are properly installed.
