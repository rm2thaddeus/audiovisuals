"""
CLI command for tempo analysis

Usage:
    python -m music_analysis.cli.analyze_tempo audio.mp3
    python -m music_analysis.cli.analyze_tempo audio.mp3 --output results/
    python -m music_analysis.cli.analyze_tempo audio.mp3 --format json
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from music_analysis.analyzers.tempo_analyzer import TempoAnalyzer


def main():
    """Main CLI entry point for tempo analysis."""
    parser = argparse.ArgumentParser(
        description='Analyze tempo and beat positions in audio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python -m music_analysis.cli.analyze_tempo song.mp3
  
  # Save to specific directory
  python -m music_analysis.cli.analyze_tempo song.mp3 --output results/
  
  # JSON only (no plots)
  python -m music_analysis.cli.analyze_tempo song.mp3 --format json
  
  # Specify initial BPM estimate
  python -m music_analysis.cli.analyze_tempo song.mp3 --start-bpm 140
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
        '--start-bpm',
        type=float,
        default=120.0,
        help='Initial BPM estimate for tracking (default: 120)'
    )
    
    parser.add_argument(
        '--hop-length',
        type=int,
        default=512,
        help='Hop length for analysis (default: 512)'
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
        print(f"Analyzing tempo: {audio_path.name}")
        print(f"Start BPM estimate: {args.start_bpm}")
    
    try:
        analyzer = TempoAnalyzer(hop_length=args.hop_length)
        results = analyzer.analyze(
            str(audio_path),
            start_bpm=args.start_bpm
        )
        
        if args.verbose:
            print(f"[OK] Analysis complete in {results['processing_time']:.2f}s")
    
    except Exception as e:
        print(f"Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Save JSON
    json_path = output_dir / f"{audio_path.stem}_tempo.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    if args.verbose or args.format == 'json':
        print(f"[OK] JSON saved: {json_path}")
    
    # Generate plots if requested
    if args.format in ['plot', 'both', 'html']:
        try:
            from music_analysis.visualization.plot_tempo import plot_tempo
            
            plot_path = output_dir / f"{audio_path.stem}_tempo.png"
            plot_tempo(results, str(audio_path), plot_path)
            
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
            
            html_path = output_dir / f"{audio_path.stem}_tempo.html"
            generate_html_report(
                results,
                str(audio_path),
                html_path,
                plot_path,
                analysis_type='tempo'
            )
            
            if args.verbose:
                print(f"[OK] HTML report saved: {html_path}")
        
        except ImportError:
            print("Warning: HTML generator not available. Skipping HTML report.")
        except Exception as e:
            print(f"Warning: HTML generation failed: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    # Print summary
    print(f"\n=== Tempo Analysis Results ===")
    print(f"File: {audio_path.name}")
    print(f"Tempo: {results['tempo']} BPM")
    print(f"Confidence: {results['tempo_confidence']:.2%}")
    print(f"Time Signature: {results['time_signature']}")
    print(f"Beats detected: {results['num_beats']}")
    print(f"Duration: {results['duration']:.1f}s")
    print(f"Processing time: {results['processing_time']:.2f}s")
    print(f"\nOutputs saved to: {output_dir}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

