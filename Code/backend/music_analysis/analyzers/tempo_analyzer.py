"""
Tempo Analyzer - Extract BPM and beat positions

Uses librosa beat tracking to extract tempo and beat timestamps.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import librosa
import numpy as np


class TempoAnalyzer:
    """Analyze tempo and beat positions in audio files."""
    
    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """
        Initialize tempo analyzer.
        
        Args:
            sr: Target sample rate for analysis
            hop_length: Hop length for beat tracking
        """
        self.sr = sr
        self.hop_length = hop_length
        self.version = "0.1.0"
    
    def analyze(
        self,
        audio_path: str,
        onset_envelope: Optional[np.ndarray] = None,
        start_bpm: float = 120.0
    ) -> Dict:
        """
        Analyze tempo and beats in an audio file.
        
        Args:
            audio_path: Path to audio file
            onset_envelope: Pre-computed onset envelope (optional)
            start_bpm: Initial BPM estimate for tracking
            
        Returns:
            Dictionary with tempo analysis results
            
        Example:
            >>> analyzer = TempoAnalyzer()
            >>> results = analyzer.analyze("song.mp3")
            >>> print(f"Tempo: {results['tempo']} BPM")
        """
        start_time = time.time()
        audio_path = Path(audio_path)
        
        # Load audio
        y, sr = librosa.load(str(audio_path), sr=self.sr)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Extract onset envelope
        if onset_envelope is None:
            onset_envelope = librosa.onset.onset_strength(
                y=y, sr=sr, hop_length=self.hop_length
            )
        
        # Estimate tempo
        tempo, beat_frames = librosa.beat.beat_track(
            onset_envelope=onset_envelope,
            sr=sr,
            hop_length=self.hop_length,
            start_bpm=start_bpm
        )
        
        # Convert to scalar if array
        if isinstance(tempo, np.ndarray):
            tempo = float(tempo[0]) if len(tempo) > 0 else 120.0
        else:
            tempo = float(tempo)
        
        # Convert beat frames to timestamps
        beat_times = librosa.frames_to_time(
            beat_frames, sr=sr, hop_length=self.hop_length
        )
        
        # Calculate beat confidence (consistency measure)
        beat_confidence = self._calculate_beat_confidence(beat_times, tempo)
        
        # Detect time signature (simple 4/4 vs 3/4 detection)
        time_signature = self._estimate_time_signature(beat_times, tempo)
        
        processing_time = time.time() - start_time
        
        # Build result dictionary
        results = {
            "tempo": round(tempo, 2),
            "tempo_confidence": round(beat_confidence, 3),
            "time_signature": time_signature,
            "num_beats": len(beat_times),
            "beats": beat_times.tolist(),
            "beat_frames": beat_frames.tolist(),
            "hop_length": self.hop_length,
            "sr": sr,
            "duration": round(duration, 2),
            "processing_time": round(processing_time, 3),
            "metadata": {
                "filename": audio_path.name,
                "filepath": str(audio_path.absolute()),
                "analyzer": "tempo_analyzer",
                "version": self.version,
                "model": "librosa",
                "timestamp": datetime.now().isoformat(),
                "sample_rate": sr,
                "audio_duration": round(duration, 2)
            }
        }
        
        return results
    
    def _calculate_beat_confidence(
        self, beat_times: np.ndarray, tempo: float
    ) -> float:
        """
        Calculate confidence in beat detection based on consistency.
        
        Higher confidence = more regular beat intervals.
        
        Args:
            beat_times: Array of beat timestamps
            tempo: Estimated tempo in BPM
            
        Returns:
            Confidence score between 0 and 1
        """
        if len(beat_times) < 2:
            return 0.0
        
        # Expected interval between beats
        expected_interval = 60.0 / tempo
        
        # Actual intervals
        intervals = np.diff(beat_times)
        
        # Calculate deviation from expected
        deviations = np.abs(intervals - expected_interval)
        normalized_deviations = deviations / expected_interval
        
        # Confidence = 1 - average normalized deviation
        confidence = 1.0 - np.mean(normalized_deviations)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))
    
    def _estimate_time_signature(
        self, beat_times: np.ndarray, tempo: float
    ) -> str:
        """
        Estimate time signature (4/4 vs 3/4).
        
        Simple heuristic: look for strong beat patterns.
        
        Args:
            beat_times: Array of beat timestamps
            tempo: Estimated tempo in BPM
            
        Returns:
            Time signature string (e.g., "4/4", "3/4")
        """
        if len(beat_times) < 8:
            return "4/4"  # Default assumption
        
        # Analyze beat groupings
        intervals = np.diff(beat_times)
        
        # Look for patterns of 3 or 4 equal intervals
        # (This is a simplified heuristic)
        median_interval = np.median(intervals)
        
        # Check if intervals cluster around 3/4 patterns
        three_cluster = np.sum(np.abs(intervals - median_interval) < 0.1 * median_interval)
        four_cluster = np.sum(np.abs(intervals - median_interval) < 0.15 * median_interval)
        
        # Simple decision (could be improved with more analysis)
        if three_cluster > four_cluster * 0.8:
            return "3/4"
        else:
            return "4/4"
    
    def analyze_section(
        self,
        audio_path: str,
        start_time: float,
        end_time: float
    ) -> Dict:
        """
        Analyze tempo for a specific section of audio.
        
        Args:
            audio_path: Path to audio file
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Tempo analysis for the specified section
        """
        # Load only the specified section
        y, sr = librosa.load(
            audio_path,
            sr=self.sr,
            offset=start_time,
            duration=end_time - start_time
        )
        
        # Create temporary file path for metadata
        temp_path = Path(audio_path).with_name(
            f"{Path(audio_path).stem}_section_{start_time}-{end_time}.mp3"
        )
        
        # Analyze section
        results = self.analyze(str(temp_path))
        
        # Adjust beat times to absolute positions
        results["beats"] = [t + start_time for t in results["beats"]]
        results["metadata"]["section"] = {
            "start": start_time,
            "end": end_time
        }
        
        return results


def analyze_tempo(audio_path: str, **kwargs) -> Dict:
    """
    Convenience function for tempo analysis.
    
    Args:
        audio_path: Path to audio file
        **kwargs: Additional arguments for TempoAnalyzer
        
    Returns:
        Tempo analysis results
    """
    analyzer = TempoAnalyzer(**kwargs)
    return analyzer.analyze(audio_path)

