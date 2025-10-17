# Phase 3 MVP - Project Structure

**Date:** 2025-10-17  
**Purpose:** Complete directory and file organization

---

## Directory Tree

```
C:\Users\aitor\audiovisual\audiovisuals\
│
├── Code/
│   │
│   ├── backend/                        # ✅ Phase 2 - Python CLI (Complete)
│   │   ├── audio_analyzer.py           # FFT feature extraction
│   │   ├── cppn.py                     # CPPN neural network (3L×4D optimal)
│   │   ├── renderer.py                 # GPU-accelerated rendering
│   │   ├── video_encoder.py            # MP4 encoding
│   │   ├── cli.py                      # Main CLI interface
│   │   ├── clip_optimize_cppn.py       # CLIP style training
│   │   │
│   │   ├── music_analysis/             # 5 semantic analyzers
│   │   │   ├── analyzers/
│   │   │   │   ├── tempo_analyzer.py
│   │   │   │   ├── key_detector.py
│   │   │   │   ├── chord_detector.py
│   │   │   │   ├── structure_analyzer.py
│   │   │   │   └── genre_classifier.py
│   │   │   ├── cli/
│   │   │   │   ├── analyze_tempo.py
│   │   │   │   ├── analyze_key.py
│   │   │   │   ├── analyze_chords.py
│   │   │   │   ├── analyze_structure.py
│   │   │   │   └── analyze_genre.py
│   │   │   └── visualization/
│   │   │       └── (plot_*.py, html_generator.py)
│   │   │
│   │   ├── styles/                     # CLIP-trained style library
│   │   │   └── organic/
│   │   │       ├── cosmic_galaxy_3L_4D.pth
│   │   │       └── (more styles...)
│   │   │
│   │   ├── tools/                      # Parameter exploration
│   │   ├── explorations/               # Experiment results
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   └── desktop/                        # 🆕 Phase 3 - Tauri Desktop App (NEW)
│       │
│       ├── src/                        # React Frontend
│       │   │
│       │   ├── components/
│       │   │   ├── tabs/               # Main feature tabs
│       │   │   │   ├── SynesthesiaTab.tsx      # Video generation
│       │   │   │   ├── AnalysisTab.tsx         # Music analysis
│       │   │   │   ├── StylesTab.tsx           # Style library
│       │   │   │   ├── ExplorerTab.tsx         # Parameter exploration
│       │   │   │   └── ProjectsTab.tsx         # File management
│       │   │   │
│       │   │   ├── common/             # Shared UI components
│       │   │   │   ├── FileDropzone.tsx        # Drag & drop
│       │   │   │   ├── ProgressBar.tsx         # Progress indicator
│       │   │   │   ├── VideoPlayer.tsx         # Video.js wrapper
│       │   │   │   ├── Button.tsx              # Custom button
│       │   │   │   ├── Select.tsx              # Custom select
│       │   │   │   └── Dialog.tsx              # Modal dialogs
│       │   │   │
│       │   │   └── charts/             # Plotly visualizations
│       │   │       ├── TempoChart.tsx
│       │   │       ├── KeyChart.tsx
│       │   │       ├── ChordChart.tsx
│       │   │       ├── StructureChart.tsx
│       │   │       └── GenreChart.tsx
│       │   │
│       │   ├── store/                  # Zustand state management
│       │   │   ├── appStore.ts                 # Global app state
│       │   │   ├── synesthesiaStore.ts         # Video generation state
│       │   │   ├── analysisStore.ts            # Analysis results state
│       │   │   ├── stylesStore.ts              # Style library state
│       │   │   └── explorerStore.ts            # Parameter exploration state
│       │   │
│       │   ├── hooks/                  # Custom React hooks
│       │   │   ├── usePythonCommand.ts         # Python process execution
│       │   │   ├── useVideoGeneration.ts       # Video generation workflow
│       │   │   ├── useFileWatcher.ts           # File system monitoring
│       │   │   └── useProgress.ts              # Progress tracking
│       │   │
│       │   ├── types/                  # TypeScript type definitions
│       │   │   ├── index.ts                    # Main exports
│       │   │   ├── music.ts                    # Music analysis types
│       │   │   ├── styles.ts                   # Style library types
│       │   │   ├── generation.ts               # Video generation types
│       │   │   └── python.ts                   # Python IPC types
│       │   │
│       │   ├── utils/                  # Utility functions
│       │   │   ├── formatters.ts               # Data formatting
│       │   │   ├── validators.ts               # Input validation
│       │   │   ├── parsers.ts                  # Response parsing
│       │   │   └── pathResolver.ts             # File path handling
│       │   │
│       │   ├── App.tsx                 # Root component
│       │   ├── main.tsx                # React entry point
│       │   └── index.css               # Global styles (Tailwind)
│       │
│       ├── src-tauri/                  # Rust Backend
│       │   ├── src/
│       │   │   ├── main.rs             # Tauri entry point
│       │   │   ├── python.rs           # Python CLI wrapper
│       │   │   ├── commands.rs         # Tauri commands (IPC)
│       │   │   ├── events.rs           # Event emitters
│       │   │   └── lib.rs              # Library exports
│       │   │
│       │   ├── Cargo.toml              # Rust dependencies
│       │   ├── tauri.conf.json         # Tauri configuration
│       │   ├── build.rs                # Build script
│       │   └── icons/                  # App icons
│       │
│       ├── public/                     # Static assets
│       │   └── (if needed)
│       │
│       ├── package.json                # Node dependencies
│       ├── tsconfig.json               # TypeScript config
│       ├── vite.config.ts              # Vite bundler config
│       ├── tailwind.config.js          # Tailwind CSS config
│       ├── postcss.config.js           # PostCSS config
│       ├── .gitignore
│       └── README.md
│
├── docs/
│   │
│   ├── Phase0-Alignment/              # ✅ Project alignment
│   │   ├── PROFILE.yaml
│   │   ├── CONTEXT.md
│   │   ├── agents.md
│   │   └── README.md
│   │
│   ├── Phase1-Ideation/               # ✅ Initial idea
│   │   ├── IDEA_NOTE.md
│   │   ├── agents.md
│   │   └── README.md
│   │
│   ├── Phase2-POC/                    # ✅ Proof of Concept (Complete)
│   │   ├── POC_PLAN.md
│   │   ├── PHASE_2_COMPLETE.md
│   │   ├── PHASE_C_BREAKTHROUGH.md    # 3L×4D discovery
│   │   ├── NETWORK_ARCHITECTURE_GUIDE.md
│   │   ├── agents.md
│   │   ├── backend/
│   │   │   └── (technical docs)
│   │   └── README.md
│   │
│   ├── Phase3-MVP/                    # 📋 Current Phase (In Progress)
│   │   ├── README.md                  # Overview
│   │   ├── PHASE_3_KICKOFF.md         # Summary & transition
│   │   ├── PRD.md                     # ✅ Product requirements
│   │   ├── UX_RESEARCH.md             # User research & UI design
│   │   ├── TECHNICAL_SPEC.md          # Technical architecture
│   │   ├── IMPLEMENTATION_PLAN.md     # 12-week timeline
│   │   ├── ARCHITECTURE_INTEGRATION.md # 3L×4D integration
│   │   ├── SETUP_GUIDE.md             # ✅ Installation guide
│   │   ├── PROJECT_STRUCTURE.md       # ✅ This file
│   │   ├── synesthesia research       # Research for Phase 4+
│   │   └── agents.md
│   │
│   ├── Audio/                         # Sample audio files
│   │   ├── TOOL - The Pot (Audio).mp3
│   │   ├── Zyryab.mp3
│   │   └── (test outputs, docs)
│   │
│   └── explorations/                  # Research explorations
│       ├── clip_organic_20251011/
│       ├── music_analysis_20251012/
│       └── README.md
│
├── styles/                            # (Legacy, will move to Code/backend/styles/)
│
├── AGENTS.md                          # Root agent coordination
├── README_TEMPLATE.md
└── START_HERE.md
```

