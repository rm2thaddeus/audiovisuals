import { useRef, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import type { AudioFile, FileValidationResult } from '../../types';

interface FileDropzoneProps {
  onFileSelected: (file: AudioFile) => void;
  onError?: (error: string) => void;
}

const ACCEPTED_FORMATS = ['.mp3', '.wav', '.flac', '.aiff', '.m4a'];
const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB

export function FileDropzone({ onFileSelected, onError }: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const validateFile = (file: File): { valid: boolean; error?: string } => {
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!ACCEPTED_FORMATS.includes(extension)) {
      return {
        valid: false,
        error: `Unsupported format. Accepted: ${ACCEPTED_FORMATS.join(', ')}`,
      };
    }

    if (file.size > MAX_FILE_SIZE) {
      return {
        valid: false,
        error: `File too large. Maximum size: ${formatFileSize(MAX_FILE_SIZE)}`,
      };
    }

    return { valid: true };
  };

  const handleFileSelect = async (file: File) => {
    setError(null);
    const validation = validateFile(file);

    if (!validation.valid) {
      const errorMsg = validation.error || 'Invalid file';
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    try {
      setIsLoading(true);

      // Validate with backend
      const backendValidation = await invoke<FileValidationResult>(
        'validate_audio_file',
        { path: (file as unknown as { path?: string }).path || file.name }
      );

      if (!backendValidation.valid) {
        const errorMsg = backendValidation.error || 'File validation failed';
        setError(errorMsg);
        onError?.(errorMsg);
        return;
      }

      // File accepted
      const audioFile: AudioFile = {
        path: (file as unknown as { path?: string }).path || file.name,
        name: file.name,
        size: file.size,
        format: file.name.split('.').pop()?.toLowerCase() || 'unknown',
      };

      onFileSelected(audioFile);
      setError(null);
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : 'Failed to validate file';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
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
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_FORMATS.join(',')}
          onChange={handleInputChange}
          className="hidden"
          disabled={isLoading}
        />

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
              <div>
                <p className="text-lg font-medium text-slate-200">
                  Drag your audio file here
                </p>
                <p className="text-sm text-slate-400 mt-1">
                  or{' '}
                  <button
                    type="button"
                    onClick={() => inputRef.current?.click()}
                    className="text-purple-400 hover:text-purple-300 underline"
                    disabled={isLoading}
                  >
                    browse files
                  </button>
                </p>
              </div>
              <p className="text-xs text-slate-500 mt-4">
                Supported formats: {ACCEPTED_FORMATS.join(', ')} (Max:{' '}
                {formatFileSize(MAX_FILE_SIZE)})
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
