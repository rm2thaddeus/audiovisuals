"""
Render an MP4 from a trained SIREN INR checkpoint produced by clip_optimize_siren.py.

Loads the saved SirenINR (and optional audio FiLM branch), regenerates text/audio
conditioners, and renders a video at the requested resolution/duration.
"""

import argparse
import json
from pathlib import Path
from typing import Optional, Tuple
import sys

import numpy as np
import torch
import torch.nn as nn
import clip

# Ensure backend modules are importable
BACKEND_ROOT = Path(__file__).resolve().parents[3]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from audio_analyzer import AudioAnalyzer  # noqa: E402
from siren_inr import SirenINR  # noqa: E402
from video_encoder import VideoEncoder  # noqa: E402


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


def load_history_config(checkpoint_path: Path) -> dict:
    hist_path = checkpoint_path.with_name(checkpoint_path.name.replace("_siren.pth", "_history.json"))
    if not hist_path.exists():
        return {}
    with open(hist_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("config", {})


def build_audio_film_from_state(
    state: Optional[dict],
    audio_dim: int,
    depth: int,
    width: int,
    device: torch.device,
) -> Optional[AudioFiLM]:
    if not state:
        return None
    # Infer hidden from first linear weight shape
    if "net.0.weight" in state:
        hidden = state["net.0.weight"].shape[0]
    else:
        return None
    audio_film = AudioFiLM(audio_dim=audio_dim, hidden=hidden, num_layers=depth, siren_hidden=width).to(device)
    audio_film.load_state_dict(state)
    audio_film.eval()
    return audio_film


def render_mp4(
    checkpoint_path: Path,
    output_path: Path,
    prompt: Optional[str],
    audio_path: Optional[str],
    duration: float,
    fps: int,
    width: int,
    height: int,
) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    ckpt = torch.load(checkpoint_path, map_location=device)
    hist_cfg = load_history_config(checkpoint_path)

    run_prompt = prompt if prompt is not None else ckpt.get("prompt", "cosmic galaxy")
    run_audio = audio_path if audio_path is not None else ckpt.get("audio_file")
    if run_audio is None:
        raise ValueError("Audio path not found in checkpoint; please specify --audio.")

    # CLIP model + text embedding
    clip_model_name = ckpt.get("clip_model", hist_cfg.get("clip_model", "ViT-B/16"))
    clip_model, _ = clip.load(clip_model_name, device=device)
    clip_model.eval()
    text_tokens = clip.tokenize([run_prompt]).to(device)
    with torch.no_grad():
        text_features = clip_model.encode_text(text_tokens)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    text_feat = text_features[0]  # (clip_dim,)

    # Audio features
    analyzer = AudioAnalyzer()
    audio_fps = hist_cfg.get("fps", 30)
    analysis = analyzer.analyze(run_audio, fps=audio_fps, duration=duration if duration > 0 else None)
    analysis["features"] = analyzer.normalize_features(analysis["features"], method="minmax")
    audio_features_np = analysis["features"]
    num_frames = analysis["num_frames"]
    actual_duration = analysis["duration"]

    # Load model
    siren_cfg = ckpt["siren_config"]
    cond_dim = ckpt["cond_dim"]
    audio_dim = ckpt["audio_dim"]
    model = SirenINR(
        coord_dim=3,
        hidden_dim=siren_cfg["width"],
        num_layers=siren_cfg["depth"],
        out_dim=3,
        cond_dim=cond_dim,
        w0_first=siren_cfg["w0_first"],
        w0_hidden=siren_cfg["w0_hidden"],
        w0_time=siren_cfg["w0_time"],
        film_hidden=siren_cfg["film_hidden"],
        output_activation=siren_cfg["output_activation"],
        use_bias=siren_cfg["use_bias"],
    ).to(device)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    model_dtype = next(model.parameters()).dtype
    text_feat = text_feat.to(device=device, dtype=model_dtype)

    # Optional audio FiLM
    audio_film_state = ckpt.get("audio_film_state")
    audio_film_enabled = ckpt.get("audio_film_enabled", False) and audio_film_state is not None
    audio_film = build_audio_film_from_state(audio_film_state, audio_dim, siren_cfg["depth"], siren_cfg["width"], device)
    if audio_film is not None:
        audio_film.eval()
    audio_film_scale = hist_cfg.get("audio_film_scale", 1.0)
    audio_gate_enabled = ckpt.get("audio_gate_enabled", False)
    audio_gate_scale = hist_cfg.get("audio_gate_scale", 1.0)

    audio_scale = hist_cfg.get("audio_scale", 0.05)

    # Coordinate grid for all frames
    xs = torch.linspace(-1.0, 1.0, width, device=device, dtype=model_dtype)
    ys = torch.linspace(-1.0, 1.0, height, device=device, dtype=model_dtype)
    yy, xx = torch.meshgrid(ys, xs, indexing="ij")
    base_xy = torch.stack([xx, yy], dim=-1).view(-1, 2)  # (H*W, 2)

    def frame_generator():
        """Yield RGB frames as uint8 for the VideoEncoder."""
        with torch.no_grad():
            for frame_idx in range(num_frames):
                t01 = frame_idx / max(1, num_frames - 1)
                coords = torch.empty((width * height, 3), device=device, dtype=model_dtype)
                coords[:, 0:2] = base_xy
                coords[:, 2] = t01 * 2.0 - 1.0

                audio_feat_np = audio_features_np[frame_idx] * audio_scale
                audio_feat = torch.tensor(audio_feat_np, device=device, dtype=model_dtype)

                cond = torch.cat([text_feat, audio_feat], dim=0).unsqueeze(0)

                extra_film = None
                if audio_film_enabled and audio_film is not None:
                    eg, eb = audio_film(audio_feat.unsqueeze(0))
                    if audio_film_scale != 1.0:
                        eg = eg * audio_film_scale
                        eb = eb * audio_film_scale
                    extra_film = (eg, eb)

                gamma_gate = None
                if audio_gate_enabled:
                    gate = audio_feat.abs().mean() * audio_gate_scale
                    gamma_gate = gate.clamp(min=0.0).view(1)

                rgb = model(coords, cond, extra_film=extra_film, gamma_gate=gamma_gate)
                rgb = rgb.view(height, width, 3)
                rgb = ((rgb + 1.0) * 0.5).clamp(0.0, 1.0)
                frame_np = (rgb * 255.0).to(torch.uint8).cpu().numpy()
                yield frame_np

    encoder = VideoEncoder(str(output_path), fps=fps)
    final_path = encoder.encode(
        frame_generator(),
        audio_path=str(run_audio),
        export_frames=False,
        frames_dir=None,
        num_frames=num_frames,
    )

    print(f"[OK] Saved video to {final_path}")
    print(f"  Duration rendered: {actual_duration:.2f}s ({num_frames} frames @ {fps} FPS)")
    print(f"  Audio file: {run_audio}")
    print(f"  Prompt: {run_prompt}")
    print(f"  Audio scale: {audio_scale}, audio FiLM: {audio_film_enabled}, audio gate: {audio_gate_enabled}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render MP4 from SIREN checkpoint")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to *_siren.pth checkpoint")
    parser.add_argument("--output", type=str, required=True, help="Output MP4 path")
    parser.add_argument("--prompt", type=str, default=None, help="Override prompt (defaults to checkpoint prompt)")
    parser.add_argument("--audio", type=str, default=None, help="Override audio path (defaults to checkpoint audio)")
    parser.add_argument("--duration", type=float, default=20.0, help="Seconds to render (0 = full audio)")
    parser.add_argument("--fps", type=int, default=30, help="Render FPS (also used for audio analysis)")
    parser.add_argument("--width", type=int, default=1280, help="Output width")
    parser.add_argument("--height", type=int, default=720, help="Output height")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    render_mp4(
        checkpoint_path=Path(args.checkpoint),
        output_path=Path(args.output),
        prompt=args.prompt,
        audio_path=args.audio,
        duration=args.duration,
        fps=args.fps,
        width=args.width,
        height=args.height,
    )


if __name__ == "__main__":
    main()
