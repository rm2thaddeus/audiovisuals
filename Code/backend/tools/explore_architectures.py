"""
Architecture Matrix Exploration - Phase C Week 1

Systematically test CPPN architectures (2-3 layers × 4-8 hidden dims)
to discover optimal configurations for organic biological patterns.

Ultra-small networks for maximum visual coherence.
Includes text overlay showing architecture parameters on each video.

Usage:
    python explore_architectures.py [--audio path/to/audio.mp3] [--duration 10]
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cppn import CPPN
import torch


# Architecture matrix configuration
ARCHITECTURE_MATRIX = {
    'layers': [2, 3],  # Focus on best performers (2L and 3L)
    'hidden_dims': [4, 6, 8],  # Ultra-small networks for maximum coherence
    'seeds': [42, 123, 456]  # 3 different random seeds per configuration
}


def create_output_directory() -> Path:
    """Create timestamped output directory for this exploration run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent.parent / 'explorations' / 'architecture_matrix' / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_architecture_configs() -> List[Dict]:
    """Generate all architecture configurations to test."""
    configs = []
    config_id = 0
    
    for layers in ARCHITECTURE_MATRIX['layers']:
        for hidden_dim in ARCHITECTURE_MATRIX['hidden_dims']:
            for seed in ARCHITECTURE_MATRIX['seeds']:
                config = {
                    'id': config_id,
                    'layers': layers,
                    'hidden_dim': hidden_dim,
                    'seed': seed,
                    'params': calculate_params(layers, hidden_dim)
                }
                configs.append(config)
                config_id += 1
    
    return configs


def calculate_params(layers: int, hidden_dim: int, input_dim: int = 12, output_dim: int = 3) -> int:
    """Calculate total number of parameters in CPPN."""
    params = 0
    
    # Input layer
    params += (input_dim + 1) * hidden_dim
    
    # Hidden layers
    params += (layers - 1) * (hidden_dim + 1) * hidden_dim
    
    # Output layer
    params += (hidden_dim + 1) * output_dim
    
    return params


def run_generation(config: Dict, audio_path: str, output_path: str, duration: int = 10) -> Dict:
    """
    Run video generation with specific architecture configuration.
    
    Args:
        config: Architecture configuration dict
        audio_path: Path to audio file
        output_path: Path for output video
        duration: Duration of clip in seconds
        
    Returns:
        Dict with generation results and metadata
    """
    print(f"\n{'='*60}")
    print(f"Config {config['id']}: {config['layers']}L × {config['hidden_dim']}D (seed={config['seed']})")
    print(f"Parameters: {config['params']:,}")
    print(f"{'='*60}")
    
    # Build CLI command with text overlay showing architecture
    text_overlay = f"{config['layers']}L × {config['hidden_dim']}D | Seed {config['seed']} | {config['params']:,} params"
    cmd = [
        sys.executable,
        str(Path(__file__).parent.parent / 'cli.py'),
        audio_path,
        output_path,
        '--resolution', '480p',  # Low res for fast exploration
        '--fps', '24',           # Lower FPS for speed
        '--layers', str(config['layers']),
        '--hidden-dim', str(config['hidden_dim']),
        '--seed', str(config['seed']),
        '--duration', str(duration),
        '--text-overlay', text_overlay
    ]
    
    try:
        # Run generation
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check if output file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            
            return {
                'success': True,
                'output_path': output_path,
                'file_size': file_size,
                'stdout': result.stdout[-500:] if len(result.stdout) > 500 else result.stdout,
                'config': config
            }
        else:
            return {
                'success': False,
                'error': 'Output file not created',
                'stdout': result.stdout,
                'stderr': result.stderr,
                'config': config
            }
            
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'error': str(e),
            'stdout': e.stdout,
            'stderr': e.stderr,
            'config': config
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'config': config
        }


def extract_representative_frame(video_path: str, output_path: str, timestamp: float = 5.0):
    """Extract a representative frame from video using ffmpeg."""
    try:
        cmd = [
            'ffmpeg',
            '-ss', str(timestamp),
            '-i', video_path,
            '-vframes', '1',
            '-q:v', '2',
            '-y',  # Overwrite
            output_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"Warning: Failed to extract frame: {e}")
        return False


