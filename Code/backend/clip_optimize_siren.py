"""
CLIP-guided optimization for SIREN INR with FiLM conditioning.

Trains a tiny SIREN to map (x, y, t) → RGB using CLIP text guidance,
temporal smoothness, TV, and range clamp penalties. Supports audio-aware FiLM
by concatenating text embedding with per-frame audio features.
"""

import argparse
import json
import math
import random
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

import clip
import numpy as np
import torch
import torch.nn.functional as F
import torch.nn as nn

from audio_analyzer import AudioAnalyzer
from siren_inr import SirenINR


def build_grid(resolution: int, time_value: float, device: torch.device) -> torch.Tensor:
    """Create coordinate grid flattened to (H*W, 3) with t column."""
    coords = torch.linspace(-1.0, 1.0, resolution, device=device)
    yy, xx = torch.meshgrid(coords, coords, indexing="ij")
    t = torch.full_like(xx, fill_value=time_value)
    grid = torch.stack([xx, yy, t], dim=-1).view(-1, 3)
    return grid


def make_crops(image_3chw: torch.Tensor, num_crops: int, min_scale: float, max_scale: float) -> torch.Tensor:
    """Generate random resized crops suitable for CLIP."""
    _, h, w = image_3chw.shape
    crops = []
    for _ in range(num_crops):
        scale = random.uniform(min_scale, max_scale)
        crop_h = max(1, int(h * scale))
        crop_w = max(1, int(w * scale))
        y0 = random.randint(0, max(0, h - crop_h))
        x0 = random.randint(0, max(0, w - crop_w))
        crop = image_3chw[:, y0 : y0 + crop_h, x0 : x0 + crop_w].unsqueeze(0)
        crop = F.interpolate(crop, size=(224, 224), mode="bilinear", align_corners=False)
        crops.append(crop)
    return torch.cat(crops, dim=0)


def tv_loss(img: torch.Tensor) -> torch.Tensor:
    """Total variation loss on image tensor in [-1, 1]."""
    dx = img[:, :, 1:, :] - img[:, :, :-1, :]
    dy = img[:, :, :, 1:] - img[:, :, :, :-1]
    return (dx.abs().mean() + dy.abs().mean())


def range_clamp_loss(img: torch.Tensor) -> torch.Tensor:
    """Soft penalty for values outside [-1, 1]."""
    over = F.relu(img - 1.0)
    under = F.relu(-1.0 - img)
    return (over + under).abs().mean()


def select_audio_feature(audio_analysis: Dict, t01: float, scale: float, device: torch.device) -> torch.Tensor:
    """Pick audio feature row for normalized time in [0,1] and scale."""
    num_frames = audio_analysis["num_frames"]
    idx = min(num_frames - 1, max(0, int(t01 * (num_frames - 1))))
    feat = audio_analysis["features"][idx] * scale
    return torch.tensor(feat, device=device, dtype=torch.float32)


