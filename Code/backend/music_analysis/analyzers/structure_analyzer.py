"""
Structure Analyzer - Music segmentation and structure analysis

Uses MSAF (Music Structure Analysis Framework) to detect structural boundaries
and segment songs into intro, verse, chorus, bridge, outro, etc.
"""

import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import librosa
import numpy as np

# Try to import MSAF, but don't fail if it's not available
try:
    import msaf
    MSAF_AVAILABLE = True
except ImportError:
    MSAF_AVAILABLE = False
    print("Warning: MSAF not available, using simple segmentation")

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)


class StructureAnalyzer:
    """Analyze music structure and detect segment boundaries."""
    
    def __init__(self, sr: int = 22050):
        """
        Initialize structure analyzer.
        
        Args:
            sr: Target sample rate for analysis
        """
        self.sr = sr
        self.version = "0.1.0"
    
    def analyze(
        self,
        audio_path: str,
        algorithm: str = "cnmf",
        boundary_algorithm: str = "sf",
        label_algorithm: str = "fmc2d"
    ) -> Dict:
        """
        Analyze music structure and detect segments.
        
        Args:
            audio_path: Path to audio file
            algorithm: Segmentation algorithm ('cnmf', 'foote', 'olda', 'scluster', 'sf')
            boundary_algorithm: Boundary detection algorithm
            label_algorithm: Label estimation algorithm
            
        Returns:
            Dictionary with structure analysis results
            
        Example:
            >>> analyzer = StructureAnalyzer()
            >>> results = analyzer.analyze("song.mp3")
            >>> print(f"Segments: {results['num_segments']}")
        """
        start_time = time.time()
        audio_path = Path(audio_path)
        
        # Load audio
        y, sr = librosa.load(str(audio_path), sr=self.sr)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Run segmentation
        if MSAF_AVAILABLE:
            try:
                # Segment boundaries (times in seconds)
                boundaries, labels = msaf.process(
                    str(audio_path),
                    boundaries_id=boundary_algorithm,
                    labels_id=label_algorithm,
                    feature="mfcc"  # Use MFCC features
                )
                
                # Convert boundaries to segments
                segments = []
                for i in range(len(boundaries) - 1):
                    start_time_seg = float(boundaries[i])
                    end_time_seg = float(boundaries[i + 1])
                    label = self._interpret_label(labels[i], i) if labels is not None else f"segment_{i}"
                    
                    segments.append({
                        "start": round(start_time_seg, 2),
                        "end": round(end_time_seg, 2),
                        "duration": round(end_time_seg - start_time_seg, 2),
                        "label": label,
                        "index": i
                    })
                
                # Calculate segment similarity if we have labels
                similarity_matrix = None
                if labels is not None:
                    similarity_matrix = self._calculate_similarity_matrix(labels)
                
            except Exception as e:
                # Fallback: create simple segmentation based on duration
                print(f"Warning: MSAF processing failed ({e}), using simple segmentation")
                boundaries, segments, similarity_matrix = self._simple_segmentation(duration)
        else:
            # Use simple segmentation if MSAF not available
            boundaries, segments, similarity_matrix = self._simple_segmentation(duration)
        
        processing_time = time.time() - start_time
        
        results = {
            "segments": segments,
            "num_segments": len(segments),
            "boundary_times": [seg["start"] for seg in segments] + [segments[-1]["end"]],
            "algorithm": algorithm,
            "duration": round(duration, 2),
            "processing_time": round(processing_time, 3),
            "metadata": {
                "filename": audio_path.name,
                "filepath": str(audio_path.absolute()),
                "analyzer": "structure_analyzer",
                "version": self.version,
                "model": f"MSAF-{algorithm}",
                "timestamp": datetime.now().isoformat(),
                "sample_rate": sr,
                "audio_duration": round(duration, 2)
            }
        }
        
        # Add similarity matrix if available
        if similarity_matrix is not None:
            results["similarity_matrix"] = similarity_matrix
        
        return results
    
    def _interpret_label(self, label: str, index: int) -> str:
        """
        Interpret MSAF label into meaningful section name.
        
        Args:
            label: MSAF label
            index: Segment index
            
        Returns:
            Interpreted label string
        """
        # MSAF labels are often just letter codes (A, B, C, etc.)
        # Try to map them to common song structures
        
        # Simple heuristic based on position
        if index == 0:
            return f"intro ({label})"
        elif index == len(label) - 1:
            return f"outro ({label})"
        else:
            # Try to identify repeated sections (verses/choruses)
            return f"section_{label}"
    
    def _calculate_similarity_matrix(self, labels: List[str]) -> List[List[float]]:
        """
        Calculate segment similarity matrix based on labels.
        
        Args:
            labels: List of segment labels
            
        Returns:
            NxN similarity matrix
        """
        n = len(labels)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                # 1.0 if same label, 0.0 otherwise
                matrix[i][j] = 1.0 if labels[i] == labels[j] else 0.0
        
        return matrix
    
    def _simple_segmentation(self, duration: float) -> tuple:
        """
        Create simple fallback segmentation.
        
        Args:
            duration: Audio duration in seconds
            
        Returns:
            Tuple of (boundaries, segments, similarity_matrix)
        """
        # Simple heuristic: divide into 4 equal segments
        num_segments = max(2, int(duration / 30))  # ~30 second segments
        segment_duration = duration / num_segments
        
        boundaries = [i * segment_duration for i in range(num_segments + 1)]
        
        segments = []
        for i in range(num_segments):
            start_time = boundaries[i]
            end_time = boundaries[i + 1]
            
            # Simple labeling
            if i == 0:
                label = "intro"
            elif i == num_segments - 1:
                label = "outro"
            else:
                label = f"section_{i}"
            
            segments.append({
                "start": round(start_time, 2),
                "end": round(end_time, 2),
                "duration": round(end_time - start_time, 2),
                "label": label,
                "index": i
            })
        
        # No similarity matrix for simple segmentation
        return boundaries, segments, None
    
    def analyze_hierarchical(
        self,
        audio_path: str,
        num_levels: int = 2
    ) -> Dict:
        """
        Perform hierarchical structure analysis.
        
        Detects structure at multiple time scales (e.g., sections vs phrases).
        
        Args:
            audio_path: Path to audio file
            num_levels: Number of hierarchical levels
            
        Returns:
            Dictionary with hierarchical structure results
        """
        start_time = time.time()
        audio_path = Path(audio_path)
        
        # Load audio
        y, sr = librosa.load(str(audio_path), sr=self.sr)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Run hierarchical analysis
        if not MSAF_AVAILABLE:
            print("Warning: MSAF not available, hierarchical analysis not supported")
            hierarchies = []
        else:
            try:
                hierarchies = []
                
                for level in range(num_levels):
                    # Use different sensitivity levels
                    boundaries, labels = msaf.process(
                        str(audio_path),
                        feature="mfcc"
                    )
                    
                    level_segments = []
                    for i in range(len(boundaries) - 1):
                        level_segments.append({
                            "start": round(float(boundaries[i]), 2),
                            "end": round(float(boundaries[i + 1]), 2),
                            "label": labels[i] if labels is not None else f"L{level}_seg{i}"
                        })
                    
                    hierarchies.append({
                        "level": level,
                        "segments": level_segments,
                        "num_segments": len(level_segments)
                    })
            
            except Exception as e:
                print(f"Warning: Hierarchical analysis failed ({e})")
                hierarchies = []
        
        processing_time = time.time() - start_time
        
        results = {
            "hierarchies": hierarchies,
            "num_levels": len(hierarchies),
            "duration": round(duration, 2),
            "processing_time": round(processing_time, 3),
            "metadata": {
                "filename": audio_path.name,
                "analyzer": "structure_analyzer",
                "mode": "hierarchical"
            }
        }
        
        return results


def analyze_structure(audio_path: str, **kwargs) -> Dict:
    """
    Convenience function for structure analysis.
    
    Args:
        audio_path: Path to audio file
        **kwargs: Additional arguments for StructureAnalyzer
        
    Returns:
        Structure analysis results
    """
    analyzer = StructureAnalyzer(**kwargs)
    return analyzer.analyze(audio_path)

