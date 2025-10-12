"""
CLI command for audio event classification.

Usage:
    python -m music_analysis.cli.analyze_genre audio.mp3
    python -m music_analysis.cli.analyze_genre audio.mp3 --output results/
    python -m music_analysis.cli.analyze_genre audio.mp3 --window-seconds 10 --overlap 0.25 --top-k 10
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from music_analysis.analyzers.genre_classifier import AudioEventClassifier, DEFAULT_MODEL


def main() -> int:
    """Main CLI entry point for audio event classification."""
    parser = argparse.ArgumentParser(
        description="Detect audio events, instruments, and sound types using Audio Spectrogram Transformer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic classification (detects instruments, vocals, genres, sound types)
  python -m music_analysis.cli.analyze_genre song.mp3

  # Save to specific directory
  python -m music_analysis.cli.analyze_genre song.mp3 --output results/

  # Get more audio event categories (top 15 instead of 10)
  python -m music_analysis.cli.analyze_genre song.mp3 --top-k 15

  # Shorter analysis windows for more detailed timeline
  python -m music_analysis.cli.analyze_genre song.mp3 --window-seconds 5

  # Limit to first few segments for quick preview
  python -m music_analysis.cli.analyze_genre song.mp3 --max-chunks 3

  # Force CPU inference (if GPU unavailable)
  python -m music_analysis.cli.analyze_genre song.mp3 --device cpu --verbose
"""
    )

    parser.add_argument(
        "audio",
        type=str,
        help="Input audio file (MP3, WAV, FLAC, etc.)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output directory (default: music_analysis/outputs/)",
    )
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        choices=["json", "plot", "html", "both"],
        default="both",
        help="Output format (default: both)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of top audio event predictions to keep (default: 10)",
    )
    parser.add_argument(
        "--window-seconds",
        type=float,
        default=10.0,
        help="Analysis window size in seconds (default: 10.0, optimized for AST)",
    )
    parser.add_argument(
        "--overlap",
        type=float,
        default=0.25,
        help="Window overlap ratio between 0.0 and 0.9 (default: 0.25)",
    )
    parser.add_argument(
        "--max-chunks",
        type=int,
        default=None,
        help="Maximum number of analysis chunks to process (default: all)",
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Inference device (default: auto)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"HuggingFace model identifier (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        help="Optional directory for model caching",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"Error: Audio file not found: {audio_path}")
        return 1

    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.device == "auto":
        device = None
    else:
        device = args.device

    if args.verbose:
        print(f"Loading model: {args.model}")
        print(f"Device: {device or 'auto'}")
        print(f"Analyzing: {audio_path.name}")
        print(
            f"Window: {args.window_seconds:.1f}s | "
            f"Overlap: {args.overlap:.2f} | "
            f"Top-K: {args.top_k}"
        )

    try:
        classifier = AudioEventClassifier(
            model_name=args.model,
            device=device,
            cache_dir=args.cache_dir,
        )
        results = classifier.analyze(
            str(audio_path),
            top_k=args.top_k,
            window_seconds=args.window_seconds,
            overlap=args.overlap,
            max_chunks=args.max_chunks,
        )
    except Exception as exc:
        print(f"Error during audio event classification: {exc}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    json_path = output_dir / f"{audio_path.stem}_genre.json"
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=2)

    if args.verbose or args.format == "json":
        print(f"[OK] JSON saved: {json_path}")

    plot_path = None
    if args.format in {"plot", "both", "html"}:
        try:
            from music_analysis.visualization.plot_genre import plot_genre

            plot_path = output_dir / f"{audio_path.stem}_genre.png"
            plot_genre(results, str(audio_path), plot_path)
            if args.verbose or args.format == "plot":
                print(f"[OK] Plot saved: {plot_path}")
        except ImportError:
            print("Warning: Visualization module not available. Skipping plots.")
        except Exception as exc:
            print(f"Warning: Plot generation failed: {exc}")
            if args.verbose:
                import traceback

                traceback.print_exc()
            plot_path = None

    if args.format in {"html", "both"}:
        try:
            from music_analysis.visualization.html_generator import (
                generate_html_report,
            )

            html_path = output_dir / f"{audio_path.stem}_genre.html"
            generate_html_report(
                results,
                str(audio_path),
                html_path,
                plot_path,
                analysis_type="genre",
            )
            if args.verbose:
                print(f"[OK] HTML report saved: {html_path}")
        except ImportError:
            print("Warning: HTML generator not available. Skipping HTML report.")
        except Exception as exc:
            print(f"Warning: HTML generation failed: {exc}")
            if args.verbose:
                import traceback

                traceback.print_exc()

    top_label = results["primary_label"]
    confidence = results["primary_confidence"] * 100

    print("\n=== Audio Event Classification Results ===")
    print(f"File: {audio_path.name}")
    print(f"Primary Event: {top_label} ({confidence:.1f}%)")
    print(f"\nTop {args.top_k} Detected Events:")
    for entry in results["predictions"]:
        print(f"  - {entry['label']}: {entry['score'] * 100:.1f}%")

    print(f"\nChunks analyzed: {len(results['chunk_predictions'])}")
    print(f"Total event classes available: {results['num_labels']}")
    print(f"Processing time: {results['processing_time']:.2f}s")
    print(f"Outputs saved to: {output_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

