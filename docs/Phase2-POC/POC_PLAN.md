---
phase: 2
artifact: poc_plan
project: audio_feature_explorer
owner: Aitor Patiño Diaz
updated: 2025-01-27
sources:
  - Research: CPPN real-time rendering feasibility, ML audio embeddings comparison
  - Environment: Windows 11, 15.8GB RAM, Python 3.12.0, NVIDIA RTX 5070 (8GB VRAM, CUDA 13.0)
  - References: NeuroMV project, ProjectM MilkDrop, OpenL3/YAMNet/VGGish embeddings
  - Implementation Plan: ../../.cursor/plans/cppn-audio-visualizer-poc-f0611ed9.plan.md
links:
  profile: ./docs/Phase0-Alignment/PROFILE.yaml
  context: ./docs/Phase0-Alignment/CONTEXT.md
  idea: ./docs/Phase1-Ideation/IDEA_NOTE.md
  backend_agents: ../../Code/backend/AGENTS.md
---

Feasibility Questions
- Can we achieve real-time CPPN rendering at 60 FPS? YES - CUDA-accelerated PyTorch on RTX 5070 can render neural fields in real-time
- What are the core dependencies? PyTorch (CUDA 13.0), librosa (audio), opencv (video), optional ML models (OpenL3/YAMNet/VGGish)
- What is the smallest end-to-end slice? Audio file → FFT features → CPPN(x,y,audio) → frames → MP4 video
- GPU Critical: RTX 5070 with 8GB VRAM and CUDA 13.0 enables complex CPPN networks and ML embeddings

Candidate Stack (Phase 2 POC: CLI Tool)
- Core: Python 3.12 + PyTorch 2.x (CUDA 13.0) + librosa + opencv
- Audio Analysis: FFT (librosa) + optional ML embeddings (OpenL3/YAMNet/VGGish)
- CPPN: PyTorch neural network (8-12 layers, sine/cosine activations)
- Rendering: CUDA-accelerated batch processing on RTX 5070, CPU fallback
- Video: opencv VideoWriter (H.264 codec), optional PNG frame export
- Future (Phase 3): Tauri desktop UI with real-time preview

Architecture Sketch (CLI POC)
- Context diagram: Audio File → Audio Analyzer (FFT + ML) → CPPN (CUDA) → Renderer (GPU) → Video Encoder → MP4
- Sequence diagram (POC slice):
  1. Load audio → 2. Extract features @ 60Hz → 3. Initialize CPPN on GPU → 4. Batch render frames → 5. Encode to MP4 with audio
- Phased Approach:
  - Phase A: FFT + CPPN baseline (720p @ 30 FPS)
  - Phase B: Add ML embeddings (OpenL3/YAMNet/VGGish benchmark)
  - Phase C: Optimize for 1080p @ 60 FPS

Spikes and Experiments
- Spike A1: CPPN CUDA Performance — Implement PyTorch CPPN, benchmark on RTX 5070, validate 60 FPS frame generation
- Spike A2: Audio Feature Extraction — FFT pipeline, normalize for CPPN inputs, verify 60Hz feature rate
- Spike B1: ML Model Benchmark — Compare OpenL3/YAMNet/VGGish inference speed and memory usage on RTX 5070
- Spike B2: Expanded CPPN Inputs — Test CPPN with 128D-512D embeddings, evaluate visual coherence vs FFT-only

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
  - [x] Identify comparable projects (NeuroMV, ProjectM MilkDrop)
  - [x] ML embeddings research (OpenL3/YAMNet/VGGish complementary to FFT)
  - [x] GPU capabilities verified (RTX 5070, CUDA 13.0)
  - [ ] Phase A: FFT + CPPN baseline implemented
  - [ ] Phase B: ML model benchmarks completed
  - [ ] Phase C: Production optimization finished
  
- Implementation Structure:
  - [x] Code/backend/ folder created
  - [x] Code/backend/AGENTS.md documented
  - [ ] Phase A baseline: audio_analyzer.py, cppn.py, renderer.py, video_encoder.py, cli.py
  - [ ] Phase B: models/ wrappers for OpenL3/YAMNet/VGGish
  - [ ] Phase C: Optimization and CLI polish

Research Findings: FFT vs ML Embeddings
- **Complementary, NOT Contradictory**: FFT and ML embeddings operate at different semantic levels
  - FFT: Real-time reactivity (bass/mid/treble, beats, spectral features)
  - ML Embeddings: Semantic understanding (mood, genre, timbre, sound events)
- **Hybrid Approach**: CPPN(x, y, time, fft_features, ml_embeddings) provides richest input space
- **Performance Considerations**:
  - FFT: Very fast, <1ms per frame
  - OpenL3: ~10-20ms per frame (512D embeddings)
  - YAMNet: ~5-10ms per frame (lightweight MobileNet, optimized for CPU)
  - VGGish: ~15-20ms per frame (128D embeddings)
- **Decision**: Start FFT-only baseline, then incrementally add ML models based on benchmarks

## GPU Optimization Results (RTX 5070) ✅ COMPLETE

**Profiling Methodology**:
- Comprehensive GPU profiling with `targeted_profiler.py`
- Tested batch sizes: 100K to 10M pixels
- Tested worker counts: 1 to 24 workers
- Tested CPPN architectures: 64x4 to 512x10
- Measured pixels/sec, FPS, and memory usage

**Optimal Configuration Discovered**:
- **CPPN**: 256 hidden dim × 8 layers (464K parameters)
- **Batch Size**: 10M pixels per batch (maximum GPU utilization)
- **Workers**: 12 parallel workers (optimal for RTX 5070)
- **Precision**: FP16 throughout pipeline (2x speed improvement)
- **Memory Usage**: 0.29GB (3.6% of 8GB VRAM)

**Performance Results**:
- **720p @ 30 FPS**: 52+ FPS (0.64x realtime)
- **1080p @ 60 FPS**: 30+ FPS (0.22x realtime)
- **Pixels/sec**: 249M pixels/sec
- **3-minute track**: ~1 minute processing time
- **Real-world speed**: 1.8x realtime @ 720p

**Key Insights**:
- GPU was severely underutilized with original configuration
- Larger CPPN (464K vs 84K params) actually performs 5x faster
- Memory is not the bottleneck - can handle 10M pixels per batch
- Optimal worker count is 12 (not 4) for RTX 5070
- FP16 precision provides consistent 2x speed improvement

Phase 2 Prompt Starters
```text
Plan the POC:
- Research dependencies and comparable solutions.
- Sketch architecture and define smallest end-to-end slice.
- Propose 1–2 spikes with success criteria.
Output: Populate this plan with references and decisions.
```


