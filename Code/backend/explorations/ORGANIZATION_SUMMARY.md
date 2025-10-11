# Exploration Results - Organization Summary

**Date**: 2025-10-11  
**Status**: ✅ Complete - Organized by trained/untrained

---

## New Structure

```
explorations/
├── README.md                      # Main documentation
├── EXPLORATION_SUMMARY.md         # Quick exploration guide
├── PARAMETER_EXPLORATION_GUIDE.md # Parameter reference
│
├── untrained/                     # Random parameter exploration
│   ├── README.md
│   ├── quick_20251011_140932/     # Complete exploration (12 videos)
│   │   ├── comparison.html
│   │   ├── segments/
│   │   └── *.mp4
│   └── quick_20251011_141004/     # Complete exploration (12 videos)
│       ├── comparison.html
│       ├── segments/
│       └── *.mp4
│
└── trained/                       # CLIP-optimized results
    ├── README.md
    └── clip_organic_20251011/     # Architecture comparison
        ├── organic_diffuse_128dim.pth  # Winner (0.2452 similarity)
        ├── organic_diffuse_128dim.png
        ├── organic_diffuse_128dim.json
        ├── organic_diffuse_256dim.pth  # (0.2217 similarity)
        ├── organic_diffuse_256dim.png
        ├── organic_diffuse_256dim.json
        ├── test_128dim.mp4
        ├── test_256dim.mp4
        ├── test_clip_10s.mp3
        └── COMPARISON_RESULTS.md
```

---

## Organization Rationale

### Why Separate Trained/Untrained?

1. **Different Purposes**:
   - **Untrained**: Parameter discovery, "happy accidents"
   - **Trained**: Specific aesthetics, reusable styles

2. **Different Workflows**:
   - **Untrained**: Fast iteration, no training
   - **Trained**: 6-8 min optimization, learned patterns

3. **Different Outputs**:
   - **Untrained**: Random colors, varied results each run
   - **Trained**: Consistent aesthetic, prompt-driven

4. **Easy Navigation**:
   - Clear distinction between exploration types
   - Timestamped subdirectories for history
   - README in each directory explains contents

---

## Quick Access

### Untrained Explorations
```bash
# View comparison pages
open explorations/untrained/quick_20251011_140932/comparison.html
open explorations/untrained/quick_20251011_141004/comparison.html

# Run new exploration
python quick_explore.py
```

### Trained Optimizations
```bash
# Use CLIP-optimized weights (128 dim - winner)
python cli.py audio.mp3 output.mp4 \
    --load-weights explorations/trained/clip_organic_20251011/organic_diffuse_128dim.pth \
    --resolution 720p --fps 30

# Create new CLIP-optimized style
python clip_optimize_cppn.py \
    --prompt "YOUR AESTHETIC" \
    --audio "audio.mp3" \
    --output "explorations/trained/clip_TIMESTAMP/style.pth"
```

---

## Current Status

### Untrained Explorations
- **Total Runs**: 4
- **Complete Runs**: 2 (140932, 141004)
- **Total Videos**: 24 (12 per run)
- **Presets Tested**: simple, reactive, complex, evolving

### Trained Optimizations  
- **Total Runs**: 1 (clip_organic_20251011)
- **Architectures Tested**: 128 dim, 256 dim
- **Winner**: 128 dim (0.2452 CLIP similarity)
- **Prompt**: "organic flowing shapes diffusing into each other with strong contrast"

---

## Documentation

Each subdirectory contains:

- **`README.md`** - Explains purpose and contents
- **Untrained**: Comparison HTML for visual review
- **Trained**: Architecture comparison analysis

Top-level guides:
- **`EXPLORATION_SUMMARY.md`** - Quick start for explorations
- **`PARAMETER_EXPLORATION_GUIDE.md`** - Complete parameter reference

---

## Best Practices

1. **Start Untrained**: Explore parameters first to understand the space
2. **Then Trained**: Once you know what patterns you like, use CLIP to optimize
3. **Keep Timestamped**: Never delete old explorations - disk is cheap!
4. **Document Findings**: Add notes to comparison docs
5. **Reuse Trained Weights**: Apply same style to different audio

---

## Migration Complete ✅

- ✅ All untrained explorations moved to `untrained/`
- ✅ All CLIP-optimized results moved to `trained/clip_organic_20251011/`
- ✅ README files created for each directory
- ✅ Clear separation of trained vs untrained
- ✅ Easy navigation and reuse

---

**Next Steps**: Continue exploring or start optimizing for new aesthetics!

