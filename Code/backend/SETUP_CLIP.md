# Setting Up CLIP-Guided CPPN Optimization

**Goal:** Train your CPPN to generate "organic shapes that diffuse amongst each other, with strong contrast"

**Time:** ~30-60 minutes for setup + 5-15 minutes per optimization run

---

## Step 1: Install Dependencies

```bash
# Make sure you're in the backend directory
cd Code/backend

# Install CLIP
pip install git+https://github.com/openai/CLIP.git

# Install additional dependencies
pip install lpips torchvision pillow
```

**Check installation:**
```bash
python -c "import clip; print('✅ CLIP installed!')"
```

---

## Step 2: Create Styles Directory

```bash
# Create directory for saving optimized weights
mkdir -p styles
```

---

## Step 3: Test Your First Optimization

Let's optimize for your aesthetic: **"organic shapes that diffuse amongst each other, with strong contrast"**

```bash
python clip_optimize_cppn.py \
    --prompt "organic flowing shapes diffusing into each other with strong contrast" \
    --audio "../../docs/Audio/TOOL - The Pot (Audio).mp3" \
    --output "styles/organic_diffuse_contrast.pth" \
    --iterations 300 \
    --resolutions 256 512
```

**What happens:**
1. Loads CLIP model (~1 minute first time, cached after)
2. Initializes your CPPN with random weights
3. Extracts audio features from your track
4. Optimizes at 256×256 for 300 steps (~2-3 minutes)
5. Then optimizes at 512×512 for 300 steps (~3-5 minutes)
6. Saves:
   - `styles/organic_diffuse_contrast.pth` (optimized weights)
   - `styles/organic_diffuse_contrast.png` (preview image)
   - `styles/organic_diffuse_contrast.json` (optimization history)

**Total time:** ~5-10 minutes

---

## Step 4: View the Preview

Open the preview image to see what your CPPN learned:

```bash
# On Windows
start styles/organic_diffuse_contrast.png

# Or navigate to the file in Explorer
```

**What to look for:**
- Do you see organic, flowing shapes?
- Are they diffusing/blending into each other?
- Is there strong contrast?

If not perfect, we'll iterate (see Step 6).

---

## Step 5: Generate a Video

Now use your optimized CPPN to generate an audio-reactive video:

```bash
python cli.py \
    "../../docs/Audio/TOOL - The Pot (Audio).mp3" \
    "test_organic_diffuse.mp4" \
    --load-weights "styles/organic_diffuse_contrast.pth" \
    --resolution 720p \
    --fps 30 \
    --audio-scale 0.08
```

**What happens:**
- Loads your optimized CPPN (not random anymore!)
- Generates video with that aesthetic
- Audio features modulate the patterns
- Result: Audio-reactive organic diffusing shapes!

**Time:** ~1-2 minutes for a short clip

---

## Step 6: Iterate and Refine

### If the result isn't quite right, try:

**A. Adjust the prompt:**
```bash
# More emphasis on contrast
python clip_optimize_cppn.py \
    --prompt "organic liquid shapes flowing together with sharp high contrast boundaries" \
    --output "styles/organic_sharp_contrast.pth"

# More diffusion/blending
python clip_optimize_cppn.py \
    --prompt "soft organic forms melting and blending into each other" \
    --output "styles/organic_soft_blend.pth"

# Different organic style
python clip_optimize_cppn.py \
    --prompt "cellular organic patterns diffusing like watercolor with strong contrast" \
    --output "styles/organic_cellular.pth"
```

**B. Try more iterations:**
```bash
python clip_optimize_cppn.py \
    --prompt "organic flowing shapes diffusing into each other with strong contrast" \
    --output "styles/organic_diffuse_long.pth" \
    --iterations 500  # More optimization steps
```

**C. Add higher resolution:**
```bash
python clip_optimize_cppn.py \
    --prompt "organic flowing shapes diffusing into each other with strong contrast" \
    --output "styles/organic_diffuse_hires.pth" \
    --resolutions 256 512 1024  # Add 1024×1024 stage
```

---

## Prompt Engineering Tips

### For "Organic Shapes"
- ✅ "organic flowing shapes"
- ✅ "cellular organic patterns"
- ✅ "liquid organic forms"
- ✅ "biological structures"
- ❌ Just "organic" (too vague)

### For "Diffusing"
- ✅ "diffusing into each other"
- ✅ "blending together"
- ✅ "melting boundaries"
- ✅ "merging and separating"

### For "Strong Contrast"
- ✅ "strong contrast"
- ✅ "high contrast boundaries"
- ✅ "sharp contrast edges"
- ✅ "bold contrast between forms"

### Complete Prompt Examples
```
"organic flowing shapes diffusing into each other with strong contrast"
"liquid organic forms blending together with high contrast boundaries"
"cellular patterns melting into each other with bold contrast"
"biological structures merging and separating with sharp contrast edges"
"fluid organic shapes with diffuse boundaries and strong contrast"
```

---

## Expected Results Timeline

**First try (300 iterations, 256+512):**
- Similarity score: ~0.25-0.30
- Visual quality: Decent, some artifacts
- Time: ~5-10 minutes

**After refinement (500 iterations, 256+512+1024):**
- Similarity score: ~0.30-0.35
- Visual quality: Much better
- Time: ~10-15 minutes

**Best results:**
- Similarity score: ~0.35+
- Requires: Good prompt + patience + possibly multiple attempts

---

## Troubleshooting

### "CUDA out of memory"
```bash
# Use smaller resolutions
python clip_optimize_cppn.py \
    --prompt "your prompt" \
    --resolutions 256 384  # Smaller than 512
```

### "CLIP model not found"
```bash
# Try a different CLIP model
python clip_optimize_cppn.py \
    --prompt "your prompt" \
    --clip-model "ViT-B/32"  # Smaller, faster
```

### "Preview looks wrong"
- Check the similarity score - should be >0.25
- Try different prompts (see examples above)
- Increase iterations (--iterations 500 or 1000)

### "Video doesn't match preview"
- Make sure you're using `--load-weights` in cli.py
- Check that audio scaling isn't too high (try --audio-scale 0.05)

---

## Quick Reference

**Basic optimization:**
```bash
python clip_optimize_cppn.py \
    --prompt "your description here" \
    --output "styles/my_style.pth"
```

**Generate video with optimized style:**
```bash
python cli.py audio.mp3 output.mp4 \
    --load-weights "styles/my_style.pth"
```

**See all options:**
```bash
python clip_optimize_cppn.py --help
```

---

## Next Steps

Once you have a style you like:

1. **Build a style library:**
   ```
   styles/
   ├── organic_diffuse_contrast.pth   # Your main style
   ├── organic_soft_blend.pth         # Softer version
   ├── organic_sharp.pth              # Sharper version
   └── README.md                      # Document what each does
   ```

2. **Test on different audio:**
   - Calm music: Try with soft blending style
   - Intense music: Try with sharp contrast style

3. **Experiment with prompts:**
   - Abstract: "geometric patterns with flowing lines"
   - Psychedelic: "swirling kaleidoscope patterns"
   - Nature: "fractal tree branches with organic growth"

---

**Ready to start?**

Run this now:
```bash
cd Code/backend
python clip_optimize_cppn.py \
    --prompt "organic flowing shapes diffusing into each other with strong contrast" \
    --output "styles/organic_diffuse_contrast.pth" \
    --iterations 300
```

Then check the preview, generate a video, and let me know how it looks! We'll iterate from there.

