# Quick Start: Your "Organic Diffusing Shapes" CPPN

**Your Goal:** Organic shapes that diffuse amongst each other, with strong contrast

**Time:** ~15-20 minutes total (10 min optimization + 2-3 min video)

---

## Step 1: Install CLIP (One-Time, ~2-3 minutes)

Open PowerShell in `Code/backend/`:

```powershell
# Install CLIP
pip install git+https://github.com/openai/CLIP.git

# Install supporting libraries
pip install lpips torchvision pillow

# Verify installation
python -c "import clip; print('✅ CLIP ready!')"
```

---

## Step 2: Create Styles Directory

```powershell
mkdir styles
```

---

## Step 3: Optimize Your CPPN (~5-10 minutes)

This is where the magic happens - CLIP trains your CPPN to generate your aesthetic!

```powershell
python clip_optimize_cppn.py `
    --prompt "organic flowing shapes diffusing into each other with strong contrast" `
    --audio "../../docs/Audio/TOOL - The Pot (Audio).mp3" `
    --output "styles/organic_diffuse_contrast.pth" `
    --iterations 300 `
    --resolutions 256 512
```

**What you'll see:**
```
============================================================
CLIP-Guided CPPN Optimization
============================================================
Prompt: 'organic flowing shapes diffusing into each other with strong contrast'
Device: cuda
CLIP Model: RN50
Resolution pyramid: [256, 512]
Iterations per resolution: 300

Loading CLIP model...
Initializing CPPN...
Extracting audio features from: ../../docs/Audio/TOOL - The Pot (Audio).mp3
Audio features shape: torch.Size([9])
Representative time: 97.15s

Encoding text prompt with CLIP...

============================================================
Resolution 1/2: 256×256
============================================================
  Iter    0/300 | Similarity: 0.2134 | Best: 0.2134
  Iter   20/300 | Similarity: 0.2456 | Best: 0.2589
  Iter   40/300 | Similarity: 0.2701 | Best: 0.2701
  ...
  Iter  299/300 | Similarity: 0.2989 | Best: 0.3021
  Resolution 256×256 complete!
  Best similarity at this resolution: 0.3021

============================================================
Resolution 2/2: 512×512
============================================================
  Iter    0/300 | Similarity: 0.3012 | Best: 0.3021
  Iter   20/300 | Similarity: 0.3145 | Best: 0.3201
  ...
  Iter  299/300 | Similarity: 0.3267 | Best: 0.3289
  Resolution 512×512 complete!
  Best similarity at this resolution: 0.3289

============================================================
Optimization Complete!
============================================================
Best similarity: 0.3289
Saved to: styles/organic_diffuse_contrast.pth
History saved to: styles/organic_diffuse_contrast.json

Preview saved to: styles/organic_diffuse_contrast.png

✅ Success! Your CPPN is now optimized for:
   'organic flowing shapes diffusing into each other with strong contrast'

📁 Files created:
   Weights: styles/organic_diffuse_contrast.pth
   Preview: styles/organic_diffuse_contrast.png
   History: styles/organic_diffuse_contrast.json

🎨 Next step: Generate a video!
   python cli.py ../../docs/Audio/TOOL - The Pot (Audio).mp3 output.mp4 --load-weights styles/organic_diffuse_contrast.pth
```

**⏱️ Total time: ~5-10 minutes**

---

## Step 4: Check the Preview

```powershell
# Open the preview image
start styles/organic_diffuse_contrast.png
```

**What to look for:**
- ✅ Do you see organic, flowing shapes?
- ✅ Are they diffusing/blending into each other?
- ✅ Is there strong contrast between forms?

If it looks good, proceed! If not, we'll iterate (see Step 6).

---

## Step 5: Generate Your Video (~2-3 minutes)

Now use your trained CPPN for an audio-reactive video:

```powershell
python cli.py `
    "../../docs/Audio/TOOL - The Pot (Audio).mp3" `
    "organic_diffuse_test.mp4" `
    --load-weights "styles/organic_diffuse_contrast.pth" `
    --resolution 720p `
    --fps 30 `
    --audio-scale 0.08
```

**What you'll see:**
```
============================================================
Audio Feature Explorer - CPPN Visualizer
Neural evolution beyond MilkDrop presets
============================================================

[OK] CUDA available: NVIDIA GeForce RTX 5070 Laptop GPU

