"""
SIREN INR renderer with FiLM conditioning (text + audio).

Usage:
    python siren_cli.py input.mp3 output.mp4 --prompt "cosmic organic nebula"
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Generator, Tuple

import clip
import numpy as np
import torch

from audio_analyzer import AudioAnalyzer
from siren_inr import SirenINR
from video_encoder import VideoEncoder


RESOLUTIONS = {
    "360p": (640, 360),
    "480p": (854, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render SIREN INR video")

    parser.add_argument("input", type=str, help="Input audio file (MP3/WAV)")
    parser.add_argument("output", type=str, help="Output MP4 path")
    parser.add_argument("--prompt", type=str, required=True, help="Text prompt for FiLM conditioning")

    # Video
    parser.add_argument("--resolution", type=str, default="720p", choices=list(RESOLUTIONS.keys()))
    parser.add_argument("--fps", type=int, default=30, choices=[24, 30, 60])
    parser.add_argument("--batch-size", type=int, default=None, help="Pixels per batch (auto if None)")

    # Model
    parser.add_argument("--depth", type=int, default=3, help="SIREN depth")
    parser.add_argument("--width", type=int, default=8, help="SIREN width")
    parser.add_argument("--w0-first", type=float, default=30.0, help="w0 for first layer")
    parser.add_argument("--w0-hidden", type=float, default=1.0, help="w0 for hidden layers")
    parser.add_argument("--w0-time", type=float, default=None, help="Optional time scaling factor")
    parser.add_argument("--film-hidden", type=int, default=64, help="FiLM hidden width")
    parser.add_argument(
        "--output-activation",
        type=str,
        default="tanh",
        choices=["tanh", "sigmoid"],
        help="Output activation",
    )
    parser.add_argument("--no-bias", action="store_true", help="Disable biases in linear layers")

    # Conditioning
    parser.add_argument(
        "--clip-model",
        type=str,
        default="ViT-B/32",
        choices=["ViT-B/32", "ViT-B/16", "RN50", "RN101"],
        help="CLIP text backbone",
    )
    parser.add_argument("--audio-scale", type=float, default=0.05, help="Scale for audio features")
    parser.add_argument("--load-weights", type=str, required=True, help="Checkpoint from clip_optimize_siren.py")

    # Runtime
    parser.add_argument("--device", type=str, choices=["auto", "cuda", "cpu"], default="auto")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed")
    parser.add_argument("--engine", type=str, default="siren", choices=["siren"], help="Engine selector")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()
    if args.device == "auto":
        args.device = "cuda" if torch.cuda.is_available() else "cpu"
    return args


def prepare_grid(width: int, height: int, device: torch.device) -> torch.Tensor:
    """Precompute XY grid, t column filled later."""
    x = torch.linspace(-1.0, 1.0, width, device=device)
    y = torch.linspace(-1.0, 1.0, height, device=device)
    yy, xx = torch.meshgrid(y, x, indexing="ij")
    xy = torch.stack([xx, yy], dim=-1).view(-1, 2)
    return xy


def load_text_embed(prompt: str, clip_model: str, device: torch.device) -> torch.Tensor:
    model, _ = clip.load(clip_model, device=device)
    model.eval()
    tokens = clip.tokenize([prompt]).to(device)
    with torch.no_grad():
        feat = model.encode_text(tokens)
        feat = feat / feat.norm(dim=-1, keepdim=True)
    return feat.detach(), feat.shape[-1]


def build_model_from_checkpoint(
    checkpoint: dict,
    cond_dim: int,
    device: torch.device,
    overrides: argparse.Namespace,
) -> SirenINR:
    cfg = checkpoint.get("siren_config", {})
    model = SirenINR(
        coord_dim=3,
        hidden_dim=cfg.get("width", overrides.width),
        num_layers=cfg.get("depth", overrides.depth),
        out_dim=3,
        cond_dim=cond_dim,
        w0_first=cfg.get("w0_first", overrides.w0_first),
        w0_hidden=cfg.get("w0_hidden", overrides.w0_hidden),
        w0_time=cfg.get("w0_time", overrides.w0_time),
        film_hidden=cfg.get("film_hidden", overrides.film_hidden),
        output_activation=cfg.get("output_activation", overrides.output_activation),
        use_bias=cfg.get("use_bias", not overrides.no_bias),
    ).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model


def render_frames(
    model: SirenINR,
    xy_grid: torch.Tensor,
    audio_analysis: dict,
    text_embed: torch.Tensor,
    audio_scale: float,
    width: int,
    height: int,
    fps: int,
    batch_size: int,
    device: torch.device,
    verbose: bool = False,
) -> Generator[np.ndarray, None, None]:
    num_pixels = xy_grid.shape[0]
    total_frames = audio_analysis["num_frames"]

    # Choose batch size
    if batch_size is None:
        if device.type == "cuda":
            batch_size = min(num_pixels, 2_000_000)
        else:
            batch_size = 200_000

    audio_feats = audio_analysis["features"] * audio_scale
    audio_feats = torch.tensor(audio_feats, device=device, dtype=torch.float32)
    cond_dim_audio = audio_feats.shape[1]

    for frame_idx in range(total_frames):
        t_val = frame_idx / max(1, total_frames - 1)
        if verbose and frame_idx % max(1, total_frames // 10) == 0:
            print(f"Rendering frame {frame_idx+1}/{total_frames} (t={t_val:.3f})")

        coords = torch.zeros((num_pixels, 3), device=device, dtype=torch.float32)
        coords[:, :2] = xy_grid
        coords[:, 2] = t_val * 2.0 - 1.0

        audio_feat = audio_feats[frame_idx]
        cond = torch.cat([text_embed[0], audio_feat], dim=0).unsqueeze(0)

        out = torch.empty((num_pixels, 3), device=device, dtype=torch.float32)
        with torch.no_grad():
            for start in range(0, num_pixels, batch_size):
                end = min(start + batch_size, num_pixels)
                batch = coords[start:end]
                pred = model(batch, cond)
                out[start:end] = pred

        img = out.view(height, width, 3)
        img = torch.clamp((img + 1.0) * 0.5, 0.0, 1.0)
        img_np = (img.cpu().numpy() * 255).astype(np.uint8)
        yield img_np


def main() -> None:
    args = parse_args()

    if args.engine != "siren":
        print("Only engine='siren' is supported in this CLI. Use cli.py for CPPN.")
        sys.exit(1)

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"[ERROR] Input not found: {input_path}")
        sys.exit(1)

    if output_path.exists():
        response = input(f"Output exists at {output_path}. Overwrite? (y/N): ")
        if response.lower() != "y":
            print("Cancelled.")
            sys.exit(0)

    if args.seed is not None:
        torch.manual_seed(args.seed)
        np.random.seed(args.seed)

    device = torch.device(args.device)
    width, height = RESOLUTIONS[args.resolution]

    print("=" * 60)
    print("SIREN INR Renderer")
    print("=" * 60)
    print(f"Prompt: {args.prompt}")
    print(f"Audio: {input_path}")
    print(f"Output: {output_path}")
    print(f"Resolution: {width}x{height} @ {args.fps} FPS")
    print(f"Device: {device}")
    print("=" * 60)

    # Audio analysis
    analyzer = AudioAnalyzer()
    audio_analysis = analyzer.analyze(str(input_path), fps=args.fps)
    audio_analysis["features"] = analyzer.normalize_features(audio_analysis["features"], method="minmax")

    # Text embedding
    text_embed, text_dim = load_text_embed(args.prompt, args.clip_model, device)

    # Load checkpoint
    ckpt_path = Path(args.load_weights)
    if not ckpt_path.exists():
        print(f"[ERROR] Checkpoint not found: {ckpt_path}")
        sys.exit(1)
    checkpoint = torch.load(ckpt_path, map_location=device)
    audio_dim = checkpoint.get("audio_dim", audio_analysis["features"].shape[1])
    cond_dim = text_dim + audio_dim

    model = build_model_from_checkpoint(checkpoint, cond_dim, device, args)

    # Grid
    xy_grid = prepare_grid(width, height, device)

    # Encoder
    encoder = VideoEncoder(str(output_path), fps=args.fps)

    start = time.time()
    frame_iter = render_frames(
        model=model,
        xy_grid=xy_grid,
        audio_analysis=audio_analysis,
        text_embed=text_embed,
        audio_scale=args.audio_scale,
        width=width,
        height=height,
        fps=args.fps,
        batch_size=args.batch_size,
        device=device,
        verbose=args.verbose,
    )

    final_video = encoder.encode(
        frame_iter,
        audio_path=str(input_path),
        export_frames=False,
        frames_dir=None,
        num_frames=audio_analysis["num_frames"],
    )

    elapsed = time.time() - start
    realtime = audio_analysis["duration"] / elapsed if audio_analysis["duration"] > 0 else 0

    print("\n[OK] Render complete")
    print(f"  Output: {final_video}")
    print(f"  Frames: {audio_analysis['num_frames']}")
    print(f"  Duration: {audio_analysis['duration']:.2f}s")
    print(f"  Wall clock: {elapsed:.1f}s")
    if realtime > 0:
        print(f"  Speed: {realtime:.2f}x realtime")


if __name__ == "__main__":
    main()


