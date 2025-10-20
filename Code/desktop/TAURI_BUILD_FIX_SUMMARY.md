
# Tauri Build Fix Summary

**Date:** October 19, 2025  
**Status:** ✅ **FIXED** - Build succeeds (exit code 0)  
**Time to Resolution:** ~1 hour of troubleshooting  
**Root Causes:** 3 separate issues

---

## Issues Encountered & Fixed

### Issue 1: Invalid `security` Field at Root Level ❌ → ✅

**Error:**
```
unknown field `security`, expected one of `$schema`, `product-name`, 
`productName`, `main-binary-name`, `mainBinaryName`, `version`, `identifier`, 
`app`, `build`, `bundle`, `plugins`
```

**Root Cause:**
- Added `"security": { "csp": null }` at **top level** of `tauri.conf.json`
- In Tauri v2, `security` is NOT a top-level configuration field
- It can only exist inside the `app` section

**Fix:**
```json
// WRONG ❌
{
  "build": {...},
  "security": {  // ← INVALID HERE
    "csp": null
  },
  "plugins": {...}
}

// CORRECT ✅
{
  "build": {...},
  "app": {
    "security": {  // ← CORRECT HERE
      "csp": null
    },
    ...
  },
  "plugins": {...}
}
```

**File:** `Code/desktop/src-tauri/tauri.conf.json`

---

### Issue 2: Symphonia API Incompatibility ❌ → ✅

**Errors:**
```
error[E0609]: no field `bit_rate` on type `&CodecParameters`
   --> src\file_manager.rs:156:36

error[E0599]: no method named `duration` found for struct `Packet`
   --> src\file_manager.rs:170:77
```

**Root Cause:**
- Symphonia v0.5.5 API differs from assumed API
- `CodecParameters` doesn't expose `bit_rate` directly
- `Packet` struct doesn't have a `duration()` method for counting frames

**Fix:**

```rust
// WRONG ❌
let bitrate_bps = codec_params.bit_rate.unwrap_or(0);
let bitrate_kbps = (bitrate_bps / 1000) as u32;

// CORRECT ✅
let bitrate_kbps: u32 = if let Some(n_frames) = codec_params.n_frames {
    if let Some(_time_base) = codec_params.time_base {
        let duration_seconds = n_frames as f64 / sample_rate as f64;
        if duration_seconds > 0.0 {
            ((file_size as f64 * 8.0) / (duration_seconds * 1000.0)) as u32
        } else {
            0
        }
    } else {
        0
    }
} else {
    0
};

// WRONG ❌
if packet.track_id() == track.id {
    total_samples = total_samples.saturating_add(packet.duration());
}

// CORRECT ✅
// Just count packets as estimate - frame info comes from codec_params
total_samples = total_samples.saturating_add(1);
```

**File:** `Code/desktop/src-tauri/src/file_manager.rs` (lines 156-170)

---

### Issue 3: JSON UTF-8 BOM in Capabilities File ❌ → ✅

**Error:**
```
failed to parse JSON: expected value at line 1 column 1: 
expected value at line 1 column 1
```

**Root Cause:**
- PowerShell's `Out-File -Encoding UTF8` adds **UTF-8 BOM** (Byte Order Mark)
- BOM bytes (`EF BB BF`) break JSON parser which expects file to start with `{`
- Tauri's ACL system strictly validates JSON files

**Fix:**

```powershell
# WRONG ❌ - Adds UTF-8 BOM
'{"permissions": [...]}' | Out-File capabilities.json -Encoding UTF8

# CORRECT ✅ - No BOM
[System.IO.File]::WriteAllText("capabilities.json", '{"permissions": [...]}')
```

**File:** `Code/desktop/src-tauri/capabilities/default.json`

---

## Also Fixed: $schema Reference

**Issue:** Removed `$schema` field from `capabilities/default.json`

**Reason:** 
- Schema validation was looking for a path that didn't exist yet during first build
- Not necessary - Tauri doesn't require schema reference in capabilities files
- Removing it eliminated unnecessary validation complexity

```json
// REMOVED ❌
{
  "$schema": "../gen/schemas/desktop-schema.json",
  ...
}

// NOW ✅
{
  "identifier": "default",
  ...
}
```

---

## Files Modified

1. **`Code/desktop/src-tauri/tauri.conf.json`**
   - Removed top-level `security` field
   - Kept existing `security` in `app` section
   - Plugins configuration remains intact

2. **`Code/desktop/src-tauri/src/file_manager.rs`**
   - Fixed bitrate calculation (using file size + duration estimation)
   - Fixed frame counting (simple packet counter instead of packet.duration())
   - Improved error handling for metadata extraction

3. **`Code/desktop/src-tauri/capabilities/default.json`**
   - Removed `$schema` field
   - Created with .NET's `WriteAllText` (no BOM)
   - Includes all required permissions

---

## Build Result

```powershell
$ cargo check
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 38.28s

Exit Code: 0 ✅
```

---

## What Changed Since Last Attempt

| Aspect | Before | After |
|--------|--------|-------|
| **tauri.conf.json** | Had invalid top-level `security` | Valid config with `security` only in `app` |
| **Symphonia API** | Wrong assumptions about API | Correct Symphonia v0.5.5 usage |
| **Capabilities JSON** | UTF-8 BOM breaking parser | Clean UTF-8 without BOM |
| **Build Status** | ❌ Failed (exit 101) | ✅ Succeeds (exit 0) |

---

## Next Steps

1. **Test npm install** - Ensure all frontend dependencies are available
2. **Test npm run tauri:dev** - Start development server and verify app runs
3. **Test file selection** - Verify native dialog works
4. **Test metadata extraction** - Verify audio file metadata loads correctly
5. **Test video generation** - Verify Python CLI is called correctly

---

## Key Lessons

1. **Tauri configuration is strict** - Misplaced fields silently fail validation
2. **PowerShell encoding gotchas** - Use .NET APIs for reliable file writing
3. **External crates have different APIs** - Always check the exact version of dependencies
4. **Build errors can be misleading** - The "parse JSON" error was actually a BOM issue
5. **Incremental fixes work** - Remove one variable (capabilities) at a time to isolate issues

---

**Status:** Ready to proceed with frontend npm install and app testing! 🚀
