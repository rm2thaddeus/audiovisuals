import type { AudioFile, AudioFileMetadata } from '../../types';

interface AudioInfoCardProps {
  audioFile: AudioFile | null;
  metadata: AudioFileMetadata | null;
  isLoading?: boolean;
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

const formatDuration = (seconds: number | undefined): string => {
  if (!seconds) return '0:00';
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

export function AudioInfoCard({
  audioFile,
  metadata,
  isLoading,
}: AudioInfoCardProps) {
  if (!audioFile) {
    return (
      <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-lg text-slate-400 text-center">
        No audio file selected
      </div>
    );
  }

  return (
    <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
      <div className="space-y-3">
        {/* File Name */}
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wide">File Name</p>
          <p className="text-slate-100 font-medium truncate">{audioFile.name}</p>
        </div>

        {/* Format & Size */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wide">Format</p>
            <p className="text-slate-100 font-medium">
              {audioFile.format.toUpperCase()}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wide">File Size</p>
            <p className="text-slate-100 font-medium">
              {formatFileSize(audioFile.size)}
            </p>
          </div>
        </div>

        {/* Metadata (if available) */}
        {metadata || isLoading ? (
          <div className="grid grid-cols-3 gap-4 pt-2 border-t border-slate-700">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">Duration</p>
              {isLoading ? (
                <div className="h-5 bg-slate-700 rounded animate-pulse mt-1" />
              ) : (
                <p className="text-slate-100 font-medium">
                  {formatDuration(metadata?.duration)}
                </p>
              )}
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">Bitrate</p>
              {isLoading ? (
                <div className="h-5 bg-slate-700 rounded animate-pulse mt-1" />
              ) : (
                <p className="text-slate-100 font-medium">
                  {metadata?.bitrate ? `${metadata.bitrate} kb/s` : 'N/A'}
                </p>
              )}
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">Sample Rate</p>
              {isLoading ? (
                <div className="h-5 bg-slate-700 rounded animate-pulse mt-1" />
              ) : (
                <p className="text-slate-100 font-medium">
                  {metadata?.sampleRate ? `${metadata.sampleRate} Hz` : 'N/A'}
                </p>
              )}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

