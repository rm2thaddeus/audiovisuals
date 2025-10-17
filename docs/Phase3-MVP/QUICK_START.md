# Phase 3 MVP - Quick Start

**Goal:** Get from "tools installed" to "app running" in 5 minutes

---

## Prerequisites Checklist

```powershell
# Verify all tools are installed:
node --version    # ✅ Should show v20+ or v22+
npm --version     # ✅ Should show 10.x.x+
rustc --version   # ✅ Should show 1.75.0+
cargo --version   # ✅ Should show 1.75.0+
python --version  # ✅ Should show 3.12.0 (already installed)
```

If any fail, see **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** for installation instructions.

---

## Step 1: Create Tauri Project (2 minutes)

```powershell
# Navigate to project root
cd C:\Users\aitor\audiovisual\audiovisuals

# Create Tauri app interactively
npm create tauri-app@latest
```

**Answer prompts:**
```
Project name: audiovisuals-desktop
Package manager: npm
UI template: React
Add TypeScript? Yes
UI flavor: TypeScript
```

**Move to correct location:**
```powershell
mv audiovisuals-desktop Code\desktop
cd Code\desktop
```

---

## Step 2: Install Dependencies (2 minutes)

```powershell
# Base dependencies
npm install

# Required packages
npm install zustand react-plotly.js plotly.js video.js lucide-react @radix-ui/react-tabs @radix-ui/react-dialog

# Dev dependencies
npm install -D @types/react @types/node @types/video.js @types/plotly.js tailwindcss postcss autoprefixer

# Initialize Tailwind
npx tailwindcss init -p
```

---

## Step 3: Configure Tailwind (<1 minute)

**Edit `tailwind.config.js`:**
```javascript
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: { purple: '#6B46C1', blue: '#3B82F6', pink: '#EC4899' },
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
      },
    },
  },
  plugins: [],
}
```

**Edit `src/index.css`:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  @apply bg-slate-900 text-slate-100;
}
```

---

## Step 4: Start Development Server (<1 minute)

```powershell
npm run tauri dev
```

**Expected:**
- Vite dev server starts
- Rust compiles (first time: ~1 minute)
- Desktop window opens
- Shows default Tauri welcome screen

**Success!** 🎉 Tauri is working!

---

## Step 5: Test Python Integration (Optional)

```powershell
# In a new terminal:
cd Code\backend

# Test CLI
python cli.py --help

# Quick video generation test (30s clip)
python cli.py "docs/Audio/Zyryab.mp3" test.mp4 --resolution 480p --duration 30 --fps 24
```

---

## Quick Reference

### Development Commands

```powershell
# Start dev server (hot reload)
npm run tauri dev

# Build for production
npm run tauri build

# Run tests (when we add them)
npm test
```

### Project Structure

```
Code/
├── backend/     # Python CLI tools (Phase 2 - done!)
└── desktop/     # Tauri app (Phase 3 - building now!)
    ├── src/         # React frontend
    ├── src-tauri/   # Rust backend
    └── package.json
```

### Key Files

- `src/App.tsx` - Main React component
- `src-tauri/src/main.rs` - Rust entry point
- `src-tauri/tauri.conf.json` - Tauri configuration

---

## Next Steps

### Week 1 (Foundation)

1. **Create tab navigation:**
   - Edit `src/App.tsx`
   - Add 5 tabs: Synesthesia, Analysis, Styles, Explorer, Projects

2. **Python wrapper in Rust:**
   - Create `src-tauri/src/python.rs`
   - Test spawning Python processes

3. **IPC communication:**
   - Create `src-tauri/src/commands.rs`
   - Test invoke/emit between React ↔ Rust

### Week 3-4 (Synesthesia Tab)

- File picker
- Style selector
- Video generation
- Progress tracking
- Video preview

See **[IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)** for full timeline.

---

## Troubleshooting

### Window won't open
```powershell
# Check for errors:
cat src-tauri\target\debug\audiovisuals-desktop.log
```

### Rust compile errors
```powershell
cargo clean
npm run tauri dev
```

### Python not found
Check path in `src-tauri/src/main.rs`:
```rust
let python_path = "python"; // or full path
```

---

## Resources

- **Full setup guide:** [SETUP_GUIDE.md](./SETUP_GUIDE.md)
- **Project structure:** [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)
- **Technical spec:** [TECHNICAL_SPEC.md](./TECHNICAL_SPEC.md)
- **Implementation plan:** [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)

---

**Status:** ✅ Setup Complete → Begin Week 1 Development

🚀 **Ready to build!**

