# Reference Artifacts Analysis

**Date:** [FILL IN]  
**Analyst:** [FILL IN]  
**Purpose:** Extract architectural lessons from existing SIREN experiments

---

## 1. Reference Files Analyzed

### File 1: `../diag_base_cosmic_particles_history.json`

**Architecture:**
- Depth: [FILL IN]
- Width: [FILL IN]
- w0_first: [FILL IN]
- w0_hidden: [FILL IN]
- w0_time: [FILL IN]
- Parameters: [FILL IN]

**Training Config:**
- Steps: [FILL IN]
- Resolution: [FILL IN]
- CLIP model: [FILL IN]
- Loss weights: [FILL IN]
- Audio scale: [FILL IN]
- Audio conditioning: [FILL IN]

**Results:**
- Best CLIP similarity: [FILL IN]
- Training time: [FILL IN]
- Visual quality: [FILL IN]
- Audio reactivity: [FILL IN]

**Observations:**
- [FILL IN: Where does motion appear?]
- [FILL IN: Where does motion fail?]
- [FILL IN: What changes produce perceptible motion?]
- [FILL IN: What changes are numerically present but visually irrelevant?]

---

### File 2: `../arch_d3w16_pot_history.json`

**Architecture:**
- Depth: [FILL IN]
- Width: [FILL IN]
- w0_first: [FILL IN]
- w0_hidden: [FILL IN]
- w0_time: [FILL IN]
- Parameters: [FILL IN]

**Training Config:**
- Steps: [FILL IN]
- Resolution: [FILL IN]
- CLIP model: [FILL IN]
- Loss weights: [FILL IN]
- Audio scale: [FILL IN]
- Audio conditioning: [FILL IN]

**Results:**
- Best CLIP similarity: [FILL IN]
- Training time: [FILL IN]
- Visual quality: [FILL IN]
- Audio reactivity: [FILL IN]

**Observations:**
- [FILL IN: Where does motion appear?]
- [FILL IN: Where does motion fail?]
- [FILL IN: What changes produce perceptible motion?]
- [FILL IN: What changes are numerically present but visually irrelevant?]

---

### File 3: `../arch_d4w12_pot_history.json`

**Architecture:**
- Depth: [FILL IN]
- Width: [FILL IN]
- w0_first: [FILL IN]
- w0_hidden: [FILL IN]
- w0_time: [FILL IN]
- Parameters: [FILL IN]

**Training Config:**
- Steps: [FILL IN]
- Resolution: [FILL IN]
- CLIP model: [FILL IN]
- Loss weights: [FILL IN]
- Audio scale: [FILL IN]
- Audio conditioning: [FILL IN]

**Results:**
- Best CLIP similarity: [FILL IN]
- Training time: [FILL IN]
- Visual quality: [FILL IN]
- Audio reactivity: [FILL IN]

**Observations:**
- [FILL IN: Where does motion appear?]
- [FILL IN: Where does motion fail?]
- [FILL IN: What changes produce perceptible motion?]
- [FILL IN: What changes are numerically present but visually irrelevant?]

---

## 2. Architecture Comparison

| Metric | diag_base_cosmic | arch_d3w16 | arch_d4w12 |
|--------|------------------|------------|------------|
| Depth | [FILL IN] | [FILL IN] | [FILL IN] |
| Width | [FILL IN] | [FILL IN] | [FILL IN] |
| Parameters | [FILL IN] | [FILL IN] | [FILL IN] |
| w0_first | [FILL IN] | [FILL IN] | [FILL IN] |
| w0_hidden | [FILL IN] | [FILL IN] | [FILL IN] |
| CLIP Sim | [FILL IN] | [FILL IN] | [FILL IN] |
| Audio Reactivity | [FILL IN] | [FILL IN] | [FILL IN] |

---

## 3. Architectural Lessons Extracted

### Lesson 1: [FILL IN TITLE]

**Finding:**
[FILL IN: What did we learn?]

**Evidence:**
[FILL IN: What supports this finding?]

**Implication:**
[FILL IN: What does this mean for net expansion?]

---

### Lesson 2: [FILL IN TITLE]

**Finding:**
[FILL IN: What did we learn?]

**Evidence:**
[FILL IN: What supports this finding?]

**Implication:**
[FILL IN: What does this mean for net expansion?]

---

### Lesson 3: [FILL IN TITLE]

**Finding:**
[FILL IN: What did we learn?]

**Evidence:**
[FILL IN: What supports this finding?]

**Implication:**
[FILL IN: What does this mean for net expansion?]

---

## 4. Motion/Reactivity Analysis

### Where Motion Appears

**Architecture:** [FILL IN]
- [FILL IN: Describe where motion is visible]
- [FILL IN: What audio features trigger it?]
- [FILL IN: Is it global or local?]

**Architecture:** [FILL IN]
- [FILL IN: Describe where motion is visible]
- [FILL IN: What audio features trigger it?]
- [FILL IN: Is it global or local?]

---

### Where Motion Fails

**Architecture:** [FILL IN]
- [FILL IN: Describe where motion fails]
- [FILL IN: Why might it fail?]
- [FILL IN: What could fix it?]

**Architecture:** [FILL IN]
- [FILL IN: Describe where motion fails]
- [FILL IN: Why might it fail?]
- [FILL IN: What could fix it?]

---

### Perceptible vs Numerical Motion

**Perceptible Motion:**
- [FILL IN: What changes produce visible motion?]
- [FILL IN: What audio scales work?]
- [FILL IN: What conditioning methods work?]

**Numerical but Invisible:**
- [FILL IN: What changes are numerically present but visually irrelevant?]
- [FILL IN: Why might they be invisible?]
- [FILL IN: What could make them visible?]

---

## 5. Hypothesis Refinement

### Original Hypothesis

[FILL IN: What was the original hypothesis from PRD?]

### Refined Hypothesis (Based on Analysis)

[FILL IN: How has the hypothesis changed based on reference artifacts?]

**Supporting Evidence:**
- [FILL IN: Evidence 1]
- [FILL IN: Evidence 2]
- [FILL IN: Evidence 3]

**Contradicting Evidence:**
- [FILL IN: Evidence 1]
- [FILL IN: Evidence 2]

---

## 6. Recommendations for Net Expansion

### Architecture Recommendations

1. **Start with:** [FILL IN: Which architecture to start with?]
   - Reason: [FILL IN]

2. **Scale to:** [FILL IN: What scale to test?]
   - Reason: [FILL IN]

3. **Avoid:** [FILL IN: What to avoid?]
   - Reason: [FILL IN]

---

### Audio Conditioning Recommendations

1. **Primary method:** [FILL IN: Which method to try first?]
   - Reason: [FILL IN]

2. **Secondary method:** [FILL IN: Which method to try second?]
   - Reason: [FILL IN]

3. **Audio scale range:** [FILL IN: What range to test?]
   - Reason: [FILL IN]

---

### Training Recommendations

1. **Loss weights:** [FILL IN: Recommended loss weights]
   - Reason: [FILL IN]

2. **Temporal schedule:** [FILL IN: Recommended schedule]
   - Reason: [FILL IN]

3. **Training resolution:** [FILL IN: Recommended resolution]
   - Reason: [FILL IN]

---

## 7. Open Questions

1. [FILL IN: Question 1]
2. [FILL IN: Question 2]
3. [FILL IN: Question 3]

---

## 8. Next Steps

Based on this analysis, the next steps are:

1. [FILL IN: Step 1]
2. [FILL IN: Step 2]
3. [FILL IN: Step 3]

---

**Analysis Complete:** [FILL IN DATE]  
**Ready for:** Baseline establishment (Phase 2)
