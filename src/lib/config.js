// Configuration for the News Dashboard
export const CONFIG = {
  // News sources configuration
  SOURCES: {
    fastighetsvarlden: {
      name: 'Fastighetsvarlden',
      url: 'https://www.fastighetsvarlden.se/',
      color: 'blue',
      translate: true
    },
    cision: {
      name: 'Cision',
      url: 'https://news.cision.com/?i=04004003',
      color: 'green',
      translate: false
    },
    lokalguiden: {
      name: 'Lokalguiden',
      url: 'https://www.lokalguiden.se/magasinet/?page=1',
      color: 'purple',
      translate: true
    },
    di: {
      name: 'DI',
      url: 'https://www.di.se/get-list-articles/?template=tagPage&id=di.tag.fastighet&lastday=2025-09-17&page=1',
      color: 'orange',
      translate: true
    },
    fastighetsnytt: {
      name: 'Fastighetsnytt',
      url: 'https://www.fastighetsnytt.se/',
      color: 'red',
      translate: true
    },
    nordicpropertynews: {
      name: 'Nordic Property News',
      url: 'https://www.nordicpropertynews.com/?page=1',
      color: 'yellow',
      translate: false
    }
  },
  
  // Scraping settings
  SCRAPING: {
    rateLimitDelay: 2000, // 2 seconds between requests
    maxRetries: 3,
    retryDelay: 5000, // 5 seconds
    timeout: 30000 // 30 seconds
  },
  
  // UI settings
  UI: {
    articlesPerPage: 20,
    maxArticles: 1000
  },
  
  // Translation settings
  TRANSLATION: {
    targetLanguage: 'en',
    sourceLanguage: 'auto'
  }
};

export const getSourceConfig = (source) => {
  return CONFIG.SOURCES[source] || null;
};

export const getAllSources = () => {
  return Object.keys(CONFIG.SOURCES);
};

export const getSourceColor = (source) => {
  const config = getSourceConfig(source);
  return config ? config.color : 'gray';
};

export const needsTranslation = (source) => {
  const config = getSourceConfig(source);
  return config ? config.translate : false;
};
