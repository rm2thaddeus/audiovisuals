---
phase: 3
artifact: notes
project: SIREN Text-Conditioned INR Generator
owner: Aitor
updated: 2025-12-10
links:
  prd: ./PRD_SIREN_INR.md
---

# SIREN INR Implementation Notes

## Components (Code/backend/)
- `siren_inr.py` – SIREN + FiLM (text + audio) with SIREN init (w0_first/w0_hidden, optional w0_time).
- `clip_optimize_siren.py` – CLIP-guided trainer (multi-crop, temporal loss, TV, range clamp, optional AMP). Saves checkpoints with metadata.
- `siren_cli.py` – Rendering entrypoint (audio + prompt + weights) with batch rendering and timing.
- `experiments/siren_search/`
  - `run_grid.py` – Tiny-grid sweep runner (depth/width/w0_first/w0_hidden) with summary CSV/JSON.
  - `flicker_metric.py` – Mean |frame diff| metric from MP4.
  - `clip_score_eval.py` – CLIP text-image score on sampled video frames.

## Training (CLIP-guided)
```bash
python Code/backend/clip_optimize_siren.py \
  --prompt "organic nebula" \
  --audio "docs/Audio/TOOL - The Pot (Audio).mp3" \
  --output-dir Code/backend/experiments/siren_search \
  --run-name nebula_tiny \
  --depth 3 --width 8 \
  --w0-first 30 --w0-hidden 1 \
  --steps 500 --train-resolution 256 \
  --clip-model ViT-B/32 --num-crops 6 --amp
```
- Losses: CLIP (multi-crop), temporal L2 (Δ in [1/24, 1/12]), TV, range clamp.
- Conditioning: text embedding + per-frame audio features (normalized, scaled by `--audio-scale`, default 0.05).
- Outputs: `<run>_siren.pth` + `<run>_history.json` in `output-dir`.

## Rendering
```bash
python Code/backend/siren_cli.py input.mp3 output.mp4 \
  --prompt "organic nebula" \
  --load-weights Code/backend/experiments/siren_search/nebula_tiny_siren.pth \
  --resolution 1080p --fps 60 \
  --clip-model ViT-B/32 \
  --depth 3 --width 8 --w0-first 30 --w0-hidden 1
```
- Uses FiLM with text+audio; batch size auto-tuned (override with `--batch-size`).
- Outputs realtime speed estimate and MP4.

## Search + Evaluation
```bash
# Tiny grid sweep
python Code/backend/experiments/siren_search/run_grid.py \
  --prompt "organic nebula" --audio docs/Audio/TOOL - The Pot (Audio).mp3 \
  --steps 200 --train-resolution 256 --clip-model ViT-B/32

# Flicker metric
python Code/backend/experiments/siren_search/flicker_metric.py run.mp4 --resize 256

# CLIP parity vs prompt
python Code/backend/experiments/siren_search/clip_score_eval.py run.mp4 \
  --prompt "organic nebula" --clip-model ViT-B/32 --samples 8
```
- Sweep results: `summary.csv`/`summary.json` under `experiments/siren_search/`.

## Desktop bridge (Tauri)
- `generate_video` command now accepts `engine="siren"` plus `prompt`, `clip_model`, `weights_path`, `depth`/`width`/`w0_time`.
- `engine="cppn"` continues to call `cli.py` unchanged; `engine="siren"` invokes `siren_cli.py`.

## Defaults & Backbones
- Backbones: ViT-B/32 (default), ViT-B/16 supported.
- Tiny grid (preferred): depth {2,3,4}, width {4,6,8,12}, w0_first {30,50}, w0_hidden {1,10}.
- Output activation: tanh → [-1,1] (renderer rescales to [0,1]).

