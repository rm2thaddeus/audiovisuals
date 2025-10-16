# Network Architecture Guide - Phase C

**Status:** 🔬 Active Research  
**Updated:** 2025-10-13  
**Purpose:** Document optimal CPPN architectures for organic biological patterns

---

## Overview

This guide documents the systematic exploration of CPPN network architectures (2-5 layers × 32-128 hidden dimensions) to discover optimal configurations for generating organic biological patterns such as spirals, cells, droplets, and fluid forms.

---

## Research Hypothesis

**Simpler networks (2-5 layers, 32-128 dims) produce better organic patterns than complex networks (8-10 layers, 256+ dims)**

### Rationale

1. **Signal Preservation** - Fewer layers prevent information loss
2. **Activation Efficacy** - Sinusoidal activations work better in shallow networks
3. **Organic Emergence** - Simplicity yields natural complexity
4. **Literature Support** - Stanley 2007, recent CPPN research

---

## Architecture Matrix

### Test Configurations

| Layers | Hidden Dims | Seeds | Total Configs |
|--------|-------------|-------|---------------|
| 2, 3, 4, 5 | 32, 64, 128 | 3 each | 36 videos |

**Total Architectures:** 12 unique (4 layers × 3 dims)  
**Total Samples:** 36 (3 seeds per architecture)

---

## Findings (To Be Updated)

### Top Performing Architectures

*This section will be updated after Week 2 rating is complete*

#### 1. [Architecture Name] - [Overall Score]/5.0

**Configuration:**
- Layers: X
- Hidden dim: X
- Parameters: X,XXX

**Ratings:**
- Organic Quality: X.X/5.0
- Coherence: X.X/5.0
- Audio Reactivity: X.X/5.0
- Aesthetic Appeal: X.X/5.0

**Visual Characteristics:**
- [Description of visual patterns]
- [Notable features]
- [Organic qualities observed]

**Recommended For:**
- [Use cases]

---

### Architecture → Visual Style Mappings

*This section documents observed relationships between architecture and visual output*

#### Layer Count Effects

**2 Layers:**
- Characteristics: [To be documented]
- Organic Quality: [To be documented]
- Best For: [To be documented]

**3 Layers:**
- Characteristics: [To be documented]
- Organic Quality: [To be documented]
- Best For: [To be documented]

**4 Layers:**
- Characteristics: [To be documented]
- Organic Quality: [To be documented]
- Best For: [To be documented]

**5 Layers:**
- Characteristics: [To be documented]
- Organic Quality: [To be documented]
- Best For: [To be documented]

#### Hidden Dimension Effects

**32 Dimensions:**
- Characteristics: [To be documented]
- Pattern Complexity: [To be documented]
- Best For: [To be documented]

**64 Dimensions:**
- Characteristics: [To be documented]
- Pattern Complexity: [To be documented]
- Best For: [To be documented]

**128 Dimensions:**
- Characteristics: [To be documented]
- Pattern Complexity: [To be documented]
- Best For: [To be documented]

---

## Best Practices for Organic Patterns

### Input Features

**Coordinate System:**
```python
# Spatial coordinates
x, y = coordinates  # [-1, 1] range

# Radial coordinates (enhances organic symmetry)
r = np.sqrt(x**2 + y**2)  # Distance from center
theta = np.arctan2(y, x)   # Angle (optional for spirals)

# Input vector: [x, y, r, time, audio_features]
```

**Audio Feature Scaling:**
- Optimal range: 0.05-0.10 for organic patterns
- Higher values (>0.15) may overwhelm spatial structure
- Lower values (<0.03) reduce audio reactivity

### Activation Functions

**Recommended Mix:**
```python
activations = ['sin', 'cos', 'gaussian', 'tanh']
# Alternate per layer for pattern diversity
```

**For Specific Patterns:**
- **Spirals:** Emphasize sin/cos activations
- **Cells/Bubbles:** Gaussian activations dominant
- **Fluid Forms:** Mix of all four types
- **Geometric:** Replace some with ReLU/LeakyReLU

### Weight Initialization

**Critical Parameter:**
```python
# Xavier initialization with high gain
nn.init.xavier_uniform_(layer.weight, gain=5.0)
```

**Why gain=5.0:**
- Prevents signal vanishing through periodic activations
- Maintains temporal variation
- Essential for audio reactivity

---

## Configuration Recipes

### For Spirals

```python
config = {
    'layers': 4,
    'hidden_dim': 128,
    'activations': ['sin', 'cos', 'sin', 'cos'],
    'include_radial': True,  # r = sqrt(x² + y²)
    'include_angular': True,  # theta = atan2(y, x)
    'audio_scale': 0.08
}
```

### For Cellular Patterns

```python
config = {
    'layers': 3,
    'hidden_dim': 64,
    'activations': ['gaussian', 'tanh', 'gaussian'],
    'include_radial': True,
    'include_angular': False,
    'audio_scale': 0.05
}
```

### For Fluid Forms

```python
config = {
    'layers': 4,
    'hidden_dim': 64,
    'activations': ['sin', 'gaussian', 'tanh', 'cos'],
    'include_radial': True,
    'include_angular': False,
    'audio_scale': 0.10
}
```

### For Organic Solvents

