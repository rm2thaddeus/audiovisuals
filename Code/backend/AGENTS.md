---
phase: 2
artifact: backend_agents
project: audio_feature_explorer
owner: Aitor Patiño Diaz
updated: 2025-10-15
status: Phase C Complete - 3L×4D Architecture Discovered
sources:
  - POC Plan: ../../docs/Phase2-POC/POC_PLAN.md
  - Current State: ../../docs/Phase2-POC/backend/CURRENT_STATE.md
  - Project Status: ./PROJECT_STATUS.md
links:
  profile: ../../docs/Phase0-Alignment/PROFILE.yaml
  context: ../../docs/Phase0-Alignment/CONTEXT.md
  poc_plan: ../../docs/Phase2-POC/POC_PLAN.md
  current_state: ../../docs/Phase2-POC/backend/CURRENT_STATE.md
---

# Backend Implementation Agents

## Status: ✅ Phase A Complete

**Two Approaches Available:**
1. **CPPN Pipeline** (Experimental) - Technical POC with untrained network
2. **Trained Model Generator** (Production) - Beautiful, structured patterns

See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for detailed comparison.

---

## Purpose
Define sub-agents and coordination for the Python CLI backend that generates audio-reactive visualizations using two distinct approaches.

## Backend Architecture Overview

### Approach 1: CPPN Pipeline (Experimental POC)

```
Audio File Input
  ↓
Audio Analyzer (FFT + ML Embeddings)
  ↓
CPPN Neural Field (PyTorch CUDA, Untrained)
  ↓
Renderer (Batch GPU Processing)
  ↓
Video Encoder (MP4 Output)
```

**Status:** ✅ Technical POC Complete  
**Limitation:** Random patterns (untrained network)  
**Use Case:** Parameter exploration, technical experimentation

### Approach 2: Trained Model Generator (Production)

```
Audio File Input
  ↓
Audio Feature Extraction (librosa)
  ↓
Pattern Type Selection (Audio-reactive)
  ↓
Trained Pattern Generators (Fractal/Organic/Flowing/Geometric)
  ↓
Video Encoder (MP4 Output)
```

**Status:** ✅ Production Ready  
**Advantage:** Beautiful, structured patterns  
**Use Case:** Production audio-reactive videos

See `trained_models/` directory for implementation.

---

## Project Structure

```
Code/backend/
├── Core Pipeline (CPPN-based)
│   ├── audio_analyzer.py      # FFT feature extraction
│   ├── cppn.py                # CPPN network (untrained)
│   ├── renderer.py            # GPU-accelerated rendering
│   ├── video_encoder.py       # MP4 encoding
│   └── cli.py                 # Command-line interface
│
├── tools/                     # Parameter Exploration Tools
│   ├── quick_explore.py       # Automated exploration
│   ├── explore_parameters.py  # Batch parameter testing
│   ├── show_video_thumbnails.py
│   ├── regenerate_all_html.py
│   ├── PARAMETER_EXPLORATION_GUIDE.md
│   ├── QUICK_TESTS.md
│   └── EXPLORATION_SUMMARY.md
│
├── trained_models/            # Production Approach ⭐
│   ├── trained_model_generator.py  # Beautiful patterns
│   └── README.md
│
├── archive/                   # Historical artifacts
│   ├── diagnostics/           # CPPN optimization history
│   ├── test_outputs/          # Test videos
│   ├── test_scripts/          # Development scripts
│   ├── audio_reactive_vqgan.py  # Early VQGAN experiment
│   └── test_video_embed.html  # Testing artifact
│
├── explorations/              # Parameter exploration results
│   └── quick_TIMESTAMP/       # Exploration runs
│
├── models/                    # (Reserved for Phase B)
├── docs/                      # (Reserved for audio samples)
│
├── AGENTS.md                  # This file (architecture)
├── README.md                  # Usage guide
├── PROJECT_STATUS.md          # Comprehensive status
└── requirements.txt           # Python dependencies
```

---

## Sub-Agents (CPPN Pipeline)

### Audio Analyzer Agent
**Purpose**: Extract rich audio features for CPPN inputs

**Triggers**: CLI invocation with audio file path

**Inputs**: 
- Audio file (MP3, WAV, etc.)
- Configuration: FFT bands, ML models to use (OpenL3/YAMNet/VGGish)

