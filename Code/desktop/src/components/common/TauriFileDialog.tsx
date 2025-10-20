import { useCallback, useState } from 'react';
import { open } from '@tauri-apps/plugin-dialog';
import { log } from '../../utils/logger';

interface TauriFileDialogProps {
  onPathSelected: (path: string) => Promise<void> | void;
  onError?: (error: string) => Promise<void> | void;
}

const AUDIO_FILTERS = [
  {
    name: 'Audio Files',
    extensions: ['mp3', 'wav', 'flac', 'aiff', 'm4a'],
  },
];

export function TauriFileDialog({ onPathSelected, onError }: TauriFileDialogProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleFileSelect = useCallback(async () => {
    try {
      setIsLoading(true);
      await log.userAction('file_dialog_open', 'TauriFileDialog');

      const selected = await open({
        multiple: false,
        filters: AUDIO_FILTERS,
      });

      const filePath = Array.isArray(selected) ? selected[0] : selected;

      if (!filePath) {
        await log.debug('File dialog closed without selection', {
          component: 'TauriFileDialog',
        });
        return;
      }

      await log.info('File selected via dialog', {
        component: 'TauriFileDialog',
        action: 'file_selected',
        metadata: { filePath },
      });

      await onPathSelected(filePath);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to open file dialog';

      await log.logError(error as Error, {
        component: 'TauriFileDialog',
        action: 'file_dialog_error',
      });

      await onError?.(message);
    } finally {
      setIsLoading(false);
    }
  }, [onPathSelected, onError]);

  return (
    <button
      onClick={handleFileSelect}
      disabled={isLoading}
      className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-medium rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
    >
      {isLoading ? (
        <div className="flex items-center justify-center gap-2">
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          Opening file dialog...
        </div>
      ) : (
        <div className="flex items-center justify-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Select Audio File
        </div>
      )}
    </button>
  );
}
