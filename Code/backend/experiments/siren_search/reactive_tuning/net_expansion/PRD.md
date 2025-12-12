---
phase: 3
artifact: prd
project: SIREN Architecture Expansion - Audio-Reactive Visuals
owner: Data Science
updated: 2025-12-17
status: Research → Architecture Validation
sources:
  - ../../../../../../docs/CPPN_SIREN_BRIEF.md
  - ../agents.md
  - ../../../../../../docs/Phase3-MVP/PRD_SIREN_INR.md
links:
  codebase:
    - ../../../../siren_inr.py
    - ../../../../clip_optimize_siren.py
    - ../../../../audio_analyzer.py
  reference_artifacts:
    - ../diag_base_cosmic_particles_history.json
    - ../arch_d3w16_pot_history.json
    - ../arch_d4w12_pot_history.json
output_dir: Code/backend/experiments/siren_search/reactive_tuning/net_expansion
---

# PRD — SIREN Architecture Expansion for Audio-Reactive Visuals

## 1. Executive Summary

**Goal:** Develop a SIREN-only neural architecture that produces visually rich, high-resolution continuous fields with perceptible, stable audio reactivity and temporal coherence, targeting real-time inference at ≥1080p60.

**Key Hypothesis:** SIRENs require a fundamentally different scaling regime than CPPNs. While CPPNs peak in an undercapacity regime (~100 params), SIRENs peak in a high-capacity, multi-frequency regime (100K+ params).

**Status:** Research phase - Architecture validation  
**Timeline:** 2-3 weeks  
**Output Location:** `Code/backend/experiments/siren_search/reactive_tuning/net_expansion/`

---

## 2. Context & Motivation

### 2.1 Prior Findings

**CPPN (Solved):**
- Tiny CPPNs (≈100 parameters) produce excellent organic visuals
- Strong audio reactivity achieved
- Optimal architecture: 3L×4D (107 params)
- Used as qualitative baseline only

**SIREN (Current State):**
- Tiny SIRENs (≤500 parameters) lack sufficient expressivity
- Audio reactivity insufficient at small scale
- Best current config: 3×12 (w0_first=40, w0_hidden=6, w0_time=3)
- CLIP similarity: 0.2703 (cosmic particles prompt)

### 2.2 Research Question

**At what scale does SIREN become expressive for audio-reactive visuals?**

This PRD formalizes the systematic exploration to answer:
1. Where does SIREN transition from undercapacity to expressive?
2. What architectural patterns unlock audio reactivity?
3. How does capacity enable separation of structure and motion?

### 2.3 Non-Goals (Explicit)

❌ **Do not hybridize with CPPN** - This is pure SIREN exploration  
❌ **Do not optimize for minimal parameter count** - Capacity is the goal  
❌ **Do not chase CLIP score at expense of motion** - Perceptible reactivity is primary  
❌ **Do not assume CPPN findings transfer directly** - Different regimes, different rules

---

## 3. Reference Artifacts Analysis (Critical First Step)

### 3.1 Required Actions

**Before any new experiments, analyze existing reference files:**

1. **Inspect checkpoint files:**
   - `../diag_base_cosmic_particles_siren.pth` (if exists)
   - `../arch_d3w16_pot_siren.pth` (if exists)
   - `../arch_d4w12_pot_siren.pth` (if exists)

2. **Analyze training histories:**
   - `../diag_base_cosmic_particles_history.json`
   - `../arch_d3w16_pot_history.json`
   - `../arch_d4w12_pot_history.json`

3. **Extract architectural lessons:**
   - Network size (layers × width)
   - Activation usage (verify pure sine)
   - Conditioning method (FiLM, audio integration)
   - Where motion/reactivity appears or fails
   - What changes produce perceptible motion
   - What changes are numerically present but visually irrelevant

### 3.2 Analysis Deliverable

**Create:** `net_expansion/reference_analysis.md`

**Contents:**
- Architecture comparison table
- Motion/reactivity observations
- Failure modes identified
- Architectural lessons extracted
- Hypothesis refinement based on findings