**Outputs**:
- Feature tensor per frame (60 Hz)
- Shape: `(num_frames, feature_dim)` where feature_dim varies by config
  - FFT-only: ~10-20 features (bass, mid, treble, spectral)
  - + OpenL3: +128 or +512 dimensions
  - + YAMNet: +521 dimensions
  - + VGGish: +128 dimensions

**Implementation**: `audio_analyzer.py`

**Protocol**:
- Load audio with librosa
- Extract FFT features (bass/mid/treble bands, spectral centroid, rolloff, flux)
- Conditionally load ML models based on CLI flags
- Normalize features to CPPN input range [-1, 1]
- Cache features for re-rendering

**Subroles**:
- FFT Extractor: Compute frequency domain features
- ML Embedder: Run OpenL3/YAMNet/VGGish if enabled
- Normalizer: Scale features to neural network range

---

### CPPN Network Agent
**Purpose**: Neural field that maps (x, y, audio_features) → (R, G, B)

**Triggers**: Frame rendering request

**Inputs**:
- Pixel coordinates: (x, y) normalized to [-1, 1]
- Time: current frame timestamp
- Audio features: from Audio Analyzer

**Outputs**:
- RGB values per pixel, shape: `(height, width, 3)`

**Implementation**: `cppn.py`

**Protocol**:
- PyTorch neural network with 8-12 layers
- Activations: sine, cosine, gaussian, tanh (bio-inspired)
- Initialize with Xavier/He weights for interesting patterns
- CUDA execution on RTX 5070, CPU fallback if unavailable
- Optional weight evolution: subtle drift for "living math" effect

**Architecture**:
```python
class CPPN(nn.Module):
    Input: [batch, input_dim]  # input_dim = 3 (x,y,t) + audio_features
    Hidden: [batch, 256] × 8 layers with mixed activations  # OPTIMIZED for RTX 5070
    Output: [batch, 3]  # RGB
```

**Performance Optimization (RTX 5070)**:
- **Optimal Configuration**: 256 hidden dim × 8 layers (464K parameters)
- **Batch Size**: 10M pixels per batch (maximum GPU utilization)
- **Workers**: 12 parallel workers for frame processing
- **Precision**: FP16 for 2x speed improvement
- **Performance**: 249M pixels/sec, 52+ FPS @ 720p

**Subroles**:
- Pattern Generator: Forward pass through network
- Weight Evolver: Optionally mutate weights over time
- Batch Processor: Efficient GPU utilization

---

### Renderer Agent
**Purpose**: Generate frames by evaluating CPPN across all pixels

**Triggers**: Video generation request

**Inputs**:
- CPPN network
- Audio features timeline
- Resolution (720p, 1080p)
- FPS (30, 60)

**Outputs**:
- Frame sequence: list of numpy arrays `(height, width, 3)`
- Performance metrics: FPS, GPU utilization

**Implementation**: `renderer.py`

**Protocol**:
- Generate pixel coordinate grid for target resolution
- For each frame timestamp:
  - Get audio features at that time
  - Batch process all pixels through CPPN (GPU)
  - Convert to RGB uint8 frame
- Optional: Parallelize chunks for long videos
- Clear CUDA cache between frames if memory constrained

**Optimization**:
- Batch size tuning for RTX 5070 (8GB VRAM) - **OPTIMIZED: 10M pixels/batch**
- Half-precision (FP16) for 2x speed improvement
- Frame caching for preview/re-renders
- **Parallel processing: 12 workers** (optimal for RTX 5070)
- **Performance: 52+ FPS @ 720p, 249M pixels/sec**

**Subroles**:
- Coordinate Generator: Create pixel grid
- Batch Processor: GPU-accelerated CPPN evaluation
- Frame Manager: Cache and memory management

---

### Video Encoder Agent
**Purpose**: Encode frame sequence to MP4 with audio

**Triggers**: Rendering complete

**Inputs**:
- Frame sequence from Renderer
- Original audio file
- Output path, codec settings

**Outputs**:
- MP4 video file (H.264)
- Optional: PNG frame exports

**Implementation**: `video_encoder.py`

**Protocol**:
- Use opencv VideoWriter for MP4 encoding
- Mux original audio track into video
- Optional: Export frames as PNG for quality inspection
- Progress bar with ETA

**Subroles**:
- Frame Writer: opencv video encoding
- Audio Muxer: Sync audio with video
- Export Manager: Optional PNG frame export

