#!/usr/bin/env python3
"""
Regenerate exploration report from existing architecture matrix output.
Useful when the original run generated videos but failed during report creation.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Import functions from explore_architectures
from explore_architectures import (
    generate_exploration_report,
    calculate_params,
    ARCHITECTURE_MATRIX
)


def reconstruct_metadata(output_dir: Path):
    """Reconstruct configs and results from output directory."""
    configs = []
    results = []
    
    config_id = 0
    for layers in ARCHITECTURE_MATRIX['layers']:
        for hidden_dim in ARCHITECTURE_MATRIX['hidden_dims']:
            for seed in ARCHITECTURE_MATRIX['seeds']:
                # Reconstruct config
                config = {
                    'id': config_id,
                    'layers': layers,
                    'hidden_dim': hidden_dim,
                    'seed': seed,
                    'params': calculate_params(layers, hidden_dim)
                }
                configs.append(config)
                
                # Check if video exists
                video_filename = f"arch_{layers}L_{hidden_dim}D_seed{seed}.mp4"
                video_path = output_dir / video_filename
                
                if video_path.exists():
                    file_size = video_path.stat().st_size
                    results.append({
                        'config': config,
                        'success': True,
                        'file_size': file_size,
                        'output_path': str(video_path)
                    })
                else:
                    results.append({
                        'config': config,
                        'success': False,
                        'error': 'Video file not found'
                    })
                
                config_id += 1
    
    return configs, results


def save_metadata(configs, results, output_dir: Path):
    """Save metadata as JSON."""
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
    if len(sys.argv) != 2:
        print("Usage: python regenerate_report.py <output_directory>")
        print("\nExample:")
        print("  python regenerate_report.py ../explorations/architecture_matrix/20251015_213644")
        sys.exit(1)
    
    output_dir = Path(sys.argv[1])
    
    if not output_dir.exists():
        print(f"Error: Directory not found: {output_dir}")
        sys.exit(1)
    
    print(f"\nRegenerating report for: {output_dir}")
    
    # Reconstruct metadata from files
    configs, results = reconstruct_metadata(output_dir)
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"   Found: {successful} successful, {failed} failed")
    
    # Generate report
    print(f"\nGenerating exploration report...")
    report_path = generate_exploration_report(configs, results, output_dir)
    
    # Save metadata
    save_metadata(configs, results, output_dir)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Report regeneration complete!")
    print(f"{'='*60}")
    print(f"Output: {output_dir}")
    print(f"Report: {report_path}")
    print(f"\nNext: Review videos and run rate_architectures.py")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()