**Timeline:** Complete before starting new experiments (Day 1-2)

---

## 4. Architecture Exploration Scope

### 4.1 Baseline SIREN (Required Starting Point)

**Purpose:** Establish canonical SIREN baseline, no tricks.

**Configuration:**
```python
SirenINR(
    coord_dim=3,        # (x, y, t) only
    hidden_dim=128,    # Minimum viable
    num_layers=5,      # Minimum viable
    cond_dim=512,      # CLIP text embedding
    w0_first=30.0,      # Standard SIREN init
    w0_hidden=1.0,      # Standard SIREN init
    w0_time=None,      # No special time scaling initially
    film_hidden=64,    # Standard FiLM conditioner
    output_activation="tanh",
    use_bias=True
)
```

**Expected Parameters:** ~100K (floor, not an experiment)

**Training:**
- Steps: 500 @ 256px
- CLIP model: ViT-B/16
- Loss weights: CLIP=1.6, temporal=0.0 (early), TV=5e-5, range=2e-4
- Audio: None initially (establish structure first)

**Deliverable:** `baseline_5x128_siren.pth` + training history

---

### 4.2 Scaling Regimes to Test

#### Regime 1: Small (Baseline)
- **Layers:** 5
- **Width:** 128
- **Params:** ~100K
- **Purpose:** Establish baseline expressivity floor

#### Regime 2: Medium (Primary Learning)
- **Layers:** 6-7
- **Width:** 256
- **Params:** ~400K-800K
- **Purpose:** Primary learning regime - where expressivity emerges

#### Regime 3: Large (Stress Test)
- **Layers:** 8
- **Width:** 256-512
- **Params:** 1M+
- **Purpose:** Stress test expressivity limits

### 4.3 Architecture Matrix

**Test Grid:**

| Regime | Layers | Width | w0_first | w0_hidden | Expected Params | Priority |
|--------|--------|-------|----------|------------|-----------------|----------|
| Small | 5 | 128 | 30 | 1.0 | ~100K | Required |
| Medium-A | 6 | 256 | 30 | 1.0 | ~400K | High |
| Medium-B | 6 | 256 | 50 | 10.0 | ~400K | High |
| Medium-C | 7 | 256 | 30 | 1.0 | ~600K | High |
| Medium-D | 7 | 256 | 50 | 10.0 | ~600K | High |
| Large-A | 8 | 256 | 30 | 1.0 | ~800K | Medium |
| Large-B | 8 | 512 | 30 | 1.0 | ~1.5M | Medium |

**Total Configurations:** 7 architectures × 3 seeds = 21 training runs

**Timeline:** 2-3 weeks (parallel GPU runs possible)

---

## 5. Audio Conditioning Requirements

### 5.1 Strategy: Test Multiple Approaches

Audio must not be treated as a weak auxiliary signal. Test at least two of the following:

#### Option A: Direct Input Concatenation

**Implementation:**
```python
# Modify coord_dim to include audio features
coord_dim = 3 + audio_dim  # (x, y, t, audio_features...)
coords = torch.cat([spatial_coords, audio_features], dim=-1)
```

**Configuration:**
- Audio scale: 0.05, 0.10, 0.15, 0.20 (sweep)
- Normalization: Min-max normalized audio features
- Test with: Medium-B (6×256) architecture

**Deliverable:** `medium_b_direct_audio_scale_{scale}_siren.pth`

---

#### Option B: Phase Modulation (Preferred)

**Concept:** Audio → per-layer phase offsets  
**Formula:** `sin(ω(Wx + b) + φ(audio))`

**Implementation:**
```python
# Add phase modulation to SirenLayer
class PhaseModulatedSirenLayer(SirenLayer):
    def forward(self, x, audio_phase=None):
        x = self.linear(x)
        if audio_phase is not None:
            x = x + audio_phase  # Phase offset
        return torch.sin(self.w0 * x)
```

**Configuration:**
- Audio → MLP → per-layer phase offsets
- Phase scale: 0.1, 0.5, 1.0 (sweep)
- Test with: Medium-C (7×256) architecture

