# CPPN & SIREN Approaches - Technical Brief

**Date:** 2025-12-17  
**Status:** Active Research & Implementation  
**Scope:** Architecture comparison, training methodology, and common pitfalls

---

## Executive Summary

This project explores two neural network approaches for audio-reactive visual generation:
- **CPPN** (Compositional Pattern-Producing Network): Original approach with mixed activations
- **SIREN** (Sinusoidal Representation Network): Alternative with sine activations and FiLM conditioning

**Key Finding:** Smaller networks (3 layers × 4-12 hidden dimensions) produce superior organic patterns compared to larger networks, despite having 4,000× fewer parameters.

---

## CPPN Approach

### Architecture

**Core Design:**
- Maps `(x, y, time, audio_features)` → `(R, G, B)`
- Mixed activation functions: `sin`, `cos`, `gaussian`, `tanh` (alternating per layer)
- Xavier initialization with `gain=5.0` (critical for temporal variation)
- CUDA-accelerated inference

**Typical Configuration:**
```python
CPPN(
    input_dim=12,      # x, y, time + 9 audio features
    hidden_dim=256,     # Phase A baseline
    num_layers=8,       # Phase A baseline
    output_dim=3        # RGB
)
```

**Optimal Configuration (Phase C Discovery):**
```python
CPPN(
    input_dim=12,
    hidden_dim=4,      # Optimal for organic patterns
    num_layers=3,       # Optimal depth
    output_dim=3
)
# Total: ~107 parameters (vs 464K baseline)
```

### What Has Been Tested

**Phase A - Baseline Pipeline:**
- Architecture: 8 layers × 256 hidden dim (464K parameters)
- Performance: 249M pixels/sec, 52+ FPS @ 720p
- Issue: Random patterns, no aesthetic control

**Phase C - Architecture Research:**
- **Systematic Testing:** 36 configurations tested
  - Layers: 2, 3, 4, 5
  - Hidden dims: 32, 64, 128 (later refined to 4, 6, 8, 12)
  - Seeds: 3 per configuration
- **Winner:** 3 layers × 4 hidden dim (3L_4D)
  - Overall score: 4.42/5.0
  - Organic quality: 5.0/5.0 (perfect)
  - Parameters: 107 (4,346× fewer than baseline)
  - Performance: 1.40× realtime @ 720p

**CLIP Training:**
- Prompt: "spinning cosmic galaxy with swirling nebula clouds..."
- Architecture: 3L_4D
- Iterations: 800 (400 @ 256px, 400 @ 512px)
- Result: CLIP similarity 0.2335
- Training time: ~8 minutes

### Training Progress

**Status:** ✅ Production-ready training pipeline

**Training Method:**
- CLIP-guided optimization (frozen CLIP encoder)
- Multi-resolution pyramid (256px → 512px)
- Adam optimizer, learning rate 0.001
- Loss: CLIP text-image cosine similarity

**Trained Styles:**
- ✅ Cosmic Galaxy (3L_4D) - CLIP sim: 0.2335
- 📋 Biology series planned (cellular, organisms, solvents, neurons)

**Performance:**
- Training: ~8 minutes per style (3L_4D)
- Inference: 1.40× realtime @ 720p, 30 FPS
- Memory: <50 MB VRAM

---

## SIREN Approach

### Architecture

**Core Design:**
- Maps `(x, y, t)` → `RGB` using sine activations
- SIREN initialization (w0_first, w0_hidden, optional w0_time)
- FiLM conditioning (gamma, beta per layer) from CLIP text embeddings
- Optional audio conditioning via separate AudioFiLM branch

**Typical Configuration:**
```python
SirenINR(
    coord_dim=3,        # x, y, t
    hidden_dim=12,      # Tiny regime (4-12)
    num_layers=3,       # Optimal depth
    cond_dim=512,       # CLIP text embedding
    w0_first=40.0,      # High frequency for first layer
    w0_hidden=6.0,      # Lower frequency for hidden
    w0_time=3.0         # Optional separate time scaling
)
```

