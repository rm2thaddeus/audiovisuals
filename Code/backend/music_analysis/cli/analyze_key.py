"""
CLI command for key detection

Usage:
    python -m music_analysis.cli.analyze_key audio.mp3
    python -m music_analysis.cli.analyze_key audio.mp3 --output results/
    python -m music_analysis.cli.analyze_key audio.mp3 --time-varying
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from music_analysis.analyzers.key_detector import KeyDetector


def main():
    """Main CLI entry point for key detection."""
    parser = argparse.ArgumentParser(
        description='Detect musical key in audio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic key detection
  python -m music_analysis.cli.analyze_key song.mp3
  
  # Save to specific directory
  python -m music_analysis.cli.analyze_key song.mp3 --output results/
  
  # Detect key changes over time
  python -m music_analysis.cli.analyze_key song.mp3 --time-varying
  
  # JSON only (no plots)
  python -m music_analysis.cli.analyze_key song.mp3 --format json
"""
    )
    
    # Required arguments
    parser.add_argument(
        'audio',
        type=str,
        help='Input audio file (MP3, WAV, FLAC, etc.)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output directory (default: music_analysis/outputs/)'
    )
    
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['json', 'plot', 'html', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    
    parser.add_argument(
        '--time-varying',
        action='store_true',
        help='Analyze key changes over time (slower)'
    )
    
    parser.add_argument(
        '--window-size',
        type=float,
        default=30.0,
        help='Window size for time-varying analysis in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--hop-length',
        type=int,
        default=512,
        help='Hop length for chroma extraction (default: 512)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)
    
    # Setup output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = Path(__file__).parent.parent / 'outputs'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run analysis
    if args.verbose:
        mode = "time-varying" if args.time_varying else "global"
        print(f"Analyzing key ({mode}): {audio_path.name}")
    
    try:
        detector = KeyDetector(hop_length=args.hop_length)
        
        if args.time_varying:
            results = detector.analyze_time_varying(
                str(audio_path),
                window_size=args.window_size
            )
        else:
            results = detector.analyze(str(audio_path))
        
        if args.verbose:
            proc_time = results.get('processing_time', 0)
            print(f"[OK] Analysis complete in {proc_time:.2f}s")
    
    except Exception as e:
        print(f"Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Save JSON
    suffix = "_key_timevarying" if args.time_varying else "_key"
    json_path = output_dir / f"{audio_path.stem}{suffix}.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    if args.verbose or args.format == 'json':
        print(f"[OK] JSON saved: {json_path}")
    
    # Generate plots if requested
    if args.format in ['plot', 'both', 'html']:
        try:
            from music_analysis.visualization.plot_key import plot_key
            
            plot_path = output_dir / f"{audio_path.stem}{suffix}.png"
            plot_key(results, str(audio_path), plot_path, args.time_varying)
            
            if args.verbose or args.format == 'plot':
                print(f"[OK] Plot saved: {plot_path}")
        
        except ImportError:
            print("Warning: Visualization module not available. Skipping plots.")
            plot_path = None
        except Exception as e:
            print(f"Warning: Plot generation failed: {e}")
            plot_path = None
    else:
        plot_path = None
    
    # Generate HTML report if requested
    if args.format in ['html', 'both']:
        try:
            from music_analysis.visualization.html_generator import generate_html_report
            
            html_path = output_dir / f"{audio_path.stem}{suffix}.html"
            generate_html_report(
                results,
                str(audio_path),
                html_path,
                plot_path,
                analysis_type='key'
            )
            
            if args.verbose:
                print(f"[OK] HTML report saved: {html_path}")
        
        except ImportError:
            print("Warning: HTML generator not available. Skipping HTML report.")
        except Exception as e:
            print(f"Warning: HTML generation failed: {e}")
    
    # Print summary
    print(f"\n=== Key Detection Results ===")
    print(f"File: {audio_path.name}")
    
    if args.time_varying:
        print(f"Overall Key: {results['overall_key']} {results['overall_scale']}")
        print(f"Key changes detected: {results['num_changes']}")
        print(f"Window size: {results['window_size']}s")
        print(f"Duration: {results['duration']:.1f}s")
    else:
        print(f"Key: {results['key']} {results['scale']}")
        print(f"Confidence: {results['confidence']:.2%}")
        print(f"Relative key: {results['relative_key']}")
        print(f"\nAlternative keys:")
        for alt in results['alternatives']:
            print(f"  - {alt['key']}: {alt['confidence']:.2%}")
        print(f"Duration: {results['duration']:.1f}s")
        print(f"Processing time: {results['processing_time']:.2f}s")
    
    print(f"\nOutputs saved to: {output_dir}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