**Deliverable:** `medium_c_phase_audio_scale_{scale}_siren.pth`

**Status:** Requires code modification (new layer type)

---

#### Option C: Partial FiLM (γ-only)

**Concept:** Apply γ-only FiLM at mid-layers  
**Rationale:** Avoid β to prevent collapse, modulate scale only

**Implementation:**
```python
# Modify FiLM conditioner to output gamma-only for mid layers
# Apply gamma-only FiLM at layers 2-4 (skip first and last)
```

**Configuration:**
- Audio → AudioFiLM → gamma-only
- Audio scale: 0.1, 0.2
- Test with: Medium-D (7×256) architecture

**Deliverable:** `medium_d_partial_film_audio_scale_{scale}_siren.pth`

**Status:** Requires code modification (gamma-only FiLM)

---

### 5.2 Audio Conditioning Test Plan

**Phase 1: Structure First (Week 1)**
- Train all architectures WITHOUT audio
- Establish baseline visual quality
- Document expressivity emergence

**Phase 2: Audio Integration (Week 2)**
- Add audio conditioning to top 2-3 architectures
- Test all three conditioning methods
- Compare perceptible motion

**Phase 3: Optimization (Week 3)**
- Refine best conditioning method
- Tune audio scales
- Final validation

---

## 6. Training Protocol

### 6.1 Optimization Settings

**Optimizer:** Adam  
**Precision:** FP32 only (no FP16 for training)  
**Learning Rate:** 1e-4 to 5e-4 (lower than CPPN)  
**Weight Decay:** 0.0 (no regularization via weight decay)  
**Gradient Clipping:** 1.0 (prevent spikes)

**LR Schedule:**
- Warmup: 250 steps (linear ramp)
- Main: Constant LR
- Optional decay: Cosine decay after 80% of steps

---

### 6.2 Loss Functions

**Primary Losses:**

1. **CLIP Guidance:**
   - Model: ViT-B/16
   - Multi-crop: 8 crops per step
   - Crop scale: 0.5-1.0 (random jitter)
   - Weight: 1.6 (fixed)

2. **Temporal Smoothness:**
   - L2 between frames: `||I_t - I_{t+Δ}||_2`
   - Delta range: [1/24, 1/12] of sequence duration
   - **Critical:** Scheduled weight (see below)

3. **Total Variation:**
   - Per-frame TV loss
   - Weight: 5e-5

4. **Range Clamp:**
   - Soft penalty for RGB outside [-1, 1]
   - Weight: 2e-4

### 6.3 Temporal Loss Schedule (Critical)

**Problem:** Early temporal loss kills reactivity

**Solution:** Scheduled temporal weight

| Phase | Steps | Temporal Weight | Rationale |
|-------|-------|----------------|-----------|
| Early | 0-200 | 0.0 | Let structure form |
| Mid | 200-400 | 0.1-0.2 | Introduce smoothness |
| Late | 400-500 | 0.3-0.5 | Enforce coherence |

**Implementation:**
```python
def get_temporal_weight(step: int, total_steps: int) -> float:
    if step < total_steps * 0.4:
        return 0.0
    elif step < total_steps * 0.8:
        return 0.1 + 0.1 * (step - total_steps * 0.4) / (total_steps * 0.4)
    else:
        return 0.3 + 0.2 * (step - total_steps * 0.8) / (total_steps * 0.2)
```

---

### 6.4 Training Resolution Strategy

**Multi-Resolution Pyramid:**

| Phase | Resolution | Steps | Purpose |
|-------|------------|-------|---------|
| 1 | 256px | 300 | Establish composition |
| 2 | 512px | 200 | Add detail |
| 3 | 1080px | Optional | Final validation |

**Default:** 256px for architecture search, 512px for final candidates

---

## 7. Evaluation Criteria

### 7.1 Required Visual Tests

**For every candidate architecture, perform:**

#### Test 1: Audio A/B Test

**Procedure:**
1. Render same (x, y, t) coordinates
2. Use two different audio embeddings (e.g., silence vs music)
3. Compare rendered frames side-by-side

