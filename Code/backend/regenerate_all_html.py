"""
Regenerate comparison HTML for all exploration directories
Creates fresh HTML files with proper video embedding
"""

from pathlib import Path
import sys

def create_html(exploration_dir):
    """Generate fresh HTML comparison page"""
    
    # Check if directory has video files
    video_files = list(exploration_dir.glob("*.mp4"))
    if not video_files:
        print(f"  [SKIP] No videos in {exploration_dir.name}")
        return False
    
    print(f"  [GENERATING] {exploration_dir.name}...")
    
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
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
        h1 { 
            color: #4CAF50; 
            text-align: center;
        }
        h2 { 
            color: #2196F3; 
            margin-top: 40px;
            border-bottom: 2px solid #2196F3;
            padding-bottom: 10px;
        }
        .segment-section {
            border: 2px solid #333;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            background: #2a2a2a;
        }
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .video-card {
            background: #333;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #444;
            transition: transform 0.2s;
        }
        .video-card:hover {
            transform: translateY(-5px);
            border-color: #FFC107;
        }
        .video-card h3 {
            margin-top: 0;
            color: #FFC107;
            font-size: 1.2em;
        }
        .params {
            font-size: 0.85em;
            color: #aaa;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
        }
        .param-line {
            margin: 3px 0;
        }
        video {
            width: 100%;
            height: auto;
            max-height: 280px;
            border-radius: 4px;
            background: #000;
            display: block;
        }
        .description {
            color: #999;
            font-style: italic;
            margin: 10px 0;
            font-size: 0.9em;
        }
        .info { 
            color: #4CAF50;
            text-align: center;
            font-size: 1.1em;
        }
        .notes {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            margin-top: 40px;
        }
        .notes ul {
            list-style-type: none;
            padding-left: 0;
        }
        .notes li {
            margin: 10px 0;
            padding-left: 30px;
            position: relative;
        }
        .notes li:before {
            content: "→";
            position: absolute;
            left: 0;
            color: #4CAF50;
        }
    </style>
</head>
<body>
    <h1>CPPN Parameter Exploration</h1>
    <p class="info">Exploring untrained network behavior with different parameters</p>
    <p class="info" style="font-size: 0.9em; color: #999;">Generated: """ + exploration_dir.name.replace("quick_", "") + """</p>
"""
    
    # Define segments and presets
    segments = [
        {"name": "start", "description": "Beginning section", "start_time": 30.0},
        {"name": "quiet", "description": "Quiet/calm section", "start_time": 0.0},
        {"name": "intense", "description": "Loud/intense section", "start_time": 364.2}
    ]
    
    presets = [
        ("simple", "Simple patterns", 3, 128, 0.05, 0.0),
        ("reactive", "Strong audio response", 4, 256, 0.15, 0.0),
        ("complex", "Complex structures", 6, 256, 0.05, 0.0),
        ("evolving", "Living patterns", 4, 256, 0.08, 0.005)
    ]
    
    # Generate sections
    for segment in segments:
        segment_name = segment["name"]
        
        # Check if this segment has videos
        segment_videos = [v for v in video_files if segment_name in v.name]
        if not segment_videos:
            continue
        
        html += f"""
    <div class="segment-section">
        <h2>Segment: {segment_name.title()}</h2>
        <p class="description">{segment["description"]} (starts at {segment["start_time"]:.1f}s in original track)</p>
        
        <div class="video-grid">
"""
        
        for preset_name, desc, layers, hidden_dim, audio_scale, evolve in presets:
            video_file = f"{segment_name}_{preset_name}.mp4"
            video_path = exploration_dir / video_file
            
            # Only add if video exists
            if video_path.exists():
                # Use direct src attribute (more compatible than source tag)
                html += f"""
            <div class="video-card">
                <h3>{preset_name.title()}</h3>
                <p class="description">{desc}</p>
                <video width="640" height="360" controls loop preload="metadata" src="{video_file}">
                    Your browser does not support the video tag. 
                    <a href="{video_file}">Download video</a>
                </video>
                <div class="params">
                    <div class="param-line">Layers: {layers}</div>
                    <div class="param-line">Hidden Dim: {hidden_dim}</div>
                    <div class="param-line">Audio Scale: {audio_scale}</div>
                    <div class="param-line">Evolution: {evolve}</div>
                </div>
            </div>
"""
        
        html += """
        </div>
    </div>
"""
    
    html += """
    <div class="notes">
        <h2>Important Notes</h2>
        <ul>
            <li>All networks are <strong>randomly initialized</strong> (not trained)</li>
            <li>Patterns are mathematical artifacts from random weight initialization</li>
            <li>Audio reactivity comes from injecting audio features as network inputs</li>
            <li>Different random seeds produce completely different patterns</li>
            <li>This is parameter exploration of an untrained network</li>
        </ul>
        <p style="margin-top: 20px; color: #999;">
            <strong>Note:</strong> If videos don't play, try opening in Chrome or Firefox. 
            You can also click on any video filename to download and play locally.
        </p>
    </div>
    
    <div style="text-align: center; margin-top: 40px; color: #666;">
        <p>Generated with CPPN Audio Visualizer - Phase A POC</p>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    output_path = exploration_dir / "comparison.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"    [OK] Created {output_path}")
    return True


def main():
    """Regenerate HTML for all explorations"""
    
    explorations_dir = Path("explorations")
    
    if not explorations_dir.exists():
        print("No explorations directory found!")
        return
    
    # Find all exploration directories
    exploration_dirs = [d for d in explorations_dir.iterdir() if d.is_dir()]
    
    if not exploration_dirs:
        print("No exploration directories found!")
        return
    
    print(f"\nFound {len(exploration_dirs)} exploration directories")
    print("Regenerating HTML files with explicit video dimensions...\n")
    
    success_count = 0
    for exp_dir in sorted(exploration_dirs):
        if create_html(exp_dir):
            success_count += 1
    
    print(f"\n[COMPLETE] Regenerated {success_count} HTML files")
    print("\nOpen any comparison.html in Chrome or Firefox to view results")
    print("If videos still don't show, the codec may need conversion")


if __name__ == "__main__":
    main()
