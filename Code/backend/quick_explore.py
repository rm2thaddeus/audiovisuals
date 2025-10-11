"""
Quick Parameter Exploration - Generate short test clips

Cuts audio into segments and generates multiple visual variations
for rapid parameter space exploration.
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
import librosa
import soundfile as sf
import numpy as np


def cut_audio_segments(audio_path, output_dir, segment_duration=15, num_segments=3):
    """
    Cut audio into interesting segments.
    
    Tries to find segments with varied characteristics (quiet, loud, mid).
    """
    print(f"Loading audio: {audio_path.name}...")
    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    total_duration = len(y) / sr
    
    print(f"Total duration: {total_duration:.1f}s")
    
    # Compute RMS energy to find interesting segments
    hop_length = 512
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
    
    # Smooth RMS
    from scipy.ndimage import gaussian_filter1d
    rms_smooth = gaussian_filter1d(rms, sigma=10)
    
    # Find segments with different energy levels
    segments = []
    
    # 1. High energy segment (loud/intense)
    high_energy_idx = np.argmax(rms_smooth)
    high_energy_time = times[high_energy_idx]
    
    # 2. Low energy segment (quiet/calm)
    low_energy_idx = np.argmin(rms_smooth)
    low_energy_time = times[low_energy_idx]
    
    # 3. Mid energy segment (balanced)
    median_energy = np.median(rms_smooth)
    mid_energy_idx = np.argmin(np.abs(rms_smooth - median_energy))
    mid_energy_time = times[mid_energy_idx]
    
    # 4. Beginning
    start_time = 30  # Skip intro
    
    # 5. Transition (high change in energy)
    energy_diff = np.abs(np.diff(rms_smooth))
    transition_idx = np.argmax(energy_diff)
    transition_time = times[transition_idx]
    
    segment_info = [
        ("start", start_time, "Beginning section"),
        ("quiet", max(0, low_energy_time - segment_duration/2), "Quiet/calm section"),
        ("intense", max(0, high_energy_time - segment_duration/2), "Loud/intense section"),
        ("mid", max(0, mid_energy_time - segment_duration/2), "Mid-energy section"),
        ("transition", max(0, transition_time - segment_duration/2), "Energy transition")
    ]
    
    # Limit to num_segments
    segment_info = segment_info[:num_segments]
    
    # Cut and save segments
    output_dir.mkdir(exist_ok=True, parents=True)
    segment_paths = []
    
    for name, start_time, description in segment_info:
        # Ensure we don't go past the end
        if start_time + segment_duration > total_duration:
            start_time = max(0, total_duration - segment_duration)
        
        start_sample = int(start_time * sr)
        end_sample = int((start_time + segment_duration) * sr)
        
        segment = y[start_sample:end_sample]
        
        output_path = output_dir / f"{audio_path.stem}_{name}_{int(segment_duration)}s.wav"
        sf.write(str(output_path), segment, sr)
        
        segment_paths.append({
            "path": output_path,
            "name": name,
            "description": description,
            "start_time": start_time,
            "duration": len(segment) / sr
        })
        
        print(f"  [OK] {name}: {start_time:.1f}s-{start_time+segment_duration:.1f}s ({description})")
    
    return segment_paths


def generate_variations(audio_segment, output_dir, quick_mode=True):
    """Generate multiple CPPN variations for a single audio segment"""
    
    # Quick test presets (optimized for speed and variety)
    presets = {
        "simple": {
            "layers": 3,
            "hidden_dim": 128,
            "audio_scale": 0.05,
            "evolve": 0.0,
            "desc": "Simple patterns"
        },
        "reactive": {
            "layers": 4,
            "hidden_dim": 256,
            "audio_scale": 0.15,
            "evolve": 0.0,
            "desc": "Strong audio response"
        },
        "complex": {
            "layers": 6,
            "hidden_dim": 256,
            "audio_scale": 0.05,
            "evolve": 0.0,
            "desc": "Complex structures"
        },
        "evolving": {
            "layers": 4,
            "hidden_dim": 256,
            "audio_scale": 0.08,
            "evolve": 0.005,
            "desc": "Living patterns"
        }
    }
    
    if quick_mode:
        # Even faster for initial exploration
        resolution = "360p"
        fps = 24
    else:
        resolution = "480p"
        fps = 30
    
    results = []
    segment_name = audio_segment["name"]
    
    for preset_name, params in presets.items():
        output_path = output_dir / f"{segment_name}_{preset_name}.mp4"
        
        cmd = [
            "python", "cli.py",
            str(audio_segment["path"]),
            str(output_path),
            "--resolution", resolution,
            "--fps", str(fps),
            "--layers", str(params["layers"]),
            "--hidden-dim", str(params["hidden_dim"]),
            "--audio-scale", str(params["audio_scale"]),
            "--evolve", str(params["evolve"])
        ]
        
        print(f"\n  => {preset_name}: {params['desc']}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            results.append({
                "preset": preset_name,
                "params": params,
                "output": str(output_path),
                "success": True
            })
            print(f"    [OK] Generated: {output_path.name}")
        except subprocess.CalledProcessError as e:
            print(f"    [ERROR] Failed: {e}")
            results.append({
                "preset": preset_name,
                "params": params,
                "output": str(output_path),
                "success": False
            })
    
    return results


def create_comparison_html(exploration_dir, segments_info, results):
    """Create an HTML page to compare results"""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>CPPN Parameter Exploration</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        h1 { color: #4CAF50; }
        h2 { color: #2196F3; margin-top: 40px; }
        .segment-section {
            border: 2px solid #333;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            background: #2a2a2a;
        }
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .video-card {
            background: #333;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #444;
        }
        .video-card h3 {
            margin-top: 0;
            color: #FFC107;
        }
        .params {
            font-size: 0.9em;
            color: #aaa;
            margin: 10px 0;
        }
        video {
            width: 100%;
            border-radius: 4px;
            background: #000;
        }
        .description {
            color: #999;
            font-style: italic;
            margin: 10px 0;
        }
        .info { color: #4CAF50; }
    </style>
</head>
<body>
    <h1>CPPN Parameter Exploration</h1>
    <p class="info">Exploring untrained network behavior with different parameters</p>
"""
    
    for segment in segments_info:
        segment_name = segment["name"]
        segment_results = [r for r in results if segment_name in str(r.get("output", ""))]
        
        html += f"""
    <div class="segment-section">
        <h2>Segment: {segment_name.title()}</h2>
        <p class="description">{segment["description"]} (starts at {segment["start_time"]:.1f}s)</p>
        
        <div class="video-grid">
"""
        
        for result in segment_results:
            if result.get("success"):
                preset = result["preset"]
                params = result["params"]
                video_path = Path(result["output"]).name
                
                html += f"""
            <div class="video-card">
                <h3>{preset.title()}</h3>
                <p class="description">{params['desc']}</p>
                <video controls loop preload="metadata">
                    <source src="{video_path}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <div class="params">
                    Layers: {params['layers']}, 
                    Dim: {params['hidden_dim']}, 
                    Audio: {params['audio_scale']}, 
                    Evolve: {params['evolve']}
                </div>
            </div>
"""
        
        html += """
        </div>
    </div>
"""
    
    html += """
    <h2>Notes</h2>
    <ul>
        <li>All networks are <strong>randomly initialized</strong> (not trained)</li>
        <li>Patterns vary based on parameter configuration</li>
        <li>Audio reactivity comes from injecting audio features as inputs</li>
        <li>Different seeds would produce completely different patterns</li>
    </ul>
</body>
</html>
"""
    
    html_path = exploration_dir / "comparison.html"
    with open(html_path, 'w') as f:
        f.write(html)
    
    print(f"\n[OK] Comparison page created: {html_path}")
    return html_path


