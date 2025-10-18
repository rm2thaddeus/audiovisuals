import { useState, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';
import { useSynesthesiaStore } from '../store/synesthesiaStore';
import type { GenerateVideoResult, ProgressState } from '../types';

export function useVideoGeneration() {
  const store = useSynesthesiaStore();
  const [unlistenProgress, setUnlistenProgress] = useState<(() => void) | null>(null);

  const generateVideo = useCallback(
    async (outputPath: string): Promise<GenerateVideoResult> => {
      try {
        // Validate inputs
        if (!store.selectedAudioFile) {
          throw new Error('Please select an audio file');
        }

        if (!store.selectedStyle) {
          throw new Error('Please select a style');
        }

        if (!store.generationSettings) {
          throw new Error('Settings not initialized');
        }

        // Set generating state
        store.setIsGenerating(true);
        store.setGenerationError(null);
        store.setGenerationProgress(null);

        // Listen for progress events
        const unlisten = await listen<ProgressState>(
          'python-progress',
          (event) => {
            store.setGenerationProgress(event.payload);
          }
        );
        setUnlistenProgress(() => unlisten);

        // Invoke Rust command
        const result = await invoke<GenerateVideoResult>('generate_video', {
          audioPath: store.selectedAudioFile.path,
          outputPath,
          styleName: store.selectedStyle.name,
          resolution: store.generationSettings.resolution,
          fps: store.generationSettings.fps,
          quality: store.generationSettings.quality,
        });

        if (!result.success) {
          throw new Error(result.message);
        }

        // Mark progress as complete
        store.setGenerationProgress({
          percentage: 100,
          phase: 'complete',
          elapsedTime: 0,
          estimatedTimeRemaining: 0,
        });

        // Save to recent generations if data available
        if (result.data) {
          const generation = {
            id: '', // Will be generated in Rust
            filename: store.selectedAudioFile.name.replace(/\.[^/.]+$/, '.mp4'),
            audioPath: store.selectedAudioFile.path,
            videoPath: result.data.videoPath,
            outputPath,
            settings: store.generationSettings,
            createdAt: new Date().toISOString(),
            duration: result.data.duration,
            fileSize: result.data.size,
            thumbnail: undefined,
          };

          try {
            await invoke('save_generation', { generation });
            // Reload recent generations
            const recent = await invoke('load_recent_generations');
            store.setRecentGenerations(recent);
          } catch (err) {
            console.error('Failed to save generation:', err);
          }
        }

        return result;
      } catch (error) {
        const errorMsg =
          error instanceof Error ? error.message : 'Video generation failed';
        store.setGenerationError(errorMsg);
        store.setGenerationProgress(null);
        throw error;
      } finally {
        store.setIsGenerating(false);
        if (unlistenProgress) {
          unlistenProgress();
          setUnlistenProgress(null);
        }
      }
    },
    [store]
  );

  const cancelGeneration = useCallback(async () => {
    try {
      await invoke('cancel_video_generation');
      store.setIsGenerating(false);
      store.setGenerationProgress(null);
    } catch (error) {
      console.error('Failed to cancel generation:', error);
    }
  }, [store]);

  return {
    generateVideo,
    cancelGeneration,
    isGenerating: store.isGenerating,
    progress: store.generationProgress,
    error: store.generationError,
  };
}
