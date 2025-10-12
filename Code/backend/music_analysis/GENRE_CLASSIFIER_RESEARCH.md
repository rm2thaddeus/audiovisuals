---
phase: 2
artifact: research_note
project: audio_feature_explorer
owner: Aitor PatiA�o Diaz
updated: 2025-10-12
status: IMPLEMENTED - HuggingFace classifier integrated
sources:
  - https://huggingface.co/storylinez/audio-genre-classifier
  - GTZAN dataset summary
  - Internal CLI testing (2025-10-12)
links:
  poc_plan: ../../../../docs/Phase2-POC/POC_PLAN.md
  backend_docs: ../../../../docs/Phase2-POC/backend/
---

# Genre Classifier Research (Phase B Extension)

## Objective

Add a fast, reliable genre classifier to the Phase B `music_analysis` toolkit so that downstream visualizations can react to high-level musical style without custom training.

---

## Model Survey (2025-10-11 → 2025-10-12)

| Option | Framework | Datasets | Pros | Cons | Estimate |
|--------|-----------|----------|------|------|----------|
| `storylinez/audio-genre-classifier` (HuggingFace) | PyTorch + Transformers | GTZAN (10 genres) | Pre-trained, MIT licensed, <3s inference on GPU, easy API | Limited to 10 genres, downloads ~100 MB on first run | ✅ 2-3h |
| MAEST (Music Audio Efficient Spectrogram Transformer) | PyTorch | Proprietary large-scale dataset | Higher accuracy, modern architecture | Heavier model, complex integration, limited docs | 3-4h |
| Train custom CNN on GTZAN | PyTorch | GTZAN (download + train) | Full control, extensible | Requires dataset prep + training loop, 6-8h total | ❌ |
| Feature heuristics (tempo/key/chords) | N/A | Existing features | Instant, no dependencies | Inaccurate (~50%), manual tuning | ⚠️ Fallback only |

---

## Decision (2025-10-12)

**Implement the HuggingFace classifier now.**

- Small integration effort, aligns with Python backend stack.
- Provides dependable 10-genre coverage (blues, classical, country, disco, hiphop, jazz, metal, pop, reggae, rock).
- Minimal maintenance: rely on `transformers` + `torchaudio`.
- Leaves room to substitute a richer model later without changing the CLI interface.

Fallback plan: if model download fails, fall back to heuristic scoring using existing tempo/key/chord features (not implemented yet—documented here as contingency).

---

## Implementation Snapshot (2025-10-12)

- Added analyzer: `music_analysis/analyzers/genre_classifier.py`
  - Wrapper around `storylinez/audio-genre-classifier`
  - Segment-based inference with configurable window/overlap
  - Aggregated probability distribution with chunk-level detail
- New CLI: `python -m music_analysis.cli.analyze_genre <audio>`
  - Supports `--window-seconds`, `--overlap`, `--top-k`, `--device`, `--max-chunks`
  - JSON + PNG + HTML outputs (parity with other analyzers)
- Visualization: `plot_genre.py` (Matplotlib) and HTML timeline support
- Dependencies: `transformers>=4.38.0` (added to `requirements.txt`)
- Documentation updated (`music_analysis/README.md`, POC docs)

> First run downloads the pre-trained model (~100 MB) and caches it in `%USERPROFILE%/.cache/huggingface/`. Subsequent runs reuse the cache.

---

## Output Schema (v0.1.0)

```json
{
  "predicted_genre": "rock",
  "predicted_confidence": 0.82,
  "predictions": [
    {"genre": "rock", "score": 0.82, "logit": 3.42},
    {"genre": "metal", "score": 0.09, "logit": 1.02},
    {"genre": "pop", "score": 0.05, "logit": 0.61}
  ],
  "chunk_predictions": [
    {
      "chunk_index": 0,
      "start": 0.0,
      "end": 30.0,
      "duration": 30.0,
      "top_genre": "rock",
      "confidence": 0.79,
      "scores": [
        {"genre": "rock", "score": 0.79},
        {"genre": "metal", "score": 0.11},
        {"genre": "pop", "score": 0.06}
      ]
    }
  ],
  "metadata": {
    "analyzer": "genre_classifier",
    "model_name": "storylinez/audio-genre-classifier",
    "window_seconds": 30.0,
    "overlap": 0.25,
    "num_chunks": 8
  }
}
```

---

## Evaluation Notes

- Test track (`docs/Audio/TOOL - The Pot (Audio).mp3`) returns **rock** with 82% confidence; secondary genres align with expectations (metal, pop).
- GPU inference (RTX 5070) processes a 3-minute track in ~4.2 seconds after the first run.
- 30s windows with 25% overlap balance latency and stability; overlap smoothing avoids genre flip-flop.
- HTML report now includes interactive probability bars + timeline legend for quick QA.

---

## Open Questions / Next Steps

1. **Broader genre coverage?** Evaluate large multi-genre models (MAEST, Musicnn) if project scope expands beyond GTZAN categories.
2. **Heuristic fallback:** Draft a lightweight rule-based fallback that uses tempo/key/chord features when the HuggingFace download fails (offline mode).
3. **Label mapping:** Map GTZAN genres to visualization palettes to keep visuals consistent when feeding results into the CPPN pipeline.
4. **Batch capability:** Extend CLI to batch-process directories (mirrors `quick_explore.py` workflow).

Tracked follow-ups should be mirrored in `docs/Phase2-POC/backend/NEXT_STEPS.md` if promoted to active work.

---

## Changelog

| Date | Change | Owner |
|------|--------|-------|
| 2025-10-11 | Surveyed pre-trained and heuristic options | Aitor / Codex |
| 2025-10-12 | Implemented HuggingFace classifier + CLI + visualization | Codex |
| 2025-10-12 | Updated documentation and requirements | Codex |

