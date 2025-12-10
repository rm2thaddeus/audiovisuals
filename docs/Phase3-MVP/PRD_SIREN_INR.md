---
phase: 3
artifact: prd
project: SIREN Text-Conditioned INR Generator (Alt to CPPN)
owner: Aitor
updated: 2025-12-10
sources:
  - ./docs/Phase2-POC/ARCHITECTURE_CATALOG.md
  - ./docs/Phase2-POC/COMPLETE_IMPLEMENTATION_REPORT.md
  - ./docs/explorations/clip_organic_20251011/COMPARISON_RESULTS.md
  - ./docs/Phase3-MVP/ARCHITECTURE_INTEGRATION.md
  - https://arxiv.org/pdf/2006.09661
links:
  profile: ./docs/Phase0-Alignment/PROFILE.yaml
  context: ./docs/Phase0-Alignment/CONTEXT.md
  architecture: ./docs/Phase3-MVP/ARCHITECTURE_INTEGRATION.md
---

# Product Requirements Document - SIREN INR (Alternative to CPPN)

## Product Summary
Goal: deliver a SIREN-based implicit neural representation (INR) generator that replaces or complements the CPPN net. The system maps continuous coordinates (x, y, t) to RGB, conditions on CLIP text embeddings via FiLM, trains with CLIP-guided losses, and targets the proven tiny-net regime (3L x 4D tier) while allowing a small search space to discover the best SIREN architecture.

Outputs: MP4/PNG frames, JSON metadata (arch, seeds, losses), checkpoints for continuation, and an evaluation report versus CPPN baselines.

## Success Criteria
- Quality: match or exceed CPPN organic quality (target >= 5.0/5.0 MOS on organic prompts) and CLIP text-image score parity on the shared prompt set.
- Temporal stability: flicker metric (mean |frame diff| or t-SSIM) <= CPPN baseline.
- Performance: >= 1.0x realtime render at 1080p60 on RTX 5070 for the selected SIREN arch; memory within current budget.
- Size: preferred architecture within the tiny regime (<= ~150 params; stretch goal <= ~300 params) to stay compatible with 3L x 4D scale.
- Training: stable convergence using SIREN init (per paper 2006.09661) with CLIP-guided losses; no mode collapse on the prompt set (N seeds > 3).

## Scope (Must Have)
- SIREN INR generator: sine activations with SIREN initialization on all layers; inputs (x, y, t) normalized to [-1, 1].
- Conditioning: FiLM modulation (gamma, beta per layer) from frozen CLIP text embeddings.
- Time continuity: continuous t coordinate included in the same SIREN input path; support arbitrary frame sampling and scrubbing.
- Training loop: CLIP text-image loss with multi-crop augmentation, temporal smoothness penalty, TV regularizer, color-range clamp; Adam/AdamW optimizer.
- Architecture search: defined grid over depth/width/frequency scale to find the best SIREN configuration within the tiny budget; automatic logging of params, losses, and speed.
- CLI integration: runnable entry point aligned with existing CLI style, with flags for layers, width, frequency scale (w0), loss weights, steps, seed, output paths.
- Evaluation harness: compare CPPN vs SIREN on the shared prompt set with CLIP score, flicker metric, render FPS, and MOS checklist.

## Scope (Nice to Have)
- Mixed conditioning: optional audio conditioning vector fused into FiLM alongside text.
- Dual-CLIP guidance: ensemble of CLIP backbones for robustness.
- Temporal spectral regularizer: low-frequency penalty in time to suppress shimmer without over-smoothing.
- Latent reuse: checkpoint warm-start for fast prompt changes.

## Non-Goals
- No Fourier-feature front-end (SIREN-only for this PRD).
- No 3D radiance fields or volumetric rendering.
- No CLIP fine-tuning; CLIP remains frozen.
- No heavy widths (>64) or deep nets beyond 6 layers in this cycle.

## Architecture Approach
- Input: (x, y, t) in [-1, 1], optionally scaled by a learnable w0 per layer (SIREN paper compatible).
- Core network: MLP with sine activations; SIREN init (first layer larger w0 to capture high frequencies, subsequent layers with reduced w0).
- Conditioner: MLP_cond(text_embed) -> {gamma_l, beta_l} for each layer; FiLM applied to pre-activation hidden states.
- Output head: linear to RGB, followed by tanh or sigmoid with clamp penalty to keep values in range.
- Parameter budget guidance:
  - Tiny sweep (preferred): depths {2, 3, 4}, widths {4, 6, 8, 12}, w0_first {30, 50}, w0_hidden {1, 10}.
  - Fallback sweep: widths up to 16–24 if tiny sweep underfits; must report param count and perf.
- Temporal handling: t shares the same scaling as x, y; optionally separate w0_t if needed, but default is shared to keep params minimal.

