import type { Generation } from '../../types';

interface GenerationListItemProps {
  generation: Generation;
  onPlay: (videoPath: string) => void;
  onDelete: (id: string) => void;
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

const formatDate = (isoString: string): string => {
  const date = new Date(isoString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

export function GenerationListItem({
  generation,
  onPlay,
  onDelete,
}: GenerationListItemProps) {
  return (
    <div className="flex items-center justify-between p-4 bg-slate-800 border border-slate-700 rounded-lg hover:border-slate-600 transition-colors">
      {/* Thumbnail & Info */}
      <div className="flex items-center gap-4 flex-1">
        {/* Thumbnail Placeholder */}
        <div className="w-16 h-16 bg-slate-900 rounded border border-slate-600 flex items-center justify-center flex-shrink-0">
          {generation.thumbnail ? (
            <img src={generation.thumbnail} alt={generation.filename} className="w-full h-full object-cover rounded" />
          ) : (
            <svg className="w-8 h-8 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          )}
        </div>

        {/* Text Info */}
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-slate-100 truncate">{generation.filename}</h4>
          <p className="text-xs text-slate-400 mt-1">{formatDate(generation.createdAt)}</p>

          {/* Settings & Size */}
          <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
            <span>{generation.settings.resolution}</span>
            <span>•</span>
            <span>{generation.settings.fps} fps</span>
            <span>•</span>
            <span>{formatFileSize(generation.fileSize)}</span>
            <span>•</span>
            <span className="text-slate-400">{generation.settings.styleName}</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 ml-4">
        {/* Play Button */}
        <button
          onClick={() => onPlay(generation.videoPath)}
          className="p-2 hover:bg-slate-700 rounded transition-colors"
          title="Play video"
        >
          <svg className="w-5 h-5 text-slate-300 hover:text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
        </button>

        {/* Copy Path Button */}
        <button
          onClick={() => navigator.clipboard.writeText(generation.videoPath)}
          className="p-2 hover:bg-slate-700 rounded transition-colors"
          title="Copy video path"
        >
          <svg className="w-5 h-5 text-slate-300 hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
        </button>

        {/* Delete Button */}
        <button
          onClick={() => {
            if (confirm(`Delete "${generation.filename}"?`)) {
              onDelete(generation.id);
            }
          }}
          className="p-2 hover:bg-red-900/30 rounded transition-colors"
          title="Delete generation"
        >
          <svg className="w-5 h-5 text-red-400 hover:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
