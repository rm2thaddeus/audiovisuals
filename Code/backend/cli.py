"""
Audio Feature Explorer - CLI

Command-line interface for generating CPPN audio-reactive visualizations.

Usage:
    python cli.py input.mp3 output.mp4 --resolution 720p --fps 30
    
    python cli.py input.mp3 output.mp4 --resolution 1080p --fps 60 --device cuda
    
    python cli.py input.mp3 output.mp4 --export-frames --evolve 0.005
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch

from audio_analyzer import AudioAnalyzer
from cppn import CPPN
from renderer import Renderer
from video_encoder import VideoEncoder


# Resolution presets
RESOLUTIONS = {
    '360p': (640, 360),
    '480p': (854, 480),
    '720p': (1280, 720),
    '1080p': (1920, 1080),
    '1440p': (2560, 1440),
    '4k': (3840, 2160)
}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate CPPN audio-reactive visualizations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (720p @ 30 FPS)
  python cli.py input.mp3 output.mp4
  
  # High quality (1080p @ 60 FPS)
  python cli.py input.mp3 output.mp4 --resolution 1080p --fps 60
  
  # With frame export and evolution
  python cli.py input.mp3 output.mp4 --export-frames --evolve 0.005
  
  # CPU fallback
  python cli.py input.mp3 output.mp4 --device cpu
"""
    )
    
    # Required arguments
    parser.add_argument('input', type=str, help='Input audio file (MP3, WAV, etc.)')
    parser.add_argument('output', type=str, help='Output video file (MP4)')
    
    # Video settings
    parser.add_argument(
        '--resolution', '-r',
        type=str,
        default='720p',
        choices=list(RESOLUTIONS.keys()),
        help='Output resolution (default: 720p)'
    )
    parser.add_argument(
        '--fps', '-f',
        type=int,
        default=30,
        choices=[24, 30, 60],
        help='Frames per second (default: 30)'
    )
    
    # CPPN settings
    parser.add_argument(
        '--layers', '-l',
        type=int,
        default=4,  # Reduced to 4 layers to preserve temporal/audio information
        help='Number of CPPN layers (default: 4, prevents information loss)'
    )
    parser.add_argument(
        '--hidden-dim', '-d',
        type=int,
        default=256,  # Optimal: 256 hidden dim for RTX 5070
        help='Hidden layer dimension (default: 256, optimal for RTX 5070)'
    )
    parser.add_argument(
        '--evolve', '-e',
        type=float,
        default=0.0,
        help='Weight evolution rate for "living math" effect (default: 0.0, try 0.001-0.01)'
    )
    parser.add_argument(
        '--audio-scale', '-a',
        type=float,
        default=0.05,
        help='Audio feature scaling factor to prevent saturation (default: 0.05, range: 0.01-0.3)'
    )
    
    # Processing settings
    parser.add_argument(
        '--device',
        type=str,
        default='auto',
        choices=['auto', 'cuda', 'cpu'],
        help='Device to use (default: auto)'
    )
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        default=None,
        help='Batch size for rendering (default: auto-optimized for GPU)'
    )
    
    # CLIP-optimized weights
    parser.add_argument(
        '--load-weights',
        type=str,
        default=None,
        help='Path to CLIP-optimized CPPN weights (.pth file from clip_optimize_cppn.py)'
    )
    
    # Export settings
    parser.add_argument(
        '--export-frames',
        action='store_true',
        help='Export individual PNG frames'
    )
    parser.add_argument(
        '--frames-dir',
        type=str,
        default=None,
        help='Directory for exported frames (default: auto)'
    )
    
    # Misc
    parser.add_argument(
        '--no-audio',
        action='store_true',
        help='Generate video without audio track'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_args()
    
    # Print banner
    print("=" * 60)
    print("Audio Feature Explorer - CPPN Visualizer")
    print("Neural evolution beyond MilkDrop presets")
    print("=" * 60)
    print()
    
    # Validate inputs
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    output_path = Path(args.output)
    if output_path.exists():
        response = input(f"Output file exists: {output_path}\nOverwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            sys.exit(0)
    
    # Determine device
    if args.device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if device == 'cuda':
            print(f"[OK] CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("[WARNING] CUDA not available, using CPU")
    else:
        device = args.device
    
    print(f"Device: {device}")
    print()
    
    # Get resolution
    resolution = RESOLUTIONS[args.resolution]
    print(f"Settings:")
    print(f"  Resolution: {resolution[0]}x{resolution[1]} ({args.resolution})")
    print(f"  FPS: {args.fps}")
    print(f"  CPPN layers: {args.layers}")
    print(f"  Hidden dim: {args.hidden_dim}")
    print(f"  Evolution rate: {args.evolve}")
    print()
    
    # Start timer
    start_time = time.time()
    
    try:
        # Step 1: Analyze audio
        print("Step 1/4: Analyzing audio...")
        analyzer = AudioAnalyzer()
        audio_analysis = analyzer.analyze(str(input_path), fps=args.fps)
        
        # Normalize features
        audio_analysis['features'] = analyzer.normalize_features(
            audio_analysis['features'],
            method='minmax'
        )
        
        # Scale audio features to prevent network saturation
        # This is critical: audio features can overwhelm spatial coordinates
        audio_analysis['features'] = audio_analysis['features'] * args.audio_scale

        # Ensure features match device precision early to avoid repeated casting
        feature_dtype = np.float16 if device == 'cuda' else np.float32
        audio_analysis['features'] = audio_analysis['features'].astype(
            feature_dtype,
            copy=False
        )
        
        print(f"[OK] Audio analyzed: {audio_analysis['num_frames']} frames")
        print(f"  Audio features scaled by {args.audio_scale} to prevent saturation")
        print()
        
        # Step 2: Initialize CPPN
        print("Step 2/4: Initializing CPPN...")
        
        # Load CLIP-optimized weights if provided
        if args.load_weights:
            weights_path = Path(args.load_weights)
            if not weights_path.exists():
                print(f"[ERROR] Weights file not found: {weights_path}")
                sys.exit(1)
            
            print(f"[INFO] Loading CLIP-optimized weights from: {weights_path}")
            checkpoint = torch.load(weights_path, map_location=device)
            
            # Handle both old-style (state_dict only) and new-style (dict with metadata)
            if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
                # Use architecture from checkpoint metadata
                if 'cppn_config' in checkpoint:
                    config = checkpoint['cppn_config']
                    cppn = CPPN(
                        input_dim=config['input_dim'],
                        hidden_dim=config['hidden_dim'],
                        num_layers=config['num_layers'],
                        device=device
                    )
                    print(f"[INFO] Using architecture from checkpoint: {config['num_layers']} layers × {config['hidden_dim']} hidden dim")
                else:
                    # Fallback to command-line args
                    cppn = CPPN(
                        input_dim=2 + 1 + audio_analysis['features'].shape[1],
                        hidden_dim=args.hidden_dim,
                        num_layers=args.layers,
                        device=device
                    )
                
                cppn.load_state_dict(checkpoint['state_dict'])
                
                if 'prompt' in checkpoint:
                    print(f"[INFO] Optimized for prompt: '{checkpoint['prompt']}'")
                if 'best_similarity' in checkpoint:
                    print(f"[INFO] CLIP similarity score: {checkpoint['best_similarity']:.4f}")
            else:
                # Old-style: just the state dict
                cppn = CPPN(
                    input_dim=2 + 1 + audio_analysis['features'].shape[1],
                    hidden_dim=args.hidden_dim,
                    num_layers=args.layers,
                    device=device
                )
                cppn.load_state_dict(checkpoint)
            
            print("[OK] Using CLIP-optimized CPPN (not random initialization!)")
        else:
            # Initialize with command-line args (random weights)
            cppn = CPPN(
                input_dim=2 + 1 + audio_analysis['features'].shape[1],  # x, y, time + features
                hidden_dim=args.hidden_dim,
                num_layers=args.layers,
                device=device
            )
            print("[INFO] Using random initialization (untrained CPPN)")
            print("[TIP] Use --load-weights to load CLIP-optimized styles")
        
        print()
        
        # Step 3: Render frames
        print("Step 3/4: Rendering frames...")
        renderer = Renderer(
            cppn,
            resolution=resolution,
            batch_size=None  # Let renderer auto-optimize batch size
        )
        
        # Estimate memory
        if args.verbose:
            memory = renderer.estimate_memory_usage()
            print(f"Memory estimate: {memory['total_per_frame_mb']:.2f} MB per frame")
            print()
        
        frame_iterator = renderer.render_sequence(
            audio_analysis,
            fps=args.fps,
            evolve_rate=args.evolve
        )
        print()
        
        # Step 4: Encode video
        print("Step 4/4: Encoding video...")
        encoder = VideoEncoder(
            str(output_path),
            fps=args.fps
        )
        
        final_video = encoder.encode(
            frame_iterator,
            audio_path=None if args.no_audio else str(input_path),
            export_frames=args.export_frames,
            frames_dir=args.frames_dir,
            num_frames=audio_analysis['num_frames']
        )
        
        # Complete
        elapsed_time = time.time() - start_time
        
        print()
        print("=" * 60)
        print("[OK] Complete!")
        print(f"  Output: {final_video}")
        print(f"  Duration: {audio_analysis['duration']:.2f}s")
        print(f"  Frames: {audio_analysis['num_frames']}")
        print(f"  Processing time: {elapsed_time:.1f}s")
        
        if audio_analysis['duration'] > 0:
            speed_factor = audio_analysis['duration'] / elapsed_time
            print(f"  Speed: {speed_factor:.2f}x realtime")
        
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
