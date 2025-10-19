/**
 * Real Estate News Hub - Frontend JavaScript
 * Handles UI interactions and communication with Python backend
 */

// Global state
let currentSource = 'all';
let currentPage = 1;
let totalPages = 1;
let searchQuery = '';
let scrapingInterval = null;

// Initialize app on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing Flask app...');
    await initializeApp();
});

/**
 * Initialize the application
 */
async function initializeApp() {
    try {
        // Load data location
        await loadDataLocation();
        
        // Always load articles first
        await loadArticles();
        
        // Always check for new articles on startup (automatic)
        console.log('Auto-checking for latest news...');
        showScrapingSidebar('Checking for latest news...');
        await checkForNewArticles();
        
    } catch (error) {
        console.error('Initialization error:', error);
        showError('Failed to initialize application');
    }
}

/**
 * Load and display data location
 */
async function loadDataLocation() {
    try {
        const dataPath = await eel.get_data_location()();
        const pathElement = document.getElementById('data-location-path');
        if (pathElement) {
            pathElement.textContent = dataPath;
        }
        console.log('Data stored at:', dataPath);
    } catch (error) {
        console.error('Failed to get data location:', error);
        const pathElement = document.getElementById('data-location-path');
        if (pathElement) {
            pathElement.textContent = 'Unable to load path';
        }
    }
}

/**
 * Open data folder in file explorer
 */
async function openDataFolder() {
    try {
        const response = await fetch('/api/get_data_location');
        const result = await response.json();
        const dataPath = result.success ? result.data_path : 'Unknown';
        await fetch('/api/open_data_folder', { method: 'POST' });
    } catch (error) {
        console.error('Failed to open data folder:', error);
        showError('Unable to open data folder');
    }
}

/**
 * Show scraping sidebar
 */
function showScrapingSidebar(message = 'Loading...') {
    const panel = document.getElementById('scraping-panel');
    const title = document.getElementById('loading-title');
    const messageEl = document.getElementById('loading-message');
    const statusBtn = document.getElementById('scraping-status-btn');
    
    title.textContent = 'Scraping News Articles';
    messageEl.textContent = message;
    panel.classList.add('show');

    // Show the scraping status button
    statusBtn.style.display = 'flex';
}

/**
 * Hide scraping sidebar
 */
function hideScrapingSidebar() {
    const panel = document.getElementById('scraping-panel');
    const statusBtn = document.getElementById('scraping-status-btn');
    
    panel.classList.remove('show');

    // Hide the scraping status button
    statusBtn.style.display = 'none';
    
    if (scrapingInterval) {
        clearInterval(scrapingInterval);
        scrapingInterval = null;
    }
}

/**
 * Toggle scraping panel visibility
 */
function toggleScrapingPanel() {
    const panel = document.getElementById('scraping-panel');
    if (panel.classList.contains('show')) {
        panel.classList.remove('show');
    } else {
        panel.classList.add('show');
    }
}

/**
 * Close sidebar (user clicked X) - just hide, keep status button visible
 */
function closeSidebar() {
    const panel = document.getElementById('scraping-panel');
    panel.classList.remove('show');
    // Keep the status button visible so user can reopen
}

/**
 * Stop scraping (user clicked Stop button)
 */