### Implementation Path (Reuse-First)
- Python entrypoint: add `siren_cli.py` mirroring the existing CPPN CLI signature in `Code/backend/cli.py` (reuses audio I/O, resolution/FPS flags, `--load-weights` for checkpoints, and `VideoEncoder`).
- Model definition: add `Code/backend/siren_inr.py` for SIREN + FiLM (inputs x, y, t + text FiLM; w0_first/w0_hidden per SIREN init).
- Training loop: fork `Code/backend/clip_optimize_cppn.py` into `clip_optimize_siren.py`, keeping CLIP text handling but adding temporal crops + TV + range clamp; persist checkpoints compatible with `--load-weights`.
- Audio features: reuse `Code/backend/audio_analyzer.py` to feed FiLM conditioning; scaling stays via existing `--audio-scale`.
- Rendering/encoding: reuse `Code/backend/renderer.py` and `Code/backend/video_encoder.py` unchanged.
- Desktop bridge: extend Tauri command to pass `--engine {cppn,siren}` so `Code/desktop` can call the new CLI without changing IPC structure.

## Training Method (Compatibility with 2006.09661)
- Initialization: strict SIREN init (first layer w0 scaled; subsequent layers lower w0) to preserve gradient flow and high-frequency capacity.
- Losses:
  - L_clip: CLIP text-image cosine loss with random crops/resizes (4–8 views).
  - L_temp: ||I_t - I_{t+Δ}||_2 with random Δ in [1/24, 1/12] of sequence duration; optional derivative penalty on t.
  - L_tv: per-frame TV to remove noise; L_range: soft clamp for RGB range.
  - Optional: frequency decay on weights to discourage ringing.
- Optimizer: Adam/AdamW; lower LR for FiLM than core weights; gradient clipping to avoid spikes in tiny nets.
- Data flow: no external dataset; frames are rendered from the INR each step.
- Stability for tiny nets: LR warm-up, smaller CLIP weight ramp, occasional EMA of weights for evaluation snapshots.

### Training Plan (Codebase Hooks)
- Start from `clip_optimize_siren.py` (fork of `Code/backend/clip_optimize_cppn.py`) to leverage existing CLIP/text plumbing; add:
  - Multi-crop CLIP loss (4–8 crops), temporal pair loss (Δ ∈ [1/24, 1/12] of clip), TV loss, and soft range clamp.
  - SIREN init (w0_first high, w0_hidden low) and FiLM conditioning fed by frozen CLIP text embeddings.
  - Logging: write JSON with prompt, w0 values, depth/width, losses, CLIP score, flicker proxy, FPS.
- Use `Code/docs/Audio/TOOL - The Pot (Audio).mp3` and `Code/docs/Audio/Zyryab.mp3` as the default prompt-audio set for parity vs CPPN.
- Checkpoint format: match `--load-weights` expectations in `siren_cli.py` (state_dict plus optional metadata: prompt, best_similarity, arch config).

### Research Scope & Implementation Notes (Data Scientist View)
- Goals and constraints: match/exceed CPPN organic MOS and CLIP parity; flicker ≤ CPPN; ≥1.0x realtime @1080p60 on RTX 5070; preferred ≤150 params (hard cap 300); use shared prompt set plus the two default audio tracks above.
- Architecture sweep (tiny-first, expand only if blocked):
  - Depth {2, 3, 4}; width {4, 6, 8, 12}; w0_first {30, 50}; w0_hidden {1, 10}; optional separate w0_t if flicker persists.
  - FiLM conditioner: 1–2 layers, width {16, 32}; test shared vs per-layer FiLM outputs; bias on/off toggle only if very low widths underfit.
  - Output head: linear → tanh vs sigmoid + soft clamp penalty; log range clamp effects.
  - Fallback widths {16, 24} only if tiny grid fails quality while still meeting perf/params.
- Loss and regularization probes:
  - CLIP crops/views {4, 6, 8}; crop scale jitter; early CLIP weight ramp vs fixed.
  - Temporal loss weight {0.1, 0.25, 0.5} with Δ ∈ [1/24, 1/12]; optional temporal derivative penalty if shimmer remains.
  - TV {0, 1e-4, 5e-4, 1e-3}; range clamp on/off; optional frequency-decay/weight-decay on higher layers if ringing appears.
- Optimization knobs:
  - Optimizer: Adam vs AdamW; core LR {1e-4, 5e-4}; FiLM LR 0.25–0.5× core; warmup {250, 500} steps; gradient clip {0.5, 1.0}.
  - EMA for eval snapshots on/off (decay ~0.99) to stabilize MOS/CLIP readouts.
- Experiment staging:
  - Stage 1 (prune): low-res (e.g., 256p), short schedules; score CLIP, flicker proxy, FPS, params; drop configs that miss realtime or exceed param cap.
  - Stage 2 (rerank): top ~5 at 720p; re-evaluate quality/flicker/perf; keep only configs meeting realtime and size budgets.
  - Stage 3 (final): top 2 at 1080p60, ≥3 seeds each prompt; produce acceptance metrics and checkpoints.
  - Stop rule: only widen width to {16, 24} for best-performing depth if no tiny config reaches quality target.
