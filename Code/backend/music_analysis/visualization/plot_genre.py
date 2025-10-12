"""
Genre visualization - Aggregated probabilities and segment timeline.

Creates Matplotlib visualizations for genre classification results.
"""

from pathlib import Path
from typing import Dict, List, Union

import matplotlib.pyplot as plt


PALETTE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


def _genre_color_mapping(genres: List[str]) -> Dict[str, str]:
    """Assign distinct colors to each genre."""
    return {
        genre: PALETTE[idx % len(PALETTE)]
        for idx, genre in enumerate(genres)
    }


def plot_genre(
    results: Dict,
    audio_path: str,
    output_path: Union[str, Path],
    figsize: tuple = (12, 8),
) -> None:
    """
    Create visualization for genre classification.

    Args:
        results: Genre classification results dictionary
        audio_path: Path to original audio file
        output_path: Path to save plot PNG
        figsize: Figure size in inches
    """
    predictions = results.get("predictions", [])
    chunk_predictions = results.get("chunk_predictions", [])
    audio_name = Path(audio_path).name

    labels = [entry["label"] for entry in predictions]
    scores = [entry["score"] for entry in predictions]
    colors = _genre_color_mapping(labels or results.get("label_set", []))

    fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=False)
    fig.suptitle(
        f"Genre Classification: {audio_name}",
        fontsize=14,
        fontweight="bold",
    )

    # Bar chart for aggregated probabilities
    ax1 = axes[0]
    if predictions:
        ax1.barh(
            labels[::-1],
            [score * 100 for score in scores[::-1]],
            color=[colors[label] for label in labels[::-1]],
            alpha=0.85,
        )
        ax1.set_xlabel("Confidence (%)")
        ax1.set_title("Aggregated Genre Probabilities")
        ax1.grid(True, axis="x", alpha=0.3)
        ax1.set_xlim(0, max(100, max(score * 100 for score in scores) * 1.1))
    else:
        ax1.text(
            0.5,
            0.5,
            "No predictions available",
            ha="center",
            va="center",
            fontsize=12,
        )
        ax1.axis("off")

    # Timeline for chunk predictions
    ax2 = axes[1]
    if chunk_predictions:
        unique_labels = list({chunk["top_label"] for chunk in chunk_predictions})
        chunk_colors = _genre_color_mapping(unique_labels)

        for chunk in chunk_predictions:
            start = chunk["start"]
            duration = chunk["end"] - chunk["start"]
            label = chunk["top_label"]
            confidence = chunk["confidence"] * 100

            ax2.broken_barh(
                [(start, duration)],
                (0, 1),
                facecolors=chunk_colors.get(label, "#999999"),
                edgecolor="#222222",
                linewidth=0.8,
                alpha=0.85,
            )
            ax2.text(
                start + duration / 2,
                0.5,
                f"{label}\n{confidence:.0f}%",
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                fontweight="bold",
            )

        ax2.set_ylim(0, 1)
        ax2.set_yticks([])
        ax2.set_xlabel("Time (seconds)")
        ax2.set_title("Segment-Level Predictions")
        ax2.grid(True, axis="x", alpha=0.3)
        ax2.set_xlim(
            0,
            max(chunk["end"] for chunk in chunk_predictions),
        )

        handles = [
            plt.Line2D(
                [0],
                [0],
                color=color,
                lw=4,
                label=label,
            )
            for label, color in chunk_colors.items()
        ]
        if handles:
            ax2.legend(
                handles=handles,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.15),
                ncol=min(len(handles), 4),
                fontsize=8,
            )
    else:
        ax2.text(
            0.5,
            0.5,
            "No chunk predictions available",
            ha="center",
            va="center",
            fontsize=12,
        )
        ax2.axis("off")

    metadata_text = (
        f"Primary event: {results.get('primary_label', 'N/A')} "
        f"({results.get('primary_confidence', 0.0) * 100:.1f}%) | "
        f"Chunks: {len(chunk_predictions)} | "
        f"Processing: {results.get('processing_time', 0.0):.2f}s"
    )
    fig.text(0.5, 0.02, metadata_text, ha="center", fontsize=10, style="italic")

    plt.tight_layout(rect=[0, 0.04, 1, 0.97])
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
