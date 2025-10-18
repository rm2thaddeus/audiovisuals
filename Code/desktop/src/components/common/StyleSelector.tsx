import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import type { StyleInfo } from '../../types';

interface StyleSelectorProps {
  selectedStyle: StyleInfo | null;
  onStyleSelect: (style: StyleInfo) => void;
  onError?: (error: string) => void;
}

export function StyleSelector({
  selectedStyle,
  onStyleSelect,
  onError,
}: StyleSelectorProps) {
  const [styles, setStyles] = useState<StyleInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadStyles();
  }, []);

  const loadStyles = async () => {
    try {
      setIsLoading(true);
      const result = await invoke<StyleInfo[]>('list_styles');
      setStyles(result);
    } catch (error) {
      const errorMsg =
        error instanceof Error ? error.message : 'Failed to load styles';
      onError?.(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredStyles = styles.filter((style) =>
    style.display_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-slate-300 mb-2">
        Visual Style
      </label>

      <div className="relative">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          disabled={isLoading}
          className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-100 rounded-lg border border-slate-600 text-left flex items-center justify-between disabled:opacity-50"
        >
          <span>
            {isLoading
              ? 'Loading styles...'
              : selectedStyle?.display_name || 'Select a style'}
          </span>
          <svg
            className={`w-5 h-5 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
        </button>

        {isOpen && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-slate-700 border border-slate-600 rounded-lg shadow-lg z-10">
            {/* Search input */}
            <input
              type="text"
              placeholder="Search styles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 bg-slate-800 border-b border-slate-600 text-slate-100 placeholder-slate-500 rounded-t-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />

            {/* Style list */}
            <div className="max-h-60 overflow-y-auto">
              {filteredStyles.length === 0 ? (
                <div className="px-4 py-2 text-slate-400 text-center">
                  No styles found
                </div>
              ) : (
                filteredStyles.map((style) => (
                  <button
                    key={style.name}
                    type="button"
                    onClick={() => {
                      onStyleSelect(style);
                      setIsOpen(false);
                      setSearchQuery('');
                    }}
                    className={`w-full text-left px-4 py-3 border-b border-slate-600 last:border-b-0 transition-colors ${
                      selectedStyle?.name === style.name
                        ? 'bg-purple-600/20 text-purple-200'
                        : 'hover:bg-slate-600 text-slate-100'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{style.display_name}</p>
                        <p className="text-xs text-slate-400 mt-1">
                          Created: {style.created}
                        </p>
                      </div>
                      {selectedStyle?.name === style.name && (
                        <svg
                          className="w-5 h-5 text-purple-400"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                    </div>
                  </button>
                ))
              )}
            </div>

            {/* Reload button */}
            <button
              type="button"
              onClick={loadStyles}
              className="w-full px-4 py-2 text-slate-400 hover:text-slate-200 text-sm border-t border-slate-600 rounded-b-lg hover:bg-slate-600/50 transition-colors"
            >
              Reload Styles
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

