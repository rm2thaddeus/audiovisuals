# Music Analysis Tools - Phase B

Independent CLI tools for semantic music feature extraction using ML models.

## Overview

This module provides music-specific analysis tools that extract high-level semantic features from audio files:

- **Tempo & Beat Tracking**: BPM estimation and beat timestamps
- **Key Detection**: Musical key identification (C major, A minor, etc.)
- **Chord Detection**: Frame-by-frame chord recognition
- **Structure Analysis**: Song section segmentation
- **Genre Classification**: Automatic genre labeling with pre-trained models
- **Instrument Detection**: Identify instruments present *(future)*
- **Mood Analysis**: Emotional content detection *(future)*

Each analyzer outputs:
- **JSON**: Structured data with all analysis results
- **PNG Plots**: Matplotlib visualizations
- **HTML Reports**: Interactive reports with embedded data and charts

## Quick Start

### Installation

The core analyzers (tempo, key) use only librosa, which should already be installed:

```bash
# Core dependencies already installed with main backend
cd Code/backend
# No additional installation needed for tempo and key analyzers

# Optional: Install Plotly for interactive HTML charts
pip install plotly>=5.0.0

# Genre classifier (HuggingFace Transformers)
pip install transformers>=4.38.0
```

> First run of the genre classifier will download a ~100 MB model from HuggingFace.

### Basic Usage

**Tempo Analysis:**
```bash
python -m music_analysis.cli.analyze_tempo song.mp3
```

**Key Detection:**
```bash
python -m music_analysis.cli.analyze_key song.mp3
```

**Genre Classification:**
```bash
python -m music_analysis.cli.analyze_genre song.mp3
```

**Specify Output Directory:**
```bash
python -m music_analysis.cli.analyze_tempo song.mp3 --output results/
python -m music_analysis.cli.analyze_key song.mp3 --output results/
python -m music_analysis.cli.analyze_genre song.mp3 --output results/
```

**JSON Only (no plots):**
```bash
python -m music_analysis.cli.analyze_tempo song.mp3 --format json
```

## Analyzer Details

### Tempo Analyzer

Extracts tempo (BPM) and beat positions using librosa beat tracking.

**Features:**
- Global tempo estimation
- Beat timestamps with frame indices
- Beat confidence scoring
- Time signature detection (4/4 vs 3/4)

**Usage:**
```bash
python -m music_analysis.cli.analyze_tempo audio.mp3 \
  --output results/ \
  --start-bpm 140 \
  --verbose
```

**Arguments:**
- `audio`: Input audio file (required)
- `--output, -o`: Output directory (default: music_analysis/outputs/)
- `--format, -f`: Output format: json, plot, html, both (default: both)
- `--start-bpm`: Initial BPM estimate for tracking (default: 120)
- `--hop-length`: Hop length for analysis (default: 512)
- `--verbose, -v`: Verbose output

**Output Example:**
```json
{
  "tempo": 120.5,
  "tempo_confidence": 0.87,
  "time_signature": "4/4",
  "num_beats": 180,
  "beats": [0.5, 1.0, 1.5, ...],
  "duration": 180.5,
  "processing_time": 2.3
}
```

**Performance:** ~0.5-2s for 3min audio

---

### Key Detector

Detects musical key using Krumhansl-Schmuckler algorithm with chroma features.

**Features:**
- Global key detection (C major, A minor, etc.)
- Confidence scoring
- Alternative key candidates
- Relative major/minor keys
- Time-varying key analysis (detect key changes)

**Usage:**
```bash
# Global key detection
python -m music_analysis.cli.analyze_key audio.mp3

# Detect key changes over time
python -m music_analysis.cli.analyze_key audio.mp3 --time-varying --window-size 30
```

**Arguments:**
- `audio`: Input audio file (required)
- `--output, -o`: Output directory (default: music_analysis/outputs/)
- `--format, -f`: Output format: json, plot, html, both (default: both)
- `--time-varying`: Analyze key changes over time (slower)
- `--window-size`: Window size for time-varying analysis in seconds (default: 30)
- `--hop-length`: Hop length for chroma extraction (default: 512)
- `--verbose, -v`: Verbose output

**Output Example:**
```json
{
  "key": "C",
  "scale": "major",
  "confidence": 0.78,
  "relative_key": "A minor",
  "alternatives": [
    {"key": "G major", "confidence": 0.65},
    {"key": "F major", "confidence": 0.52}
  ],
  "duration": 180.5,
  "processing_time": 1.8
}
```

**Performance:** ~1-3s for 3min audio (global), ~5-10s (time-varying)

---

### Chord Detector ✅

Frame-by-frame chord detection using chroma features and template matching.

**Features:**
- Chord recognition (major and minor triads)
- Chord vocabulary extraction
- Chord change detection
- Confidence scoring

**Usage:**
```bash
python -m music_analysis.cli.analyze_chords audio.mp3
python -m music_analysis.cli.analyze_chords audio.mp3 --smoothing 10
```