async function stopScraping() {
    try {
        // Stop scraping is handled by the backend automatically
        const result = { success: true };
        if (result.success) {
            showNotification('Check stopped successfully', 'info');
            hideScrapingSidebar();
            loadArticles();
        } else {
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Error stopping check:', error);
        showNotification('Failed to stop check', 'error');
    }
}

/**
 * Start tracking scraping progress
 */
function startProgressTracking() {
    // Update progress every 500ms
    scrapingInterval = setInterval(async () => {
        try {
            // Progress tracking is handled by the backend
            const progress = { current_page: 0, total_pages: 6, current_source: 'Processing...' };
            updateProgressDisplay(progress);
        } catch (error) {
            console.error('Error getting progress:', error);
        }
    }, 500);
}

/**
 * Update progress display
 */
function updateProgressDisplay(progress) {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const progressPercentage = document.getElementById('progress-percentage');
    const pagesScraped = document.getElementById('pages-scraped');
    const articlesScraped = document.getElementById('articles-scraped');
    const loadingTitle = document.getElementById('loading-title');
    
    // Calculate percentage
    let percentage = 0;
    if (progress.total_pages > 0) {
        percentage = Math.round((progress.current_page / progress.total_pages) * 100);
    }
    
    // Update title to show current source
    if (progress.current_source) {
        loadingTitle.textContent = `Checking ${progress.current_source}`;
    } else {
        loadingTitle.textContent = 'Checking Latest Articles';
    }
    
    // Update UI
    progressBar.style.width = percentage + '%';
    progressText.textContent = progress.message || 'Processing...';
    progressPercentage.textContent = percentage + '%';
    pagesScraped.textContent = progress.current_page || 0;
    articlesScraped.textContent = progress.articles_scraped || 0;
}

/**
 * Called by Python when scraping is completed
 */
// Flask API handles this automatically
function scraping_completed() {
    console.log('Check completed!');
    
    // Update button to show completion
    const statusBtn = document.getElementById('scraping-status-btn');
    const icon = document.getElementById('scraping-icon');
    const text = document.getElementById('scraping-text');
    
    // Change to checkmark and success state
    icon.classList.remove('animate-spin');
    icon.textContent = 'check_circle';
    text.textContent = 'Complete';
    statusBtn.classList.remove('bg-green-500/10', 'hover:bg-green-500/20', 'text-green-600');
    statusBtn.classList.add('bg-blue-500/10', 'hover:bg-blue-500/20', 'text-blue-600');
    
    // Hide button after 5 seconds
    setTimeout(() => {
        hideScrapingSidebar();
    }, 5000);
    
    loadArticles();
    showNotification('Check completed successfully!', 'success');
}

/**
 * Called by Python to update scraping progress
 */
// Flask API handles this automatically
function update_scraping_progress(progress) {
    updateProgressDisplay(progress);
}

/**
 * Load articles from backend
 */
async function loadArticles() {
    const container = document.getElementById('articles-container');
    const countText = document.getElementById('article-count-text');
    const lastScrapeText = document.getElementById('last-scrape-text');
    const paginationContainer = document.getElementById('pagination-container');
    
    try {
        // Show loading
        container.innerHTML = `
            <div class="text-center text-[#4e7f97] dark:text-gray-400 py-8">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <p class="mt-4">Loading articles...</p>
            </div>
        `;
        
        // Get articles from backend (20 per page for better visibility)
        const params = new URLSearchParams({
            source: currentSource,
            page: currentPage,
            search: searchQuery
        });
        const response = await fetch(`/api/get_articles?${params}`);
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Failed to load articles');
        }
        
        // Update state
        totalPages = result.total_pages;
        
        // Debug logging
        console.log('Articles loaded:', {
            total: result.total,
            page: result.page,
            totalPages: result.total_pages,
            articlesOnPage: result.articles.length
        });
        
        // Update stats
        const startNum = ((result.page - 1) * 20) + 1;
        const endNum = startNum + result.articles.length - 1;
        countText.textContent = `Showing ${startNum}-${endNum} of ${result.total} articles`;
        
        if (result.last_scrape) {
            const date = new Date(result.last_scrape);
            lastScrapeText.textContent = `Last updated: ${formatDate(date)}`;
        }
        
        // Render articles
        if (result.articles.length === 0) {
            container.innerHTML = `
                <div class="text-center text-[#4e7f97] dark:text-gray-400 py-12">
                    <span class="material-symbols-outlined text-6xl mb-4 opacity-50">article</span>
                    <p class="text-lg">No articles found</p>
                    <p class="text-sm mt-2">Try adjusting your search or check back later</p>
                </div>
            `;
            paginationContainer.classList.add('hidden');
        } else {
            container.innerHTML = result.articles.map(article => createArticleCard(article)).join('');
            
            // Always show pagination if there's more than one page
            if (result.total_pages > 1) {
                console.log('Showing pagination:', result.total_pages, 'pages');
                paginationContainer.classList.remove('hidden');
                updatePaginationControls();
            } else {
                console.log('Hiding pagination: only', result.total_pages, 'page');
                paginationContainer.classList.add('hidden');
            }
        }
        
    } catch (error) {
        console.error('Error loading articles:', error);
        container.innerHTML = `
            <div class="text-center text-red-500 py-12">
                <span class="material-symbols-outlined text-6xl mb-4">error</span>
                <p class="text-lg">Failed to load articles</p>
                <p class="text-sm mt-2">${error.message}</p>
            </div>
        `;
    }
}

