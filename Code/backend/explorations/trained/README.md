# Trained (CLIP-Optimized) Results

CLIP-guided CPPN optimization results - networks trained to generate specific aesthetics.

## What This Is

These are **CPPN networks optimized using CLIP** to match text descriptions. Unlike untrained explorations:

- ✅ **Learned aesthetics** - Weights optimized toward specific visual goals
- ✅ **Consistent output** - Same weights produce similar patterns
- ✅ **Prompt-driven** - Controlled by text descriptions
- ✅ **Reusable** - Apply same style to different audio

## How CLIP Optimization Works

```
Text Prompt → CLIP Encoder → Text Features
                                    ↓
                              Similarity Score
                                    ↑
CPPN Output → CLIP Encoder → Image Features
```

The CPPN's weights are adjusted to maximize similarity between generated images and the text prompt.

## Training Details

- **Method**: Gradient descent on CLIP similarity
- **Time**: ~6-8 minutes per style
- **Resolution Pyramid**: 256×256 → 512×512 (coarse to fine)
- **Iterations**: 400-800 per resolution
- **Learning Rate**: 0.001 (Adam optimizer)

## Exploration Runs

Each `clip_TIMESTAMP/` directory contains:

```
clip_organic_20251011/
├── organic_diffuse_128dim.pth    # 128 hidden dim weights
├── organic_diffuse_128dim.png    # Preview image
├── organic_diffuse_128dim.json   # Training history
├── organic_diffuse_256dim.pth    # 256 hidden dim weights
├── organic_diffuse_256dim.png    # Preview image
├── organic_diffuse_256dim.json   # Training history
├── test_128dim.mp4               # 10s test video (128 dim)
├── test_256dim.mp4               # 10s test video (256 dim)
├── test_clip_10s.mp3             # Test audio clip
└── COMPARISON_RESULTS.md         # Architecture comparison
```

## Using Trained Weights

### Generate video with optimized style:
```bash
python cli.py your_audio.mp3 output.mp4 \
    --load-weights explorations/trained/clip_*/[STYLE].pth \
    --resolution 720p --fps 30 --audio-scale 0.10
```

The CLI automatically loads the correct architecture from the checkpoint metadata!

## Architecture Comparison

We test multiple architectures to find which optimizes best:

| Architecture | Parameters | CLIP Score | Visual Quality |
|--------------|-----------|------------|----------------|
| 128 hidden dim | 51K | 0.2452 | ⭐ Winner |
| 256 hidden dim | 201K | 0.2217 | Good |

**Key Finding**: Simpler networks (128 dim) can optimize better for specific aesthetics!

## Best Practices

1. **Start with clear prompts** - Be specific about visual goals
2. **Test multiple architectures** - Different sizes optimize differently
3. **Use audio scale 0.08-0.12** - Works well with CLIP-optimized weights
4. **Monitor similarity scores** - Target >0.24 for good results
5. **Compare previews** - Visual check before full renders

## Creating New Optimizations

```bash
python clip_optimize_cppn.py \
    --prompt "organic flowing shapes with strong contrast" \
    --audio "path/to/audio.mp3" \
    --output "explorations/trained/clip_TIMESTAMP/mystyle.pth" \
    --hidden-dim 128 \
    --iterations 400 \
    --resolutions 256 512
```

## When to Use Trained vs Untrained

### Use Trained (CLIP) When:
- You have a specific aesthetic in mind
- You want consistent results across different audio
- You need semantic control ("organic", "geometric", etc.)
- You're willing to wait 6-8 min for training

### Use Untrained When:
- You want variety and surprise
- You need instant results
- You're exploring parameter space
- You like "happy accidents"

## Evaluation Metrics

- **CLIP Similarity** - How well output matches prompt (target >0.24)
- **Visual Inspection** - Does it look like the prompt?
- **Audio Reactivity** - Does it respond to music nicely?
- **Temporal Coherence** - Smooth transitions, no flickering?

---

**Purpose**: Create specific, reusable visual styles through learned optimization

