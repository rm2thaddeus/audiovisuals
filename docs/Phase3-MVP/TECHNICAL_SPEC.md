# Phase 3 MVP - Technical Specification

**Date:** 2025-10-13  
**Status:** 📐 Planning  
**Architecture:** Tauri 2.0 Desktop Application

---

## Technology Stack

### Frontend Layer

**Framework:** React 18.2+
- TypeScript 5.0+ for type safety
- Functional components with hooks
- Vite for build tooling (fast HMR)

**Styling:** Tailwind CSS 3.4+
- Custom theme with dark mode
- Component-based utility classes
- Responsive design system

**State Management:** Zustand 4.4+
- Lightweight (<1KB)
- Simple API
- DevTools support

**UI Components:**
- Radix UI primitives (accessible)
- Custom components for domain-specific needs
- Framer Motion for animations

**Data Visualization:**
- Plotly.js for interactive charts
- React-Plotly.js wrapper
- Custom chart components

**Video:** Video.js 8.0+
- HTML5 video player
- Custom controls
- Thumbnail generation

### Backend Layer

**Framework:** Tauri 2.0
- Rust 1.75+ 
- Multi-window support
- System tray integration

**Python Integration:**
- Process spawning via Rust std::process
- STDOUT/STDERR streaming
- Graceful shutdown

**File System:**
- Tauri FS API (sandboxed)
- Native file dialogs
- Watch for file changes

**IPC (Inter-Process Communication):**
- Tauri's invoke/emit system
- Type-safe commands
- Event streaming

### Python Backend (Existing)

**Reuse all existing CLI tools:**
- `cli.py` - CPPN generation
- `music_analysis/*` - 5 analyzers
- `clip_optimize_cppn.py` - Style training
- `tools/*` - Parameter exploration

**No changes needed** - Wrapper layer handles integration

---

## Project Structure

```
audiovisuals-desktop/
├── src-tauri/           # Rust backend
│   ├── src/
│   │   ├── main.rs      # App entry point
│   │   ├── python.rs    # Python CLI wrapper
│   │   ├── commands.rs  # Tauri commands
│   │   ├── events.rs    # Event emitters
│   │   └── lib.rs       # Library exports
│   ├── Cargo.toml       # Rust dependencies
│   ├── tauri.conf.json  # Tauri configuration
│   └── icons/           # App icons
│
├── src/                 # React frontend
│   ├── components/      # UI components
│   │   ├── tabs/
│   │   │   ├── SynesthesiaTab.tsx
│   │   │   ├── AnalysisTab.tsx
│   │   │   ├── StylesTab.tsx
│   │   │   ├── ExplorerTab.tsx
│   │   │   └── ProjectsTab.tsx
│   │   ├── common/
│   │   │   ├── FileDropzone.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   ├── VideoPlayer.tsx
│   │   │   └── ...
│   │   └── charts/
│   │       ├── TempoChart.tsx
│   │       ├── ChordChart.tsx
│   │       └── ...
│   ├── store/           # Zustand stores
│   │   ├── appStore.ts
│   │   ├── synesthesiaStore.ts
│   │   ├── analysisStore.ts
│   │   └── stylesStore.ts
│   ├── hooks/           # Custom hooks
│   │   ├── usePythonCommand.ts
│   │   ├── useVideoGeneration.ts
│   │   └── useFileWatcher.ts
│   ├── types/           # TypeScript types
│   │   ├── music.ts
│   │   ├── styles.ts
│   │   └── generation.ts
│   ├── utils/           # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── parsers.ts
│   ├── App.tsx          # Root component
│   ├── main.tsx         # Entry point
│   └── styles/          # Global styles
│
├── Code/backend/        # Existing Python code
│   └── [No changes needed]
│
├── public/              # Static assets
│   ├── styles/          # Bundled style previews
│   └── examples/        # Sample files
│
├── package.json         # Node dependencies
├── tsconfig.json        # TypeScript config
├── tailwind.config.js   # Tailwind config
└── vite.config.ts       # Vite config
```

