---
title: reactive_tuning experiment
updated: 2025-12-11
---

Purpose
- Hold audio-reactivity focused SIREN runs with higher temporal/audio coupling.

How to run (10–20s diagnostic, 480p/720p)
- Baseline: `python Code/backend/clip_optimize_siren.py --prompt "<<<prompt>>>" --audio "<<<audio>>>" --output-dir Code/backend/experiments/siren_search/reactive_tuning --run-name diag_base --depth 3 --width 12 --w0-first 40 --w0-hidden 6 --w0-time 3 --steps 400 --train-resolution 256 --clip-model ViT-B/16 --num-crops 8 --clip-weight 1.6 --temp-weight 0.5 --tv-weight 5e-5 --range-weight 2e-4 --audio-scale 0.05`
- Boosted audio: same as baseline but `--run-name diag_audio015 --audio-scale 0.15 --enable-audio-film --audio-film-hidden 32 --audio-film-scale 1.0 --enable-audio-gate --audio-gate-scale 1.0`
- Optional sharpen: raise `--w0-first 50` or `--w0-hidden 10` if shapes look too smooth (may add ringing).

What to compare
- Visual delta between `audio-scale 0.05` vs `0.15` using identical seed/run-name pair.
- Temporal motion vs flicker: if too smooth, lower `--tv-weight`; if too flickery, reduce `--w0-hidden` or `--w0-time`.

Notes
- Audio features are min-max normalized; raising `--audio-scale` and enabling the audio FiLM branch/gate should noticeably increase responsiveness.
- CLIP crops/views (`--num-crops 8`, `--clip-weight 1.6`) are set higher for structure; lower them if over-constrained.

After-run logging (pairwise comparison)
- Render two runs with the same prompt/seed: `diag_base` (audio-scale 0.05) and `diag_audio015` (audio-scale 0.15 + audio FiLM/gate).
- Record: which is more reactive, presence of flicker, shape sharpness, and any ringing artifacts.
- If boosted run wins without artifacts, promote audio-scale 0.15 + audio FiLM/gate as default for this prompt/audio combo.
