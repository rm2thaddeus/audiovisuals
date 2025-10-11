# CLIP-Guided CPPN - Practical Implementation Guide

**Date:** 2025-10-11  
**Purpose:** Concrete explanation of how CLIP-guided CPPN would work with your audio-reactive system

---

## How It Works in Practice

### The Basic Concept

**Short version:** It's a text-or-image-guided art machine that mutates a tiny coordinate-based neural net until CLIP says "yeah, that looks like your prompt." You don't "eat" it; you poke it, measure it, and judge whether it's making cool, prompt-faithful visuals without taking a geological era per frame.

**Technical version:**
- **CPPN**: A small neural net that takes pixel coordinates `(x, y[, t])` and outputs RGB. Because of its activation stew (sin, gaussian, etc.), it loves symmetry, repetition, and organic motifs. Classic idea from Stanley, 2007.
- **CLIP-guided**: Optimize the CPPN's weights so the rendered image scores high under CLIP for a text prompt or reference image. This is "synthesis through optimization"—the same trick behind CLIPDraw and VQGAN+CLIP.

**The Process:**
```
Text Prompt: "flowing organic blue patterns"
        ↓
    CLIP encodes text → feature vector
        ↓
    Optimize CPPN weights so that:
    CLIP(generated_image) ≈ CLIP(text_prompt)
        ↓
    Result: Beautiful patterns matching description
```

**Note:** No extra training required—just gradient descent with CLIP as the judge.

---

## Real-World Example Projects

While there aren't many **CPPN+CLIP** projects specifically, there are several successful CLIP-guided generation projects that demonstrate the technique:

### 1. **VQGAN+CLIP** (Most Popular Example)

**What it does:**
- Uses CLIP to guide VQGAN (Vector Quantized GAN) to generate images from text
- Started the "AI art" revolution in 2021
- Creates stunning, surreal images from prompts

**How it works:**
```python
# Simplified VQGAN+CLIP loop
for iteration in range(max_iterations):
    # Generate image from latent codes
    generated_image = vqgan.decode(latent_codes)
    
    # Compare with text prompt using CLIP
    image_features = clip.encode_image(generated_image)
    text_features = clip.encode_text(prompt)
    
    # Loss: how different are they?
    loss = -cosine_similarity(image_features, text_features)
    
    # Optimize latent codes to reduce loss
    loss.backward()
    optimizer.step()
```

**Famous Examples:**
- "A painting of a fox in the style of Starry Night"
- "Cyberpunk cityscape at sunset"
- Created viral AI art movement

**GitHub:** Search "VQGAN+CLIP" - many implementations available

---

### 2. **CLIP-Guided Diffusion** (OpenAI)

**What it does:**
- Uses CLIP to guide diffusion models
- Higher quality than VQGAN+CLIP
- Slower but more photorealistic

**GitHub:** `openai/guided-diffusion`

---

### 3. **CLIPDraw** (Simpler Example)

**What it does:**
- Uses CLIP to guide generation of vector drawings
- Creates SVG paths that match text descriptions
- Great example of CLIP-guided optimization

**How it works:**
```python
# Initialize random strokes
strokes = random_svg_paths()

for step in range(optimization_steps):
    # Render SVG to image
    image = render(strokes)
    
    # Get CLIP similarity with text
    similarity = clip_similarity(image, text_prompt)
    
    # Optimize stroke parameters
    loss = -similarity
    loss.backward()
    strokes = strokes - learning_rate * strokes.grad
```

**GitHub:** `kvfrans/clipdraw`

---

## How This Would Work With Your CPPN

### Your Current System

```python
# Current: Random weights, crude audio reactivity
cppn = CPPN(input_dim=12, hidden_dim=256, layers=4)
# Random initialization
nn.init.xavier_uniform_(cppn.weight, gain=5.0)

# Generate frame
coords = generate_coordinates(resolution)
audio_features = extract_fft(audio, frame_time)
rgb = cppn(coords, audio_features)  # Random patterns
```

**Problem:** Random patterns, no aesthetic control

---

### CLIP-Guided Version