**Arguments:**
- `audio`: Input audio file (required)
- `--output, -o`: Output directory (default: music_analysis/outputs/)
- `--format, -f`: Output format: json, plot, html, both (default: both)
- `--smoothing`: Smoothing window size (default: 5 frames)
- `--verbose, -v`: Verbose output

**Output Example:**
```json
{
  "chords": [
    {"time": 0.5, "chord": "C", "confidence": 0.92, "duration": 2.1},
    {"time": 2.6, "chord": "G", "confidence": 0.88, "duration": 1.8}
  ],
  "chord_vocabulary": ["C", "G", "Am", "F"],
  "chord_changes": 142,
  "unique_chords": 18
}
```

**Performance:** ~10s for 6min audio

**Note:** Uses chroma-based template matching. For more accurate results, CREMA model can be integrated (requires TensorFlow).

---

### Structure Analyzer ✅

Segment audio into structural sections (intro, verse, chorus, bridge, outro).

**Features:**
- Automatic boundary detection
- Section labeling
- Segment duration analysis
- Simple fallback segmentation (when MSAF unavailable)

**Usage:**
```bash
python -m music_analysis.cli.analyze_structure audio.mp3
python -m music_analysis.cli.analyze_structure audio.mp3 --algorithm cnmf
```

**Arguments:**
- `audio`: Input audio file (required)
- `--output, -o`: Output directory (default: music_analysis/outputs/)
- `--format, -f`: Output format: json, plot, html, both (default: both)
- `--algorithm`: Segmentation algorithm (default: cnmf)
- `--verbose, -v`: Verbose output

**Output Example:**
```json
{
  "segments": [
    {"start": 0.0, "end": 15.2, "label": "intro", "duration": 15.2},
    {"start": 15.2, "end": 45.8, "label": "section_1", "duration": 30.6}
  ],
  "num_segments": 12,
  "boundary_times": [0.0, 15.2, 45.8, ...],
  "algorithm": "cnmf"
}
```

**Performance:** ~1-2s for 6min audio (fallback method)

**Note:** Currently using simple time-based segmentation due to MSAF compatibility issues. Full MSAF integration can be added when dependencies are resolved.

---

### Genre Classifier ✅

Genre prediction using the pre-trained `storylinez/audio-genre-classifier` HuggingFace model.

**Features:**
- Ten-genre classifier trained on the GTZAN dataset
- Segment-level analysis with configurable window size and overlap
- Aggregated probability distribution with JSON, PNG, and HTML outputs
- GPU acceleration when CUDA is available

**Usage:**
```bash
python -m music_analysis.cli.analyze_genre audio.mp3
python -m music_analysis.cli.analyze_genre audio.mp3 --window-seconds 45 --overlap 0.5
```

**Arguments:**
- `audio`: Input audio file (required)
- `--output, -o`: Output directory (default: music_analysis/outputs/)
- `--format, -f`: Output format: json, plot, html, both (default: both)
- `--window-seconds`: Window length in seconds (default: 30.0)
- `--overlap`: Overlap ratio between windows (default: 0.25)
- `--top-k`: Number of top predictions to keep (default: 5)
- `--max-chunks`: Limit number of windows processed (optional)
- `--device`: `auto`, `cpu`, or `cuda` (default: auto)
- `--model`: HuggingFace model identifier (default: storylinez/audio-genre-classifier)

**Output Example:**
```json
{
  "predicted_genre": "rock",
  "predicted_confidence": 0.82,
  "predictions": [
    {"genre": "rock", "score": 0.82, "logit": 3.42},
    {"genre": "metal", "score": 0.09, "logit": 1.02},
    {"genre": "pop", "score": 0.05, "logit": 0.61}
  ],
  "chunk_predictions": [
    {"start": 0.0, "end": 30.0, "top_genre": "rock", "confidence": 0.79},
    {"start": 22.5, "end": 52.5, "top_genre": "rock", "confidence": 0.86}
  ]
}
```

**Performance:** ~4-6s for a 3 min track on RTX 5070 (first run downloads model ~100 MB)

**Note:** Requires `transformers>=4.38.0`. Model downloads are cached in the HuggingFace directory (`~/.cache/huggingface/` by default).

---

## Output Formats

### JSON Output

All analyzers produce structured JSON with consistent schema:

```json
{
  "results": {
    /* Analyzer-specific results */
  },
  "duration": 180.5,
  "processing_time": 2.3,
  "metadata": {
    "filename": "song.mp3",
    "analyzer": "tempo_analyzer",
    "version": "0.1.0",
    "timestamp": "2025-10-11T23:30:00",
    "sample_rate": 22050
  }
}
```

**Location:** `music_analysis/outputs/<filename>_<analyzer>.json`

### PNG Plots

High-resolution matplotlib visualizations (150 DPI):

- **Tempo**: Waveform with beat markers, onset envelope, interval histogram
- **Key**: Chromagram, chroma profile, key candidates, waveform

**Location:** `music_analysis/outputs/<filename>_<analyzer>.png`

### HTML Reports

Self-contained interactive HTML reports with:
- Summary cards with key metrics
- Embedded PNG plots
- Interactive Plotly charts
- Collapsible raw JSON data
- Responsive design, print-friendly