class AudioFiLM(nn.Module):
    """Small MLP to produce additive FiLM params from audio only."""

    def __init__(self, audio_dim: int, hidden: int, num_layers: int, siren_hidden: int) -> None:
        super().__init__()
        self.num_layers = num_layers
        self.siren_hidden = siren_hidden
        self.net = nn.Sequential(
            nn.Linear(audio_dim, hidden),
            nn.ReLU(inplace=True),
            nn.Linear(hidden, num_layers * siren_hidden * 2),
        )

    def forward(self, audio_feat: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        params = self.net(audio_feat)
        params = params.view(audio_feat.shape[0], self.num_layers, self.siren_hidden * 2)
        gammas, betas = params.split(self.siren_hidden, dim=-1)
        return gammas, betas


def train_siren(
    args: argparse.Namespace,
) -> Dict:
    device = torch.device("cuda" if args.device == "cuda" and torch.cuda.is_available() else "cpu")

    # CLIP model
    clip_model, _ = clip.load(args.clip_model, device=device)
    clip_model.eval()

    # Text embedding
    text_tokens = clip.tokenize([args.prompt]).to(device)
    with torch.no_grad():
        text_features = clip_model.encode_text(text_tokens)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    text_features = text_features.detach()
    clip_dim = text_features.shape[-1]

    # Audio analysis
    analyzer = AudioAnalyzer()
    audio_analysis = analyzer.analyze(
        args.audio,
        fps=args.fps,
        duration=args.duration if args.duration > 0 else None,
    )
    audio_analysis["features"] = analyzer.normalize_features(audio_analysis["features"], method="minmax")
    audio_dim = audio_analysis["features"].shape[1]

    cond_dim = clip_dim + audio_dim

    model = SirenINR(
        coord_dim=3,
        hidden_dim=args.width,
        num_layers=args.depth,
        out_dim=3,
        cond_dim=cond_dim,
        w0_first=args.w0_first,
        w0_hidden=args.w0_hidden,
        w0_time=args.w0_time,
        film_hidden=args.film_hidden,
        output_activation=args.output_activation,
        use_bias=not args.no_bias,
    ).to(device)

    audio_film: Optional[AudioFiLM] = None
    if args.enable_audio_film:
        audio_film = AudioFiLM(
            audio_dim=audio_dim,
            hidden=args.audio_film_hidden,
            num_layers=args.depth,
            siren_hidden=args.width,
        ).to(device)

    params = list(model.parameters())
    if audio_film is not None:
        params += list(audio_film.parameters())
    optimizer = torch.optim.Adam(
        params,
        lr=args.lr,
        betas=(0.9, 0.999),
        weight_decay=args.weight_decay,
    )

    scaler = torch.cuda.amp.GradScaler(enabled=args.amp and device.type == "cuda")

    best_similarity = -1.0
    best_state = None
    best_audio_state = None
    history = []

    coords_cache = {}

    def get_coords(t_val: float) -> torch.Tensor:
        key = round(t_val, 4)
        if key not in coords_cache:
            coords_cache[key] = build_grid(args.train_resolution, t_val * 2.0 - 1.0, device)
        return coords_cache[key]

    def build_cond(t_val: float) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]], Optional[torch.Tensor]]:
        audio_feat = select_audio_feature(audio_analysis, t_val, args.audio_scale, device)
        cond = torch.cat([text_features[0], audio_feat], dim=0)

        extra_film: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
        if audio_film is not None:
            extra_gamma, extra_beta = audio_film(audio_feat.unsqueeze(0))
            if args.audio_film_scale != 1.0:
                extra_gamma = extra_gamma * args.audio_film_scale
                extra_beta = extra_beta * args.audio_film_scale
            extra_film = (extra_gamma, extra_beta)

        gamma_gate: Optional[torch.Tensor] = None
        if args.enable_audio_gate:
            gate = audio_feat.abs().mean() * args.audio_gate_scale
            gamma_gate = gate.clamp(min=0.0).view(1)

        return cond.unsqueeze(0), extra_film, gamma_gate  # (1, cond_dim), optional FiLM/gate

    for step in range(1, args.steps + 1):
        model.train()
        optimizer.zero_grad(set_to_none=True)

        # Sample times
        t0 = random.random()
        delta = random.uniform(args.temporal_delta_min, args.temporal_delta_max)
        t1 = min(1.0, t0 + delta)

        coords0 = get_coords(t0)
        coords1 = get_coords(t1)

        cond0, extra0, gate0 = build_cond(t0)
        cond1, extra1, gate1 = build_cond(t1)

        with torch.cuda.amp.autocast(enabled=args.amp and device.type == "cuda"):
            # Forward passes
            img0 = model(coords0, cond0, extra_film=extra0, gamma_gate=gate0).view(
                args.train_resolution, args.train_resolution, 3
            )
            img1 = model(coords1, cond1, extra_film=extra1, gamma_gate=gate1).view(
                args.train_resolution, args.train_resolution, 3
            )

            # Move to CHW in [-1,1]
            img0_chw = img0.permute(2, 0, 1)
            img1_chw = img1.permute(2, 0, 1)

            # CLIP crops on img0
            img0_clip = (img0_chw + 1.0) * 0.5
            crops = make_crops(
                img0_clip,
                num_crops=args.num_crops,
                min_scale=args.crop_min_scale,
                max_scale=args.crop_max_scale,
            )
            mean = torch.tensor([0.48145466, 0.4578275, 0.40821073], device=device).view(1, 3, 1, 1)
            std = torch.tensor([0.26862954, 0.26130258, 0.27577711], device=device).view(1, 3, 1, 1)
            crops = (crops - mean) / std

            image_features = clip_model.encode_image(crops)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            similarity = (image_features @ text_features.T).squeeze()
            clip_loss = -similarity.mean()

            # Temporal loss between img0/img1
            temp_loss = F.mse_loss(img0_chw, img1_chw)

            # TV and range clamp on img0
            tv = tv_loss(img0_chw.unsqueeze(0))
            rclamp = range_clamp_loss(img0_chw.unsqueeze(0))

            total_loss = (
                args.clip_weight * clip_loss
                + args.temp_weight * temp_loss
                + args.tv_weight * tv
                + args.range_weight * rclamp
            )

        scaler.scale(total_loss).backward()
        if args.grad_clip is not None and args.grad_clip > 0:
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
        scaler.step(optimizer)
        scaler.update()

        sim_value = similarity.mean().item()
        if sim_value > best_similarity:
            best_similarity = sim_value
            best_state = {k: v.detach().cpu() for k, v in model.state_dict().items()}
            if audio_film is not None:
                best_audio_state = {k: v.detach().cpu() for k, v in audio_film.state_dict().items()}

        if step % args.log_interval == 0 or step == args.steps:
            entry = {
                "step": step,
                "clip_loss": clip_loss.item(),
                "temp_loss": temp_loss.item(),
                "tv_loss": tv.item(),
                "range_loss": rclamp.item(),
                "similarity": sim_value,
                "best_similarity": best_similarity,
            }
            history.append(entry)
            print(
                f"[{step:05d}/{args.steps}] "
                f"sim={sim_value:.4f} best={best_similarity:.4f} "
                f"clip={clip_loss.item():.4f} temp={temp_loss.item():.4f} "
                f"tv={tv.item():.4f} range={rclamp.item():.4f}"
            )

    if best_state is None:
        best_state = {k: v.detach().cpu() for k, v in model.state_dict().items()}
    if audio_film is not None and best_audio_state is None:
        best_audio_state = {k: v.detach().cpu() for k, v in audio_film.state_dict().items()}

    return {
        "best_similarity": best_similarity,
        "best_state": best_state,
        "best_audio_state": best_audio_state,
        "history": history,
        "audio_dim": audio_dim,
        "clip_dim": clip_dim,
        "model_config": {
            "depth": args.depth,
            "width": args.width,
            "w0_first": args.w0_first,
            "w0_hidden": args.w0_hidden,
            "w0_time": args.w0_time,
            "film_hidden": args.film_hidden,
            "output_activation": args.output_activation,
            "use_bias": not args.no_bias,
        },
        "audio_film_enabled": args.enable_audio_film,
        "audio_gate_enabled": args.enable_audio_gate,
    }


