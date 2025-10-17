# Audio Feature Explorer - Desktop App

**Purpose:** Desktop GUI for synesthesia generation and music analysis  
**Tech Stack:** Tauri 2 + React 18 + TypeScript + Tailwind CSS  
**Status:** ✅ Setup Complete - Ready for Development

---

## This Directory Will Contain

After running `npm create tauri-app`, this directory will have:

```
Code/desktop/
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── store/              # Zustand state
│   ├── hooks/              # Custom hooks
│   ├── types/              # TypeScript types
│   ├── utils/              # Utilities
│   ├── App.tsx             # Root component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
│
├── src-tauri/              # Rust backend
│   ├── src/
│   │   ├── main.rs         # Tauri entry
│   │   ├── python.rs       # Python wrapper
│   │   ├── commands.rs     # IPC commands
│   │   └── lib.rs
│   ├── Cargo.toml          # Rust deps
│   └── tauri.conf.json     # Config
│
├── package.json            # Node deps
├── tsconfig.json           # TypeScript config
├── vite.config.ts          # Vite config
├── tailwind.config.js      # Tailwind config
└── README.md               # This file becomes the main README
```

---

## Installation Commands (Run After Tools Installed)

```powershell
# 1. Create Tauri project
cd C:\Users\aitor\audiovisual\audiovisuals
npm create tauri-app@latest
# Answer: audiovisuals-desktop, npm, React, Yes, TypeScript

# 2. Move to correct location
mv audiovisuals-desktop Code\desktop
cd Code\desktop

# 3. Install dependencies
npm install
npm install zustand react-plotly.js plotly.js video.js lucide-react @radix-ui/react-tabs @radix-ui/react-dialog
npm install -D @types/react @types/node @types/video.js @types/plotly.js tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 4. Start development
npm run tauri dev
```

---

## Pre-Installation Checklist

Before running the commands above, verify:

- [ ] Node.js installed (`node --version` shows v20+)
- [ ] npm installed (`npm --version` shows 10+)
- [ ] Rust installed (`rustc --version` shows 1.75+)
- [ ] cargo installed (`cargo --version` shows 1.75+)
- [ ] Python 3.12 accessible (`python --version` shows 3.12.0)
- [ ] Terminal restarted after installations

---

## Post-Installation Checklist

After running setup commands, verify:

- [ ] `Code/desktop/` directory exists
- [ ] `npm run tauri dev` opens app window
- [ ] Hot reload works (edit `src/App.tsx`, see changes)
- [ ] Python CLI accessible: `cd Code\backend && python cli.py --help`
- [ ] Ready to start Week 1 development

---

## Quick Links

**Setup Guides:**
- [Complete Setup Guide](../../docs/Phase3-MVP/SETUP_GUIDE.md)
- [Quick Start (5 min)](../../docs/Phase3-MVP/QUICK_START.md)
- [Project Structure](../../docs/Phase3-MVP/PROJECT_STRUCTURE.md)

**Development Docs:**
- [Technical Spec](../../docs/Phase3-MVP/TECHNICAL_SPEC.md)
- [Implementation Plan](../../docs/Phase3-MVP/IMPLEMENTATION_PLAN.md)
- [UX Research](../../docs/Phase3-MVP/UX_RESEARCH.md)

**Phase 2 (Python Backend):**
- [Backend README](../backend/README.md)
- [CLI Documentation](../backend/QUICK_START_AITOR.md)
- [Music Analysis](../backend/music_analysis/README.md)

---

## What Happens Next

### Week 1 (Foundation)
1. Create tab navigation shell (5 tabs)
2. Build Python CLI wrapper in Rust
3. Test IPC communication (React ↔ Rust ↔ Python)

### Week 3-4 (Synesthesia Tab)
1. File picker (drag & drop)
2. Style selector (from `Code/backend/styles/`)
3. Video generation workflow
4. Progress tracking
5. Video preview player

### Week 5-6 (Analysis Tab)
1. Analyzer selection UI
2. Parallel execution (5 analyzers)
3. Plotly chart integration
4. Export functionality

See [IMPLEMENTATION_PLAN.md](../../docs/Phase3-MVP/IMPLEMENTATION_PLAN.md) for complete timeline.

---

**This file will be replaced with the actual app README after setup.**

📋 **Current Status:** Waiting for tool installation  
📘 **Next:** Follow [SETUP_GUIDE.md](../../docs/Phase3-MVP/SETUP_GUIDE.md)

