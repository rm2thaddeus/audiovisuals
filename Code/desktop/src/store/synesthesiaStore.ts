import { create } from 'zustand';
import type { 
  AudioFile, 
  AudioFileMetadata, 
  Style, 
  StyleInfo, 
  GenerationSettings,
  ProgressState,
  Generation 
} from '../types';

export interface SynesthesiaState {
  // Feature 1: File Selection
  selectedAudioFile: AudioFile | null;
  audioMetadata: AudioFileMetadata | null;
  isValidatingFile: boolean;
  fileError: string | null;

  // Feature 3: Style Selector
  selectedStyle: Style | null;
  availableStyles: StyleInfo[];
  isLoadingStyles: boolean;
  styleError: string | null;

  // Feature 4: Settings Panel
  generationSettings: GenerationSettings | null;

  // Feature 6: Progress Tracking
  generationProgress: ProgressState | null;
  isGenerating: boolean;
  generationError: string | null;

  // Feature 8: Recent Generations
  recentGenerations: Generation[];
  isLoadingGenerations: boolean;

  // Setters for Feature 1
  setSelectedAudioFile: (file: AudioFile | null) => void;
  setAudioMetadata: (metadata: AudioFileMetadata | null) => void;
  setIsValidatingFile: (validating: boolean) => void;
  setFileError: (error: string | null) => void;

  // Setters for Feature 3
  setSelectedStyle: (style: Style | null) => void;
  setAvailableStyles: (styles: StyleInfo[]) => void;
  setIsLoadingStyles: (loading: boolean) => void;
  setStyleError: (error: string | null) => void;

  // Setters for Feature 4
  setGenerationSettings: (settings: Partial<GenerationSettings>) => void;

  // Setters for Feature 6
  setGenerationProgress: (progress: ProgressState | null) => void;
  setIsGenerating: (generating: boolean) => void;
  setGenerationError: (error: string | null) => void;

  // Setters for Feature 8
  setRecentGenerations: (generations: Generation[]) => void;
  addGeneration: (generation: Generation) => void;
  removeGeneration: (id: string) => void;
  setIsLoadingGenerations: (loading: boolean) => void;

  // Utility methods
  reset: () => void;
}

const initialSettings: GenerationSettings = {
  resolution: '720p',
  fps: 30,
  quality: 80,
  audioPath: '',
  styleName: '',
};

export const useSynesthesiaStore = create<SynesthesiaState>((set) => ({
  // Initial states
  selectedAudioFile: null,
  audioMetadata: null,
  isValidatingFile: false,
  fileError: null,

  selectedStyle: null,
  availableStyles: [],
  isLoadingStyles: false,
  styleError: null,

  generationSettings: { ...initialSettings },
  generationProgress: null,
  isGenerating: false,
  generationError: null,

  recentGenerations: [],
  isLoadingGenerations: false,

  // Feature 1 Setters
  setSelectedAudioFile: (file) => set({ selectedAudioFile: file, fileError: null }),
  setAudioMetadata: (metadata) => set({ audioMetadata: metadata }),
  setIsValidatingFile: (validating) => set({ isValidatingFile: validating }),
  setFileError: (error) => set({ fileError: error }),

  // Feature 3 Setters
  setSelectedStyle: (style) => set({ selectedStyle: style, styleError: null }),
  setAvailableStyles: (styles) => set({ availableStyles: styles }),
  setIsLoadingStyles: (loading) => set({ isLoadingStyles: loading }),
  setStyleError: (error) => set({ styleError: error }),

  // Feature 4 Setters
  setGenerationSettings: (settings) =>
    set((state) => ({
      generationSettings: state.generationSettings
        ? { ...state.generationSettings, ...settings }
        : { ...initialSettings, ...settings },
    })),

  // Feature 6 Setters
  setGenerationProgress: (progress) => set({ generationProgress: progress }),
  setIsGenerating: (generating) => set({ isGenerating: generating }),
  setGenerationError: (error) => set({ generationError: error }),

  // Feature 8 Setters
  setRecentGenerations: (generations) => set({ recentGenerations: generations }),
  addGeneration: (generation) =>
    set((state) => ({
      recentGenerations: [generation, ...state.recentGenerations].slice(0, 20),
    })),
  removeGeneration: (id) =>
    set((state) => ({
      recentGenerations: state.recentGenerations.filter((g) => g.id !== id),
    })),
  setIsLoadingGenerations: (loading) => set({ isLoadingGenerations: loading }),

  // Utility
  reset: () =>
    set({
      selectedAudioFile: null,
      audioMetadata: null,
      selectedStyle: null,
      generationSettings: { ...initialSettings },
      generationProgress: null,
      isGenerating: false,
      generationError: null,
      fileError: null,
      styleError: null,
    }),
}));

