"""
Compute mean absolute frame-to-frame difference (flicker metric) for MP4.
"""

import argparse
import json
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np


def read_video(path: str, resize: Tuple[int, int] = (256, 256)):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {path}")
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if resize is not None:
            frame = cv2.resize(frame, resize, interpolation=cv2.INTER_AREA)
        frames.append(frame.astype(np.float32) / 255.0)
    cap.release()
    if len(frames) < 2:
        raise ValueError("Video must have at least 2 frames for flicker metric")
    return np.stack(frames, axis=0)


def flicker(frames: np.ndarray) -> float:
    diffs = np.abs(np.diff(frames, axis=0))
    return float(diffs.mean())


def main() -> None:
    parser = argparse.ArgumentParser(description="Flicker metric: mean |frame diff|")
    parser.add_argument("video", type=str, help="Input MP4")
    parser.add_argument("--resize", type=int, default=256, help="Resize shorter side to this value")
    parser.add_argument("--output", type=str, default=None, help="Optional JSON output path")
    args = parser.parse_args()

    frames = read_video(args.video, resize=(args.resize, args.resize))
    metric = flicker(frames)
    result = {"video": args.video, "flicker": metric}
    print(json.dumps(result, indent=2))

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()


