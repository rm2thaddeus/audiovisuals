# Visual Explorations - CLIP-Optimized Results

**Purpose**: Storage for CLIP-guided training experiments and mood board explorations  
**Status**: Active development - Major breakthrough achieved!  
**Date**: October 11, 2025

---

## 🎨 What This Directory Contains

### CLIP-Optimized Visualizations

This directory stores results from **CLIP-guided CPPN training experiments** - networks trained to generate specific visual aesthetics using text prompts.

**Key Difference from Code Explorations**:
- **`Code/backend/explorations/`** - Training metadata, weights, technical data
- **`docs/explorations/`** - Full videos, HTML viewers, presentation materials

This directory has the **visual outputs** ready for viewing and presentation.

---

## 📁 Current Explorations

### clip_organic_20251011/ (CLIP TRAINING SUCCESS! 🎉)

**Prompt**: "Organic flowing shapes diffusing into each other with strong contrast"

**Status**: ✅ **COMPLETE** - Major milestone achieved!

**Contents**:
- `index.html` - Interactive comparison viewer (OPEN THIS!)
- `organic_diffuse_128dim_full.mp4` - TOOL video, 128 dim (409 MB) 🏆
- `organic_diffuse_256dim_full.mp4` - TOOL video, 256 dim (390 MB)
- `zyryab_organic_128dim.mp4` - Zyryab video, 128 dim (373 MB) 🏆
- `zyryab_organic_256dim.mp4` - Zyryab video, 256 dim (351 MB)
- Preview images and comparison docs

**Key Findings**:
- **128 dim wins!** (0.2452 vs 0.2217 CLIP similarity)
- **Yellow-green palette** emerged from prompt
- **Styles are reusable** - Same weights on different music
- **Training is fast** - 6-8 minutes per architecture

**View**: Open `clip_organic_20251011/index.html` for full demo

---

### music_analysis_20251012/ (PHASE B COMPLETE! 🎵)

**Purpose**: Complete music semantic analysis baseline - understand the music before visualizing it!

**Status**: ✅ **COMPLETE** - All 5 analyzers working!

**Contents**:
- `index.html` - Master analysis viewer (OPEN THIS!)
- `tool/` - TOOL analysis (15 files: 5 analyzers × 3 formats)
- `zyryab/` - Zyryab analysis (15 files: 5 analyzers × 3 formats)
- `FINDINGS.md` - Detailed insights and visual mapping strategies
- `README.md` - Usage guide

**Analyzers Implemented:**
1. **Tempo** - BPM, beats, time signature (librosa)
2. **Key** - Musical key detection (Krumhansl-Schmuckler)
3. **Chords** - Progression timeline (Chroma template matching)
4. **Structure** - Segment boundaries (Time-based)
5. **Audio Events** - 527 classes: genres, instruments, vocals (AST) ⭐

**Key Findings**:
- **TOOL correctly identified:** Heavy metal, Progressive rock, Electric guitar
- **Zyryab correctly identified:** Flamenco (6.7%!), Acoustic strings, Spanish style
- **Processing:** ~20-24s per 6min track (6% of duration)
- **Rich data:** Tempo, key, chords, structure, 527 audio event classes

**Impact for Visualization:**
- Genre → Auto-select visual styles
- Instruments → Layer-based patterns
- Tempo → Animation speed
- Key → Color harmony
- Chords → Color transitions
- Structure → Scene changes

**View**: Open `music_analysis_20251012/index.html` for all results

---

## 🎯 Future Explorations (Planned)

### Mood Board Series

**Goal**: Create visual palettes for different concepts/moods

#### Urban/Electronic Theme
- `clip_cyberpunk_DATE/` - Neon geometric pink/blue
- `clip_glitch_DATE/` - Digital corruption red/black
- `clip_matrix_DATE/` - Green cascading code patterns

#### Nature/Organic Theme
- `clip_forest_DATE/` - Fractal trees green/brown
- `clip_ocean_DATE/` - Underwater waves blue/teal
- `clip_fire_DATE/` - Flames orange/red/yellow

#### Space/Cosmic Theme
- `clip_nebula_DATE/` - Deep space purple/blue
- `clip_solar_DATE/` - Sun corona orange/yellow
- `clip_aurora_DATE/` - Northern lights green/purple

#### Abstract/Artistic Theme
- `clip_pastel_DATE/` - Soft watercolor pink/lavender
- `clip_monochrome_DATE/` - Black and white high contrast
- `clip_rainbow_DATE/` - Vibrant multi-color abstract

**Timeline**: 1-2 styles per week, 15-20 total in 2-3 months

---

## 📊 Organization Structure

