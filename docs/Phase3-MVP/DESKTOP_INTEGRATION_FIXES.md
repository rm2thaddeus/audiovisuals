---
title: Desktop Integration Fixes (P0/P1)
updated: 2025-10-19
scope: /docs/Phase3-MVP
links:
  critical_issues: ../../Code/desktop/CRITICAL_ISSUES_ANALYSIS.md
  impl_plan: ./IMPLEMENTATION_PLAN.md
  tech_spec: ./TECHNICAL_SPEC.md
  arch_integration: ./ARCHITECTURE_INTEGRATION.md
---

# Desktop Integration Fixes (P0/P1)

Purpose
- Unblock core flow: Select file → Show metadata → Generate video.
- Replace web file APIs with Tauri-native capabilities and add robust logging.

Summary of Fixes
- Enable native dialogs (v2)
  - Rust: add plugin and init
    - `src-tauri/Cargo.toml`: `tauri-plugin-dialog = "2"`
    - `src-tauri/src/lib.rs`: `.plugin(tauri_plugin_dialog::init())`
  - Frontend: `npm i @tauri-apps/plugin-dialog`; use `open({ filters: [...] })`
  - Resource: https://github.com/tauri-apps/tauri-plugin-dialog/tree/v2

- Absolute paths end-to-end
  - Use dialog return (absolute path string) in `FileDropzone`
  - Send full path to Rust `validate_audio_file` and Python CLI

- Real metadata extraction
  - Option A — ffprobe (FFmpeg)
    - Add `tauri-plugin-shell = "2"`, `.plugin(tauri_plugin_shell::init())`
    - Run: `ffprobe -v quiet -of json -show_format -show_streams <audio>`
    - Parse JSON for duration/bitrate/sample_rate/channels/codec
    - Resource: https://ffmpeg.org/ffprobe.html
  - Option B — Pure Rust (Symphonia)
    - Crate: `symphonia` (+ format/codec features)
    - Read container → stream → decoder → derive duration & audio params
    - Resources: https://crates.io/crates/symphonia, https://docs.rs/symphonia, examples: https://github.com/pdeljanov/Symphonia/tree/master/symphonia/examples

- Visible error logging
  - Add `tauri-plugin-log = "2"` and enable Webview/Stdout/LogDir targets
  - Frontend: `@tauri-apps/plugin-log` + `attachConsole()`; pipe Rust `log` macros
  - Resource: https://github.com/tauri-apps/tauri-plugin-log/tree/v2

- Cleanup UI
  - Remove duplicate file selection buttons
  - Remove `prompt()` fallback

Optional
- Drag-and-drop files via window `FileDrop` events at the Rust layer or frontend drop handlers; validate path in Rust.

Validation Checklist
- Native dialog returns an absolute path on Windows/macOS/Linux
- Rust validation passes for selected file (`PathBuf::exists == true`)
- Metadata panel shows real duration/bitrate/sample rate/channels
- Python CLI receives the same absolute `audio_path` and generates video
- Errors are visible in the in-app console and persisted to log files

References (Authoritative)
- Dialog plugin (v2): https://github.com/tauri-apps/tauri-plugin-dialog/tree/v2
- Shell plugin (v2): https://github.com/tauri-apps/tauri-plugin-shell/tree/v2
- Log plugin (v2): https://github.com/tauri-apps/tauri-plugin-log/tree/v2
- ffprobe docs: https://ffmpeg.org/ffprobe.html
- Symphonia: https://crates.io/crates/symphonia, https://docs.rs/symphonia