```python
import torch
import clip

# Load CLIP model
clip_model, preprocess = clip.load("ViT-B/32", device="cuda")

# Initialize CPPN
cppn = CPPN(input_dim=12, hidden_dim=256, layers=4)

# Text prompt for style
prompt = "flowing organic patterns with vibrant colors"
text_features = clip_model.encode_text(clip.tokenize(prompt).to("cuda"))

# Optimization loop (run once per video or per style)
optimizer = torch.optim.Adam(cppn.parameters(), lr=0.001)

print("Optimizing CPPN to match style description...")
for iteration in range(200):  # ~1-5 minutes on GPU
    # Generate a frame
    coords = generate_coordinates((256, 256))  # Smaller for speed
    audio_features = extract_fft(audio, frame_time=0)  # Use representative audio
    
    # Generate image
    rgb = cppn(coords, audio_features)
    image = rgb.reshape(256, 256, 3)
    
    # Preprocess for CLIP
    clip_image = preprocess(PIL.Image.fromarray(image)).unsqueeze(0).to("cuda")
    
    # Get CLIP features
    image_features = clip_model.encode_image(clip_image)
    
    # Loss: maximize similarity to text prompt
    similarity = torch.cosine_similarity(image_features, text_features)
    loss = -similarity  # Negative because we want to maximize
    
    # Optimize CPPN weights
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    if iteration % 50 == 0:
        print(f"Iteration {iteration}, Similarity: {similarity.item():.4f}")

# Save optimized weights
torch.save(cppn.state_dict(), "cppn_optimized_organic_flow.pth")

# Now use optimized CPPN for full video generation
print("Generating video with optimized CPPN...")
for frame_idx in range(num_frames):
    audio_features = extract_fft(audio, frame_time=frame_idx/fps)
    rgb = cppn(coords, audio_features)  # Now generates "organic flow" patterns!
    frames.append(rgb)
```

---

## Advantages Over Random Initialization

### Before CLIP Guidance (Current)
```
Audio Input → Random CPPN → Random patterns that happen to look OK
```
- ❌ No aesthetic control
- ❌ Every run completely different
- ❌ No way to ask for specific styles
- ✅ Fast (no optimization needed)

### After CLIP Guidance
```
Text Prompt → CLIP optimizes CPPN → Beautiful patterns matching description
Audio Input → Optimized CPPN → Audio-reactive version of desired style
```
- ✅ Aesthetic control via text prompts
- ✅ Consistent style across runs
- ✅ Can specify styles: "cyberpunk", "organic", "geometric", etc.
- ✅ Still fast after optimization (1-5 min one-time cost)

---

## Critical Implementation Details

### Coordinate Scaling is Everything

**The most important trick:**
```python
# BAD: Coordinates in [0, 1] or [-1, 1]
x = torch.linspace(0, 1, width)  # Sin/cos see ~0.3 radians of range → boring

# GOOD: Map to [-π, π] or similar
x = torch.linspace(-np.pi, np.pi, width)  # Full sinusoidal range → rich patterns
```

Map `(x, y)` to `[-π, π]` so sinusoidal activations do useful work instead of producing giant flat fields.

### Multi-Resolution Pyramid

**Start low-res, then upsample:**
```python
# Phase 1: 256² for 100 steps (fast, establishes composition)
optimize(resolution=256, steps=100)

# Phase 2: Upsample to 512² and continue
optimize(resolution=512, steps=200)

# Optional Phase 3: 1024² for final detail
optimize(resolution=1024, steps=200)
```

This pyramid trick stabilizes early composition and prevents the CPPN from getting stuck in local minima.

### Avoid CLIP Gaming

**Use different CLIP models for optimization vs evaluation:**
```python
# Optimize with one CLIP variant
optimize_clip = clip.load("RN50")

# Evaluate with a different one
eval_clip = clip.load("ViT-B/32")
```

If the score collapses across backbones, you've overfit the judge (CLIP gaming).

### Audio-Reactive Extension

**Feed time + audio features as extra inputs:**
```python
# Your current CPPN: (x, y, audio_features) → RGB
# Enhanced: (x, y, t, tempo, spectral_centroid, chroma_pca) → RGB

def cppn_forward(coords, time, audio_features):
    # coords: (N, 2)  # x, y
    # time: (N, 1)    # t ∈ [0, 1]
    # audio_features: (N, K)  # smoothed audio features
    
    inputs = torch.cat([coords, time, audio_features], dim=-1)
    return network(inputs)
```

**Evaluate temporal coherence** with SSIM between consecutive frames. If it looks like a disco migraine, your temporal smoothing is too weak.

---

## Practical Implementation for Your Project

### Step 1: Install CLIP

