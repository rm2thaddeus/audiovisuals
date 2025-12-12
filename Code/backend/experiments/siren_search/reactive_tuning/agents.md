---
title: reactive_tuning agents
phase: 3
artifact: agents
project: siren_search_reactive
owner: Aitor Patiño Diaz
updated: 2025-12-11
sources:
  - ../../../../../docs/Phase3-MVP/PRD_SIREN_INR.md
  - ../README.md
---

# Purpose
- Track reactive SIREN tuning experiments and record which configs respond best to audio while maintaining structure.

# Latest findings (2025-12-11)
- Prompt used: “galaxy filled with dense points, starfield particles, high particle count”.
- Audio is muxed in all previews via `VideoEncoder`; ffmpeg is required on PATH.
- Baseline (3×12, w0_first=40, w0_hidden=6, w0_time=3) remains the strongest on CLIP similarity; new configs offer variants to inspect for motion/particle density.

# Recent runs (Pot track)
- `diag_base_cosmic_particles` (3×12, w0_first=40, w0_hidden=6, w0_time=3): best sim 0.2703, preview `diag_base_cosmic_particles_preview.mp4`.
- `arch_d4w12_pot` (4×12, w0_first=50, w0_hidden=5, w0_time=2.5): best sim 0.2642, preview `arch_d4w12_pot_preview.mp4`.
- `arch_d3w16_pot` (3×16, w0_first=50, w0_hidden=8, w0_time=2): best sim 0.2666, preview `arch_d3w16_pot_preview.mp4`.
- All artifacts live in this folder (`*_siren.pth`, `*_history.json`, `*_preview.mp4`).

# How to rerun or extend
- Train: `python Code/backend/clip_optimize_siren.py --prompt "<prompt>" --audio "<audio>" --output-dir Code/backend/experiments/siren_search/reactive_tuning --run-name <name> --depth <d> --width <w> --w0-first <f0> --w0-hidden <fh> --w0-time <ft> --steps 320-400 --train-resolution 256 --clip-model ViT-B/16 --num-crops 8 --clip-weight 1.6 --temp-weight 0.5 --tv-weight 5e-5 --range-weight 2e-4 --audio-scale 0.05`
- Render with audio muxed: `python Code/backend/experiments/siren_search/reactive_tuning/render_siren_checkpoint.py --checkpoint <name>_siren.pth --output <name>_preview.mp4 --fps 30 --width 1280 --height 720`
- If visuals are too smooth: raise `w0_first` (40→50) or `w0_hidden` slightly; if flicker appears, lower `w0_hidden` or `w0_time` and raise `temp_weight`.
- To boost audio coupling further, increase `--audio-scale` (e.g., 0.1–0.2) and enable `--enable-audio-film` + `--enable-audio-gate`.

# Next suggested probes
- Re-evaluate previews for motion/particle density; pick between 3×12 baseline vs 3×16 width for richness vs stability.
- Try a high-crop variant (`--num-crops 10`, `--clip-weight 1.2`) to reduce over-sharpening if CLIP pushes artifacts.
- Run a Zyryab sweep mirroring the two alt configs to see if responsiveness generalizes.
