# Backend Exploration Tools

**Purpose:** Tools for exploring CPPN parameter space and discovering interesting visual styles

---

## 🔬 Phase C: Architecture Exploration (NEW!)

**Systematic research into optimal network architectures for organic biological patterns**

See **[ARCHITECTURE_EXPLORATION_README.md](./ARCHITECTURE_EXPLORATION_README.md)** for complete guide.

**Quick Start:**
```bash
# Week 1: Generate test videos (36 configurations)
python explore_architectures.py

# Week 2: Rate visual quality
python rate_architectures.py

# Week 3: Use existing CLIP training on winners
# (See ARCHITECTURE_EXPLORATION_README.md)
```

**Goal:** Discover optimal 2-5 layer architectures for spirals, cells, droplets, fluid forms.

---

## Quick Start

### Automated Exploration (Recommended)

```bash
python quick_explore.py
```

**What it does:**
1. Cuts audio into 3 segments (10 seconds each)
2. Generates 4 CPPN variations per segment
3. Creates comparison HTML to view all results

**Output:** `../explorations/quick_TIMESTAMP/comparison.html`

---

## Available Tools

### `quick_explore.py` - Automated Parameter Exploration

Fast, automated exploration of CPPN parameter space.

**Features:**
- Automatically finds interesting audio segments (quiet, intense, varied)
- Tests 4 preset configurations: simple, reactive, complex, evolving
- Generates side-by-side comparison HTML
- Fast generation (360p @ 24fps)

**Usage:**
```bash
python quick_explore.py
# Looks for audio in ../../docs/Audio/
# Generates 12 videos in ../explorations/quick_TIMESTAMP/
```

**Presets tested:**
- **Simple**: 3 layers, minimal complexity
- **Reactive**: Strong audio response (audio_scale=0.15)
- **Complex**: 6 layers, intricate patterns
- **Evolving**: Living math effect (evolve=0.005)

---

### `explore_parameters.py` - Batch Parameter Testing

Test multiple custom parameter configurations in batch.

**Features:**
- 8 predefined presets (organic, geometric, reactive, minimal, maximal, etc.)
- Generates summary JSON with results
- Configurable resolution and FPS

**Usage:**
```bash
python explore_parameters.py
# Tests all 8 presets on available audio files
# Creates timestamped results directory
```

**Presets:**
- Organic Flow (smooth, calm)
- Geometric (complex structures)
- Reactive Simple (fewer layers, strong audio)
- Deep Subtle (many layers, subtle audio)
- Living Math (with evolution)
- High Contrast (large network + evolution)
- Minimal (simplest possible)
- Maximal (most complex)

---

### `show_video_thumbnails.py` - Thumbnail HTML Generator

Creates HTML pages with video thumbnails instead of embedded players.

**Features:**
- More reliable than embedded video
- Click thumbnails to open in default player
- Download links for each video

**Usage:**
```bash
python show_video_thumbnails.py
# Scans ../explorations/ for video files
# Creates thumbnails.html in each exploration directory
```

**When to use:**
- Embedded videos not playing in browser
- Want easier video navigation
- Prefer external video player

---

### `regenerate_all_html.py` - HTML Regeneration Utility

Regenerates comparison HTML files for all exploration directories.

**Features:**
- Updates with current preset definitions
- Fixes video embedding issues
- Standardized HTML format

**Usage:**
```bash
python regenerate_all_html.py
# Regenerates comparison.html in all exploration directories
```

**When to use:**
- HTML files outdated or broken
- Changed preset definitions
- Need consistent HTML format across all explorations

---

## Documentation

### `PARAMETER_EXPLORATION_GUIDE.md`

Comprehensive guide to CPPN parameter space exploration.

**Contains:**
- Parameter explanations (layers, hidden-dim, audio-scale, evolve)
- Effect descriptions for each parameter
- Recommended presets for different music types
- Quick testing workflow
- Pattern discovery tips
- Troubleshooting guide

**Read this to understand:**
- What each parameter does
- How to create custom configurations
- How to interpret results
- Best practices for exploration

---

### `QUICK_TESTS.md`

Copy/paste commands for manual testing.

**Contains:**
- Fast test commands (360p, short clips)
- Full track render commands
- High quality render commands
- Parameter sweep commands

**Use when:**
- Want to test specific parameter values
- Need quick manual testing
- Creating custom configurations
- Rendering final outputs

---

### `EXPLORATION_SUMMARY.md`

Summary of completed exploration runs.

