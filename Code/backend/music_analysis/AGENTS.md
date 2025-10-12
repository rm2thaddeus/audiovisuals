---
phase: 2b
artifact: music_analysis_agents
project: audio_feature_explorer
owner: Aitor Patiño Diaz
updated: 2025-10-11
status: Phase B Implementation - Music Semantic Analysis
sources:
  - POC Plan: ../../../docs/Phase2-POC/POC_PLAN.md
  - ML Exploration: ../../../docs/Phase2-POC/ML_EXPLORATION_OPTIONS.md
  - Phase B Plan: phase-b-music-analysis.plan.md
links:
  profile: ../../../docs/Phase0-Alignment/PROFILE.yaml
  context: ../../../docs/Phase0-Alignment/CONTEXT.md
  poc_plan: ../../../docs/Phase2-POC/POC_PLAN.md
  backend_agents: ../AGENTS.md
---

# Music Analysis Agents - Phase B

## Status: 🚧 Implementation in Progress

**Goal**: Extract semantic music features using open-source ML models  
**Output**: Independent CLI tools with JSON + Plots + HTML reports  
**Integration**: Standalone tools, optional future connection to CPPN pipeline

---

## Purpose

Define sub-agents for music semantic analysis: extracting high-level musical information (chords, tempo, key, structure, instruments, genre, mood) from audio files.

Unlike the Phase A audio analyzer (FFT-only), these tools use specialized ML models to understand musical semantics.

---

## Architecture Overview

```
Audio File Input
  ↓
┌─────────────────────────────────────────────────┐
│ Music Analysis Agents (Independent)             │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ Tempo        │  │ Key          │            │
│  │ Analyzer     │  │ Detector     │            │
│  └──────┬───────┘  └──────┬───────┘            │
│         │                 │                     │
│  ┌──────▼───────┐  ┌──────▼───────┐            │
│  │ Chord        │  │ Structure    │            │
│  │ Detector     │  │ Analyzer     │            │
│  └──────┬───────┘  └──────┬───────┘            │
│         │                 │                     │
│  ┌──────▼──────────────────▼───────┐            │
│  │ Visualization & HTML Generator  │            │
│  └─────────────┬───────────────────┘            │
└────────────────┼─────────────────────────────────┘
                 ↓
        JSON + PNG + HTML Outputs
```

**Key Design Principles:**
- **Independence**: Each analyzer runs standalone
- **Consistency**: Common output format (JSON schema)
- **Modularity**: Easy to add new analyzers
- **Visualization**: Every analysis gets plots + HTML report

---

## Project Structure

```
Code/backend/music_analysis/
├── analyzers/                    # Core Analysis Agents
│   ├── __init__.py
│   ├── tempo_analyzer.py         # Tempo & beat tracking (librosa)
│   ├── key_detector.py           # Key detection (librosa)
│   ├── chord_detector.py         # Chord recognition (CREMA)
│   └── structure_analyzer.py     # Structure segmentation (MSAF)
│
├── cli/                          # CLI Command Agents
│   ├── __init__.py
│   ├── analyze_tempo.py          # Tempo analysis CLI
│   ├── analyze_key.py            # Key detection CLI
│   ├── analyze_chords.py         # Chord analysis CLI
│   └── analyze_structure.py      # Structure analysis CLI
│
├── visualization/                # Visualization Agents
│   ├── __init__.py
│   ├── plot_tempo.py             # Beat timeline plots
│   ├── plot_key.py               # Chroma feature heatmaps
│   ├── plot_chords.py            # Chord progression charts
│   ├── plot_structure.py         # Segment boundary plots
│   ├── html_generator.py         # HTML report builder
│   └── templates/
│       └── base_report.html      # HTML template
│
├── outputs/                      # Analysis results (gitignored)
├── AGENTS.md                     # This file
├── README.md                     # Usage guide
└── requirements.txt              # Dependencies
```

---

## Sub-Agents

### Tempo Analyzer Agent

**Purpose**: Extract tempo (BPM) and beat positions

**Triggers**: User runs `python -m music_analysis.cli.analyze_tempo audio.mp3`

**Inputs**:
- Audio file (MP3, WAV, FLAC, etc.)
- Optional: onset sensitivity, hop length

**Outputs**:
```json
{
  "tempo": 120.5,
  "tempo_confidence": 0.87,
  "beats": [0.5, 1.0, 1.5, 2.0, ...],
  "beat_frames": [22050, 44100, 66150, ...],
  "hop_length": 512,
  "sr": 22050,
  "duration": 180.5,
  "processing_time": 2.3,
  "metadata": {
    "filename": "song.mp3",
    "analyzer": "tempo_analyzer",
    "version": "0.1.0",
    "timestamp": "2025-10-11T23:30:00"
  }
}
```