```python
config = {
    'layers': 2,
    'hidden_dim': 128,
    'activations': ['sin', 'tanh'],
    'include_radial': True,
    'include_angular': False,
    'audio_scale': 0.06
}
```

---

## CLIP Training Prompts (Week 3)

### Biology-Focused Prompts

```python
ORGANIC_PROMPTS = [
    # Cellular
    "organic flowing cellular structures with spiral patterns",
    "biological cell division with radial symmetry",
    "organic shapes resembling microorganisms under microscope",
    
    # Fluid Dynamics
    "biological droplets and bubbles with soft membranes",
    "microscopic organic solvents with fluid dynamics",
    "fluid biological forms with gentle gradients",
    
    # Patterns
    "spiral patterns in nature like shells and galaxies",
    "organic branching structures like neurons or blood vessels",
    "flowing organic patterns resembling natural processes"
]
```

### Expected Outcomes

**128 dim vs 256 dim:**
- Previous CLIP training showed 128 dim outperformed 256 dim
- Expect similar results with even smaller networks
- Hypothesis: 64-128 dim optimal for organic aesthetics

---

## Performance Metrics

### Inference Speed (RTX 5070)

*To be updated with actual measurements*

| Architecture | Pixels/sec | FPS @ 720p | Relative Speed |
|--------------|-----------|------------|----------------|
| 2L × 32D | TBD | TBD | TBD |
| 3L × 64D | TBD | TBD | TBD |
| 4L × 128D | TBD | TBD | TBD |
| 5L × 128D | TBD | TBD | TBD |

**Current Baseline:** 4L × 256D = 249M pixels/sec, 52+ FPS @ 720p

**Hypothesis:** Smaller networks will be faster (fewer parameters)

---

## MVP Integration Plan

### Option A: Simple Presets (Recommended)

**UI Design:**
```
Style Presets:
[Organic Cells]  [Spiral Flow]  [Fluid Droplets]  [Microorganisms]

Hidden: Network architecture (4L × 64D, etc.)
User sees: Visual style names only
```

**Implementation:**
```python
PRESET_ARCHITECTURES = {
    'organic_cells': {'layers': 3, 'hidden_dim': 64},
    'spiral_flow': {'layers': 4, 'hidden_dim': 128},
    'fluid_droplets': {'layers': 2, 'hidden_dim': 128},
    'microorganisms': {'layers': 4, 'hidden_dim': 64}
}
```

### Option B: Advanced Controls (Future)

**UI Design:**
```
Network Architecture (Advanced)
  Layers:      [▓▓▓▓░░] 4
  Hidden Dim:  [▓▓▓░░░] 128
  [Preview] [Reset to Preset]
```

**For Power Users:**
- Real-time parameter adjustment
- Immediate preview
- Save custom configurations

---

## Week-by-Week Progress

### ✅ Week 1: Architecture Matrix Testing

**Goal:** Generate 36 test videos (12 configs × 3 seeds)

**Tools Created:**
- `explore_architectures.py` - Automated testing script
- CLI updated with `--seed` and `--duration` arguments

**Deliverable:** `Code/backend/explorations/architecture_matrix/[timestamp]/`

### 🔬 Week 2: Visual Catalog & Rating (In Progress)

**Goal:** Rate all videos, create architecture catalog

**Tools Created:**
- `rate_architectures.py` - Interactive rating tool
- Rating categories: Organic, Coherence, Reactivity, Aesthetic

**Deliverable:** `ARCHITECTURE_CATALOG.md` with ranked results

### 📋 Week 3: CLIP Training (Planned)

**Goal:** Train top 3-5 architectures with organic prompts

**Tools:** Existing `clip_optimize_cppn.py`

**Deliverable:** 9+ trained styles in `Code/backend/styles/organic/`

### 📄 Week 4: Documentation & Integration (Planned)

**Goal:** Finalize guide, update POC plan, prepare MVP

**Deliverable:** Complete architecture guide, MVP integration specs

---

## References

### Literature

1. **Stanley, Kenneth O.** (2007). "Compositional pattern producing networks: A novel abstraction of development." *Genetic programming and evolvable machines*, 8(2), 131-162.

2. **CLIP** (2021). "Learning Transferable Visual Models From Natural Language Supervision." OpenAI.

3. **CPPN Research**: Various online tutorials and implementations showing smaller networks produce complex patterns.

### Internal Documentation

- `docs/Phase2-POC/POC_PLAN.md` - Phase C section
- `Code/backend/AGENTS.md` - Current architecture
- `docs/Phase2-POC/backend/CURRENT_STATE.md` - Baseline status
- `docs/Phase2-POC/backend/PHASE_A_IMPLEMENTATION.md` - Implementation details

---

## Next Steps

1. **Complete Week 2 Rating** - Rate all 36 videos, identify winners
2. **Select Top Architectures** - Choose 3-5 for CLIP training
3. **Prepare Organic Prompts** - Refine biology-focused prompts
4. **Run CLIP Training** - Optimize winners with organic aesthetics
5. **Compare Results** - Random vs CLIP-trained quality
6. **Document Findings** - Update this guide with results
7. **Define MVP Presets** - Create preset system for desktop app

---

**Status:** Active Research - Week 1 Complete, Week 2 In Progress  
**Updated:** 2025-10-13  
**Phase:** C - Network Architecture & Visual Interpretation



