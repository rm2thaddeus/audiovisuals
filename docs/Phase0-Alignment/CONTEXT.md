---
phase: 0
artifact: project_context
project: audio_feature_explorer
owner: Aitor Patino Diaz
updated: 2025-10-17
sources:
  - Research Proposal: Audio Feature Explorer (Local Desktop Edition)
  - CV: AI framework designer with audio/video analysis experience
links:
  profile: ./docs/Phase0-Alignment/PROFILE.yaml
  context: ./docs/Phase0-Alignment/CONTEXT.md
---

Main Idea (one sentence)
- Build a desktop audio reactive visualization app that analyzes local audio files using ML models (OpenL3, YAMNet, VGGish) and renders bio-inspired fractal visuals, inspired by MilkDrop presets, with a Tauri-based cross-platform architecture.

Environment and Constraints
- OS: Windows (primary), cross-platform target (Windows/macOS/Linux)
- Editor: Cursor with AI assistance
- Runtime: Tauri (Rust) + Python sidecar + WebView frontend
- Repos/Permissions: Local development, potential open-source release

Goals and Non-Goals
- Goals:
  - Local-first audio analysis with ML models (OpenL3, YAMNet, VGGish)
  - Bio-inspired fractal visualization using WebGL shaders
  - Cross-platform desktop app with Tauri architecture
  - Real-time audio-reactive visuals inspired by MilkDrop
  - Offline processing for privacy and performance
- Non-Goals:
  - Cloud-based processing or server dependencies
  - Simple waveform displays (focus on advanced ML-driven analysis)
  - Mobile/web versions (desktop-focused)
  - Live audio input processing (file-based analysis)

Assumptions and Risks
- Assumptions:
  - Tauri sidecar architecture can efficiently bridge Python ML backend with WebView frontend
  - Audio ML models can run locally with acceptable performance on modern desktop hardware
  - WebGL shaders can achieve real-time fractal visualization at 30+ FPS
  - PyInstaller can package Python dependencies into a standalone executable
- Risks:
  - Library conflicts between Python ML frameworks and Rust/Tauri integration
  - Performance bottlenecks in IPC communication between Python backend and frontend
  - Cross-platform packaging complexity with ML model dependencies
  - Real-time visualization lag due to computation or communication delays
  - Local desktop environment currently missing Node.js and Rust CLIs in PATH, blocking npm/cargo commands until resolved

Phase 0 Prompt Starters
```text
Begin Expertise Assessment (Level 1):
- Assess core programming language and editor familiarity.
- Identify basic technical gaps and learning preferences.
- Help articulate the main project idea in one sentence.
- Adapt assistance style based on identified gaps.
Outputs: Update PROFILE.yaml with expertise gaps and CONTEXT.md with main idea.

For deeper assessment, continue to Level 2:
- Identify specific technical challenges and AI tool experience.
- Establish collaboration preferences and learning priorities.
- Document detailed expertise gaps for targeted assistance.

For comprehensive projects, proceed to Level 3:
- Assess architecture knowledge and scalability considerations.
- Understand security requirements and integration patterns.
- Establish long-term learning objectives.
```

