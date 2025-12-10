"""
Evaluate CLIP text-image similarity on sampled frames from an MP4.
"""

import argparse
import json
from pathlib import Path
from typing import List

import clip
import cv2
import numpy as np
import torch


def sample_frames(video_path: str, num_samples: int, target_size: int = 256) -> List[np.ndarray]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}")
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = np.linspace(0, max(0, total_frames - 1), num_samples).astype(int)
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (target_size, target_size), interpolation=cv2.INTER_AREA)
        frames.append(frame.astype(np.float32) / 255.0)
    cap.release()
    if not frames:
        raise ValueError("No frames sampled")
    return frames


def clip_score(frames: List[np.ndarray], prompt: str, clip_model: str, device: torch.device) -> float:
    model, _ = clip.load(clip_model, device=device)
    model.eval()

    text_tokens = clip.tokenize([prompt]).to(device)
    with torch.no_grad():
        text_feat = model.encode_text(text_tokens)
        text_feat = text_feat / text_feat.norm(dim=-1, keepdim=True)

    images = torch.tensor(np.stack(frames), device=device)
    images = images.permute(0, 3, 1, 2)  # NCHW

    mean = torch.tensor([0.48145466, 0.4578275, 0.40821073], device=device).view(1, 3, 1, 1)
    std = torch.tensor([0.26862954, 0.26130258, 0.27577711], device=device).view(1, 3, 1, 1)
    images = (images - mean) / std

    with torch.no_grad():
        img_feat = model.encode_image(images)
        img_feat = img_feat / img_feat.norm(dim=-1, keepdim=True)
        sim = (img_feat @ text_feat.T).squeeze(-1)
    return float(sim.mean().item())


def main() -> None:
    parser = argparse.ArgumentParser(description="CLIP score on sampled frames")
    parser.add_argument("video", type=str, help="Video path")
    parser.add_argument("--prompt", type=str, required=True, help="Text prompt")
    parser.add_argument("--clip-model", type=str, default="ViT-B/32")
    parser.add_argument("--samples", type=int, default=8, help="Number of frames to sample")
    parser.add_argument("--device", type=str, default="auto", choices=["auto", "cuda", "cpu"])
    parser.add_argument("--output", type=str, default=None, help="Optional JSON output path")
    args = parser.parse_args()

    device = torch.device("cuda" if args.device == "cuda" and torch.cuda.is_available() else "cpu")
    frames = sample_frames(args.video, num_samples=args.samples)
    score = clip_score(frames, prompt=args.prompt, clip_model=args.clip_model, device=device)

    result = {"video": args.video, "prompt": args.prompt, "clip_model": args.clip_model, "score": score}
    print(json.dumps(result, indent=2))
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()


