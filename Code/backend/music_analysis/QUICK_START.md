# Music Analysis - Quick Start Guide

**5-Minute Introduction to Phase B Tools**

---

## What Is This?

4 independent CLI tools that analyze music and extract semantic features:
- 🥁 **Tempo** - BPM and beat positions
- 🎹 **Key** - Musical key detection
- 🎸 **Chords** - Chord progression
- 📊 **Structure** - Song segmentation

---

## Quick Start (3 Commands)

### 1. Analyze Your First Song

```bash
cd Code/backend
python -m music_analysis.cli.analyze_tempo "../../docs/Audio/TOOL - The Pot (Audio).mp3"
```

**You'll get:**
- `outputs/TOOL - The Pot (Audio)_tempo.json` - Data
- `outputs/TOOL - The Pot (Audio)_tempo.png` - Visualization  
- `outputs/TOOL - The Pot (Audio)_tempo.html` - Interactive report

### 2. View HTML Report

```bash
# Windows
start music_analysis/outputs/"TOOL - The Pot (Audio)_tempo.html"
```

**You'll see:**
- Interactive Plotly charts
- Summary metrics
- Full JSON data
- Beat timeline visualization

### 3. Try All Analyzers

```bash
# Tempo
python -m music_analysis.cli.analyze_tempo audio.mp3

# Key
python -m music_analysis.cli.analyze_key audio.mp3

# Chords
python -m music_analysis.cli.analyze_chords audio.mp3

# Structure
python -m music_analysis.cli.analyze_structure audio.mp3
```

---

## Common Use Cases

### Get BPM for DJ Mixing
```bash
python -m music_analysis.cli.analyze_tempo song.mp3 --format json
# Check the tempo field in JSON
```

### Find Song Key for Harmonic Mixing
```bash
python -m music_analysis.cli.analyze_key song.mp3 --format json
# Check key and scale fields
```

### Extract Chord Progression
```bash
python -m music_analysis.cli.analyze_chords song.mp3
# View chord timeline in HTML report
```

### Identify Song Sections
```bash
python -m music_analysis.cli.analyze_structure song.mp3
# See intro, verse, chorus boundaries
```

---

## Output Formats

### JSON - Structured Data
```json
{
  "tempo": 143.55,
  "beats": [0.5, 1.0, 1.5, ...],
  "duration": 383.6,
  "metadata": { ... }
}
```
**Use for:** Programmatic access, data analysis

### PNG - Static Visualization
- High-resolution plots (150 DPI)
- Waveform with overlays
- Professional quality
**Use for:** Reports, presentations

### HTML - Interactive Report
- Plotly interactive charts
- Collapsible JSON data
- Responsive design
**Use for:** Exploration, sharing results

---

## Performance

All analyzers are fast:

| Analyzer | Time for 6min song | Speed |
|----------|-------------------|-------|
| Tempo | 3.8s | 60x realtime |
| Key | 4.0s | 58x realtime |
| Chords | 10.2s | 23x realtime |
| Structure | 1.7s | 140x realtime |
| **All 4** | **19.7s** | **~20x realtime** |

---

## Advanced Options

### Custom Output Directory
```bash
python -m music_analysis.cli.analyze_tempo song.mp3 --output my_results/
```

### JSON Only (Faster)
```bash
python -m music_analysis.cli.analyze_tempo song.mp3 --format json
```

### Verbose Mode
```bash
python -m music_analysis.cli.analyze_tempo song.mp3 --verbose
```

### Time-Varying Key Detection
```bash
python -m music_analysis.cli.analyze_key song.mp3 --time-varying
```

### Adjust Chord Smoothing
```bash
python -m music_analysis.cli.analyze_chords song.mp3 --smoothing 10
```

---

## Next Steps

**Read Full Documentation:**
- `README.md` - Complete guide
- `AGENTS.md` - Architecture details
- `PHASE_B_COMPLETE.md` - Implementation report

**Try With Your Music:**
- Test with different genres
- Compare results across songs
- Export data for other tools

**Integrate with Visualizations (Phase 3):**
- Use tempo for animation speed
- Map chords to colors
- Trigger transitions at structure boundaries

---

## Troubleshooting

**No outputs generated:**
- Check you're in `Code/backend/` directory
- Verify audio file path is correct
- Use `--verbose` flag for details

**Missing plots:**
- Ensure matplotlib is installed
- Try `--format json` first

**Missing HTML:**
- Install plotly: `pip install plotly`
- Or use `--format plot` instead

---

## What's Next?

**Phase B+:** Genre classifier (optional)
- Pre-trained HuggingFace model available
- See `GENRE_CLASSIFIER_RESEARCH.md`
- ~2-3 hours to implement

**Phase 3:** MVP Integration
- Connect music features to visualizations
- Build intelligent audio-visual mapping
- See `docs/Phase2-POC/POC_PLAN.md` for 4 integration paths

---

**Last Updated:** 2025-10-11  
**Version:** 1.0.0  
**Status:** Production-ready

