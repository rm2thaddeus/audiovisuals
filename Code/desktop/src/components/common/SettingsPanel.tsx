import type { Resolution, FPS } from '../../types';

interface SettingsPanelProps {
  resolution: Resolution;
  fps: FPS;
  quality: number;
  onResolutionChange: (res: Resolution) => void;
  onFpsChange: (fps: FPS) => void;
  onQualityChange: (quality: number) => void;
  onReset: () => void;
}

const RESOLUTIONS: Resolution[] = ['480p', '720p', '1080p'];
const FPS_OPTIONS: FPS[] = [24, 30, 60];

const estimateRenderTime = (
  durationSeconds: number,
  resolution: Resolution,
  fps: FPS,
  quality: number
): number => {
  // Rough estimation based on typical generation speeds
  // 720p30fps: 1x realtime (1 sec video = 1 sec render)
  // 1080p60fps: 4x realtime
  // 480p24fps: 0.25x realtime
  
  const resolutionFactor = {
    '480p': 0.25,
    '720p': 1,
    '1080p': 2.5,
  };

  const fpsFactor = fps / 30;
  const qualityFactor = 1 + (quality - 50) / 200; // Higher quality = slower

  const speedFactor = resolutionFactor[resolution] * fpsFactor * qualityFactor;
  return Math.ceil((durationSeconds * speedFactor) / 60); // Return in minutes
};

export function SettingsPanel({
  resolution,
  fps,
  quality,
  onResolutionChange,
  onFpsChange,
  onQualityChange,
  onReset,
}: SettingsPanelProps) {
  // Estimate render time (assuming 3-minute track = 180 seconds)
  const estimatedMinutes = estimateRenderTime(180, resolution, fps, quality);

  return (
    <div className="space-y-6 p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
      <div>
        <h3 className="text-sm font-semibold text-slate-200 mb-4">
          Generation Settings
        </h3>
      </div>

      {/* Resolution Selector */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-3">
          Resolution
        </label>
        <div className="grid grid-cols-3 gap-2">
          {RESOLUTIONS.map((res) => (
            <button
              key={res}
              type="button"
              onClick={() => onResolutionChange(res)}
              className={`py-2 px-3 rounded-lg font-medium transition-colors ${
                resolution === res
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {res}
            </button>
          ))}
        </div>
      </div>

      {/* FPS Selector */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-3">
          Frame Rate
        </label>
        <div className="grid grid-cols-3 gap-2">
          {FPS_OPTIONS.map((f) => (
            <button
              key={f}
              type="button"
              onClick={() => onFpsChange(f as FPS)}
              className={`py-2 px-3 rounded-lg font-medium transition-colors ${
                fps === f
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {f} fps
            </button>
          ))}
        </div>
      </div>

      {/* Quality Slider */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <label className="text-sm font-medium text-slate-300">Quality</label>
          <span className="text-sm text-slate-400">{quality}%</span>
        </div>
        <input
          type="range"
          min="0"
          max="100"
          value={quality}
          onChange={(e) => onQualityChange(parseInt(e.target.value))}
          className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
        />
        <div className="flex justify-between text-xs text-slate-500 mt-1">
          <span>Low (fast)</span>
          <span>High (slow)</span>
        </div>
      </div>

      {/* Estimated Render Time */}
      <div className="pt-4 border-t border-slate-700">
        <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
          <span className="text-sm text-slate-400">
            Est. render time (3 min audio):
          </span>
          <span className="text-lg font-semibold text-purple-400">
            {estimatedMinutes} min
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-2">
          Actual time depends on your system. GPU acceleration enabled.
        </p>
      </div>

      {/* Reset Button */}
      <button
        type="button"
        onClick={onReset}
        className="w-full py-2 px-4 text-sm font-medium text-slate-300 hover:text-slate-100 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
      >
        Reset to Defaults
      </button>
    </div>
  );
}