**Location:** `music_analysis/outputs/<filename>_<analyzer>.html`

**View in browser:**
```bash
# Windows
start music_analysis/outputs/song_tempo.html

# Linux/Mac
open music_analysis/outputs/song_tempo.html
```

---

## Architecture

See `AGENTS.md` for detailed architecture documentation.

**Module Structure:**
```
music_analysis/
├── analyzers/           # Core analysis algorithms
│   ├── tempo_analyzer.py
│   ├── key_detector.py
│   └── ...
├── cli/                 # Command-line interfaces
│   ├── analyze_tempo.py
│   ├── analyze_key.py
│   └── ...
├── visualization/       # Plotting and HTML generation
│   ├── plot_tempo.py
│   ├── plot_key.py
│   └── html_generator.py
└── outputs/             # Analysis results (gitignored)
```

---

## Integration with Main Pipeline

These analyzers are **independent** by design. They can optionally be integrated with the main CPPN visualization pipeline in the future:

**Potential Phase C Integration:**
- Chord progressions → Color palette modulation
- Structure segments → Visual transition triggers
- Tempo → Animation speed synchronization
- Key → Color harmony rules

**Example Future CLI:**
```bash
python cli.py audio.mp3 output.mp4 \
  --use-music-analysis \
  --chords --structure --tempo
```

---

## Testing

Test with sample audio:

```bash
# Test tempo analyzer
python -m music_analysis.cli.analyze_tempo "../docs/Audio/TOOL - The Pot (Audio).mp3" --verbose

# Test key detector
python -m music_analysis.cli.analyze_key "../docs/Audio/TOOL - The Pot (Audio).mp3" --verbose

# Test time-varying key
python -m music_analysis.cli.analyze_key "../docs/Audio/TOOL - The Pot (Audio).mp3" --time-varying --verbose
```

Expected results:
- JSON files in `music_analysis/outputs/`
- PNG plots in `music_analysis/outputs/`
- HTML reports in `music_analysis/outputs/`

---

## Known Limitations

### Model Limitations

1. **Genre Dependency**: Models trained primarily on Western music may struggle with non-Western genres
2. **Recording Quality**: Poor audio quality affects all analyzers
3. **Time Signature**: Simple 4/4 vs 3/4 detection only (complex signatures not supported)
4. **Key Changes**: Global key detection may miss temporary modulations

### Performance

- **Tempo**: Very fast (<3s for 3min audio)
- **Key**: Fast (<3s global, ~10s time-varying)
- **Chords** *(future)*: Slower (~20-30s, requires GPU for real-time)
- **Structure** *(future)*: Moderate (~10-20s)

### Platform

- **Windows**: Fully supported
- **Linux/Mac**: Should work, not extensively tested
- **Essentia**: May be difficult to install on Windows (optional dependency)

---

## Troubleshooting

**Import errors:**
```
ModuleNotFoundError: No module named 'music_analysis'
```
Solution: Run from `Code/backend/` directory or ensure Python path is correct

**Audio loading errors:**
```
Error: Audio file not found
```
Solution: Use absolute paths or check file path is correct

**Missing plots:**
```
Warning: Visualization module not available
```
Solution: Install matplotlib (should be already installed with main backend)

**Missing interactive charts:**
```
Warning: HTML generator not available
```
Solution: Install plotly: `pip install plotly>=5.0.0`

---

## Development

### Adding New Analyzers

1. Create analyzer class in `analyzers/new_analyzer.py`
2. Implement `analyze()` method returning consistent JSON schema
3. Create CLI command in `cli/analyze_new.py`
4. Create plot function in `visualization/plot_new.py`
5. Update HTML generator to support new type
6. Add documentation to README and AGENTS.md

### Code Style

- Follow PEP 8
- Type hints for all functions
- Docstrings with examples
- Error handling with informative messages

### Testing

Run tests from `Code/backend/`:
```bash
# Unit tests (when implemented)
pytest music_analysis/tests/

# Manual testing
python -m music_analysis.cli.analyze_tempo <test_audio>
```

---

## References

- **librosa**: https://librosa.org/doc/latest/
- **Krumhansl-Schmuckler**: Key-finding algorithm for key detection
- **CREMA** *(future)*: https://github.com/bmcfee/crema
- **MSAF** *(future)*: https://github.com/urinieto/msaf
- **Essentia** *(future)*: https://essentia.upf.edu/

---

## Status

**Phase B - Complete** ✅
- [x] Directory structure created
- [x] AGENTS.md documentation
- [x] Tempo analyzer implemented (librosa)
- [x] Key detector implemented (Krumhansl-Schmuckler)
- [x] Chord detector implemented (chroma-based)
- [x] Structure analyzer implemented (time-based fallback)
- [x] Genre classifier implemented (HuggingFace Transformers)
- [x] CLI commands for all 5 analyzers
- [x] Visualization functions (matplotlib)
- [x] HTML report generation (Plotly, including genre)
- [x] Tested with sample audio

**All 5 music analyzers fully functional!**

---

**Updated:** 2025-10-12  
**Author:** Aitor Patiño Diaz  
**Version:** 0.1.0
