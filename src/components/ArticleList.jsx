import React from 'react';
import { ExternalLink, Calendar, Tag } from 'lucide-react';
import { CONFIG } from '../lib/config.js';

export function ArticleList({ 
  articles, 
  loading, 
  currentPage, 
  totalPages, 
  totalArticles, 
  onPageChange, 
  onArticleClick 
}) {
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

  const getSourceName = (source) => {
    return CONFIG.SOURCES[source]?.name || source;
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">Loading articles...</span>
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 dark:text-gray-400">
          <Tag className="h-12 w-12 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No articles found</h3>
          <p>Try adjusting your search or source filter.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Articles
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {totalArticles} articles found
          </p>
        </div>
      </div>

      {/* Articles */}
      <div className="grid gap-4">
        {articles.map((article, index) => (
          <div
            key={`${article.url}-${index}`}
            className="card p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`source-badge ${getSourceColor(article.source)}`}>
                    {getSourceName(article.source)}
                  </span>
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <Calendar className="h-4 w-4 mr-1" />
                    {formatDate(article.date)}
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
                  {article.title}
                </h3>
                
                {article.originalTitle && article.originalTitle !== article.title && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2 italic">
                    Original: {article.originalTitle}
                  </p>
                )}
                
                <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                  {article.url}
                </p>
              </div>
              
              <button
                onClick={() => onArticleClick(article.url)}
                className="ml-4 flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm"
              >
                <ExternalLink className="h-4 w-4" />
                View
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-2">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
          >
            Previous
          </button>
          
          <div className="flex items-center space-x-1">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const page = i + 1;
              return (
                <button
                  key={page}
                  onClick={() => onPageChange(page)}
                  className={`px-3 py-2 text-sm font-medium rounded-lg ${
                    currentPage === page
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700'
                  }`}
                >
                  {page}
                </button>
              );
            })}
          </div>
          
          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
