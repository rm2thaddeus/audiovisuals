import { useState, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { appDataDir, join } from '@tauri-apps/api/path';
import { useSynesthesiaStore } from '../store/synesthesiaStore';
import type { GenerateVideoResult, GenerationSettings } from '../types';

type VideoGenerationData = NonNullable<GenerateVideoResult['data']>;

export function useVideoGeneration() {
  const store = useSynesthesiaStore();
  const [, setUnlistenProgress] = useState<(() => void) | null>(null);

  const generateVideo = useCallback(
    async (
      audioPath: string,
      styleName: string,
      settings: GenerationSettings
    ): Promise<VideoGenerationData | null> => {
      try {
        // Validate inputs
        if (!audioPath) {
          throw new Error('Please select an audio file');
        }

        if (!styleName) {
          throw new Error('Please select a style');
        }

        if (!settings) {
          throw new Error('Settings not initialized');
        }

        const dataDir = await appDataDir();
        const generationsDir = await join(dataDir, 'generations');

        const timestamp = Date.now();
        const outputFilename = `${timestamp}_output.mp4`;
        const outputPath = await join(generationsDir, outputFilename);

        // Set generating state
        store.setIsGenerating(true);
        store.setGenerationError(null);
        store.setGenerationProgress({
          percentage: 0,
          phase: 'analyzing',
          elapsedTime: 0,
          estimatedTimeRemaining: 0,
        });

        // Listen for progress events from Python
        const unlisten = await listen<any>(
          'python-progress',
          (event) => {
            // Parse progress from the event
            const progress = event.payload.progress || 0;
            const message = event.payload.message || '';
            
            // Determine phase based on message
            let phase: 'analyzing' | 'rendering' | 'encoding' | 'complete' = 'analyzing';
            if (message.includes('Rendering')) phase = 'rendering';
            else if (message.includes('Encoding')) phase = 'encoding';
            
            store.setGenerationProgress({
              percentage: progress,
              phase,
              elapsedTime: 0,
              estimatedTimeRemaining: 0,
            });
          }
        );
        setUnlistenProgress(() => unlisten);

        // Invoke Rust command
        const response = await invoke<GenerateVideoResult>('generate_video', {
          params: {
            audio_path: audioPath,
            output_path: outputPath,
            style_name: styleName,
            resolution: settings.resolution,
            fps: settings.fps,
            quality: settings.quality,
            layers: settings.layers,
            hidden_dim: settings.hiddenDim,
          },
        });

        if (!response.success) {
          throw new Error(response.message);
        }

        // Mark progress as complete
        store.setGenerationProgress({
          percentage: 100,
          phase: 'complete',
          elapsedTime: 0,
          estimatedTimeRemaining: 0,
        });

        // Save to recent generations if data available
        if (response.data) {
          const generation = {
            id: `gen_${Date.now()}`,
            filename: audioPath.split(/[\\/]/).pop()?.replace(/\.[^/.]+$/, '.mp4') || 'output.mp4',
            audioPath,
            videoPath: response.data.videoPath,
            outputPath,
            settings,
            createdAt: new Date().toISOString(),
            duration: response.data.duration,
            fileSize: response.data.size,
            thumbnail: undefined,
          };

          try {
            await invoke('save_generation', { generation });
            // Reload recent generations
            const recent = await invoke<any>('load_recent_generations');
            store.setRecentGenerations(recent);
          } catch (err) {
            console.error('Failed to save generation:', err);
          }
        }

        return response.data || null;
      } catch (error) {
        const errorMsg =
          error instanceof Error ? error.message : 'Video generation failed';
        store.setGenerationError(errorMsg);
        store.setGenerationProgress(null);
        throw error;
      } finally {
        store.setIsGenerating(false);
        setUnlistenProgress((cleanup) => {
          if (cleanup) {
            cleanup();
          }
          return null;
        });
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
