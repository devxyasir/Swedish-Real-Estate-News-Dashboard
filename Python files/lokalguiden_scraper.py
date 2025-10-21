"""
Lokalguiden.se News Scraper
Scrapes latest news articles from Lokalguiden magazine
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from typing import List, Dict, Set
import logging
from pathlib import Path
from config import LOKALGUIDEN_DATA_FILE, SCRAPER_LOG_FILE, ensure_data_directory

# Ensure data directory exists
ensure_data_directory()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(SCRAPER_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LokalguidenScraper:
    """Scraper for lokalguiden.se magazine"""
    
    BASE_URL = "https://www.lokalguiden.se/magasinet/?page=1"
    RATE_LIMIT_DELAY = 2  # seconds between requests
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    def __init__(self, data_file = None):
        """
        Initialize scraper
        
        Args:
            data_file: Path to JSON file for storing scraped data
        """
        self.data_file = Path(data_file) if data_file else LOKALGUIDEN_DATA_FILE
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.articles_data = self._load_existing_data()
        self.article_urls: Set[str] = set(article['url'] for article in self.articles_data.get('articles', []))
        
    def _load_existing_data(self) -> Dict:
        """Load existing data from JSON file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data.get('articles', []))} existing articles")
                    return data
            except json.JSONDecodeError:
                logger.warning("Corrupted JSON file, starting fresh")
                return self._initialize_data_structure()
        return self._initialize_data_structure()
    
    def _initialize_data_structure(self) -> Dict:
        """Initialize the data structure"""
        return {
            'last_scrape': None,
            'total_articles': 0,
            'source': 'lokalguiden',
            'articles': []
        }
    
    def _save_data(self):
        """Save data to JSON file"""
        self.articles_data['total_articles'] = len(self.articles_data['articles'])
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.articles_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {self.articles_data['total_articles']} articles to {self.data_file}")
    
    def _fetch_page(self) -> str:
        """
        Fetch the page with retry logic
        
        Returns:
            HTML content as string
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Fetching Lokalguiden news (attempt {attempt + 1}/{self.MAX_RETRIES})")
                response = self.session.get(self.BASE_URL, timeout=30)
                response.raise_for_status()
                
                # Rate limiting
                time.sleep(self.RATE_LIMIT_DELAY)
                return response.text
                
            except requests.RequestException as e:
                logger.error(f"Error fetching page: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch page after {self.MAX_RETRIES} attempts")
                    return None
    
    def _parse_page(self, html: str) -> List[Dict]:
        """
        Parse the page and extract articles
        
        Args:
            html: HTML content
            
        Returns:
            List of article dictionaries
        """
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Find all article divs with class "article"
        article_divs = soup.find_all('div', class_='article', attrs={'data-id': True})
        logger.info(f"Found {len(article_divs)} article divs on page")
        
        for article_div in article_divs:
            try:
                # Skip if this is a quote article or banner
                if 'quote-article' in article_div.get('class', []):
                    continue
                    
                # Find the title
                title_elem = article_div.find('p', class_='title')
                if not title_elem:
                    logger.debug("No title found in article div, skipping")
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # Find the link (look for link with /magasinet/artikel/ in href)
                link_elem = article_div.find('a', href=lambda x: x and '/magasinet/artikel/' in x)
                if not link_elem:
                    logger.debug("No article link found, skipping")
                    continue
                
                # Get URL
                url = link_elem.get('href', '')
                if not url:
                    continue
                
                # Make URL absolute if needed
                if url.startswith('/'):
                    url = f"https://www.lokalguiden.se{url}"
                
                # Find category (optional)
                category_elem = article_div.find('span', class_='category')
                category = category_elem.get_text(strip=True) if category_elem else None
                
                # Get article ID
                article_id = article_div.get('data-id')
                
                # Use scrape date as published date (as per user request)
                # Format: YYYY-MM-DD
                scrape_date = datetime.now().strftime('%Y-%m-%d')
                
                article_data = {
                    'title': title,
                    'url': url,
                    'date': scrape_date,  # Use scrape date since no published date is visible
                    'category': category,
                    'article_id': article_id,
                    'scraped_at': datetime.now().isoformat(),
                    'source': 'lokalguiden'
                }
                
                articles.append(article_data)
                logger.debug(f"Extracted: {title}")
                
            except Exception as e:
                logger.debug(f"Error extracting article: {e}")
                continue
        
        logger.info(f"Extracted {len(articles)} articles from Lokalguiden")
        return articles
    
    def _is_duplicate(self, url: str) -> bool:
        """Check if article URL already exists"""
        return url in self.article_urls
    
    def scrape_latest(self) -> int:
        """
        Scrape latest articles from page 1
        
        Returns:
            Number of new articles found
        """
        logger.info("Starting Lokalguiden news scrape...")
        
        # Fetch page
        html = self._fetch_page()
        if not html:
            logger.error("Failed to fetch Lokalguiden page")
            return 0
        
        # Parse articles
        articles = self._parse_page(html)
        new_articles_count = 0
        
        for article in articles:
            if not self._is_duplicate(article['url']):
                # Note: Translation will be handled in main app.py
                self.articles_data['articles'].append(article)
                self.article_urls.add(article['url'])
                new_articles_count += 1
                logger.info(f"New article: {article['title']}")
        
        # Update last scrape time
        self.articles_data['last_scrape'] = datetime.now().isoformat()
        self._save_data()
        
        logger.info(f"Lokalguiden scrape completed: {new_articles_count} new articles")
        logger.info(f"Total Lokalguiden articles in database: {len(self.articles_data['articles'])}")
        
        return new_articles_count


def main():
    """Main function for testing"""
    scraper = LokalguidenScraper()
    
    print("=" * 60)
    print("Lokalguiden News Scraper")
    print("=" * 60)
    print()
    
    new_count = scraper.scrape_latest()
    
    print()
    print("=" * 60)
    print(f"Found {new_count} new articles")
    print(f"Total articles: {len(scraper.articles_data['articles'])}")
    print(f"Data saved to: {scraper.data_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()