def save_artifacts(
    args: argparse.Namespace,
    train_result: Dict,
    output_dir: Path,
) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / f"{args.run_name}_siren.pth"
    history_path = output_dir / f"{args.run_name}_history.json"

    save_data = {
        "state_dict": train_result["best_state"],
        "audio_film_state": train_result["best_audio_state"],
        "prompt": args.prompt,
        "best_similarity": train_result["best_similarity"],
        "clip_model": args.clip_model,
        "audio_file": args.audio,
        "train_resolution": args.train_resolution,
        "steps": args.steps,
        "siren_config": train_result["model_config"],
        "cond_dim": train_result["clip_dim"] + train_result["audio_dim"],
        "audio_dim": train_result["audio_dim"],
        "audio_film_enabled": train_result.get("audio_film_enabled", False),
        "audio_gate_enabled": train_result.get("audio_gate_enabled", False),
    }
    torch.save(save_data, checkpoint_path)

    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "run_name": args.run_name,
                "prompt": args.prompt,
                "best_similarity": train_result["best_similarity"],
                "history": train_result["history"],
                "config": vars(args),
            },
            f,
            indent=2,
        )

    return checkpoint_path, history_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CLIP-guided SIREN INR optimization")

    # Prompts / IO
    parser.add_argument("--prompt", type=str, required=True, help="Text prompt for CLIP guidance")
    parser.add_argument(
        "--audio",
        type=str,
        default="docs/Audio/TOOL - The Pot (Audio).mp3",
        help="Audio path for conditioning",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="Code/backend/experiments/siren_search",
        help="Directory for checkpoints/logs",
    )
    parser.add_argument("--run-name", type=str, default="run", help="Run name prefix")

    # Model
    parser.add_argument("--depth", type=int, default=3, help="Number of SIREN layers")
    parser.add_argument("--width", type=int, default=8, help="Hidden width")
    parser.add_argument("--w0-first", type=float, default=30.0, help="w0 for first layer")
    parser.add_argument("--w0-hidden", type=float, default=1.0, help="w0 for hidden layers")
    parser.add_argument("--w0-time", type=float, default=None, help="Optional time scaling factor")
    parser.add_argument("--film-hidden", type=int, default=64, help="FiLM conditioner hidden width")
    parser.add_argument(
        "--output-activation",
        type=str,
        choices=["tanh", "sigmoid"],
        default="tanh",
        help="Output activation",
    )
    parser.add_argument("--no-bias", action="store_true", help="Disable biases in linear layers")

    # Training
    parser.add_argument("--steps", type=int, default=500, help="Training steps")
    parser.add_argument("--train-resolution", type=int, default=256, help="Training resolution (square)")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--weight-decay", type=float, default=0.0, help="Weight decay")
    parser.add_argument("--grad-clip", type=float, default=1.0, help="Gradient clipping max norm")
    parser.add_argument("--amp", action="store_true", help="Enable mixed precision")
    parser.add_argument("--device", type=str, choices=["auto", "cuda", "cpu"], default="auto")
    parser.add_argument("--fps", type=int, default=30, help="Audio FPS for feature extraction")
    parser.add_argument("--duration", type=float, default=0.0, help="Optional duration seconds (0=full)")
    parser.add_argument("--audio-scale", type=float, default=0.05, help="Scale factor for audio features")

    # Loss
    parser.add_argument("--clip-weight", type=float, default=1.0, help="Weight for CLIP loss")
    parser.add_argument("--temp-weight", type=float, default=0.25, help="Weight for temporal loss")
    parser.add_argument("--tv-weight", type=float, default=1e-4, help="Weight for TV loss")
    parser.add_argument("--range-weight", type=float, default=5e-4, help="Weight for range clamp loss")
    parser.add_argument("--num-crops", type=int, default=4, help="Number of random crops per step")
    parser.add_argument("--crop-min-scale", type=float, default=0.5, help="Min crop scale relative to image")
    parser.add_argument("--crop-max-scale", type=float, default=1.0, help="Max crop scale relative to image")
    parser.add_argument("--temporal-delta-min", type=float, default=1 / 24, help="Min temporal delta (seconds)")
    parser.add_argument("--temporal-delta-max", type=float, default=1 / 12, help="Max temporal delta (seconds)")

    # Audio FiLM / gate
    parser.add_argument("--enable-audio-film", action="store_true", help="Add audio-only FiLM branch (additive)")
    parser.add_argument("--audio-film-hidden", type=int, default=32, help="Hidden width for audio FiLM MLP")
    parser.add_argument(
        "--audio-film-scale",
        dest="audio_film_scale",
        type=float,
        default=1.0,
        help="Scale for audio FiLM outputs",
    )
    parser.add_argument("--enable-audio-gate", action="store_true", help="Gate FiLM gamma by audio envelope")
    parser.add_argument(
        "--audio-gate-scale",
        type=float,
        default=1.0,
        help="Scale factor applied to mean-abs audio envelope for gamma gating",
    )

    # CLIP
    parser.add_argument(
        "--clip-model",
        type=str,
        default="ViT-B/32",
        choices=["ViT-B/32", "ViT-B/16", "RN50", "RN101"],
        help="CLIP backbone",
    )

    # Logging
    parser.add_argument("--log-interval", type=int, default=50, help="Steps between log prints")

    args = parser.parse_args()
    if args.device == "auto":
        args.device = "cuda" if torch.cuda.is_available() else "cpu"
    return args


def main() -> None:
    args = parse_args()
    start = time.time()
    print("=" * 60)
    print("CLIP-guided SIREN optimization")
    print("=" * 60)
    print(f"Prompt: {args.prompt}")
    print(f"Audio: {args.audio}")
    print(f"Device: {args.device}")
    print(f"Resolution: {args.train_resolution}x{args.train_resolution}")
    print(f"Depth x Width: {args.depth} x {args.width}")
    print(f"CLIP model: {args.clip_model}")
    print("=" * 60)

    result = train_siren(args)

    out_dir = Path(args.output_dir)
    ckpt_path, hist_path = save_artifacts(args, result, out_dir)

    elapsed = time.time() - start
    print("\n[OK] Training complete")
    print(f"  Best similarity: {result['best_similarity']:.4f}")
    print(f"  Checkpoint: {ckpt_path}")
    print(f"  History: {hist_path}")
    print(f"  Elapsed: {elapsed/60:.2f} min")


if __name__ == "__main__":
    main()