```bash
pip install git+https://github.com/openai/CLIP.git
pip install lpips  # For diversity evaluation
```

### Step 2: Create CLIP Optimization Script

```python
# Code/backend/clip_optimize_cppn.py

import torch
import clip
from cppn import CPPN
from audio_analyzer import AudioAnalyzer
import numpy as np
from PIL import Image

def optimize_cppn_with_clip(
    prompt: str,
    audio_file: str,
    iterations: int = 200,
    resolution: tuple = (256, 256),
    output_path: str = "optimized_cppn.pth"
):
    """
    Optimize CPPN weights to match a text description using CLIP.
    
    Args:
        prompt: Text description of desired style
        audio_file: Path to audio for representative features
        iterations: Number of optimization steps
        resolution: Image resolution for optimization
        output_path: Where to save optimized weights
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load CLIP
    print("Loading CLIP model...")
    clip_model, preprocess = clip.load("ViT-B/32", device=device)
    
    # Initialize CPPN
    print("Initializing CPPN...")
    cppn = CPPN(input_dim=12, hidden_dim=256, num_layers=4).to(device)
    
    # Extract representative audio features
    print("Extracting audio features...")
    analyzer = AudioAnalyzer(audio_file)
    audio_features = analyzer.get_features(frame_time=10.0)  # Use 10s mark
    audio_tensor = torch.tensor(audio_features, dtype=torch.float32).to(device)
    
    # Encode text prompt
    text_tokens = clip.tokenize([prompt]).to(device)
    with torch.no_grad():
        text_features = clip_model.encode_text(text_tokens)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    
    # Generate coordinate grid (CRITICAL: Scale to [-π, π] for sinusoidal activations)
    x = torch.linspace(-np.pi, np.pi, resolution[0], device=device)
    y = torch.linspace(-np.pi, np.pi, resolution[1], device=device)
    X, Y = torch.meshgrid(x, y, indexing='ij')
    coords = torch.stack([X.flatten(), Y.flatten()], dim=-1)
    
    # Optimizer
    optimizer = torch.optim.Adam(cppn.parameters(), lr=0.001)
    
    # Optimization loop
    print(f"Optimizing CPPN for prompt: '{prompt}'")
    best_similarity = -1
    best_state = None
    
    for iteration in range(iterations):
        optimizer.zero_grad()
        
        # Generate image
        rgb = cppn(coords, audio_tensor)
        image = rgb.reshape(resolution[0], resolution[1], 3)
        
        # Convert to PIL Image and preprocess for CLIP
        image_np = (image.detach().cpu().numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(image_np)
        clip_image = preprocess(pil_image).unsqueeze(0).to(device)
        
        # Get CLIP image features
        image_features = clip_model.encode_image(clip_image)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        # Compute similarity
        similarity = (image_features * text_features).sum()
        loss = -similarity  # Maximize similarity = minimize negative
        
        # Backprop
        loss.backward()
        optimizer.step()
        
        # Track best
        if similarity.item() > best_similarity:
            best_similarity = similarity.item()
            best_state = cppn.state_dict().copy()
        
        if iteration % 20 == 0:
            print(f"Iteration {iteration:3d} | Similarity: {similarity.item():.4f}")
    
    # Save best weights
    torch.save(best_state, output_path)
    print(f"\nOptimization complete!")
    print(f"Best similarity: {best_similarity:.4f}")
    print(f"Saved to: {output_path}")
    
    return output_path


if __name__ == "__main__":
    # Example usage
    optimize_cppn_with_clip(
        prompt="flowing organic patterns with vibrant blue and purple colors",
        audio_file="../../docs/Audio/TOOL - The Pot (Audio).mp3",
        iterations=200,
        output_path="cppn_organic_flow.pth"
    )
```

### Step 3: Use Optimized CPPN in CLI

```python
# Modify cli.py to support loading optimized weights

# Add argument
parser.add_argument(
    '--load-weights',
    type=str,
    default=None,
    help='Path to CLIP-optimized CPPN weights'
)

# In main():
if args.load_weights:
    print(f"Loading optimized weights from {args.load_weights}")
    cppn.load_state_dict(torch.load(args.load_weights))
    print("Using CLIP-optimized CPPN!")
```

### Step 4: Generate Videos with Style