/**
 * Create HTML for article card
 */
function createArticleCard(article) {
    const date = article.date ? formatDate(new Date(article.date)) : 'Date unknown';
    
    // Determine source badge
    let sourceBadge = '';
    if (article.source === 'fastighetsvarlden') {
        sourceBadge = '<span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Fastighetsvarlden</span>';
    } else if (article.source === 'cision') {
        sourceBadge = '<span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Cision</span>';
    } else if (article.source === 'lokalguiden') {
        sourceBadge = '<span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">Lokalguiden</span>';
    } else if (article.source === 'di') {
        sourceBadge = '<span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">DI</span>';
    } else if (article.source === 'fastighetsnytt') {
        sourceBadge = '<span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Fastighetsnytt</span>';
    } else if (article.source === 'nordicpropertynews') {
        sourceBadge = '<span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">Nordic Property News</span>';
    }
    
    return `
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 bg-white dark:bg-background-dark rounded-xl shadow-sm hover:shadow-lg transition-shadow fade-in">
            <div class="flex flex-col gap-2 flex-grow">
                <div class="flex flex-wrap items-center gap-2">
                    <p class="text-[#0e171b] dark:text-white text-base font-medium leading-normal">
                        ${escapeHtml(article.title)}
                    </p>
                    ${sourceBadge}
                </div>
                <p class="text-[#4e7f97] dark:text-gray-400 text-sm font-normal leading-normal">
                    ${date}
                </p>
            </div>
            <button 
                onclick="openArticle('${escapeHtml(article.url)}')"
                class="flex items-center justify-center gap-2 mt-4 sm:mt-0 px-4 py-2 text-white bg-primary hover:bg-primary/90 rounded-lg transition-colors text-sm font-medium w-full sm:w-auto">
                View / Open Link
            </button>
        </div>
    `;
}

/**
 * Open article in browser
 */
async function openArticle(url) {
    try {
        // Open article link in new tab
        window.open(url, '_blank');
    } catch (error) {
        console.error('Error opening article:', error);
    }
}

/**
 * Select website
 */
function selectWebsite(source) {
    if (currentSource === source) return;
    
    currentSource = source;
    currentPage = 1;
    
    // Update UI
    document.querySelectorAll('.website-tab').forEach(tab => {
        const tabSource = tab.getAttribute('data-source');
        if (tabSource === source) {
            tab.classList.remove('bg-background-light', 'dark:bg-background-dark', 'border', 'border-gray-200', 'dark:border-gray-700');
            tab.classList.add('bg-primary/20', 'hover:bg-primary/30');
            tab.querySelector('p').classList.remove('text-[#0e171b]', 'dark:text-white');
            tab.querySelector('p').classList.add('text-primary');
        } else {
            tab.classList.remove('bg-primary/20', 'hover:bg-primary/30');
            tab.classList.add('bg-background-light', 'dark:bg-background-dark', 'border', 'border-gray-200', 'dark:border-gray-700');
            tab.querySelector('p').classList.remove('text-primary');
            tab.querySelector('p').classList.add('text-[#0e171b]', 'dark:text-white');
        }
    });
    
    loadArticles();
}

/**
 * Search articles
 */
let searchTimeout;
function searchArticles() {
    const input = document.getElementById('search-input');
    searchQuery = input.value.trim();
    currentPage = 1;
    
    // Debounce search
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        loadArticles();
    }, 300);
}

/**
 * Check for new articles
 */
