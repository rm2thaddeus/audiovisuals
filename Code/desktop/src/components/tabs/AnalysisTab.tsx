/**
 * Analysis Tab - Music Semantic Analysis
 *
 * Week 5-6 implementation target.
 */

export function AnalysisTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Music Analysis</h2>

      <div className="rounded-lg border border-slate-700 bg-slate-800 p-6">
        <p className="text-slate-400">
          Coming in Week 5-6: Extract semantic features from music using five specialized analyzers.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
        {['Tempo', 'Key', 'Chords', 'Structure', 'Genre'].map((analyzer) => (
          <div key={analyzer} className="rounded border border-slate-700 bg-slate-800 p-3">
            <p className="text-sm font-medium">{analyzer}</p>
            <p className="mt-1 text-xs text-slate-400">Coming soon...</p>
          </div>
        ))}
      </div>
    </div>
  );
}