def generate_exploration_report(configs: List[Dict], results: List[Dict], output_dir: Path):
    """Generate comprehensive exploration report."""
    
    # Summary statistics
    total_configs = len(configs)
    successful = sum(1 for r in results if r['success'])
    failed = total_configs - successful
    
    # Group by architecture (ignoring seed)
    arch_groups = {}
    for result in results:
        if result['success']:
            config = result['config']
            key = f"{config['layers']}L_{config['hidden_dim']}D"
            if key not in arch_groups:
                arch_groups[key] = []
            arch_groups[key].append(result)
    
    # Generate markdown report
    report = f"""# Architecture Matrix Exploration Report

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Status:** {successful}/{total_configs} configurations completed successfully

---

## Matrix Configuration

**Layers tested:** {', '.join(map(str, ARCHITECTURE_MATRIX['layers']))}  
**Hidden dimensions:** {', '.join(map(str, ARCHITECTURE_MATRIX['hidden_dims']))}  
**Seeds per config:** {len(ARCHITECTURE_MATRIX['seeds'])}  
**Total configurations:** {total_configs}

---

## Results Summary

| Layers | Hidden Dim | Params | Seeds Tested | Success | Avg Size (MB) |
|--------|-----------|--------|--------------|---------|---------------|
"""
    
    # Add results for each unique architecture
    for layers in ARCHITECTURE_MATRIX['layers']:
        for hidden_dim in ARCHITECTURE_MATRIX['hidden_dims']:
            key = f"{layers}L_{hidden_dim}D"
            if key in arch_groups:
                group = arch_groups[key]
                avg_size = sum(r['file_size'] for r in group) / len(group) / (1024*1024)
                params = group[0]['config']['params']
                report += f"| {layers} | {hidden_dim} | {params:,} | {len(group)} | ✅ | {avg_size:.1f} |\n"
            else:
                params = calculate_params(layers, hidden_dim)
                report += f"| {layers} | {hidden_dim} | {params:,} | 0 | ❌ | - |\n"
    
    report += f"""
---

## Failed Configurations

"""
    
    if failed > 0:
        for result in results:
            if not result['success']:
                config = result['config']
                report += f"""
### Config {config['id']}: {config['layers']}L × {config['hidden_dim']}D (seed={config['seed']})

**Error:** {result.get('error', 'Unknown error')}

"""
    else:
        report += "None - all configurations succeeded! ✅\n"
    
    report += f"""
---

## Next Steps

1. **Visual Review** - Open videos in `{output_dir.name}` and review visual quality
2. **Rating** - Use `rate_architectures.py` to rate each configuration on:
   - Organic quality (spirals, cells, fluid forms)
   - Coherence (spatial continuity)
   - Audio reactivity (responsiveness)
   - Aesthetic appeal (subjective beauty)
3. **Selection** - Identify top 3-5 configurations for CLIP training
4. **Documentation** - Update ARCHITECTURE_CATALOG.md with findings

---

## Files Generated

**Videos:** {successful} × 10-second clips  
**Frames:** {successful} representative frames (at t=5s)  
**Location:** `{output_dir}`

---

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    # Write report
    report_path = output_dir / 'EXPLORATION_REPORT.md'
    report_path.write_text(report, encoding='utf-8')
    print(f"\nReport saved to: {report_path}")
    
    return report_path


def save_metadata(configs: List[Dict], results: List[Dict], output_dir: Path):
    """Save detailed metadata as JSON."""
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'matrix': ARCHITECTURE_MATRIX,
        'total_configs': len(configs),
        'results': results
    }
    
    metadata_path = output_dir / 'metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Metadata saved to: {metadata_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Systematically explore CPPN architecture space for organic patterns'
    )
    parser.add_argument(
        '--audio',
        type=str,
        default=None,
        help='Path to audio file (default: finds first audio in docs/Audio/)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=10,
        help='Duration of test clips in seconds (default: 10)'
    )
    parser.add_argument(
        '--skip-frames',
        action='store_true',
        help='Skip frame extraction (faster)'
    )
    
    args = parser.parse_args()
    
    # Find audio file
    if args.audio is None:
        # Look for audio in docs/Audio/
        audio_dir = Path(__file__).parent.parent.parent / 'docs' / 'Audio'
        audio_files = list(audio_dir.glob('*.mp3')) + list(audio_dir.glob('*.wav'))
        if audio_files:
            audio_path = str(audio_files[0])
            print(f"Using audio: {audio_path}")
        else:
            print("Error: No audio file found in docs/Audio/")
            print("Please specify --audio path/to/audio.mp3")
            sys.exit(1)
    else:
        audio_path = args.audio
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found: {audio_path}")
            sys.exit(1)
    
    # Create output directory
    output_dir = create_output_directory()
    print(f"\nArchitecture Matrix Exploration")
    print(f"Output directory: {output_dir}")
    print(f"Audio: {audio_path}")
    print(f"Duration: {args.duration}s per clip")
    
    # Generate configurations
    configs = generate_architecture_configs()
    print(f"\nTesting {len(configs)} configurations:")
    print(f"   Layers: {ARCHITECTURE_MATRIX['layers']}")
    print(f"   Hidden dims: {ARCHITECTURE_MATRIX['hidden_dims']}")
    print(f"   Seeds: {ARCHITECTURE_MATRIX['seeds']}")
    print(f"   Total: {len(ARCHITECTURE_MATRIX['layers'])} × {len(ARCHITECTURE_MATRIX['hidden_dims'])} × {len(ARCHITECTURE_MATRIX['seeds'])} = {len(configs)}")
    
    # Run generations
    results = []
    for i, config in enumerate(configs, 1):
        print(f"\n[{i}/{len(configs)}] Processing configuration {config['id']}...")
        
        # Generate output filename
        output_filename = f"arch_{config['layers']}L_{config['hidden_dim']}D_seed{config['seed']}.mp4"
        output_path = str(output_dir / output_filename)
        
        # Run generation
        result = run_generation(config, audio_path, output_path, args.duration)
        results.append(result)
        
        # Extract representative frame
        if result['success'] and not args.skip_frames:
            frame_path = str(output_dir / output_filename.replace('.mp4', '_frame.png'))
            extract_representative_frame(output_path, frame_path)
        
        # Print status
        if result['success']:
            size_mb = result['file_size'] / (1024 * 1024)
            print(f"Success - {size_mb:.1f} MB")
        else:
            print(f"Failed - {result.get('error', 'Unknown error')}")
    
    # Generate report
    print(f"\n{'='*60}")
    print("Generating exploration report...")
    print(f"{'='*60}")
    
    report_path = generate_exploration_report(configs, results, output_dir)
    save_metadata(configs, results, output_dir)
    
    # Final summary
    successful = sum(1 for r in results if r['success'])
    print(f"\n{'='*60}")
    print(f"Exploration Complete!")
    print(f"{'='*60}")
    print(f"Successful: {successful}/{len(configs)}")
    print(f"Output: {output_dir}")
    print(f"Report: {report_path}")
    print(f"\nNext: Review videos and run rate_architectures.py")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()