```bash
# First: Optimize CPPN for a style
python clip_optimize_cppn.py

# Then: Generate video using optimized weights
python cli.py input.mp3 output.mp4 \
    --load-weights cppn_organic_flow.pth \
    --resolution 720p \
    --fps 30

# Different styles:
python clip_optimize_cppn.py --prompt "geometric cyberpunk neon patterns"
python cli.py input.mp3 cyberpunk.mp4 --load-weights cppn_cyberpunk.pth

python clip_optimize_cppn.py --prompt "soft pastel watercolor abstract"
python cli.py input.mp3 pastel.mp4 --load-weights cppn_pastel.pth
```

---

## Expected Results

### Without CLIP Guidance (Current)
- Random colors and patterns
- No control over aesthetic
- Different every time

### With CLIP Guidance
- **Prompt:** "flowing organic blue patterns"
  - Result: Smooth, flowing shapes in blue/cyan/teal palette
  
- **Prompt:** "geometric cyberpunk neon"
  - Result: Angular, glitchy patterns in pink/blue neon
  
- **Prompt:** "soft pastel watercolor abstract"
  - Result: Gentle, blurred forms in soft pink/lavender/cream

---

## Workflow

### One-Time Setup (per style)
```bash
# 1-5 minutes per style
python clip_optimize_cppn.py --prompt "your description" --output style1.pth
python clip_optimize_cppn.py --prompt "another style" --output style2.pth
python clip_optimize_cppn.py --prompt "third style" --output style3.pth
```

### Video Generation (fast)
```bash
# Use any optimized style
python cli.py audio.mp3 video1.mp4 --load-weights style1.pth  # Fast!
python cli.py audio.mp3 video2.mp4 --load-weights style2.pth  # Fast!
python cli.py audio.mp3 video3.mp4 --load-weights style3.pth  # Fast!
```

### Build Style Library
```
Code/backend/styles/
├── organic_flow.pth          # "flowing organic patterns"
├── cyberpunk_neon.pth        # "geometric cyberpunk neon"
├── pastel_watercolor.pth     # "soft pastel watercolor"
├── cosmic_space.pth          # "cosmic nebula space"
├── glitch_art.pth            # "glitch art digital corruption"
└── README.md                 # Descriptions of each style
```

---

## Pros & Cons

### ✅ Advantages
1. **Text-based control** - "Make it more organic" → adjust prompt
2. **Consistent results** - Same weights = same style
3. **Fast after optimization** - One-time cost per style
4. **No dataset needed** - CLIP already trained
5. **Maintains audio reactivity** - Still uses audio features
6. **Build style library** - Reuse across projects

### ⚠️ Considerations
1. **Optimization time** - 1-5 min per style (one-time)
2. **Quality depends on prompt** - Need good text descriptions
3. **CLIP bias** - May favor photorealistic over abstract
4. **Memory usage** - CLIP + CPPN both on GPU

---

## Next Steps to Implement

### Week 1: Basic Integration
1. Install CLIP: `pip install git+https://github.com/openai/CLIP.git`
2. Create `clip_optimize_cppn.py` script (see above)
3. Test with simple prompt: "colorful abstract patterns"
4. Modify `cli.py` to load optimized weights

### Week 2: Refinement
1. Test multiple prompts (10-15 different styles)
2. Tune optimization parameters (iterations, learning rate)
3. Create style library
4. Document best prompts

### Week 3: Integration
1. Add CLI arguments for style selection
2. Create preset system
3. User testing
4. Documentation

---

## Evaluation: How to Know It's Working

You're not judging photorealism. You're judging: **does it follow the prompt; does it generate rich, coherent structure; is it fast; and does it avoid CLIP-gaming artifacts.**

### A. Faithfulness to Prompt

**Quantitative:**
- **Held-out CLIP score**: Use a *different* CLIP checkpoint for evaluation (e.g., optimize with RN50, evaluate with ViT-B/32)
- **Baseline comparison**: Compare against CLIPDraw and VQGAN+CLIP on the same prompts

**Qualitative:**
- **Human rating**: 1–5 scale for prompt match and legibility
- **Target**: Median ≥3.5/5 across 40-50 test prompts

### B. Visual Quality and Diversity

**Texture/Structure Richness:**
- CPPNs should excel at global regularities and symmetry
- Score diversity with LPIPS between different seeds

**Mode Variety:**
- Run 10 seeds per prompt
- Report mean pairwise LPIPS
- **Target**: LPIPS ≥0.25 for non-abstract prompts
- If everything collapses to the same spiral-vines aesthetic, your regularizers are too narrow

