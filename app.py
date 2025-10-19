"""
Real Estate News Hub - Main Application
Eel-based desktop application for scraping and viewing news
"""

import eel
import json
import time
from datetime import datetime
from pathlib import Path
import threading
from fastighetsvarlden_scraper import FastighetsVarldenScraper
from cision_scraper import CisionScraper
from lokalguiden_scraper import LokalguidenScraper
from di_scraper import DIScraper
from fastighetsnytt_scraper import FastighetsnyttScraper
from nordicpropertynews_scraper import NordicPropertyNewsScraper
import logging
from deep_translator import GoogleTranslator
from config import (
    FASTIGHETSVARLDEN_DATA_FILE, 
    CISION_DATA_FILE, 
    LOKALGUIDEN_DATA_FILE,
    DI_DATA_FILE,
    FASTIGHETSNYTT_DATA_FILE,
    NORDICPROPERTYNEWS_DATA_FILE,
    APP_LOG_FILE,
    ensure_data_directory,
    get_data_directory
)

# Ensure data directory exists
ensure_data_directory()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(APP_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Eel with the web folder
eel.init('web')

# Global variables
scraper = None
scraping_in_progress = False
scraping_thread = None
translator = GoogleTranslator(source='auto', target='en')


class ScraperProgress:
    """Track scraping progress"""
    def __init__(self):
        self.current_page = 0
        self.total_pages = 0
        self.articles_scraped = 0
        self.status = "idle"
        self.message = ""
        self.current_source = ""
        self.sources_completed = []


progress = ScraperProgress()


def translate_title(title):
    """
    Translate article title to English
    
    Args:
        title: Original title in any language
        
    Returns:
        Translated title in English (or original if translation fails)
    """
    try:
        # Skip if title is already in English (rough check)
        if all(ord(char) < 128 for char in title):
            # Likely already English, but still translate to be sure
            pass
        
        translated = translator.translate(title)
        return translated
    except Exception as e:
        logger.warning(f"Translation failed for '{title}': {e}")
        return title  # Return original if translation fails


@eel.expose
def get_initial_state():
    """
    Get initial application state
    Returns info about existing articles and triggers auto-check for new ones
    """
    data_file = FASTIGHETSVARLDEN_DATA_FILE
    
    if not data_file.exists():
        # First run - no data exists
        return {
            'needs_scraping': True,
            'article_count': 0,
            'last_scrape': None
        }
    
    # Load existing data
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        article_count = data.get('total_articles', 0)
        last_scrape = data.get('last_incremental_scrape') or data.get('last_full_scrape')
        
        return {
            'needs_scraping': True,  # Always check for new articles on startup
            'article_count': article_count,
            'last_scrape': last_scrape
        }
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return {
            'needs_scraping': True,
            'article_count': 0,
            'last_scrape': None
        }


@eel.expose
def start_scraping():
    """Start the scraping process (incremental only - checks latest news)"""
    global scraping_in_progress, scraping_thread, progress, scraper
    
    if scraping_in_progress:
        return {'success': False, 'message': 'Scraping already in progress'}
    
    progress.status = "starting"
    progress.message = "Checking for latest news..."
    scraping_in_progress = True
    
    # Start scraping in a separate thread
    scraping_thread = threading.Thread(target=_scrape_worker)
    scraping_thread.daemon = True
    scraping_thread.start()
    
    return {'success': True, 'message': 'Checking for new articles...'}


@eel.expose
def stop_scraping():
    """Stop the scraping process"""
    global scraping_in_progress, progress
    
    if scraping_in_progress:
        scraping_in_progress = False
        progress.status = "stopped"
        progress.message = "Scraping stopped by user"
        logger.info("Scraping stopped by user")
        return {'success': True, 'message': 'Scraping stopped'}
    
    return {'success': False, 'message': 'No scraping in progress'}


def _scrape_worker():
    """Worker function for scraping (runs in separate thread)"""
    global scraping_in_progress, progress
    
    try:
        logger.info("Checking for latest news articles from all sources")
        progress.status = "checking"
        progress.sources_completed = []
        progress.total_pages = 6  # 6 sources to check
        progress.current_page = 0
        
        total_new_articles = 0
        
        # Scrape Fastighetsvarlden (Site 1)
        progress.current_source = "Fastighetsvarlden"
        progress.current_page = 1
        progress.message = "Checking Fastighetsvarlden for new articles..."
        eel.update_scraping_progress(progress.__dict__)()
        
        new_count_1 = _run_fastighetsvarlden_scrape()
        total_new_articles += new_count_1
        progress.sources_completed.append("Fastighetsvarlden")
        
        # Scrape Cision (Site 2)
        progress.current_source = "Cision"
        progress.current_page = 2
        progress.message = "Checking Cision for new articles..."
        eel.update_scraping_progress(progress.__dict__)()
        
        new_count_2 = _run_cision_scrape()
        total_new_articles += new_count_2
        progress.sources_completed.append("Cision")
        
        # Scrape Lokalguiden (Site 3)
        progress.current_source = "Lokalguiden"
        progress.current_page = 3
        progress.message = "Checking Lokalguiden for new articles..."
        eel.update_scraping_progress(progress.__dict__)()
        
        new_count_3 = _run_lokalguiden_scrape()
        total_new_articles += new_count_3
        progress.sources_completed.append("Lokalguiden")
        
        # Scrape DI (Site 4)
        progress.current_source = "DI"
        progress.current_page = 4
        progress.message = "Checking DI for new articles..."
        eel.update_scraping_progress(progress.__dict__)()
        
        new_count_4 = _run_di_scrape()
        total_new_articles += new_count_4
        progress.sources_completed.append("DI")
        
        # Scrape Fastighetsnytt (Site 5)
        progress.current_source = "Fastighetsnytt"
        progress.current_page = 5
        progress.message = "Checking Fastighetsnytt for new articles..."
            eel.update_scraping_progress(progress.__dict__)()
            
        new_count_5 = _run_fastighetsnytt_scrape()
        total_new_articles += new_count_5
        progress.sources_completed.append("Fastighetsnytt")
        
        # Scrape Nordic Property News (Site 6)
        progress.current_source = "Nordic Property News"
        progress.current_page = 6
        progress.message = "Checking Nordic Property News for new articles..."
            eel.update_scraping_progress(progress.__dict__)()
            
        new_count_6 = _run_nordicpropertynews_scrape()
        total_new_articles += new_count_6
        progress.sources_completed.append("Nordic Property News")
        
        # Complete
        progress.status = "completed"
        progress.articles_scraped = total_new_articles
        progress.message = f"Check completed! Found {total_new_articles} new articles"
        eel.update_scraping_progress(progress.__dict__)()
        
        # Notify frontend that scraping is done
        eel.scraping_completed()()
        
    except Exception as e:
        logger.error(f"Scraping error: {e}", exc_info=True)
        progress.status = "error"
        progress.message = f"Error: {str(e)}"
        eel.update_scraping_progress(progress.__dict__)()
    
    finally:
        scraping_in_progress = False


def _run_full_scrape():
    """Run a full scrape of all pages"""
    global progress, scraper
    
    # Check if we should resume from a previous page
    start_page = scraper.articles_data.get('last_page_scraped', 0) + 1
    if start_page > 1:
        logger.info(f"Resuming scrape from page {start_page}")
    
    # Get first page to determine total pages
    first_page_html = scraper._fetch_page(1)
    if not first_page_html:
        raise Exception("Failed to fetch first page")
    
    max_page = scraper._get_max_page_number(first_page_html)
    progress.total_pages = max_page
    scraper.articles_data['total_pages'] = max_page
    
    logger.info("=" * 70)
    if start_page == 1:
        logger.info(f"STARTING FULL SCRAPE: {max_page} PAGES")
    else:
        logger.info(f"RESUMING SCRAPE: Pages {start_page}-{max_page} (Total: {max_page})")
    logger.info("=" * 70)
    
    # Process pages from start_page to max_page
    for page_num in range(start_page, max_page + 1):
        if not scraping_in_progress:
            logger.warning("Scraping interrupted by user")
            break
        
        progress.current_page = page_num
        progress.message = f"Scraping page {page_num} of {max_page}..."
        eel.update_scraping_progress(progress.__dict__)()
        
        # Fetch page
        if page_num == 1 and start_page == 1:
            html = first_page_html
        else:
            html = scraper._fetch_page(page_num)
        
        if not html:
            logger.warning(f"Failed to fetch page {page_num}, skipping...")
            continue
        
        # Parse articles
        articles = scraper._parse_page(html)
        new_count = 0
        
        for article in articles:
            if not scraper._is_duplicate(article['url']):
                # Translate title to English
                original_title = article['title']
                translated_title = translate_title(original_title)
                
                # Store both original and translated
                article['title'] = translated_title
                article['original_title'] = original_title
                
                scraper.articles_data['articles'].append(article)
                scraper.article_urls.add(article['url'])
                new_count += 1
        
        progress.articles_scraped = len(scraper.articles_data['articles'])
        
        # Update last page scraped
        scraper.articles_data['last_page_scraped'] = page_num
        
        logger.info(f"Page {page_num}/{max_page}: Found {len(articles)} articles, {new_count} new (Total: {progress.articles_scraped})")
        
        # Save progress every 10 pages
        if page_num % 10 == 0:
            scraper._save_data()
            logger.info(f"[SAVED] Progress saved at page {page_num}: {progress.articles_scraped} articles")
    
    # Final save
    scraper.articles_data['last_full_scrape'] = datetime.now().isoformat()
    scraper._save_data()
    logger.info("=" * 70)
    logger.info("[SUCCESS] FULL SCRAPE COMPLETED!")
    logger.info(f"Total pages scraped: {max_page}")
    logger.info(f"Total articles: {progress.articles_scraped}")
    logger.info("=" * 70)


def _run_fastighetsvarlden_scrape():
    """Scrape Fastighetsvarlden (Site 1) - page 1 only"""
    global progress
    
    try:
        scraper = FastighetsVarldenScraper()
    new_articles_count = 0
        
        html = scraper._fetch_page(1)
        if not html:
            logger.warning("Failed to fetch Fastighetsvarlden page 1")
            return 0
        
        articles = scraper._parse_page(html)
        logger.info(f"Found {len(articles)} articles on Fastighetsvarlden page 1")
        
        for article in articles:
            if not scraper._is_duplicate(article['url']):
                # Translate title to English
                original_title = article['title']
                translated_title = translate_title(original_title)
                
                # Store both original and translated
                article['title'] = translated_title
                article['original_title'] = original_title
                article['source'] = 'fastighetsvarlden'
                
                scraper.articles_data['articles'].append(article)
                scraper.article_urls.add(article['url'])
                new_articles_count += 1
                logger.info(f"New Fastighetsvarlden article: {translated_title}")
        
        scraper.articles_data['last_incremental_scrape'] = datetime.now().isoformat()
        scraper._save_data()
        
        logger.info(f"Fastighetsvarlden: {new_articles_count} new articles")
        return new_articles_count
        
    except Exception as e:
        logger.error(f"Error scraping Fastighetsvarlden: {e}")
        return 0


def _run_cision_scrape():
    """Scrape Cision (Site 2) - page 1 only"""
    global progress
    
    try:
        scraper = CisionScraper()
        new_articles_count = scraper.scrape_latest()
        
        logger.info(f"Cision: {new_articles_count} new articles")
        return new_articles_count
        
    except Exception as e:
        logger.error(f"Error scraping Cision: {e}")
        return 0


def _run_lokalguiden_scrape():
    """Scrape Lokalguiden (Site 3) - page 1 only"""
    global progress
    
    try:
        scraper = LokalguidenScraper()
        
        # Scrape without translation first
        html = scraper._fetch_page()
        if not html:
            logger.warning("Failed to fetch Lokalguiden page")
            return 0
        
        articles = scraper._parse_page(html)
        new_articles_count = 0
        
        for article in articles:
            if not scraper._is_duplicate(article['url']):
                # Translate title to English
                original_title = article['title']
                translated_title = translate_title(original_title)
                
                # Store both original and translated
                article['title'] = translated_title
                article['original_title'] = original_title
                article['source'] = 'lokalguiden'
                
                scraper.articles_data['articles'].append(article)
                scraper.article_urls.add(article['url'])
                new_articles_count += 1
                logger.info(f"New Lokalguiden article: {translated_title}")
        
        scraper.articles_data['last_scrape'] = datetime.now().isoformat()
        scraper._save_data()
        
        logger.info(f"Lokalguiden: {new_articles_count} new articles")
        return new_articles_count
        
    except Exception as e:
        logger.error(f"Error scraping Lokalguiden: {e}")
        return 0


def _run_di_scrape():
    """Scrape DI (Site 4) - page 1 only"""
    global progress
    
    try:
        scraper = DIScraper()
        
        # Scrape without translation first
        html = scraper._fetch_page()
        if not html:
            logger.warning("Failed to fetch DI page")
            return 0
        
        articles = scraper._parse_page(html)
        new_articles_count = 0
        
        for article in articles:
            if not scraper._is_duplicate(article['url']):
                # Translate title to English
                original_title = article['title']
                translated_title = translate_title(original_title)
                
                # Store both original and translated
                article['title'] = translated_title
                article['original_title'] = original_title
                article['source'] = 'di'
                
                scraper.articles_data['articles'].append(article)
                scraper.article_urls.add(article['url'])
                new_articles_count += 1
                logger.info(f"New DI article: {translated_title}")
        
        scraper.articles_data['last_scrape'] = datetime.now().isoformat()
        scraper._save_data()
        
        logger.info(f"DI: {new_articles_count} new articles")
        return new_articles_count
        
    except Exception as e:
        logger.error(f"Error scraping DI: {e}")
        return 0


def _run_fastighetsnytt_scrape():
    """Scrape Fastighetsnytt (Site 5) - homepage only"""
    global progress
    
    try:
        scraper = FastighetsnyttScraper()
        
        # Scrape homepage (parses __NEXT_DATA__ JSON)
        html = scraper._fetch_page()
        if not html:
            logger.warning("Failed to fetch Fastighetsnytt homepage")
            return 0
        
        articles = scraper._parse_page(html)
        new_articles_count = 0
        
        for article in articles:
            if not scraper._is_duplicate(article['url']):
                # Translate title to English
                original_title = article['title']
                translated_title = translate_title(original_title)
                
                # Store both original and translated
                article['title'] = translated_title
                article['original_title'] = original_title
                article['source'] = 'fastighetsnytt'
                
                scraper.articles_data['articles'].append(article)
                scraper.article_urls.add(article['url'])
                new_articles_count += 1
                logger.info(f"New Fastighetsnytt article: {translated_title}")
        
        scraper.articles_data['last_scrape'] = datetime.now().isoformat()
    scraper._save_data()
        
        logger.info(f"Fastighetsnytt: {new_articles_count} new articles")
        return new_articles_count
        
    except Exception as e:
        logger.error(f"Error scraping Fastighetsnytt: {e}")
        return 0


def _run_nordicpropertynews_scrape():
    """Scrape Nordic Property News (Site 6) - page 1 only"""
    global progress
    
    try:
        scraper = NordicPropertyNewsScraper()
        
        # Scrape page 1 (no translation needed, already in English)
        html = scraper._fetch_page()
        if not html:
            logger.warning("Failed to fetch Nordic Property News page")
            return 0
        
        articles = scraper._parse_page(html)
        new_articles_count = 0
        
        for article in articles:
            if not scraper._is_duplicate(article['url']):
                # No translation needed - already in English
                article['source'] = 'nordicpropertynews'
                
                scraper.articles_data['articles'].append(article)
                scraper.article_urls.add(article['url'])
                new_articles_count += 1
                logger.info(f"New Nordic Property News article: {article['title']}")
        
        scraper.articles_data['last_scrape'] = datetime.now().isoformat()
        scraper._save_data()
        
        logger.info(f"Nordic Property News: {new_articles_count} new articles")
        return new_articles_count
        
    except Exception as e:
        logger.error(f"Error scraping Nordic Property News: {e}")
        return 0


@eel.expose
def get_scraping_progress():
    """Get current scraping progress"""
    return progress.__dict__


@eel.expose
def get_articles(source="all", search_query="", page=1, per_page=20):
    """
    Get articles for display
    
    Args:
        source: Source website ("fastighetsvarlden", "cision", "lokalguiden", "di", or "all")
        search_query: Search filter
        page: Page number for pagination
        per_page: Articles per page
    """
    try:
        articles = []
        last_scrape = None
        
        # Load articles from Fastighetsvarlden
        if source in ["fastighetsvarlden", "all"]:
            fv_file = FASTIGHETSVARLDEN_DATA_FILE
            if fv_file.exists():
                with open(fv_file, 'r', encoding='utf-8') as f:
                    fv_data = json.load(f)
                    fv_articles = fv_data.get('articles', [])
                    # Ensure source field is set
                    for article in fv_articles:
                        if 'source' not in article:
                            article['source'] = 'fastighetsvarlden'
                    articles.extend(fv_articles)
                    last_scrape = fv_data.get('last_incremental_scrape') or fv_data.get('last_full_scrape')
        
        # Load articles from Cision
        if source in ["cision", "all"]:
            cision_file = CISION_DATA_FILE
            if cision_file.exists():
                with open(cision_file, 'r', encoding='utf-8') as f:
                    cision_data = json.load(f)
                    cision_articles = cision_data.get('articles', [])
                    # Ensure source field is set
                    for article in cision_articles:
                        if 'source' not in article:
                            article['source'] = 'cision'
                    articles.extend(cision_articles)
                    cision_scrape = cision_data.get('last_scrape')
                    if cision_scrape:
                        if not last_scrape or cision_scrape > last_scrape:
                            last_scrape = cision_scrape
        
        # Load articles from Lokalguiden
        if source in ["lokalguiden", "all"]:
            lg_file = LOKALGUIDEN_DATA_FILE
            if lg_file.exists():
                with open(lg_file, 'r', encoding='utf-8') as f:
                    lg_data = json.load(f)
                    lg_articles = lg_data.get('articles', [])
                    # Ensure source field is set
                    for article in lg_articles:
                        if 'source' not in article:
                            article['source'] = 'lokalguiden'
                    articles.extend(lg_articles)
                    lg_scrape = lg_data.get('last_scrape')
                    if lg_scrape:
                        if not last_scrape or lg_scrape > last_scrape:
                            last_scrape = lg_scrape
        
        # Load articles from DI
        if source in ["di", "all"]:
            di_file = DI_DATA_FILE
            if di_file.exists():
                with open(di_file, 'r', encoding='utf-8') as f:
                    di_data = json.load(f)
                    di_articles = di_data.get('articles', [])
                    # Ensure source field is set
                    for article in di_articles:
                        if 'source' not in article:
                            article['source'] = 'di'
                    articles.extend(di_articles)
                    di_scrape = di_data.get('last_scrape')
                    if di_scrape:
                        if not last_scrape or di_scrape > last_scrape:
                            last_scrape = di_scrape
        
        # Load articles from Fastighetsnytt
        if source in ["fastighetsnytt", "all"]:
            fn_file = FASTIGHETSNYTT_DATA_FILE
            if fn_file.exists():
                with open(fn_file, 'r', encoding='utf-8') as f:
                    fn_data = json.load(f)
                    fn_articles = fn_data.get('articles', [])
                    # Ensure source field is set
                    for article in fn_articles:
                        if 'source' not in article:
                            article['source'] = 'fastighetsnytt'
                    articles.extend(fn_articles)
                    fn_scrape = fn_data.get('last_scrape')
                    if fn_scrape:
                        if not last_scrape or fn_scrape > last_scrape:
                            last_scrape = fn_scrape
        
        # Load articles from Nordic Property News
        if source in ["nordicpropertynews", "all"]:
            npn_file = NORDICPROPERTYNEWS_DATA_FILE
            if npn_file.exists():
                with open(npn_file, 'r', encoding='utf-8') as f:
                    npn_data = json.load(f)
                    npn_articles = npn_data.get('articles', [])
                    # Ensure source field is set
                    for article in npn_articles:
                        if 'source' not in article:
                            article['source'] = 'nordicpropertynews'
                    articles.extend(npn_articles)
                    npn_scrape = npn_data.get('last_scrape')
                    if npn_scrape:
                        if not last_scrape or npn_scrape > last_scrape:
                            last_scrape = npn_scrape
        
        # Filter by search query
        if search_query:
            query_lower = search_query.lower()
            articles = [
                a for a in articles
                if query_lower in a['title'].lower()
            ]
        
        # Sort by date (newest first)
        articles = sorted(
            articles,
            key=lambda x: x.get('date', '') or '',
            reverse=True
        )
        
        # Pagination
        total = len(articles)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_articles = articles[start_idx:end_idx]
        
        return {
            'success': True,
            'articles': page_articles,
            'total': total,
            'page': page,
            'total_pages': total_pages,
            'last_scrape': last_scrape
        }
    
    except Exception as e:
        logger.error(f"Error getting articles: {e}")
        return {
            'success': False,
            'articles': [],
            'total': 0,
            'page': page,
            'total_pages': 0,
            'error': str(e)
        }


@eel.expose
def check_for_new_articles():
    """
    Check if there are new articles available from all sources
    """
    try:
        total_new = 0
        
        # Check Fastighetsvarlden
        try:
            fv_scraper = FastighetsVarldenScraper()
            html = fv_scraper._fetch_page(1)
            if html:
                articles = fv_scraper._parse_page(html)
                new_count = sum(1 for a in articles if not fv_scraper._is_duplicate(a['url']))
                total_new += new_count
        except Exception as e:
            logger.warning(f"Error checking Fastighetsvarlden: {e}")
        
        # Check Cision
        try:
            cision_scraper = CisionScraper()
            html = cision_scraper._fetch_page()
            if html:
                articles = cision_scraper._parse_page(html)
                new_count = sum(1 for a in articles if not cision_scraper._is_duplicate(a['url']))
                total_new += new_count
        except Exception as e:
            logger.warning(f"Error checking Cision: {e}")
        
        # Check Lokalguiden
        try:
            lg_scraper = LokalguidenScraper()
            html = lg_scraper._fetch_page()
            if html:
                articles = lg_scraper._parse_page(html)
                new_count = sum(1 for a in articles if not lg_scraper._is_duplicate(a['url']))
                total_new += new_count
        except Exception as e:
            logger.warning(f"Error checking Lokalguiden: {e}")
        
        # Check DI
        try:
            di_scraper = DIScraper()
            html = di_scraper._fetch_page()
            if html:
                articles = di_scraper._parse_page(html)
                new_count = sum(1 for a in articles if not di_scraper._is_duplicate(a['url']))
                total_new += new_count
        except Exception as e:
            logger.warning(f"Error checking DI: {e}")
        
        # Check Fastighetsnytt
        try:
            fn_scraper = FastighetsnyttScraper()
            html = fn_scraper._fetch_page()
            if html:
                articles = fn_scraper._parse_page(html)
                new_count = sum(1 for a in articles if not fn_scraper._is_duplicate(a['url']))
                total_new += new_count
        except Exception as e:
            logger.warning(f"Error checking Fastighetsnytt: {e}")
        
        # Check Nordic Property News
        try:
            npn_scraper = NordicPropertyNewsScraper()
            html = npn_scraper._fetch_page()
            if html:
                articles = npn_scraper._parse_page(html)
                new_count = sum(1 for a in articles if not npn_scraper._is_duplicate(a['url']))
                total_new += new_count
        except Exception as e:
            logger.warning(f"Error checking Nordic Property News: {e}")
        
        return {
            'has_new': total_new > 0,
            'new_count': total_new
        }
    
    except Exception as e:
        logger.error(f"Error checking for new articles: {e}")
        return {'has_new': False, 'error': str(e)}


@eel.expose
def open_article_link(url):
    """Open article link in default browser"""
    import webbrowser
    try:
        webbrowser.open(url)
        return {'success': True}
    except Exception as e:
        logger.error(f"Error opening link: {e}")
        return {'success': False, 'error': str(e)}


@eel.expose
def get_data_location():
    """Get the location where all scraped data is stored"""
    return get_data_directory()


@eel.expose
def open_data_folder(folder_path):
    """Open data folder in file explorer"""
    import subprocess
    import platform
    import os
    
    try:
        system = platform.system()
        if system == 'Windows':
            os.startfile(folder_path)
        elif system == 'Darwin':  # macOS
            subprocess.Popen(['open', folder_path])
        else:  # Linux and others
            subprocess.Popen(['xdg-open', folder_path])
        return {'success': True}
    except Exception as e:
        logger.error(f"Error opening folder: {e}")
        return {'success': False, 'error': str(e)}


def find_available_port(start_port=8080, max_attempts=10):
    """Find an available port starting from start_port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                logger.info(f"Found available port: {port}")
                return port
        except OSError:
            logger.debug(f"Port {port} is in use, trying next...")
            continue
    
    # If no port found, return None
    logger.error(f"Could not find available port in range {start_port}-{start_port + max_attempts}")
    return None


# Create Flask app for PythonAnywhere
app = None

def create_app():
    """Create Flask application for PythonAnywhere"""
    global app
    if app is None:
        from flask import Flask, send_from_directory, jsonify, request
        
        app = Flask(__name__, static_folder='web', static_url_path='')
        
        # Flask routes
        @app.route('/')
        def index():
            return send_from_directory('web', 'index.html')
        
        @app.route('/<path:filename>')
        def static_files(filename):
            return send_from_directory('web', filename)
        
        # API routes for Eel functions
        @app.route('/api/check_for_new_articles', methods=['POST'])
        def api_check_for_new_articles():
            try:
                # Call the existing function
                result = check_for_new_articles()
                return jsonify(result)
            except Exception as e:
                logger.error(f"API error: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @app.route('/api/get_articles', methods=['GET'])
        def api_get_articles():
            try:
                source = request.args.get('source', 'all')
                page = int(request.args.get('page', 1))
                search = request.args.get('search', '')
                
                # Call the existing function
                result = get_articles(source, page, search)
                return jsonify(result)
            except Exception as e:
                logger.error(f"API error: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        # Data location functionality removed
    
    return app


def main():
    """Main application entry point"""
    import os
    import sys
    
    try:
        logger.info("Starting Real Estate News Hub...")
        
        # Check if running on PythonAnywhere
        if 'pythonanywhere.com' in os.getenv('HTTP_HOST', ''):
            logger.info("Detected PythonAnywhere environment - using Eel web mode")
            # For PythonAnywhere, just initialize Eel and let WSGI handle it
            eel.init('web')
            return
        
        # Get host and port from environment variables or use defaults
        host = os.getenv('HOST', '0.0.0.0')  # Bind to all interfaces for external access
        port = int(os.getenv('PORT', 8080))
        
        # For server deployment, use web mode instead of chrome-app
        mode = 'web' if os.getenv('SERVER_MODE', 'false').lower() == 'true' else 'chrome-app'
        
        logger.info(f"Starting application on {host}:{port} in {mode} mode")
        
        if mode == 'web':
            # Web server mode - accessible via IP/domain
            eel.start('index.html', host=host, port=port, mode='web', 
                     block=False, shutdown_delay=1.0)
            logger.info(f"🌐 Server is running at: http://{host}:{port}")
            logger.info("Press Ctrl+C to stop the server")
            
            # Keep the server running
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Server stopped by user")
        else:
            # Desktop mode (original behavior)
            eel.start('index.html', size=(1200, 800), port=port, mode='chrome-app', 
                     close_callback=lambda *args: None, 
                     cmdline_args=['--disable-web-security', '--disable-features=VizDisplayCompositor'])
        
    except KeyboardInterrupt:
        logger.info("Application closed by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        if 'mode' in locals() and mode == 'web':
            logger.error("Server failed to start. Check if port is available.")
        else:
            show_error_dialog("Application Error", f"An error occurred:\n\n{str(e)}")


def show_error_dialog(title, message):
    """Show error dialog (works in windowed mode)"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception as dialog_error:
        # If tkinter not available or fails, just log
        logger.error(f"Could not show error dialog: {dialog_error}")
        pass


if __name__ == "__main__":
    main()
