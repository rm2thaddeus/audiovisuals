interface ProgressBarProps {
  percentage: number;
  phase?: 'analyzing' | 'rendering' | 'encoding' | 'complete';
  showLabel?: boolean;
  animated?: boolean;
}

const phaseLabels = {
  analyzing: 'Analyzing audio...',
  rendering: 'Rendering frames...',
  encoding: 'Encoding video...',
  complete: 'Complete!',
};

const phaseColors = {
  analyzing: 'from-blue-500 to-blue-600',
  rendering: 'from-purple-500 to-purple-600',
  encoding: 'from-amber-500 to-amber-600',
  complete: 'from-green-500 to-green-600',
};

export function ProgressBar({
  percentage,
  phase = 'analyzing',
  showLabel = true,
  animated = true,
}: ProgressBarProps) {
  // Clamp percentage between 0 and 100
  const clampedPercentage = Math.max(0, Math.min(100, percentage));

  return (
    <div className="w-full space-y-2">
      {/* Label */}
      {showLabel && (
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-slate-300">
            {phaseLabels[phase]}
          </p>
          <p className="text-sm font-semibold text-slate-200">
            {clampedPercentage}%
          </p>
        </div>
      )}

      {/* Progress Bar Background */}
      <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
        {/* Progress Fill */}
        <div
          className={`h-full bg-gradient-to-r ${phaseColors[phase]} transition-all ${
            animated ? 'duration-500' : 'duration-0'
          } ease-out`}
          style={{ width: `${clampedPercentage}%` }}
        >
          {/* Animated shimmer effect */}
          {animated && clampedPercentage < 100 && (
            <div className="h-full w-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
          )}
        </div>
      </div>

      {/* Optional: Percentage text below */}
      {!showLabel && (
        <p className="text-xs text-slate-500 text-right">{clampedPercentage}%</p>
      )}
    </div>
  );
}

