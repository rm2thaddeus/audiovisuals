"""
Audio Feature Analyzer - Phase A Baseline (FFT-only)

Extracts audio features for CPPN visualization:
- FFT features: bass, mid, treble frequency bands
- Spectral features: centroid, rolloff, flux
- Temporal features: time progression, beat detection

Usage:
    analyzer = AudioAnalyzer()
    features = analyzer.analyze(audio_path, fps=60)
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, Tuple
import warnings

warnings.filterwarnings('ignore')


class AudioAnalyzer:
    """Extract audio features for CPPN inputs."""
    
    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """
        Initialize analyzer.
        
        Args:
            sr: Target sample rate for audio loading
            hop_length: Hop length for FFT analysis
        """
        self.sr = sr
        self.hop_length = hop_length
        
    def analyze(self, audio_path: str, fps: int = 60) -> Dict:
        """
        Analyze audio file and extract features.
        
        Args:
            audio_path: Path to audio file (MP3, WAV, etc.)
            fps: Target frames per second for feature extraction
            
        Returns:
            Dictionary containing:
                - 'audio': Original audio signal
                - 'sr': Sample rate
                - 'duration': Audio duration in seconds
                - 'features': Feature tensor (num_frames, feature_dim)
                - 'fps': Frames per second
                - 'num_frames': Number of frames
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        print(f"Loading audio: {audio_path.name}")
        
        # Load audio
        audio, sr = librosa.load(audio_path, sr=self.sr, mono=True)
        duration = len(audio) / sr
        
        print(f"Duration: {duration:.2f}s, Sample rate: {sr}Hz")
        
        # Calculate hop length for target FPS
        hop_length_fps = sr // fps
        
        print(f"Extracting features @ {fps} FPS...")
        
        # Extract FFT features
        fft_features = self._extract_fft_features(audio, sr, hop_length_fps)
        
        # Extract spectral features
        spectral_features = self._extract_spectral_features(audio, sr, hop_length_fps)
        
        # Extract temporal features
        temporal_features = self._extract_temporal_features(audio, sr, hop_length_fps, duration)
        
        # Combine all features
        features = np.concatenate([
            fft_features,
            spectral_features,
            temporal_features
        ], axis=1)
        
        num_frames = features.shape[0]
        feature_dim = features.shape[1]
        
        print(f"Features extracted: {num_frames} frames x {feature_dim} dimensions")
        
        return {
            'audio': audio,
            'sr': sr,
            'duration': duration,
            'features': features,
            'fps': fps,
            'num_frames': num_frames,
            'feature_names': self._get_feature_names()
        }
    
    def _extract_fft_features(self, audio: np.ndarray, sr: int, hop_length: int) -> np.ndarray:
        """Extract frequency band features (bass, mid, treble)."""
        # Compute Short-Time Fourier Transform
        stft = librosa.stft(audio, hop_length=hop_length, n_fft=2048)
        magnitude = np.abs(stft)
        
        # Define frequency bands (Hz)
        bass_range = (20, 250)      # Bass
        mid_range = (250, 4000)     # Midrange
        treble_range = (4000, 20000) # Treble
        
        # Convert Hz to frequency bins
        freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
        
        bass_bins = np.where((freqs >= bass_range[0]) & (freqs <= bass_range[1]))[0]
        mid_bins = np.where((freqs >= mid_range[0]) & (freqs <= mid_range[1]))[0]
        treble_bins = np.where((freqs >= treble_range[0]) & (freqs <= treble_range[1]))[0]
        
        # Compute mean energy in each band
        bass = np.mean(magnitude[bass_bins, :], axis=0)
        mid = np.mean(magnitude[mid_bins, :], axis=0)
        treble = np.mean(magnitude[treble_bins, :], axis=0)
        
        # Stack features
        fft_features = np.vstack([bass, mid, treble]).T
        
        return fft_features
    
    def _extract_spectral_features(self, audio: np.ndarray, sr: int, hop_length: int) -> np.ndarray:
        """Extract spectral characteristics."""
        # Spectral centroid (brightness)
        centroid = librosa.feature.spectral_centroid(y=audio, sr=sr, hop_length=hop_length)[0]
        
        # Spectral rolloff (frequency below which 85% of energy is contained)
        rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr, hop_length=hop_length)[0]
        
        # Spectral flux (change in spectrum over time)
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr, hop_length=hop_length)
        
        # Stack features
        spectral_features = np.vstack([centroid, rolloff, onset_env]).T
        
        return spectral_features
    
    def _extract_temporal_features(self, audio: np.ndarray, sr: int, hop_length: int, duration: float) -> np.ndarray:
        """Extract temporal features."""
        num_frames = len(audio) // hop_length + 1
        
        # Time progression (0 to 1)
        time = np.linspace(0, 1, num_frames)
        
        # Detect beats
        tempo, beats = librosa.beat.beat_track(y=audio, sr=sr, hop_length=hop_length)
        
        # Create beat signal (1 at beat, decay to 0)
        beat_signal = np.zeros(num_frames)
        beat_frames = librosa.frames_to_samples(beats, hop_length=hop_length) // hop_length
        beat_frames = beat_frames[beat_frames < num_frames]
        
        if len(beat_frames) > 0:
            beat_signal[beat_frames] = 1.0
            # Apply exponential decay
            for i in range(1, len(beat_signal)):
                beat_signal[i] = max(beat_signal[i], beat_signal[i-1] * 0.8)
        
        # Overall energy (RMS)
        rms = librosa.feature.rms(y=audio, hop_length=hop_length)[0]
        
        # Stack features
        temporal_features = np.vstack([time, beat_signal, rms]).T
        
        return temporal_features
    
    def _get_feature_names(self) -> list:
        """Get names of extracted features."""
        return [
            'bass', 'mid', 'treble',           # FFT features
            'centroid', 'rolloff', 'flux',     # Spectral features
            'time', 'beat', 'rms'              # Temporal features
        ]
    
    def normalize_features(self, features: np.ndarray, method: str = 'minmax') -> np.ndarray:
        """
        Normalize features to CPPN input range.
        
        Args:
            features: Feature tensor (num_frames, feature_dim)
            method: 'minmax' for [-1, 1] or 'zscore' for standardization
            
        Returns:
            Normalized features
        """
        if method == 'minmax':
            # Normalize to [-1, 1]
            min_val = features.min(axis=0, keepdims=True)
            max_val = features.max(axis=0, keepdims=True)
            
            # Avoid division by zero
            range_val = max_val - min_val
            range_val[range_val == 0] = 1.0
            
            normalized = 2 * (features - min_val) / range_val - 1
            
        elif method == 'zscore':
            # Standardize (mean=0, std=1)
            mean = features.mean(axis=0, keepdims=True)
            std = features.std(axis=0, keepdims=True)
            std[std == 0] = 1.0
            
            normalized = (features - mean) / std
        else:
            raise ValueError(f"Unknown normalization method: {method}")
            
        return normalized


if __name__ == '__main__':
    # Test the analyzer
    import sys
    
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        print("Usage: python audio_analyzer.py <audio_file>")
        sys.exit(1)
    
    analyzer = AudioAnalyzer()
    result = analyzer.analyze(audio_file, fps=30)
    
    print(f"\nFeature summary:")
    print(f"  Shape: {result['features'].shape}")
    print(f"  Feature names: {', '.join(result['feature_names'])}")
    print(f"  Min values: {result['features'].min(axis=0)}")
    print(f"  Max values: {result['features'].max(axis=0)}")
    
    # Normalize features
    normalized = analyzer.normalize_features(result['features'])
    print(f"\nNormalized features:")
    print(f"  Min: {normalized.min():.3f}, Max: {normalized.max():.3f}")

