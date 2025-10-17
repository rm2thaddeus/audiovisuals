# Week 1 Foundation Setup - Comprehensive Guide

**Date:** 2025-10-17  
**Target:** Complete React+Rust foundation with Python integration working  
**Duration:** 5 days  
**Status:** Ready to execute  

---

## Prerequisites Checklist

**Before starting, verify:**

```powershell
# ✅ PowerShell command to check all prerequisites
node --version          # Should show v20.x or v22.x
npm --version           # Should show 10.x.x or higher
rustc --version         # Should show 1.75.0 or higher
cargo --version         # Should show 1.75.0 or higher
python --version        # Should show 3.12.0 (already installed)
```

If any command fails, follow [../../docs/Phase3-MVP/SETUP_GUIDE.md](../../docs/Phase3-MVP/SETUP_GUIDE.md)

---

## Day 1-2: React Foundation

### Phase 1A Tasks

#### 1. Set up directory structure

```powershell
# ✅ CORRECT PowerShell commands

# Navigate to desktop app
Set-Location Code\desktop

# Create component directories
New-Item -ItemType Directory -Path "src\components\tabs" -Force
New-Item -ItemType Directory -Path "src\components\common" -Force
New-Item -ItemType Directory -Path "src\components\charts" -Force
New-Item -ItemType Directory -Path "src\store" -Force
New-Item -ItemType Directory -Path "src\hooks" -Force
New-Item -ItemType Directory -Path "src\types" -Force
New-Item -ItemType Directory -Path "src\utils" -Force

# Verify structure
Get-ChildItem -Recurse src\components
```

**Expected Output:**
```
src\components\
├── tabs\
├── common\
└── charts\
```

#### 2. Create Zustand stores (Week 1)

**File:** `src/store/appStore.ts`
```typescript
import { create } from 'zustand';

interface AppState {
  activeTab: string;
  theme: 'dark' | 'light';
  isLoading: boolean;
  error: string | null;
  
  setActiveTab: (tab: string) => void;
  setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: 'synesthesia',
  theme: 'dark',
  isLoading: false,
  error: null,
  
  setActiveTab: (tab) => set({ activeTab: tab }),
  setError: (error) => set({ error }),
}));
```

#### 3. Create TypeScript types (Week 1)

**File:** `src/types/index.ts`
```typescript
// Core types for the application

export interface GenerateVideoParams {
  audioPath: string;
  outputPath: string;
  resolution: '480p' | '720p' | '1080p';
  fps: 24 | 30 | 60;
  layers?: number;
  hiddenDim?: number;
}

export interface AnalyzeParams {
  audioPath: string;
  analyzers: Array<'tempo' | 'key' | 'chords' | 'structure' | 'genre'>;
}

export interface CommandResult {
  success: boolean;
  message: string;
  data?: any;
}

export interface ProgressEvent {
  progress: number;  // 0-100
  message: string;
}
```

#### 4. Create custom hooks (Week 1)

**File:** `src/hooks/usePythonCommand.ts`
```typescript
import { useState } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';
import type { CommandResult, ProgressEvent } from '../types';

export function usePythonCommand() {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const runCommand = async (
    command: string,
    params: any
  ): Promise<CommandResult> => {
    try {
      setIsLoading(true);
      setError(null);
      setProgress(0);

      // Listen for progress events
      const unlisten = await listen<ProgressEvent>('python-progress', (event) => {
        setProgress(event.payload.progress);
      });

      const result = await invoke<CommandResult>(command, params);

      unlisten();
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { runCommand, isLoading, progress, error };
}
```

#### 5. Test hot reload

```powershell
# Start development server
npm run tauri dev

# Expected: App window opens with 5 tabs
# Test: Edit src/App.tsx, save, should reload instantly
```

**Success Criteria:**
- [ ] App launches without errors
- [ ] 5 tabs visible and clickable
- [ ] Hot reload works (edit, save, instant refresh)
- [ ] Dark theme applied
- [ ] No console errors

---

## Day 2-3: Rust Foundation

### Phase 1B Tasks

#### 1. Create python.rs (Week 1 - DONE ✅)

File is ready at: `src-tauri/src/python.rs`

**Already includes:**
- ✅ Windows path handling comments
- ✅ PythonProcess struct
- ✅ spawn(), wait(), kill() methods
- ✅ Progress parsing
- ✅ Event emission
- ✅ Tests

#### 2. Create commands.rs (Week 1)

**File:** `src-tauri/src/commands.rs`
```rust
// NOTE: Windows-compatible IPC commands for Tauri desktop app

use crate::python::PythonProcess;
use tauri::Window;
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct GenerateVideoParams {
    pub audio_path: String,
    pub output_path: String,
    pub resolution: String,
    pub fps: u32,
}

#[derive(Serialize)]
pub struct CommandResult {
    pub success: bool,
    pub message: String,
    pub data: Option<String>,
}

/// Generate video using Python CLI
#[tauri::command]
pub async fn generate_video(
    params: GenerateVideoParams,
    window: Window,
) -> Result<CommandResult, String> {
    // TODO: Implementation in Week 3
    Ok(CommandResult {
        success: false,
        message: "Feature coming in Week 3-4".to_string(),
        data: None,
    })
}

/// Test Python process spawning
#[tauri::command]
pub async fn test_python(_window: Window) -> Result<CommandResult, String> {
    // Test command for Week 1 integration
    let mut process = PythonProcess::new(_window);
    
    // Run: python --version
    process.spawn("--version", vec![])?;
    let exit_code = process.wait()?;
    
    Ok(CommandResult {
        success: exit_code == 0,
        message: format!("Python test completed with exit code: {}", exit_code),
        data: None,
    })
}
```