---

### CLI Coordinator Agent
**Purpose**: Orchestrate the full pipeline

**Triggers**: User CLI invocation

**Inputs**:
- Command line arguments:
  ```
  python cli.py input.mp3 output.mp4 \
    --resolution 1080p \
    --fps 60 \
    --models openl3,yamnet \
    --cppn-layers 10 \
    --device cuda
  ```

**Outputs**:
- Generated video file
- Performance report
- Optional: Feature cache, debug visualizations

**Implementation**: `cli.py`

**Protocol**:
1. Parse arguments and validate inputs
2. Detect CUDA availability, set device
3. Call Audio Analyzer → get feature timeline
4. Initialize CPPN with config
5. Call Renderer → get frame sequence
6. Call Video Encoder → write MP4
7. Report performance metrics

**Error Handling**:
- Graceful fallback to CPU if CUDA unavailable
- Memory overflow: reduce batch size or resolution
- Invalid audio: informative error messages

**Subroles**:
- Argument Parser: CLI interface
- Pipeline Orchestrator: Coordinate sub-agents
- Progress Reporter: User feedback

---

## Handoff Protocol

### Audio Analyzer → CPPN
- **Data**: Feature tensor `(num_frames, feature_dim)`
- **Format**: Normalized to [-1, 1] range
- **Trigger**: Feature extraction complete

### CPPN → Renderer
- **Data**: Initialized network ready for inference
- **Contract**: Network accepts `(x, y, time, features...)`
- **Trigger**: CPPN loaded and validated

### Renderer → Video Encoder
- **Data**: Frame sequence list
- **Format**: numpy uint8 arrays `(H, W, 3)`
- **Trigger**: All frames rendered

---

## Success Criteria (Phase A: Baseline) ✅ COMPLETE

- [x] Audio Analyzer extracts FFT features @ 60 Hz
- [x] CPPN network initializes on CUDA (RTX 5070)
- [x] Renderer generates 720p frames without errors
- [x] Video Encoder produces synced MP4 output
- [x] CLI runs end-to-end: audio file → video file
- [x] Performance: <5min for 3min audio track (**ACHIEVED: ~1min for 3min audio**)

## GPU Optimization Results (RTX 5070)

**Profiling Methodology**:
- Tested batch sizes: 100K to 10M pixels
- Tested worker counts: 1 to 24 workers
- Tested CPPN architectures: 64x4 to 512x10
- Measured pixels/sec, FPS, and memory usage

**Optimal Configuration** (Updated 2025-10-11):
- **CPPN**: 256 hidden dim × 4 layers (201K parameters) - reduced from 8 to preserve signals
- **Weight Init**: Xavier uniform with gain=5.0 (critical for temporal variation)
- **Batch Size**: 5M pixels per batch (auto-optimized per GPU)
- **Workers**: 1 (sequential - parallel causes CUDA deadlocks)
- **Precision**: FP16 throughout pipeline
- **Memory Usage**: Streaming architecture (constant memory)

**Performance Results**:
- **720p @ 30 FPS**: 52+ FPS (0.64x realtime)
- **1080p @ 60 FPS**: 30+ FPS (0.22x realtime)
- **Pixels/sec**: 249M pixels/sec
- **3-minute track**: ~1 minute processing time

## Critical Fix: Xavier Gain=5.0 (2025-10-11)

**Problem**: CPPN was generating completely static videos - all frames pixel-perfect identical (variance=0.00) regardless of time or audio changes.

**Root Cause**: Xavier initialization with gain=1.0 caused signal vanishing through alternating sin/cos/gaussian/tanh activations:
- Layer 0 (sin): Small inputs → small outputs (±0.075)
- Layer 1 (cos): cos(±0.075) ≈ 0.997 ≈ 1.0 → **SATURATION**
- Subsequent layers processed nearly-constant inputs
- Final output collapsed to constant RGB≈(0.5, 0.5, 0.5)

**Solution**: Changed Xavier gain from 1.0 to 5.0 in `cppn.py::_initialize_weights()`

**Results After Fix**:
- Time variance: 0.098 (was 0.000)
- Audio variance: 0.003 (was 0.000)
- Space variance: 0.058 (was 0.000)
- Frame-to-frame RGB variance: 244.54 (was 0.00)
- Visual output: Dynamic, varying colors throughout video

