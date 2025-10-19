"""
Configuration file for News Dashboard
Defines data storage location and other settings
"""

from pathlib import Path
import os

# Always use the project directory for data storage
DATA_DIR = Path(__file__).parent / "data"

# Ensure directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Data file paths
FASTIGHETSVARLDEN_DATA_FILE = DATA_DIR / "fastighet_news_data.json"
CISION_DATA_FILE = DATA_DIR / "cision_news_data.json"
LOKALGUIDEN_DATA_FILE = DATA_DIR / "lokalguiden_news_data.json"
DI_DATA_FILE = DATA_DIR / "di_news_data.json"
FASTIGHETSNYTT_DATA_FILE = DATA_DIR / "fastighetsnytt_news_data.json"
NORDICPROPERTYNEWS_DATA_FILE = DATA_DIR / "nordicpropertynews_news_data.json"

# Log file paths
APP_LOG_FILE = DATA_DIR / "app.log"
SCRAPER_LOG_FILE = DATA_DIR / "scraper.log"

def get_data_directory():
    """Get the data directory path"""
    return str(DATA_DIR)

def ensure_data_directory():
    """Ensure data directory exists"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR

# Ensure data directory exists on import
ensure_data_directory()

