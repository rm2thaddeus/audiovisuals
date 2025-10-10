<!-- f0611ed9-dacc-47fa-a2d8-3adac32de725 8b1df3fa-ea7e-4ae8-98ec-5f6b6e68c7ef -->
# CPPN Audio Visualizer POC Implementation Plan

## Objective

Create a working CLI that loads an audio track and generates a video with living, neural-generated visuals using CPPN (Compositional Pattern-Producing Networks) - the AI evolution beyond static MilkDrop presets.

## Implementation Strategy

### Phase 1: Environment Setup & Dependencies

- Install CUDA-enabled PyTorch (torch with CUDA 13.0 support)
- Install audio processing libraries: librosa, soundfile, numpy
- Install video encoding: opencv-python (cv2) for MP4 output
- Verify CUDA availability and RTX 5070 detection
- Set up CPU fallback detection logic

### Phase 2: Audio Analysis Pipeline

- Implement FFT-based feature extraction (bass, mid, treble bands)
- Extract temporal features: time progression, beat detection
- Add spectral features: spectral centroid, rolloff for richer CPPN inputs
- Create audio feature normalization for CPPN input range
- Output: Feature tensor per frame (60 FPS target)

### Phase 3: CPPN Implementation

- Design CPPN architecture with sine/cosine/gaussian activations (bio-inspired)
- Implement PyTorch CPPN with CUDA support:
  - Input: (x, y, time, bass, mid, treble, spectral_features)
  - Output: (R, G, B) per pixel
  - Network: 8-12 layers, ~500K parameters (balanced complexity)
- Initialize with Xavier/He weights for interesting starting patterns
- Create weight evolution strategy: subtle drift during playback for "living math"

### Phase 4: Neural Field Renderer

- Implement batched pixel coordinate generation (efficient GPU usage)
- CPPN forward pass on GPU with automatic CPU fallback
- Render 1920x1080 frames at 60 FPS (target)
- Implement frame caching for preview/re-rendering
- Add parallelization: process audio chunks concurrently where possible

### Phase 5: Video Generation Pipeline

- Frame-by-frame rendering loop synced to audio timeline
- MP4 video encoding with opencv (H.264 codec)
- Optional: Export individual frames as PNG for quality inspection
- Progress indicators and ETA calculation
- Memory management for long audio tracks

### Phase 6: CLI Interface

- Arguments: input audio path, output video path, resolution, FPS
- Optional tweaks: CPPN complexity, color schemes, evolution rate
- CUDA/CPU selection with auto-detection
- Verbose mode for debugging performance

## Technical Stack

- **Python 3.12** (current environment)
- **PyTorch with CUDA 13.0** (GPU acceleration on RTX 5070)
- **librosa** (audio analysis)
- **opencv-python** (video encoding)
- **numpy** (numerical operations)

## Key Files to Create

```
audiovisuals/
├── src/
│   ├── audio_analyzer.py      # FFT + feature extraction
│   ├── cppn.py                 # CPPN network architecture
│   ├── renderer.py             # Neural field rendering
│   ├── video_encoder.py        # MP4 generation
│   └── cli.py                  # Main CLI entry point
├── requirements.txt            # Dependencies
└── README.md                   # Usage instructions
```

## Success Criteria

- Load audio file and extract features successfully
- CPPN generates coherent, audio-reactive visuals
- Renders 60 FPS video on RTX 5070 (30 FPS acceptable on CPU)
- Output: MP4 video file with synchronized audio
- Processing time: <5min for 3min audio track on GPU

## Risks & Mitigations

- **CPPN too slow**: Start with lower resolution (720p), optimize batch size
- **Memory overflow**: Process in chunks, clear CUDA cache between frames
- **Incoherent visuals**: Tune audio feature normalization, adjust CPPN depth
- **Cross-platform issues**: Focus Windows-first, document GPU requirements

### To-dos

- [ ] Install PyTorch with CUDA 13.0 support and audio/video processing libraries
- [ ] Implement audio_analyzer.py with FFT and spectral feature extraction
- [ ] Create cppn.py with PyTorch neural network using sine/cosine activations
- [ ] Implement renderer.py with CUDA-accelerated neural field rendering and CPU fallback
- [ ] Create video_encoder.py for MP4 generation with opencv and frame export
- [ ] Build cli.py main entry point with argument parsing and progress tracking
- [ ] Test end-to-end pipeline: audio file to video output on RTX 5070