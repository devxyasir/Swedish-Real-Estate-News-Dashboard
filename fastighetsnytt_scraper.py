"""
Fastighetsnytt.se News Scraper
Scrapes latest real estate news from fastighetsnytt.se
Parses Next.js __NEXT_DATA__ JSON structure
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
FASTIGHETSNYTT_DATA_FILE = data_dir / "fastighetsnytt_news_data.json"
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


class FastighetsnyttScraper:
    """Scraper for fastighetsnytt.se real estate news"""
    
    BASE_URL = "https://www.fastighetsnytt.se/"
    RATE_LIMIT_DELAY = 2  # seconds between requests
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    def __init__(self, data_file = None):
        """
        Initialize scraper
        
        Args:
            data_file: Path to JSON file for storing scraped data
        """
        self.data_file = Path(data_file) if data_file else FASTIGHETSNYTT_DATA_FILE
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
                    logger.info(f"Loaded {len(data.get('articles', []))} existing Fastighetsnytt articles")
                    return data
            except json.JSONDecodeError:
                logger.warning("Corrupted Fastighetsnytt JSON file, starting fresh")
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
        logger.info(f"Saved {self.articles_data['total_articles']} Fastighetsnytt articles to {self.data_file}")
    
    def _fetch_page(self) -> str:
        """Fetch the homepage"""
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Fetching Fastighetsnytt homepage (attempt {attempt + 1}/{self.MAX_RETRIES})")
                response = self.session.get(self.BASE_URL, timeout=30)
                response.raise_for_status()
                time.sleep(self.RATE_LIMIT_DELAY)
                return response.text
            except requests.RequestException as e:
                logger.error(f"Error fetching Fastighetsnytt homepage: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch Fastighetsnytt homepage after {self.MAX_RETRIES} attempts")
                    return None
    
    def _parse_page(self, html: str) -> List[Dict]:
        """
        Parse articles from Next.js __NEXT_DATA__ JSON structure
        
        Args:
            html: HTML content of the page
            
        Returns:
            List of article dictionaries
        """
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        try:
            # Find the __NEXT_DATA__ script tag
            next_data_script = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
            
            if not next_data_script:
                logger.warning("Could not find __NEXT_DATA__ script tag")
                return articles
            
            # Parse the JSON
            next_data = json.loads(next_data_script.string)
            
            # Navigate to the containers array
            containers = next_data.get('props', {}).get('containers', [])
            
            logger.info(f"Found {len(containers)} containers in __NEXT_DATA__")
            
            # Extract articles from containers
            for container in containers:
                # Only process articlelisting containers
                if container.get('type') == 'articlelisting':
                    article_data = container.get('article', {})
                    
                    # Extract article information
                    article_url = article_data.get('url')
                    headline = article_data.get('headlineHtml', '')
                    pub_time = article_data.get('publicationTime')
                    article_id = article_data.get('id')
                    
                    # Skip if missing essential data
                    if not article_url or not headline:
                        continue
                    
                    # Build full URL
                    full_url = f"{self.BASE_URL.rstrip('/')}{article_url}"
                    
                    # Parse publication date
                    if pub_time:
                        try:
                            # Parse ISO format date
                            pub_date = datetime.fromisoformat(pub_time.replace('Z', '+00:00'))
                            date_str = pub_date.strftime('%Y-%m-%d')
                        except Exception as e:
                            logger.warning(f"Could not parse date {pub_time}: {e}")
                            date_str = datetime.now().strftime('%Y-%m-%d')
                    else:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                    
                    # Extract category/section if available
                    section_path = article_data.get('sectionPath', [])
                    category = section_path[0].get('name', 'Okategoriserad') if section_path else 'Okategoriserad'
                    
                    # Create article object
                    article = {
                        'title': headline,
                        'url': full_url,
                        'date': date_str,
                        'category': category,
                        'article_id': article_id,
                        'publication_time': pub_time,
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    articles.append(article)
            
            logger.info(f"Parsed {len(articles)} articles from Fastighetsnytt")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse __NEXT_DATA__ JSON: {e}")
        except Exception as e:
            logger.error(f"Error parsing Fastighetsnytt page: {e}", exc_info=True)
        
        return articles
    
    def _is_duplicate(self, url: str) -> bool:
        """Check if article URL already exists"""
        return url in self.article_urls
    
    def scrape_latest(self):
        """
        Scrape latest articles from homepage
        
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
                logger.info(f"New Fastighetsnytt article: {article['title'][:80]}...")
        
        self.articles_data['last_scrape'] = datetime.now().isoformat()
        self._save_data()
        
        logger.info(f"Fastighetsnytt scraping complete: {new_articles_count} new articles")
        return new_articles_count


if __name__ == "__main__":
    scraper = FastighetsnyttScraper()
    print("Starting Fastighetsnytt latest articles scrape...")
    new_count = scraper.scrape_latest()
    print(f"Found {new_count} new articles.")
    print(f"Total articles in database: {len(scraper.articles_data['articles'])}")