---

## Rust Backend Implementation

### main.rs - App Entry Point

```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod events;
mod python;

use tauri::{Manager, State};
use std::sync::Mutex;

// App state
pub struct AppState {
    pub python_path: Mutex<String>,
    pub backend_path: Mutex<String>,
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // Initialize app state
            let python_path = find_python_executable()?;
            let backend_path = find_backend_directory()?;
            
            app.manage(AppState {
                python_path: Mutex::new(python_path),
                backend_path: Mutex::new(backend_path),
            });
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::generate_video,
            commands::analyze_music,
            commands::train_style,
            commands::explore_parameters,
            commands::list_styles,
            commands::list_audio_files,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn find_python_executable() -> Result<String, String> {
    // Check for Python in various locations
    // Return path to python.exe
    // TODO: Implement
    Ok("python".to_string())
}

fn find_backend_directory() -> Result<String, String> {
    // Locate Code/backend/ relative to app
    // TODO: Implement
    Ok("../Code/backend".to_string())
}
```

### python.rs - Python CLI Wrapper

```rust
use std::process::{Command, Stdio, Child};
use std::io::{BufRead, BufReader};
use tauri::{Window, Manager};
use serde::Serialize;

#[derive(Clone, Serialize)]
pub struct ProgressEvent {
    pub progress: f32,
    pub message: String,
}

pub struct PythonCommand {
    window: Window,
    process: Option<Child>,
}

impl PythonCommand {
    pub fn new(window: Window) -> Self {
        Self {
            window,
            process: None,
        }
    }
    
    pub fn spawn(
        &mut self,
        python_path: &str,
        script: &str,
        args: Vec<String>,
    ) -> Result<(), String> {
        let mut cmd = Command::new(python_path);
        cmd.arg(script)
           .args(args)
           .stdout(Stdio::piped())
           .stderr(Stdio::piped());
        
        let mut process = cmd.spawn()
            .map_err(|e| format!("Failed to spawn Python: {}", e))?;
        
        // Capture STDOUT for progress
        if let Some(stdout) = process.stdout.take() {
            let window = self.window.clone();
            std::thread::spawn(move || {
                let reader = BufReader::new(stdout);
                for line in reader.lines() {
                    if let Ok(line) = line {
                        // Parse progress from line
                        if let Some(progress) = parse_progress(&line) {
                            let _ = window.emit("python-progress", ProgressEvent {
                                progress,
                                message: line.clone(),
                            });
                        }
                    }
                }
            });
        }
        
        self.process = Some(process);
        Ok(())
    }
    
    pub fn wait(&mut self) -> Result<i32, String> {
        if let Some(mut process) = self.process.take() {
            let status = process.wait()
                .map_err(|e| format!("Process error: {}", e))?;
            Ok(status.code().unwrap_or(-1))
        } else {
            Err("No process running".to_string())
        }
    }
    
    pub fn kill(&mut self) -> Result<(), String> {
        if let Some(mut process) = self.process.take() {
            process.kill()
                .map_err(|e| format!("Failed to kill: {}", e))?;
        }
        Ok(())
    }
}

fn parse_progress(line: &str) -> Option<f32> {
    // Parse lines like "Progress: 65%"
    if line.contains("Progress:") {
        if let Some(percent) = line.split("%").next() {
            if let Some(num) = percent.split(":").last() {
                return num.trim().parse::<f32>().ok();
            }
        }
    }
    None
}
```

### commands.rs - Tauri Commands

