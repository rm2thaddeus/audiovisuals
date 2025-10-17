import * as Tabs from '@radix-ui/react-tabs';
import { SynesthesiaTab } from './components/tabs/SynesthesiaTab';
import { AnalysisTab } from './components/tabs/AnalysisTab';
import { StylesTab } from './components/tabs/StylesTab';
import { ExplorerTab } from './components/tabs/ExplorerTab';
import { ProjectsTab } from './components/tabs/ProjectsTab';
import { TestIntegration } from './components/TestIntegration';
import { useAppStore, AppTab } from './store/appStore';
import './App.css';

function App() {
  const { activeTab, setActiveTab, error, setError } = useAppStore();

  return (
    <div className="flex h-screen flex-col bg-slate-900 text-slate-100">
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4 shadow-lg">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          Audio Feature Explorer
        </h1>
        <p className="mt-1 text-sm text-slate-400">ML-powered audio-reactive visualizations</p>
      </header>

      <Tabs.Root
        value={activeTab}
        onValueChange={(value) => setActiveTab(value as AppTab)}
        className="flex flex-1 flex-col"
      >
        <Tabs.List className="flex gap-1 bg-slate-800 border-b border-slate-700 px-6">
          {[
            { value: 'synesthesia', label: 'Synesthesia' },
            { value: 'analysis', label: 'Analysis' },
            { value: 'styles', label: 'Styles' },
            { value: 'explorer', label: 'Explorer' },
            { value: 'projects', label: 'Projects' },
          ].map(({ value, label }) => (
            <Tabs.Trigger
              key={value}
              value={value}
              className={`border-b-2 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === value
                  ? 'border-purple-500 text-purple-300'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <div className="flex-1 overflow-auto bg-slate-900">
          <Tabs.Content value="synesthesia" className="h-full p-6">
            <SynesthesiaTab />
            <div className="mt-6">
              <TestIntegration />
            </div>
          </Tabs.Content>

          <Tabs.Content value="analysis" className="h-full p-6">
            <AnalysisTab />
          </Tabs.Content>

          <Tabs.Content value="styles" className="h-full p-6">
            <StylesTab />
          </Tabs.Content>

          <Tabs.Content value="explorer" className="h-full p-6">
            <ExplorerTab />
          </Tabs.Content>

          <Tabs.Content value="projects" className="h-full p-6">
            <ProjectsTab />
          </Tabs.Content>
        </div>
      </Tabs.Root>

      <footer className="bg-slate-800 border-t border-slate-700 px-6 py-3 text-xs text-slate-400">
        <div className="flex items-center justify-between">
          <p>Phase 3 MVP - Week 1 Foundation</p>
          {error && (
            <button onClick={() => setError(null)} className="text-rose-300 hover:text-rose-200 transition-colors">
              Clear error
            </button>
          )}
        </div>
        {error && <p className="mt-1 text-rose-300">{error}</p>}
      </footer>
    </div>
  );
}

export default App;
