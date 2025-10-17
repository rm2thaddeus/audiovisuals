import { useState } from 'react';
import * as Tabs from '@radix-ui/react-tabs';
import { SynesthesiaTab } from './components/tabs/SynesthesiaTab';
import { AnalysisTab } from './components/tabs/AnalysisTab';
import { StylesTab } from './components/tabs/StylesTab';
import { ExplorerTab } from './components/tabs/ExplorerTab';
import { ProjectsTab } from './components/tabs/ProjectsTab';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState<'synesthesia' | 'analysis' | 'styles' | 'explorer' | 'projects'>('synesthesia');

  return (
    <div className="h-screen bg-slate-900 text-slate-100 flex flex-col">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4 shadow-lg">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          🎨 Audio Feature Explorer
        </h1>
        <p className="text-sm text-slate-400 mt-1">ML-powered audio-reactive visualizations</p>
      </header>

      {/* Tabs */}
      <Tabs.Root
        value={activeTab}
        onValueChange={(value) => setActiveTab(value as any)}
        className="flex-1 flex flex-col"
      >
        {/* Tab List */}
        <Tabs.List className="bg-slate-800 border-b border-slate-700 flex px-6 gap-1">
          <Tabs.Trigger
            value="synesthesia"
            className={`py-3 px-4 font-medium text-sm transition-colors border-b-2 ${
              activeTab === 'synesthesia'
                ? 'border-purple-500 text-purple-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            🎨 Synesthesia
          </Tabs.Trigger>

          <Tabs.Trigger
            value="analysis"
            className={`py-3 px-4 font-medium text-sm transition-colors border-b-2 ${
              activeTab === 'analysis'
                ? 'border-purple-500 text-purple-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            🎵 Analysis
          </Tabs.Trigger>

          <Tabs.Trigger
            value="styles"
            className={`py-3 px-4 font-medium text-sm transition-colors border-b-2 ${
              activeTab === 'styles'
                ? 'border-purple-500 text-purple-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            🎭 Styles
          </Tabs.Trigger>

          <Tabs.Trigger
            value="explorer"
            className={`py-3 px-4 font-medium text-sm transition-colors border-b-2 ${
              activeTab === 'explorer'
                ? 'border-purple-500 text-purple-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            🔬 Explorer
          </Tabs.Trigger>

          <Tabs.Trigger
            value="projects"
            className={`py-3 px-4 font-medium text-sm transition-colors border-b-2 ${
              activeTab === 'projects'
                ? 'border-purple-500 text-purple-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            📁 Projects
          </Tabs.Trigger>
        </Tabs.List>

        {/* Tab Content */}
        <div className="flex-1 overflow-auto">
          <Tabs.Content value="synesthesia" className="p-6 h-full">
            <SynesthesiaTab />
          </Tabs.Content>

          <Tabs.Content value="analysis" className="p-6 h-full">
            <AnalysisTab />
          </Tabs.Content>

          <Tabs.Content value="styles" className="p-6 h-full">
            <StylesTab />
          </Tabs.Content>

          <Tabs.Content value="explorer" className="p-6 h-full">
            <ExplorerTab />
          </Tabs.Content>

          <Tabs.Content value="projects" className="p-6 h-full">
            <ProjectsTab />
          </Tabs.Content>
        </div>
      </Tabs.Root>

      {/* Footer */}
      <footer className="bg-slate-800 border-t border-slate-700 px-6 py-3 text-xs text-slate-500">
        <p>Phase 3 MVP • Week 1 Foundation</p>
      </footer>
    </div>
  );
}

export default App;