```rust
use tauri::{State, Window};
use crate::AppState;
use crate::python::PythonCommand;
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct GenerateVideoParams {
    pub audio_path: String,
    pub output_path: String,
    pub style_path: Option<String>,
    pub resolution: String,
    pub fps: u32,
}

#[derive(Serialize)]
pub struct CommandResult {
    pub success: bool,
    pub message: String,
    pub data: Option<String>,
}

#[tauri::command]
pub async fn generate_video(
    params: GenerateVideoParams,
    state: State<'_, AppState>,
    window: Window,
) -> Result<CommandResult, String> {
    let python_path = state.python_path.lock().unwrap().clone();
    let backend_path = state.backend_path.lock().unwrap().clone();
    
    let mut args = vec![
        params.audio_path,
        params.output_path,
        "--resolution".to_string(),
        params.resolution,
        "--fps".to_string(),
        params.fps.to_string(),
    ];
    
    if let Some(style) = params.style_path {
        args.push("--load-weights".to_string());
        args.push(style);
    }
    
    let script = format!("{}/cli.py", backend_path);
    
    let mut cmd = PythonCommand::new(window);
    cmd.spawn(&python_path, &script, args)?;
    
    let exit_code = cmd.wait()?;
    
    Ok(CommandResult {
        success: exit_code == 0,
        message: if exit_code == 0 {
            "Video generated successfully".to_string()
        } else {
            format!("Generation failed with code {}", exit_code)
        },
        data: Some(params.output_path),
    })
}

#[tauri::command]
pub async fn analyze_music(
    audio_path: String,
    analyzers: Vec<String>,
    state: State<'_, AppState>,
    window: Window,
) -> Result<CommandResult, String> {
    let python_path = state.python_path.lock().unwrap().clone();
    let backend_path = state.backend_path.lock().unwrap().clone();
    
    // Run analyzers in parallel
    let mut handles = vec![];
    
    for analyzer in analyzers {
        let script = format!(
            "{}/music_analysis/cli/analyze_{}.py",
            backend_path, analyzer
        );
        let args = vec![audio_path.clone()];
        
        let python = python_path.clone();
        let win = window.clone();
        
        let handle = std::thread::spawn(move || {
            let mut cmd = PythonCommand::new(win);
            cmd.spawn(&python, &script, args)?;
            cmd.wait()
        });
        
        handles.push(handle);
    }
    
    // Wait for all to complete
    let results: Vec<Result<i32, String>> = handles
        .into_iter()
        .map(|h| h.join().unwrap())
        .collect();
    
    let all_success = results.iter().all(|r| r.is_ok() && r.as_ref().unwrap() == &0);
    
    Ok(CommandResult {
        success: all_success,
        message: if all_success {
            "Analysis complete".to_string()
        } else {
            "Some analyzers failed".to_string()
        },
        data: None,
    })
}

#[tauri::command]
pub async fn list_styles(
    state: State<'_, AppState>,
) -> Result<Vec<StyleInfo>, String> {
    let backend_path = state.backend_path.lock().unwrap().clone();
    let styles_path = format!("{}/styles", backend_path);
    
    // Scan for .pth files
    let entries = std::fs::read_dir(&styles_path)
        .map_err(|e| format!("Failed to read styles dir: {}", e))?;
    
    let mut styles = vec![];
    for entry in entries {
        let entry = entry.map_err(|e| format!("Entry error: {}", e))?;
        let path = entry.path();
        
        if path.extension().and_then(|s| s.to_str()) == Some("pth") {
            if let Some(name) = path.file_stem().and_then(|s| s.to_str()) {
                styles.push(StyleInfo {
                    name: name.to_string(),
                    path: path.to_string_lossy().to_string(),
                    // TODO: Load metadata from JSON sidecar
                    params: 0,
                    similarity: 0.0,
                });
            }
        }
    }
    
    Ok(styles)
}

#[derive(Serialize)]
pub struct StyleInfo {
    pub name: String,
    pub path: String,
    pub params: usize,
    pub similarity: f32,
}

// TODO: Implement remaining commands
// - train_style
// - explore_parameters  
// - list_audio_files
```

---

## React Frontend Implementation

### App.tsx - Root Component