Configuration:
  Input:        ../../docs/Audio/TOOL - The Pot (Audio).mp3
  Output:       organic_diffuse_test.mp4
  Resolution:   1280×720
  FPS:          30
  Device:       cuda

  CPPN:
    Layers:     4
    Hidden dim: 256
    Evolve:     0.0
    Parameters: 201,897

  Processing:
    Batch size: 5000000 pixels (auto-optimized)

Step 1/4: Analyzing audio...
[OK] Audio analyzed: 11638 frames
  Audio features scaled by 0.08 to prevent saturation

Step 2/4: Initializing CPPN...
[INFO] Loading CLIP-optimized weights from: styles/organic_diffuse_contrast.pth
[INFO] Optimized for prompt: 'organic flowing shapes diffusing into each other with strong contrast'
[INFO] CLIP similarity score: 0.3289
[OK] Using CLIP-optimized CPPN (not random initialization!)

Step 3/4: Rendering frames...
  Progress: 100% [11638/11638 frames] | 52.3 FPS | ETA: 0s

Step 4/4: Encoding video...
  Writing video...
  Muxing audio...

============================================================
Generation Complete!
============================================================
Output: organic_diffuse_test.mp4
Duration: 6.5 minutes
Render time: ~3.7 minutes
```

**🎉 Your first CLIP-guided audio-reactive video is ready!**

Open it:
```powershell
start organic_diffuse_test.mp4
```

---

## Step 6: Iterate If Needed

### If you want more contrast:
```powershell
python clip_optimize_cppn.py `
    --prompt "organic liquid shapes flowing together with sharp high contrast boundaries" `
    --output "styles/organic_sharp_contrast.pth" `
    --iterations 400
```

### If you want softer diffusion:
```powershell
python clip_optimize_cppn.py `
    --prompt "soft organic forms melting and blending into each other like watercolor" `
    --output "styles/organic_soft_blend.pth" `
    --iterations 400
```

### If you want cellular/biological look:
```powershell
python clip_optimize_cppn.py `
    --prompt "cellular organic patterns diffusing like cells under microscope with strong contrast" `
    --output "styles/organic_cellular.pth" `
    --iterations 400
```

Then generate videos with each:
```powershell
python cli.py audio.mp3 sharp_contrast.mp4 --load-weights styles/organic_sharp_contrast.pth
python cli.py audio.mp3 soft_blend.mp4 --load-weights styles/organic_soft_blend.pth
python cli.py audio.mp3 cellular.mp4 --load-weights styles/organic_cellular.pth
```

---

## Understanding the Similarity Score

**What the score means:**
- **0.20-0.25**: Barely matching prompt (needs more iterations)
- **0.25-0.30**: Decent match (usable)
- **0.30-0.35**: Good match ✅ (what we're aiming for)
- **0.35+**: Excellent match (rare with CPPNs, but possible!)

**Your goal: ≥0.30**

If you get <0.28, try:
- More iterations (--iterations 500)
- Add higher resolution (--resolutions 256 512 1024)
- Refine your prompt

---

## Quick Reference

**Optimize a new style:**
```powershell
python clip_optimize_cppn.py --prompt "your description" --output "styles/my_style.pth"
```

**Generate video with that style:**
```powershell
python cli.py audio.mp3 output.mp4 --load-weights "styles/my_style.pth"
```

**See optimization progress:**
```powershell
# Opens JSON with similarity history
code styles/organic_diffuse_contrast.json
```

---

## What's Next?

Once you have a style you love:

1. **Test on different music** - Does it work for calm vs intense tracks?
2. **Build a style library** - Create 3-5 variations you can reuse
3. **Experiment with prompts** - Try abstract, geometric, psychedelic styles
4. **Share your results** - Show me what you create!

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'clip'"
```powershell
pip install git+https://github.com/openai/CLIP.git
```

### "CUDA out of memory"
```powershell
# Use smaller resolution
python clip_optimize_cppn.py --prompt "..." --resolutions 256 384
```

### "Preview looks nothing like my description"
- Check similarity score (should be >0.25)
- Try more iterations (--iterations 500)
- Refine prompt (be more specific)

### "Video doesn't match preview"
- Check you're using `--load-weights`
- Try lower `--audio-scale` (0.05 instead of 0.08)

---

**Ready? Run this now:**

```powershell
cd Code/backend
pip install git+https://github.com/openai/CLIP.git lpips torchvision pillow
mkdir styles
python clip_optimize_cppn.py `
    --prompt "organic flowing shapes diffusing into each other with strong contrast" `
    --output "styles/organic_diffuse_contrast.pth"
```

Then show me the preview and we'll iterate from there! 🎨

