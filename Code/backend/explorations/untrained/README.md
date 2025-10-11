# Untrained Parameter Explorations

Random weight parameter exploration results - discovering "happy accidents" from untrained networks.

## What This Is

These are **untrained CPPN networks** with random initialization. The patterns you see are mathematical artifacts from:
- Random weight initialization
- Different network architectures (layers, dimensions)
- Audio feature injection
- Weight evolution over time

**No learning happened** - these are pure mathematical pattern generators responding to audio.

## Exploration Runs

Each `quick_TIMESTAMP/` directory contains:
- **comparison.html** - View all results side-by-side
- **segments/** - Test audio clips (10s each)
- **12 videos** - 3 audio segments × 4 CPPN presets

## The 4 Presets

| Preset | Config | What You See |
|--------|--------|--------------|
| **simple** | 3 layers, 128 dim, audio=0.05 | Clean, flowing patterns |
| **reactive** | 4 layers, 128 dim, audio=0.15 | Strong audio response |
| **complex** | 5 layers, 256 dim, audio=0.08 | Intricate structures |
| **evolving** | 4 layers, 128 dim, audio=0.10, evolve=0.02 | Living/morphing patterns |

## Why Explore Untrained Networks?

1. **Fast iteration** - No training needed (instant results)
2. **Parameter discovery** - Find which architectures produce interesting patterns
3. **Audio reactivity testing** - See how different scales affect visuals
4. **Color variety** - Every run has different random colors
5. **"Happy accidents"** - Sometimes random is beautiful!

## How to Use These Results

1. **Review comparison.html** in each directory
2. **Note which presets you like** and why
3. **Identify patterns** - What layer counts, dimensions work?
4. **Inform next steps**:
   - Use liked parameters for full renders
   - Use as baseline for CLIP optimization
   - Understand what kind of patterns the network can make

## Limitations

- ❌ No aesthetic control (colors are random)
- ❌ No consistency between runs (different random seeds)
- ❌ No semantic understanding of music
- ✅ BUT: Fast, varied, and sometimes surprisingly good!

## Tools

- **quick_explore.py** - Automated exploration generator
- **PARAMETER_EXPLORATION_GUIDE.md** - Complete parameter guide
- **QUICK_TESTS.md** - Manual testing commands

---

**Purpose**: Find promising parameter configurations before investing in training