**Contains:**
- Links to exploration results
- What was tested
- How to review results
- Next steps recommendations

---

## Workflow

### 1. Quick Exploration (Find What Works)

```bash
# Run automated exploration
python quick_explore.py

# Review results
# Open: ../explorations/quick_TIMESTAMP/comparison.html

# Note which parameters work well
```

### 2. Manual Testing (Refine)

```bash
# Copy commands from QUICK_TESTS.md
# Modify parameters based on what worked
# Test on different audio segments
```

### 3. Full Render (Final Output)

```bash
# Use best parameters found
cd ..
python cli.py "audio.mp3" "final.mp4" \
    --resolution 720p \
    --fps 30 \
    --layers 4 \
    --audio-scale 0.12
```

---

## Tips

### For Best Results

1. **Start with quick_explore.py**
   - Fastest way to see variety
   - Good baseline for comparison

2. **Test different music types**
   - Quiet/ambient: lower audio-scale (0.03-0.05)
   - Energetic/electronic: higher audio-scale (0.10-0.15)
   - Complex/layered: more layers (6-8)

3. **Use short clips for iteration**
   - 10-30 seconds ideal for testing
   - Fast feedback loop
   - Save full renders for final parameters

4. **Compare side-by-side**
   - Use comparison HTML
   - Note which works best for each segment
   - Different parameters suit different music

5. **Document findings**
   - Note which parameters work well
   - Save best configurations
   - Build personal preset library

### Understanding Results

**Remember:** CPPN is **untrained** (random weights)
- Patterns are mathematical artifacts
- Every run produces different colors (random initialization)
- You're finding "happy accidents" not learned aesthetics

**What to look for:**
- Complexity appropriate for music?
- Audio reactivity noticeable?
- Evolution adds or distracts?
- Overall aesthetic appeal?

---

## Troubleshooting

### Videos Not Generating
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Use CPU fallback if needed (slower)
python quick_explore.py --device cpu
```

### HTML Videos Not Playing
```bash
# Generate thumbnails instead
python show_video_thumbnails.py

# Or try different browser (Chrome/Firefox)
```

### Out of Memory
- Reduce resolution in quick_explore.py (line 140: `resolution = "360p"`)
- Close other GPU applications
- Use CPU fallback

### Slow Performance
- Ensure CUDA is being used
- Reduce resolution for testing
- Use fewer layers (3-4 instead of 6-8)
- Check GPU isn't thermal throttling

---

## Advanced Usage

### Custom Presets

Edit `quick_explore.py` presets (lines 107-136):

```python
presets = {
    "your_preset": {
        "layers": 4,
        "hidden_dim": 256,
        "audio_scale": 0.08,
        "evolve": 0.0,
        "desc": "Your description"
    }
}
```

### Custom Audio Segments

Cut specific segments with ffmpeg:

```bash
# Cut 15 seconds starting at 2:30
ffmpeg -i audio.mp3 -ss 150 -t 15 segment.mp3

# Then test
cd ..
python cli.py segment.mp3 test.mp4 [params]
```

### Batch Processing

Create a script to test multiple configurations:

```bash
# test_batch.ps1
$configs = @(
    @{layers=3; scale=0.05},
    @{layers=4; scale=0.08},
    @{layers=5; scale=0.12}
)

foreach ($config in $configs) {
    python ../cli.py audio.mp3 "test_L$($config.layers)_S$($config.scale).mp4" `
        --layers $config.layers `
        --audio-scale $config.scale
}
```

---

## Output Structure

Exploration runs create:

```
explorations/quick_TIMESTAMP/
├── comparison.html      # Side-by-side comparison
├── thumbnails.html      # Thumbnail view (if generated)
├── README.md            # Exploration details
├── segments/            # Audio clips used
│   ├── audio_start_10s.wav
│   ├── audio_quiet_10s.wav
│   └── audio_intense_10s.wav
└── [videos]             # Generated videos
    ├── start_simple.mp4
    ├── start_reactive.mp4
    ├── start_complex.mp4
    ├── start_evolving.mp4
    ├── quiet_simple.mp4
    ├── [etc...]
```

---

## See Also

- **Parent README**: `../README.md` - Main backend usage guide
- **Parameter Guide**: `PARAMETER_EXPLORATION_GUIDE.md` - Detailed parameter documentation
- **Quick Tests**: `QUICK_TESTS.md` - Copy/paste test commands
- **AGENTS.md**: `../AGENTS.md` - Architecture and implementation details

---

**Updated:** 2025-10-11  
**Status:** Tools organized and documented




