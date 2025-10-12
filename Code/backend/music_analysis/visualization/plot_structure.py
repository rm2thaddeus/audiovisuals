"""
Structure visualization - Segment boundaries and structure plots

Creates matplotlib visualizations for music structure analysis results.
"""

from pathlib import Path
from typing import Dict, Union

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np


def plot_structure(
    results: Dict,
    audio_path: str,
    output_path: Union[str, Path],
    figsize: tuple = (14, 10)
) -> None:
    """
    Create visualization for structure analysis.
    
    Shows waveform and spectrogram with segment boundaries overlaid.
    
    Args:
        results: Structure analysis results dictionary
        audio_path: Path to original audio file
        output_path: Path to save plot PNG
        figsize: Figure size in inches
    """
    # Load audio for visualization
    y, sr = librosa.load(audio_path, sr=results['metadata']['sample_rate'])
    
    # Create figure with 3 subplots
    fig, axes = plt.subplots(3, 1, figsize=figsize)
    fig.suptitle(
        f"Structure Analysis: {Path(audio_path).name}\n"
        f"Algorithm: {results['algorithm']} | "
        f"Segments: {results['num_segments']}",
        fontsize=14,
        fontweight='bold'
    )
    
    # === Plot 1: Waveform with boundaries ===
    ax1 = axes[0]
    times = librosa.times_like(y, sr=sr)
    ax1.plot(times, y, alpha=0.6, linewidth=0.5, color='steelblue')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Waveform with Segment Boundaries')
    ax1.grid(True, alpha=0.3)
    
    # Add segment boundaries
    boundary_times = results['boundary_times']
    for boundary_time in boundary_times:
        ax1.axvline(boundary_time, color='red', alpha=0.7, linewidth=2, linestyle='--')
    
    # Color segments
    segments = results['segments']
    colors = plt.cm.tab20(np.linspace(0, 1, len(segments)))
    
    for i, seg in enumerate(segments):
        ax1.axvspan(
            seg['start'], seg['end'],
            alpha=0.2,
            color=colors[i]
        )
        
        # Add label if segment is wide enough
        if seg['duration'] > 5:
            mid_time = (seg['start'] + seg['end']) / 2
            ax1.text(
                mid_time, ax1.get_ylim()[1] * 0.85,
                seg['label'],
                ha='center',
                fontsize=8,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
            )
    
    ax1.set_xlim([0, results['duration']])
    
    # === Plot 2: Mel spectrogram with boundaries ===
    ax2 = axes[1]
    
    # Compute mel spectrogram
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    S_dB = librosa.power_to_db(S, ref=np.max)
    
    img = librosa.display.specshow(
        S_dB,
        sr=sr,
        x_axis='time',
        y_axis='mel',
        ax=ax2,
        cmap='viridis'
    )
    fig.colorbar(img, ax=ax2, format='%+2.0f dB')
    ax2.set_title('Mel Spectrogram with Segment Boundaries')
    
    # Add segment boundaries
    for boundary_time in boundary_times:
        ax2.axvline(boundary_time, color='red', alpha=0.7, linewidth=2, linestyle='--')
    
    # Color segments
    for i, seg in enumerate(segments):
        ax2.axvspan(
            seg['start'], seg['end'],
            alpha=0.15,
            color=colors[i]
        )
    
    # === Plot 3: Segment duration chart ===
    ax3 = axes[2]
    
    segment_labels = [f"{seg['label']}\n({seg['start']:.1f}s)" for seg in segments]
    segment_durations = [seg['duration'] for seg in segments]
    x_pos = np.arange(len(segments))
    
    bars = ax3.bar(x_pos, segment_durations, color=colors, alpha=0.7, edgecolor='black')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(segment_labels, rotation=45, ha='right', fontsize=8)
    ax3.set_ylabel('Duration (s)')
    ax3.set_xlabel('Segments')
    ax3.set_title('Segment Durations')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add duration labels on bars
    for bar, duration in zip(bars, segment_durations):
        height = bar.get_height()
        ax3.text(
            bar.get_x() + bar.get_width() / 2, height,
            f'{duration:.1f}s',
            ha='center', va='bottom',
            fontsize=8
        )
    
    # Add metadata
    metadata_text = (
        f"Duration: {results['duration']:.1f}s | "
        f"Processing: {results['processing_time']:.2f}s | "
        f"Segments: {results['num_segments']}"
    )
    fig.text(0.5, 0.02, metadata_text, ha='center', fontsize=10, style='italic')
    
    # Save figure
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_structure_similarity(
    results: Dict,
    output_path: Union[str, Path],
    figsize: tuple = (10, 8)
) -> None:
    """
    Create visualization of segment similarity matrix.
    
    Args:
        results: Structure analysis results with similarity_matrix
        output_path: Path to save plot
        figsize: Figure size in inches
    """
    if 'similarity_matrix' not in results or results['similarity_matrix'] is None:
        print("No similarity matrix available for visualization")
        return
    
    similarity_matrix = np.array(results['similarity_matrix'])
    segments = results['segments']
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot similarity matrix
    im = ax.imshow(similarity_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Similarity', rotation=270, labelpad=20)
    
    # Set labels
    segment_labels = [seg['label'] for seg in segments]
    ax.set_xticks(range(len(segments)))
    ax.set_yticks(range(len(segments)))
    ax.set_xticklabels(segment_labels, rotation=45, ha='right')
    ax.set_yticklabels(segment_labels)
    
    ax.set_xlabel('Segment')
    ax.set_ylabel('Segment')
    ax.set_title('Segment Similarity Matrix')
    
    # Add grid
    ax.set_xticks(np.arange(len(segments)) + 0.5, minor=True)
    ax.set_yticks(np.arange(len(segments)) + 0.5, minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_structure_hierarchical(
    results: Dict,
    audio_path: str,
    output_path: Union[str, Path],
    figsize: tuple = (14, 10)
) -> None:
    """
    Create visualization for hierarchical structure analysis.
    
    Shows multiple levels of segmentation.
    
    Args:
        results: Hierarchical structure analysis results
        audio_path: Path to audio file
        output_path: Path to save plot
        figsize: Figure size in inches
    """
    if 'hierarchies' not in results:
        print("No hierarchical data available for visualization")
        return
    
    # Load audio
    y, sr = librosa.load(audio_path)
    duration = librosa.get_duration(y=y, sr=sr)
    
    hierarchies = results['hierarchies']
    num_levels = len(hierarchies)
    
    # Create figure
    fig, axes = plt.subplots(num_levels + 1, 1, figsize=figsize, sharex=True)
    fig.suptitle(
        f"Hierarchical Structure Analysis: {Path(audio_path).name}",
        fontsize=14,
        fontweight='bold'
    )
    
    # Plot waveform on top
    times = librosa.times_like(y, sr=sr)
    axes[0].plot(times, y, alpha=0.6, linewidth=0.5, color='steelblue')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title('Waveform')
    axes[0].grid(True, alpha=0.3)
    
    # Plot each hierarchical level
    for level_idx, hierarchy in enumerate(hierarchies):
        ax = axes[level_idx + 1]
        segments = hierarchy['segments']
        
        # Create timeline visualization
        ax.set_ylim([0, 1])
        ax.set_ylabel(f'Level {level_idx}')
        ax.set_title(f'Level {level_idx}: {hierarchy["num_segments"]} segments')
        
        colors = plt.cm.tab20(np.linspace(0, 1, len(segments)))
        
        for i, seg in enumerate(segments):
            ax.axvspan(seg['start'], seg['end'], alpha=0.5, color=colors[i])
            
            # Add boundary lines
            ax.axvline(seg['start'], color='black', linewidth=1, alpha=0.5)
            
            # Add label
            if seg['end'] - seg['start'] > duration * 0.05:  # Only label if segment is >5% of duration
                mid_time = (seg['start'] + seg['end']) / 2
                ax.text(
                    mid_time, 0.5, seg['label'],
                    ha='center', va='center',
                    fontsize=8,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.7)
                )
        
        ax.set_yticks([])
        ax.grid(True, alpha=0.3, axis='x')
    
    # Set x-axis for bottom plot
    axes[-1].set_xlabel('Time (s)')
    axes[-1].set_xlim([0, duration])
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