**Success Criteria:** Visible difference between audio conditions

**Deliverable:** `{arch_name}_audio_ab_comparison.png`

---

#### Test 2: Motion Persistence Test

**Procedure:**
1. Train with temporal loss disabled (early phase)
2. Enable temporal loss (late phase)
3. Verify motion survives temporal smoothing

**Success Criteria:** Motion remains perceptible after temporal loss enabled

**Deliverable:** `{arch_name}_motion_persistence.mp4` (before/after comparison)

---

#### Test 3: Resolution Scaling

**Procedure:**
1. Render at 256px, 512px, 1080px
2. Compare structure quality
3. Check for collapse or artifacts

**Success Criteria:** Structure improves with resolution, no collapse

**Deliverable:** `{arch_name}_resolution_comparison.png` (3-panel)

---

### 7.2 Qualitative Metrics

**Human Evaluation Checklist:**

1. **Perceptible Audio Motion:** Yes/No
   - Can you see the difference when audio changes?
   - Is motion synchronized with audio beats?

2. **Structural Coherence:** 1-5 scale
   - Does the visual make sense spatially?
   - Are patterns coherent or chaotic?

3. **Flicker Presence:** 1-5 scale (lower is better)
   - How much temporal flicker?
   - Is it distracting or acceptable?

4. **Textural Richness vs Noise:** 1-5 scale
   - Rich detail or just noise?
   - Does texture serve the visual?

5. **Overall Quality:** 1-5 scale
   - Would you use this in production?
   - Does it match or exceed CPPN baseline?

**Note:** CLIP score alone is insufficient - perceptible motion is primary.

---

### 7.3 Quantitative Metrics

**Record for each run:**

- CLIP similarity (text-image cosine)
- Parameter count
- Training time
- Inference FPS @ 1080p60
- VRAM usage
- Temporal variance (frame-to-frame difference)
- Audio variance (silence vs music difference)

**Deliverable:** `net_expansion/results_summary.csv`

---

## 8. Implementation Steps

### Step 1: Reference Analysis (Days 1-2)

**Tasks:**
1. Load and inspect reference checkpoint files
2. Analyze training histories
3. Extract architectural lessons
4. Document findings in `reference_analysis.md`

**Deliverables:**
- `reference_analysis.md`
- Architecture comparison table
- Hypothesis refinement

---

### Step 2: Baseline Establishment (Days 3-4)

**Tasks:**
1. Train baseline 5×128 SIREN (no audio)
2. Validate training pipeline works at scale
3. Establish visual quality baseline
4. Document expressivity floor

**Command:**
```bash
python Code/backend/clip_optimize_siren.py \
  --prompt "cosmic galaxy filled with dense points, starfield particles" \
  --audio "docs/Audio/TOOL - The Pot (Audio).mp3" \
  --output-dir Code/backend/experiments/siren_search/reactive_tuning/net_expansion \
  --run-name baseline_5x128 \
  --depth 5 --width 128 \
  --w0-first 30 --w0-hidden 1.0 \
  --steps 500 --train-resolution 256 \
  --clip-model ViT-B/16 --num-crops 8 \
  --clip-weight 1.6 --temp-weight 0.0 \
  --tv-weight 5e-5 --range-weight 2e-4 \
  --audio-scale 0.0 \
  --device cuda
```

**Deliverables:**
- `baseline_5x128_siren.pth`
- `baseline_5x128_history.json`
- `baseline_5x128_preview.mp4`

---

### Step 3: Medium Regime Exploration (Days 5-10)

**Tasks:**
1. Train Medium-A through Medium-D architectures
2. Test different w0 configurations
3. Compare expressivity emergence
4. Identify top 2-3 candidates

