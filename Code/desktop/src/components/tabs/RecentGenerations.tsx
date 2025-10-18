import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useSynesthesiaStore } from '../../store/synesthesiaStore';
import { GenerationListItem } from '../common/GenerationListItem';
import { VideoPlayer } from '../common/VideoPlayer';
import type { Generation } from '../../types';

export function RecentGenerations() {
  const store = useSynesthesiaStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load generations on mount
  useEffect(() => {
    loadGenerations();
  }, []);

  const loadGenerations = async () => {
    try {
      setIsLoading(true);
      store.setIsLoadingGenerations(true);
      const recent = await invoke<Generation[]>('load_recent_generations');
      store.setRecentGenerations(recent);
    } catch (error) {
      console.error('Failed to load generations:', error);
    } finally {
      setIsLoading(false);
      store.setIsLoadingGenerations(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await invoke('delete_generation', { id });
      // Reload list
      await loadGenerations();
    } catch (error) {
      console.error('Failed to delete generation:', error);
    }
  };

  const handleClearAll = async () => {
    if (confirm('Delete all generations? This cannot be undone.')) {
      try {
        await invoke('clear_all_generations');
        await loadGenerations();
        setSelectedVideo(null);
      } catch (error) {
        console.error('Failed to clear generations:', error);
      }
    }
  };

  // Filter generations by search query
  const filteredGenerations = store.recentGenerations.filter((gen) =>
    gen.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-100">Recent Generations</h2>
        <p className="text-slate-400 mt-1">
          {store.recentGenerations.length} video{store.recentGenerations.length !== 1 ? 's' : ''} generated
        </p>
      </div>

      {/* Video Player (if selected) */}
      {selectedVideo && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-300">Video Preview</h3>
            <button
              onClick={() => setSelectedVideo(null)}
              className="text-xs text-slate-400 hover:text-slate-200 underline"
            >
              Close
            </button>
          </div>
          <VideoPlayer src={selectedVideo} height={400} />
        </div>
      )}

      {/* Search & Actions */}
      <div className="flex items-center gap-3">
        <input
          type="text"
          placeholder="Search videos..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
        <button
          onClick={loadGenerations}
          disabled={isLoading}
          className="px-4 py-2 text-slate-300 hover:text-slate-100 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors disabled:opacity-50"
          title="Refresh list"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-slate-600 border-t-slate-300 rounded-full animate-spin" />
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          )}
        </button>
        {store.recentGenerations.length > 0 && (
          <button
            onClick={handleClearAll}
            className="px-4 py-2 text-red-400 hover:text-red-300 bg-red-900/20 hover:bg-red-900/30 rounded-lg transition-colors"
            title="Delete all generations"
          >
            Clear All
          </button>
        )}
      </div>

      {/* List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-slate-600 border-t-purple-500 rounded-full animate-spin" />
        </div>
      ) : filteredGenerations.length === 0 ? (
        <div className="text-center py-12">
          <svg className="w-12 h-12 text-slate-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 001.591-.23m0 0A9.37 9.37 0 0012 3c-5.718 0-10.404 4.534-10.404 10.125 0 1.33.264 2.605.807 3.84m0 0a9.382 9.382 0 001.946 3.197m10.423-10.423a9.375 9.375 0 10-13.27 13.268"
            />
          </svg>
          <p className="text-slate-400">
            {searchQuery ? 'No videos match your search' : 'No videos generated yet'}
          </p>
          <p className="text-xs text-slate-500 mt-2">
            {searchQuery ? 'Try adjusting your search' : 'Generate your first video in the Synesthesia tab'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredGenerations.map((generation) => (
            <GenerationListItem
              key={generation.id}
              generation={generation}
              onPlay={setSelectedVideo}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Statistics */}
      {store.recentGenerations.length > 0 && (
        <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
          <h4 className="text-sm font-medium text-slate-300 mb-3">Statistics</h4>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-slate-500">Total Generated</p>
              <p className="text-lg font-semibold text-slate-100">{store.recentGenerations.length}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Most Used Style</p>
              <p className="text-lg font-semibold text-slate-100">
                {getMostUsedStyle(store.recentGenerations)}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Total Size</p>
              <p className="text-lg font-semibold text-slate-100">
                {getTotalSize(store.recentGenerations)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function getMostUsedStyle(generations: Generation[]): string {
  if (generations.length === 0) return 'N/A';

  const styleCounts = generations.reduce(
    (acc, gen) => {
      acc[gen.settings.styleName] = (acc[gen.settings.styleName] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const mostUsed = Object.entries(styleCounts).sort(([, a], [, b]) => b - a)[0];
  return mostUsed ? mostUsed[0] : 'N/A';
}

function getTotalSize(generations: Generation[]): string {
  const total = generations.reduce((sum, gen) => sum + gen.fileSize, 0);
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(total) / Math.log(k));
  return Math.round((total / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}
