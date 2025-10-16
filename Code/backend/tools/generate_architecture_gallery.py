#!/usr/bin/env python3
"""
Generate beautiful HTML gallery for architecture exploration results.

Creates an interactive gallery with video previews, stats, and filtering.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import base64


def get_all_exploration_runs() -> List[Path]:
    """Find all architecture exploration directories."""
    base_dir = Path(__file__).parent.parent / 'explorations' / 'architecture_matrix'
    if not base_dir.exists():
        return []
    
    # Get all timestamped directories
    runs = sorted([d for d in base_dir.iterdir() if d.is_dir()], reverse=True)
    return runs


def load_exploration_metadata(run_dir: Path) -> Dict:
    """Load metadata from an exploration run."""
    metadata_file = run_dir / 'metadata.json'
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return None


def generate_gallery_html(output_path: Path):
    """Generate comprehensive HTML gallery."""
    
    runs = get_all_exploration_runs()
    
    if not runs:
        print("No exploration runs found!")
        return
    
    print(f"Found {len(runs)} exploration runs")
    
    # Collect all configurations across all runs
    all_configs = []
    
    for run_dir in runs:
        metadata = load_exploration_metadata(run_dir)
        if not metadata:
            continue
        
        run_name = run_dir.name
        matrix = metadata.get('matrix', {})
        
        # Process each result
        for result in metadata.get('results', []):
            if not result['success']:
                continue
            
            config = result['config']
            # Resolve path - it might be relative in the metadata
            video_path = Path(result['output_path'])
            if not video_path.is_absolute():
                video_path = (run_dir / video_path).resolve()
            
            # Find frame if it exists
            frame_path = video_path.parent / video_path.name.replace('.mp4', '_frame.png')
            
            # Calculate relative path from the output HTML location
            gallery_dir = Path(__file__).parent.parent / 'explorations' / 'architecture_matrix'
            
            all_configs.append({
                'run': run_name,
                'layers': config['layers'],
                'hidden_dim': config['hidden_dim'],
                'seed': config['seed'],
                'params': config['params'],
                'file_size_mb': result['file_size'] / (1024 * 1024),
                'video_path': video_path.relative_to(gallery_dir.resolve()),
                'frame_path': frame_path.relative_to(gallery_dir.resolve()) if frame_path.exists() else None,
                'config_id': f"{config['layers']}L_{config['hidden_dim']}D_seed{config['seed']}"
            })
    
    print(f"Found {len(all_configs)} successful configurations")
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CPPN Architecture Exploration Gallery</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e4e4e4;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            margin-bottom: 40px;
            backdrop-filter: blur(10px);
        }}
        
        h1 {{
            font-size: 3em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #a0a0a0;
            font-size: 1.2em;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 30px;
            flex-wrap: wrap;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .stat-label {{
            color: #a0a0a0;
            margin-top: 5px;
        }}
        
        .controls {{
            background: rgba(255, 255, 255, 0.05);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        
        .control-group {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .control-group label {{
            color: #c0c0c0;
            font-weight: 500;
        }}
        
        select, input {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #e4e4e4;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        select:hover, input:hover {{
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.3);
        }}
        
        select:focus, input:focus {{
            outline: none;
            border-color: #667eea;
            background: rgba(255, 255, 255, 0.15);
        }}
        
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        
        .video-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            overflow: hidden;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
            cursor: pointer;
        }}
        
        .video-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
            border-color: rgba(102, 126, 234, 0.5);
        }}
        
        .video-preview {{
            position: relative;
            width: 100%;
            aspect-ratio: 16/9;
            background: #000;
            overflow: hidden;
        }}
        
        .video-preview video {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .video-preview img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .play-overlay {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 60px;
            height: 60px;
            background: rgba(102, 126, 234, 0.9);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .video-card:hover .play-overlay {{
            opacity: 1;
        }}
        
        .play-overlay::after {{
            content: '▶';
            color: white;
            font-size: 24px;
            margin-left: 4px;
        }}
        
        .video-info {{
            padding: 20px;
        }}
        
        .config-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #fff;
        }}
        
        .config-details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }}
        
        .detail {{
            background: rgba(255, 255, 255, 0.05);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.9em;
        }}
        
        .detail-label {{
            color: #a0a0a0;
            font-size: 0.85em;
            margin-bottom: 3px;
        }}
        
        .detail-value {{
            color: #fff;
            font-weight: 600;
        }}
        
        .run-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-top: 10px;
        }}
        
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }}
        
        .modal.active {{
            display: flex;
        }}
        
        .modal-content {{
            max-width: 90vw;
            max-height: 90vh;
            background: #1a1a2e;
            border-radius: 15px;
            padding: 30px;
            position: relative;
        }}
        
        .modal video {{
            width: 100%;
            max-height: 70vh;
            border-radius: 10px;
        }}
        
        .close-modal {{
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 30px;
            color: #fff;
            cursor: pointer;
            background: rgba(255, 255, 255, 0.1);
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }}
        
        .close-modal:hover {{
            background: rgba(255, 255, 255, 0.2);
            transform: rotate(90deg);
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px;
            color: #a0a0a0;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CPPN Architecture Exploration</h1>
        <p class="subtitle">Audio-Reactive Neural Field Visualizations</p>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{len(all_configs)}</div>
                <div class="stat-label">Configurations</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(runs)}</div>
                <div class="stat-label">Exploration Runs</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(set(c['layers'] for c in all_configs))}</div>
                <div class="stat-label">Layer Counts</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(set(c['hidden_dim'] for c in all_configs))}</div>
                <div class="stat-label">Hidden Dimensions</div>
            </div>
        </div>
    </div>
    
    <div class="controls">
        <div class="control-group">
            <label>
                Layers:
                <select id="layerFilter">
                    <option value="all">All</option>
"""
    
    # Add layer filter options
    for layers in sorted(set(c['layers'] for c in all_configs)):
        html += f'                    <option value="{layers}">{layers}L</option>\n'
    
    html += """                </select>
            </label>
            
            <label>
                Hidden Dim:
                <select id="dimFilter">
                    <option value="all">All</option>
"""
    
    # Add dimension filter options
    for dim in sorted(set(c['hidden_dim'] for c in all_configs)):
        html += f'                    <option value="{dim}">{dim}D</option>\n'
    
    html += """                </select>
            </label>
            
            <label>
                Seed:
                <select id="seedFilter">
                    <option value="all">All</option>
"""
    
    # Add seed filter options
    for seed in sorted(set(c['seed'] for c in all_configs)):
        html += f'                    <option value="{seed}">Seed {seed}</option>\n'
    
    html += """                </select>
            </label>
            
            <label>
                Sort by:
                <select id="sortBy">
                    <option value="params">Parameters</option>
                    <option value="layers">Layers</option>
                    <option value="hidden_dim">Hidden Dim</option>
                    <option value="file_size">File Size</option>
                    <option value="run">Run (Newest First)</option>
                </select>
            </label>
        </div>
    </div>
    
    <div class="gallery" id="gallery">
"""
    
    # Add video cards
    for config in all_configs:
        frame_src = str(config['frame_path']) if config['frame_path'] else ""
        video_src = str(config['video_path'])
        
        html += f"""        <div class="video-card" 
             data-layers="{config['layers']}" 
             data-dim="{config['hidden_dim']}" 
             data-seed="{config['seed']}"
             data-params="{config['params']}"
             data-size="{config['file_size_mb']:.2f}"
             data-run="{config['run']}"
             onclick="openModal('{video_src}')">
            <div class="video-preview">
"""
        
        if frame_src:
            html += f'                <img src="{frame_src}" alt="Preview">\n'
        else:
            html += '                <div style="background: #000; width: 100%; height: 100%;"></div>\n'
        
        html += """                <div class="play-overlay"></div>
            </div>
            <div class="video-info">
                <div class="config-title">{config_id}</div>
                <div class="config-details">
                    <div class="detail">
                        <div class="detail-label">Layers</div>
                        <div class="detail-value">{layers}</div>
                    </div>
                    <div class="detail">
                        <div class="detail-label">Hidden Dim</div>
                        <div class="detail-value">{hidden_dim}</div>
                    </div>
                    <div class="detail">
                        <div class="detail-label">Parameters</div>
                        <div class="detail-value">{params:,}</div>
                    </div>
                    <div class="detail">
                        <div class="detail-label">File Size</div>
                        <div class="detail-value">{file_size_mb:.1f} MB</div>
                    </div>
                </div>
                <span class="run-badge">{run}</span>
            </div>
        </div>
""".format(**config)
    
    html += """    </div>
    
    <div class="modal" id="videoModal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal()">&times;</span>
            <video id="modalVideo" controls autoplay loop>
                <source src="" type="video/mp4">
            </video>
        </div>
    </div>
    
    <script>
        const gallery = document.getElementById('gallery');
        const layerFilter = document.getElementById('layerFilter');
        const dimFilter = document.getElementById('dimFilter');
        const seedFilter = document.getElementById('seedFilter');
        const sortBy = document.getElementById('sortBy');
        
        function filterAndSort() {
            const cards = Array.from(gallery.querySelectorAll('.video-card'));
            
            // Filter
            cards.forEach(card => {
                const layerMatch = layerFilter.value === 'all' || card.dataset.layers === layerFilter.value;
                const dimMatch = dimFilter.value === 'all' || card.dataset.dim === dimFilter.value;
                const seedMatch = seedFilter.value === 'all' || card.dataset.seed === seedFilter.value;
                
                if (layerMatch && dimMatch && seedMatch) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Sort visible cards
            const visibleCards = cards.filter(card => card.style.display !== 'none');
            const sortKey = sortBy.value;
            
            visibleCards.sort((a, b) => {
                let aVal, bVal;
                
                if (sortKey === 'run') {
                    return b.dataset.run.localeCompare(a.dataset.run);
                } else {
                    aVal = parseFloat(a.dataset[sortKey]);
                    bVal = parseFloat(b.dataset[sortKey]);
                    return aVal - bVal;
                }
            });
            
            // Reorder in DOM
            visibleCards.forEach(card => gallery.appendChild(card));
        }
        
        layerFilter.addEventListener('change', filterAndSort);
        dimFilter.addEventListener('change', filterAndSort);
        seedFilter.addEventListener('change', filterAndSort);
        sortBy.addEventListener('change', filterAndSort);
        
        function openModal(videoSrc) {
            const modal = document.getElementById('videoModal');
            const video = document.getElementById('modalVideo');
            video.src = videoSrc;
            modal.classList.add('active');
        }
        
        function closeModal() {
            const modal = document.getElementById('videoModal');
            const video = document.getElementById('modalVideo');
            video.pause();
            modal.classList.remove('active');
        }
        
        // Close modal on background click
        document.getElementById('videoModal').addEventListener('click', (e) => {
            if (e.target.id === 'videoModal') {
                closeModal();
            }
        });
        
        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
        
        // Initial sort
        filterAndSort();
    </script>
</body>
</html>
"""
    
    # Write HTML file
    output_path.write_text(html, encoding='utf-8')
    print(f"\nGallery generated: {output_path}")
    print(f"\nOpen in browser: file:///{output_path.absolute()}")


def main():
    output_dir = Path(__file__).parent.parent / 'explorations' / 'architecture_matrix'
    output_file = output_dir / 'index.html'
    
    generate_gallery_html(output_file)
    
    print("\n" + "="*60)
    print("Gallery generation complete!")
    print("="*60)
    print(f"\nOpen the gallery:")
    print(f"  {output_file.absolute()}")


if __name__ == '__main__':
    main()