```
docs/explorations/
├── README.md                           # This file
│
├── clip_organic_20251011/              # First successful optimization
│   ├── index.html                      # ⭐ Interactive viewer
│   ├── organic_diffuse_128dim_full.mp4 # TOOL (128 dim, winner)
│   ├── organic_diffuse_256dim_full.mp4 # TOOL (256 dim)
│   ├── zyryab_organic_128dim.mp4       # Zyryab (128 dim, winner)
│   ├── zyryab_organic_256dim.mp4       # Zyryab (256 dim)
│   ├── *.png                           # Preview images
│   └── COMPARISON_RESULTS.md           # Analysis
│
├── clip_cyberpunk_DATE/                # Future: Neon aesthetic
├── clip_cosmic_DATE/                   # Future: Space aesthetic
├── clip_nature_DATE/                   # Future: Organic aesthetic
└── [future mood boards...]
```

---

## 🎨 How to Use This Directory

### Viewing Results

**Interactive HTML Viewers**:
```bash
# Open any exploration's index.html
docs/explorations/clip_organic_20251011/index.html
```

Each exploration directory has an `index.html` with:
- Side-by-side architecture comparison
- Embedded video players with audio
- Technical stats and CLIP scores
- Download buttons for videos and weights

### Downloading Videos

All videos are self-contained with audio:
- Ready to share
- Ready to present
- Ready for editing/post-processing

### Reusing Trained Weights

Weights are stored in `Code/backend/explorations/trained/`, referenced from HTML.

**Generate new video with trained style**:
```bash
cd Code/backend
python cli.py "audio.mp3" output.mp4 \
    --load-weights explorations/trained/clip_organic_20251011/organic_diffuse_128dim.pth \
    --resolution 720p --fps 30
```

---

## 🔬 Mood Board Experimentation Workflow

### 1. Choose Concept
Decide on aesthetic goal (cyberpunk, cosmic, nature, etc.)

### 2. Craft Prompt
Write descriptive text:
- Include structure keywords (flowing, geometric, fractal, etc.)
- Include mood keywords (vibrant, soft, harsh, gentle, etc.)
- Include color hints (blues, oranges, pastels, neon, etc.)

### 3. Run Optimization
```bash
cd Code/backend
python clip_optimize_cppn.py \
    --prompt "YOUR AESTHETIC DESCRIPTION" \
    --audio "../../docs/Audio/TOOL - The Pot (Audio).mp3" \
    --output "explorations/trained/clip_CONCEPT_DATE/style.pth" \
    --hidden-dim 128 \
    --iterations 400
```

### 4. Generate Test Videos
```bash
# Full length (6+ minutes)
python cli.py "../../docs/Audio/TOOL - The Pot (Audio).mp3" \
    "../../docs/explorations/clip_CONCEPT_DATE/tool_full.mp4" \
    --load-weights explorations/trained/clip_CONCEPT_DATE/style.pth \
    --resolution 720p --fps 30

# Test with second track
python cli.py "../../docs/Audio/Zyryab.mp3" \
    "../../docs/explorations/clip_CONCEPT_DATE/zyryab_full.mp4" \
    --load-weights explorations/trained/clip_CONCEPT_DATE/style.pth \
    --resolution 720p --fps 30
```

### 5. Create Exploration Page
Copy `clip_organic_20251011/index.html` as template, update paths and descriptions.

### 6. Document Findings
Note:
- CLIP similarity achieved
- Color palette that emerged
- Visual characteristics (structure, movement, etc.)
- Which architecture performed better
- Audio reactivity quality

---

## 📖 Related Documentation

### Implementation
- **Training Script**: `Code/backend/clip_optimize_cppn.py`
- **CPPN Network**: `Code/backend/cppn.py`
- **CLI**: `Code/backend/cli.py`

### Technical Guides
- **Implementation**: `docs/Phase2-POC/CLIP_GUIDED_CPPN_PRACTICAL.md`
- **Milestone**: `docs/Phase2-POC/MILESTONE_CLIP_TRAINING.md`
- **ML Roadmap**: `docs/Phase2-POC/ML_EXPLORATION_ROADMAP.md`

### Presentation
- **For Leo**: `docs/Phase2-POC/PRESENTATION_FOR_LEO.md`

---

## 🎯 Goals

### Short-term (1 month)
- Create 7-10 distinct mood board styles
- Validate concept space through experimentation
- Document prompt engineering techniques
- Build foundational style library

### Medium-term (2-3 months)
- Expand to 15-20 core styles
- Test ML feature enhancements (OpenL3)
- Explore CLIP model variations
- Build production selection system

### Long-term (6 months)
- Comprehensive style library (30+ styles)
- User-contributed styles
- Advanced features (color control, interpolation)
- Commercial deployment

---

**Updated**: October 11, 2025  
**Status**: ✅ First exploration complete, mood board system validated  
**Next**: Expand style library, test concept variations

🎨 **The beginning of an artistic exploration journey!** 🚀

