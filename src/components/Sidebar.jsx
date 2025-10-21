import React, { useState } from 'react';
import { Search, Play, Square, Database, FolderOpen } from 'lucide-react';
import { CONFIG } from '../lib/config.js';

export function Sidebar({ 
  currentSource, 
  onSourceChange, 
  onSearch, 
  onStartScraping, 
  onStopScraping, 
  isScraping 
}) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    onSearch(searchQuery);
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const getSourceColor = (source) => {
    const colors = {
      fastighetsvarlden: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      cision: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      lokalguiden: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      di: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      fastighetsnytt: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      nordicpropertynews: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
    };
    return colors[source] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  };

  return (
    <aside className="w-80 bg-white dark:bg-gray-800 shadow-sm border-r border-gray-200 dark:border-gray-700">
      <div className="p-6">
        {/* Scraping Controls */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            News Sources
          </h3>
          
          <div className="space-y-2 mb-4">
            <button
              onClick={() => onSourceChange('all')}
              className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                currentSource === 'all'
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              All Sources
            </button>
            
            {Object.entries(CONFIG.SOURCES).map(([key, source]) => (
              <button
                key={key}
                onClick={() => onSourceChange(key)}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  currentSource === key
                    ? getSourceColor(key)
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                {source.name}
              </button>
            ))}
          </div>
        </div>

        {/* Search */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Search Articles
          </h3>
          
          <form onSubmit={handleSearchSubmit} className="relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder="Search articles..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </form>
        </div>

        {/* Scraping Controls */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Scraping Controls
          </h3>
          
          <div className="space-y-3">
            {!isScraping ? (
              <button
                onClick={onStartScraping}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                <Play className="h-4 w-4" />
                Start Scraping
              </button>
            ) : (
              <button
                onClick={onStopScraping}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                <Square className="h-4 w-4" />
                Stop Scraping
              </button>
            )}
          </div>
        </div>

        {/* Data Management */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Data Management
          </h3>
          
          <div className="space-y-2">
            <button className="w-full flex items-center gap-2 px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
              <Database className="h-4 w-4" />
              View Database
            </button>
            
            <button className="w-full flex items-center gap-2 px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
              <FolderOpen className="h-4 w-4" />
              Open Data Folder
            </button>
          </div>
        </div>

        {/* Info */}
        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <p className="text-xs text-blue-800 dark:text-blue-300">
            <strong>Note:</strong> The app checks 6 sources: Fastighetsvarlden, Cision, Lokalguiden, DI, Fastighetsnytt, and Nordic Property News. Swedish titles are translated to English automatically.
          </p>
        </div>
      </div>
    </aside>
  );
}
