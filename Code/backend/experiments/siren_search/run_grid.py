"""
Tiny-grid runner for SIREN CLIP optimization.

Executes multiple configs of clip_optimize_siren.py and writes a summary CSV/JSON.
"""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import List


def build_grid() -> List[dict]:
    depths = [2, 3, 4]
    widths = [4, 6, 8, 12]
    w0_first = [30.0, 50.0]
    w0_hidden = [1.0, 10.0]
    grid = []
    for d in depths:
        for w in widths:
            for w0f in w0_first:
                for w0h in w0_hidden:
                    grid.append(
                        {
                            "depth": d,
                            "width": w,
                            "w0_first": w0f,
                            "w0_hidden": w0h,
                        }
                    )
    return grid


def run_config(args: argparse.Namespace, cfg: dict, out_dir: Path) -> dict:
    run_name = f"d{cfg['depth']}_w{cfg['width']}_w0f{int(cfg['w0_first'])}_w0h{int(cfg['w0_hidden'])}"
    cmd = [
        sys.executable,
        "Code/backend/clip_optimize_siren.py",
        "--prompt",
        args.prompt,
        "--audio",
        args.audio,
        "--output-dir",
        str(out_dir),
        "--run-name",
        run_name,
        "--depth",
        str(cfg["depth"]),
        "--width",
        str(cfg["width"]),
        "--w0-first",
        str(cfg["w0_first"]),
        "--w0-hidden",
        str(cfg["w0_hidden"]),
        "--steps",
        str(args.steps),
        "--train-resolution",
        str(args.train_resolution),
        "--clip-model",
        args.clip_model,
        "--device",
        args.device,
        "--num-crops",
        str(args.num_crops),
    ]
    if args.amp:
        cmd.append("--amp")

    print(f"[GRID] Running {run_name}")
    subprocess.run(cmd, check=True)

    history_path = out_dir / f"{run_name}_history.json"
    best_similarity = None
    if history_path.exists():
        with open(history_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            best_similarity = data.get("best_similarity", None)

    ckpt_path = out_dir / f"{run_name}_siren.pth"
    return {
        "run_name": run_name,
        "best_similarity": best_similarity,
        "checkpoint": str(ckpt_path),
        **cfg,
    }


def write_summary(entries: List[dict], out_dir: Path) -> None:
    csv_path = out_dir / "summary.csv"
    json_path = out_dir / "summary.json"
    fields = ["run_name", "best_similarity", "depth", "width", "w0_first", "w0_hidden", "checkpoint"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(entries)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    print(f"[GRID] Summary written to {csv_path} and {json_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SIREN grid search")
    parser.add_argument("--prompt", type=str, required=True, help="Text prompt")
    parser.add_argument("--audio", type=str, default="docs/Audio/TOOL - The Pot (Audio).mp3")
    parser.add_argument("--output-dir", type=str, default="Code/backend/experiments/siren_search")
    parser.add_argument("--steps", type=int, default=200, help="Steps per config")
    parser.add_argument("--train-resolution", type=int, default=256)
    parser.add_argument("--clip-model", type=str, default="ViT-B/32")
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--num-crops", type=int, default=4)
    parser.add_argument("--amp", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    for cfg in build_grid():
        result = run_config(args, cfg, out_dir)
        entries.append(result)

    write_summary(entries, out_dir)


if __name__ == "__main__":
    main()


