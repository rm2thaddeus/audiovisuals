# Backend Directory Organization

**Date:** 2025-10-11  
**Status:** ✅ Reorganized and Cleaned

---

## Summary of Changes

The backend directory has been reorganized for better maintainability and clarity. Files are now grouped by function, with clear separation between core pipeline, exploration tools, production solutions, and archived materials.

---

## Directory Structure

```
Code/backend/
├── Core Pipeline Files (CPPN-based)
│   ├── audio_analyzer.py      # FFT audio feature extraction
│   ├── cppn.py                # CPPN neural network (untrained)
│   ├── renderer.py            # GPU-accelerated frame rendering
│   ├── video_encoder.py       # MP4 video encoding with audio
│   └── cli.py                 # Command-line interface
│
├── tools/                     # Exploration & Testing Tools
│   ├── quick_explore.py       # Automated parameter exploration
│   ├── explore_parameters.py  # Batch parameter testing
│   ├── show_video_thumbnails.py  # HTML thumbnail generator
│   ├── regenerate_all_html.py    # HTML regeneration utility
│   ├── PARAMETER_EXPLORATION_GUIDE.md  # Complete exploration guide
│   ├── QUICK_TESTS.md               # Copy/paste test commands
│   └── EXPLORATION_SUMMARY.md       # Exploration results summary
│
├── trained_models/            # Production Approach ⭐
│   ├── trained_model_generator.py  # Beautiful pattern generation
│   ├── trained_TOOL - The Pot (Audio).mp4  # Example output
│   └── README.md              # Usage guide
│
├── archive/                   # Historical Artifacts
│   ├── diagnostics/           # CPPN optimization diagnostics
│   │   ├── diagnostic_*/      # Diagnostic run results
│   │   └── DIAGNOSTIC_REPORT.md  # Comprehensive diagnostic report
│   ├── test_outputs/          # Test video outputs
│   ├── test_scripts/          # Development/testing scripts
│   ├── audio_reactive_vqgan.py  # Early VQGAN experiment
│   └── test_video_embed.html    # HTML embedding test
│
├── explorations/              # Parameter Exploration Results
│   └── quick_TIMESTAMP/       # Individual exploration runs
│       ├── comparison.html    # Side-by-side video comparison
│       ├── thumbnails.html    # Video thumbnails
│       ├── README.md          # Exploration details
│       ├── segments/          # Audio segment clips
│       └── *.mp4              # Generated videos
│
├── models/                    # (Reserved for Phase B ML models)
├── docs/                      # (Reserved for audio samples)
│   └── Audio/
│       └── phase_a/
│
├── __pycache__/               # Python cache (gitignored)
│
├── AGENTS.md                  # Architecture & agent coordination
├── README.md                  # Main usage guide
└── requirements.txt           # Python dependencies
```

---

## What Was Moved

### Moved to `tools/`
Files related to parameter exploration and testing:
- `quick_explore.py` → `tools/quick_explore.py`
- `explore_parameters.py` → `tools/explore_parameters.py`
- `show_video_thumbnails.py` → `tools/show_video_thumbnails.py`
- `regenerate_all_html.py` → `tools/regenerate_all_html.py`
- `PARAMETER_EXPLORATION_GUIDE.md` → `tools/PARAMETER_EXPLORATION_GUIDE.md`
- `QUICK_TESTS.md` → `tools/QUICK_TESTS.md`
- `EXPLORATION_SUMMARY.md` → `tools/EXPLORATION_SUMMARY.md`

### Moved to `archive/`
Experimental and testing artifacts:
- `audio_reactive_vqgan.py` → `archive/audio_reactive_vqgan.py`
- `test_video_embed.html` → `archive/test_video_embed.html`

### Kept in Root
Core files and primary documentation:
- Core pipeline: `audio_analyzer.py`, `cppn.py`, `renderer.py`, `video_encoder.py`, `cli.py`
- Documentation: `README.md`, `AGENTS.md`
- Configuration: `requirements.txt`

---

## Quick Start Guide

### For Production Use (Recommended)
```bash
cd trained_models/
python trained_model_generator.py
# Places audio file in this directory first
# Output: trained_[filename].mp4 with beautiful patterns
```

### For Parameter Exploration (CPPN)
```bash
# Run automated exploration
cd tools/
python quick_explore.py
# Generates 12 variations in explorations/quick_TIMESTAMP/
# Open comparison.html to review results
```

### For Custom CPPN Generation
```bash
# From backend root
python cli.py input.mp3 output.mp4 --resolution 720p --fps 30
# See README.md for full options
```

---

## File Purposes

### Core Pipeline Files

**`audio_analyzer.py`**
- Extracts FFT features from audio (bass, mid, treble, spectral, temporal)
- Normalizes features to [-1, 1] range for CPPN input
- Supports configurable FPS for frame-level feature extraction

