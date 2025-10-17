import { useCallback, useState } from 'react';
import { useAppStore } from '../store/appStore';
import { usePythonCommand } from '../hooks/usePythonCommand';
import type { CommandResult } from '../types';

export function TestIntegration() {
  const { runCommand, isLoading, progress, error, reset } = usePythonCommand();
  const { setError } = useAppStore();
  const [result, setResult] = useState<CommandResult | null>(null);

  const handleTest = useCallback(async () => {
    try {
      reset();
      setResult(null);
      const outcome = await runCommand('test_python');
      setResult(outcome);
      setError(outcome.success ? null : outcome.message);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
    }
  }, [reset, runCommand, setError]);

  return (
    <div className="space-y-4 rounded border border-slate-700 bg-slate-800 p-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-100">Integration Harness</h3>
        {isLoading && <span className="text-xs text-slate-400">Running... {Math.round(progress)}%</span>}
      </div>

      <button
        onClick={handleTest}
        disabled={isLoading}
        className="rounded bg-purple-600 px-4 py-2 text-sm font-medium transition-colors hover:bg-purple-700 disabled:opacity-50"
      >
        {isLoading ? 'Testing...' : 'Test Python Integration'}
      </button>

      {error && (
        <div className="rounded border border-red-700 bg-red-950 p-3 text-sm text-red-100">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-1 rounded border border-emerald-700 bg-emerald-950 p-3 text-sm text-emerald-100">
          <p>
            <span className="font-semibold">Success:</span> {result.success ? 'Yes' : 'No'}
          </p>
          <p>
            <span className="font-semibold">Message:</span> {result.message}
          </p>
        </div>
      )}
    </div>
  );
}