async function checkForNewArticles(silent = false) {
    const refreshBtn = document.getElementById('refresh-btn');
    
    try {
        if (!silent) {
            refreshBtn.disabled = true;
            refreshBtn.querySelector('span:first-child').classList.add('animate-spin');
        }
        
        const response = await fetch('/api/check_for_new_articles', { method: 'POST' });
        const result = await response.json();
        
        if (result.has_new) {
            if (!silent) {
                // Show notification
                showNotification(`${result.new_count} new articles available! Scraping...`);
            }
            
            // Start scraping
            showScrapingSidebar(`Found ${result.new_count} new articles. Scraping...`);
            // Scraping is handled by check_for_new_articles
            await checkForNewArticles();
            startProgressTracking();
        } else {
            if (!silent) {
                showNotification('No new articles. You\'re up to date!', 'info');
            }
        }
        
    } catch (error) {
        console.error('Error checking for new articles:', error);
        if (!silent) {
            showNotification('Failed to check for new articles', 'error');
        }
    } finally {
        if (!silent) {
            refreshBtn.disabled = false;
            refreshBtn.querySelector('span:first-child').classList.remove('animate-spin');
        }
    }
}

/**
 * Pagination
 */
function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        loadArticles();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        loadArticles();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function updatePaginationControls() {
    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');
    const pageInfo = document.getElementById('page-info');
    const pageNumbers = document.getElementById('page-numbers');
    
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    
    // Generate page number buttons
    pageNumbers.innerHTML = '';
    
    // Show up to 7 page buttons (1 ... 4 5 6 ... 10)
    let pagesToShow = [];
    
    if (totalPages <= 7) {
        // Show all pages if 7 or less
        for (let i = 1; i <= totalPages; i++) {
            pagesToShow.push(i);
        }
    } else {
        // Always show first page
        pagesToShow.push(1);
        
        if (currentPage > 3) {
            pagesToShow.push('...');
        }
        
        // Show pages around current page
        for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
            if (!pagesToShow.includes(i)) {
                pagesToShow.push(i);
            }
        }
        
        if (currentPage < totalPages - 2) {
            pagesToShow.push('...');
        }
        
        // Always show last page
        if (!pagesToShow.includes(totalPages)) {
            pagesToShow.push(totalPages);
        }
    }
    
    // Create buttons
    pagesToShow.forEach(page => {
        if (page === '...') {
            const dots = document.createElement('span');
            dots.className = 'px-2 text-[#4e7f97] dark:text-gray-400';
            dots.textContent = '...';
            pageNumbers.appendChild(dots);
        } else {
            const btn = document.createElement('button');
            btn.onclick = () => goToPage(page);
            btn.textContent = page;
            
            if (page === currentPage) {
                btn.className = 'px-4 py-2 bg-primary text-white rounded-lg font-medium';
            } else {
                btn.className = 'px-4 py-2 bg-white dark:bg-background-dark border border-gray-200 dark:border-gray-700 text-[#0e171b] dark:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 hover:border-primary transition-all font-medium';
            }
            
            pageNumbers.appendChild(btn);
        }
    });
    
    console.log('Pagination updated:', { currentPage, totalPages, pagesToShow });
}

/**
 * Go to specific page
 */
function goToPage(pageNum) {
    if (pageNum >= 1 && pageNum <= totalPages && pageNum !== currentPage) {
        currentPage = pageNum;
        loadArticles();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg flex items-center gap-3 fade-in ${
        type === 'error' ? 'bg-red-500' : type === 'info' ? 'bg-blue-500' : 'bg-green-500'
    } text-white`;
    
    notification.innerHTML = `
        <span class="material-symbols-outlined">${
            type === 'error' ? 'error' : type === 'info' ? 'info' : 'check_circle'
        }</span>
        <p>${message}</p>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

/**
 * Show error
 */
function showError(message) {
    showNotification(message, 'error');
}

/**
 * Format date
 */
function formatDate(date) {
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
        return 'Today';
    } else if (days === 1) {
        return 'Yesterday';
    } else if (days < 7) {
        return `${days} days ago`;
    } else {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