```typescript
import { useState } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import SynesthesiaTab from '@/components/tabs/SynesthesiaTab';
import AnalysisTab from '@/components/tabs/AnalysisTab';
import StylesTab from '@/components/tabs/StylesTab';
import ExplorerTab from '@/components/tabs/ExplorerTab';
import ProjectsTab from '@/components/tabs/ProjectsTab';

type TabValue = 'synesthesia' | 'analysis' | 'styles' | 'explorer' | 'projects';

function App() {
  const [activeTab, setActiveTab] = useState<TabValue>('synesthesia');

  return (
    <div className="h-screen bg-slate-900 text-slate-100">
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <h1 className="text-2xl font-bold text-purple-400">
          Audio Feature Explorer
        </h1>
      </header>

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TabValue)}>
        <TabsList className="px-6 bg-slate-800 border-b border-slate-700">
          <TabsTrigger value="synesthesia">🎨 Synesthesia</TabsTrigger>
          <TabsTrigger value="analysis">🎵 Analysis</TabsTrigger>
          <TabsTrigger value="styles">🎭 Styles</TabsTrigger>
          <TabsTrigger value="explorer">🔬 Explorer</TabsTrigger>
          <TabsTrigger value="projects">📁 Projects</TabsTrigger>
        </TabsList>

        <div className="p-6">
          <TabsContent value="synesthesia">
            <SynesthesiaTab />
          </TabsContent>
          <TabsContent value="analysis">
            <AnalysisTab />
          </TabsContent>
          <TabsContent value="styles">
            <StylesTab />
          </TabsContent>
          <TabsContent value="explorer">
            <ExplorerTab />
          </TabsContent>
          <TabsContent value="projects">
            <ProjectsTab />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}

export default App;
```

### store/synesthesiaStore.ts - State Management

```typescript
import { create } from 'zustand';
import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';

interface SynesthesiaState {
  audioFile: string | null;
  selectedStyle: string | null;
  resolution: string;
  fps: number;
  isGenerating: boolean;
  progress: number;
  progressMessage: string;
  recentGenerations: Generation[];
  
  setAudioFile: (path: string) => void;
  setStyle: (style: string) => void;
  setResolution: (res: string) => void;
  setFps: (fps: number) => void;
  generateVideo: (fullVideo: boolean) => Promise<void>;
}

interface Generation {
  outputPath: string;
  audioPath: string;
  style: string;
  timestamp: Date;
  size: number;
}

export const useSynesthesiaStore = create<SynesthesiaState>((set, get) => ({
  audioFile: null,
  selectedStyle: null,
  resolution: '720p',
  fps: 30,
  isGenerating: false,
  progress: 0,
  progressMessage: '',
  recentGenerations: [],
  
  setAudioFile: (path) => set({ audioFile: path }),
  setStyle: (style) => set({ selectedStyle: style }),
  setResolution: (res) => set({ resolution: res }),
  setFps: (fps) => set({ fps }),
  
  generateVideo: async (fullVideo) => {
    const { audioFile, selectedStyle, resolution, fps } = get();
    
    if (!audioFile) {
      throw new Error('No audio file selected');
    }
    
    set({ isGenerating: true, progress: 0 });
    
    // Listen for progress events
    const unlisten = await listen<{ progress: number; message: string }>(
      'python-progress',
      (event) => {
        set({
          progress: event.payload.progress,
          progressMessage: event.payload.message,
        });
      }
    );
    
    try {
      const outputPath = `outputs/generated_${Date.now()}.mp4`;
      
      const result = await invoke<{ success: boolean; message: string; data: string }>(
        'generate_video',
        {
          params: {
            audioPath: audioFile,
            outputPath,
            stylePath: selectedStyle,
            resolution,
            fps,
          },
        }
      );
      
      if (result.success) {
        // Add to recent generations
        set((state) => ({
          recentGenerations: [
            {
              outputPath,
              audioPath: audioFile,
              style: selectedStyle || 'default',
              timestamp: new Date(),
              size: 0, // TODO: Get file size
            },
            ...state.recentGenerations,
          ].slice(0, 10), // Keep last 10
        }));
      } else {
        throw new Error(result.message);
      }
    } finally {
      unlisten();
      set({ isGenerating: false, progress: 0, progressMessage: '' });
    }
  },
}));
```