**Diagnostic Tools Created**:
- `test_cppn_directly.py`: Unit test for CPPN responsiveness
- `analyze_video_frames.py`: Video frame variance analysis
- `diagnose_cppn.py`: Comprehensive CPPN diagnostic

**Architecture Notes**:
- Larger weights (gain=5.0) maintain signal through periodic activations
- Coordinate scaling: ±0.5 (was ±1.0) for input balance
- Time mapping: [0,1] → [-1,1] for consistent range
- Audio amplification: 3x in renderer (on top of 0.05 CLI scale)

---

## Trained Model Generator Agent (Production Approach)

**Purpose**: Generate beautiful, structured patterns using proven mathematical generators

**Triggers**: User runs `trained_model_generator.py`

**Inputs**:
- Audio file (MP3, WAV, etc.)
- Target resolution (default: 512x512)
- FPS (default: 30)

**Outputs**:
- Professional-quality MP4 with audio-reactive pattern selection
- Beautiful structured patterns (fractal, organic, flowing, geometric)

**Implementation**: `trained_models/trained_model_generator.py`

**Protocol**:
- Extract audio features (energy, brightness, roughness)
- Select pattern type based on audio characteristics:
  - High energy → Geometric patterns
  - High brightness → Fractal patterns
  - Medium energy → Flowing patterns
  - Low energy → Organic patterns
- Generate frame using selected pattern generator
- Encode to MP4 with original audio

**Pattern Generators**:
- **Fractal**: Recursive branching structures
- **Organic**: Nature-like blob formations
- **Flowing**: Wave-like curve patterns
- **Geometric**: Angular polygon designs

**Advantages**:
- ✅ Beautiful, structured output (vs random noise)
- ✅ Immediate results (no training required)
- ✅ Production-ready quality
- ✅ Intelligent audio reactivity

**Status**: ✅ **PRODUCTION READY**

See `trained_models/README.md` for detailed usage.

---

## Implementation Timeline

### ✅ Phase A: Baseline (Complete)
- [x] Audio Analyzer (FFT-only)
- [x] CPPN + Renderer
- [x] Video Encoder + CLI
- [x] Integration testing
- [x] GPU optimization (RTX 5070)
- [x] Parameter exploration tools
- [x] Documentation

**Result**: Technical POC complete, pipeline functional

### ⏸️ Phase B: ML Integration (On Hold)
**Blocker**: Untrained CPPN won't benefit from richer audio features

**Alternative**: Trained Model Generator implemented as production solution

### 🎯 Phase C: Future Enhancements (Optional)
Potential directions:
1. Train CPPN network for aesthetic patterns
2. Integrate pre-trained generative models (StyleGAN, Diffusion)
3. Enhance trained pattern generators
4. Add color palette control
5. Implement pattern interpolation

See `../../docs/Phase2-POC/backend/NEXT_STEPS.md` for detailed options.

---

## Notes

### Development Guidelines
- Follow Phase 2 conventions: small edits, update `updated` fields
- Document performance metrics for each spike
- Keep GPU/CPU paths clearly separated for maintainability
- Profile bottlenecks before optimizing
- **CRITICAL:** NEVER use emojis in Python scripts that output to console - Windows cmd/PowerShell fail with UnicodeEncodeError on cp1252 encoding

### Usage Recommendations

**For Production Use:**
- Use `trained_model_generator.py` in `trained_models/` directory
- Provides beautiful, structured patterns immediately
- No parameter tuning required

**For Technical Exploration:**
- Use CPPN pipeline (core files + `cli.py`)
- Explore parameter space with `tools/quick_explore.py`
- Useful for understanding neural field generation
- See `tools/PARAMETER_EXPLORATION_GUIDE.md`

**For Development:**
- Archive contains historical diagnostics and test scripts
- See `archive/diagnostics/DIAGNOSTIC_REPORT.md` for optimization history
- Test scripts available in `archive/test_scripts/`

### Key Learnings

1. **Xavier Gain Critical**: gain=5.0 required to prevent signal vanishing through periodic activations
2. **Coordinate Scaling**: ±0.5 (not ±1.0) balances spatial vs temporal/audio features
3. **Audio Amplification**: 3x amplification in renderer for proper feature influence
4. **Untrained Network Limitation**: Random weights → random patterns, not aesthetics
5. **Production Solution**: Trained pattern generators provide immediate beautiful results

