// Shared types used across the Week 1 desktop foundation.

export type ResolutionOption = '480p' | '720p' | '1080p';
export type FpsOption = 24 | 30 | 60;

export interface GenerateVideoParams {
  audioPath: string;
  outputPath: string;
  resolution: ResolutionOption;
  fps: FpsOption;
  layers?: number;
  hiddenDim?: number;
}

export type AnalyzerKey = 'tempo' | 'key' | 'chords' | 'structure' | 'genre';

export interface AnalyzeParams {
  audioPath: string;
  analyzers: AnalyzerKey[];
}

export interface CommandResult<TData = unknown> {
  success: boolean;
  message: string;
  data?: TData;
}

export interface ProgressEvent {
  progress: number; // 0-100 percentage from backend
  message: string;
}

