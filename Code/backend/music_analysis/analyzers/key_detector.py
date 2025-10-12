"""
Key Detector - Musical key detection using chroma features

Uses Krumhansl-Schmuckler algorithm with librosa chroma features.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import librosa
import numpy as np


# Krumhansl-Schmuckler key profiles
# Major and minor key templates (C=0, C#=1, ..., B=11)
MAJOR_PROFILE = np.array([
    6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88
])

MINOR_PROFILE = np.array([
    6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17
])

# Key names
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


class KeyDetector:
    """Detect musical key using chroma features and key profiles."""
    
    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """
        Initialize key detector.
        
        Args:
            sr: Target sample rate
            hop_length: Hop length for chroma extraction
        """
        self.sr = sr
        self.hop_length = hop_length
        self.version = "0.1.0"
        
        # Normalize key profiles
        self.major_profile = MAJOR_PROFILE / np.sum(MAJOR_PROFILE)
        self.minor_profile = MINOR_PROFILE / np.sum(MINOR_PROFILE)
    
    def analyze(self, audio_path: str) -> Dict:
        """
        Detect the musical key of an audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with key detection results
            
        Example:
            >>> detector = KeyDetector()
            >>> results = detector.analyze("song.mp3")
            >>> print(f"Key: {results['key']} {results['scale']}")
        """
        start_time = time.time()
        audio_path = Path(audio_path)
        
        # Load audio
        y, sr = librosa.load(str(audio_path), sr=self.sr)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Extract chroma features
        chroma = librosa.feature.chroma_cqt(
            y=y, sr=sr, hop_length=self.hop_length
        )
        
        # Average chroma over time
        chroma_avg = np.mean(chroma, axis=1)
        
        # Normalize
        chroma_avg = chroma_avg / np.sum(chroma_avg)
        
        # Correlate with all 24 keys (12 major + 12 minor)
        key_scores = self._correlate_with_keys(chroma_avg)
        
        # Find best key
        best_idx = np.argmax(key_scores)
        best_score = key_scores[best_idx]
        
        # Determine if major or minor
        if best_idx < 12:
            key = KEY_NAMES[best_idx]
            scale = "major"
        else:
            key = KEY_NAMES[best_idx - 12]
            scale = "minor"
        
        # Get alternative keys
        alternatives = self._get_alternatives(key_scores, top_k=3)
        
        # Calculate relative major/minor
        relative_key = self._get_relative_key(key, scale)
        
        processing_time = time.time() - start_time
        
        results = {
            "key": key,
            "scale": scale,
            "confidence": round(float(best_score), 3),
            "key_profile": chroma_avg.tolist(),
            "relative_key": relative_key,
            "alternatives": alternatives,
            "chroma_features": chroma.tolist(),
            "duration": round(duration, 2),
            "processing_time": round(processing_time, 3),
            "metadata": {
                "filename": audio_path.name,
                "filepath": str(audio_path.absolute()),
                "analyzer": "key_detector",
                "version": self.version,
                "model": "Krumhansl-Schmuckler",
                "timestamp": datetime.now().isoformat(),
                "sample_rate": sr,
                "audio_duration": round(duration, 2)
            }
        }
        
        return results
    
    def _correlate_with_keys(self, chroma: np.ndarray) -> np.ndarray:
        """
        Correlate chroma vector with all 24 key profiles.
        
        Args:
            chroma: 12-dimensional chroma vector
            
        Returns:
            Array of 24 correlation scores (12 major + 12 minor)
        """
        scores = np.zeros(24)
        
        # Test all 12 major keys
        for i in range(12):
            shifted_profile = np.roll(self.major_profile, i)
            scores[i] = np.corrcoef(chroma, shifted_profile)[0, 1]
        
        # Test all 12 minor keys
        for i in range(12):
            shifted_profile = np.roll(self.minor_profile, i)
            scores[12 + i] = np.corrcoef(chroma, shifted_profile)[0, 1]
        
        return scores
    
    def _get_alternatives(
        self, key_scores: np.ndarray, top_k: int = 3
    ) -> List[Dict]:
        """
        Get alternative key candidates.
        
        Args:
            key_scores: Array of correlation scores for all 24 keys
            top_k: Number of alternatives to return
            
        Returns:
            List of alternative key dictionaries
        """
        # Get indices of top k scores (excluding the best one)
        top_indices = np.argsort(key_scores)[::-1][1:top_k+1]
        
        alternatives = []
        for idx in top_indices:
            if idx < 12:
                key = KEY_NAMES[idx]
                scale = "major"
            else:
                key = KEY_NAMES[idx - 12]
                scale = "minor"
            
            alternatives.append({
                "key": f"{key} {scale}",
                "confidence": round(float(key_scores[idx]), 3)
            })
        
        return alternatives
    
    def _get_relative_key(self, key: str, scale: str) -> str:
        """
        Get relative major/minor key.
        
        Args:
            key: Key name (e.g., "C")
            scale: Scale type ("major" or "minor")
            
        Returns:
            Relative key string (e.g., "A minor" for C major)
        """
        key_idx = KEY_NAMES.index(key)
        
        if scale == "major":
            # Relative minor is 3 semitones down
            relative_idx = (key_idx - 3) % 12
            relative_scale = "minor"
        else:
            # Relative major is 3 semitones up
            relative_idx = (key_idx + 3) % 12
            relative_scale = "major"
        
        return f"{KEY_NAMES[relative_idx]} {relative_scale}"
    
    def analyze_time_varying(
        self, audio_path: str, window_size: float = 30.0
    ) -> Dict:
        """
        Analyze key over time with sliding windows.
        
        Useful for detecting key changes during the song.
        
        Args:
            audio_path: Path to audio file
            window_size: Window size in seconds
            
        Returns:
            Dictionary with time-varying key analysis
        """
        audio_path = Path(audio_path)
        
        # Load audio
        y, sr = librosa.load(str(audio_path), sr=self.sr)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Calculate number of windows
        hop_size = window_size / 2  # 50% overlap
        num_windows = int((duration - window_size) / hop_size) + 1
        
        key_timeline = []
        
        for i in range(num_windows):
            start_time = i * hop_size
            end_time = start_time + window_size
            
            # Extract window
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            y_window = y[start_sample:end_sample]
            
            # Extract chroma for window
            chroma = librosa.feature.chroma_cqt(
                y=y_window, sr=sr, hop_length=self.hop_length
            )
            chroma_avg = np.mean(chroma, axis=1)
            chroma_avg = chroma_avg / np.sum(chroma_avg)
            
            # Detect key for window
            key_scores = self._correlate_with_keys(chroma_avg)
            best_idx = np.argmax(key_scores)
            
            if best_idx < 12:
                key = KEY_NAMES[best_idx]
                scale = "major"
            else:
                key = KEY_NAMES[best_idx - 12]
                scale = "minor"
            
            key_timeline.append({
                "time": round(start_time, 2),
                "key": key,
                "scale": scale,
                "confidence": round(float(key_scores[best_idx]), 3)
            })
        
        # Determine overall key (most common)
        key_counts = {}
        for entry in key_timeline:
            key_str = f"{entry['key']} {entry['scale']}"
            key_counts[key_str] = key_counts.get(key_str, 0) + 1
        
        overall_key = max(key_counts, key=key_counts.get)
        key, scale = overall_key.split()
        
        results = {
            "overall_key": key,
            "overall_scale": scale,
            "key_timeline": key_timeline,
            "num_changes": len(set(f"{e['key']} {e['scale']}" for e in key_timeline)),
            "duration": round(duration, 2),
            "window_size": window_size,
            "metadata": {
                "filename": audio_path.name,
                "analyzer": "key_detector",
                "mode": "time_varying"
            }
        }
        
        return results


def detect_key(audio_path: str, **kwargs) -> Dict:
    """
    Convenience function for key detection.
    
    Args:
        audio_path: Path to audio file
        **kwargs: Additional arguments for KeyDetector
        
    Returns:
        Key detection results
    """
    detector = KeyDetector(**kwargs)
    return detector.analyze(audio_path)

