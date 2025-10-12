"""
Chord visualization - Chord progression timeline

Creates matplotlib visualizations for chord detection results.
"""

from pathlib import Path
from typing import Dict, Union

import librosa
import librosa.display
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def plot_chords(
    results: Dict,
    audio_path: str,
    output_path: Union[str, Path],
    figsize: tuple = (14, 10)
) -> None:
    """
    Create visualization for chord detection.
    
    Shows waveform and chromagram with chord labels overlaid.
    
    Args:
        results: Chord detection results dictionary
        audio_path: Path to original audio file
        output_path: Path to save plot PNG
        figsize: Figure size in inches
    """
    # Load audio for visualization
    y, sr = librosa.load(audio_path, sr=results['metadata']['sample_rate'])
    
    # Create figure with 3 subplots
    fig, axes = plt.subplots(3, 1, figsize=figsize)
    fig.suptitle(
        f"Chord Detection: {Path(audio_path).name}\n"
        f"Detected {results['chord_changes']} chord changes | "
        f"{results['unique_chords']} unique chords",
        fontsize=14,
        fontweight='bold'
    )
    
    # === Plot 1: Waveform with chord regions ===
    ax1 = axes[0]
    times = librosa.times_like(y, sr=sr)
    ax1.plot(times, y, alpha=0.6, linewidth=0.5, color='steelblue')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Waveform with Chord Regions')
    ax1.grid(True, alpha=0.3)
    
    # Color code chords
    chords = results['chords']
    unique_chords = results['chord_vocabulary']
    colors = plt.cm.tab20(np.linspace(0, 1, len(unique_chords)))
    chord_to_color = {chord: colors[i] for i, chord in enumerate(unique_chords)}
    
    for chord_info in chords:
        start = chord_info['time']
        duration = chord_info['duration']
        end = start + duration
        chord_name = chord_info['chord']
        
        # Color region
        color = chord_to_color.get(chord_name, 'gray')
        ax1.axvspan(start, end, alpha=0.3, color=color)
        
        # Add label if chord is wide enough
        if duration > 2:
            mid_time = start + duration / 2
            ax1.text(
                mid_time, ax1.get_ylim()[1] * 0.85,
                chord_name,
                ha='center',
                fontsize=9,
                fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor=color, linewidth=2)
            )
    
    ax1.set_xlim([0, results['duration']])
    
    # === Plot 2: Chromagram with chord boundaries ===
    ax2 = axes[1]
    
    # Compute chromagram
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    img = librosa.display.specshow(
        chroma,
        sr=sr,
        x_axis='time',
        y_axis='chroma',
        ax=ax2,
        cmap='coolwarm'
    )
    fig.colorbar(img, ax=ax2)
    ax2.set_title('Chromagram with Chord Boundaries')
    
    # Add chord boundaries
    for chord_info in chords:
        ax2.axvline(chord_info['time'], color='white', alpha=0.7, linewidth=2, linestyle='--')
    
    # === Plot 3: Chord timeline ===
    ax3 = axes[2]
    
    # Create timeline with chord names
    y_pos = 0
    for i, chord_info in enumerate(chords):
        start = chord_info['time']
        duration = chord_info['duration']
        chord_name = chord_info['chord']
        confidence = chord_info['confidence']
        
        # Draw bar
        color = chord_to_color.get(chord_name, 'gray')
        bar = ax3.barh(
            y_pos, duration, left=start,
            height=0.8, color=color, alpha=0.7,
            edgecolor='black', linewidth=1
        )
        
        # Add label
        if duration > 1:
            ax3.text(
                start + duration / 2, y_pos,
                f"{chord_name}\n{confidence:.0%}",
                ha='center', va='center',
                fontsize=8,
                fontweight='bold'
            )
    
    ax3.set_ylim([-0.5, 0.5])
    ax3.set_xlim([0, results['duration']])
    ax3.set_xlabel('Time (s)')
    ax3.set_yticks([])
    ax3.set_title('Chord Progression Timeline')
    ax3.grid(True, alpha=0.3, axis='x')
    
    # Add legend with unique chords
    if len(unique_chords) <= 15:  # Only show legend if not too many chords
        legend_patches = [
            mpatches.Patch(color=chord_to_color[chord], label=chord)
            for chord in unique_chords[:15]
        ]
        ax3.legend(
            handles=legend_patches,
            loc='upper right',
            ncol=min(5, len(unique_chords)),
            fontsize=8
        )
    
    # Add metadata
    metadata_text = (
        f"Duration: {results['duration']:.1f}s | "
        f"Processing: {results['processing_time']:.2f}s | "
        f"Chord changes: {results['chord_changes']}"
    )
    fig.text(0.5, 0.02, metadata_text, ha='center', fontsize=10, style='italic')
    
    # Save figure
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_chord_statistics(
    results: Dict,
    output_path: Union[str, Path],
    figsize: tuple = (10, 8)
) -> None:
    """
    Create statistical visualization of chord usage.
    
    Args:
        results: Chord detection results
        output_path: Path to save plot
        figsize: Figure size in inches
    """
    chords = results['chords']
    
    # Count chord occurrences and total duration
    chord_counts = {}
    chord_durations = {}
    
    for chord_info in chords:
        chord = chord_info['chord']
        duration = chord_info['duration']
        
        chord_counts[chord] = chord_counts.get(chord, 0) + 1
        chord_durations[chord] = chord_durations.get(chord, 0) + duration
    
    # Sort by duration
    sorted_chords = sorted(chord_durations.items(), key=lambda x: x[1], reverse=True)
    chord_names = [c[0] for c in sorted_chords[:15]]  # Top 15
    durations = [c[1] for c in sorted_chords[:15]]
    counts = [chord_counts[c] for c in chord_names]
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle('Chord Statistics', fontsize=14, fontweight='bold')
    
    # Plot 1: Duration
    ax1.barh(chord_names, durations, color='steelblue', alpha=0.7)
    ax1.set_xlabel('Total Duration (s)')
    ax1.set_title('Chord Duration')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Plot 2: Occurrences
    ax2.barh(chord_names, counts, color='coral', alpha=0.7)
    ax2.set_xlabel('Number of Occurrences')
    ax2.set_title('Chord Frequency')
    ax2.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


