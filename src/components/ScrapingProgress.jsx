import React from 'react';
import { X, CheckCircle, AlertCircle, Loader } from 'lucide-react';

export function ScrapingProgress({ progress, onStop }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Loader className="h-5 w-5 text-blue-500 animate-spin" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800';
      case 'error':
        return 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800';
      default:
        return 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800';
    }
  };

  const progressPercentage = progress.totalSources > 0 
    ? (progress.currentSourceIndex / progress.totalSources) * 100 
    : 0;

  return (
    <div className={`mb-6 p-4 rounded-lg border ${getStatusColor(progress.status)}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {getStatusIcon(progress.status)}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {progress.status === 'completed' ? 'Scraping Completed' : 
               progress.status === 'error' ? 'Scraping Error' : 
               'Scraping in Progress'}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {progress.message}
            </p>
          </div>
        </div>
        
        {progress.status === 'scraping' && (
          <button
            onClick={onStop}
            className="flex items-center gap-2 px-3 py-1 text-sm text-red-600 hover:text-red-700 bg-red-100 hover:bg-red-200 rounded-lg transition-colors"
          >
            <X className="h-4 w-4" />
            Stop
          </button>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span>Progress</span>
          <span>{progress.currentSourceIndex} / {progress.totalSources}</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Current Source */}
      {progress.currentSource && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Currently checking:
          </p>
          <p className="font-medium text-gray-900 dark:text-white">
            {progress.currentSource}
          </p>
        </div>
      )}

      {/* Completed Sources */}
      {progress.sourcesCompleted.length > 0 && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Completed sources:
          </p>
          <div className="flex flex-wrap gap-2">
            {progress.sourcesCompleted.map((source, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full dark:bg-green-900 dark:text-green-200"
              >
                <CheckCircle className="h-3 w-3" />
                {source}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Articles Count */}
      {progress.articlesScraped > 0 && (
        <div className="text-sm text-gray-600 dark:text-gray-400">
          <strong>{progress.articlesScraped}</strong> new articles found
        </div>
      )}
    </div>
  );
}