**Implementation**: `analyzers/tempo_analyzer.py`

**Protocol**:
1. Load audio with librosa (sr=22050)
2. Extract onset envelope
3. Estimate tempo using `librosa.beat.tempo()`
4. Track beats using `librosa.beat.beat_track()`
5. Calculate beat confidence (consistency)
6. Return structured JSON output

**Dependencies**: librosa (already available)

**Performance**: ~0.5-2s for 3min audio

**Subroles**:
- Audio Loader: Load and validate audio file
- Onset Detector: Compute onset strength envelope
- Tempo Estimator: Global BPM estimation
- Beat Tracker: Frame-by-frame beat positions

---

### Key Detector Agent

**Purpose**: Detect musical key (C major, A minor, etc.)

**Triggers**: User runs `python -m music_analysis.cli.analyze_key audio.mp3`

**Inputs**:
- Audio file
- Optional: window size for time-varying analysis

**Outputs**:
```json
{
  "key": "C",
  "scale": "major",
  "confidence": 0.78,
  "key_profile": [0.85, 0.12, 0.45, ...],
  "alternatives": [
    {"key": "Am", "confidence": 0.65},
    {"key": "G", "confidence": 0.52}
  ],
  "chroma_features": [[0.8, 0.2, ...], ...],
  "duration": 180.5,
  "processing_time": 1.8,
  "metadata": { ... }
}
```

**Implementation**: `analyzers/key_detector.py`

**Protocol**:
1. Load audio with librosa
2. Extract chroma features (STFT or CQT)
3. Compute average chroma vector
4. Correlate with key profiles (Krumhansl-Schmuckler)
5. Rank keys by correlation score
6. Return top key + alternatives

**Dependencies**: librosa, numpy

**Performance**: ~1-3s for 3min audio

**Algorithm**: Krumhansl-Schmuckler key-finding algorithm using chroma correlation

**Subroles**:
- Chroma Extractor: Compute pitch class features
- Key Profiler: Compare with known key templates
- Confidence Scorer: Rank key hypotheses

---

### Chord Detector Agent

**Purpose**: Detect chord progression throughout the track

**Triggers**: User runs `python -m music_analysis.cli.analyze_chords audio.mp3`

**Inputs**:
- Audio file
- Optional: hop size, chord vocabulary

**Outputs**:
```json
{
  "chords": [
    {"time": 0.0, "chord": "C:maj", "confidence": 0.92},
    {"time": 2.5, "chord": "G:maj", "confidence": 0.88},
    {"time": 5.0, "chord": "Am", "confidence": 0.85},
    {"time": 7.5, "chord": "F:maj", "confidence": 0.90}
  ],
  "chord_vocabulary": ["C:maj", "G:maj", "Am", "F:maj", ...],
  "chord_changes": 32,
  "duration": 180.5,
  "processing_time": 25.3,
  "model": "CREMA",
  "metadata": { ... }
}
```

**Implementation**: `analyzers/chord_detector.py`

**Protocol**:
1. Load audio
2. Load CREMA pre-trained model
3. Extract features (mel spectrogram or CQT)
4. Run inference frame-by-frame
5. Post-process: smooth predictions, merge short segments
6. Return chord timeline

**Dependencies**: CREMA, tensorflow, librosa

**Performance**: ~20-30s for 3min audio (ML inference)

**Model**: CREMA (Convolutional and Recurrent Estimators for Music Analysis)

**Subroles**:
- Feature Extractor: Audio → ML features
- Chord Predictor: ML model inference
- Post-Processor: Smooth and merge predictions

---

### Structure Analyzer Agent

**Purpose**: Segment track into structural sections (intro, verse, chorus, etc.)

**Triggers**: User runs `python -m music_analysis.cli.analyze_structure audio.mp3`

**Inputs**:
- Audio file
- Optional: algorithm choice (CNMF, Foote, etc.), boundary sensitivity

**Outputs**:
```json
{
  "segments": [
    {"start": 0.0, "end": 15.2, "label": "intro", "confidence": 0.85},
    {"start": 15.2, "end": 45.8, "label": "verse1", "confidence": 0.78},
    {"start": 45.8, "end": 76.5, "label": "chorus1", "confidence": 0.92},
    {"start": 76.5, "end": 107.0, "label": "verse2", "confidence": 0.80}
  ],
  "num_segments": 8,
  "boundary_times": [15.2, 45.8, 76.5, 107.0, ...],
  "similarity_matrix": [[1.0, 0.3, ...], ...],
  "algorithm": "CNMF",
  "duration": 180.5,
  "processing_time": 12.5,
  "metadata": { ... }
}
```

**Implementation**: `analyzers/structure_analyzer.py`

