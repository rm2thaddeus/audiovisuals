"""
CLI command for music structure analysis

Usage:
    python -m music_analysis.cli.analyze_structure audio.mp3
    python -m music_analysis.cli.analyze_structure audio.mp3 --output results/
    python -m music_analysis.cli.analyze_structure audio.mp3 --algorithm cnmf
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from music_analysis.analyzers.structure_analyzer import StructureAnalyzer


def main():
    """Main CLI entry point for structure analysis."""
    parser = argparse.ArgumentParser(
        description='Analyze music structure and detect segment boundaries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic structure analysis
  python -m music_analysis.cli.analyze_structure song.mp3
  
  # Save to specific directory
  python -m music_analysis.cli.analyze_structure song.mp3 --output results/
  
  # Use different algorithm
  python -m music_analysis.cli.analyze_structure song.mp3 --algorithm foote
  
  # JSON only (no plots)
  python -m music_analysis.cli.analyze_structure song.mp3 --format json
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
        '--algorithm',
        type=str,
        default='cnmf',
        choices=['cnmf', 'foote', 'olda', 'scluster', 'sf'],
        help='Segmentation algorithm (default: cnmf)'
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
        print(f"Analyzing structure: {audio_path.name}")
        print(f"Algorithm: {args.algorithm}")
    
    try:
        analyzer = StructureAnalyzer()
        results = analyzer.analyze(
            str(audio_path),
            algorithm=args.algorithm
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
    json_path = output_dir / f"{audio_path.stem}_structure.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    if args.verbose or args.format == 'json':
        print(f"[OK] JSON saved: {json_path}")
    
    # Generate plots if requested
    if args.format in ['plot', 'both', 'html']:
        try:
            from music_analysis.visualization.plot_structure import plot_structure
            
            plot_path = output_dir / f"{audio_path.stem}_structure.png"
            plot_structure(results, str(audio_path), plot_path)
            
            if args.verbose or args.format == 'plot':
                print(f"[OK] Plot saved: {plot_path}")
        
        except ImportError:
            print("Warning: Visualization module not available. Skipping plots.")
            plot_path = None
        except Exception as e:
            print(f"Warning: Plot generation failed: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            plot_path = None
    else:
        plot_path = None
    
    # Generate HTML report if requested
    if args.format in ['html', 'both']:
        try:
            from music_analysis.visualization.html_generator import generate_html_report
            
            html_path = output_dir / f"{audio_path.stem}_structure.html"
            generate_html_report(
                results,
                str(audio_path),
                html_path,
                plot_path,
                analysis_type='structure'
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
    print(f"\n=== Structure Analysis Results ===")
    print(f"File: {audio_path.name}")
    print(f"Algorithm: {results['algorithm']}")
    print(f"Segments detected: {results['num_segments']}")
    print(f"Duration: {results['duration']:.1f}s")
    print(f"Processing time: {results['processing_time']:.2f}s")
    
    print(f"\nSegment breakdown:")
    for i, seg in enumerate(results['segments'][:10]):  # Show first 10
        print(f"  {i+1}. {seg['start']:.1f}s - {seg['end']:.1f}s: {seg['label']} ({seg['duration']:.1f}s)")
    
    if len(results['segments']) > 10:
        print(f"  ... and {len(results['segments']) - 10} more segments")
    
    print(f"\nOutputs saved to: {output_dir}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())


