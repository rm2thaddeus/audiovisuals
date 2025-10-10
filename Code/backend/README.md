# Audio Feature Explorer - Backend

CPPN-based audio-reactive visualization CLI tool.

## Overview

This backend generates videos with AI-generated visuals (CPPNs) that respond to audio features, representing the neural evolution beyond static MilkDrop presets.

## Architecture

```
Audio File → Audio Analyzer → CPPN (CUDA) → Renderer → Video Encoder → MP4
```

## Project Structure

```
backend/
├── audio_analyzer.py      # FFT + ML embeddings extraction
├── cppn.py                # CPPN neural network architecture
├── renderer.py            # GPU-accelerated frame rendering
├── video_encoder.py       # MP4 generation
├── cli.py                 # Main CLI entry point
├── models/                # ML model wrappers
│   ├── openl3_wrapper.py
│   ├── yamnet_wrapper.py
│   └── vggish_wrapper.py
├── requirements.txt       # Python dependencies
└── AGENTS.md              # Implementation guide

```

## Development Phases

### Phase A: Baseline (Week 1)
- FFT-only audio analysis
- Simple CPPN with sine/cosine activations
- CUDA acceleration on RTX 5070
- Output: 720p @ 30 FPS

### Phase B: ML Integration (Week 2)
- Benchmark OpenL3/YAMNet/VGGish
- Integrate best-performing models
- Expand CPPN inputs with embeddings

### Phase C: Optimization (Week 3)
- Multi-resolution support (720p/1080p)
- Parallelized frame processing
- CLI polish and frame export

## Hardware Requirements

- **GPU**: NVIDIA RTX 5070 (8GB VRAM) with CUDA 13.0
- **RAM**: 16GB+ recommended
- **OS**: Windows 11 (primary), cross-platform future

## Installation

```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip install -r requirements.txt
```

## Usage (Coming Soon)

```bash
# Basic usage
python cli.py input.mp3 output.mp4

# With ML embeddings
python cli.py input.mp3 output.mp4 --models openl3,yamnet --resolution 1080p --fps 60

# CPU fallback
python cli.py input.mp3 output.mp4 --device cpu
```

## Development Status

- [x] Folder structure created
- [x] AGENTS.md documented
- [ ] Phase A: Baseline implementation
- [ ] Phase B: ML model integration
- [ ] Phase C: Optimization

## See Also

- [POC Plan](../../docs/Phase2-POC/POC_PLAN.md)
- [Implementation Plan](../../.cursor/plans/cppn-audio-visualizer-poc-f0611ed9.plan.md)
- [Backend Agents](./AGENTS.md)

