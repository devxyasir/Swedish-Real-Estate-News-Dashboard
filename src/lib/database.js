import Dexie from 'dexie';

class NewsDatabase extends Dexie {
  constructor() {
    super('NewsDatabase');
    
    this.version(1).stores({
      articles: '++id, title, url, date, source, scrapedAt, originalTitle',
      scrapes: '++id, source, timestamp, articlesCount, status'
    });
  }
}

const db = new NewsDatabase();

export const saveArticles = async (articles, source) => {
  try {
    const timestamp = new Date().toISOString();
    
    // Save articles
    await db.articles.bulkPut(articles.map(article => ({
      ...article,
      source,
      scrapedAt: timestamp
    })));
    
    // Save scrape record
    await db.scrapes.add({
      source,
      timestamp,
      articlesCount: articles.length,
      status: 'completed'
    });
    
    return { success: true, count: articles.length };
  } catch (error) {
    console.error('Error saving articles:', error);
    return { success: false, error: error.message };
  }
};

export const getArticles = async (source = 'all', page = 1, limit = 20, searchQuery = '') => {
  try {
    let query = db.articles.orderBy('scrapedAt').reverse();
    
    if (source !== 'all') {
      query = query.filter(article => article.source === source);
    }
    
    if (searchQuery) {
      query = query.filter(article => 
        article.title.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    const total = await query.count();
    const articles = await query.offset((page - 1) * limit).limit(limit).toArray();
    
    return {
      success: true,
      articles,
      total,
      page,
      totalPages: Math.ceil(total / limit)
    };
  } catch (error) {
    console.error('Error getting articles:', error);
    return { success: false, error: error.message };
  }
};

export const getExistingUrls = async (source) => {
  try {
    const articles = await db.articles
      .where('source')
      .equals(source)
      .toArray();
    
    return new Set(articles.map(article => article.url));
  } catch (error) {
    console.error('Error getting existing URLs:', error);
    return new Set();
  }
};

export const getLastScrapeTime = async (source) => {
  try {
    const lastScrape = await db.scrapes
      .where('source')
      .equals(source)
      .orderBy('timestamp')
      .last();
    
    return lastScrape ? lastScrape.timestamp : null;
  } catch (error) {
    console.error('Error getting last scrape time:', error);
    return null;
  }
};

export const clearData = async () => {
  try {
    await db.articles.clear();
    await db.scrapes.clear();
    return { success: true };
  } catch (error) {
    console.error('Error clearing data:', error);
    return { success: false, error: error.message };
  }
};

export default db;
