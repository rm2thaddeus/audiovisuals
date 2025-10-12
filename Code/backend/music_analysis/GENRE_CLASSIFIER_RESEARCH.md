# Genre Classifier Research - Phase B+

**Date:** 2025-10-11  
**Status:** Research phase - evaluating pre-trained models  
**Question:** Can we find a pre-trained PyTorch genre classifier?

---

## Research Findings

### Pre-Trained Models Available

**1. HuggingFace: storylinez/audio-genre-classifier** ⭐
- **Framework:** PyTorch
- **Dataset:** GTZAN (10 genres)
- **Genres:** blues, classical, country, disco, hiphop, jazz, metal, pop, reggae, rock
- **Accuracy:** ~85% on GTZAN test set
- **Status:** Pre-trained, downloadable
- **Link:** https://huggingface.co/storylinez/audio-genre-classifier

**How to use:**
```python
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import torchaudio

model = AutoModelForAudioClassification.from_pretrained("storylinez/audio-genre-classifier")
feature_extractor = AutoFeatureExtractor.from_pretrained("storylinez/audio-genre-classifier")

# Load and preprocess audio
waveform, sr = torchaudio.load("audio.mp3")
inputs = feature_extractor(waveform, sampling_rate=sr, return_tensors="pt")

# Get predictions
with torch.no_grad():
    logits = model(**inputs).logits
    predicted_class = logits.argmax(-1).item()
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
```

**Dependencies:**
```
transformers>=4.30.0
torchaudio>=2.0.0
```

**Estimated implementation time:** 2-3 hours
- Download model (~100MB)
- Create analyzer wrapper
- Implement CLI command
- Add visualization
- Test with sample audio

---

**2. MAEST (Music Audio Efficient Spectrogram Transformer)**
- **Framework:** PyTorch
- **Type:** Transformer-based
- **Status:** Pre-trained on large music dataset
- **More advanced:** Better accuracy but more complex
- **Estimated time:** 3-4 hours

---

**3. Custom PyTorch CNN (Train from Scratch)**
- **Dataset:** GTZAN (1000 songs, ~1.2GB)
- **Architecture:** Simple CNN on mel-spectrograms
- **Training time:** 2-4 hours on RTX 5070
- **Total time:** 6-8 hours (download + train + integrate)
- **Not recommended:** Too time-intensive for POC

---

## Recommendation

### Option A: Implement HuggingFace Model ✅ RECOMMENDED

**Pros:**
- ✅ Pre-trained and ready
- ✅ PyTorch-based (no TensorFlow)
- ✅ Standard 10 genres (GTZAN)
- ✅ Easy HuggingFace integration
- ✅ ~85% accuracy
- ✅ Fast inference (~2-5s per song)

**Cons:**
- ⚠️ Requires `transformers` library (~500MB with deps)
- ⚠️ Model download ~100MB
- ⚠️ Limited to 10 GTZAN genres

**Implementation checklist:**
- [ ] Install transformers and torchaudio
- [ ] Create `analyzers/genre_classifier.py`
- [ ] Download and test model
- [ ] Implement CLI command
- [ ] Create visualization (pie chart, bar chart)
- [ ] Add HTML generation
- [ ] Test with sample audio
- [ ] Update documentation

**Estimated time:** 2-3 hours

---

### Option B: Feature-Based Genre Heuristics (Quick Alternative)

If model download fails or is too large, implement simple heuristics:

```python
def estimate_genre(tempo, key, chord_complexity, spectral_features):
    """
    Simple genre estimation based on extracted features.
    
    Not ML-based, but provides reasonable estimates.
    """
    # Rock: 110-140 BPM, power chords, high energy
    # Classical: Variable tempo, complex harmony, full spectrum
    # Electronic: 120-140 BPM, simple harmony, high treble
    # Jazz: Complex chords, swing rhythm, mid-range focus
    # Metal: Fast tempo (140+), minor keys, high distortion
    # etc.
    
    scores = {
        'rock': calculate_rock_score(tempo, key, chords, spectral),
        'electronic': calculate_electronic_score(...),
        'classical': calculate_classical_score(...),
        # ... etc
    }
    
    return max(scores, key=scores.get)
```

**Pros:**
- ✅ No model download
- ✅ Fast implementation (1 hour)
- ✅ Uses existing features

**Cons:**
- ❌ Lower accuracy (~50-60%)
- ❌ Requires manual rule tuning
- ❌ Less robust

**Estimated time:** 1 hour

---

## Decision Point

**Question for user:**

1. **Implement HuggingFace pre-trained model?** (2-3 hours, ~85% accuracy)
   - Requires transformers library
   - Model download ~100MB
   - Proper ML classification

2. **Simple heuristic classifier?** (1 hour, ~50-60% accuracy)
   - Uses existing features
   - No downloads
   - Good enough for POC

3. **Skip genre for now?** (0 hours)
   - Already have 4 excellent analyzers
   - Can add later if needed

---

## Technical Notes

### GTZAN Genre Dataset

**10 Genres:**
1. Blues
2. Classical
3. Country
4. Disco
5. Hip-hop
6. Jazz
7. Metal
8. Pop
9. Reggae
10. Rock

**Limitations:**
- Western music focus
- Limited electronic sub-genres
- No modern genres (trap, lo-fi, etc.)
- Dated dataset (2000s music)

### Modern Alternatives

For more comprehensive genre classification, would need:
- **Million Song Dataset** models (500+ genres)
- **Spotify API** genre tags (requires API key)
- **Custom training** on modern music datasets

---

## Status

**Current:** Research complete, models identified  
**Decision needed:** Which implementation approach?  
**Blocker:** None - can proceed with HuggingFace model  
**Timeline:** 2-3 hours if approved

---

**Updated:** 2025-10-11  
**Next:** Await decision on implementation approach