**Protocol**:
1. Load audio
2. Extract self-similarity features (MFCC, chroma, timbre)
3. Compute self-similarity matrix
4. Run MSAF segmentation algorithm (CNMF, Foote, or Levy)
5. Label segments (intro, verse, chorus, etc. if possible)
6. Return segment boundaries + metadata

**Dependencies**: MSAF, librosa, numpy, scipy

**Performance**: ~10-20s for 3min audio

**Algorithm**: Music Structure Analysis Framework (MSAF) with CNMF or Foote novelty

**Subroles**:
- Feature Extractor: Audio → self-similarity features
- Boundary Detector: Find structural change points
- Label Assigner: Infer section types (optional)

---

## CLI Coordinator Agents

### Pattern for All CLI Commands

**Purpose**: Provide user-facing command-line interface

**Triggers**: User invocation via `python -m music_analysis.cli.analyze_*`

**Common Arguments**:
```bash
python -m music_analysis.cli.analyze_tempo audio.mp3 \
  --output outputs/ \
  --format both \
  --verbose
```

**Protocol** (applies to all CLI commands):
1. Parse arguments with argparse
2. Validate audio file exists
3. Create output directory if needed
4. Run analyzer (show progress if verbose)
5. Save JSON results
6. Generate matplotlib plot
7. Generate HTML report (if requested)
8. Print summary and output paths

**Error Handling**:
- File not found → clear error message
- Unsupported format → suggest valid formats
- Analysis failure → log error, suggest troubleshooting
- Missing dependencies → installation instructions

**Subroles**:
- Argument Parser: CLI interface
- File Validator: Check inputs
- Progress Reporter: User feedback
- Output Manager: Save results

---

## Visualization Agents

### Plot Generator Agents

**Purpose**: Create matplotlib visualizations for each analysis type

**Implementations**:
- `plot_tempo.py`: Waveform + beat markers
- `plot_key.py`: Chroma heatmap + key profile
- `plot_chords.py`: Chord progression timeline
- `plot_structure.py`: Spectrogram + segment boundaries

**Common Pattern**:
```python
def plot_analysis(results: dict, audio_path: str, output_path: Path) -> None:
    """Generate visualization plot."""
    # Load audio for waveform
    y, sr = librosa.load(audio_path)
    
    # Create figure
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    
    # Plot waveform
    librosa.display.waveshow(y, sr=sr, ax=axes[0])
    
    # Overlay analysis results
    # (beats, chords, boundaries, etc.)
    
    # Save high-res PNG
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
```

**Subroles**:
- Waveform Plotter: Audio visualization
- Feature Overlay: Add analysis results
- Style Manager: Consistent visual style

---

### HTML Report Generator Agent

**Purpose**: Create interactive HTML reports with embedded visualizations

**Triggers**: CLI command with `--format html` or `--format both`

**Implementation**: `visualization/html_generator.py`

**Protocol**:
1. Load HTML template
2. Embed JSON results
3. Add Plotly interactive charts (if available)
4. Embed matplotlib PNG (base64 or file reference)
5. Add metadata (file info, processing time, model versions)
6. Save HTML file

**Template** (`templates/base_report.html`):
- Modern, responsive design
- Collapsible sections for JSON data
- Interactive charts (Plotly.js)
- Print-friendly styles
- Dark mode support (optional)

**Subroles**:
- Template Renderer: HTML generation
- Chart Builder: Interactive Plotly charts
- Data Embedder: JSON + images in HTML

---

## Handoff Protocols

### Audio File → Analyzer
- **Input**: Path to audio file (string)
- **Validation**: Check file exists, format supported
- **Loading**: librosa.load() with appropriate sr
- **Error**: Raise clear exception if load fails

### Analyzer → JSON Output
- **Format**: Consistent schema across all analyzers
- **Required fields**: results, duration, processing_time, metadata
- **Timestamps**: Seconds (float) for all time values
- **Confidence**: 0.0-1.0 range where applicable

### JSON → Visualization
- **Input**: Parsed JSON dict + original audio path
- **Output**: PNG file saved to disk
- **Requirements**: High resolution (150+ DPI), readable labels
- **Style**: Consistent colors/fonts across analyzers

### Visualization → HTML Report
- **Input**: JSON dict + PNG path
- **Output**: Self-contained HTML file
- **Features**: Embedded images, interactive charts, responsive
- **Accessibility**: Proper headings, alt text, ARIA labels

---

## Success Criteria (Phase B)

### Week 1: Foundation ✅ COMPLETE
- [x] Directory structure created
- [x] AGENTS.md documentation complete
- [x] Tempo analyzer implemented
- [x] Key detector implemented
- [x] CLI commands for tempo + key
- [x] Visualization functions (matplotlib)
- [x] HTML report generation (Plotly)
- [x] Tested with sample audio