- Metrics and harness reuse:
  - Quality: CLIP text-image cosine vs CPPN; MOS checklist on organic prompts.
  - Temporal: mean |frame diff|; t-SSIM optional if compute allows.
  - Performance: FPS from CLI timing; VRAM usage.
  - Size/robustness: param count; variance across ≥3 seeds.
- Logging and artifacts:
  - Per-run JSON under `Code/backend/experiments/siren_search/*.json` with prompt, seed, depth/width, w0_first/w0_hidden(/w0_t), FiLM config, losses, CLIP score, flicker proxy, FPS, params, VRAM, checkpoint path.
  - Summary CSV for quick ranking; retain top-2 checkpoints and short MP4/PNG renders for QA review.
- Risk mitigations to apply during sweeps:
  - Underfitting: step up w0_first or width; allow bias; modestly raise CLIP crops.
  - Flicker/shimmer: increase L_temp, try separate w0_t, slightly higher TV, or temporal spectral penalty if needed.
  - Adversarial textures: cap early CLIP weight, rely on multi-crop + range clamp, optional mild color jitter.

## Evaluation and Acceptance Tests
- A1 Quality: CLIP score parity or better vs CPPN on shared prompt set; MOS >= baseline on organic prompts.
- A2 Temporal: flicker metric <= CPPN baseline; no visible jumps on scrub test.
- A3 Performance: render >= 1.0x realtime at 1080p60 on RTX 5070 for the chosen architecture; VRAM within current CPPN envelope.
- A4 Size: chosen architecture within the stated param budget (preferred <= ~150 params; hard cap <= ~300).
- A5 Robustness: at least 3 seeds per prompt without collapse; loss curves stable (no divergence) for full training schedule.

### Minimal Acceptance Harness (Reuse)
- Rendering speed: reuse existing CLI timing output (from `Code/backend/cli.py` pattern) to assert ≥1.0x realtime for the tiny SIREN arch.
- Flicker metric: add a post-render frame-diff script (can live beside `siren_cli.py`) to compute mean |frame diff| on the produced MP4.
- CLIP score parity: reuse CLIP encoder flow from `clip_optimize_siren.py` on sampled frames to compare against CPPN outputs.

## Deliverables
- Training script and CLI entry for SIREN INR with FiLM + CLIP guidance.
- Config presets for tiny and fallback widths (YAML/JSON).
- Architecture search report: grid tested, metrics (quality, flicker, FPS, params), and selection rationale.
- Checkpoints for the top-1 and top-2 architectures; sample renders (MP4/PNGs).
- Integration notes for swapping CPPN with SIREN in the existing pipeline (CLI flags, expected runtime).
- Code drops:
  - `Code/backend/siren_inr.py` (model), `Code/backend/siren_cli.py` (entrypoint), `Code/backend/clip_optimize_siren.py` (CLIP-guided training).
  - Desktop integration: `Code/desktop` Tauri command adds `engine`/`mode` flag and forwards it to the backend CLI unchanged.
  - Metadata emit: JSON sidecar per run (arch, seeds, losses, FPS, flicker proxy, output paths).

## Risks and Mitigations
- Tiny nets underfit high-frequency detail: mitigate by tuning w0_first, allowing width 8–12 fallback, and using multi-crop CLIP guidance.
- Flicker from weak temporal coupling: strengthen L_temp, ensure consistent t scaling, optionally add spectral temporal penalty.
- Adversarial textures from CLIP: multi-crop, color jitter, TV, and clamp; cap CLIP loss weight early, then ramp.
- Performance regressions: profile after each architecture candidate; reject configs that fail realtime even if quality is higher.
- Missing FiLM/SIREN code: reuse existing CLI, audio analyzer, renderer, and CLIP plumbing to limit new surface area; implement SIREN/FiLM as a drop-in module with the same I/O contract.

## Open Questions
- Default w0 values for tiny regime: 30/1 vs 50/10? Need a quick ablation.
- Should we allow a small positional bias term per layer to help with very low widths?
- Do we expose audio conditioning in this PRD or defer to a follow-up?
- Which CLIP backbone is the default (ViT-B/32 for speed vs B/16 for quality)?
- Where to store the search logs? Proposed: `Code/backend/experiments/siren_search/*.json` with one JSON per config plus a summary CSV.

## Milestones
- M1 Design (1 day): lock search grid, losses, and metrics; finalize CLI flags.
- M2 Prototype (1–2 days): implement SIREN INR + FiLM + training loop; smoke-test low-res renders.
- M3 Search (2–3 days): run tiny-grid sweep; log quality, flicker, FPS, params; pick top-2.
- M4 Validate (1 day): extended runs on top-2, confirm metrics and realtime at 1080p60.
- M5 Deliver (1 day): export checkpoints, configs, sample videos, and the search report; wire CLI integration notes.
