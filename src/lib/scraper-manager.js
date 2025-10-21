import { FastighetsvarldenScraper } from './scrapers/fastighetsvarlden-scraper.js';
import { CisionScraper } from './scrapers/cision-scraper.js';
import { LokalguidenScraper } from './scrapers/lokalguiden-scraper.js';
import { DIScraper } from './scrapers/di-scraper.js';
import { FastighetsnyttScraper } from './scrapers/fastighetsnytt-scraper.js';
import { NordicPropertyNewsScraper } from './scrapers/nordicpropertynews-scraper.js';
import { saveArticles, getExistingUrls } from './database.js';
import { CONFIG } from './config.js';

export class ScraperManager {
  constructor() {
    this.scrapers = {
      fastighetsvarlden: new FastighetsvarldenScraper(),
      cision: new CisionScraper(),
      lokalguiden: new LokalguidenScraper(),
      di: new DIScraper(),
      fastighetsnytt: new FastighetsnyttScraper(),
      nordicpropertynews: new NordicPropertyNewsScraper()
    };
    
    this.isScraping = false;
    this.progress = {
      status: 'idle',
      currentSource: null,
      sourcesCompleted: [],
      totalSources: Object.keys(this.scrapers).length,
      currentSourceIndex: 0,
      message: '',
      articlesScraped: 0
    };
  }

  async scrapeAll(onProgress) {
    if (this.isScraping) {
      console.log('Scraping already in progress');
      return { success: false, message: 'Scraping already in progress' };
    }

    this.isScraping = true;
    this.progress.status = 'scraping';
    this.progress.sourcesCompleted = [];
    this.progress.currentSourceIndex = 0;
    this.progress.articlesScraped = 0;

    try {
      console.log('Starting scraping process...');
      
      const sourceNames = Object.keys(this.scrapers);
      let totalNewArticles = 0;

      for (let i = 0; i < sourceNames.length; i++) {
        const sourceName = sourceNames[i];
        const scraper = this.scrapers[sourceName];
        
        this.progress.currentSource = CONFIG.SOURCES[sourceName].name;
        this.progress.currentSourceIndex = i + 1;
        this.progress.message = `Checking ${CONFIG.SOURCES[sourceName].name} for new articles...`;
        
        if (onProgress) {
          onProgress({ ...this.progress });
        }

        try {
          // Get existing URLs to avoid duplicates
          const existingUrls = await getExistingUrls(sourceName);
          
          // Scrape articles
          const articles = await scraper.scrape();
          
          // Filter out duplicates
          const newArticles = articles.filter(article => !existingUrls.has(article.url));
          
          if (newArticles.length > 0) {
            // Save new articles
            const result = await saveArticles(newArticles, sourceName);
            if (result.success) {
              totalNewArticles += result.count;
              console.log(`Saved ${result.count} new articles from ${CONFIG.SOURCES[sourceName].name}`);
            }
          }
          
          this.progress.sourcesCompleted.push(CONFIG.SOURCES[sourceName].name);
          
        } catch (error) {
          console.error(`Error scraping ${sourceName}:`, error);
          this.progress.sourcesCompleted.push(`${CONFIG.SOURCES[sourceName].name} (Error)`);
        }
      }

      this.progress.status = 'completed';
      this.progress.articlesScraped = totalNewArticles;
      this.progress.message = `Check completed! Found ${totalNewArticles} new articles`;
      
      if (onProgress) {
        onProgress({ ...this.progress });
      }

      console.log(`Scraping completed. Found ${totalNewArticles} new articles total.`);
      return { success: true, articlesScraped: totalNewArticles };

    } catch (error) {
      console.error('Scraping error:', error);
      this.progress.status = 'error';
      this.progress.message = `Error: ${error.message}`;
      
      if (onProgress) {
        onProgress({ ...this.progress });
      }
      
      return { success: false, error: error.message };
    } finally {
      this.isScraping = false;
    }
  }

  async scrapeSource(sourceName) {
    if (!this.scrapers[sourceName]) {
      throw new Error(`Unknown source: ${sourceName}`);
    }

    const scraper = this.scrapers[sourceName];
    const existingUrls = await getExistingUrls(sourceName);
    const articles = await scraper.scrape();
    const newArticles = articles.filter(article => !existingUrls.has(article.url));
    
    if (newArticles.length > 0) {
      const result = await saveArticles(newArticles, sourceName);
      return { success: result.success, articlesScraped: result.count };
    }
    
    return { success: true, articlesScraped: 0 };
  }

  getProgress() {
    return { ...this.progress };
  }

  stopScraping() {
    this.isScraping = false;
    this.progress.status = 'stopped';
    this.progress.message = 'Scraping stopped by user';
    return { success: true };
  }
}

export const scraperManager = new ScraperManager();