#### 3. Update main.rs

**File:** `src-tauri/src/main.rs`
```rust
// ... existing code ...

mod commands;
mod python;

use commands::{generate_video, test_python};

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            generate_video,
            test_python,
        ])
        // ... rest of builder ...
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

#### 4. Test Rust compilation

```powershell
# Compile Rust backend
cargo build

# Expected: No errors, successful compilation
```

**Success Criteria:**
- [ ] Rust compiles without errors
- [ ] No warnings about unused imports
- [ ] python.rs module loads correctly
- [ ] Commands registered successfully

---

## Day 4-5: Integration Testing

### Phase 1C Tasks

#### 1. Create integration test

**File:** `src/components/TestIntegration.tsx`
```typescript
import { useState } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { CommandResult } from '../types';

export function TestIntegration() {
  const [result, setResult] = useState<CommandResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testPython = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await invoke<CommandResult>('test_python');
      setResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 p-6 bg-slate-800 border border-slate-700 rounded">
      <h3 className="font-bold">Integration Test</h3>
      
      <button
        onClick={testPython}
        disabled={loading}
        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded"
      >
        {loading ? 'Testing...' : 'Test Python Integration'}
      </button>

      {error && (
        <div className="p-3 bg-red-900 text-red-100 rounded">
          {error}
        </div>
      )}

      {result && (
        <div className="p-3 bg-green-900 text-green-100 rounded">
          <p><strong>Success:</strong> {result.success ? 'Yes' : 'No'}</p>
          <p><strong>Message:</strong> {result.message}</p>
        </div>
      )}
    </div>
  );
}
```

#### 2. Add test component to App.tsx

Add to SynesthesiaTab or create a test page.

#### 3. End-to-end test flow

```powershell
# Start dev server
npm run tauri dev

# In app:
# 1. Click "Test Python Integration" button
# 2. Watch console for success/failure
# 3. Should see python version output
```

**Success Criteria:**
- [ ] React button clicks invoke Rust command
- [ ] Rust spawns Python process
- [ ] Python --version executes successfully
- [ ] Result displays in React component
- [ ] No deadlocks or panics
- [ ] Clean shutdown

---

## PowerShell Command Reference

**For This Week:**

```powershell
# Navigate to project
Set-Location Code\desktop

# Development
npm run tauri dev                    # Start dev server (hot reload)
cargo build                          # Compile Rust backend
cargo test                           # Run Rust tests
npm test                             # Run React tests (when added)

# Directory operations
New-Item -ItemType Directory -Path "path" -Force
Get-ChildItem                        # List files (alias: ls)
Remove-Item -Path "file" -Force      # Delete file
Copy-Item -Path "src" -Destination "dst"  # Copy
Move-Item -Path "old" -Destination "new"  # Move

# Path handling (both work in Rust/PowerShell)
# Forward slash: "Code/desktop"
# Backslash: "Code\desktop"
```

---

## Success Criteria - Week 1 Complete

### Frontend ✅
- [ ] 5 tabs render correctly
- [ ] Dark theme applied (Tailwind)
- [ ] Tab switching works smoothly
- [ ] No console errors
- [ ] Hot reload functional
- [ ] Zustand stores initialized
- [ ] Types defined
- [ ] Hooks created

### Backend ✅
- [ ] Rust compiles cleanly
- [ ] python.rs module loads
- [ ] commands.rs defined
- [ ] IPC handlers registered
- [ ] PythonProcess tests pass
- [ ] No memory leaks (processes cleanup)

### Integration ✅
- [ ] React button → Rust command → Python executed
- [ ] Output captured and displayed
- [ ] Events stream correctly
- [ ] Error handling works
- [ ] Process cleanup automatic

---

## Troubleshooting

### npm: not found
```powershell
# Node.js not in PATH after install
# Solution: Restart terminal/PowerShell completely
# Restart computer if still failing
```

### Rust compile errors
```powershell
# Clear build cache
cargo clean
cargo build
```

### Hot reload not working
```powershell
# Restart dev server
# Stop: Press Ctrl+C
# Restart: npm run tauri dev
```

### IPC communication fails
1. Check browser console: F12 in app window
2. Check terminal for Rust panics
3. Verify Cargo.toml has tauri dependency
4. Check Tauri version matches npm version

---

## Next Steps (Week 2)

Once Week 1 complete:
1. Expand test_python command to real use cases
2. Implement generate_video command
3. Add file picker component
4. Implement progress tracking UI
5. Begin Synesthesia tab feature work (Week 3)

---

**Document Updated:** 2025-10-17  
**Status:** Ready for execution  
**Duration:** 5 days  
**Next:** Execute Day 1 tasks above

✅ **React foundation files created** - `src/App.tsx` + tab stubs  
✅ **Rust foundation files created** - `python.rs` + command stubs  
✅ **This guide created** - Ready to follow  

🚀 **Ready to build!**