def main():
    """Main exploration workflow"""
    
    print("=" * 60)
    print("CPPN Parameter Exploration - Quick Test")
    print("=" * 60)
    
    # Find audio files
    audio_files = [
        Path("../../docs/Audio/TOOL - The Pot (Audio).mp3"),
        Path("../../docs/Audio/Zyryab.mp3")
    ]
    
    available = [f for f in audio_files if f.exists()]
    
    if not available:
        print("No audio files found!")
        return
    
    print(f"\nAvailable audio:")
    for i, audio in enumerate(available):
        print(f"  {i+1}. {audio.name}")
    
    # Use first audio or prompt user
    audio_path = available[0]
    print(f"\nUsing: {audio_path.name}\n")
    
    # Create exploration directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exploration_dir = Path(f"explorations/quick_{timestamp}")
    segments_dir = exploration_dir / "segments"
    
    # Step 1: Cut audio into segments
    print("Step 1: Cutting audio into segments...")
    segments = cut_audio_segments(
        audio_path,
        segments_dir,
        segment_duration=10,  # 10 second clips for speed
        num_segments=3        # 3 varied segments
    )
    
    # Step 2: Generate variations for each segment
    print("\nStep 2: Generating CPPN variations...")
    all_results = []
    
    for segment in segments:
        print(f"\nProcessing segment: {segment['name']} ({segment['description']})")
        results = generate_variations(segment, exploration_dir, quick_mode=True)
        all_results.extend(results)
    
    # Step 3: Create comparison page
    print("\nStep 3: Creating comparison page...")
    html_path = create_comparison_html(exploration_dir, segments, all_results)
    
    # Summary
    print("\n" + "=" * 60)
    print("[OK] Exploration Complete!")
    print("=" * 60)
    print(f"Output directory: {exploration_dir}")
    print(f"Comparison page: {html_path}")
    print(f"\nGenerated:")
    print(f"  - {len(segments)} audio segments")
    print(f"  - {len(all_results)} video variations")
    print(f"\nOpen {html_path.name} in your browser to compare results!")
    print("=" * 60)


if __name__ == "__main__":
    main()