### Week 2: Core Models 🚧
- [ ] Chord detector (CREMA) implemented
- [ ] Structure analyzer (MSAF) implemented
- [ ] All 4 CLI commands functional
- [ ] Basic matplotlib plots for all analyzers

### Week 3: Polish 📋
- [ ] HTML report generation working
- [ ] Interactive Plotly visualizations
- [ ] Full testing on sample audio
- [ ] Documentation complete (README.md)

### Week 4: Integration 📋
- [ ] requirements.txt finalized
- [ ] Backend README.md updated
- [ ] Test suite passing
- [ ] Performance benchmarks documented

---

## Technical Specifications

### Output JSON Schema

All analyzers follow this base schema:

```json
{
  "results": {
    /* Analyzer-specific results */
  },
  "duration": 180.5,
  "processing_time": 2.3,
  "metadata": {
    "filename": "song.mp3",
    "filepath": "/path/to/song.mp3",
    "analyzer": "tempo_analyzer",
    "version": "0.1.0",
    "model": "librosa",
    "timestamp": "2025-10-11T23:30:00",
    "sample_rate": 22050,
    "audio_duration": 180.5
  }
}
```

### Performance Targets

| Analyzer | Target Time (3min audio) | Actual |
|----------|--------------------------|--------|
| Tempo    | <3s                      | TBD    |
| Key      | <3s                      | TBD    |
| Chords   | <30s                     | TBD    |
| Structure| <20s                     | TBD    |

### Dependencies

**Core** (already available):
- librosa >= 0.10.0
- numpy >= 1.24.0
- scipy >= 1.10.0
- matplotlib >= 3.7.0

**New** (Phase B):
- CREMA >= 0.1.0 (chord detection)
- MSAF >= 0.1.80 (structure analysis)
- tensorflow >= 2.13.0 (for CREMA)
- plotly >= 5.0.0 (interactive charts)
- music21 >= 9.1.0 (optional, music theory utilities)

**Optional** (Phase B+):
- essentia >= 2.1b6 (instruments, genre, mood)
- jinja2 >= 3.0.0 (HTML templating)

---

## Future Enhancements (Phase B+)

### Additional Analyzers

**Instrument Detector**:
- Essentia instrument detection models
- Output: Instrument presence timeline
- CLI: `python -m music_analysis.cli.analyze_instruments`

**Genre Classifier**:
- MusiCNN or Essentia genre models
- Output: Genre probabilities
- CLI: `python -m music_analysis.cli.analyze_genre`

**Mood Analyzer**:
- Essentia mood/emotion models
- Output: Valence, arousal, mood labels
- CLI: `python -m music_analysis.cli.analyze_mood`

### Integration with CPPN Pipeline

**Phase C (Optional)**:
- Connect music analysis to visualization
- Chord → Color palette modulation
- Structure → Visual transition triggers
- Tempo → Animation speed sync
- Key → Color harmony rules

**Implementation**: Add flag to main CLI
```bash
python cli.py audio.mp3 output.mp4 \
  --use-music-analysis \
  --chords --structure --tempo
```

---

## Development Guidelines

### Code Style
- Follow PEP 8
- Type hints for all functions
- Docstrings with examples
- Error handling with informative messages

### Testing
- Unit tests for each analyzer
- Integration tests for CLI commands
- Test with multiple music genres
- Validate JSON schema compliance

### Documentation
- Inline code comments for complex logic
- README with quick start examples
- Model accuracy notes and limitations
- Performance benchmarks

### Version Control
- Small, focused commits
- Update `updated` field in AGENTS.md
- Document breaking changes
- Tag releases (v0.1.0, v0.2.0, etc.)

---

## Notes

### Model Selection Rationale

**Tempo/Key (librosa)**:
- ✅ Already available, no new dependencies
- ✅ Fast, reliable for most music
- ✅ Good starting point for Phase B

**Chords (CREMA)**:
- ✅ State-of-art open-source chord recognition
- ✅ Pre-trained on large music dataset
- ⚠️ Requires tensorflow (check GPU compatibility)

**Structure (MSAF)**:
- ✅ Mature, well-documented framework
- ✅ Multiple algorithms (CNMF, Foote, Levy)
- ✅ Pure Python, easy installation

### Known Limitations

1. **Genre dependency**: Models trained on Western music may struggle with non-Western genres
2. **Recording quality**: Poor audio quality affects all analyzers
3. **Real-time**: Current implementation is offline (batch processing)
4. **Labeling**: Structure segment labels (verse/chorus) require heuristics or training data

### References

- **CREMA**: https://github.com/bmcfee/crema
- **MSAF**: https://github.com/urinieto/msaf
- **librosa**: https://librosa.org/doc/latest/
- **Essentia**: https://essentia.upf.edu/

---

**Updated**: 2025-10-11  
**Status**: Implementation in progress  
**Next**: Implement tempo and key analyzers