**Optimal Configuration (Reactive Tuning):**
- Depth: 3 layers
- Width: 12 hidden dimensions
- w0_first: 40
- w0_hidden: 6
- w0_time: 3
- Parameters: ~300-500 (within tiny regime)

### What Has Been Tested

**Architecture Search (Phase 3):**
- **Tiny Grid Sweep:**
  - Depths: {2, 3, 4}
  - Widths: {4, 6, 8, 12}
  - w0_first: {30, 40, 50}
  - w0_hidden: {1, 5, 6, 10}
  - w0_time: {2, 2.5, 3}

**Recent Experiments (Reactive Tuning):**
- **Baseline:** 3×12, w0_first=40, w0_hidden=6, w0_time=3
  - Best CLIP similarity: 0.2703 (cosmic particles prompt)
- **Alternatives Tested:**
  - 4×12 (w0_first=50, w0_hidden=5, w0_time=2.5): sim 0.2642
  - 3×16 (w0_first=50, w0_hidden=8, w0_time=2): sim 0.2666

**Audio Reactivity Experiments:**
- Baseline: `audio-scale=0.05` (minimal coupling)
- Boosted: `audio-scale=0.15` + AudioFiLM + audio gate
- Comparison: Visual delta between low/high audio coupling

**Training Configuration:**
- CLIP model: ViT-B/16
- Multi-crop augmentation: 8 crops
- Loss weights: CLIP=1.6, temporal=0.5, TV=5e-5, range=2e-4
- Steps: 320-400 @ 256px training resolution

### Training Progress

**Status:** 🔬 Active experimentation

**Training Method:**
- CLIP-guided with multi-crop loss
- Temporal smoothness penalty (L2 between frames)
- Total Variation (TV) regularization
- Range clamping for RGB values
- Optional AudioFiLM for enhanced audio coupling

**Current Results:**
- Best CLIP similarity: 0.2703 (baseline 3×12 config)
- Training time: ~10-20 minutes per run
- Flicker metrics: Being evaluated
- Performance: Real-time capable (target ≥1.0× @ 1080p60)

**Challenges:**
- Finding balance between structure (CLIP) and motion (temporal)
- Audio coupling strength vs visual coherence
- Flicker suppression without over-smoothing

---

## General Pitfalls & Lessons Learned

### 1. Weight Initialization Critical

**Problem:** CPPN generated static frames (all identical, variance=0.00)

**Root Cause:**
- Xavier initialization with `gain=1.0` caused signal vanishing
- Small inputs → small outputs through sin/cos → saturation
- Final output collapsed to constant RGB≈(0.5, 0.5, 0.5)

**Solution:**
- Changed Xavier `gain` from 1.0 to 5.0
- Larger weights maintain signal through periodic activations
- Result: Dynamic, varying colors throughout video

**Lesson:** Initialization gain is critical for networks with periodic activations.

---

### 2. Network Size Myth Debunked

**Assumption:** "Bigger network = better patterns"

**Reality:** Smaller networks produce superior organic patterns

**Evidence:**
- 3L×4D (107 params): 5.0/5 organic quality, 4.42/5 overall
- 8L×256D (464K params): ~2.5/5 organic quality, ~2.5/5 overall
- 4,346× fewer parameters, better results

**Why Smaller Wins:**
1. Signal preservation - fewer layers prevent information loss
2. Activation efficacy - sin/cos work better in shallow networks
3. Organic emergence - simplicity yields natural complexity
4. Less overfitting - tiny networks can't memorize, must generalize

**Lesson:** Architecture matters more than capacity for organic patterns.

---

### 3. FP16 Precision Issues

**Problem:** FP16 caused gradient issues during CLIP optimization

