# Audio Feature Explorer - Desktop App

**Status:** ✅ **Week 1 Foundation Setup Ready**  
**Tech Stack:** Tauri 2 + React 18 + TypeScript + Tailwind CSS + Rust  
**Phase:** Phase 3 MVP  
**Target:** Complete by Week 12  

---

## 🎯 Quick Start

### Prerequisites
Before you start, install:
- ✅ Node.js (v20+)
- ✅ Rust (1.75+)
- ✅ Python 3.12 (already installed)

See [../../docs/Phase3-MVP/SETUP_GUIDE.md](../../docs/Phase3-MVP/SETUP_GUIDE.md) for setup instructions.

### Run Development Server

```powershell
# ✅ CORRECT PowerShell commands

Set-Location Code\desktop
npm run tauri dev

# Expected: App window opens with 5 tabs
# Hot reload: Edit src/App.tsx and save to see changes
```

---

## 📁 Directory Structure

```
Code/desktop/
├── src/                          # React frontend
│   ├── components/
│   │   ├── tabs/                # Tab pages (5 tabs)
│   │   ├── common/              # Reusable components
│   │   └── charts/              # Data visualization
│   ├── store/                   # Zustand state management
│   ├── hooks/                   # Custom React hooks
│   ├── types/                   # TypeScript types
│   ├── App.tsx                  # Main component (tab navigation)
│   └── main.tsx                 # Entry point
│
├── src-tauri/                   # Rust backend
│   └── src/
│       ├── main.rs             # Tauri entry point
│       ├── python.rs           # Python process wrapper ✅
│       ├── commands.rs         # IPC command handlers ✅
│       └── lib.rs              # Module exports
│
├── AGENTS.md                    # Agent coordination guide
├── WEEK_1_SETUP.md             # Detailed setup instructions
└── README.md                    # This file
```

---

## 📅 Development Timeline

### ✅ Week 1: Foundation (CURRENT)
- ✅ React Tab Navigation
- ✅ Zustand state management
- ✅ Rust Python wrapper (python.rs)
- ✅ IPC command system
- ✅ Integration tests

**Files Ready:**
- `src/App.tsx` - 5-tab navigation ✅
- `src/components/tabs/*.tsx` - Tab stubs ✅
- `src-tauri/src/python.rs` - Process spawning ✅
- `Code/desktop/WEEK_1_SETUP.md` - Complete guide ✅

### Week 2-3: Synesthesia Tab
- File picker (drag & drop)
- Style selector
- Video generation workflow
- Progress tracking UI
- Video preview player

### Week 4-6: Analysis Tab
- Audio file selector
- 5-analyzer selection
- Plotly charts integration
- Data export
- Results caching

### Week 7-8: Styles Tab
- Style library browser
- Style metadata viewing
- Custom style training UI
- Style export/import

### Week 9-10: Explorer Tab (Post-MVP)
- Parameter space visualization
- Preset management
- Real-time preview

### Week 11-12: Projects Tab (Post-MVP)
- File management
- Project organization
- Quick actions

---

## 🔧 For Developers

### PowerShell Command Reference

```powershell
# NOTE: Use PowerShell syntax on Windows (not bash!)

# Development
npm run tauri dev          # Start dev server with hot reload
npm run build              # Build production app
cargo build                # Compile Rust backend
cargo test                 # Run Rust unit tests

# File operations (NOT bash equivalents!)
New-Item -ItemType Directory -Path "src/components" -Force
Remove-Item -Path "file.txt" -Force
Copy-Item -Path "src" -Destination "src-backup"
Move-Item -Path "old" -Destination "new"

# Paths (both work)
"Code\desktop"             # Backslash (Windows native)
"Code/desktop"             # Forward slash (also works)
```

### React Development

**Hot Reload:** Automatically reloads when you edit files in `src/`

**Debugging:**
1. Press `F12` in the app window to open DevTools
2. Check Console for errors
3. React DevTools extension recommended

**TypeScript:** Full type safety in components

**Tailwind CSS:** Dark theme pre-configured in `tailwind.config.js`

### Rust Development

**IPC Commands:** Add new commands in `src-tauri/src/commands.rs`

```rust
#[tauri::command]
pub async fn my_new_command(window: Window) -> Result<String, String> {
    // Implementation
    Ok("Success".to_string())
}
```

Then register in `main.rs`:
```rust
.invoke_handler(tauri::generate_handler![my_new_command])
```

**Python Integration:** Use `python.rs` PythonProcess struct:

```rust
let mut process = PythonProcess::new(window);
process.spawn("Code\\backend\\cli.py", vec!["--help"])?;
let exit_code = process.wait()?;
```

---

## 📖 Documentation

**Project Level:**
- [AGENTS.md](./AGENTS.md) - Agent coordination roles
- [WEEK_1_SETUP.md](./WEEK_1_SETUP.md) - Week 1 detailed guide

**Phase 3 Level:**
- [../../docs/Phase3-MVP/TECHNICAL_SPEC.md](../../docs/Phase3-MVP/TECHNICAL_SPEC.md) - Architecture details
- [../../docs/Phase3-MVP/IMPLEMENTATION_PLAN.md](../../docs/Phase3-MVP/IMPLEMENTATION_PLAN.md) - Full 12-week plan
- [../../docs/Phase3-MVP/UX_RESEARCH.md](../../docs/Phase3-MVP/UX_RESEARCH.md) - UI mockups and flows

**Backend (Python):**
- [../backend/README.md](../backend/README.md) - Python CLI docs
- [../backend/QUICK_START_AITOR.md](../backend/QUICK_START_AITOR.md) - CLI quick start

---

## ✨ Key Features (Week 1 Foundation)

### ✅ Completed
- Tab navigation system
- State management (Zustand)
- Python process integration (Rust)
- Type-safe IPC communication
- Hot reload development
- Dark theme UI

### 🚀 Coming (Week 3-4)
- Video generation from audio
- Real-time progress tracking
- Style library browser
- Output video preview

### 🔮 Future (Week 5-12)
- Music semantic analysis (5 analyzers)
- Interactive Plotly visualizations
- Parameter exploration
- Project management

---

## 🐛 Troubleshooting

**npm: not found**
```powershell
# Node.js not installed or not in PATH
# Solution: Restart terminal after installation
# Or reinstall Node.js from https://nodejs.org/
```

**Rust compile errors**
```powershell
cargo clean
cargo build
```

**Hot reload not working**
```powershell
# Stop server: Ctrl+C
# Restart: npm run tauri dev
```

**IPC communication fails**
1. Open DevTools: F12 in app window
2. Check Console for error messages
3. Verify command is registered in main.rs
4. Check Tauri logs in terminal

See [WEEK_1_SETUP.md](./WEEK_1_SETUP.md) for more troubleshooting.

---

## 🤝 Contributing

Follow patterns in [AGENTS.md](./AGENTS.md):
- Small, reviewable changes
- Comment non-obvious code
- Test before commit
- Use proper PowerShell commands (not bash)
- Update this README if adding major features

---

**Phase 3 MVP • Week 1 Foundation Setup Complete**  
**Ready for development** ✅  
**Next Step:** Follow [WEEK_1_SETUP.md](./WEEK_1_SETUP.md)