### components/tabs/SynesthesiaTab.tsx

```typescript
import { useSynesthesiaStore } from '@/store/synesthesiaStore';
import FileDropzone from '@/components/common/FileDropzone';
import ProgressBar from '@/components/common/ProgressBar';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function SynesthesiaTab() {
  const {
    audioFile,
    selectedStyle,
    resolution,
    fps,
    isGenerating,
    progress,
    progressMessage,
    setAudioFile,
    setStyle,
    setResolution,
    setFps,
    generateVideo,
  } = useSynesthesiaStore();

  return (
    <div className="space-y-6">
      {/* File Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">Audio File</label>
        <FileDropzone
          accept=".mp3,.wav,.flac,.ogg"
          onFileSelect={setAudioFile}
          currentFile={audioFile}
        />
      </div>

      {/* Video Preview Area */}
      <div className="bg-slate-800 rounded-lg p-6 aspect-video flex items-center justify-center">
        {audioFile ? (
          <div className="text-center">
            <p className="text-slate-400 mb-4">Video preview will appear here</p>
            <Button variant="outline" size="sm">
              Load Preview
            </Button>
          </div>
        ) : (
          <p className="text-slate-500">Select an audio file to begin</p>
        )}
      </div>

      {/* Settings */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Style</label>
          <Select value={selectedStyle || ''} onValueChange={setStyle}>
            <SelectTrigger>
              <SelectValue placeholder="Select a style..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="organic_flow">Organic Flow</SelectItem>
              <SelectItem value="cyberpunk_neon">Cyberpunk Neon</SelectItem>
              <SelectItem value="cosmic_nebula">Cosmic Nebula</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Resolution</label>
          <Select value={resolution} onValueChange={setResolution}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="480p">480p</SelectItem>
              <SelectItem value="720p">720p (Recommended)</SelectItem>
              <SelectItem value="1080p">1080p</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">FPS</label>
          <Select value={fps.toString()} onValueChange={(v) => setFps(parseInt(v))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24">24 FPS</SelectItem>
              <SelectItem value="30">30 FPS</SelectItem>
              <SelectItem value="60">60 FPS</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-4">
        <Button
          onClick={() => generateVideo(false)}
          disabled={!audioFile || isGenerating}
          variant="outline"
        >
          Quick Preview (10s)
        </Button>
        <Button
          onClick={() => generateVideo(true)}
          disabled={!audioFile || isGenerating}
          className="flex-1"
        >
          {isGenerating ? 'Generating...' : 'Generate Full Video'}
        </Button>
      </div>

      {/* Progress */}
      {isGenerating && (
        <div className="space-y-2">
          <ProgressBar value={progress} />
          <p className="text-sm text-slate-400">{progressMessage}</p>
        </div>
      )}

      {/* Recent Generations */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Recent Generations</h3>
        <div className="space-y-2">
          {/* TODO: Map over recentGenerations */}
          <div className="bg-slate-800 rounded p-3 flex justify-between items-center">
            <div>
              <p className="font-medium">tool_organic_720p.mp4</p>
              <p className="text-sm text-slate-400">409 MB • 5 minutes ago</p>
            </div>
            <Button variant="ghost" size="sm">
              Open
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## Data Formats & APIs

### IPC Commands

```typescript
// Tauri Commands (invoke from frontend)

interface GenerateVideoParams {
  audioPath: string;
  outputPath: string;
  stylePath?: string;
  resolution: string;
  fps: number;
}

invoke<CommandResult>('generate_video', { params: GenerateVideoParams });
invoke<CommandResult>('analyze_music', { audioPath: string, analyzers: string[] });
invoke<CommandResult>('train_style', { params: TrainStyleParams });
invoke<StyleInfo[]>('list_styles');
invoke<AudioFileInfo[]>('list_audio_files', { directory: string });
```

### IPC Events

```typescript
// Events emitted from backend

interface ProgressEvent {
  progress: number;  // 0-100
  message: string;
}

