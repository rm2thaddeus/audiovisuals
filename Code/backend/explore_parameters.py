"""
Parameter Exploration Tool for CPPN Audio Visualizer

Generates multiple short videos with different CPPN configurations
to explore the parameter space and find interesting visual styles.
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

# Parameter presets to explore
PRESETS = {
    "organic_flow": {
        "layers": 4,
        "hidden_dim": 256,
        "audio_scale": 0.05,
        "evolve": 0.0,
        "description": "Smooth organic patterns"
    },
    "geometric": {
        "layers": 8,
        "hidden_dim": 128,
        "audio_scale": 0.08,
        "evolve": 0.0,
        "description": "More complex geometric structures"
    },
    "reactive_simple": {
        "layers": 3,
        "hidden_dim": 512,
        "audio_scale": 0.15,
        "evolve": 0.0,
        "description": "Fewer layers, stronger audio response"
    },
    "deep_subtle": {
        "layers": 6,
        "hidden_dim": 256,
        "audio_scale": 0.03,
        "evolve": 0.0,
        "description": "Deep network, subtle audio modulation"
    },
    "living_math": {
        "layers": 4,
        "hidden_dim": 256,
        "audio_scale": 0.05,
        "evolve": 0.003,
        "description": "Evolving weights for 'living' patterns"
    },
    "high_contrast": {
        "layers": 5,
        "hidden_dim": 384,
        "audio_scale": 0.12,
        "evolve": 0.001,
        "description": "High dimensional with evolution"
    },
    "minimal": {
        "layers": 2,
        "hidden_dim": 128,
        "audio_scale": 0.10,
        "evolve": 0.0,
        "description": "Minimal complexity, pure shapes"
    },
    "maximal": {
        "layers": 8,
        "hidden_dim": 512,
        "audio_scale": 0.05,
        "evolve": 0.002,
        "description": "Maximum complexity and detail"
    }
}


def run_generation(audio_path, output_path, preset_name, params, resolution="480p", fps=24):
    """Run CLI with specific parameters"""
    
    cmd = [
        "python", "cli.py",
        str(audio_path),
        str(output_path),
        "--resolution", resolution,
        "--fps", str(fps),
        "--layers", str(params["layers"]),
        "--hidden-dim", str(params["hidden_dim"]),
        "--audio-scale", str(params["audio_scale"]),
        "--evolve", str(params["evolve"])
    ]
    
    print(f"\n{'='*60}")
    print(f"Preset: {preset_name}")
    print(f"Description: {params['description']}")
    print(f"Parameters: layers={params['layers']}, dim={params['hidden_dim']}, "
          f"audio_scale={params['audio_scale']}, evolve={params['evolve']}")
    print(f"{'='*60}\n")
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating {preset_name}: {e}")
        return False


def main():
    """Generate exploration videos"""
    
    # Setup
    output_dir = Path("explorations")
    output_dir.mkdir(exist_ok=True)
    
    # Timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / timestamp
    run_dir.mkdir(exist_ok=True)
    
    # Audio files to test
    audio_files = [
        "../../docs/Audio/TOOL - The Pot (Audio).mp3",
        "../../docs/Audio/Zyryab.mp3"
    ]
    
    # Check which audio files exist
    available_audio = []
    for audio in audio_files:
        audio_path = Path(audio)
        if audio_path.exists():
            available_audio.append(audio_path)
            print(f"✓ Found: {audio_path.name}")
        else:
            print(f"✗ Not found: {audio_path}")
    
    if not available_audio:
        print("\nNo audio files found!")
        return
    
    # Use first available audio (or you can loop through all)
    audio_path = available_audio[0]
    print(f"\nUsing: {audio_path.name}")
    
    # Generate with each preset
    results = {}
    for preset_name, params in PRESETS.items():
        output_path = run_dir / f"{preset_name}.mp4"
        
        success = run_generation(
            audio_path,
            output_path,
            preset_name,
            params,
            resolution="480p",  # Small for fast generation
            fps=24              # Lower FPS for speed
        )
        
        results[preset_name] = {
            "success": success,
            "params": params,
            "output": str(output_path)
        }
    
    # Save results summary
    summary_path = run_dir / "exploration_summary.json"
    with open(summary_path, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "audio_file": str(audio_path),
            "presets": results
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Exploration complete!")
    print(f"Results saved to: {run_dir}")
    print(f"Summary: {summary_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

