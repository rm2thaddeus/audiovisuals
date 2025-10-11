# CPPN Parameter Exploration Results

**Date:** 2025-10-11  
**Audio:** TOOL - The Pot  
**Total Videos:** 12 variations

---

## What Was Generated

### Audio Segments (10 seconds each)

1. **Start (30s-40s)** - Beginning section
2. **Quiet (0s-10s)** - Quiet/calm section  
3. **Intense (364s-374s)** - Loud/intense section

### CPPN Variations (4 per segment)

| Preset | Layers | Hidden Dim | Audio Scale | Evolve | Description |
|--------|--------|------------|-------------|--------|-------------|
| **simple** | 3 | 128 | 0.05 | 0.0 | Simple patterns |
| **reactive** | 4 | 256 | 0.15 | 0.0 | Strong audio response |
| **complex** | 6 | 256 | 0.05 | 0.0 | Complex structures |
| **evolving** | 4 | 256 | 0.08 | 0.005 | Living patterns |

---

## Files Generated

### Videos (12 total)

**Start Segment:**
- `start_simple.mp4` - Simple, flowing patterns
- `start_reactive.mp4` - Strong audio reactivity
- `start_complex.mp4` - 6-layer complexity
- `start_evolving.mp4` - Evolving weights

**Quiet Segment:**
- `quiet_simple.mp4` - Simple, flowing patterns
- `quiet_reactive.mp4` - Strong audio reactivity
- `quiet_complex.mp4` - 6-layer complexity
- `quiet_evolving.mp4` - Evolving weights

**Intense Segment:**
- `intense_simple.mp4` - Simple, flowing patterns
- `intense_reactive.mp4` - Strong audio reactivity
- `intense_complex.mp4` - 6-layer complexity
- `intense_evolving.mp4` - Evolving weights

### Audio Clips
- `segments/TOOL - The Pot (Audio)_start_10s.wav`
- `segments/TOOL - The Pot (Audio)_quiet_10s.wav`
- `segments/TOOL - The Pot (Audio)_intense_10s.wav`

### Comparison Page
- **`comparison.html`** - View all videos side-by-side

---

## How to Review

### Option 1: HTML Comparison (Recommended)
```
Open: comparison.html in your web browser
```

All 12 videos displayed in a grid:
- Organized by segment (start, quiet, intense)
- Each variation shown with parameters
- Easy side-by-side comparison

### Option 2: Individual Videos
Watch each video directly:
- Resolution: 360p (fast generation)
- FPS: 24
- Duration: 10 seconds each

---

## What to Look For

### 1. Pattern Complexity
- **Simple (3 layers):** Clean, flowing shapes
- **Complex (6 layers):** Intricate geometric patterns
- Which feels right for this music?

### 2. Audio Reactivity
- **Reactive (0.15 scale):** Strong response to audio
- **Simple/Complex (0.05 scale):** Subtle response
- Does it match the music's energy?

### 3. Evolution Effect
- **Evolving:** Patterns slowly morph over time
- **Static:** Patterns stay consistent
- Is the drift interesting or distracting?

### 4. Segment Characteristics
- **Start:** How do patterns work with the intro?
- **Quiet:** Do visuals complement calm parts?
- **Intense:** Do they match the energy?

---

## Next Steps

### 1. Give Feedback
Note which variations you like:
- Which preset works best? (simple/reactive/complex/evolving)
- Which segment shows it best?
- What would you change?

### 2. Test More Parameters
Based on what you liked, try variations:
```bash
# If you liked "reactive", try similar configs
python cli.py audio.mp3 test.mp4 --layers 4 --audio-scale 0.12

# If you liked "complex", try more layers
python cli.py audio.mp3 test.mp4 --layers 7 --hidden-dim 256

# If you liked "evolving", try different evolution rates
python cli.py audio.mp3 test.mp4 --layers 4 --evolve 0.008
```

### 3. Full Track Render
Once you find a favorite configuration, render the full track:
```bash
python cli.py "../../docs/Audio/TOOL - The Pot (Audio).mp3" final.mp4 \
    --resolution 720p \
    --fps 30 \
    --layers [YOUR_CHOICE] \
    --hidden-dim [YOUR_CHOICE] \
    --audio-scale [YOUR_CHOICE] \
    --evolve [YOUR_CHOICE]
```

---

## Technical Notes

### Why These Segments?
- **Start:** Shows how patterns establish themselves
- **Quiet:** Tests subtle, calm visualization
- **Intense:** Tests dynamic, energetic response

### Why These Presets?
- **Simple:** Baseline - clean and clear
- **Reactive:** Maximum audio response
- **Complex:** Maximum detail/complexity
- **Evolving:** Adds temporal variation

### Untrained Network
Remember: All patterns are from **random initialization**!
- No learned aesthetics
- Colors/shapes are mathematical artifacts
- Different runs = completely different patterns
- You're finding "happy accidents"

---

## Feedback Template

**Favorite Overall:**
- Segment: [start/quiet/intense]
- Preset: [simple/reactive/complex/evolving]
- Why: [what did you like?]

**Least Favorite:**
- Segment: [start/quiet/intense]
- Preset: [simple/reactive/complex/evolving]
- Why: [what didn't work?]

**Suggestions:**
- More/less complexity?
- More/less audio reactivity?
- Colors interesting?
- Evolution useful?

---

**Exploration Complete!**  
Review `comparison.html` to see all results side-by-side.

