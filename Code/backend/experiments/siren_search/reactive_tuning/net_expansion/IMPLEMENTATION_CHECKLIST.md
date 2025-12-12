# SIREN Architecture Expansion - Implementation Checklist

**Status:** Ready to Start  
**Last Updated:** 2025-12-17

---

## Pre-Flight Checklist

- [ ] Read `PRD.md` completely
- [ ] Review reference artifacts in `../` directory
- [ ] Verify GPU availability (CUDA)
- [ ] Check audio files exist: `docs/Audio/TOOL - The Pot (Audio).mp3`
- [ ] Create output directory: `net_expansion/`

---

## Phase 1: Reference Analysis (Days 1-2)

### Day 1: Load & Inspect

- [ ] Load `../diag_base_cosmic_particles_history.json`
- [ ] Load `../arch_d3w16_pot_history.json`
- [ ] Load `../arch_d4w12_pot_history.json`
- [ ] Extract architecture configs (depth, width, w0 values)
- [ ] Extract training configs (loss weights, steps, etc.)
- [ ] Note CLIP similarity scores
- [ ] Document parameter counts

### Day 2: Analyze & Document

- [ ] Compare architectures side-by-side
- [ ] Identify where motion appears/fails
- [ ] Document conditioning methods used
- [ ] Extract architectural lessons
- [ ] Create `reference_analysis.md`
- [ ] Refine hypothesis based on findings

**Deliverable:** `reference_analysis.md`

---

## Phase 2: Baseline Establishment (Days 3-4)

### Day 3: Train Baseline

- [ ] Run baseline 5×128 training (no audio)
- [ ] Monitor training loss curves
- [ ] Verify checkpoint saved correctly
- [ ] Generate preview video
- [ ] Document visual quality baseline

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

### Day 4: Validate & Document

- [ ] Review baseline visual quality
- [ ] Compare to reference artifacts
- [ ] Document expressivity floor
- [ ] Note any training issues
- [ ] Prepare for medium regime

**Deliverables:**
- `baseline_5x128_siren.pth`
- `baseline_5x128_history.json`
- `baseline_5x128_preview.mp4`

---

## Phase 3: Medium Regime Exploration (Days 5-10)

### Day 5: Medium-A & Medium-B

- [ ] Train Medium-A (6×256, w0=30/1.0)
- [ ] Train Medium-B (6×256, w0=50/10.0)
- [ ] Monitor both training runs
- [ ] Compare initial results

### Day 6: Medium-C & Medium-D

- [ ] Train Medium-C (7×256, w0=30/1.0)
- [ ] Train Medium-D (7×256, w0=50/10.0)
- [ ] Monitor both training runs
- [ ] Compare initial results

### Day 7: Evaluation & Comparison

- [ ] Generate previews for all 4 medium architectures
- [ ] Compare visual quality
- [ ] Compare CLIP similarity scores
- [ ] Identify top 2-3 candidates
- [ ] Document expressivity emergence

### Day 8-10: Refinement (if needed)

- [ ] Re-train top candidates with different seeds
- [ ] Test different w0 configurations
- [ ] Document findings

**Deliverables:**
- 4 trained architectures
- Training histories
- Preview videos
- Expressivity comparison report

---

## Phase 4: Audio Conditioning Implementation (Days 11-12)

### Day 11: Code Modifications

- [ ] **Option A:** Modify `siren_inr.py` for direct audio input
  - [ ] Add `audio_dim` parameter to `SirenINR.__init__`
  - [ ] Adjust `coord_dim` calculation
  - [ ] Test with dummy audio features
  - [ ] Verify forward pass works

- [ ] **Option B:** Implement phase modulation
  - [ ] Create `PhaseModulatedSirenLayer` class
  - [ ] Add audio → phase MLP
  - [ ] Integrate into `SirenINR`
  - [ ] Test with dummy audio

- [ ] **Option C:** Implement partial FiLM
  - [ ] Modify `FiLMConditioner` for gamma-only mode
  - [ ] Add flag to `SirenINR` for partial FiLM
  - [ ] Test gamma-only FiLM application

### Day 12: Test Runs

- [ ] Test Option A with top architecture
- [ ] Test Option B with top architecture
- [ ] Test Option C with top architecture
- [ ] Verify all three methods work
- [ ] Document any issues

**Deliverables:**
- Modified `siren_inr.py`
- Test runs completed
- Comparison report

---

## Phase 5: Audio Conditioning Testing (Days 13-15)

### Day 13: Direct Input Testing

- [ ] Train top architecture with direct input (audio-scale 0.05)
- [ ] Train top architecture with direct input (audio-scale 0.10)
- [ ] Train top architecture with direct input (audio-scale 0.15)
- [ ] Train top architecture with direct input (audio-scale 0.20)
- [ ] Perform Audio A/B tests for each
- [ ] Document perceptible motion

