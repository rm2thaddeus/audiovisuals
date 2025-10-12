# Audio Feature Explorer - Backend

**Status:** ✅ Phase A Complete - POC Working  
**Organization:** ✅ Reorganized 2025-10-11 (see [ORGANIZATION.md](./ORGANIZATION.md))  
**Note:** ⚠️ CPPN network is **untrained** (see [CURRENT_STATE.md](../../docs/Phase2-POC/backend/CURRENT_STATE.md))

**Two Approaches Available:**
1. **CPPN Pipeline** - Experimental POC for parameter exploration
2. **Trained Model Generator** ⭐ - Production-ready beautiful patterns (see `trained_models/`)

---

## Quick Start

```bash
# Basic usage (720p @ 30 FPS)
python cli.py input.mp3 output.mp4

# High quality (1080p @ 60 FPS)
python cli.py input.mp3 output.mp4 --resolution 1080p --fps 60

# With evolution effect
python cli.py input.mp3 output.mp4 --evolve 0.005 --audio-scale 0.1
```

See **Usage Examples** below for more options.

---

## What This Does

Generates audio-reactive videos using a CPPN (Compositional Pattern Producing Network) that creates visual patterns responding to music.

**Pipeline:**
```
Audio File → FFT Analysis → CPPN Generation → GPU Rendering → MP4 Video
```

**Important:** The CPPN is **randomly initialized** (not trained), so visuals are mathematical artifacts that happen to look interesting. See [CURRENT_STATE.md](../../docs/Phase2-POC/backend/CURRENT_STATE.md) for details and limitations.

---

## Installation

### Requirements
- Python 3.10+
- NVIDIA GPU with CUDA support (tested on RTX 5070)
- ffmpeg (for audio muxing)

### Setup

```bash
# 1. Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify ffmpeg is installed
ffmpeg -version
```

---

## Usage Examples

### Basic Generation
```bash
# 720p @ 30 FPS (default)
python cli.py "path/to/audio.mp3" output.mp4
```

### High Quality
```bash
# 1080p @ 60 FPS
python cli.py audio.mp3 output_hq.mp4 --resolution 1080p --fps 60
```

### Parameter Tuning
```bash
# More CPPN layers (more complex patterns)
python cli.py audio.mp3 output.mp4 --layers 6 --hidden-dim 512

# Stronger audio influence
python cli.py audio.mp3 output.mp4 --audio-scale 0.1

# "Living math" evolution effect
python cli.py audio.mp3 output.mp4 --evolve 0.005
```

### Export Options
```bash
# Export individual PNG frames
python cli.py audio.mp3 output.mp4 --export-frames --frames-dir frames/

# Silent video (no audio track)
python cli.py audio.mp3 output.mp4 --no-audio
```

### CPU Fallback
```bash
# Force CPU (no GPU required, much slower)
python cli.py audio.mp3 output.mp4 --device cpu
```

---

## Command-Line Options

```
python cli.py INPUT OUTPUT [OPTIONS]

Required:
  INPUT                    Audio file (MP3, WAV, etc.)
  OUTPUT                   Output video file (MP4)

Video Settings:
  --resolution, -r         360p, 480p, 720p, 1080p, 1440p, 4k (default: 720p)
  --fps, -f                24, 30, 60 (default: 30)

CPPN Settings:
  --layers, -l             Number of layers (default: 4)
  --hidden-dim, -d         Hidden units per layer (default: 256)
  --evolve, -e             Weight evolution rate 0.0-0.01 (default: 0.0)
  --audio-scale, -a        Audio feature scaling 0.01-0.3 (default: 0.05)

Processing:
  --device                 auto, cuda, cpu (default: auto)
  --batch-size, -b         Pixels per batch (default: auto-optimized)

Export:
  --export-frames          Save individual PNG frames
  --frames-dir             Directory for frames (default: auto)
  --no-audio               Generate video without audio track

Other:
  --verbose, -v            Detailed output
```

---

## Performance

**Tested on RTX 5070 Laptop GPU:**

| Resolution | FPS | Speed | Time (3min audio) |
|------------|-----|-------|-------------------|
| 720p       | 30  | 0.61x realtime | ~4.9 minutes |
| 1080p      | 60  | 0.22x realtime | ~13.6 minutes |

*Speed may vary based on GPU, CPPN complexity, and audio length.*

---

## Project Structure

```
backend/
├── Core Pipeline (CPPN-based)
│   ├── cli.py                 # Main entry point
│   ├── audio_analyzer.py      # FFT feature extraction
│   ├── cppn.py                # CPPN network (untrained)
│   ├── renderer.py            # GPU-accelerated rendering
│   └── video_encoder.py       # MP4 generation with ffmpeg
│
├── tools/                     # Exploration & Testing
│   ├── quick_explore.py       # Automated parameter exploration
│   ├── explore_parameters.py  # Batch parameter testing
│   ├── show_video_thumbnails.py
│   ├── regenerate_all_html.py
│   ├── PARAMETER_EXPLORATION_GUIDE.md
│   ├── QUICK_TESTS.md
│   └── README.md              # Tools documentation
│
├── trained_models/            # Production Approach ⭐
│   ├── trained_model_generator.py  # Beautiful patterns
│   └── README.md
│
├── archive/                   # Historical artifacts
│   ├── diagnostics/           # CPPN optimization history
│   ├── test_outputs/          # Test videos
│   └── test_scripts/          # Experimental scripts
│
├── explorations/              # Parameter exploration results
├── models/                    # (Reserved for Phase B)
├── docs/                      # (Reserved for audio samples)
│
├── AGENTS.md                  # Architecture documentation
├── README.md                  # This file (usage guide)
└── requirements.txt           # Python dependencies
```