listen<ProgressEvent>('python-progress', (event) => {
  console.log(`Progress: ${event.payload.progress}%`);
});

listen<string>('python-error', (event) => {
  console.error('Python error:', event.payload);
});

listen<string>('python-complete', (event) => {
  console.log('Complete:', event.payload);
});
```

### Music Analysis JSON Format

```typescript
// Tempo Analysis
interface TempoData {
  tempo: number;
  confidence: number;
  beats: number[];
  time_signature: string;
}

// Key Detection
interface KeyData {
  key: string;
  scale: string;
  confidence: number;
  alternatives: Array<{ key: string; scale: string; confidence: number }>;
}

// Chords
interface ChordData {
  chords: Array<{
    time: number;
    chord: string;
    confidence: number;
  }>;
  vocabulary: string[];
}

// Structure
interface StructureData {
  segments: Array<{
    start: number;
    end: number;
    label: string;
  }>;
}
```

---

## Security Considerations

### Tauri Allowlist

```json
{
  "tauri": {
    "allowlist": {
      "fs": {
        "all": false,
        "readFile": true,
        "writeFile": true,
        "readDir": true,
        "createDir": true,
        "scope": ["$APPDATA/*", "$DOCUMENT/*", "Code/backend/*"]
      },
      "shell": {
        "all": false,
        "execute": false,
        "sidecar": false,
        "open": true,
        "scope": []
      },
      "dialog": {
        "all": true
      },
      "process": {
        "all": false,
        "exit": true,
        "relaunch": false
      }
    }
  }
}
```

### Python Process Sandboxing

- ✅ No direct shell access
- ✅ Controlled via Rust std::process
- ✅ Limited file system access
- ✅ STDOUT/STDERR captured
- ✅ Timeout enforcement
- ✅ Resource limits (memory, CPU)

---

## Performance Optimization

### Frontend

1. **Code Splitting**
   - Lazy load tab components
   - Dynamic imports for large libraries

2. **Virtual Lists**
   - For file browsers (100s+ files)
   - For recent generations

3. **Memoization**
   - React.memo for expensive components
   - useMemo for computed values

4. **Debouncing**
   - Parameter sliders
   - Search inputs

### Backend

1. **Process Pooling**
   - Reuse Python processes where possible
   - Warm start for faster execution

2. **Caching**
   - Style list caching
   - File metadata caching

3. **Async Operations**
   - Parallel analyzer execution
   - Background file scanning

---

## Testing Strategy

### Unit Tests

**Frontend (Jest + React Testing Library):**
- Component rendering
- State management
- Utility functions

**Backend (Rust cargo test):**
- Command parsing
- Python wrapper
- File operations

### Integration Tests

**Tauri Integration:**
- IPC communication
- Process spawning
- File system access

**End-to-End (Playwright):**
- Full user flows
- Tab navigation
- Video generation workflow

### Manual Testing

**User Acceptance Testing:**
- 3-5 target users
- Task-based scenarios
- Feedback collection

---

## Build & Deployment

### Development Build

```bash
# Install dependencies
npm install
cd src-tauri && cargo build

# Run dev server
npm run tauri dev
```

### Production Build

```bash
# Build for current platform
npm run tauri build

# Output:
# - Windows: .msi installer
# - Mac: .dmg bundle
# - Linux: .AppImage, .deb
```

### Auto-Updates (Future)

- Use Tauri updater
- Check for updates on launch
- Background download
- Install on next restart

---

## Documentation Requirements

### User Documentation

- [ ] Getting started guide
- [ ] Feature tutorials
- [ ] Keyboard shortcuts
- [ ] Troubleshooting guide

### Developer Documentation

- [ ] Architecture overview
- [ ] API reference
- [ ] Contributing guide
- [ ] Build instructions

---

**Specification Date:** October 13, 2025  
**Status:** Ready for implementation  
**Next:** Begin Tauri project setup

🚀 **Technical foundation is solid - let's build!**


