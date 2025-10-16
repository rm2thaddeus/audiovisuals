# Architecture Exploration Tools - Phase C

**Purpose:** Systematic exploration of CPPN architectures for organic biological patterns

---

## Overview

These tools implement the Phase C research plan to discover optimal CPPN network architectures (2-5 layers × 32-128 hidden dimensions) for generating organic patterns like spirals, cells, droplets, and fluid forms.

---

## Tools

### 1. `explore_architectures.py` - Week 1: Matrix Testing

**Purpose:** Generate test videos for all architecture configurations

**Matrix:**
- Layers: 2, 3, 4, 5
- Hidden dimensions: 32, 64, 128
- Seeds: 3 per configuration
- Total: 36 videos (12 architectures × 3 seeds)

**Usage:**
```bash
# Use default audio (first file in docs/Audio/)
python explore_architectures.py

# Specify audio file
python explore_architectures.py --audio path/to/audio.mp3

# Adjust duration (default: 10s)
python explore_architectures.py --duration 15

# Skip frame extraction (faster)
python explore_architectures.py --skip-frames
```

**Output:**
- Directory: `../explorations/architecture_matrix/YYYYMMDD_HHMMSS/`
- 36 video files (480p @ 24fps for speed)
- 36 representative frames (PNG at t=5s)
- `EXPLORATION_REPORT.md` - Summary report
- `metadata.json` - Detailed configuration data

**Naming Convention:**
```
arch_2L_32D_seed42.mp4
arch_4L_128D_seed123.mp4
```

### 2. `rate_architectures.py` - Week 2: Visual Rating

**Purpose:** Interactive rating tool for visual quality assessment

**Rating Criteria (1-5 scale):**
1. **Organic Quality** - Spirals, cells, fluid forms
2. **Coherence** - Spatial continuity
3. **Audio Reactivity** - Responsiveness to music
4. **Aesthetic Appeal** - Subjective beauty

**Usage:**
```bash
# Rate latest exploration
python rate_architectures.py

# Rate specific exploration
python rate_architectures.py path/to/exploration_dir

# Resume interrupted rating
python rate_architectures.py --resume
```

**Workflow:**
1. Tool opens each video in default player
2. Watch and close player when done
3. Rate on 4 criteria (1-5)
4. Add optional notes
5. Ratings saved incrementally (resume-able)

**Output:**
- `ratings.json` - All ratings and summary
- `../../docs/Phase2-POC/ARCHITECTURE_CATALOG.md` - Visual catalog

---

## Week-by-Week Workflow

### Week 1: Matrix Testing

```bash
cd Code/backend/tools

# Run exploration (36 videos, ~30-60 min depending on hardware)
python explore_architectures.py

# Review generated report
# Open explorations/architecture_matrix/[timestamp]/EXPLORATION_REPORT.md
```

**Expected Time:** 1-2 minutes per video = 36-72 minutes total

### Week 2: Visual Rating

```bash
cd Code/backend/tools

# Run rating tool
python rate_architectures.py

# Follow prompts to rate each video
# Can quit and resume anytime
```

**Expected Time:** 2-3 minutes per video = 72-108 minutes total

**Tips:**
- Watch for organic qualities (spirals, cells, fluid motion)
- Note which architectures feel "biological"
- Compare similar architectures (same layers, different dims)
- Take breaks - ratings saved incrementally

### Week 3: CLIP Training (Existing Tool)

```bash
cd Code/backend

# Train top architecture with organic prompt
python clip_optimize_cppn.py \
  --prompt "organic flowing cellular structures with spiral patterns" \
  --audio "../docs/Audio/sample.mp3" \
  --layers 4 \
  --hidden-dim 128 \
  --output styles/organic/cellular_4L_128D.pth

# Repeat for top 3-5 architectures
```

**Expected Time:** 6-8 minutes per architecture

### Week 4: Documentation & Integration

1. Update `NETWORK_ARCHITECTURE_GUIDE.md` with findings
2. Document winning architectures
3. Create preset recommendations
4. Plan MVP integration

---

## Architecture Presets (cppn.py)

After Week 2-3, the following presets will be available:

```python
from cppn import CPPN, get_preset, list_presets

# List available presets
list_presets()

# Use preset
config = get_preset('small_cellular')
cppn = CPPN(
    num_layers=config['num_layers'],
    hidden_dim=config['hidden_dim']
)

# Or create custom
cppn = CPPN(num_layers=3, hidden_dim=64)
```

