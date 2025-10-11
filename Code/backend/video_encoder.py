"""
Video Encoder - MP4 generation with audio sync

Encodes rendered frames into MP4 video with original audio track.
Supports optional PNG frame export for quality inspection.

Usage:
    encoder = VideoEncoder(output_path='output.mp4', fps=30)
    encoder.encode(frames, audio_path='input.mp3')
"""

import itertools
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import cv2
import numpy as np
from tqdm import tqdm


class VideoEncoder:
    """Encode frames to MP4 video with audio."""
    
    def __init__(
        self,
        output_path: str,
        fps: int = 30,
        codec: str = 'mp4v',  # or 'avc1' for H.264
        quality: int = 90
    ):
        """
        Initialize encoder.
        
        Args:
            output_path: Output video file path
            fps: Frames per second
            codec: Video codec ('mp4v' or 'avc1')
            quality: Video quality (0-100, higher is better)
        """
        self.output_path = Path(output_path)
        self.fps = fps
        self.codec = codec
        self.quality = quality
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"VideoEncoder initialized:")
        print(f"  Output: {self.output_path}")
        print(f"  FPS: {self.fps}")
        print(f"  Codec: {self.codec}")
    
    def encode(
        self,
        frames: Iterable[np.ndarray],
        audio_path: Optional[str] = None,
        export_frames: bool = False,
        frames_dir: Optional[str] = None,
        num_frames: Optional[int] = None
    ) -> Path:
        """
        Encode frames to video.
        
        Args:
            frames: Iterable of RGB frames (uint8 numpy arrays)
            audio_path: Path to original audio file (for muxing)
            export_frames: If True, save individual PNG frames
            frames_dir: Directory for PNG frames (if export_frames=True)
            num_frames: Optional count for progress display
        
        Returns:
            Path to generated video file
        """
        frame_iter = iter(frames)
        try:
            first_frame = next(frame_iter)
        except StopIteration:
            raise ValueError("No frames to encode")
        
        print(f"\nEncoding video...")
        print(f"  Target frames: {num_frames if num_frames is not None else 'unknown'}")
        print(f"  Resolution: {first_frame.shape[1]}x{first_frame.shape[0]}")
        
        frames_dir_path = None
        if export_frames:
            frames_dir_path = self._prepare_frames_dir(frames_dir)
        
        # Create temporary video without audio
        temp_video, frame_count = self._encode_frames_stream(
            itertools.chain([first_frame], frame_iter),
            frames_dir_path=frames_dir_path,
            num_frames=num_frames
        )
        
        # Mux audio if provided
        if audio_path:
            final_video = self._mux_audio(temp_video, audio_path)
            if temp_video.exists():
                temp_video.unlink()  # Clean up temp file
        else:
            final_video = temp_video
        
        print(f"[OK] Video saved: {final_video}")
        print(f"  Frames encoded: {frame_count}")
        print(f"  Size: {final_video.stat().st_size / (1024**2):.2f} MB")
        
        return final_video
    
    def _encode_frames_stream(
        self,
        frames: Iterable[np.ndarray],
        frames_dir_path: Optional[Path],
        num_frames: Optional[int] = None
    ) -> Tuple[Path, int]:
        """Encode frames to video file from an iterable."""
        frames_iter = iter(frames)
        try:
            first_frame = next(frames_iter)
        except StopIteration:
            raise ValueError("No frames to encode")
        
        # Get frame dimensions
        height, width = first_frame.shape[:2]
        
        # Create temp file for video without audio
        temp_path = self.output_path.with_suffix('.temp.mp4')
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        writer = cv2.VideoWriter(
            str(temp_path),
            fourcc,
            self.fps,
            (width, height)
        )
        
        if not writer.isOpened():
            raise RuntimeError(f"Failed to open video writer for {temp_path}")
        
        frame_count = 0
        progress = tqdm(total=num_frames, desc="Encoding frames")
        
        try:
            # Write first frame
            self._write_frame(writer, first_frame, frame_count, frames_dir_path)
            frame_count += 1
            progress.update(1)
            
            for frame in frames_iter:
                self._write_frame(writer, frame, frame_count, frames_dir_path)
                frame_count += 1
                progress.update(1)
        finally:
            progress.close()
            writer.release()
        
        return temp_path, frame_count
    
    def _write_frame(
        self,
        writer: cv2.VideoWriter,
        frame: np.ndarray,
        index: int,
        frames_dir_path: Optional[Path]
    ):
        """Write single frame to video (and optionally export as PNG)."""
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)
        
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        writer.write(frame_bgr)
        
        if frames_dir_path is not None:
            frame_path = frames_dir_path / f"frame_{index:05d}.png"
            cv2.imwrite(str(frame_path), frame_bgr)
    
    def _prepare_frames_dir(self, frames_dir: Optional[str]) -> Path:
        """Ensure the frames directory exists and return it."""
        if frames_dir is None:
            frames_dir_path = self.output_path.parent / f"{self.output_path.stem}_frames"
        else:
            frames_dir_path = Path(frames_dir)
        
        frames_dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Exporting frames to: {frames_dir_path}")
        
        return frames_dir_path
    
        return temp_path
    
    def _mux_audio(self, video_path: Path, audio_path: str) -> Path:
        """Mux audio with video using ffmpeg."""
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            print(f"Warning: Audio file not found: {audio_path}")
            print("Proceeding without audio...")
            shutil.move(str(video_path), str(self.output_path))
            return self.output_path
        
        print("Muxing audio with video...")
        
        # Check if ffmpeg is available
        if not self._check_ffmpeg():
            print("Warning: ffmpeg not found. Proceeding without audio...")
            shutil.move(str(video_path), str(self.output_path))
            return self.output_path
        
        # Use ffmpeg to combine video and audio
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-i', str(video_path),
            '-i', str(audio_path),
            '-c:v', 'copy',  # Copy video codec
            '-c:a', 'aac',   # Encode audio to AAC
            '-shortest',     # Match shortest stream
            str(self.output_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print("[OK] Audio muxed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Warning: ffmpeg muxing failed: {e}")
            print("Proceeding without audio...")
            shutil.move(str(video_path), str(self.output_path))
        
        return self.output_path
    
    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available."""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _export_frames(
        self,
        frames: List[np.ndarray],
        frames_dir: Optional[str] = None
    ):
        """Export frames as PNG files."""
        if frames_dir is None:
            frames_dir = self.output_path.parent / f"{self.output_path.stem}_frames"
        else:
            frames_dir = Path(frames_dir)
        
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Exporting frames to: {frames_dir}")
        
        for i, frame in enumerate(tqdm(frames, desc="Exporting frames")):
            frame_path = frames_dir / f"frame_{i:05d}.png"
            
            # OpenCV expects BGR
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(frame_path), frame_bgr)
        
        print(f"[OK] Exported {len(frames)} frames to {frames_dir}")


if __name__ == '__main__':
    # Test video encoder
    print("Testing VideoEncoder...")
    
    # Create test frames (gradient pattern)
    width, height = 640, 360
    num_frames = 30  # 1 second at 30 FPS
    
    frames = []
    for i in range(num_frames):
        # Create gradient that changes over time
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Color gradient based on frame
        r = int(255 * (i / num_frames))
        g = int(255 * (1 - i / num_frames))
        b = 128
        
        # Create gradient
        for y in range(height):
            frame[y, :, 0] = r * (y / height)  # Red channel
            frame[y, :, 1] = g  # Green channel
            frame[y, :, 2] = b * (1 - y / height)  # Blue channel
        
        frames.append(frame)
    
    print(f"Generated {len(frames)} test frames")
    
    # Test encoding
    encoder = VideoEncoder('test_output.mp4', fps=30)
    
    output_path = encoder.encode(
        frames,
        audio_path=None,  # No audio for test
        export_frames=False
    )
    
    print(f"\n[OK] VideoEncoder test complete!")
    print(f"  Output: {output_path}")
    
    # Clean up
    if output_path.exists():
        print(f"  Test file created successfully")
        # output_path.unlink()  # Uncomment to delete test file

