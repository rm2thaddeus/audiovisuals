"""
Tempo visualization - Beat timeline plots

Creates matplotlib visualizations for tempo analysis results.
"""

from pathlib import Path
from typing import Dict, Union

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np


def plot_tempo(
    results: Dict,
    audio_path: str,
    output_path: Union[str, Path],
    figsize: tuple = (14, 8)
) -> None:
    """
    Create visualization for tempo analysis.
    
    Shows waveform with beat markers and tempo information.
    
    Args:
        results: Tempo analysis results dictionary
        audio_path: Path to original audio file
        output_path: Path to save plot PNG
        figsize: Figure size in inches
    """
    # Load audio for visualization
    y, sr = librosa.load(audio_path, sr=results['sr'])
    
    # Create figure
    fig, axes = plt.subplots(3, 1, figsize=figsize)
    fig.suptitle(
        f"Tempo Analysis: {Path(audio_path).name}\n"
        f"Tempo: {results['tempo']} BPM | "
        f"Time Signature: {results['time_signature']} | "
        f"Confidence: {results['tempo_confidence']:.1%}",
        fontsize=14,
        fontweight='bold'
    )
    
    # === Plot 1: Waveform with beat markers ===
    ax1 = axes[0]
    times = librosa.times_like(y, sr=sr)
    ax1.plot(times, y, alpha=0.6, linewidth=0.5, color='steelblue')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Waveform with Beat Markers')
    ax1.grid(True, alpha=0.3)
    
    # Add beat markers
    beat_times = np.array(results['beats'])
    for beat_time in beat_times:
        ax1.axvline(beat_time, color='red', alpha=0.5, linewidth=1.5, linestyle='--')
    
    # Highlight first few beats
    for i, beat_time in enumerate(beat_times[:8]):
        ax1.text(
            beat_time, ax1.get_ylim()[1] * 0.9,
            str(i + 1),
            color='red',
            fontweight='bold',
            ha='center'
        )
    
    ax1.set_xlim([0, results['duration']])
    
    # === Plot 2: Onset strength envelope ===
    ax2 = axes[1]
    onset_env = librosa.onset.onset_strength(
        y=y, sr=sr, hop_length=results['hop_length']
    )
    onset_times = librosa.times_like(onset_env, sr=sr, hop_length=results['hop_length'])
    
    ax2.plot(onset_times, onset_env, color='darkgreen', linewidth=1)
    ax2.set_ylabel('Onset Strength')
    ax2.set_title('Onset Strength Envelope')
    ax2.grid(True, alpha=0.3)
    
    # Add beat markers on onset envelope
    for beat_time in beat_times:
        ax2.axvline(beat_time, color='red', alpha=0.5, linewidth=1, linestyle='--')
    
    ax2.set_xlim([0, results['duration']])
    
    # === Plot 3: Beat interval histogram ===
    ax3 = axes[2]
    if len(beat_times) > 1:
        intervals = np.diff(beat_times)
        expected_interval = 60.0 / results['tempo']
        
        ax3.hist(
            intervals,
            bins=30,
            color='steelblue',
            alpha=0.7,
            edgecolor='black'
        )
        ax3.axvline(
            expected_interval,
            color='red',
            linewidth=2,
            linestyle='--',
            label=f'Expected: {expected_interval:.3f}s'
        )
        ax3.set_xlabel('Beat Interval (seconds)')
        ax3.set_ylabel('Count')
        ax3.set_title('Beat Interval Distribution')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # Add metadata text
    metadata_text = (
        f"Beats: {results['num_beats']} | "
        f"Duration: {results['duration']:.1f}s | "
        f"Processing: {results['processing_time']:.2f}s"
    )
    fig.text(0.5, 0.02, metadata_text, ha='center', fontsize=10, style='italic')
    
    # Save figure
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_tempo_section(
    results: Dict,
    audio_path: str,
    output_path: Union[str, Path],
    start_time: float = 0.0,
    duration: float = 30.0
) -> None:
    """
    Create detailed tempo visualization for a specific section.
    
    Useful for zooming into a particular part of the song.
    
    Args:
        results: Tempo analysis results
        audio_path: Path to audio file
        output_path: Path to save plot
        start_time: Section start time in seconds
        duration: Section duration in seconds
    """
    # Load audio section
    y, sr = librosa.load(
        audio_path,
        sr=results['sr'],
        offset=start_time,
        duration=duration
    )
    
    # Filter beats for this section
    beat_times = np.array(results['beats'])
    section_beats = beat_times[
        (beat_times >= start_time) &
        (beat_times < start_time + duration)
    ] - start_time  # Adjust to section time
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot waveform
    times = librosa.times_like(y, sr=sr)
    ax.plot(times, y, alpha=0.6, linewidth=0.8, color='steelblue')
    
    # Add beat markers
    for i, beat_time in enumerate(section_beats):
        ax.axvline(beat_time, color='red', alpha=0.7, linewidth=2, linestyle='--')
        ax.text(
            beat_time, ax.get_ylim()[1] * 0.9,
            str(i + 1),
            color='red',
            fontweight='bold',
            ha='center',
            fontsize=12
        )
    
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('Amplitude', fontsize=12)
    ax.set_title(
        f"Detailed Beat View: {start_time:.1f}s - {start_time + duration:.1f}s\n"
        f"Tempo: {results['tempo']} BPM",
        fontsize=14,
        fontweight='bold'
    )
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