**Current Presets:**
- `tiny_organic` - 2L × 64D (fluid forms)
- `small_cellular` - 3L × 64D (cells, bubbles)
- `medium_spiral` - 4L × 128D (spirals, flows)
- `balanced` - 4L × 64D (default organic)
- `baseline` - 4L × 256D (Phase A comparison)

---

## CLI Integration

The main CLI now supports architecture testing:

```bash
cd Code/backend

# Test specific architecture
python cli.py audio.mp3 output.mp4 \
  --layers 3 \
  --hidden-dim 64 \
  --seed 42

# Test with different seeds
python cli.py audio.mp3 output1.mp4 --seed 42
python cli.py audio.mp3 output2.mp4 --seed 123
python cli.py audio.mp3 output3.mp4 --seed 456

# Short duration for testing
python cli.py audio.mp3 output.mp4 --duration 10
```

**New Arguments:**
- `--seed` - Reproducible initialization
- `--duration` - Process only N seconds of audio

---

## Output Structure

```
Code/backend/
├── explorations/
│   └── architecture_matrix/
│       └── YYYYMMDD_HHMMSS/
│           ├── arch_2L_32D_seed42.mp4
│           ├── arch_2L_32D_seed42_frame.png
│           ├── arch_2L_32D_seed123.mp4
│           ├── arch_2L_32D_seed123_frame.png
│           ├── ... (36 videos + 36 frames)
│           ├── EXPLORATION_REPORT.md
│           ├── metadata.json
│           └── ratings.json (after Week 2)
│
├── styles/
│   └── organic/  (after Week 3)
│       ├── cellular_4L_128D.pth
│       ├── spiral_4L_128D.pth
│       └── fluid_2L_64D.pth
│
└── tools/
    ├── explore_architectures.py
    ├── rate_architectures.py
    └── ARCHITECTURE_EXPLORATION_README.md

docs/Phase2-POC/
├── NETWORK_ARCHITECTURE_GUIDE.md
└── ARCHITECTURE_CATALOG.md
```

---

## Expected Outcomes

### Phase C Week 2 Complete:
- [ ] 36 videos generated and cataloged
- [ ] All videos rated on 4 criteria
- [ ] Architecture catalog created with rankings
- [ ] Top 3-5 architectures identified

### Phase C Week 3 Complete:
- [ ] Top architectures trained with CLIP
- [ ] 9+ trained styles created (3 prompts × 3 archs)
- [ ] Random vs CLIP-trained comparison

### Phase C Week 4 Complete:
- [ ] Architecture guide fully documented
- [ ] MVP preset system defined
- [ ] Integration plan finalized

---

## Troubleshooting

### Video Generation Fails

```bash
# Check audio file exists
ls -l ../docs/Audio/

# Test with shorter duration
python explore_architectures.py --duration 5

# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

### Rating Tool Issues

```bash
# Resume interrupted rating
python rate_architectures.py --resume

# Manual video playback
# Open explorations/architecture_matrix/[timestamp]/
# Play videos manually and rate
```

### Storage Space

Each exploration run generates ~1-2 GB of videos. Clean old explorations:

```bash
# Keep only latest 2 explorations
cd explorations/architecture_matrix/
ls -lt | tail -n +3 | awk '{print $9}' | xargs rm -rf
```

---

## Performance Notes

**Video Generation Time (RTX 5070):**
- 2L × 32D: ~30s per 10s clip
- 4L × 128D: ~60s per 10s clip
- 5L × 128D: ~90s per 10s clip

**Total Exploration Time:**
- Matrix generation: 36-72 minutes
- Rating session: 72-108 minutes
- CLIP training: 18-40 minutes (3-5 archs)
- **Total: 2-4 hours spread over 3 weeks**

---

## References

- **Phase C Plan:** `../../docs/Phase2-POC/POC_PLAN.md` (Phase C section)
- **Architecture Guide:** `../../docs/Phase2-POC/NETWORK_ARCHITECTURE_GUIDE.md`
- **CLIP Training:** `../clip_optimize_cppn.py`
- **Baseline Implementation:** `../../docs/Phase2-POC/backend/PHASE_A_IMPLEMENTATION.md`

---

**Created:** 2025-10-13  
**Phase:** C - Network Architecture & Visual Interpretation  
**Status:** Week 1 tools ready, Week 2-4 planned



