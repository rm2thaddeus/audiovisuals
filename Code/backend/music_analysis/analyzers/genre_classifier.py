"""
Audio Event Classifier - Pre-trained Audio Spectrogram Transformer

Wraps `MIT/ast-finetuned-audioset-10-10-0.4593` to detect audio events, instruments, and sound types.
Provides 527 audio classes including instruments, vocals, genres, and sound textures.
"""

import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import torch
import torch.nn.functional as F
import torchaudio
from transformers import (
    AutoFeatureExtractor,
    AutoModelForAudioClassification,
)


DEFAULT_MODEL = "MIT/ast-finetuned-audioset-10-10-0.4593"


@dataclass
class AudioEventPrediction:
    """Container for individual prediction entries."""

    label: str
    score: float
    logit: float


class AudioEventClassifier:
    """Detect audio events, instruments, and sound types using Audio Spectrogram Transformer (AST)."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: Optional[str] = None,
        cache_dir: Optional[str] = None,
    ) -> None:
        """
        Initialize genre classifier.

        Args:
            model_name: HuggingFace model identifier
            device: Preferred device ('cpu', 'cuda', or None for auto)
            cache_dir: Optional directory for model cache
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.device = self._resolve_device(device)
        self.version = "0.1.0"

        self.model = AutoModelForAudioClassification.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True,
        ).to(self.device)
        self.model.eval()

        self.feature_extractor = AutoFeatureExtractor.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True,
        )

        self.labels = [
            label for _, label in sorted(self.model.config.id2label.items())
        ]

    def analyze(
        self,
        audio_path: str,
        top_k: int = 10,
        window_seconds: float = 10.0,
        overlap: float = 0.25,
        max_chunks: Optional[int] = None,
    ) -> Dict:
        """
        Analyze audio file and detect audio events.

        Args:
            audio_path: Path to audio file
            top_k: Number of top predictions to keep (default 10 for richer features)
            window_seconds: Analysis window size in seconds (default 10s for AST)
            overlap: Window overlap ratio (0.0 - 0.9)
            max_chunks: Optional maximum number of chunks to process

        Returns:
            Dictionary containing audio event predictions and metadata
        """
        start_time = time.time()
        audio_path = Path(audio_path)

        waveform, sample_rate = torchaudio.load(str(audio_path))

        # Convert to mono to match model expectations
        if waveform.dim() == 2:
            waveform = waveform.mean(dim=0)

        target_sr = self.feature_extractor.sampling_rate
        if sample_rate != target_sr:
            waveform = torchaudio.functional.resample(
                waveform, sample_rate, target_sr
            )
            sample_rate = target_sr

        # Normalize waveform to [-1, 1]
        waveform = waveform / waveform.abs().max().clamp(min=1e-8)

        chunk_samples = max(int(window_seconds * sample_rate), 1)
        total_samples = waveform.shape[-1]

        if total_samples <= chunk_samples:
            segments = [waveform]
            segment_ranges = [(0, total_samples)]
        else:
            step = max(int(chunk_samples * (1.0 - overlap)), 1)
            segments = []
            segment_ranges = []
            for start in range(0, total_samples, step):
                end = min(start + chunk_samples, total_samples)
                chunk = waveform[start:end]

                if chunk.shape[-1] < chunk_samples:
                    padding = chunk_samples - chunk.shape[-1]
                    chunk = F.pad(chunk, (0, padding))

                segments.append(chunk)
                segment_ranges.append((start, end))

                if max_chunks and len(segments) >= max_chunks:
                    break

        logits_list: List[torch.Tensor] = []
        chunk_predictions: List[Dict] = []
        analysis_top_k = max(1, min(top_k, len(self.labels)))

        for idx, (chunk, (start_idx, end_idx)) in enumerate(
            zip(segments, segment_ranges)
        ):
            inputs = self.feature_extractor(
                chunk.cpu().numpy(),
                sampling_rate=sample_rate,
                return_tensors="pt",
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)

            logits = outputs.logits[0].cpu()
            logits_list.append(logits)

            probabilities = torch.softmax(logits, dim=-1)
            scores, indices = torch.topk(probabilities, analysis_top_k)

            chunk_predictions.append(
                {
                    "chunk_index": idx,
                    "start": start_idx / sample_rate,
                    "end": end_idx / sample_rate,
                    "duration": (end_idx - start_idx) / sample_rate,
                    "top_label": self.model.config.id2label[int(indices[0])],
                    "confidence": float(scores[0]),
                    "events": [
                        {
                            "label": self.model.config.id2label[int(i)],
                            "score": float(s),
                        }
                        for s, i in zip(scores.tolist(), indices.tolist())
                    ],
                }
            )

        avg_logits = torch.stack(logits_list, dim=0).mean(dim=0)
        probabilities = torch.softmax(avg_logits, dim=-1)
        scores, indices = torch.topk(probabilities, analysis_top_k)

        predictions: List[AudioEventPrediction] = [
            AudioEventPrediction(
                label=self.model.config.id2label[int(index)],
                score=float(score),
                logit=float(avg_logits[int(index)]),
            )
            for score, index in zip(scores.tolist(), indices.tolist())
        ]

        primary_prediction = predictions[0]

        processing_time = time.time() - start_time

        results: Dict = {
            "primary_label": primary_prediction.label,
            "primary_confidence": primary_prediction.score,
            "predictions": [
                {
                    "label": pred.label,
                    "score": pred.score,
                    "logit": pred.logit,
                }
                for pred in predictions
            ],
            "chunk_predictions": chunk_predictions,
            "label_set": self.labels,
            "num_labels": len(self.labels),
            "processing_time": round(processing_time, 3),
            "metadata": {
                "filename": audio_path.name,
                "filepath": str(audio_path.absolute()),
                "analyzer": "audio_event_classifier",
                "version": self.version,
                "model_name": self.model_name,
                "model_labels_count": len(self.labels),
                "device": self.device,
                "sample_rate": sample_rate,
                "window_seconds": window_seconds,
                "overlap": overlap,
                "num_chunks": len(chunk_predictions),
                "timestamp": datetime.now().isoformat(),
            },
        }

        return results

    @staticmethod
    def _resolve_device(device: Optional[str]) -> str:
        """Resolve device string."""
        if device:
            if device == "cuda" and not torch.cuda.is_available():
                return "cpu"
            return device
        return "cuda" if torch.cuda.is_available() else "cpu"


def classify_audio_events(audio_path: str, **kwargs) -> Dict:
    """
    Convenience function for audio event classification.

    Args:
        audio_path: Path to audio file
        **kwargs: Additional classifier arguments

    Returns:
        Audio event classification results
    """
    classifier = AudioEventClassifier(**kwargs)
    return classifier.analyze(audio_path)


