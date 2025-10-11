# CPPN Parameter Exploration Guide

**Goal:** Discover interesting visual styles by exploring the untrained network's parameter space.

---

## Quick Start

### Option 1: Automated Exploration (Running Now!)

```bash
python quick_explore.py
```

**What it does:**
1. Cuts audio into 3 varied 10-second segments (quiet, intense, transition)
2. Generates 4 variations per segment (simple, reactive, complex, evolving)
3. Creates an HTML comparison page to view all results side-by-side

**Output:** `explorations/quick_TIMESTAMP/comparison.html`

---

### Option 2: Manual Exploration (Your Own Tests)

```bash
# Test different parameters manually
python cli.py "path/to/audio.mp3" output.mp4 [OPTIONS]
```

---

## Parameter Guide

### 1. **--layers** (Network Depth)
Controls pattern complexity and structure.

```bash
# Simple, flowing patterns
python cli.py audio.mp3 simple.mp4 --layers 3

# Moderate complexity (default)
python cli.py audio.mp4 --layers 4

# Complex geometric structures
python cli.py audio.mp3 complex.mp4 --layers 8
```

**Effect:**
- **2-3 layers:** Simple, smooth, organic shapes
- **4-5 layers:** Balanced complexity
- **6-8 layers:** Complex, intricate patterns
- **8+ layers:** Very detailed but slower

---

### 2. **--hidden-dim** (Network Width)
Controls pattern detail and expressiveness.

```bash
# Minimalist
python cli.py audio.mp3 minimal.mp4 --hidden-dim 128

# Balanced (default)
python cli.py audio.mp3 output.mp4 --hidden-dim 256

# High detail
python cli.py audio.mp3 detailed.mp4 --hidden-dim 512
```

**Effect:**
- **128:** Simple, clean patterns
- **256:** Good balance (recommended)
- **384-512:** More expressive but slower

---

### 3. **--audio-scale** (Audio Reactivity)
How much audio features influence the visuals.

```bash
# Subtle audio influence
python cli.py audio.mp3 subtle.mp4 --audio-scale 0.03

# Default
python cli.py audio.mp3 output.mp4 --audio-scale 0.05

# Strong audio response
python cli.py audio.mp3 reactive.mp4 --audio-scale 0.15

# Extreme (may oversaturate)
python cli.py audio.mp3 extreme.mp4 --audio-scale 0.3
```

**Effect:**
- **0.01-0.03:** Subtle, smooth changes
- **0.05-0.08:** Noticeable reactivity (recommended)
- **0.10-0.20:** Strong, punchy response
- **0.20+:** Extreme, potentially chaotic

---

### 4. **--evolve** (Weight Evolution)
Creates "living math" by slowly changing network weights.

```bash
# Static patterns (default)
python cli.py audio.mp3 static.mp4 --evolve 0.0

# Subtle evolution
python cli.py audio.mp3 living.mp4 --evolve 0.002

# Noticeable drift
python cli.py audio.mp3 evolving.mp4 --evolve 0.005

# Strong evolution
python cli.py audio.mp3 morphing.mp4 --evolve 0.01
```

**Effect:**
- **0.0:** Patterns stay consistent
- **0.001-0.003:** Subtle, organic drift
- **0.005-0.008:** Noticeable evolution
- **0.01+:** Patterns morph significantly

---

## Recommended Presets

### 1. Organic Flow (Smooth & Calm)
```bash
python cli.py audio.mp3 organic.mp4 \
    --layers 4 \
    --hidden-dim 256 \
    --audio-scale 0.05 \
    --evolve 0.0
```
**Best for:** Ambient, calm music

---

### 2. Reactive Geometric (Punchy & Structured)
```bash
python cli.py audio.mp3 geometric.mp4 \
    --layers 6 \
    --hidden-dim 256 \
    --audio-scale 0.12 \
    --evolve 0.0
```
**Best for:** Electronic, rhythmic music

---

### 3. Living Abstract (Evolving & Complex)
```bash
python cli.py audio.mp3 abstract.mp4 \
    --layers 5 \
    --hidden-dim 384 \
    --audio-scale 0.08 \
    --evolve 0.005
```
**Best for:** Experimental, dynamic music

---

### 4. Minimal Reactive (Simple & Clean)
```bash
python cli.py audio.mp3 minimal.mp4 \
    --layers 2 \
    --hidden-dim 128 \
    --audio-scale 0.10 \
    --evolve 0.0
```
**Best for:** Any genre, focuses on pure forms

---

### 5. Maximal Complexity (Rich & Detailed)
```bash
python cli.py audio.mp3 maximal.mp4 \
    --layers 8 \
    --hidden-dim 512 \
    --audio-scale 0.05 \
    --evolve 0.002
```
**Best for:** Complex, layered music (slower to render)

---

## Quick Testing Workflow

### 1. Create Test Segments
Use short clips (10-30 seconds) for fast iteration:

```bash
# Using ffmpeg to cut segments
ffmpeg -i input.mp3 -ss 30 -t 15 segment1.mp3
ffmpeg -i input.mp3 -ss 120 -t 15 segment2.mp3
```

Or use the automated tool:
```bash
python quick_explore.py
```

---

### 2. Test Matrix
Generate a parameter matrix for comparison:

| Parameter | Low | Medium | High |
|-----------|-----|--------|------|
| **Layers** | 3 | 5 | 8 |
| **Dim** | 128 | 256 | 512 |
| **Audio** | 0.03 | 0.08 | 0.15 |
| **Evolve** | 0.0 | 0.005 | 0.01 |

Generate one video per combination to find favorites.

---

### 3. Resolution Options
Start small, then scale up:

```bash
# Fast testing (360p @ 24fps)
python cli.py audio.mp3 test.mp4 --resolution 360p --fps 24

# Preview quality (480p @ 30fps)
python cli.py audio.mp3 preview.mp4 --resolution 480p --fps 30

# Good quality (720p @ 30fps)
python cli.py audio.mp3 output.mp4 --resolution 720p --fps 30

# High quality (1080p @ 60fps) - slower!
python cli.py audio.mp3 hq.mp4 --resolution 1080p --fps 60
```

---

## Pattern Discovery Tips

### 1. Start Simple
Begin with basic parameters and gradually increase complexity:
- Start: `--layers 3 --hidden-dim 128`
- Add complexity: `--layers 5 --hidden-dim 256`
- Push limits: `--layers 8 --hidden-dim 512`

### 2. Vary One Parameter at a Time
Keep other params constant to see specific effects:
```bash
# Test audio scale variations
python cli.py audio.mp3 scale_03.mp4 --audio-scale 0.03
python cli.py audio.mp3 scale_08.mp4 --audio-scale 0.08
python cli.py audio.mp3 scale_15.mp4 --audio-scale 0.15
```

### 3. Test with Different Music Types
- **Quiet/Ambient:** Lower audio-scale (0.03-0.05)
- **Rhythmic/Electronic:** Higher audio-scale (0.10-0.15)
- **Complex/Orchestral:** More layers (6-8)
- **Minimal/Sparse:** Fewer layers (2-3)

### 4. Evolution for Long Tracks
For longer videos, add subtle evolution to keep it interesting:
```bash
python cli.py long_track.mp3 output.mp4 --evolve 0.003
```

---

## Understanding the Results

### What You're Seeing
**Remember:** These are **random patterns** from untrained weights!

- ✅ **Spatial coherence:** Patterns flow naturally
- ✅ **Temporal smoothness:** No flickering
- ✅ **Audio reactivity:** Features modulate output
- ❌ **Artistic intent:** No learned aesthetics
- ❌ **Semantic meaning:** No "understanding" of music

### What to Look For
When evaluating results:

1. **Do patterns complement the music?**
   - Quiet parts → calm visuals
   - Intense parts → dynamic changes

2. **Is complexity appropriate?**
   - Not too busy or too simple
   - Balanced detail level

3. **Does evolution add or detract?**
   - Subtle drift can be nice
   - Too much becomes distracting

4. **Color palette interesting?**
   - Random but sometimes lucky!
   - Every seed different

---

## Advanced Techniques

### 1. Combine Multiple Tracks
Use different parameters for verse/chorus:
```bash
# Verse (subtle)
python cli.py verse.mp3 verse.mp4 --layers 3 --audio-scale 0.03

# Chorus (intense)
python cli.py chorus.mp3 chorus.mp4 --layers 6 --audio-scale 0.12

# Concatenate with video editor
```

### 2. Parameter Interpolation
Gradually change parameters over time (requires custom script).

### 3. Post-Processing
- Color grading (LUTs in video editor)
- Blend modes (overlay on other footage)
- Speed changes (time-remap)

---

## Troubleshooting

### Patterns Too Busy
- **Reduce** `--layers` (try 3-4)
- **Reduce** `--hidden-dim` (try 128-256)

### Patterns Too Simple
- **Increase** `--layers` (try 6-8)
- **Increase** `--hidden-dim` (try 384-512)

### Not Reactive Enough
- **Increase** `--audio-scale` (try 0.10-0.15)

### Too Chaotic
- **Decrease** `--audio-scale` (try 0.03-0.05)
- **Reduce** `--evolve` (try 0.0-0.002)

### Colors Boring
- 🎲 Try different runs (random weights = random colors!)
- No control yet - future feature

---

## Example Session

```bash
# 1. Create exploration directory
mkdir my_exploration
cd my_exploration

# 2. Cut audio segment for testing (30 seconds)
ffmpeg -i ../input.mp3 -ss 60 -t 30 test_segment.mp3

# 3. Generate variations
python ../cli.py test_segment.mp3 simple.mp4 --layers 3 --hidden-dim 128 --resolution 480p
python ../cli.py test_segment.mp3 reactive.mp4 --layers 4 --audio-scale 0.12 --resolution 480p
python ../cli.py test_segment.mp3 complex.mp4 --layers 6 --hidden-dim 384 --resolution 480p
python ../cli.py test_segment.mp3 evolving.mp4 --layers 4 --evolve 0.005 --resolution 480p

# 4. Review and pick favorite
# 5. Render full track with chosen parameters at higher quality
python ../cli.py ../input.mp3 final.mp4 --layers 4 --audio-scale 0.12 --resolution 1080p
```

---

## Automated Exploration Output

The `quick_explore.py` tool is currently generating:

**3 Audio Segments:**
- Quiet/calm section
- Loud/intense section  
- Mid-energy section

**4 Variations Each:**
- Simple (3 layers, basic)
- Reactive (4 layers, strong audio)
- Complex (6 layers, intricate)
- Evolving (4 layers + evolution)

**Total:** 12 short videos + comparison HTML

Check: `explorations/quick_TIMESTAMP/comparison.html`

---

## What's Next?

After exploring parameters:

1. **Document Favorites**
   - Save parameter combinations that work well
   - Note which music types they suit

2. **Create Preset Library**
   - Build a collection of "good" configurations
   - Share with others

3. **Full Renders**
   - Apply best params to full tracks
   - Higher resolution/framerate

4. **Phase B Planning**
   - Decide if parameter exploration is enough
   - Or if training/CLIP guidance needed
   - See `NEXT_STEPS.md` for options

---

**Updated:** 2025-10-11  
**Status:** Exploration tools ready!