**Documentation:**

Local (Code/backend/):
- **README.md** - This file (usage guide)
- **AGENTS.md** - Architecture and agent coordination
- **tools/README.md** - Exploration tools guide

Project Status (docs/Phase2-POC/):
- **POC_PLAN.md** - Phase 2 POC plan and status tracking ⭐
- **backend/CURRENT_STATE.md** - Limitations and context
- **backend/NEXT_STEPS.md** - Future ML exploration paths (5 options)
- **backend/PROJECT_STATUS.md** - Comprehensive project status
- **backend/ORGANIZATION.md** - Directory structure guide
- **backend/PHASE_A_COMPLETE.md** - Phase A completion report
- **backend/REORGANIZATION_SUMMARY.md** - Documentation consolidation

```

---

## Phase Status

### ✅ Phase A: Baseline (Complete)
- [x] FFT audio analysis @ 30/60 FPS
- [x] CPPN network with mixed activations
- [x] GPU-accelerated rendering (RTX 5070)
- [x] MP4 encoding with audio muxing
- [x] Full CLI interface
- [x] Performance optimization

### ⏸️ Phase B: Enhancement (Blocked - See Documentation)
Original plan was ML model integration (OpenL3/YAMNet), but:
- **Problem:** Untrained network won't benefit from richer features
- **Decision needed:** Train network? Use pre-trained models? Different approach?
- See [NEXT_STEPS.md](../../docs/Phase2-POC/backend/NEXT_STEPS.md) for detailed options

---

## Documentation

**Local (Code/backend/):**
- **`README.md`** (this file) - Usage and quick start
- **`AGENTS.md`** - System architecture and agent specifications
- **`tools/README.md`** - Parameter exploration tools guide

**Project Status (docs/Phase2-POC/):**
- **`POC_PLAN.md`** - Phase 2 POC plan with comprehensive status tracking
- **`backend/CURRENT_STATE.md`** - Critical limitations and technical context
- **`backend/NEXT_STEPS.md`** - Future ML exploration paths (5 detailed options)
- **`backend/PROJECT_STATUS.md`** - Comprehensive project status and comparison
- **`backend/ORGANIZATION.md`** - Backend directory structure guide
- **`backend/PHASE_A_COMPLETE.md`** - Phase A implementation details
- **`backend/REORGANIZATION_SUMMARY.md`** - Documentation consolidation summary

---

## Known Issues

1. **Untrained Network:** CPPN generates random patterns (not learned aesthetics)
2. **Limited Control:** Visuals are determined by random weight initialization
3. **No Semantic Mapping:** Audio features modulate random patterns (crude reactivity)

See [CURRENT_STATE.md](../../docs/Phase2-POC/backend/CURRENT_STATE.md) for full details.

---

## Troubleshooting

### CUDA Out of Memory
```bash
# Reduce batch size
python cli.py audio.mp3 output.mp4 --batch-size 1000000

# Or use lower resolution
python cli.py audio.mp3 output.mp4 --resolution 480p
```

### Slow Performance
- Ensure CUDA is available: `python -c "import torch; print(torch.cuda.is_available())"`
- Use lower resolution or fewer layers
- Check GPU isn't being used by other processes

### ffmpeg Not Found
- Install ffmpeg: https://ffmpeg.org/download.html
- Add to PATH
- Verify: `ffmpeg -version`

---

## Examples

Generated videos are saved to the specified output path.

**Sample command:**
```bash
python cli.py "../../docs/Audio/TOOL - The Pot (Audio).mp3" tool_visualization.mp4 --resolution 1080p --fps 60 --evolve 0.003
```

**Output:** `tool_visualization.mp4` (386 MB, 6.4 minutes, audio-reactive visuals)

---

## Music Analysis Tools (Phase B) 🎵

**NEW**: Independent CLI tools for extracting semantic music features!

Located in `music_analysis/` directory with full documentation in [music_analysis/README.md](./music_analysis/README.md).

### Available Analyzers

**Tempo & Beat Tracking:**
```bash
python -m music_analysis.cli.analyze_tempo audio.mp3
```
Extracts BPM, beat positions, and time signature.

**Key Detection:**
```bash
python -m music_analysis.cli.analyze_key audio.mp3
```
Detects musical key (C major, A minor, etc.) with confidence scores.

### Output Formats

Each analyzer generates:
- **JSON**: Structured data with all results
- **PNG**: Matplotlib visualizations
- **HTML**: Interactive reports with Plotly charts

Outputs saved to `music_analysis/outputs/`

**Chord Detection:**
```bash
python -m music_analysis.cli.analyze_chords audio.mp3
```
Detects chords using chroma features and template matching.

**Structure Analysis:**
```bash
python -m music_analysis.cli.analyze_structure audio.mp3
```
Segments audio into structural sections (intro, verse, chorus, etc.).

### All 4 Analyzers Available

✅ Tempo & Beat Tracking  
✅ Key Detection  
✅ Chord Detection  
✅ Structure Analysis

See [music_analysis/README.md](./music_analysis/README.md) for complete documentation.

---

## Contributing

This is a POC demonstrating technical feasibility. See [NEXT_STEPS.md](../../docs/Phase2-POC/backend/NEXT_STEPS.md) for future development directions.

---

## License

See project root for license information.

---

**Updated:** 2025-10-11  
**Version:** Phase A Complete, Phase B Week 1 Complete

