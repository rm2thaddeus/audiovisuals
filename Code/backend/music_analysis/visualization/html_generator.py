"""
HTML Report Generator - Create interactive HTML reports

Generates self-contained HTML reports with JSON data, plots, and interactive charts.
"""

import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union


def generate_html_report(
    results: Dict,
    audio_path: str,
    output_path: Union[str, Path],
    plot_path: Optional[Union[str, Path]] = None,
    analysis_type: str = 'tempo'
) -> None:
    """
    Generate HTML report for music analysis.
    
    Args:
        results: Analysis results dictionary
        audio_path: Path to original audio file
        output_path: Path to save HTML report
        plot_path: Path to plot PNG (optional, will be embedded)
        analysis_type: Type of analysis ('tempo', 'key', 'chords', 'structure', 'genre')
    """
    audio_name = Path(audio_path).name
    
    # Embed plot as base64 if provided
    plot_html = ""
    if plot_path and Path(plot_path).exists():
        with open(plot_path, 'rb') as f:
            plot_base64 = base64.b64encode(f.read()).decode('utf-8')
            plot_html = f'<img src="data:image/png;base64,{plot_base64}" style="width: 100%; max-width: 1200px; height: auto;">'
    
    # Generate type-specific content
    if analysis_type == 'tempo':
        summary_html = _generate_tempo_summary(results)
        interactive_html = _generate_tempo_interactive(results)
    elif analysis_type == 'key':
        summary_html = _generate_key_summary(results)
        interactive_html = _generate_key_interactive(results)
    elif analysis_type == 'structure':
        summary_html = _generate_structure_summary(results)
        interactive_html = _generate_structure_interactive(results)
    elif analysis_type == 'chords':
        summary_html = _generate_chords_summary(results)
        interactive_html = _generate_chords_interactive(results)
    elif analysis_type == 'genre':
        summary_html = _generate_genre_summary(results)
        interactive_html = _generate_genre_interactive(results)
    else:
        summary_html = "<p>Analysis summary not available for this type.</p>"
        interactive_html = ""
    
    # Build complete HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Music Analysis: {audio_name}</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        header {{
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        h1 {{
            color: #007bff;
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        h2 {{
            color: #333;
            font-size: 1.5em;
            margin: 30px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        h3 {{
            color: #555;
            font-size: 1.2em;
            margin: 20px 0 10px 0;
        }}
        
        .metadata {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        
        .metadata p {{
            margin: 5px 0;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .summary-card.secondary {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .summary-card.tertiary {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        
        .summary-card h3 {{
            color: white;
            font-size: 0.9em;
            margin-bottom: 10px;
            opacity: 0.9;
        }}
        
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
        }}
        
        .plot-container {{
            margin: 30px 0;
            text-align: center;
        }}
        
        .json-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 0.9em;
        }}
        
        .collapsible {{
            background-color: #007bff;
            color: white;
            cursor: pointer;
            padding: 15px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 1.1em;
            border-radius: 5px;
            margin: 10px 0;
            transition: background-color 0.3s;
        }}
        
        .collapsible:hover {{
            background-color: #0056b3;
        }}
        
        .collapsible:after {{
            content: '\\002B';
            color: white;
            font-weight: bold;
            float: right;
            margin-left: 5px;
        }}
        
        .collapsible.active:after {{
            content: "\\2212";
        }}
        
        .content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
            background-color: #f8f9fa;
            border-radius: 0 0 5px 5px;
        }}
        
        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
            .collapsible {{
                display: none;
            }}
            .content {{
                max-height: none !important;
                display: block !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎵 Music Analysis Report</h1>
            <p style="font-size: 1.1em; color: #666;">
                <strong>File:</strong> {audio_name}<br>
                <strong>Analysis Type:</strong> {analysis_type.title()}<br>
                <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </header>
        
        <section>
            <h2>📊 Summary</h2>
            {summary_html}
        </section>
        
        <section>
            <h2>📈 Visualization</h2>
            <div class="plot-container">
                {plot_html if plot_html else '<p><em>No plot available</em></p>'}
            </div>
        </section>
        
        {interactive_html}
        
        <section>
            <h2>📄 Metadata</h2>
            <div class="metadata">
                {_format_metadata(results.get('metadata', dict()))}
            </div>
        </section>
        
        <section>
            <button type="button" class="collapsible">📋 View Raw JSON Data</button>
            <div class="content">
                <div class="json-container">
                    <pre>{json.dumps(results, indent=2)}</pre>
                </div>
            </div>
        </section>
        
        <footer>
            <p>Generated by Music Analysis System | Phase B Implementation</p>
            <p>Audio Feature Explorer - Aitor Patiño Diaz</p>
        </footer>
    </div>
    
    <script>
        // Collapsible sections
        var coll = document.getElementsByClassName("collapsible");
        for (var i = 0; i < coll.length; i++) {{
            coll[i].addEventListener("click", function() {{
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                if (content.style.maxHeight) {{
                    content.style.maxHeight = null;
                }} else {{
                    content.style.maxHeight = content.scrollHeight + "px";
                }}
            }});
        }}
    </script>
</body>
</html>"""
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def _generate_tempo_summary(results: Dict) -> str:
    """Generate HTML summary for tempo analysis."""
    return f"""
    <div class="summary-grid">
        <div class="summary-card">
            <h3>Tempo (BPM)</h3>
            <div class="value">{results['tempo']}</div>
        </div>
        <div class="summary-card secondary">
            <h3>Confidence</h3>
            <div class="value">{results['tempo_confidence']:.1%}</div>
        </div>
        <div class="summary-card tertiary">
            <h3>Time Signature</h3>
            <div class="value">{results['time_signature']}</div>
        </div>
        <div class="summary-card">
            <h3>Beats Detected</h3>
            <div class="value">{results['num_beats']}</div>
        </div>
    </div>
    
    <div class="metadata">
        <p><strong>Duration:</strong> {results['duration']:.1f} seconds</p>
        <p><strong>Processing Time:</strong> {results['processing_time']:.2f} seconds</p>
        <p><strong>Average Beat Interval:</strong> {60.0 / results['tempo']:.3f} seconds</p>
    </div>
    """


def _generate_tempo_interactive(results: Dict) -> str:
    """Generate interactive Plotly chart for tempo."""
    beat_times = results['beats']
    
    # Create beat positions for plotting
    beat_y = [1] * len(beat_times)
    
    return f"""
    <section>
        <h2>📍 Interactive Beat Timeline</h2>
        <div id="tempo-interactive"></div>
    </section>
    
    <script>
        var beatData = {{
            x: {json.dumps(beat_times)},
            y: {json.dumps(beat_y)},
            mode: 'markers',
            type: 'scatter',
            marker: {{
                size: 12,
                color: 'red',
                symbol: 'diamond'
            }},
            name: 'Beats',
            hovertemplate: 'Beat at %{{x:.2f}}s<extra></extra>'
        }};
        
        var layout = {{
            title: 'Beat Positions',
            xaxis: {{
                title: 'Time (seconds)',
                showgrid: true
            }},
            yaxis: {{
                showticklabels: false,
                showgrid: false
            }},
            hovermode: 'closest',
            height: 250
        }};
        
        Plotly.newPlot('tempo-interactive', [beatData], layout);
    </script>
    """


def _generate_key_summary(results: Dict) -> str:
    """Generate HTML summary for key detection."""
    if 'overall_key' in results:  # Time-varying analysis
        return f"""
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Overall Key</h3>
                <div class="value">{results['overall_key']} {results['overall_scale']}</div>
            </div>
            <div class="summary-card secondary">
                <h3>Key Changes</h3>
                <div class="value">{results['num_changes']}</div>
            </div>
            <div class="summary-card tertiary">
                <h3>Window Size</h3>
                <div class="value">{results['window_size']}s</div>
            </div>
        </div>
        """
    else:  # Global analysis
        alternatives_html = "".join([
            f"<li>{alt['key']}: {alt['confidence']:.1%}</li>"
            for alt in results['alternatives']
        ])
        
        return f"""
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Detected Key</h3>
                <div class="value">{results['key']} {results['scale']}</div>
            </div>
            <div class="summary-card secondary">
                <h3>Confidence</h3>
                <div class="value">{results['confidence']:.1%}</div>
            </div>
            <div class="summary-card tertiary">
                <h3>Relative Key</h3>
                <div class="value">{results['relative_key']}</div>
            </div>
        </div>
        
        <div class="metadata">
            <p><strong>Duration:</strong> {results['duration']:.1f} seconds</p>
            <p><strong>Processing Time:</strong> {results['processing_time']:.2f} seconds</p>
            <p><strong>Alternative Keys:</strong></p>
            <ul>
                {alternatives_html}
            </ul>
        </div>
        """


def _generate_key_interactive(results: Dict) -> str:
    """Generate interactive Plotly chart for key detection."""
    if 'overall_key' in results:  # Time-varying
        return ""  # Time-varying visualization is in the plot
    
    # Chroma profile bar chart
    key_profile = results['key_profile']
    key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    return f"""
    <section>
        <h2>🎹 Interactive Chroma Profile</h2>
        <div id="key-interactive"></div>
    </section>
    
    <script>
        var chromaData = {{
            x: {json.dumps(key_names)},
            y: {json.dumps(key_profile)},
            type: 'bar',
            marker: {{
                color: 'steelblue'
            }},
            hovertemplate: '%{{x}}: %{{y:.3f}}<extra></extra>'
        }};
        
        var layout = {{
            title: 'Average Chroma Profile',
            xaxis: {{
                title: 'Pitch Class'
            }},
            yaxis: {{
                title: 'Normalized Energy'
            }},
            height: 400
        }};
        
        Plotly.newPlot('key-interactive', [chromaData], layout);
    </script>
    """


def _generate_structure_summary(results: Dict) -> str:
    """Generate HTML summary for structure analysis."""
    segments = results['segments'][:5]  # Show first 5 segments
    
    segments_html = "".join([
        f"""<li><strong>{seg['label']}</strong>: {seg['start']:.1f}s - {seg['end']:.1f}s ({seg['duration']:.1f}s)</li>"""
        for seg in segments
    ])
    
    if len(results['segments']) > 5:
        segments_html += f"<li><em>... and {len(results['segments']) - 5} more segments</em></li>"
    
    return f"""
    <div class="summary-grid">
        <div class="summary-card">
            <h3>Total Segments</h3>
            <div class="value">{results['num_segments']}</div>
        </div>
        <div class="summary-card secondary">
            <h3>Algorithm</h3>
            <div class="value" style="font-size: 1.5em;">{results['algorithm'].upper()}</div>
        </div>
        <div class="summary-card tertiary">
            <h3>Duration</h3>
            <div class="value">{results['duration']:.1f}s</div>
        </div>
        <div class="summary-card">
            <h3>Avg Segment</h3>
            <div class="value">{results['duration'] / results['num_segments']:.1f}s</div>
        </div>
    </div>
    
    <div class="metadata">
        <p><strong>Processing Time:</strong> {results['processing_time']:.2f} seconds</p>
        <p><strong>First 5 Segments:</strong></p>
        <ul>
            {segments_html}
        </ul>
    </div>
    """


def _generate_structure_interactive(results: Dict) -> str:
    """Generate interactive Plotly chart for structure."""
    segments = results['segments']
    
    # Prepare data for timeline chart
    labels = [seg['label'] for seg in segments]
    starts = [seg['start'] for seg in segments]
    durations = [seg['duration'] for seg in segments]
    
    return f"""
    <section>
        <h2>📊 Interactive Segment Timeline</h2>
        <div id="structure-interactive"></div>
    </section>
    
    <script>
        var structureData = {{
            x: {json.dumps(durations)},
            y: {json.dumps(labels)},
            type: 'bar',
            orientation: 'h',
            marker: {{
                color: 'steelblue'
            }},
            hovertemplate: '%{{y}}: %{{x:.1f}}s<extra></extra>'
        }};
        
        var layout = {{
            title: 'Segment Durations',
            xaxis: {{
                title: 'Duration (seconds)',
                showgrid: true
            }},
            yaxis: {{
                title: 'Segment',
                automargin: true
            }},
            hovermode: 'closest',
            height: Math.max(400, {len(segments)} * 30)
        }};
        
        Plotly.newPlot('structure-interactive', [structureData], layout);
    </script>
    """


def _generate_chords_summary(results: Dict) -> str:
    """Generate HTML summary for chord detection."""
    chords = results['chords'][:10]  # Show first 10 chords
    
    chords_html = "".join([
        f"""<li><strong>{c['chord']}</strong> at {c['time']:.1f}s ({c['confidence']:.0%}, {c['duration']:.1f}s)</li>"""
        for c in chords
    ])
    
    if len(results['chords']) > 10:
        chords_html += f"<li><em>... and {len(results['chords']) - 10} more chord changes</em></li>"
    
    vocab_html = ', '.join(results['chord_vocabulary'][:20])
    if len(results['chord_vocabulary']) > 20:
        vocab_html += f" ... (+{len(results['chord_vocabulary']) - 20} more)"
    
    return f"""
    <div class="summary-grid">
        <div class="summary-card">
            <h3>Chord Changes</h3>
            <div class="value">{results['chord_changes']}</div>
        </div>
        <div class="summary-card secondary">
            <h3>Unique Chords</h3>
            <div class="value">{results['unique_chords']}</div>
        </div>
        <div class="summary-card tertiary">
            <h3>Duration</h3>
            <div class="value">{results['duration']:.1f}s</div>
        </div>
        <div class="summary-card">
            <h3>Avg Chord Duration</h3>
            <div class="value">{results['duration'] / max(results['chord_changes'], 1):.1f}s</div>
        </div>
    </div>
    
    <div class="metadata">
        <p><strong>Processing Time:</strong> {results['processing_time']:.2f} seconds</p>
        <p><strong>Chord Vocabulary:</strong> {vocab_html}</p>
        <p><strong>First 10 Chord Changes:</strong></p>
        <ul>
            {chords_html}
        </ul>
    </div>
    """


def _generate_chords_interactive(results: Dict) -> str:
    """Generate interactive Plotly chart for chords."""
    chords = results['chords']
    
    # Prepare data
    times = [c['time'] for c in chords]
    chord_names = [c['chord'] for c in chords]
    durations = [c['duration'] for c in chords]
    confidences = [c['confidence'] for c in chords]
    
    return f"""
    <section>
        <h2>🎸 Interactive Chord Timeline</h2>
        <div id="chords-interactive"></div>
    </section>
    
    <script>
        var chordsData = {{
            x: {json.dumps(times)},
            y: {json.dumps(chord_names)},
            mode: 'markers',
            type: 'scatter',
            marker: {{
                size: {json.dumps([d * 2 for d in durations])},  // Size based on duration
                color: {json.dumps([c * 100 for c in confidences])},  // Color based on confidence
                colorscale: 'Viridis',
                showscale: true,
                colorbar: {{
                    title: 'Confidence (%)'
                }},
                line: {{
                    color: 'black',
                    width: 1
                }}
            }},
            text: {json.dumps([f"{c['chord']} ({c['confidence']:.0%})" for c in chords])},
            hovertemplate: '%{{text}}<br>Time: %{{x:.1f}}s<extra></extra>'
        }};
        
        var layout = {{
            title: 'Chord Progression',
            xaxis: {{
                title: 'Time (seconds)',
                showgrid: true
            }},
            yaxis: {{
                title: 'Chord',
                automargin: true
            }},
            hovermode: 'closest',
            height: Math.max(400, {len(set(chord_names))} * 40)
        }};
        
        Plotly.newPlot('chords-interactive', [chordsData], layout);
    </script>
    """


def _generate_genre_summary(results: Dict) -> str:
    """Generate HTML summary for genre classification."""
    predictions = results.get('predictions', [])
    chunk_predictions = results.get('chunk_predictions', [])
    primary = predictions[0] if predictions else None
    avg_confidence = (
        sum(chunk['confidence'] for chunk in chunk_predictions) / len(chunk_predictions)
        if chunk_predictions else 0.0
    )
    total_chunks = len(chunk_predictions)
    total_duration = (
        max(chunk['end'] for chunk in chunk_predictions)
        if chunk_predictions else 0.0
    )

    prediction_items = "".join(
        f"<li><strong>{entry['genre']}</strong> &mdash; {entry['score'] * 100:.1f}%</li>"
        for entry in predictions
    )

    return f"""
    <div class="summary-grid">
        <div class="summary-card">
            <h3>Predicted Genre</h3>
            <div class="value">{primary['genre'] if primary else 'N/A'}</div>
            <p>{primary['score'] * 100:.1f}% confidence</p>
        </div>
        <div class="summary-card secondary">
            <h3>Average Chunk Confidence</h3>
            <div class="value">{avg_confidence * 100:.1f}%</div>
        </div>
        <div class="summary-card tertiary">
            <h3>Chunks Analyzed</h3>
            <div class="value">{total_chunks}</div>
        </div>
        <div class="summary-card">
            <h3>Coverage</h3>
            <div class="value">{total_duration:.1f}s</div>
        </div>
    </div>
    
    <div class="metadata">
        <p><strong>Top Predictions:</strong></p>
        <ul>
            {prediction_items or '<li>No predictions available</li>'}
        </ul>
    </div>
    """


def _generate_genre_interactive(results: Dict) -> str:
    """Generate interactive Plotly charts for genre classification."""
    predictions = results.get('predictions', [])
    chunk_predictions = results.get('chunk_predictions', [])

    palette = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    ]

    ordered_genres = [entry['genre'] for entry in predictions]
    for chunk in chunk_predictions:
        if chunk['top_genre'] not in ordered_genres:
            ordered_genres.append(chunk['top_genre'])

    color_map = {
        genre: palette[idx % len(palette)]
        for idx, genre in enumerate(ordered_genres)
    }

    bar_data = {
        "type": "bar",
        "orientation": "h",
        "x": [entry['score'] * 100 for entry in reversed(predictions)],
        "y": [entry['genre'] for entry in reversed(predictions)],
        "marker": {
            "color": [color_map[entry['genre']] for entry in reversed(predictions)],
            "line": {"color": "#222222", "width": 1},
        },
        "hovertemplate": "%{y}: %{x:.1f}%<extra></extra>",
    }

    timeline_data = {
        "type": "bar",
        "orientation": "h",
        "base": [chunk['start'] for chunk in chunk_predictions],
        "x": [
            max(chunk['end'] - chunk['start'], 1e-6)
            for chunk in chunk_predictions
        ],
        "y": ["Segments"] * len(chunk_predictions),
        "marker": {
            "color": [
                color_map.get(chunk['top_genre'], "#888888")
                for chunk in chunk_predictions
            ],
            "line": {"color": "#222222", "width": 1},
        },
        "hovertext": [
            f"{chunk['top_genre']} ({chunk['confidence'] * 100:.1f}%)<br>"
            f"{chunk['start']:.1f}s - {chunk['end']:.1f}s"
            for chunk in chunk_predictions
        ],
        "hoverinfo": "text",
    }

    legend_items = "".join(
        f"<li><span style='display:inline-block;width:12px;height:12px;"
        f"background:{color_map[genre]};margin-right:8px;border-radius:2px;'></span>"
        f"{genre}</li>"
        for genre in ordered_genres
    )

    return f"""
    <section>
        <h2>Interactive Genre Breakdown</h2>
        <div id="genre-probabilities"></div>
    </section>
    <section>
        <h2>Segment Timeline</h2>
        <div id="genre-timeline"></div>
        <div class="metadata" style="margin-top: 10px;">
            <p><strong>Genre Legend:</strong></p>
            <ul style="columns: 2; list-style: none; padding-left: 0;">
                {legend_items}
            </ul>
        </div>
    </section>
    <script>
        const genreBarData = {json.dumps([bar_data])};
        const barLayout = {{
            height: Math.max(320, {len(predictions)} * 40),
            margin: {{l: 120, r: 40, t: 30, b: 60}},
            xaxis: {{title: 'Confidence (%)', range: [0, 100]}},
            yaxis: {{automargin: true}},
        }};
        Plotly.newPlot('genre-probabilities', genreBarData, barLayout);

        const timelineData = {json.dumps([timeline_data])};
        const timelineLayout = {{
            height: 200,
            barmode: 'stack',
            margin: {{l: 80, r: 40, t: 30, b: 60}},
            xaxis: {{title: 'Time (seconds)', showgrid: true}},
            yaxis: {{showticklabels: false}},
        }};
        Plotly.newPlot('genre-timeline', timelineData, timelineLayout);
    </script>
    """


def _format_metadata(metadata: Dict) -> str:
    """Format metadata dictionary as HTML."""
    lines = []
    for key, value in metadata.items():
        # Format key name
        key_display = key.replace('_', ' ').title()
        
        # Format value - handle nested dictionaries
        if isinstance(value, dict):
            # Skip nested dictionaries for now
            continue
        elif isinstance(value, (int, float)):
            value_display = f"{value:.2f}" if isinstance(value, float) else str(value)
        else:
            value_display = str(value)
        
        lines.append(f"<p><strong>{key_display}:</strong> {value_display}</p>")
    
    return "\n".join(lines)
