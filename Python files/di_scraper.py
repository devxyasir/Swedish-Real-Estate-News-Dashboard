"""
DI.se (Dagens Industri) News Scraper
Scrapes latest real estate news from di.se
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, date
from typing import List, Dict, Set
import logging
from pathlib import Path
from config import DI_DATA_FILE, SCRAPER_LOG_FILE, ensure_data_directory

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


class DIScraper:
    """Scraper for di.se real estate news"""
    
    # Use today's date for the lastday parameter
    BASE_URL = f"https://www.di.se/get-list-articles/?template=tagPage&id=di.tag.fastighet&lastday={date.today().strftime('%Y-%m-%d')}&page=1"
    RATE_LIMIT_DELAY = 2  # seconds between requests
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    def __init__(self, data_file = None):
        """
        Initialize scraper
        
        Args:
            data_file: Path to JSON file for storing scraped data
        """
        self.data_file = Path(data_file) if data_file else DI_DATA_FILE
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
            'source': 'di',
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
                logger.info(f"Fetching DI news (attempt {attempt + 1}/{self.MAX_RETRIES})")
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
        
        # Find all article elements
        article_elements = soup.find_all('article', class_='news-item')
        logger.info(f"Found {len(article_elements)} article elements on page")
        
        for article_elem in article_elements:
            try:
                # Find the title
                title_elem = article_elem.find('h2', class_='news-item__heading')
                if not title_elem:
                    logger.debug("No title found in article element, skipping")
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # Find the link
                link_elem = article_elem.find('a', href=True)
                if not link_elem:
                    logger.debug("No link found, skipping")
                    continue
                
                # Get URL
                url = link_elem.get('href', '')
                if not url:
                    continue
                
                # Make URL absolute if needed
                if url.startswith('/'):
                    url = f"https://www.di.se{url}"
                
                # Get date - try multiple methods
                article_date = None
                
                # Method 1: Try data-day attribute on article element
                data_day = article_elem.get('data-day')
                if data_day:
                    article_date = data_day
                
                # Method 2: Try <time> tag
                if not article_date:
                    time_elem = article_elem.find('time', class_='global-xs-bold')
                    if time_elem:
                        time_text = time_elem.get_text(strip=True)
                        # Parse Swedish date format: "16 september 2025"
                        try:
                            # Map Swedish months to numbers
                            month_map = {
                                'januari': '01', 'februari': '02', 'mars': '03', 'april': '04',
                                'maj': '05', 'juni': '06', 'juli': '07', 'augusti': '08',
                                'september': '09', 'oktober': '10', 'november': '11', 'december': '12'
                            }
                            
                            parts = time_text.split()
                            if len(parts) == 3:
                                day = parts[0].zfill(2)
                                month = month_map.get(parts[1].lower(), '01')
                                year = parts[2]
                                article_date = f"{year}-{month}-{day}"
                        except Exception as e:
                            logger.debug(f"Error parsing date from time tag: {e}")
                
                # If no date found, use today's date
                if not article_date:
                    article_date = datetime.now().strftime('%Y-%m-%d')
                
                # Get article ID
                article_id = article_elem.get('data-id')
                
                article_data = {
                    'title': title,
                    'url': url,
                    'date': article_date,
                    'article_id': article_id,
                    'scraped_at': datetime.now().isoformat(),
                    'source': 'di'
                }
                
                articles.append(article_data)
                logger.debug(f"Extracted: {title}")
                
            except Exception as e:
                logger.debug(f"Error extracting article: {e}")
                continue
        
        logger.info(f"Extracted {len(articles)} articles from DI")
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
        logger.info("Starting DI news scrape...")
        
        # Fetch page
        html = self._fetch_page()
        if not html:
            logger.error("Failed to fetch DI page")
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
        
        logger.info(f"DI scrape completed: {new_articles_count} new articles")
        logger.info(f"Total DI articles in database: {len(self.articles_data['articles'])}")
        
        return new_articles_count


def main():
    """Main function for testing"""
    scraper = DIScraper()
    
    print("=" * 60)
    print("DI (Dagens Industri) News Scraper")
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

