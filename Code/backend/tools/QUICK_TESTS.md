# Quick Parameter Tests - Copy/Paste Commands

Ready-to-run commands for exploring different CPPN configurations.

---

## Available Audio

```
../../docs/Audio/TOOL - The Pot (Audio).mp3  (6.4 minutes)
../../docs/Audio/Zyryab.mp3                  (variable length)
```

---

## Fast Tests (10-15 second clips, 360p)

### Cut a Test Segment First
```bash
# Using existing test audio
set INPUT=test_audio.wav

# Or cut a new segment (requires ffmpeg)
ffmpeg -i "../../docs/Audio/TOOL - The Pot (Audio).mp3" -ss 60 -t 15 test_15s.mp3
set INPUT=test_15s.mp3
```

### Test 1: Simple & Clean
```bash
python cli.py %INPUT% test_simple.mp4 ^
    --resolution 360p ^
    --fps 24 ^
    --layers 3 ^
    --hidden-dim 128 ^
    --audio-scale 0.05
```

### Test 2: Reactive
```bash
python cli.py %INPUT% test_reactive.mp4 ^
    --resolution 360p ^
    --fps 24 ^
    --layers 4 ^
    --hidden-dim 256 ^
    --audio-scale 0.15
```

### Test 3: Complex Patterns
```bash
python cli.py %INPUT% test_complex.mp4 ^
    --resolution 360p ^
    --fps 24 ^
    --layers 6 ^
    --hidden-dim 256 ^
    --audio-scale 0.08
```

### Test 4: Living/Evolving
```bash
python cli.py %INPUT% test_evolving.mp4 ^
    --resolution 360p ^
    --fps 24 ^
    --layers 4 ^
    --hidden-dim 256 ^
    --audio-scale 0.08 ^
    --evolve 0.005
```

---

## Single Full Track Tests (Faster Preview)

### TOOL - Organic Style
```bash
python cli.py "../../docs/Audio/TOOL - The Pot (Audio).mp3" tool_organic.mp4 ^
    --resolution 480p ^
    --fps 24 ^
    --layers 4 ^
    --hidden-dim 256 ^
    --audio-scale 0.05
```

### TOOL - Reactive Style
```bash
python cli.py "../../docs/Audio/TOOL - The Pot (Audio).mp3" tool_reactive.mp4 ^
    --resolution 480p ^
    --fps 24 ^
    --layers 5 ^
    --hidden-dim 256 ^
    --audio-scale 0.12
```

### Zyryab - Flowing Style
```bash
python cli.py "../../docs/Audio/Zyryab.mp3" zyryab_flowing.mp4 ^
    --resolution 480p ^
    --fps 24 ^
    --layers 3 ^
    --hidden-dim 256 ^
    --audio-scale 0.06 ^
    --evolve 0.002
```

---

## High Quality Finals (After Finding Favorites)

### Best Configuration @ 720p
```bash
python cli.py "../../docs/Audio/TOOL - The Pot (Audio).mp3" final_720p.mp4 ^
    --resolution 720p ^
    --fps 30 ^
    --layers 4 ^
    --hidden-dim 256 ^
    --audio-scale 0.08 ^
    --evolve 0.003
```

### Best Configuration @ 1080p
```bash
python cli.py "../../docs/Audio/TOOL - The Pot (Audio).mp3" final_1080p.mp4 ^
    --resolution 1080p ^
    --fps 30 ^
    --layers 4 ^
    --hidden-dim 256 ^
    --audio-scale 0.08 ^
    --evolve 0.003
```

---

## Parameter Sweep (One Variable)

### Sweep Audio Scale
```bash
python cli.py %INPUT% scale_03.mp4 --resolution 360p --fps 24 --audio-scale 0.03
python cli.py %INPUT% scale_05.mp4 --resolution 360p --fps 24 --audio-scale 0.05
python cli.py %INPUT% scale_08.mp4 --resolution 360p --fps 24 --audio-scale 0.08
python cli.py %INPUT% scale_12.mp4 --resolution 360p --fps 24 --audio-scale 0.12
python cli.py %INPUT% scale_15.mp4 --resolution 360p --fps 24 --audio-scale 0.15
```

### Sweep Layer Count
```bash
python cli.py %INPUT% layers_2.mp4 --resolution 360p --fps 24 --layers 2
python cli.py %INPUT% layers_3.mp4 --resolution 360p --fps 24 --layers 3
python cli.py %INPUT% layers_4.mp4 --resolution 360p --fps 24 --layers 4
python cli.py %INPUT% layers_6.mp4 --resolution 360p --fps 24 --layers 6
python cli.py %INPUT% layers_8.mp4 --resolution 360p --fps 24 --layers 8
```

### Sweep Evolution Rate
```bash
python cli.py %INPUT% evolve_00.mp4 --resolution 360p --fps 24 --evolve 0.000
python cli.py %INPUT% evolve_02.mp4 --resolution 360p --fps 24 --evolve 0.002
python cli.py %INPUT% evolve_05.mp4 --resolution 360p --fps 24 --evolve 0.005
python cli.py %INPUT% evolve_08.mp4 --resolution 360p --fps 24 --evolve 0.008
python cli.py %INPUT% evolve_10.mp4 --resolution 360p --fps 24 --evolve 0.010
```

---

## Automated Batch
```bash
# Generate all quick tests at once
for %%p in (simple reactive complex evolving) do (
    python cli.py %INPUT% %%p.mp4 --resolution 360p --fps 24 [params]
)
```

---

## Currently Running

The `quick_explore.py` script is generating:
- 3 audio segments (10s each)
- 4 variations per segment
- Total: 12 videos @ 360p

**Check progress:** Look for MP4 files appearing in `explorations/quick_*/`

---

**Tip:** Start with 360p @ 24fps for speed, then re-render favorites at higher quality!

