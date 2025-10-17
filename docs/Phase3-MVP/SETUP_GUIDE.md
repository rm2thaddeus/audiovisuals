# Phase 3 MVP - Complete Setup Guide

**Date:** 2025-10-17  
**Status:** 🔧 Environment Setup  
**Platform:** Windows 10/11

---

## Prerequisites Installation

### Step 1: Install Node.js (Required)

**Option A: Direct Download (Recommended)**
1. Visit: https://nodejs.org/en/download/
2. Download **LTS version** (20.x or 22.x) for Windows
3. Run installer (`node-v20.x.x-x64.msi`)
4. Follow installer (accept defaults)
5. Restart terminal

**Option B: Using winget**
```powershell
winget install OpenJS.NodeJS.LTS
```

**Verify Installation:**
```powershell
node --version    # Should show v20.x.x or v22.x.x
npm --version     # Should show 10.x.x or higher
```

---

### Step 2: Install Rust (Required)

**Option A: Direct Download (Recommended)**
1. Visit: https://www.rust-lang.org/tools/install
2. Download `rustup-init.exe`
3. Run installer
4. Select option **1** (default installation)
5. Wait for installation to complete
6. **Restart terminal** (important!)

**Option B: Using winget**
```powershell
winget install Rustlang.Rustup
```

**Verify Installation:**
```powershell
rustc --version   # Should show rustc 1.75.0 or higher
cargo --version   # Should show cargo 1.75.0 or higher
```

---

### Step 3: Install Tauri CLI (Required)

**After Node.js and Rust are installed:**

```powershell
npm install -g @tauri-apps/cli
```

**Verify:**
```powershell
npm list -g @tauri-apps/cli
```

---

## Project Initialization

### Step 1: Create Tauri Project

```powershell
# Navigate to project root
cd C:\Users\aitor\audiovisual\audiovisuals

# Create Tauri app (INTERACTIVE - answer prompts)
npm create tauri-app@latest
```

**Prompts and Answers:**
```
? Project name: audiovisuals-desktop
? Choose your package manager: npm
? Choose your UI template: React
? Add TypeScript? Yes
? Choose your UI flavor: TypeScript
```

This creates: `C:\Users\aitor\audiovisual\audiovisuals\audiovisuals-desktop\`

---

### Step 2: Move to Correct Location

```powershell
# Move created project to Code/desktop
mv audiovisuals-desktop Code/desktop
cd Code/desktop
```

---

### Step 3: Install Dependencies

```powershell
# Install base dependencies
npm install

# Install additional required packages
npm install zustand react-plotly.js plotly.js video.js
npm install lucide-react @radix-ui/react-tabs @radix-ui/react-dialog

# Install dev dependencies
npm install -D @types/react @types/node @types/video.js
npm install -D tailwindcss postcss autoprefixer
npm install -D @types/plotly.js

# Initialize Tailwind CSS
npx tailwindcss init -p
```

---

### Step 4: Configure Tailwind

**File: `Code/desktop/tailwind.config.js`**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand colors from UX_RESEARCH.md
        brand: {
          purple: '#6B46C1',
          blue: '#3B82F6',
          pink: '#EC4899',
        },
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
      },
    },
  },
  plugins: [],
}
```