---

## File Count Summary

### Phase 2 Backend (Python) - ✅ Complete
- **Core files:** 10 (cli.py, cppn.py, renderer.py, etc.)
- **Music analysis:** 15 (5 analyzers + CLI wrappers + visualizations)
- **Tools:** 10 (exploration, rating, HTML generation)
- **Documentation:** 20+ markdown files
- **Total:** ~50 Python files, fully functional

### Phase 3 Desktop (Tauri) - 🆕 To Create
- **React components:** ~25 files (tabs, common, charts)
- **State management:** 5 stores
- **Hooks:** 4 custom hooks
- **Types:** 5 TypeScript files
- **Utilities:** 4 utility modules
- **Rust backend:** 4 source files
- **Config files:** 6 (package.json, tsconfig, tailwind, etc.)
- **Total:** ~50 new files to create

---

## Key Integration Points

### Python ← Rust Communication

**Rust spawns Python:**
```
Code/desktop/src-tauri/src/python.rs
  ↓ spawns
Code/backend/cli.py (or music_analysis CLI)
  ↓ outputs
STDOUT/STDERR captured by Rust
  ↓ parsed
Sent to React via events
```

### React ← Rust Communication

**React invokes Rust:**
```
Code/desktop/src/components/tabs/SynesthesiaTab.tsx
  ↓ calls
invoke('generate_video', { params })
  ↓ handled by
Code/desktop/src-tauri/src/commands.rs
  ↓ spawns
Code/backend/cli.py
```

