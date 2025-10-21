import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ArticleList } from './components/ArticleList';
import { ScrapingProgress } from './components/ScrapingProgress';
import { scraperManager } from './lib/scraper-manager.js';
import { getArticles } from './lib/database.js';
import { CONFIG } from './lib/config.js';

function App() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentSource, setCurrentSource] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [totalPages, setTotalPages] = useState(1);
  const [totalArticles, setTotalArticles] = useState(0);
  const [scrapingProgress, setScrapingProgress] = useState(null);
  const [isScraping, setIsScraping] = useState(false);

  // Load articles on component mount and when filters change
  useEffect(() => {
    loadArticles();
  }, [currentSource, currentPage, searchQuery]);

  // Auto-scrape on first load
  useEffect(() => {
    const hasRunBefore = localStorage.getItem('news-hub-initialized');
    if (!hasRunBefore) {
      localStorage.setItem('news-hub-initialized', 'true');
      startScraping();
    }
  }, []);

  const loadArticles = async () => {
    setLoading(true);
    try {
      const result = await getArticles(currentSource, currentPage, 20, searchQuery);
      if (result.success) {
        setArticles(result.articles);
        setTotalPages(result.totalPages);
        setTotalArticles(result.total);
      } else {
        console.error('Failed to load articles:', result.error);
      }
    } catch (error) {
      console.error('Error loading articles:', error);
    } finally {
      setLoading(false);
    }
  };

  const startScraping = async () => {
    if (isScraping) return;
    
    setIsScraping(true);
    setScrapingProgress({
      status: 'starting',
      message: 'Starting scraping process...',
      currentSource: null,
      sourcesCompleted: [],
      totalSources: Object.keys(CONFIG.SOURCES).length,
      currentSourceIndex: 0,
      articlesScraped: 0
    });

    try {
      const result = await scraperManager.scrapeAll((progress) => {
        setScrapingProgress(progress);
      });

      if (result.success) {
        console.log(`Scraping completed. Found ${result.articlesScraped} new articles.`);
        // Reload articles to show new ones
        await loadArticles();
      } else {
        console.error('Scraping failed:', result.error);
      }
    } catch (error) {
      console.error('Scraping error:', error);
    } finally {
      setIsScraping(false);
      setScrapingProgress(null);
    }
  };

  const stopScraping = () => {
    scraperManager.stopScraping();
    setIsScraping(false);
    setScrapingProgress(null);
  };

  const handleSourceChange = (source) => {
    setCurrentSource(source);
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const handleArticleClick = (url) => {
    window.open(url, '_blank');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      
      <div className="flex">
        <Sidebar 
          currentSource={currentSource}
          onSourceChange={handleSourceChange}
          onSearch={handleSearch}
          onStartScraping={startScraping}
          onStopScraping={stopScraping}
          isScraping={isScraping}
        />
        
        <main className="flex-1 p-6">
          {scrapingProgress && (
            <ScrapingProgress 
              progress={scrapingProgress}
              onStop={stopScraping}
            />
          )}
          
          <ArticleList
            articles={articles}
            loading={loading}
            currentPage={currentPage}
            totalPages={totalPages}
            totalArticles={totalArticles}
            onPageChange={handlePageChange}
            onArticleClick={handleArticleClick}
          />
        </main>
      </div>
    </div>
  );
}

export default App;
