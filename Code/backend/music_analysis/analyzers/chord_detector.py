"""
Chord Detector - Chord recognition from audio

Uses chroma features and pattern matching to detect chords.
For more accurate results, CREMA model can be used (requires TensorFlow).
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import librosa
import numpy as np


# Chord templates (major and minor triads)
CHORD_TEMPLATES = {
    'C': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],  # C E G
    'C#': [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    'D': [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],
    'D#': [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
    'E': [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    'F': [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    'F#': [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    'G': [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    'G#': [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    'A': [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    'A#': [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    'B': [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
    # Minor chords
    'Cm': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    'C#m': [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    'Dm': [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    'D#m': [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0],
    'Em': [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    'Fm': [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    'F#m': [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
    'Gm': [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0],
    'G#m': [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
    'Am': [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    'A#m': [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    'Bm': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
}


class ChordDetector:
    """Detect chords using chroma features and template matching."""
    
    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """
        Initialize chord detector.
        
        Args:
            sr: Target sample rate
            hop_length: Hop length for chroma extraction
        """
        self.sr = sr
        self.hop_length = hop_length
        self.version = "0.1.0"
        
        # Normalize chord templates
        self.chord_templates = {
            name: np.array(template) / np.sum(template)
            for name, template in CHORD_TEMPLATES.items()
        }
    
    def analyze(
        self,
        audio_path: str,
        smoothing_window: int = 5
    ) -> Dict:
        """
        Detect chords in an audio file.
        
        Args:
            audio_path: Path to audio file
            smoothing_window: Window size for smoothing chord detections
            
        Returns:
            Dictionary with chord detection results
            
        Example:
            >>> detector = ChordDetector()
            >>> results = detector.analyze("song.mp3")
            >>> print(f"Detected {len(results['chords'])} chord changes")
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
        
        # Detect chords frame by frame
        frame_chords = []
        frame_confidences = []
        
        for i in range(chroma.shape[1]):
            chroma_frame = chroma[:, i]
            chroma_frame = chroma_frame / (np.sum(chroma_frame) + 1e-10)
            
            chord, confidence = self._match_chord(chroma_frame)
            frame_chords.append(chord)
            frame_confidences.append(confidence)
        
        # Convert frame indices to times
        frame_times = librosa.frames_to_time(
            np.arange(len(frame_chords)),
            sr=sr,
            hop_length=self.hop_length
        )
        
        # Smooth and merge chord detections
        chords = self._merge_chords(
            frame_chords,
            frame_confidences,
            frame_times,
            smoothing_window
        )
        
        # Get chord vocabulary (unique chords detected)
        chord_vocabulary = sorted(set(c['chord'] for c in chords))
        
        processing_time = time.time() - start_time
        
        results = {
            "chords": chords,
            "chord_vocabulary": chord_vocabulary,
            "chord_changes": len(chords),
            "unique_chords": len(chord_vocabulary),
            "duration": round(duration, 2),
            "processing_time": round(processing_time, 3),
            "metadata": {
                "filename": audio_path.name,
                "filepath": str(audio_path.absolute()),
                "analyzer": "chord_detector",
                "version": self.version,
                "model": "librosa-chroma-template-matching",
                "timestamp": datetime.now().isoformat(),
                "sample_rate": sr,
                "audio_duration": round(duration, 2)
            }
        }
        
        return results
    
    def _match_chord(self, chroma: np.ndarray) -> Tuple[str, float]:
        """
        Match chroma vector to chord templates.
        
        Args:
            chroma: 12-dimensional chroma vector
            
        Returns:
            Tuple of (chord_name, confidence)
        """
        best_chord = "N"  # No chord
        best_score = 0.0
        
        for chord_name, template in self.chord_templates.items():
            # Correlation between chroma and template
            score = np.corrcoef(chroma, template)[0, 1]
            
            if score > best_score:
                best_score = score
                best_chord = chord_name
        
        # If score is too low, mark as "N" (no chord)
        if best_score < 0.5:
            best_chord = "N"
        
        return best_chord, float(best_score)
    
    def _merge_chords(
        self,
        frame_chords: List[str],
        frame_confidences: List[float],
        frame_times: np.ndarray,
        min_duration: int = 5
    ) -> List[Dict]:
        """
        Merge consecutive same chords and filter short detections.
        
        Args:
            frame_chords: Chord names per frame
            frame_confidences: Confidence scores per frame
            frame_times: Time stamps per frame
            min_duration: Minimum number of frames for a chord
            
        Returns:
            List of merged chord detections
        """
        if not frame_chords:
            return []
        
        merged = []
        current_chord = frame_chords[0]
        start_time = frame_times[0]
        confidences = [frame_confidences[0]]
        
        for i in range(1, len(frame_chords)):
            if frame_chords[i] == current_chord:
                # Same chord, accumulate
                confidences.append(frame_confidences[i])
            else:
                # Chord changed, save previous chord if long enough
                if len(confidences) >= min_duration:
                    merged.append({
                        "time": round(float(start_time), 2),
                        "chord": current_chord,
                        "confidence": round(float(np.mean(confidences)), 3),
                        "duration": round(float(frame_times[i-1] - start_time), 2)
                    })
                
                # Start new chord
                current_chord = frame_chords[i]
                start_time = frame_times[i]
                confidences = [frame_confidences[i]]
        
        # Add last chord
        if len(confidences) >= min_duration:
            merged.append({
                "time": round(float(start_time), 2),
                "chord": current_chord,
                "confidence": round(float(np.mean(confidences)), 3),
                "duration": round(float(frame_times[-1] - start_time), 2)
            })
        
        return merged


def detect_chords(audio_path: str, **kwargs) -> Dict:
    """
    Convenience function for chord detection.
    
    Args:
        audio_path: Path to audio file
        **kwargs: Additional arguments for ChordDetector
        
    Returns:
        Chord detection results
    """
    detector = ChordDetector(**kwargs)
    return detector.analyze(audio_path)