**`cppn.py`**
- CPPN neural network with mixed activations (sin, cos, gaussian, tanh)
- Xavier initialization with gain=5.0 (critical for signal preservation)
- GPU-accelerated with FP16 support (RTX 5070 optimized)
- Untrained (random weights) - generates mathematical patterns

**`renderer.py`**
- GPU-accelerated batch pixel processing
- Optimized for RTX 5070: 5M pixels/batch, FP16 precision
- Sequential frame rendering (parallel caused CUDA deadlocks)
- Memory-efficient streaming architecture

**`video_encoder.py`**
- MP4 encoding using OpenCV
- Audio muxing with ffmpeg
- Optional PNG frame export
- Streaming encoder for memory efficiency

**`cli.py`**
- Command-line interface coordinating all components
- Configurable resolution, FPS, CPPN layers, audio scaling
- Device selection (CUDA/CPU) with auto-detection
- Progress tracking and performance reporting

---

### Tools Directory

**`quick_explore.py`**
- Automated parameter exploration tool
- Cuts audio into 3 segments (start, quiet, intense)
- Generates 4 variations per segment (simple, reactive, complex, evolving)
- Creates HTML comparison page for easy review

**`explore_parameters.py`**
- Batch parameter testing with custom presets
- Tests 8 predefined configurations (organic, geometric, reactive, etc.)
- Generates exploration summary JSON

**`show_video_thumbnails.py`**
- Creates HTML pages with video thumbnails
- More reliable than embedded video players
- Click thumbnails to open in default player

**`regenerate_all_html.py`**
- Regenerates comparison HTML for all exploration runs
- Fixes video embedding issues
- Updates with current preset definitions

---

### Trained Models Directory

**`trained_model_generator.py`**
- ⭐ **Production-ready solution**
- Uses proven mathematical pattern generators (not random)
- Audio-reactive pattern selection based on energy/brightness
- 4 pattern types: Fractal, Organic, Flowing, Geometric
- Immediate beautiful results, no training required

---

### Archive Directory

Contains historical artifacts from development:
- **diagnostics/**: CPPN optimization history, performance testing
- **test_outputs/**: Test videos from development
- **test_scripts/**: Experimental diagnostic scripts
- **audio_reactive_vqgan.py**: Early VQGAN experiment (superseded by trained_model_generator.py)
- **test_video_embed.html**: HTML video embedding tests

---

## Documentation Files

**`README.md`**
- Main usage guide for the backend
- Installation instructions
- Command-line examples
- Performance benchmarks
- Troubleshooting

**`AGENTS.md`**
- Architecture overview (dual approaches)
- Sub-agent specifications (Audio Analyzer, CPPN, Renderer, Encoder)
- Implementation timeline and status
- Performance optimization details
- Usage recommendations

---

## Exploration Results

The `explorations/` directory contains parameter exploration runs. Each run generates:
- **comparison.html**: Side-by-side video comparison with embedded players
- **thumbnails.html**: Video thumbnails with download links
- **README.md**: Detailed exploration parameters and results
- **segments/**: Audio segment clips used for testing
- **\*.mp4**: Generated videos (12 per run: 3 segments × 4 variations)

To review an exploration:
1. Open `explorations/quick_TIMESTAMP/comparison.html` in a browser
2. Compare different parameter combinations
3. Note which configurations work well for different music types

---

## Development Workflow

### Adding New Features
1. Implement in appropriate core file (`audio_analyzer.py`, `cppn.py`, etc.)
2. Update CLI if new parameters needed
3. Test with `cli.py` using short audio clip
4. Document in `README.md` and `AGENTS.md`
5. Update `updated` field in YAML frontmatter

### Testing Parameter Changes
1. Use `tools/quick_explore.py` for automated testing
2. Or create custom presets in `tools/explore_parameters.py`
3. Review results in generated HTML files
4. Document findings in exploration README

### Debugging Issues
1. Check `archive/diagnostics/` for similar past issues
2. Use `archive/test_scripts/` for targeted testing
3. Add new diagnostic scripts to archive if needed

---

## Next Steps

### For Users
- **Production videos**: Use `trained_models/trained_model_generator.py`
- **Experimentation**: Use `tools/quick_explore.py` to find interesting CPPN parameters
- **Custom generation**: Use `cli.py` with your preferred parameters

### For Developers
- **Phase B**: Decide on ML integration approach (see `NEXT_STEPS.md`)
- **Enhancements**: Add color palette control, pattern interpolation, etc.
- **Training**: Train CPPN network for learned aesthetics (optional)

---

## Maintenance

### Keeping Organized
- New exploration tools → `tools/`
- New experimental files → `archive/`
- New production features → core files or `trained_models/`
- Documentation updates → project docs

### Cleaning Up
- Old exploration runs can be deleted from `explorations/` after review
- Keep latest 2-3 runs for reference
- Archive contains historical data (don't delete without review)

---

**Organized:** 2025-10-11  
**Structure:** Modular, maintainable, clearly separated by function  
**Status:** ✅ Ready for Phase B planning and future development