### C. Speed and Stability

**Throughput:**
- Seconds to convergence at 512×512 to reach target CLIP score
- **Target**: 95% of best score within 250–500 steps on consumer GPU

**Temporal Stability (for audio-reactive):**
- Measure SSIM between consecutive frames
- Check for flicker by jittering time `t`

### D. Robustness and Honesty

**Adversarial Artifact Check:**
- Test prompts known to bait CLIP into shortcuts (single token, text-in-image)
- Visual inspection for weird "watermarks" or text-like scratches
- **Target**: No obvious CLIP-gaming artifacts dominating gradients

### Minimal Benchmark You Can Run This Week

**1. Prompt Set:**
- 40 text prompts: 20 concrete ("red fox on snow"), 10 stylistic ("cyberpunk"), 10 abstract
- 10 image prompts (if image-guided mode supported)

**2. Baselines:**
- CLIPDraw (vector-stroke synthesis)
- VQGAN+CLIP (pixel-space baseline)

**3. Metrics:**
- Held-out CLIP score
- Human ratings (1-5 scale)
- LPIPS diversity (mean pairwise between seeds)
- Time-to-target
- Memory usage

**4. Key Ablations:**
- **Parameterization**: sin vs gaussian vs mixed activations; depth/width
- **Optimization**: Adam vs evolutionary (CPPNs historically pair well with CMA-ES)
- **Regularizers**: Total variation, Fourier penalties, random cutout augmentations

### Pass/Fail Criteria

**Your implementation is solid if:**
- ✅ Prompt match: Human rating ≥3.5/5 median, within 10% of VQGAN+CLIP on held-out CLIP score
- ✅ Speed: Reach 95% of best score within 250–500 steps at 512² on single consumer GPU
- ✅ Diversity: Mean LPIPS between seeds ≥0.25 for non-abstract prompts
- ✅ Robustness: No obvious text-like scratches, false "watermarks," or adversarial speckle

---

## Resources

**Papers:**
- **CLIP**: "Learning Transferable Visual Models From Natural Language Supervision" (OpenAI, 2021)
- **CPPNs**: Stanley, 2007 - "Compositional Pattern Producing Networks" ([Gwern](https://gwern.net/doc/ai/nn/fully-connected/2007-stanley.pdf))
- **CLIPDraw**: "Exploring Text-to-Drawing Synthesis through Language-Image Encoders" ([arXiv:2106.14843](https://arxiv.org/abs/2106.14843))
- **VQGAN+CLIP**: "Open Domain Image Generation and Editing" ([arXiv:2204.08583](https://arxiv.org/abs/2204.08583))

**Code Examples:**
- **OpenAI CLIP**: `https://github.com/openai/CLIP`
- **VQGAN+CLIP**: Search GitHub for many implementations
- **CLIPDraw**: `https://github.com/kvfrans/clipdraw`
- **Simple CPPN**: `https://github.com/hardmaru/cppn-tensorflow` (TensorFlow toy implementation)

**Evaluation Resources:**
- **CLIP gaming artifacts**: "Red Teaming Deep Neural Networks" ([NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/febe5c5c6973f713cc43bf0f7c90edbe-Paper-Conference.pdf))
- **Interpretability benchmarks**: Stephen Casper's work on benchmarking CLIP

**Community:**
- r/MediaSynthesis - AI art community
- Disco Diffusion - Popular CLIP-guided art tool
- Midjourney/DALL-E - Commercial applications of similar techniques

---

## TL;DR Rubric

**Setup:**
- 50 prompts (40 text, 10 image)
- 10 seeds per prompt
- 500 steps at 512²

**Report:**
- Held-out CLIP score (different model than optimization)
- Human ratings (1-5 scale)
- LPIPS diversity
- Time-to-target
- VRAM usage
- Artifact check gallery

**Baselines:**
- CLIPDraw (clearer shapes)
- VQGAN+CLIP (pixel-space comparison)

**Pass Criteria:**
- Prompt match near baselines
- Faster or comparable time-to-target
- Better symmetry/texture variety (CPPN advantage)
- No CLIP-gaming artifacts

Now you can evaluate your artsy coordinate gremlin like a professional, instead of nodding through a meeting while it draws neon ferns.

---

**Updated:** 2025-10-11  
**Status:** Ready to implement with rigorous evaluation  
**Estimated Time:** 2-3 weeks for full integration + evaluation


