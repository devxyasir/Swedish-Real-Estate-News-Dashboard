"""
Fastighetsvarlden.se News Scraper
Scrapes all news articles from the archive with rate limiting, pagination, and duplication handling
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from typing import List, Dict, Set
import logging
from pathlib import Path
import re
from config import FASTIGHETSVARLDEN_DATA_FILE, SCRAPER_LOG_FILE, ensure_data_directory

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


class FastighetsVarldenScraper:
    """Scraper for fastighetsvarlden.se archive"""
    
    BASE_URL = "https://www.fastighetsvarlden.se/arkivet"
    RATE_LIMIT_DELAY = 2  # seconds between requests
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    def __init__(self, data_file = None):
        """
        Initialize scraper
        
        Args:
            data_file: Path to JSON file for storing scraped data
        """
        self.data_file = Path(data_file) if data_file else FASTIGHETSVARLDEN_DATA_FILE
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
            'last_full_scrape': None,
            'last_incremental_scrape': None,
            'last_page_scraped': 0,
            'total_pages': 0,
            'total_articles': 0,
            'articles': []
        }
    
    def _save_data(self):
        """Save data to JSON file"""
        self.articles_data['total_articles'] = len(self.articles_data['articles'])
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.articles_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {self.articles_data['total_articles']} articles to {self.data_file}")
    
    def _fetch_page(self, page_num: int) -> str:
        """
        Fetch a page with retry logic
        
        Args:
            page_num: Page number to fetch (1 for first page)
            
        Returns:
            HTML content as string
        """
        if page_num == 1:
            url = self.BASE_URL
        else:
            url = f"{self.BASE_URL}/page/{page_num}/"
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Fetching page {page_num} (attempt {attempt + 1}/{self.MAX_RETRIES})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Rate limiting
                time.sleep(self.RATE_LIMIT_DELAY)
                return response.text
                
            except requests.RequestException as e:
                logger.error(f"Error fetching page {page_num}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch page {page_num} after {self.MAX_RETRIES} attempts")
                    return None
    
    def _parse_page(self, html: str) -> List[Dict]:
        """
        Parse a page and extract articles
        
        Args:
            html: HTML content
            
        Returns:
            List of article dictionaries
        """
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Primary method: Extract from date sections (most reliable for this site)
        articles = self._extract_from_date_sections(soup)
        
        # Fallback method if primary doesn't find articles
        if not articles:
            logger.warning("Date section extraction failed, trying alternative methods")
            articles = self._extract_from_links(soup)
        
        return articles
    
    def _extract_article_from_element(self, elem) -> Dict:
        """Extract article data from an element"""
        try:
            # Find title and link
            title_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=lambda x: x and any(
                keyword in str(x).lower() for keyword in ['title', 'headline', 'entry-title']
            ))
            
            if not title_elem:
                title_elem = elem.find('a')
            
            if not title_elem:
                return None
            
            # Get title and URL
            if title_elem.name == 'a':
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href')
            else:
                link = title_elem.find('a')
                if link:
                    title = link.get_text(strip=True)
                    url = link.get('href')
                else:
                    title = title_elem.get_text(strip=True)
                    url = None
            
            if not url or not title:
                return None
            
            # Make URL absolute
            if url.startswith('/'):
                url = f"https://www.fastighetsvarlden.se{url}"
            
            # Find date
            date_elem = elem.find(['time', 'span', 'div'], class_=lambda x: x and any(
                keyword in str(x).lower() for keyword in ['date', 'time', 'published']
            ))
            
            date = None
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                date = self._parse_date(date_text)
            
            # If no date in element, try to find datetime attribute
            if not date and date_elem and date_elem.has_attr('datetime'):
                date = date_elem['datetime']
            
            return {
                'title': title,
                'url': url,
                'date': date,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.debug(f"Error extracting article from element: {e}")
            return None
    
    def _extract_from_date_sections(self, soup) -> List[Dict]:
        """Extract articles organized by date sections"""
        articles = []
        
        # Find main content area first
        main_content = soup.find(['main', 'div'], id=lambda x: x and 'content' in str(x).lower())
        if not main_content:
            main_content = soup.find(['main', 'div'], class_=lambda x: x and 'content' in str(x).lower())
        if not main_content:
            main_content = soup
        
        # Find all elements that could be date headers or articles
        all_elements = main_content.find_all(['h2', 'h3', 'h4', 'p', 'div', 'li', 'ul'])
        
        current_date = None
        
        for elem in all_elements:
            # Get text content
            elem_text = elem.get_text(strip=True)
            
            # Check if this element is a date header (format: YYYY-MM-DD)
            date_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', elem_text)
            if date_match:
                current_date = elem_text
                logger.debug(f"Found date header: {current_date}")
                continue
            
            # If we have a current date, look for article links in this element
            if current_date:
                # Find all links within this element
                links = elem.find_all('a', href=True)
                
                for link in links:
                    title = link.get_text(strip=True)
                    url = link.get('href')
                    
                    if not url or not title:
                        continue
                    
                    # Make URL absolute
                    if url.startswith('/'):
                        url = f"https://www.fastighetsvarlden.se{url}"
                    
                    # Filter to only include article URLs (notiser, nyheter, analys-fakta, etc.)
                    # Exclude pagination and navigation links
                    if (url.startswith('https://www.fastighetsvarlden.se/') and
                        any(section in url for section in ['/notiser/', '/nyheter/', '/analys-fakta/', '/portrattet/']) and
                        '/page/' not in url and
                        '/arkivet/' not in url and
                        len(title) > 5):  # Ensure title is substantial
                        
                        articles.append({
                            'title': title,
                            'url': url,
                            'date': current_date,
                            'scraped_at': datetime.now().isoformat()
                        })
                        logger.debug(f"  - Added: {title} ({current_date})")
        
        logger.info(f"Extracted {len(articles)} articles with dates")
        return articles
    
    def _extract_from_links(self, soup) -> List[Dict]:
        """Fallback method: extract from all content links"""
        articles = []
        
        # Find main content area
        main_content = soup.find(['main', 'article', 'div'], class_=lambda x: x and any(
            keyword in str(x).lower() for keyword in ['content', 'main', 'posts']
        ))
        
        if not main_content:
            main_content = soup
        
        # Find all links in content area
        links = main_content.find_all('a', href=True)
        
        for link in links:
            url = link.get('href')
            title = link.get_text(strip=True)
            
            # Filter for article URLs
            if url and title and len(title) > 10:
                if url.startswith('/'):
                    url = f"https://www.fastighetsvarlden.se{url}"
                
                # Filter out navigation, pagination, and non-article links
                if (('/notiser/' in url or '/analys-fakta/' in url) and 
                    '/page/' not in url and
                    '/arkivet/' not in url or url == "https://www.fastighetsvarlden.se/arkivet"):
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': None,  # Will try to get from article page later
                        'scraped_at': datetime.now().isoformat()
                    })
        
        return articles
    
    def _parse_date(self, date_text: str) -> str:
        """Parse various date formats"""
        # Try different date patterns
        patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # 2025-10-17
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # 17/10/2025
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # 17.10.2025
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_text)
            if match:
                return match.group(0)
        
        return date_text
    
    def _get_max_page_number(self, html: str) -> int:
        """Get the maximum page number from pagination"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for pagination elements
        pagination = soup.find(['div', 'nav', 'ul'], class_=lambda x: x and any(
            keyword in str(x).lower() for keyword in ['pagination', 'paging', 'page-numbers']
        ))
        
        if not pagination:
            # Try to find any links to /page/
            all_links = soup.find_all('a', href=re.compile(r'/page/\d+/'))
            if all_links:
                page_numbers = []
                for link in all_links:
                    match = re.search(r'/page/(\d+)/', link.get('href'))
                    if match:
                        page_numbers.append(int(match.group(1)))
                return max(page_numbers) if page_numbers else 1
        else:
            # Find all page links in pagination
            page_links = pagination.find_all('a', href=re.compile(r'/page/\d+/'))
            page_numbers = []
            
            for link in page_links:
                match = re.search(r'/page/(\d+)/', link.get('href'))
                if match:
                    page_numbers.append(int(match.group(1)))
            
            # Also check for text content that might contain page numbers
            page_texts = pagination.find_all(text=re.compile(r'\d+'))
            for text in page_texts:
                try:
                    num = int(text.strip())
                    if num > 0:
                        page_numbers.append(num)
                except ValueError:
                    continue
            
            if page_numbers:
                return max(page_numbers)
        
        return 1
    
    def _is_duplicate(self, url: str) -> bool:
        """Check if article URL already exists"""
        return url in self.article_urls
    
    def scrape_all_pages(self, start_page: int = 1, end_page: int = None):
        """
        Scrape all pages from the archive
        
        Args:
            start_page: Page to start from (default: 1)
            end_page: Page to end at (default: None, will scrape until last page)
        """
        logger.info("Starting full archive scrape...")
        
        # Get first page to determine total pages
        first_page_html = self._fetch_page(start_page)
        if not first_page_html:
            logger.error("Failed to fetch first page")
            return
        
        # Determine max page if not specified
        if end_page is None:
            max_page = self._get_max_page_number(first_page_html)
            logger.info(f"Detected {max_page} total pages")
            end_page = max_page
        
        # Process first page
        logger.info(f"Processing page {start_page}")
        articles = self._parse_page(first_page_html)
        new_articles_count = 0
        
        for article in articles:
            if not self._is_duplicate(article['url']):
                self.articles_data['articles'].append(article)
                self.article_urls.add(article['url'])
                new_articles_count += 1
        
        logger.info(f"Page {start_page}: Found {len(articles)} articles, {new_articles_count} new")
        
        # Save after first page
        self._save_data()
        
        # Process remaining pages
        for page_num in range(start_page + 1, end_page + 1):
            html = self._fetch_page(page_num)
            if not html:
                logger.warning(f"Skipping page {page_num} due to fetch error")
                continue
            
            logger.info(f"Processing page {page_num}/{end_page}")
            articles = self._parse_page(html)
            new_articles_count = 0
            
            for article in articles:
                if not self._is_duplicate(article['url']):
                    self.articles_data['articles'].append(article)
                    self.article_urls.add(article['url'])
                    new_articles_count += 1
            
            logger.info(f"Page {page_num}: Found {len(articles)} articles, {new_articles_count} new")
            
            # Save every 10 pages
            if page_num % 10 == 0:
                self._save_data()
                logger.info(f"Progress saved. Total articles: {len(self.articles_data['articles'])}")
        
        # Final save
        self.articles_data['last_full_scrape'] = datetime.now().isoformat()
        self._save_data()
        logger.info(f"Full scrape completed! Total articles: {len(self.articles_data['articles'])}")
    
    def scrape_latest(self, max_pages: int = 5):
        """
        Scrape only the latest pages for daily updates
        
        Args:
            max_pages: Maximum number of pages to check (default: 5)
        """
        logger.info("Starting incremental scrape for latest articles...")
        
        new_articles_count = 0
        pages_checked = 0
        pages_with_new_content = 0
        
        for page_num in range(1, max_pages + 1):
            html = self._fetch_page(page_num)
            if not html:
                continue
            
            pages_checked += 1
            logger.info(f"Checking page {page_num} for new articles...")
            articles = self._parse_page(html)
            
            page_new_count = 0
            for article in articles:
                if not self._is_duplicate(article['url']):
                    self.articles_data['articles'].append(article)
                    self.article_urls.add(article['url'])
                    new_articles_count += 1
                    page_new_count += 1
            
            if page_new_count > 0:
                pages_with_new_content += 1
                logger.info(f"Page {page_num}: Found {page_new_count} new articles")
            else:
                logger.info(f"Page {page_num}: No new articles found")
                # If no new articles on this page, likely no new articles on next pages either
                if page_num > 1:
                    logger.info("No new articles found, stopping incremental scrape")
                    break
        
        self.articles_data['last_incremental_scrape'] = datetime.now().isoformat()
        self._save_data()
        
        logger.info(f"Incremental scrape completed!")
        logger.info(f"Pages checked: {pages_checked}")
        logger.info(f"New articles found: {new_articles_count}")
        logger.info(f"Total articles in database: {len(self.articles_data['articles'])}")


def main():
    """Main function for full scrape"""
    scraper = FastighetsVarldenScraper()
    
    print("=" * 60)
    print("Fastighetsvarlden.se News Scraper")
    print("=" * 60)
    print()
    print("This will scrape ALL articles from the archive.")
    print("Depending on the number of pages, this may take several hours.")
    print()
    
    # Check if there's existing data
    if scraper.articles_data['articles']:
        print(f"Found existing data: {len(scraper.articles_data['articles'])} articles")
        response = input("Continue scraping from where you left off? (y/n): ")
        if response.lower() != 'y':
            print("Scraping cancelled.")
            return
    
    # Start scraping
    start_time = time.time()
    scraper.scrape_all_pages()
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    print()
    print("=" * 60)
    print(f"Scraping completed in {elapsed_time/60:.2f} minutes")
    print(f"Total articles scraped: {len(scraper.articles_data['articles'])}")
    print(f"Data saved to: {scraper.data_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
