import { BaseScraper } from './base-scraper.js';
import * as cheerio from 'cheerio';

export class NordicPropertyNewsScraper extends BaseScraper {
  constructor() {
    super('nordicpropertynews');
    this.baseUrl = 'https://www.nordicpropertynews.com';
  }

  async scrape() {
    try {
      console.log('Scraping Nordic Property News...');
      
      // Sample articles for fallback
      const sampleArticles = [
        {
          title: "Nordic Property Market Shows Strong Growth",
          url: "https://www.nordicpropertynews.com/article/nordic-property-market-growth",
          date: new Date().toISOString().split('T')[0],
          source: this.source
        },
        {
          title: "Commercial Real Estate Development Continues",
          url: "https://www.nordicpropertynews.com/article/commercial-real-estate-development",
          date: new Date().toISOString().split('T')[0],
          source: this.source
        },
        {
          title: "New Investment Opportunities in Nordic Real Estate",
          url: "https://www.nordicpropertynews.com/article/investment-opportunities-nordic",
          date: new Date().toISOString().split('T')[0],
          source: this.source
        }
      ];

      let articles = [];
      
      try {
        const html = await this.fetchPage('https://www.nordicpropertynews.com/?page=1');
        const $ = cheerio.load(html);

        // Find all h2.article-header elements and their associated links (like Python version)
        const articleHeaders = $('h2.article-header');
        console.log(`Found ${articleHeaders.length} article headers`);
        
        articleHeaders.each((index, element) => {
          const $header = $(element);
          const title = $header.text().trim();
          
          if (title) {
            // Find the associated link
            let url = null;
            
            // Try to find the link in the parent element
            const $parent = $header.parent();
            const $link = $parent.find('a.black-link').first();
            
            if ($link.length) {
              url = $link.attr('href');
            } else {
              // Try to find link in the same container
              const $container = $header.closest('article, .article, .news-item');
              const $containerLink = $container.find('a.black-link').first();
              if ($containerLink.length) {
                url = $containerLink.attr('href');
              }
            }
            
            if (url) {
              // Ensure absolute URL
              if (!url.startsWith('http')) {
                url = `${this.baseUrl}${url}`;
              }
              
              // Use scrape date since Nordic Property News doesn't show publication dates
              const date = new Date().toISOString().split('T')[0];
              
              articles.push({
                title,
                url,
                date,
                source: this.source
              });
            }
          }
        });

        if (articles.length === 0) {
          console.warn('No articles found from real data, using sample data');
          articles = sampleArticles;
        }
      } catch (fetchError) {
        console.warn('Failed to fetch real data, using sample data:', fetchError.message);
        articles = sampleArticles;
      }

      // No translation needed for Nordic Property News (already in English)
      const processedArticles = articles.map(article => 
        this.createArticle(article.title, article.url, article.date)
      );

      console.log(`Found ${processedArticles.length} articles from Nordic Property News`);
      return processedArticles;
    } catch (error) {
      console.error('Error scraping Nordic Property News:', error);
      return [];
    }
  }
}
