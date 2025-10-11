# Audio Files

This directory contains source audio files for the Audio Feature Explorer project.

## 📁 Contents

### Source Audio Tracks
- **TOOL - The Pot (Audio).mp3** - 6:23, 320 kbps, Progressive rock
- **Zyryab.mp3** - Source audio file

### Phase A Results (Untrained CPPN)
- **phase_a/** - Earlier results with random untrained networks
  - Demonstrates technical pipeline working
  - Random patterns with no aesthetic control
  - Historical reference

---

## 🎨 CLIP-Optimized Results

**🚨 MOVED TO**: `docs/explorations/clip_organic_20251011/`

All CLIP-trained visualization results are now in the explorations directory:

### View Results
```bash
# Open interactive comparison page
docs/explorations/clip_organic_20251011/index.html
```

**What's there**:
- 4 full videos (TOOL & Zyryab, both architectures)
- Interactive HTML viewer with tabs
- Architecture comparison (128 dim vs 256 dim)
- Preview images
- Technical documentation

---

## 📊 Quick Comparison

| Approach | Location | Quality | Status |
|----------|----------|---------|--------|
| **Phase A (Untrained)** | `phase_a/` | Random patterns | Historical |
| **CLIP-Optimized** | `../explorations/clip_organic_20251011/` | Learned aesthetics | ✅ Active |

---

## 🚀 Generate Your Own

### Use CLIP-Optimized Style
```bash
cd ../../Code/backend

python cli.py "../../docs/Audio/YOUR_AUDIO.mp3" output.mp4 \
    --load-weights explorations/trained/clip_organic_20251011/organic_diffuse_128dim.pth \
    --resolution 720p --fps 30
```

### Create New Style
```bash
python clip_optimize_cppn.py \
    --prompt "YOUR AESTHETIC DESCRIPTION" \
    --audio "../../docs/Audio/YOUR_AUDIO.mp3" \
    --output "explorations/trained/clip_NEW/style.pth" \
    --hidden-dim 128
```

---

## 📚 Documentation

- **Explorations**: `../explorations/README.md`
- **CLIP Milestone**: `../Phase2-POC/MILESTONE_CLIP_TRAINING.md`
- **Implementation**: `../Phase2-POC/CLIP_GUIDED_CPPN_PRACTICAL.md`
- **Presentation for Leo**: `../Phase2-POC/PRESENTATION_FOR_LEO.md`

---

**Updated**: October 11, 2025  
**Purpose**: Source audio storage + reference to visualization results  
**Note**: All CLIP results now in `docs/explorations/` for better organization
