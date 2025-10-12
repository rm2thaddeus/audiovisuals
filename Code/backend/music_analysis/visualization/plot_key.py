"""
Key detection visualization - Chroma features and key profiles

Creates matplotlib visualizations for key detection results.
"""

from pathlib import Path
from typing import Dict, Union

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np


# Key names for labeling
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def plot_key(
    results: Dict,
    audio_path: str,
    output_path: Union[str, Path],
    time_varying: bool = False,
    figsize: tuple = (14, 10)
) -> None:
    """
    Create visualization for key detection.
    
    Shows chroma features, key profile, and detected key.
    
    Args:
        results: Key detection results dictionary
        audio_path: Path to original audio file
        output_path: Path to save plot PNG
        time_varying: Whether results are from time-varying analysis
        figsize: Figure size in inches
    """
    if time_varying:
        _plot_key_timevarying(results, audio_path, output_path, figsize)
    else:
        _plot_key_global(results, audio_path, output_path, figsize)


def _plot_key_global(
    results: Dict,
    audio_path: str,
    output_path: Union[str, Path],
    figsize: tuple
) -> None:
    """Plot global key detection results."""
    # Load audio
    y, sr = librosa.load(audio_path, sr=results['metadata']['sample_rate'])
    
    # Extract chroma features
    chroma = np.array(results['chroma_features'])
    
    # Create figure with 3 subplots
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Title
    fig.suptitle(
        f"Key Detection: {Path(audio_path).name}\n"
        f"Detected Key: {results['key']} {results['scale']} "
        f"(Confidence: {results['confidence']:.1%})",
        fontsize=14,
        fontweight='bold'
    )
    
    # === Plot 1: Chromagram (full span) ===
    ax1 = fig.add_subplot(gs[0, :])
    img = librosa.display.specshow(
        chroma,
        sr=sr,
        x_axis='time',
        y_axis='chroma',
        ax=ax1,
        cmap='coolwarm'
    )
    ax1.set_title('Chromagram (Pitch Class Energy Over Time)')
    fig.colorbar(img, ax=ax1, format='%+2.0f')
    
    # === Plot 2: Average chroma profile ===
    ax2 = fig.add_subplot(gs[1, 0])
    key_profile = np.array(results['key_profile'])
    
    bars = ax2.bar(range(12), key_profile, color='steelblue', alpha=0.7, edgecolor='black')
    
    # Highlight detected key
    key_idx = KEY_NAMES.index(results['key'])
    bars[key_idx].set_color('red')
    bars[key_idx].set_alpha(0.9)
    
    ax2.set_xticks(range(12))
    ax2.set_xticklabels(KEY_NAMES)
    ax2.set_ylabel('Normalized Energy')
    ax2.set_title('Average Chroma Profile')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # === Plot 3: Key candidates ===
    ax3 = fig.add_subplot(gs[1, 1])
    
    # Main key
    key_names_display = [f"{results['key']}\n{results['scale']}"]
    confidences = [results['confidence']]
    colors = ['red']
    
    # Alternatives
    for alt in results['alternatives'][:4]:
        key_names_display.append(alt['key'].replace(' ', '\n'))
        confidences.append(alt['confidence'])
        colors.append('steelblue')
    
    bars = ax3.barh(range(len(confidences)), confidences, color=colors, alpha=0.7)
    ax3.set_yticks(range(len(confidences)))
    ax3.set_yticklabels(key_names_display)
    ax3.set_xlabel('Confidence')
    ax3.set_title('Key Candidates')
    ax3.set_xlim([0, 1])
    ax3.grid(True, alpha=0.3, axis='x')
    
    # Add confidence values
    for i, (bar, conf) in enumerate(zip(bars, confidences)):
        ax3.text(
            conf + 0.02, i, f'{conf:.2%}',
            va='center',
            fontsize=9
        )
    
    # === Plot 4: Waveform with key info ===
    ax4 = fig.add_subplot(gs[2, :])
    times = librosa.times_like(y, sr=sr)
    ax4.plot(times, y, alpha=0.6, linewidth=0.5, color='steelblue')
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Amplitude')
    ax4.set_title('Audio Waveform')
    ax4.grid(True, alpha=0.3)
    
    # Add key information box
    info_text = (
        f"Key: {results['key']} {results['scale']}\n"
        f"Relative: {results['relative_key']}\n"
        f"Confidence: {results['confidence']:.1%}"
    )
    ax4.text(
        0.02, 0.98, info_text,
        transform=ax4.transAxes,
        fontsize=11,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    )
    
    # Add metadata
    metadata_text = (
        f"Duration: {results['duration']:.1f}s | "
        f"Processing: {results['processing_time']:.2f}s | "
        f"Model: {results['metadata']['model']}"
    )
    fig.text(0.5, 0.02, metadata_text, ha='center', fontsize=10, style='italic')
    
    # Save figure
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def _plot_key_timevarying(
    results: Dict,
    audio_path: str,
    output_path: Union[str, Path],
    figsize: tuple
) -> None:
    """Plot time-varying key detection results."""
    # Load audio
    y, sr = librosa.load(audio_path)
    
    # Create figure
    fig, axes = plt.subplots(2, 1, figsize=figsize)
    fig.suptitle(
        f"Time-Varying Key Detection: {Path(audio_path).name}\n"
        f"Overall Key: {results['overall_key']} {results['overall_scale']} | "
        f"Key Changes: {results['num_changes']}",
        fontsize=14,
        fontweight='bold'
    )
    
    # === Plot 1: Waveform with key changes ===
    ax1 = axes[0]
    times = librosa.times_like(y, sr=sr)
    ax1.plot(times, y, alpha=0.6, linewidth=0.5, color='steelblue')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Waveform with Key Regions')
    ax1.grid(True, alpha=0.3)
    
    # Color regions by key
    key_timeline = results['key_timeline']
    colors = plt.cm.tab20(np.linspace(0, 1, results['num_changes']))
    
    for i, entry in enumerate(key_timeline):
        start_time = entry['time']
        if i < len(key_timeline) - 1:
            end_time = key_timeline[i + 1]['time']
        else:
            end_time = results['duration']
        
        ax1.axvspan(
            start_time, end_time,
            alpha=0.2,
            color=colors[i % len(colors)]
        )
        
        # Add key label
        if end_time - start_time > 5:  # Only label if section is wide enough
            mid_time = (start_time + end_time) / 2
            ax1.text(
                mid_time, ax1.get_ylim()[1] * 0.9,
                f"{entry['key']}\n{entry['scale']}",
                ha='center',
                fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
            )
    
    ax1.set_xlim([0, results['duration']])
    
    # === Plot 2: Key timeline ===
    ax2 = axes[1]
    
    # Create key index mapping
    unique_keys = sorted(set(f"{e['key']} {e['scale']}" for e in key_timeline))
    key_to_idx = {k: i for i, k in enumerate(unique_keys)}
    
    # Plot key changes
    for entry in key_timeline:
        key_str = f"{entry['key']} {entry['scale']}"
        idx = key_to_idx[key_str]
        ax2.scatter(
            entry['time'], idx,
            s=100 * entry['confidence'],
            alpha=0.7,
            color=colors[key_timeline.index(entry) % len(colors)]
        )
    
    # Connect points
    times_plot = [e['time'] for e in key_timeline]
    indices = [key_to_idx[f"{e['key']} {e['scale']}"] for e in key_timeline]
    ax2.plot(times_plot, indices, 'k--', alpha=0.3, linewidth=1)
    
    ax2.set_yticks(range(len(unique_keys)))
    ax2.set_yticklabels(unique_keys)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Detected Key')
    ax2.set_title('Key Changes Timeline')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, results['duration']])
    
    # Add metadata
    metadata_text = (
        f"Window size: {results['window_size']}s | "
        f"Duration: {results['duration']:.1f}s | "
        f"Unique keys: {results['num_changes']}"
    )
    fig.text(0.5, 0.02, metadata_text, ha='center', fontsize=10, style='italic')
    
    # Save figure
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

