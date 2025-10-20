# Quick Fix Guide - Desktop App Integration Issues

**For:** Rapid reference when fixing critical issues  
**See Also:** `CRITICAL_ISSUES_ANALYSIS.md` (detailed), `INVESTIGATION_SUMMARY.md` (overview)

---

## 🚨 The 5 Problems (One-Liner Each)

1. **Duplicate file buttons** - Remove HTML input, keep only Tauri dialog
2. **Path resolution fails** - Web API gives filename, need full path
3. **Dialog plugin disabled** - Enable in Cargo.toml + lib.rs + tauri.conf.json
4. **Metadata is zeros** - Connect Rust to Python for real audio info
5. **Python CLI unreachable** - Fix path handling so CLI gets valid inputs

---

## ⚡ Quick Fixes (Copy-Paste Ready)

### Fix 1: Enable Tauri Dialog Plugin

**File:** `Code/desktop/src-tauri/Cargo.toml`
```toml
[dependencies]
tauri-plugin-dialog = "2"  # Add this line
```

**File:** `Code/desktop/src-tauri/src/lib.rs`
```rust
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())  // Uncomment this
        .invoke_handler(tauri::generate_handler![
```

**File:** `Code/desktop/src-tauri/tauri.conf.json`
```json
"plugins": {
  "shell": {
    "open": true
  },
  "dialog": {
    "all": true
  }
}
```

### Fix 2: Update TauriFileDialog to Use Real API

**File:** `Code/desktop/src/components/common/TauriFileDialog.tsx`
```typescript
import { open } from '@tauri-apps/plugin-dialog';
import { log } from '../../utils/logger';
import type { AudioFile } from '../../types';

export function TauriFileDialog({ onFileSelected, onError }: TauriFileDialogProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleFileSelect = useCallback(async () => {
    try {
      setIsLoading(true);
      await log.userAction('file_dialog_open', 'TauriFileDialog');

      const selected = await open({
        multiple: false,
        filters: [{
          name: 'Audio Files',
          extensions: ['mp3', 'wav', 'flac', 'aiff', 'm4a'],
        }],
      });

      if (selected && typeof selected === 'string') {
        const audioFile: AudioFile = {
          path: selected,
          name: selected.split(/[\\/]/).pop() || 'unknown',
          size: 0,
          format: selected.split('.').pop()?.toLowerCase() || 'unknown',
        };

        await log.info('File selected via dialog', {
          component: 'TauriFileDialog',
          metadata: { filePath: audioFile.path },
        });

        onFileSelected(audioFile);
      }
    } catch (error) {
      await log.logError(error as Error, {
        component: 'TauriFileDialog',
      });
      onError?.(error instanceof Error ? error.message : 'Failed to open file dialog');
    } finally {
      setIsLoading(false);
    }
  }, [onFileSelected, onError]);

  return (
    <button onClick={handleFileSelect} disabled={isLoading} className="...">
      {isLoading ? 'Opening...' : 'Select Audio File'}
    </button>
  );
}
```

### Fix 3: Remove HTML File Input from FileDropzone

**File:** `Code/desktop/src/components/common/FileDropzone.tsx`

Remove lines 181-188 (the `<input ref={inputRef}>` element) and lines 217-225 (the "browse files" button).

Keep only:
- Drag-and-drop zone
- TauriFileDialog button

### Fix 4: Implement Real Metadata Extraction

**File:** `Code/desktop/src-tauri/src/file_manager.rs`
```rust
#[tauri::command]
pub async fn get_file_metadata(path: String) -> Result<AudioFileMetadata, String> {
    if !Path::new(&path).exists() {
        return Err("File not found".to_string());
    }

    // Use ffprobe to get metadata
    let output = std::process::Command::new("ffprobe")
        .args(&[
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            &path
        ])
        .output()
        .map_err(|e| format!("Failed to run ffprobe: {}", e))?;

    if !output.status.success() {
        return Err("ffprobe failed".to_string());
    }

    let json: serde_json::Value = serde_json::from_slice(&output.stdout)
        .map_err(|e| format!("Failed to parse ffprobe output: {}", e))?;

    let format = json["format"].as_object()
        .ok_or("Invalid ffprobe format")?;

    let duration = format["duration"]
        .as_str()
        .and_then(|s| s.parse::<f32>().ok())
        .unwrap_or(0.0);

    let bitrate = format["bit_rate"]
        .as_str()
        .and_then(|s| s.parse::<u32>().ok())
        .unwrap_or(0);

    Ok(AudioFileMetadata {
        path,
        duration,
        bitrate,
        sample_rate: 44100, // Would need to parse from streams
    })
}
```

