#!/usr/bin/env python3
"""
Show video thumbnails instead of embedded videos
Much more reliable than HTML video embedding
"""

import os
from pathlib import Path
import subprocess

def create_thumbnail_html(exploration_dir):
    """Create HTML with video thumbnails instead of embedded videos"""
    exploration_path = Path(exploration_dir)
    
    if not exploration_path.exists():
        print(f"Folder not found: {exploration_dir}")
        return False
    
    # Find all MP4 videos
    videos = list(exploration_path.glob('*.mp4'))
    if not videos:
        print(f"No videos found in {exploration_dir}")
        return False
    
    videos.sort()
    
    # Group videos by segment
    segments = {}
    for video in videos:
        name = video.stem
        if '_' in name:
            segment, preset = name.split('_', 1)
            if segment not in segments:
                segments[segment] = []
            segments[segment].append((preset, video.name))
    
    # Preset descriptions
    preset_descriptions = {
        'simple': 'Simple patterns',
        'reactive': 'Strong audio response', 
        'complex': 'Complex structures',
        'evolving': 'Living patterns'
    }
    
    preset_params = {
        'simple': 'Layers: 3, Dim: 128, Audio: 0.05, Evolve: 0.0',
        'reactive': 'Layers: 4, Dim: 128, Audio: 0.15, Evolve: 0.0',
        'complex': 'Layers: 5, Dim: 256, Audio: 0.08, Evolve: 0.0',
        'evolving': 'Layers: 4, Dim: 128, Audio: 0.10, Evolve: 0.02'
    }
    
    # Generate HTML with thumbnails
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CPPN Parameter Exploration Results</title>
    <style>
        body {{
            background: #111;
            color: #eee;
            font-family: sans-serif;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .segment {{
            margin-bottom: 40px;
        }}
        .segment h2 {{
            color: #007acc;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }}
        .video-grid {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
        }}
        .video-card {{
            background: #222;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(255,255,255,0.1);
            text-align: center;
            max-width: 300px;
        }}
        .video-card h3 {{
            margin-top: 0;
            color: #007acc;
        }}
        .description {{
            color: #ccc;
            margin-bottom: 15px;
        }}
        .thumbnail {{
            width: 280px;
            height: 210px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(255,255,255,0.2);
            margin-bottom: 15px;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .thumbnail:hover {{
            transform: scale(1.05);
        }}
        .download-link {{
            display: block;
            color: #007acc;
            text-decoration: none;
            margin-top: 10px;
            padding: 8px 16px;
            border: 1px solid #007acc;
            border-radius: 5px;
            transition: background 0.2s;
        }}
        .download-link:hover {{
            background: #007acc;
            color: white;
        }}
        .params {{
            font-size: 12px;
            color: #888;
            margin-top: 10px;
        }}
        .instructions {{
            background: #333;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CPPN Parameter Exploration Results</h1>
        <p>Generated: {exploration_path.name}</p>
        <p>Total Videos: {len(videos)}</p>
    </div>
    
    <div class="instructions">
        <h3>How to View Videos:</h3>
        <p>Click on any thumbnail to open the video in your default player, or use the download link to save it.</p>
        <p>Each video is 10 seconds long and shows different CPPN parameter combinations.</p>
    </div>
'''
    
    # Add each segment
    for segment, videos_list in segments.items():
        html += f'''
    <div class="segment">
        <h2>{segment.title()} Segment</h2>
        <div class="video-grid">
'''
        
        for preset, video_file in videos_list:
            desc = preset_descriptions.get(preset, preset)
            params = preset_params.get(preset, 'Unknown parameters')
            
            html += f'''
            <div class="video-card">
                <h3>{preset.title()}</h3>
                <p class="description">{desc}</p>
                <img class="thumbnail" src="{video_file}" alt="{preset} video thumbnail" 
                     onclick="window.open('{video_file}', '_blank')">
                <a href="{video_file}" class="download-link" download>
                    Download Video
                </a>
                <div class="params">
                    {params}
                </div>
            </div>
'''
        
        html += '''
        </div>
    </div>
'''
    
    html += '''
</body>
</html>
'''
    
    # Write the HTML file
    html_file = exploration_path / 'thumbnails.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'[OK] Created {html_file}')
    return True

def main():
    """Create thumbnail HTML for all exploration folders"""
    exploration_base = Path('explorations')
    
    if not exploration_base.exists():
        print("No explorations folder found")
        return
    
    folders = [d for d in exploration_base.iterdir() if d.is_dir()]
    folders.sort()
    
    created_count = 0
    for folder in folders:
        # Check if folder has videos
        videos = list(folder.glob('*.mp4'))
        if videos:
            if create_thumbnail_html(folder):
                created_count += 1
        else:
            print(f"[SKIP] No videos in {folder.name}")
    
    print(f"\n[COMPLETE] Created {created_count} thumbnail HTML files")
    print("Open any thumbnails.html file to view video previews!")
    print("Click thumbnails to open videos in your default player.")

if __name__ == '__main__':
    main()
