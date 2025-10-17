# Audio Feature Explorer - Desktop App

**Phase 3 MVP Development**  
**Tech Stack:** Tauri 2.0 + React 18 + TypeScript + Tailwind CSS

---

## Quick Start

### Start Development Server
```powershell
npm run tauri:dev
```

**First run:** Rust compilation takes ~60 seconds  
**Subsequent runs:** Starts in ~5 seconds with hot reload

### Build for Production
```powershell
npm run tauri:build
```

Output: `src-tauri/target/release/audiovisuals-desktop.exe`

---

## Project Structure

```
desktop/
├── src/                    # React frontend
├── src-tauri/              # Rust backend
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
├── vite.config.ts          # Build config
├── tailwind.config.js      # CSS config
└── SETUP_COMPLETE.md       # Installation guide
```

---

## What's Included

### System Tools
- ✅ Rust 1.90.0
- ✅ Node.js v22.20.0
- ✅ Tauri CLI 2.8.4
- ✅ VS Build Tools 2022

### Frontend Stack
- ✅ React 18.3.1 + TypeScript
- ✅ Vite (fast bundler)
- ✅ Tailwind CSS (utility-first)
- ✅ Zustand (state management)
- ✅ React-Plotly.js (charts)
- ✅ Video.js (video player)
- ✅ Lucide React (icons)

### Backend (Tauri/Rust)
- ✅ Tauri 2.8.4
- ✅ Shell plugin (for Python CLI)
- ✅ IPC commands ready

---

## Phase 3 Roadmap

### ✅ Week 1: Foundation (Complete!)
- [x] Install Rust, Node.js, Tauri
- [x] Create React + TypeScript project
- [x] Configure Tailwind CSS
- [x] Install dependencies
- [x] Test development environment

### Week 2: Tab Navigation Shell
- [ ] Create 5-tab layout
- [ ] Set up routing
- [ ] Design UI components
- [ ] Implement state management

### Weeks 3-4: Synesthesia Tab
- [ ] Python CLI wrapper (Rust)
- [ ] File picker
- [ ] Style selector
- [ ] Video generation
- [ ] Progress tracking

### Weeks 5-6: Analysis Tab
- [ ] Multi-analyzer UI
- [ ] Plotly chart integration
- [ ] Export functionality

### Weeks 7-8: Styles Tab
- [ ] Library browser
- [ ] CLIP training wizard
- [ ] Style management

### Weeks 9-10: Explorer & Projects
- [ ] Parameter exploration
- [ ] Preset management
- [ ] File browser

### Weeks 11-12: Polish & Testing
- [ ] Error handling
- [ ] Performance optimization
- [ ] User testing

---

## Documentation

### Setup & Installation
- [SETUP_COMPLETE.md](./SETUP_COMPLETE.md) - Complete installation guide

### Phase 3 Planning
- [Phase 3 Kickoff](../../docs/Phase3-MVP/PHASE_3_KICKOFF.md)
- [UX Research](../../docs/Phase3-MVP/UX_RESEARCH.md)
- [Technical Spec](../../docs/Phase3-MVP/TECHNICAL_SPEC.md)
- [Implementation Plan](../../docs/Phase3-MVP/IMPLEMENTATION_PLAN.md)

### Phase 2 Backend (Python CLI)
- [Backend README](../backend/README.md)
- [Quick Start](../backend/QUICK_START_AITOR.md)
- [Music Analysis](../backend/music_analysis/README.md)

---

## Development Commands

```powershell
# Development
npm run dev              # Frontend only (Vite)
npm run tauri:dev        # Full app (Tauri + React)

# Build
npm run build            # Frontend build
npm run tauri:build      # Full app build

# Preview
npm run preview          # Preview production build

# Tauri CLI
npx tauri info           # System information
npx tauri dev            # Start development
npx tauri build          # Build for production
npx tauri --help         # All commands
```

---

## Troubleshooting

### Dev Server Won't Start
1. Restart terminal after installing Build Tools
2. Check Rust: `rustc --version`
3. Check Node: `node --version`
4. Reinstall dependencies: `npm install`

### Rust Compilation Slow
- First compilation: 30-60 seconds (normal)
- Subsequent: < 5 seconds
- Restart computer if >5 minutes

### Hot Reload Not Working
- Check Vite terminal output
- Close app and restart dev server
- Delete `node_modules/.vite` cache

---

## Integration with Python Backend

The desktop app will call Python CLI tools in `Code/backend/`:
- `cli.py` - Video generation
- `music_analysis/` - Semantic analysis
- `clip_optimize_cppn.py` - Style training

**Integration:** Week 3 (Rust wrapper + IPC bridge)

---

## Resources

- [Tauri Docs](https://tauri.app/)
- [React Docs](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Zustand](https://github.com/pmndrs/zustand)
- [Plotly React](https://plotly.com/javascript/react/)

---

**Status:** ✅ Ready for Phase 3 MVP Development  
**Next:** Review [UX Research](../../docs/Phase3-MVP/UX_RESEARCH.md) and start Week 2 tasks  
**Updated:** October 17, 2025

