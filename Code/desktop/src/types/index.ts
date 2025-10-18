// Shared types used across the Week 1 desktop foundation.

export type ResolutionOption = '480p' | '720p' | '1080p';
export type FpsOption = 24 | 30 | 60;
export type AnalyzerKey = 'tempo' | 'key' | 'chords' | 'structure' | 'genre';

export interface GenerateVideoParams {
  audioPath: string;
  outputPath: string;
  resolution: ResolutionOption;
  fps: FpsOption;
  quality?: number;
}

export interface AnalyzeParams {
  audioPath: string;
  analyzers: AnalyzerKey[];
}

export interface CommandResult<T = unknown> {
  success: boolean;
  message: string;
  data?: T;
}

export interface ProgressEvent {
  progress: number;
  message: string;
}

// Feature 1: File Selection Types
export interface AudioFile {
  path: string;
  name: string;
  size: number;
  duration?: number;
  format: string;
}

export interface FileValidationResult {
  valid: boolean;
  error?: string;
}

export interface AudioFileMetadata {
  path: string;
  duration: number;
  bitrate: number;
  sampleRate: number;
}

// Feature 3: Style Selector Types
export interface Style {
  name: string;
  path: string;
  thumbnail?: string;
  parameters: {
    layers: number;
    hiddenDim: number;
    date: string;
  };
}

export interface StyleInfo {
  name: string;
  displayName: string;
  thumbnail: string;
  created: string;
}

export interface StyleDetails extends StyleInfo {
  parameters: Record<string, number>;
  description?: string;
}

// Feature 4: Settings Panel Types
export type Resolution = '480p' | '720p' | '1080p';
export type FPS = 24 | 30 | 60;

export interface GenerationSettings {
  resolution: Resolution;
  fps: FPS;
  quality: number;
  audioPath: string;
  styleName: string;
}

// Feature 5: Video Generation Types
export interface GenerateVideoResult extends CommandResult {
  data?: {
    videoPath: string;
    duration: number;
    size: number;
  };
}

// Feature 6: Progress Tracking Types
export interface ProgressState {
  percentage: number;
  phase: 'analyzing' | 'rendering' | 'encoding' | 'complete';
  elapsedTime: number;
  estimatedTimeRemaining: number;
  speed?: string;
}

export interface ProgressEventData {
  percentage: number;
  phase: 'analyzing' | 'rendering' | 'encoding' | 'complete';
  elapsedTime?: number;
  estimatedTimeRemaining?: number;
  speed?: string;
}

// Feature 7: Video Player Types
export interface VideoPlayerProps {
  src: string;
  autoplay?: boolean;
  controls?: boolean;
  width?: number;
  height?: number;
}

// Feature 8: Recent Generations Types
export interface Generation {
  id: string;
  filename: string;
  audioPath: string;
  videoPath: string;
  outputPath: string;
  settings: GenerationSettings;
  createdAt: string;
  duration: number;
  fileSize: number;
  thumbnail?: string;
}

export interface GenerationMetadata extends Omit<Generation, 'id'> {
  // For saving new generations
}