**Symptoms:**
- Gradients stuck (similarity didn't improve)
- Training instability
- Underflow/overflow in tiny networks

**Solution:**
- Disabled FP16 for CLIP training (needs stable gradients)
- Use FP32 for training, FP16 only for inference
- Or use mixed precision with careful gradient scaling

**Lesson:** FP16 requires careful handling during optimization, especially for small networks.

---

### 4. Temporal Smoothness vs Flicker

**Problem:** Balancing temporal continuity with visual detail

**Challenges:**
- Too much temporal loss → over-smoothing, no motion
- Too little temporal loss → flicker, shimmer artifacts
- CLIP pushes for structure, but can create adversarial textures

**Solutions:**
- Temporal loss weight: 0.1-0.5 (tuned per architecture)
- Temporal delta: random Δ in [1/24, 1/12] of sequence duration
- TV regularization: 5e-5 to 1e-3 (suppresses noise)
- Optional temporal spectral penalty for shimmer

**Lesson:** Temporal smoothness requires careful loss weighting and regularization.

---

### 5. Audio Feature Scaling

**Problem:** Audio features can overwhelm spatial coordinates

**Symptoms:**
- Visuals become chaotic, lose spatial structure
- Audio reactivity too strong, patterns break apart
- Or audio reactivity too weak, no visible response

**Solutions:**
- Default audio scale: 0.05 (minimal coupling)
- Boosted scale: 0.15-0.20 (stronger coupling)
- AudioFiLM branch: Separate modulation path for audio
- Audio gate: Conditional audio influence

**Lesson:** Audio feature scaling is a critical hyperparameter for reactivity vs coherence.

---

### 6. CLIP Adversarial Textures

**Problem:** CLIP can create adversarial patterns that fool the model

**Symptoms:**
- High-frequency noise patterns
- Unnatural color combinations
- Text-like artifacts

**Mitigations:**
- Multi-crop augmentation (4-8 crops)
- Crop scale jitter (0.5-1.0)
- TV regularization (suppresses noise)
- Range clamping (keeps RGB in valid range)
- Early CLIP weight ramp (start low, increase gradually)

**Lesson:** CLIP guidance requires regularization to prevent adversarial artifacts.

---

### 7. Coordinate Scaling

**Problem:** Coordinates in [0, 1] or [-1, 1] produce boring patterns

**Issue:**
- Sin/cos activations see only ~0.3 radians of range
- Results in flat, uninteresting fields

**Solution:**
- Map coordinates to [-π, π] or similar
- Full sinusoidal range → rich patterns
- Or use SIREN w0 scaling to control frequency

**Lesson:** Coordinate scaling is crucial for periodic activation functions.

---

### 8. Windows Console Encoding

**Problem:** Unicode emojis fail on Windows console (cp1252 encoding)

**Symptoms:**
- UnicodeEncodeError when printing emojis
- Script crashes on Windows

**Solution:**
- Remove all emojis from console output
- Use ASCII-only characters for progress indicators
- Document this as a critical warning

**Lesson:** Cross-platform compatibility requires avoiding Unicode in console output.

---

### 9. Variable Name Collisions

**Problem:** Parameter names conflict with local variables

**Example:**
- `duration` parameter vs `duration` local variable
- Causes bugs in audio analysis

**Solution:**
- Use descriptive names: `audio_duration` vs `clip_duration`
- Be careful with parameter vs local variable names
- Test early with quick runs (100 iterations)

**Lesson:** Careful naming prevents subtle bugs.

---

### 10. Architecture Search Complexity

**Problem:** Large search space makes finding optimal config difficult

**Challenge:**
- Many hyperparameters: depth, width, w0_first, w0_hidden, w0_time
- Loss weights: CLIP, temporal, TV, range
- Audio coupling: scale, FiLM, gate
- Training: LR, optimizer, warmup, gradient clip

**Approach:**
- Start with tiny grid (preferred ≤150 params)
- Stage 1: Low-res (256px), short schedules, prune configs
- Stage 2: Top ~5 at 720p, re-evaluate
- Stage 3: Top 2 at 1080p60, ≥3 seeds each
- Only expand if tiny grid fails quality target

**Lesson:** Systematic staged search prevents combinatorial explosion.

---

## Comparison: CPPN vs SIREN

### Architecture Differences

| Aspect | CPPN | SIREN |
|--------|------|-------|
| **Activations** | Mixed (sin, cos, gaussian, tanh) | Sine only |
| **Initialization** | Xavier (gain=5.0) | SIREN init (w0 scaling) |
| **Conditioning** | Audio features in input | FiLM (gamma/beta per layer) |
| **Audio Integration** | Direct input concatenation | Optional AudioFiLM branch |
| **Optimal Size** | 3L×4D (107 params) | 3L×12D (~300-500 params) |

### Training Differences

| Aspect | CPPN | SIREN |
|--------|------|-------|
| **CLIP Guidance** | Direct optimization | FiLM conditioning |
| **Temporal Loss** | Not used (inherent smoothness) | Explicit temporal penalty |
| **Regularization** | Minimal | TV + range clamp |
| **Training Time** | ~8 min (3L_4D) | ~10-20 min (3L×12D) |
| **CLIP Similarity** | 0.2335 (cosmic) | 0.2703 (cosmic particles) |

### Performance

| Metric | CPPN (3L×4D) | SIREN (3L×12D) |
|--------|---------------|----------------|
| **Parameters** | 107 | ~300-500 |
| **Inference** | 1.40× realtime @ 720p | Real-time capable |
| **Memory** | <50 MB | <100 MB |
| **Organic Quality** | 5.0/5.0 | Being evaluated |

### Use Cases

**CPPN:**
- ✅ Proven organic patterns (5.0/5.0 rating)
- ✅ Simpler architecture (fewer parameters)
- ✅ Faster training (~8 min)
- ✅ Direct audio integration

**SIREN:**
- ✅ Better CLIP similarity (0.2703 vs 0.2335)
- ✅ More flexible conditioning (FiLM)
- ✅ Explicit temporal control
- ✅ Better regularization options

---

## Current Status

### CPPN
- ✅ Optimal architecture discovered (3L×4D)
- ✅ CLIP training validated
- ✅ Production-ready pipeline
- ✅ One trained style (cosmic galaxy)

### SIREN
- 🔬 Active architecture search
- 🔬 Audio reactivity tuning
- 🔬 Flicker metric evaluation
- 📋 Best config: 3×12 (w0_first=40, w0_hidden=6, w0_time=3)

### Next Steps

**CPPN:**
- Train biology series (cellular, organisms, solvents, neurons)
- Expand style library
- Integrate into MVP desktop app

**SIREN:**
- Complete architecture search evaluation
- Validate flicker metrics vs CPPN baseline
- Test at 1080p60 for real-time performance
- Compare final quality metrics

---

## Key Takeaways

1. **Smaller is better** - Tiny networks (100-500 params) produce superior organic patterns
2. **Initialization matters** - Gain=5.0 critical for CPPN, SIREN init critical for SIREN
3. **CLIP training works** - Both approaches benefit from CLIP guidance
4. **Audio coupling is delicate** - Scale 0.05-0.15 range, requires careful tuning
5. **Temporal smoothness is hard** - Balance between motion and flicker requires regularization
6. **Systematic search pays off** - Staged architecture search prevents wasted compute
7. **Cross-platform issues** - Windows console encoding requires ASCII-only output
8. **Both approaches viable** - CPPN proven, SIREN promising with better CLIP scores

---

## References

- **CPPN:** Stanley, K.O. (2007). "Compositional pattern producing networks"
- **SIREN:** Sitzmann, V. et al. (2020). "Implicit Neural Representations with Periodic Activation Functions"
- **CLIP:** Radford, A. et al. (2021). "Learning Transferable Visual Models From Natural Language Supervision"
- **FiLM:** Perez, E. et al. (2018). "Film: Visual Reasoning with a General Conditioning Layer"

---

**Document Status:** Active - Updated with latest experimental results  
**Last Updated:** 2025-12-17  
**Maintainer:** Aitor Patiño Diaz