**File: `Code/desktop/src/index.css`**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Dark theme base */
body {
  @apply bg-slate-900 text-slate-100;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
```

---

### Step 5: Configure Tauri

**File: `Code/desktop/src-tauri/tauri.conf.json`**

Update `build` section:
```json
{
  "build": {
    "beforeBuildCommand": "npm run build",
    "beforeDevCommand": "npm run dev",
    "devPath": "http://localhost:5173",
    "distDir": "../dist"
  }
}
```

Update `allowlist`:
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
        "scope": ["$APPDATA/*", "$DOCUMENT/*", "$HOME/audiovisual/audiovisuals/Code/backend/*"]
      },
      "dialog": {
        "all": true,
        "open": true,
        "save": true
      },
      "shell": {
        "all": false,
        "execute": false,
        "sidecar": false,
        "open": true
      },
      "process": {
        "all": false,
        "exit": true
      }
    },
    "windows": [
      {
        "title": "Audio Feature Explorer",
        "width": 1280,
        "height": 800,
        "resizable": true,
        "fullscreen": false
      }
    ]
  }
}
```

---

## Project Structure

After setup, you'll have:

```
audiovisuals/
├── Code/
│   ├── backend/                 # ✅ Existing Python CLI (no changes)
│   │   ├── cli.py
│   │   ├── cppn.py
│   │   ├── audio_analyzer.py
│   │   ├── music_analysis/
│   │   └── ...
│   │
│   └── desktop/                 # 🆕 NEW Tauri desktop app
│       ├── src/                 # React frontend
│       │   ├── components/
│       │   │   ├── tabs/
│       │   │   │   ├── SynesthesiaTab.tsx
│       │   │   │   ├── AnalysisTab.tsx
│       │   │   │   ├── StylesTab.tsx
│       │   │   │   ├── ExplorerTab.tsx
│       │   │   │   └── ProjectsTab.tsx
│       │   │   ├── common/
│       │   │   │   ├── FileDropzone.tsx
│       │   │   │   ├── ProgressBar.tsx
│       │   │   │   └── VideoPlayer.tsx
│       │   │   └── charts/
│       │   │       └── (Plotly chart components)
│       │   ├── store/
│       │   │   ├── appStore.ts
│       │   │   ├── synesthesiaStore.ts
│       │   │   └── analysisStore.ts
│       │   ├── hooks/
│       │   │   └── usePythonCommand.ts
│       │   ├── types/
│       │   │   └── index.ts
│       │   ├── utils/
│       │   │   └── formatters.ts
│       │   ├── App.tsx
│       │   ├── main.tsx
│       │   └── index.css
│       │
│       ├── src-tauri/            # Rust backend
│       │   ├── src/
│       │   │   ├── main.rs       # Entry point
│       │   │   ├── python.rs     # Python CLI wrapper
│       │   │   ├── commands.rs   # Tauri commands
│       │   │   └── lib.rs
│       │   ├── Cargo.toml
│       │   ├── tauri.conf.json
│       │   └── icons/
│       │
│       ├── package.json
│       ├── tsconfig.json
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       └── README.md
│
└── docs/
    ├── Phase0-Alignment/
    ├── Phase1-Ideation/
    ├── Phase2-POC/
    └── Phase3-MVP/            # ⬅ You are here
        ├── SETUP_GUIDE.md     # This file
        ├── PRD.md
        ├── UX_RESEARCH.md
        ├── TECHNICAL_SPEC.md
        ├── IMPLEMENTATION_PLAN.md
        ├── PHASE_3_KICKOFF.md
        └── ARCHITECTURE_INTEGRATION.md
```

---

## Quick Start Commands

### Development Mode

```powershell
cd Code/desktop

# Start Tauri development server (hot reload)
npm run tauri dev
```

This will:
1. Start Vite dev server (React frontend)
2. Compile Rust backend
3. Launch desktop app window
4. Enable hot module reload

### Build for Production

```powershell
cd Code/desktop

# Build optimized app
npm run tauri build
```

Output: `Code/desktop/src-tauri/target/release/bundle/msi/audiovisuals-desktop_0.1.0_x64_en-US.msi`

---

## Testing Python Integration

### Test 1: Python Detection

```powershell
# Verify Python is accessible
python --version  # Should show 3.12.0

# Test CLI tool
cd Code/backend
python cli.py --help
```

### Test 2: Basic Generation

```powershell
cd Code/backend

# Generate a test video (30 seconds)
python cli.py "docs/Audio/Zyryab.mp3" test_output.mp4 --resolution 480p --fps 24 --duration 30
```

Expected: Video generates successfully in ~20 seconds

### Test 3: Music Analysis

```powershell
cd Code/backend

# Test tempo analyzer
python -m music_analysis.cli.analyze_tempo "docs/Audio/Zyryab.mp3"
```

Expected: JSON output with tempo, beats, time signature

---

## Troubleshooting

### Issue: Node.js not found after install
**Solution:** Restart PowerShell/Terminal completely (close all windows)

### Issue: Rust compile errors
**Solution:** 
```powershell
rustup update
cargo clean
```

### Issue: Python not found in Tauri app
**Solution:** Check Python path in `Code/desktop/src-tauri/src/main.rs`:
```rust
// Add explicit Python path
let python_path = r"C:\Users\aitor\AppData\Local\Programs\Python\Python312\python.exe";
```

### Issue: CUDA errors
**Solution:** CLI tools fall back to CPU automatically. No action needed.

### Issue: npm install fails
**Solution:**
```powershell
npm cache clean --force
rm -r node_modules
rm package-lock.json
npm install
```

### Issue: Tauri window won't open
**Solution:**
1. Check Windows Firewall (allow `audiovisuals-desktop.exe`)
2. Run as Administrator
3. Check `src-tauri/target/debug/audiovisuals-desktop.log`

---

## Development Workflow

### Day-to-Day Development

1. **Start dev server:**
   ```powershell
   cd Code/desktop
   npm run tauri dev
   ```

2. **Edit React components** in `src/`
   - Changes hot-reload automatically

3. **Edit Rust code** in `src-tauri/src/`
   - App rebuilds automatically (may take 10-30 seconds)

4. **Test Python integration:**
   - Use Rust functions in `src-tauri/src/python.rs`
   - Call from React via `invoke('command_name')`

### Code → Test → Debug Cycle

**React (Frontend):**
- Edit `.tsx` files → Save → See changes instantly
- Use browser DevTools: `Ctrl+Shift+I` in app window

**Rust (Backend):**
- Edit `.rs` files → Save → Wait for recompile → App restarts
- Check terminal for Rust compile errors

**Python (CLI):**
- Edit `.py` files in `Code/backend/` → No rebuild needed
- Test standalone: `python cli.py ...`
- Test via Tauri: Click UI buttons

---

## Next Steps

### After Setup is Complete

1. ✅ Verify all installations
   ```powershell
   node --version
   rustc --version
   python --version
   npm run tauri dev  # Should open app window
   ```

2. ✅ Read the architecture docs:
   - `docs/Phase3-MVP/TECHNICAL_SPEC.md` - How it works
   - `docs/Phase3-MVP/UX_RESEARCH.md` - What we're building
   - `docs/Phase3-MVP/IMPLEMENTATION_PLAN.md` - Week-by-week plan

3. ✅ Begin Week 1 tasks:
   - Create tab navigation shell
   - Build Python wrapper in Rust
   - Test IPC communication

4. ✅ Join communities:
   - Tauri Discord: https://discord.gg/tauri
   - GitHub Discussions

---

## Resources

### Documentation
- **Tauri:** https://tauri.app/v1/guides/
- **React:** https://react.dev/learn
- **Zustand:** https://github.com/pmndrs/zustand
- **Plotly.js:** https://plotly.com/javascript/

### Tools
- **VS Code Extensions:**
  - rust-analyzer (Rust support)
  - Tailwind CSS IntelliSense
  - ES7+ React/Redux/React-Native snippets

### Internal Docs
- `docs/Phase3-MVP/` - All Phase 3 planning
- `Code/backend/README.md` - Python CLI documentation
- `Code/backend/music_analysis/README.md` - Analyzer docs

---

## Success Checklist

- [ ] Node.js installed and verified
- [ ] Rust installed and verified  
- [ ] Python 3.12 verified (already installed ✅)
- [ ] Tauri CLI installed
- [ ] Project created at `Code/desktop/`
- [ ] Dependencies installed (`npm install` complete)
- [ ] Tailwind configured
- [ ] Dev server runs (`npm run tauri dev` works)
- [ ] App window opens
- [ ] Hot reload works (edit `.tsx`, see changes)
- [ ] Python CLI accessible from terminal
- [ ] Ready for Week 1 development 🚀

---

**Document Date:** 2025-10-17  
**Status:** Ready for installation  
**Next:** Install Node.js and Rust, then run setup commands

🛠️ **Once tools are installed, run the commands in "Project Initialization" section above!**

