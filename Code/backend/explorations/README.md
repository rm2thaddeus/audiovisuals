# Exploration Results

This directory contains both **untrained** (random parameter exploration) and **trained** (CLIP-optimized) CPPN results.

## Organization

```
explorations/
├── untrained/          # Random weight parameter exploration
│   ├── quick_*/        # Timestamped exploration runs
│   │   ├── comparison.html
│   │   ├── segments/
│   │   └── *.mp4
│
└── trained/            # CLIP-optimized (learned aesthetics)
    └── clip_*/         # Timestamped CLIP optimization runs
        ├── *.pth       # Optimized weights
        ├── *.png       # Preview images
        ├── *.mp4       # Test videos
        └── *.md        # Comparison docs
```

## Untrained vs Trained

### Untrained (`untrained/`)
- **Purpose**: Discover interesting visual styles by exploring random network parameters
- **Method**: Test different layer counts, dimensions, audio scales, evolution rates
- **Output**: "Happy accidents" from random weight initialization
- **Tools**: `quick_explore.py`, `cli.py` with random weights
- **Characteristics**:
  - Colors/patterns are random each run
  - No learned aesthetics
  - Fast to generate (no training needed)
  - Useful for parameter tuning

### Trained (`trained/`)
- **Purpose**: Create specific aesthetics through CLIP-guided optimization
- **Method**: Use CLIP to guide network weights toward a text prompt
- **Output**: Networks learned to generate specific visual styles
- **Tools**: `clip_optimize_cppn.py`
- **Characteristics**:
  - Consistent aesthetic aligned with prompt
  - Learned patterns (not random)
  - Requires training time (~6-8 min per style)
  - Weights can be reused for different audio

## Usage

### Viewing Untrained Results
```bash
# Open comparison page in browser
open explorations/untrained/quick_TIMESTAMP/comparison.html
```

### Using Trained Weights
```bash
# Generate video with CLIP-optimized style
python cli.py audio.mp3 output.mp4 \
    --load-weights explorations/trained/clip_*/[STYLE].pth \
    --resolution 720p --fps 30
```

### Creating New Explorations

**Untrained exploration:**
```bash
python quick_explore.py  # Automated parameter testing
```

**Trained optimization:**
```bash
python clip_optimize_cppn.py \
    --prompt "YOUR AESTHETIC DESCRIPTION" \
    --audio "path/to/audio.mp3" \
    --output "explorations/trained/clip_TIMESTAMP/style.pth"
```

## Best Practices

1. **Untrained first**: Start with parameter exploration to understand the space
2. **Trained second**: Once you know what kind of patterns you like, use CLIP to optimize
3. **Keep timestamped**: Each exploration run is timestamped for easy organization
4. **Document findings**: Add notes to comparison docs about what worked/didn't work

## Current Status

- **Untrained**: 2 exploration runs complete (12 videos each)
- **Trained**: 1 CLIP optimization complete (2 architectures tested)

---

**Updated**: 2025-10-11

