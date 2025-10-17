---
phase: 3
artifact: agents_desktop
project: audiovisuals-desktop
owner: Aitor
updated: 2025-10-17
status: Week 1 - Foundation Setup
sources:
  - PHASE_3_KICKOFF.md
  - TECHNICAL_SPEC.md
  - IMPLEMENTATION_PLAN.md
links:
  profile: ../../docs/Phase0-Alignment/PROFILE.yaml
  context: ../../docs/Phase0-Alignment/CONTEXT.md
  poc: ../../docs/Phase2-POC/POC_PLAN.md
  technical: ../../docs/Phase3-MVP/TECHNICAL_SPEC.md
  implementation: ../../docs/Phase3-MVP/IMPLEMENTATION_PLAN.md
---

# Desktop Application - Agent Coordination

**Status:** Week 1 - Foundation Setup  
**Current Phase:** Building Tauri skeleton with Python integration  
**Timeline:** Weeks 1-12 (see IMPLEMENTATION_PLAN.md)

---

## Agent Roster

### Frontend Developer (React/TypeScript)
**Purpose:** Build React UI components and state management

**Responsibilities:**
- Create Tab navigation shell (5 tabs)
- Implement Zustand state stores
- Design Plotly chart components
- Build Video.js player wrapper
- Style with Tailwind CSS

**Input:** UX mockups from TECHNICAL_SPEC.md  
**Output:** React components, hooks, type definitions  
**Success:** Tabs render, hot reload works, no console errors

---

### Backend Developer (Rust/Tauri)
**Purpose:** Build Rust backend for Python integration and IPC

**Responsibilities:**
- Create Python CLI wrapper (spawn processes, capture output)
- Implement IPC commands (generate_video, analyze_music, etc.)
- Handle file system access
- Manage progress event streaming
- Error handling and process cleanup

**Input:** Python CLI specifications (cli.py, music_analysis CLI)  
**Output:** Rust backend functions, IPC command handlers  
**Success:** Python processes spawn correctly, STDOUT captured, IPC works

---

### Integration Specialist
**Purpose:** Coordinate React ↔ Rust ↔ Python communication

**Responsibilities:**
- Test end-to-end workflows
- Validate data flow between layers
- Debug communication issues
- Create integration tests

**Input:** Frontend components + Rust commands  
**Output:** Working workflows (video generation, analysis, etc.)  
**Success:** React button clicks trigger Python CLI, results display

---

## Week 1 Coordination Plan

### Phase 1A: React Foundation (Days 1-2)

**Tasks:**
1. Create src/components/ directory structure
2. Build Tab navigation shell (src/App.tsx)
3. Create 5 empty tab components
4. Set up Zustand stores
5. Apply Tailwind dark theme

**Success Gate:** npm run tauri dev renders 5 tabs without errors

---

### Phase 1B: Rust Foundation (Days 2-3)

**Tasks:**
1. Create src-tauri/src/python.rs - Python wrapper
2. Create src-tauri/src/commands.rs - IPC commands
3. Implement process spawning and STDOUT capture
4. Add progress event emission
5. Test with simple Python script

**Success Gate:** Rust compiles, can spawn python --version

---

### Phase 1C: Integration Testing (Days 4-5)

**Tasks:**
1. Create test flows
2. Test React → Rust invocation
3. Test Rust → Python process spawn
4. Test STDOUT capture and event streaming
5. Document integration patterns

**Success Gate:** Click button in UI → Python runs → Result displays

---

## PowerShell Syntax Guide

NOTE: These commands run in Windows PowerShell, NOT bash/Unix shell.

### Common Commands (PowerShell vs Bash)

```powershell
# ✅ CORRECT PowerShell
npm run tauri dev
npm install zustand react-plotly.js
New-Item -ItemType Directory -Path "src/components" -Force
Remove-Item -Path "src/App.css" -Force
Copy-Item -Path "file.txt" -Destination "file_copy.txt"
Move-Item -Path "old_name" -Destination "new_name"

# ❌ WRONG - Unix/Bash (will fail in PowerShell)
npm run tauri dev                        # Same, OK
npm install zustand                     # Same, OK
mkdir src/components                    # Use New-Item instead!
rm src/App.css                          # Use Remove-Item instead!
cp file.txt file_copy.txt              # Use Copy-Item instead!
mv old_name new_name                   # Use Move-Item instead!
```

### Path Handling (Windows)

```powershell
# ✅ CORRECT - Both forward and backslash work in PowerShell
$path1 = "Code\desktop"
$path2 = "Code/desktop"          # Also valid in modern PowerShell
$pythonPath = "C:\Python312\python.exe"

# ❌ WRONG - Unix paths (won't work on Windows)
$path = "/home/user/code"        # Will fail - Linux path
$python = "/usr/bin/python"      # Will fail - Linux path
```

