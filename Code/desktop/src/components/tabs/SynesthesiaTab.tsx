import React, { useState, useEffect } from 'react';
import FileDropzone from '../common/FileDropzone';
import AudioInfoCard from '../common/AudioInfoCard';
import StyleSelector from '../common/StyleSelector';
import SettingsPanel from '../common/SettingsPanel';
import ProgressBar from '../common/ProgressBar';
import VideoPlayer from '../common/VideoPlayer';
import GenerationListItem from '../common/GenerationListItem';
import { useSynesthesiaStore } from '../../store/synesthesiaStore';
import { useVideoGeneration } from '../../hooks/useVideoGeneration';

export const SynesthesiaTab: React.FC = () => {
  const store = useSynesthesiaStore();
  const { generateVideo, isGenerating, error: generationError } = useVideoGeneration();
  
  const [generationComplete, setGenerationComplete] = useState(false);
  const [generatedVideoPath, setGeneratedVideoPath] = useState<string | null>(null);

  // Listen for generation completion
  useEffect(() => {
    if (store.generationProgress?.phase === 'complete') {
      setGenerationComplete(true);
      // Video path would be available in store after successful generation
    }
  }, [store.generationProgress]);

  const handleGenerate = async () => {
    if (!store.selectedAudioFile) {
      alert('Please select an audio file');
      return;
    }
    if (!store.selectedStyle) {
      alert('Please select a style');
      return;
    }

    try {
      setGenerationComplete(false);
      const result = await generateVideo(
        store.selectedAudioFile.path,
        store.selectedStyle.name,
        store.generationSettings
      );
      
      if (result) {
        setGeneratedVideoPath(result.videoPath);
      }
    } catch (err) {
      console.error('Generation failed:', err);
    }
  };

  return (
    <div className="flex flex-col gap-8 p-6 h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="border-b border-slate-700 pb-4">
        <h1 className="text-3xl font-bold text-white mb-2">Synesthesia Generator</h1>
        <p className="text-slate-400">Transform your audio into mesmerizing visuals</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1 overflow-hidden">
        {/* Left Panel: Configuration */}
        <div className="lg:col-span-2 flex flex-col gap-6 overflow-y-auto pr-2">
          {/* Feature 1: File Selection */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h2 className="text-lg font-semibold text-white mb-4">1. Select Audio</h2>
            <FileDropzone />
          </div>

          {/* Feature 2: Audio Info */}
          {store.selectedAudioFile && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-semibold text-white mb-4">2. Audio Details</h2>
              <AudioInfoCard file={store.selectedAudioFile} />
            </div>
          )}

          {/* Feature 3: Style Selection */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h2 className="text-lg font-semibold text-white mb-4">3. Choose Style</h2>
            <StyleSelector />
          </div>

          {/* Feature 4: Settings */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h2 className="text-lg font-semibold text-white mb-4">4. Settings</h2>
            <SettingsPanel />
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={!store.selectedAudioFile || !store.selectedStyle || isGenerating}
            className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
          >
            {isGenerating ? 'Generating...' : 'Generate Video'}
          </button>

          {generationError && (
            <div className="bg-red-900/30 border border-red-600 rounded-lg p-4">
              <p className="text-red-400 text-sm"><strong>Error:</strong> {generationError}</p>
            </div>
          )}
        </div>

        {/* Right Panel: Progress & Preview */}
        <div className="lg:col-span-1 flex flex-col gap-6 overflow-y-auto">
          {/* Feature 6: Progress */}
          {isGenerating && store.generationProgress && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-semibold text-white mb-4">Generation Progress</h2>
              <ProgressBar
                percentage={store.generationProgress.percentage}
                phase={store.generationProgress.phase}
                animated
              />
              <div className="mt-4 text-sm text-slate-400 space-y-2">
                <p>Phase: <span className="text-purple-400 font-semibold">{store.generationProgress.phase}</span></p>
                <p>Progress: <span className="text-purple-400 font-semibold">{store.generationProgress.percentage}%</span></p>
              </div>
            </div>
          )}

          {/* Feature 7: Video Preview */}
          {generatedVideoPath && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-semibold text-white mb-4">Preview</h2>
              <VideoPlayer src={generatedVideoPath} controls autoplay={false} />
            </div>
          )}

          {/* Feature 8: Recent Generations */}
          {store.recentGenerations.length > 0 && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-semibold text-white mb-4">Recent</h2>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {store.recentGenerations.slice(0, 3).map((gen) => (
                  <GenerationListItem
                    key={gen.id}
                    generation={gen}
                    onPlay={() => setGeneratedVideoPath(gen.videoPath)}
                    onDelete={() => store.removeGeneration(gen.id)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
