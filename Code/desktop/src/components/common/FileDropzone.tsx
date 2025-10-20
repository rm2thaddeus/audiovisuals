import { useCallback, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { log } from '../../utils/logger';
import { TauriFileDialog } from './TauriFileDialog';
import type {
  AudioFile,
  AudioFileMetadata,
  FileValidationResult,
} from '../../types';

interface FileDropzoneProps {
  onFileSelected: (file: AudioFile) => void;
  onMetadataLoaded?: (metadata: AudioFileMetadata) => void;
  onError?: (error: string) => void;
}

const ACCEPTED_FORMATS = ['.mp3', '.wav', '.flac', '.aiff', '.m4a'];
const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB

const formatFileSize = (bytes: number): string => {
  if (!bytes) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(k)), sizes.length - 1);
  return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`;
};

const getFileName = (path: string): string => path.split(/[\\/]/).pop() || path;

const getExtensionFromPath = (path: string): string =>
  `.${getFileName(path).split('.').pop()?.toLowerCase() ?? ''}`;

export function FileDropzone({
  onFileSelected,
  onMetadataLoaded,
  onError,
}: FileDropzoneProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const emitError = useCallback(async (message: string) => {
    setError(message);
    onError?.(message);
    await log.error(message, {
      component: 'FileDropzone',
      action: 'file_error',
    });
  }, [onError]);

  const validateFrontendConstraints = (size?: number, extension?: string): string | null => {
    if (extension && !ACCEPTED_FORMATS.includes(extension)) {
      return `Unsupported format. Accepted: ${ACCEPTED_FORMATS.join(', ')}`;
    }
    if (size && size > MAX_FILE_SIZE) {
      return `File too large. Maximum size: ${formatFileSize(MAX_FILE_SIZE)}`;
    }
    return null;
  };

  const handleValidatedSelection = async (
    filePath: string,
    options: { sizeHint?: number; nameHint?: string } = {},
  ) => {
    setError(null);
    setIsLoading(true);

    try {
      const validation = await invoke<FileValidationResult>('validate_audio_file', {
        path: filePath,
      });

      if (!validation.valid) {
        const backendError = validation.error || 'File validation failed';
        await emitError(backendError);
        return;
      }

      const canonicalPath = validation.canonicalPath || filePath;
      const metadata = await invoke<AudioFileMetadata>('get_file_metadata', {
        path: canonicalPath,
      });

      const audioFile: AudioFile = {
        path: metadata.path,
        name: options.nameHint ?? getFileName(metadata.path),
        size: metadata.fileSize ?? options.sizeHint ?? 0,
        duration: metadata.duration,
        format: metadata.format || getExtensionFromPath(metadata.path).slice(1),
        bitrate: metadata.bitrate,
        sampleRate: metadata.sampleRate,
        channels: metadata.channels,
      };

      onMetadataLoaded?.(metadata);
      onFileSelected(audioFile);

      await log.info('File selected successfully', {
        component: 'FileDropzone',
        action: 'file_selected',
        metadata: {
          path: audioFile.path,
          name: audioFile.name,
          size: audioFile.size,
          format: audioFile.format,
        },
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to process file';
      await log.logError(err as Error, {
        component: 'FileDropzone',
        action: 'file_validation_error',
        metadata: { path: filePath },
      });
      await emitError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDialogSelection = useCallback(
    async (path: string) => {
      await log.userAction('file_select_attempt', 'FileDropzone', { filePath: path });

      const extension = getExtensionFromPath(path);
      const frontError = validateFrontendConstraints(undefined, extension);
      if (frontError) {
        await emitError(frontError);
        return;
      }

      await handleValidatedSelection(path, { nameHint: getFileName(path) });
    },
    [emitError],
  );

  const handleDrop = useCallback(
    async (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      event.stopPropagation();
      setIsDragActive(false);

      const files = event.dataTransfer.files;
      if (!files || files.length === 0) {
        return;
      }

      const file = files[0];
      const droppedPath = (file as unknown as { path?: string }).path;

      if (!droppedPath) {
        await emitError('Drag-and-drop path not available. Please use Select Audio File.');
        return;
      }

      await log.userAction('file_drag_drop', 'FileDropzone', {
        filePath: droppedPath,
        fileSize: file.size,
      });

      const extension = getExtensionFromPath(droppedPath);
      const frontError = validateFrontendConstraints(file.size, extension);
      if (frontError) {
        await emitError(frontError);
        return;
      }

      await handleValidatedSelection(droppedPath, {
        sizeHint: file.size,
        nameHint: file.name,
      });
    },
    [emitError],
  );

  const handleDrag = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();

    if (event.type === 'dragenter' || event.type === 'dragover') {
      setIsDragActive(true);
    } else if (event.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  return (
    <div className="w-full">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          isDragActive
            ? 'border-purple-500 bg-purple-500/10'
            : 'border-slate-600 bg-slate-800/50 hover:border-purple-400'
        } ${isLoading ? 'opacity-50 pointer-events-none' : ''}`}
      >
        <div className="flex flex-col items-center gap-3">
          {isLoading ? (
            <>
              <div className="w-8 h-8 border-4 border-slate-600 border-t-purple-500 rounded-full animate-spin" />
              <p className="text-slate-400">Validating audio file...</p>
            </>
          ) : (
            <>
              <svg
                className="w-12 h-12 text-slate-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M12 18.75a6 6 0 006-6v-1.5m0-6a6 6 0 00-6 6v1.5m0 0a6 6 0 01-6-6v-1.5m0 6a6 6 0 006 6v1.5"
                />
              </svg>
              <div className="text-slate-200">
                <p className="text-lg font-medium">Drag your audio file here</p>
                <p className="text-sm text-slate-400 mt-1">or use the button below</p>
              </div>

              <div className="mt-4 w-full">
                <TauriFileDialog onPathSelected={handleDialogSelection} onError={emitError} />
              </div>
              <p className="text-xs text-slate-500 mt-4">
                Supported formats: {ACCEPTED_FORMATS.join(', ')} (Max: {formatFileSize(MAX_FILE_SIZE)})
              </p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-900/50 border border-red-700 rounded text-red-200 text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
