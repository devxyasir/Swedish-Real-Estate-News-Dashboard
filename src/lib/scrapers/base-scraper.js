import axios from 'axios';
import * as cheerio from 'cheerio';
import { CONFIG } from '../config.js';
import { translateTitle } from '../translation.js';

export class BaseScraper {
  constructor(source) {
    this.source = source;
    this.config = CONFIG.SOURCES[source];
    this.rateLimitDelay = CONFIG.SCRAPING.rateLimitDelay;
    this.maxRetries = CONFIG.SCRAPING.maxRetries;
    this.retryDelay = CONFIG.SCRAPING.retryDelay;
    this.timeout = CONFIG.SCRAPING.timeout;
    this.lastRequestTime = 0;
  }

  async delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async rateLimit() {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    
    if (timeSinceLastRequest < this.rateLimitDelay) {
      await this.delay(this.rateLimitDelay - timeSinceLastRequest);
    }
    
    this.lastRequestTime = Date.now();
  }

  async fetchPage(url, retries = 0) {
    await this.rateLimit();
    
    try {
      // Try direct request first
      const response = await axios.get(url, {
        timeout: this.timeout,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
        }
      });
      
      return response.data;
    } catch (error) {
      // If CORS error, try with CORS proxy
      if (error.message.includes('CORS') || error.message.includes('cross-origin') || error.code === 'ERR_NETWORK') {
        console.warn('CORS error detected, trying CORS proxy...');
        try {
          const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`;
          const proxyResponse = await axios.get(proxyUrl, {
            timeout: this.timeout,
            headers: {
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
          });
          return proxyResponse.data;
        } catch (proxyError) {
          console.warn('CORS proxy also failed:', proxyError.message);
          throw new Error(`CORS blocked: ${error.message}`);
        }
      }
      
      if (retries < this.maxRetries) {
        console.warn(`Request failed, retrying in ${this.retryDelay}ms... (${retries + 1}/${this.maxRetries})`);
        await this.delay(this.retryDelay);
        return this.fetchPage(url, retries + 1);
      }
      throw error;
    }
  }

  async translateIfNeeded(title) {
    if (this.config.translate) {
      return await translateTitle(title, this.source);
    }
    return title;
  }

  formatDate(dateString) {
    if (!dateString) return new Date().toISOString().split('T')[0];
    
    try {
      const date = new Date(dateString);
      return date.toISOString().split('T')[0];
    } catch (error) {
      console.warn('Date parsing failed, using current date:', error);
      return new Date().toISOString().split('T')[0];
    }
  }

  createArticle(title, url, date, originalTitle = null) {
    return {
      title,
      url,
      date: this.formatDate(date),
      source: this.source,
      originalTitle,
      scrapedAt: new Date().toISOString()
    };
  }

  async scrape() {
    throw new Error('scrape() method must be implemented by subclass');
  }
}
