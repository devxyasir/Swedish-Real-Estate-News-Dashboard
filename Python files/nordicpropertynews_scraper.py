"""
Nordic Property News Scraper
Scrapes latest real estate news from nordicpropertynews.com
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from typing import List, Dict, Set
import logging
from pathlib import Path
from config import ensure_data_directory

# Get data directory path
data_dir = ensure_data_directory()
NORDICPROPERTYNEWS_DATA_FILE = data_dir / "nordicpropertynews_news_data.json"
SCRAPER_LOG_FILE = data_dir / "scraper.log"

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


class NordicPropertyNewsScraper:
    """Scraper for nordicpropertynews.com"""
    
    BASE_URL = "https://www.nordicpropertynews.com/?page=1"
    RATE_LIMIT_DELAY = 2  # seconds between requests
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    def __init__(self, data_file = None):
        """
        Initialize scraper
        
        Args:
            data_file: Path to JSON file for storing scraped data
        """
        self.data_file = Path(data_file) if data_file else NORDICPROPERTYNEWS_DATA_FILE
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.articles_data = self._load_existing_data()
        self.article_urls: Set[str] = set(article['url'] for article in self.articles_data.get('articles', []))
        
    def _load_existing_data(self) -> Dict:
        """Load existing article data from JSON file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data.get('articles', []))} existing Nordic Property News articles")
                    return data
            except json.JSONDecodeError:
                logger.warning("Corrupted Nordic Property News JSON file, starting fresh")
                return self._initialize_data_structure()
        return self._initialize_data_structure()
    
    def _initialize_data_structure(self) -> Dict:
        """Initialize the data structure for storing articles"""
        return {
            'last_scrape': None,
            'total_articles': 0,
            'articles': []
        }
    
    def _save_data(self):
        """Save article data to JSON file"""
        self.articles_data['total_articles'] = len(self.articles_data['articles'])
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.articles_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {self.articles_data['total_articles']} Nordic Property News articles to {self.data_file}")
    
    def _fetch_page(self) -> str:
        """Fetch page 1"""
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Fetching Nordic Property News page 1 (attempt {attempt + 1}/{self.MAX_RETRIES})")
                response = self.session.get(self.BASE_URL, timeout=30)
                response.raise_for_status()
                time.sleep(self.RATE_LIMIT_DELAY)
                return response.text
            except requests.RequestException as e:
                logger.error(f"Error fetching Nordic Property News page: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch Nordic Property News page after {self.MAX_RETRIES} attempts")
                    return None
    
    def _parse_page(self, html: str) -> List[Dict]:
        """
        Parse articles from the HTML
        Extracts all h2.article-header elements and their associated links
        
        Args:
            html: HTML content of the page
            
        Returns:
            List of article dictionaries
        """
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        try:
            # Find all h2 elements with class="article-header"
            article_headers = soup.find_all('h2', class_='article-header')
            
            logger.info(f"Found {len(article_headers)} article headers")
            
            # Use scraping date as the date for all articles
            scrape_date = datetime.now().strftime('%Y-%m-%d')
            
            for header in article_headers:
                title = header.get_text(strip=True)
                
                # Find the parent link element
                # The h2 is typically inside an <a> tag or the <a> is a sibling/nearby
                link_element = header.find_parent('a', class_='black-link')
                
                # If not found as parent, try to find sibling or nearby link
                if not link_element:
                    # Try finding the link in the parent's parent or nearby
                    parent = header.find_parent()
                    if parent:
                        link_element = parent.find('a', class_='black-link', href=True)
                
                if not link_element:
                    # Last resort: look for any nearby a tag with href containing the site
                    parent = header.find_parent()
                    if parent:
                        link_element = parent.find('a', href=True)
                
                if link_element and link_element.get('href'):
                    url = link_element.get('href')
                    
                    # Ensure absolute URL
                    if not url.startswith('http'):
                        url = f"https://www.nordicpropertynews.com{url}"
                    
                    # Create article object
                    article = {
                        'title': title,
                        'url': url,
                        'date': scrape_date,  # Use scraping date
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    articles.append(article)
                    logger.debug(f"Parsed article: {title[:60]}...")
                else:
                    logger.warning(f"Could not find link for article: {title[:60]}...")
            
            logger.info(f"Successfully parsed {len(articles)} articles from Nordic Property News")
            
        except Exception as e:
            logger.error(f"Error parsing Nordic Property News page: {e}", exc_info=True)
        
        return articles
    
    def _is_duplicate(self, url: str) -> bool:
        """Check if article URL already exists"""
        return url in self.article_urls
    
    def scrape_latest(self):
        """
        Scrape latest articles from page 1
        
        Returns:
            Number of new articles found
        """
        new_articles_count = 0
        
        html = self._fetch_page()
        if not html:
            return 0
        
        articles = self._parse_page(html)
        
        for article in articles:
            if not self._is_duplicate(article['url']):
                self.articles_data['articles'].append(article)
                self.article_urls.add(article['url'])
                new_articles_count += 1
                logger.info(f"New Nordic Property News article: {article['title'][:80]}...")
        
        self.articles_data['last_scrape'] = datetime.now().isoformat()
        self._save_data()
        
        logger.info(f"Nordic Property News scraping complete: {new_articles_count} new articles")
        return new_articles_count


if __name__ == "__main__":
    scraper = NordicPropertyNewsScraper()
    print("Starting Nordic Property News latest articles scrape...")
    new_count = scraper.scrape_latest()
    print(f"Found {new_count} new articles.")
    print(f"Total articles in database: {len(scraper.articles_data['articles'])}")