**Commands (example for Medium-A):**
```bash
python Code/backend/clip_optimize_siren.py \
  --prompt "cosmic galaxy filled with dense points, starfield particles" \
  --audio "docs/Audio/TOOL - The Pot (Audio).mp3" \
  --output-dir Code/backend/experiments/siren_search/reactive_tuning/net_expansion \
  --run-name medium_a_6x256_w30_h1 \
  --depth 6 --width 256 \
  --w0-first 30 --w0-hidden 1.0 \
  --steps 500 --train-resolution 256 \
  --clip-model ViT-B/16 --num-crops 8 \
  --clip-weight 1.6 --temp-weight 0.0 \
  --tv-weight 5e-5 --range-weight 2e-4 \
  --audio-scale 0.0 \
  --device cuda
```

**Deliverables:**
- 4 trained architectures (Medium-A through D)
- Training histories
- Preview videos
- Expressivity comparison report

---

### Step 4: Audio Conditioning Implementation (Days 11-12)

**Tasks:**
1. Implement Option A (Direct Input) - modify `siren_inr.py`
2. Implement Option B (Phase Modulation) - new layer type
3. Implement Option C (Partial FiLM) - gamma-only FiLM
4. Test each with top architecture candidate

**Code Changes Required:**

**Option A:** Modify `SirenINR.__init__` to accept `audio_dim` and adjust `coord_dim`

**Option B:** Create `PhaseModulatedSirenLayer` class

**Option C:** Modify `FiLMConditioner` to support gamma-only mode

**Deliverables:**
- Code modifications in `siren_inr.py`
- Test runs with each conditioning method
- Comparison report

---

### Step 5: Audio Conditioning Testing (Days 13-15)

**Tasks:**
1. Train top 2-3 architectures with each audio conditioning method
2. Perform Audio A/B tests
3. Evaluate motion persistence
4. Compare perceptible reactivity

**Commands (example for Direct Input):**
```bash
python Code/backend/clip_optimize_siren.py \
  --prompt "cosmic galaxy filled with dense points, starfield particles" \
  --audio "docs/Audio/TOOL - The Pot (Audio).mp3" \
  --output-dir Code/backend/experiments/siren_search/reactive_tuning/net_expansion \
  --run-name medium_a_direct_audio_scale_0.15 \
  --depth 6 --width 256 \
  --w0-first 30 --w0-hidden 1.0 \
  --steps 500 --train-resolution 256 \
  --clip-model ViT-B/16 --num-crops 8 \
  --clip-weight 1.6 --temp-weight 0.0 \
  --tv-weight 5e-5 --range-weight 2e-4 \
  --audio-scale 0.15 \
  --enable-direct-audio-input \
  --device cuda
```

**Deliverables:**
- Trained models with audio conditioning
- Audio A/B comparison images
- Motion persistence videos
- Reactivity evaluation report

---

### Step 6: Large Regime Stress Test (Days 16-17)

**Tasks:**
1. Train Large-A and Large-B architectures
2. Test expressivity limits
3. Evaluate performance vs quality tradeoff
4. Document scaling behavior

**Deliverables:**
- Large regime trained models
- Scaling analysis report
- Performance benchmarks

---

### Step 7: Final Evaluation & Documentation (Days 18-21)

**Tasks:**
1. Perform resolution scaling tests
2. Complete qualitative evaluation checklist
3. Compile results summary CSV
4. Write final architecture recommendation report
5. Document lessons learned

**Deliverables:**
- `results_summary.csv`
- `architecture_recommendation.md`
- `lessons_learned.md`
- `final_report.md`

---

## 9. Success Definition

### 9.1 Primary Success Criteria

**This PRD is successful if we can answer:**

1. **At what scale does SIREN become expressive?**
   - Clear parameter range identified
   - Expressivity threshold documented

2. **Which audio conditioning methods work?**
   - At least one method produces perceptible motion
   - Method validated across multiple architectures

3. **What are the validated SIREN architectures?**
   - Short list (≤3) of architectures that work
   - Each validated with audio A/B test and motion persistence

4. **What architectural intuition can we transfer?**
   - Clear lessons for future models
   - Understanding of capacity vs expressivity tradeoff

### 9.2 Secondary Success Criteria

