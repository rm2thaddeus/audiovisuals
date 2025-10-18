import { useCallback, useEffect, useRef, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen, UnlistenFn } from '@tauri-apps/api/event';
import type { CommandResult, ProgressEvent } from '../types';

interface UsePythonCommandResult {
  runCommand: <T = unknown>(
    command: string,
    params?: Record<string, unknown>
  ) => Promise<CommandResult<T>>;
  isLoading: boolean;
  progress: number;
  error: string | null;
  reset: () => void;
}

/**
 * Small helper hook to invoke Tauri commands that wrap Python processes.
 * Subscribes to the shared `python-progress` event so the UI can display status.
 */
export function usePythonCommand(): UsePythonCommandResult {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const progressUnlistenRef = useRef<UnlistenFn | null>(null);

  const cleanupListener = useCallback(() => {
    if (progressUnlistenRef.current) {
      progressUnlistenRef.current();
      progressUnlistenRef.current = null;
    }
  }, []);

  useEffect(() => cleanupListener, [cleanupListener]);

  const reset = useCallback(() => {
    setIsLoading(false);
    setProgress(0);
    setError(null);
    cleanupListener();
  }, [cleanupListener]);

  const runCommand = useCallback(
    async <T,>(command: string, params: Record<string, unknown> = {}) => {
      try {
        setIsLoading(true);
        setError(null);
        setProgress(0);

        progressUnlistenRef.current = await listen<ProgressEvent>(
          'python-progress',
          (event) => setProgress(event.payload.progress)
        );

        const result = await invoke<CommandResult<T>>(command, params);
        return result;
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
        cleanupListener();
      }
    },
    [cleanupListener]
  );

  return { runCommand, isLoading, progress, error, reset };
}