### Navigating Directories

```powershell
# ✅ CORRECT
Set-Location Code\desktop         # Change directory
Get-ChildItem                     # List files (equivalent to ls)
Get-Location                      # Show current directory (pwd)
pwd                              # Also works in modern PowerShell

# ❌ WRONG
cd Code/desktop                  # Might work but Set-Location is standard
ls                               # Might work but Get-ChildItem is standard
pwd                              # Modern PowerShell supports it
```

### Running Commands

```powershell
# ✅ CORRECT - Run Node/npm commands
npm run tauri dev               # Start dev server

# ✅ CORRECT - Run Python
python --version               # Check Python version
python Code\backend\cli.py     # Run Python script

# ❌ WRONG - Don't mix shells
npm run tauri dev &            # Background jobs use different syntax
python -c "print('hello')"     # Works but be careful with quotes
```

---

## Code Examples

### Rust: Process Spawning (src-tauri/src/python.rs)

```rust
use std::process::{Command, Stdio};

pub fn spawn_python_process(script: &str, args: Vec<&str>) -> std::io::Result<()> {
    // ✅ CORRECT: Windows-compatible path handling
    let output = Command::new("python")
        .arg(script)
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()?;
    
    println!("stdout: {}", String::from_utf8_lossy(&output.stdout));
    Ok(())
}

// ❌ WRONG: Unix paths will fail
fn bad_example() {
    Command::new("/usr/bin/python3")  // Doesn't exist on Windows!
        .spawn();
}
```

### React: Invoking Rust Commands (src/App.tsx)

```typescript
import { invoke } from '@tauri-apps/api/tauri';

// ✅ CORRECT: Invoke Rust command
const handleGenerateVideo = async () => {
    try {
        const result = await invoke('generate_video', {
            audioPath: 'docs/Audio/sample.mp3',
            outputPath: 'output.mp4',
            resolution: '720p',
            fps: 30
        });
        console.log('Success:', result);
    } catch (error) {
        console.error('Error:', error);
    }
};

// ❌ WRONG: Don't call Python directly from React
const bad_example = async () => {
    const result = await fetch('python://cli.py');  // This won't work!
};
```

---

## File Structure Being Created

```
Code/desktop/
├── src/
│   ├── components/
│   │   ├── tabs/
│   │   │   ├── SynesthesiaTab.tsx    # Week 3-4
│   │   │   ├── AnalysisTab.tsx       # Week 5-6
│   │   │   ├── StylesTab.tsx         # Week 7-8
│   │   │   ├── ExplorerTab.tsx       # Week 9-10 (post-MVP)
│   │   │   └── ProjectsTab.tsx       # Week 9-10 (post-MVP)
│   │   ├── common/
│   │   │   ├── FileDropzone.tsx      # Week 3
│   │   │   ├── ProgressBar.tsx       # Week 3
│   │   │   ├── VideoPlayer.tsx       # Week 3
│   │   │   └── Button.tsx            # Week 1
│   │   └── charts/
│   │       ├── TempoChart.tsx        # Week 5
│   │       ├── KeyChart.tsx          # Week 5
│   │       └── (more in Week 5-6)
│   ├── store/
│   │   ├── appStore.ts              # Week 1
│   │   ├── synesthesiaStore.ts       # Week 3
│   │   ├── analysisStore.ts          # Week 5
│   │   └── stylesStore.ts            # Week 7
│   ├── hooks/
│   │   ├── usePythonCommand.ts       # Week 1
│   │   ├── useVideoGeneration.ts     # Week 3
│   │   └── useProgress.ts            # Week 1
│   ├── types/
│   │   ├── index.ts                  # Week 1
│   │   ├── music.ts                  # Week 1
│   │   ├── generation.ts             # Week 1
│   │   └── python.ts                 # Week 1
│   ├── App.tsx                       # Week 1 - Tab navigation
│   ├── main.tsx                      # Week 1
│   └── index.css                     # Week 1 - Global Tailwind
│
├── src-tauri/src/
│   ├── main.rs                       # Week 1 - Entry point
│   ├── python.rs                     # Week 1 - Process spawning
│   ├── commands.rs                   # Week 1 - IPC commands
│   ├── events.rs                     # Week 2 - Event handling
│   └── lib.rs
│
├── AGENTS.md                         # This file
└── README.md
```

---

## Next Handoff (End of Week 1)

**Complete Deliverables:**
- ✅ 5 tabs rendering correctly
- ✅ Python process spawning works
- ✅ IPC communication functional
- ✅ Integration tests passing
- ✅ No known blockers

**Gate Before Week 2:**
All integration tests must pass. No deadlocks, no memory leaks, clean error handling.

---

**Updated:** 2025-10-17  
**Status:** Week 1 Foundation Setup in Progress  
**Next:** Begin Phase 1A (React Foundation)