### Day 14: Phase Modulation Testing

- [ ] Train top architecture with phase modulation (phase-scale 0.1)
- [ ] Train top architecture with phase modulation (phase-scale 0.5)
- [ ] Train top architecture with phase modulation (phase-scale 1.0)
- [ ] Perform Audio A/B tests for each
- [ ] Document perceptible motion

### Day 15: Partial FiLM Testing

- [ ] Train top architecture with partial FiLM (audio-scale 0.1)
- [ ] Train top architecture with partial FiLM (audio-scale 0.2)
- [ ] Perform Audio A/B tests for each
- [ ] Document perceptible motion
- [ ] Compare all three methods
- [ ] Select best conditioning method

**Deliverables:**
- Trained models with audio conditioning
- Audio A/B comparison images
- Motion persistence videos
- Reactivity evaluation report

---

## Phase 6: Large Regime Stress Test (Days 16-17)

### Day 16: Large-A

- [ ] Train Large-A (8×256, w0=30/1.0)
- [ ] Monitor training stability
- [ ] Generate preview
- [ ] Document expressivity

### Day 17: Large-B

- [ ] Train Large-B (8×512, w0=30/1.0)
- [ ] Monitor training stability
- [ ] Generate preview
- [ ] Document expressivity
- [ ] Compare to medium regime
- [ ] Analyze scaling behavior

**Deliverables:**
- Large regime trained models
- Scaling analysis report
- Performance benchmarks

---

## Phase 7: Final Evaluation & Documentation (Days 18-21)

### Day 18: Resolution Scaling Tests

- [ ] Render top 2-3 architectures at 256px
- [ ] Render top 2-3 architectures at 512px
- [ ] Render top 2-3 architectures at 1080px
- [ ] Compare structure quality
- [ ] Document any collapse/artifacts
- [ ] Create resolution comparison images

### Day 19: Qualitative Evaluation

- [ ] Complete evaluation checklist for each architecture
  - [ ] Perceptible audio motion: Yes/No
  - [ ] Structural coherence: 1-5
  - [ ] Flicker presence: 1-5
  - [ ] Textural richness: 1-5
  - [ ] Overall quality: 1-5
- [ ] Compare to CPPN baseline
- [ ] Document findings

### Day 20: Compile Results

- [ ] Create `results_summary.csv`
  - [ ] Architecture configs
  - [ ] Parameter counts
  - [ ] CLIP similarity scores
  - [ ] Training times
  - [ ] Inference FPS
  - [ ] Qualitative scores
- [ ] Create `architecture_recommendation.md`
- [ ] Create `lessons_learned.md`

### Day 21: Final Report

- [ ] Write `final_report.md`
  - [ ] Executive summary
  - [ ] Methodology
  - [ ] Results
  - [ ] Recommendations
  - [ ] Next steps
- [ ] Review all documentation
- [ ] Mark PRD as complete

**Deliverables:**
- `results_summary.csv`
- `architecture_recommendation.md`
- `lessons_learned.md`
- `final_report.md`

---

## Quick Reference: Training Command Template

```bash
python Code/backend/clip_optimize_siren.py \
  --prompt "cosmic galaxy filled with dense points, starfield particles" \
  --audio "docs/Audio/TOOL - The Pot (Audio).mp3" \
  --output-dir Code/backend/experiments/siren_search/reactive_tuning/net_expansion \
  --run-name {ARCH_NAME} \
  --depth {DEPTH} --width {WIDTH} \
  --w0-first {W0_FIRST} --w0-hidden {W0_HIDDEN} \
  --steps 500 --train-resolution 256 \
  --clip-model ViT-B/16 --num-crops 8 \
  --clip-weight 1.6 --temp-weight 0.0 \
  --tv-weight 5e-5 --range-weight 2e-4 \
  --audio-scale {AUDIO_SCALE} \
  --device cuda
```

---

## Troubleshooting

### Training Instability

- [ ] Reduce learning rate (try 5e-5)
- [ ] Increase gradient clipping (try 2.0)
- [ ] Check for NaN in loss
- [ ] Verify input normalization

### No Audio Reactivity

- [ ] Verify audio features are non-zero
- [ ] Check audio scale (try higher: 0.15-0.20)
- [ ] Verify conditioning method is applied
- [ ] Check Audio A/B test shows difference

### Poor Visual Quality

- [ ] Increase w0_first (try 50)
- [ ] Increase w0_hidden (try 10)
- [ ] Try different architecture (more layers/width)
- [ ] Check CLIP similarity score

---

**Status Tracking:** Update this checklist as you progress  
**Last Updated:** 2025-12-17