### File System Access

**Allowed paths:**
- `$APPDATA/*` - Application data
- `$DOCUMENT/*` - User documents
- `Code/backend/*` - Python backend (read .pth, .mp3, etc.)

**Restricted:**
- Cannot execute arbitrary shell commands
- Cannot access system directories
- Sandboxed by Tauri security model

---

## Data Flow Examples

### Example 1: Video Generation

```
1. User selects audio in SynesthesiaTab.tsx
   ↓
2. User clicks "Generate Video"
   ↓
3. synesthesiaStore.generateVideo() called
   ↓
4. invoke('generate_video', { audioPath, stylePath, ... })
   ↓
5. Rust commands::generate_video() spawns Python
   ↓
6. Python cli.py processes audio → renders frames → encodes video
   ↓
7. Python STDOUT: "Progress: 45%" parsed by Rust
   ↓
8. Rust emits event 'python-progress' → React updates UI
   ↓
9. Python exits with code 0 (success)
   ↓
10. React shows success message, displays video in VideoPlayer
```

### Example 2: Music Analysis

```
1. User selects audio in AnalysisTab.tsx
   ↓
2. User checks all 5 analyzers, clicks "Run Analysis"
   ↓
3. analysisStore.runAnalysis() called
   ↓
4. invoke('analyze_music', { audioPath, analyzers: ['tempo', 'key', ...] })
   ↓
5. Rust spawns 5 Python processes in parallel
   ↓
6. Each analyzer outputs JSON to files
   ↓
7. Rust reads JSON files, aggregates results
   ↓
8. Returns results to React
   ↓
9. React renders Plotly charts with data
```

---

## Configuration Files

### package.json (Node dependencies)

```json
{
  "name": "audiovisuals-desktop",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "tauri": "tauri",
    "tauri:dev": "tauri dev",
    "tauri:build": "tauri build"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tauri-apps/api": "^1.5.0",
    "zustand": "^4.4.0",
    "react-plotly.js": "^2.6.0",
    "plotly.js": "^2.27.0",
    "video.js": "^8.6.0",
    "lucide-react": "^0.294.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/node": "^20.0.0",
    "@types/video.js": "^7.3.0",
    "@types/plotly.js": "^2.12.0",
    "@tauri-apps/cli": "^1.5.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.2.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

### Cargo.toml (Rust dependencies)

```toml
[package]
name = "audiovisuals-desktop"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = { version = "1.5", features = ["dialog-all", "fs-all", "shell-open"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1", features = ["full"] }

[build-dependencies]
tauri-build = { version = "1.5" }
```

---

## Next Steps After Setup

1. **Verify structure exists:**
   ```powershell
   tree Code\desktop /F | more
   ```

2. **Start development (Week 1):**
   - Create tab navigation shell
   - Build Python wrapper (python.rs)
   - Test IPC communication

3. **Follow implementation plan:**
   - See `docs/Phase3-MVP/IMPLEMENTATION_PLAN.md`
   - Week-by-week tasks

---

**Document Date:** 2025-10-17  
**Status:** Structure documented, ready for creation  
**Next:** Install tools (see SETUP_GUIDE.md), then initialize project

📁 **This structure will be created after running `npm create tauri-app`**

