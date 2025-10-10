---
phase: 2
artifact: poc_plan
project: audio_feature_explorer
owner: Aitor Patiño Diaz
updated: 2025-01-27
sources:
  - Research: CPPN real-time rendering feasibility
  - Environment: Windows 11, 15.8GB RAM, Python 3.12.0
  - References: NeuroMV project, ProjectM MilkDrop, WebGL neural inference
links:
  profile: ./docs/Phase0-Alignment/PROFILE.yaml
  context: ./docs/Phase0-Alignment/CONTEXT.md
  idea: ./docs/Phase1-Ideation/IDEA_NOTE.md
---

Feasibility Questions
- Can we achieve real-time CPPN rendering at 60 FPS? YES - WebGL shaders can run neural networks in real-time on modern GPUs
- What are the core dependencies? WebGL/GLSL, FFT libraries (FFTW/KISS FFT), Python ML stack (PyTorch/TensorFlow), Tauri framework
- What is the smallest end-to-end slice? Audio file → FFT analysis → CPPN inputs → WebGL neural field renderer → visual output

Candidate Stack
- Frontend: Tauri (Rust) + WebGL/GLSL shaders + Svelte/React UI
- Backend: Python sidecar (PyTorch/TensorFlow) + FFT libraries (FFTW/KISS FFT)
- Data: Local audio files, pre-trained CPPN weights, cached analysis results
- Infra: Cross-platform desktop app (Windows/macOS/Linux), local-first processing
- MCP: GitHub (version control), Browser Tools (WebGL testing), Context7 (research)

Architecture Sketch
- Context diagram: Audio File → Python Backend (FFT + ML) → Tauri IPC → WebGL Frontend (CPPN Renderer) → Visual Output
- Sequence diagram (MVP slice): 
  1. Load audio file → 2. Extract FFT features → 3. Map to CPPN inputs → 4. Render neural field → 5. Display real-time visuals

Spikes and Experiments
- Spike 1: CPPN WebGL Shader Performance — Implement basic CPPN in GLSL, measure FPS on target hardware, validate 60 FPS feasibility
- Spike 2: Audio-CPPN Integration — Create FFT → neural input mapping, test with sample audio, validate real-time responsiveness

UX/UI Notes
- Personas: Audio enthusiasts seeking next-gen visualization, developers exploring neural art, artists creating AI-driven visuals
- User journey: Drag audio file → See living neural patterns emerge → Adjust parameters → Export/share visuals
- Wireframe notes: Minimal UI with large visualization canvas, audio controls overlay, parameter adjustment panel

Risks and Mitigations
- Risk: CPPN rendering too slow for real-time — Mitigation: Optimize shader complexity, use lower resolution, implement quality settings
- Risk: Audio-CPPN mapping produces incoherent visuals — Mitigation: Research optimal feature mapping, test with diverse audio samples
- Risk: Cross-platform packaging complexity — Mitigation: Start with Windows-only, use PyInstaller + Tauri sidecar approach

Checklists
- Research Checklist:
  - [ ] Identify 3–5 comparable projects
  - [ ] Validate licensing and constraints
  - [ ] Prototype smallest E2E slice

Phase 2 Prompt Starters
```text
Plan the POC:
- Research dependencies and comparable solutions.
- Sketch architecture and define smallest end-to-end slice.
- Propose 1–2 spikes with success criteria.
Output: Populate this plan with references and decisions.
```