- At least one architecture matches or exceeds CPPN baseline quality
- Real-time inference feasible (≥1.0× @ 1080p60)
- Temporal coherence acceptable (flicker ≤ baseline)
- Audio reactivity perceptible (human evaluation: Yes)

### 9.3 Success Statement

**Target outcome:**

> "This is the regime where SIREN starts behaving like a proper audiovisual model, and here's why."

**Even if CPPN remains aesthetically superior, understanding this boundary is the win.**

---

## 10. Expected Artifacts

### 10.1 Code Artifacts

- Modified `siren_inr.py` (audio conditioning methods)
- Training scripts (if needed)
- Evaluation scripts (audio A/B, motion persistence, resolution scaling)

### 10.2 Model Artifacts

- 7+ trained SIREN checkpoints (`.pth` files)
- Training histories (`.json` files)
- Preview videos (`.mp4` files)

### 10.3 Documentation Artifacts

- `reference_analysis.md`
- `results_summary.csv`
- `architecture_recommendation.md`
- `lessons_learned.md`
- `final_report.md`

### 10.4 Evaluation Artifacts

- Audio A/B comparison images
- Motion persistence videos
- Resolution scaling comparisons
- Qualitative evaluation checklists

---

## 11. Timeline & Milestones

| Milestone | Days | Deliverables |
|-----------|------|--------------|
| M1: Reference Analysis | 1-2 | `reference_analysis.md` |
| M2: Baseline Established | 3-4 | Baseline 5×128 model |
| M3: Medium Regime Explored | 5-10 | 4 medium architectures trained |
| M4: Audio Conditioning Implemented | 11-12 | Code modifications + test runs |
| M5: Audio Conditioning Tested | 13-15 | Audio A/B tests, motion persistence |
| M6: Large Regime Tested | 16-17 | Large architectures trained |
| M7: Final Evaluation | 18-21 | Complete documentation |

**Total Timeline:** 3 weeks (21 days)

---

## 12. Risk Mitigation

### Risk 1: Training Instability at Scale

**Mitigation:**
- Start with baseline (5×128)
- Use gradient clipping
- Monitor loss curves closely
- Reduce LR if divergence occurs

### Risk 2: Audio Conditioning Doesn't Work

**Mitigation:**
- Test multiple conditioning methods
- Start with direct input (simplest)
- Document failure modes
- Even negative results are valuable

### Risk 3: Insufficient Expressivity

**Mitigation:**
- Test up to Large regime (1M+ params)
- Try different w0 configurations
- Document scaling behavior
- Understand limits is also success

### Risk 4: Temporal Loss Kills Reactivity

**Mitigation:**
- Use scheduled temporal weight (start at 0.0)
- Test motion persistence explicitly
- Document when reactivity disappears

---

## 13. Notes from Prior Research

**Observations to Guide Exploration:**

1. **Tiny networks excel at organic emergence (CPPN)**
   - Don't try to replicate this with SIREN
   - Different regimes, different strengths

2. **Large networks excel at signal fidelity (SIREN)**
   - This is where SIREN should shine
   - Capacity enables separation of structure and motion

3. **Audio reactivity is global, not local**
   - Audio affects entire field, not just regions
   - Conditioning method should reflect this

4. **Capacity enables separation of structure and motion**
   - Small networks: structure and motion compete
   - Large networks: can encode both simultaneously

**These observations should guide, not constrain, exploration.**

---

## 14. References

- **SIREN Paper:** Sitzmann, V. et al. (2020). "Implicit Neural Representations with Periodic Activation Functions"
- **FiLM Paper:** Perez, E. et al. (2018). "Film: Visual Reasoning with a General Conditioning Layer"
- **CLIP Paper:** Radford, A. et al. (2021). "Learning Transferable Visual Models From Natural Language Supervision"
- **CPPN Brief:** `docs/CPPN_SIREN_BRIEF.md`
- **SIREN PRD:** `docs/Phase3-MVP/PRD_SIREN_INR.md`

---

**Document Status:** Active - Ready for Implementation  
**Last Updated:** 2025-12-17  
**Next Review:** After M1 (Reference Analysis Complete)