---

## 🧪 Test After Each Fix

### After Fix 1 (Dialog Plugin)
```powershell
cd Code/desktop/src-tauri
cargo check  # Should compile without errors
```

### After Fix 2 (TauriFileDialog)
```powershell
cd Code/desktop
npm run tauri:dev
# Click "Select Audio File" → Should open native file picker
```

### After Fix 3 (Remove HTML Input)
- UI should have only ONE file selection button
- No more confusing duplicate UI

### After Fix 4 (Metadata)
- Select an audio file
- Should see real duration (e.g., "3:25" not "0:00")
- Should see real bitrate (e.g., "320 kbps" not "0 kbps")

---

## 📍 Code Locations Reference

| Issue | File | Lines | What to Change |
|-------|------|-------|----------------|
| Duplicate buttons | FileDropzone.tsx | 217-233 | Remove HTML input button |
| Fake path usage | FileDropzone.tsx | 84 | Remove file.name usage |
| prompt() fallback | TauriFileDialog.tsx | 22 | Replace with open() API |
| Plugin disabled | lib.rs | ~30 | Uncomment .plugin(tauri_plugin_dialog::init()) |
| Plugin config | tauri.conf.json | plugins.dialog | Add proper config |
| Plugin dependency | Cargo.toml | dependencies | Add tauri-plugin-dialog |
| Metadata placeholder | file_manager.rs | 82-109 | Call ffprobe or Python CLI |
| Duration placeholder | file_manager.rs | 100-109 | Implement proper extraction |

---

## 🎯 Success Criteria

### After All Fixes Applied

**User can:**
1. ✅ Click "Select Audio File" → Native dialog opens
2. ✅ Browse files visually → Select MP3/WAV/FLAC
3. ✅ See real file metadata → Duration, bitrate shown correctly
4. ✅ Click "Generate Video" → Python CLI executes successfully
5. ✅ Watch progress bar → Updates in real-time
6. ✅ Play generated video → Audio synced, visuals correct

**No more:**
- ❌ Duplicate buttons
- ❌ Manual path entry via prompt()
- ❌ "File does not exist" errors
- ❌ "Duration: 0:00" for all files
- ❌ Silent failures

---

## 💡 Quick Tips

### If Dialog Still Doesn't Work
1. Clear Rust build cache: `rm -rf src-tauri/target`
2. Reinstall npm packages: `rm -rf node_modules && npm install`
3. Check Tauri version: `cargo tree | grep tauri-plugin-dialog`

### If Metadata Shows Zeros
1. Verify ffprobe installed: `ffprobe -version`
2. Check file path escaping (Windows backslashes)
3. Add logging before ffprobe call
4. Test with absolute path manually

### If Video Generation Fails
1. Check Python CLI works standalone: `python cli.py test.mp3 out.mp4`
2. Verify file path format (forward slashes work on Windows too)
3. Check debug console for Rust command logs
4. Verify Python is in PATH

---

## 🔧 Development Workflow

1. **Make one fix at a time**
2. **Test immediately after each fix**
3. **Check debug console for errors**
4. **Document any new issues found**
5. **Update AGENTS.md when fixed**

---

## 📚 Related Documents

- **`CRITICAL_ISSUES_ANALYSIS.md`** - Full technical analysis (600+ lines)
- **`INVESTIGATION_SUMMARY.md`** - Executive overview
- **`AGENTS.md`** - Project status and coordination
- **`LOGGING_AND_TELEMETRY_SETUP.md`** - Debug tools guide
- **`COMPILATION_FIXES.md`** - Past issues resolved

---

**Last Updated:** 2025-10-19  
**Status:** Ready to fix  
**Estimated Time:** 4-6 hours for P0 fixes

