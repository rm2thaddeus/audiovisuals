"""
CPPN Frame Renderer - GPU-accelerated batch processing

Renders video frames by evaluating CPPN across all pixels for each audio frame.
Optimized for RTX 5070 with memory management and progress tracking.

Usage:
    renderer = Renderer(cppn, resolution=(1280, 720))
    for frame in renderer.render_sequence(audio_features, fps=30):
        ...
"""

import numpy as np
import torch
from tqdm import tqdm
from typing import Iterator, List, Tuple, Optional


class Renderer:
    """GPU-accelerated frame renderer for CPPN visualizations."""
    
    def __init__(
        self,
        cppn,
        resolution: Tuple[int, int] = (1280, 720),
        batch_size: int = None
    ):
        """
        Initialize renderer.
        
        Args:
            cppn: CPPN network instance
            resolution: (width, height) in pixels
            batch_size: Number of pixels to process per batch
        """
        self.cppn = cppn
        self.width, self.height = resolution
        self.total_pixels = self.width * self.height
        self.device = cppn.device
        self.torch_device = torch.device(self.device if self.device == 'cuda' else 'cpu')
        self.cppn_dtype = next(cppn.parameters()).dtype
        self.input_dtype = torch.float16 if self.device == 'cuda' and self.cppn_dtype == torch.float16 else torch.float32
        
        # Optimize batch size for GPU memory - MAXIMUM utilization
        if batch_size is None:
            if self.device == 'cuda':
                # Use MAXIMUM batches for RTX 5070 - aim for ~95% of VRAM
                gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                if gpu_memory_gb >= 7.5:  # RTX 5070 (7.96 GB)
                    # Use optimal batch size: 5M pixels for 8x256 CPPN
                    self.batch_size = min(self.total_pixels, 5_000_000)  # 5M pixels per batch
                else:
                    self.batch_size = min(1_000_000, self.total_pixels)   # Smaller GPU: 1M
            else:
                self.batch_size = 100000  # CPU fallback - larger batches
        else:
            self.batch_size = batch_size
        
        # DISABLE parallel processing - causes CUDA deadlocks
        self.max_workers = 1  # Sequential processing only
        self.frame_batch_size = 1  # Process 1 frame at a time
        
        # Pre-generate coordinate grid ONCE and keep on device
        self._prepare_coordinates()
        
        # Preallocate reusable batch buffer to avoid per-frame allocations
        buffer_len = min(self.batch_size, self.total_pixels)
        self._batch_input = torch.empty(
            (buffer_len, self.cppn.input_dim),
            dtype=self.input_dtype,
            device=self.torch_device
        )
        
        print(f"Renderer initialized:")
        print(f"  Resolution: {self.width}x{self.height} ({self.total_pixels:,} pixels)")
        print(f"  Batch size: {self.batch_size:,} pixels")
        print(f"  Device: {self.device}")
        print(f"  Total batches: {(self.total_pixels + self.batch_size - 1) // self.batch_size}")
    
    def _prepare_coordinates(self):
        """Pre-generate normalized pixel coordinates and keep on device."""
        # Use reduced coordinate range to balance with time/audio features
        coord_scale = 0.5
        x_coords = np.linspace(-coord_scale, coord_scale, self.width, dtype=np.float32)
        y_coords = np.linspace(-coord_scale, coord_scale, self.height, dtype=np.float32)
        
        xx, yy = np.meshgrid(x_coords, y_coords)
        
        x_flat = torch.from_numpy(xx.flatten()).to(self.torch_device)
        y_flat = torch.from_numpy(yy.flatten()).to(self.torch_device)
        
        self.x_flat = x_flat
        self.y_flat = y_flat
        
        print(f"  Coordinate grid prepared: {len(x_flat):,} points on {self.device}")
    
    def render_frame(
        self,
        time: float,
        audio_features: np.ndarray,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Render a single frame.
        
        Args:
            time: Current time (0 to 1)
            audio_features: Audio feature vector (9D for baseline)
            show_progress: Show progress bar for this frame
        
        Returns:
            RGB image (height, width, 3) as numpy uint8
        """
        # Prepare output buffer
        rgb_output = np.zeros((self.total_pixels, 3), dtype=np.float32)
        
        # Calculate number of batches
        num_batches = (self.total_pixels + self.batch_size - 1) // self.batch_size
        
        # Process in batches
        self.cppn.eval()
        
        iterator = range(num_batches)
        if show_progress:
            iterator = tqdm(iterator, desc="Rendering frame", leave=False)
        
        # Convert audio features to tensor once
        audio_tensor = torch.from_numpy(audio_features).to(
            self.torch_device,
            dtype=self.input_dtype
        )
        feature_dim = audio_tensor.shape[0]
        
        with torch.no_grad():
            for i in iterator:
                start_idx = i * self.batch_size
                end_idx = min((i + 1) * self.batch_size, self.total_pixels)
                batch_len = end_idx - start_idx
                
                batch_input = self._batch_input[:batch_len]
                
                # Fill batch input in-place to avoid reallocation
                batch_input[:, 0].copy_(self.x_flat[start_idx:end_idx])
                batch_input[:, 1].copy_(self.y_flat[start_idx:end_idx])
                # Amplify time: map [0,1] to [-1,1] to match coordinate scale
                batch_input[:, 2].fill_(time * 2.0 - 1.0)
                # Amplify audio features by 3x for balance (was 10x - too aggressive)
                batch_input[:, 3:3 + feature_dim].copy_(
                    audio_tensor.unsqueeze(0).expand(batch_len, -1) * 3.0
                )
                
                batch_output = self.cppn(batch_input)
                
                # Store output (convert FP16 to FP32 for final image)
                batch_output = batch_output.to(dtype=torch.float32).cpu().numpy()
                rgb_output[start_idx:end_idx] = batch_output
        
        # Reshape to image
        rgb_image = rgb_output.reshape(self.height, self.width, 3)
        
        # Convert to uint8
        rgb_image = (rgb_image * 255).astype(np.uint8)
        
        return rgb_image
    
    def _render_frame_batch(self, frame_indices: List[int], features: np.ndarray, 
                           evolve_rate: float = 0.0) -> List[Tuple[int, np.ndarray]]:
        """Render a batch of frames in parallel."""
        frames = []
        
        for frame_idx in frame_indices:
            # Get audio features for this frame
            audio_features = features[frame_idx]
            
            # Calculate normalized time
            time = frame_idx / max(1, len(features) - 1)
            
            # Render frame
            frame = self.render_frame(time, audio_features, show_progress=False)
            frames.append((frame_idx, frame))
            
            # Optional: Evolve CPPN weights for "living math" effect
            if evolve_rate > 0 and frame_idx % 10 == 0:
                self.cppn.evolve_weights(mutation_rate=evolve_rate)
        
        return frames
    
    def render_sequence(
        self,
        audio_analysis: dict,
        fps: int = 30,
        evolve_rate: float = 0.0,
        clear_cache_every: int = 100
    ) -> Iterator[np.ndarray]:
        """
        Render sequence of frames from audio analysis.
        
        Args:
            audio_analysis: Dictionary from AudioAnalyzer.analyze()
            fps: Frames per second
            evolve_rate: CPPN weight evolution rate (0 = no evolution)
            clear_cache_every: Clear CUDA cache every N frames
        
        Returns:
            List of RGB frames (numpy uint8 arrays)
        """
        features = audio_analysis['features']
        duration = audio_analysis['duration']
        num_frames = audio_analysis['num_frames']
        
        print(f"\nRendering sequence (SEQUENTIAL):")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Total frames: {num_frames}")
        print(f"  Target FPS: {fps}")
        
        frame_stats = []  # Track RGB statistics
        rendered_count = 0
        
        # Process frames sequentially with progress bar
        for frame_idx in tqdm(range(num_frames), desc="Rendering frames"):
            # Get audio features for this frame
            audio_features = features[frame_idx]
            
            # Calculate normalized time
            time_val = frame_idx / max(1, num_frames - 1)
            
            # Render frame
            frame = self.render_frame(time_val, audio_features, show_progress=False)
            
            # Track statistics for diagnostic logging
            if frame_idx % max(1, num_frames // 10) == 0 or frame_idx < 3:
                frame_std = frame.std()
                frame_stats.append({
                    'idx': frame_idx,
                    'mean': float(frame.mean()),
                    'std': float(frame_std),
                    'r_mean': float(frame[:, :, 0].mean()),
                    'g_mean': float(frame[:, :, 1].mean()),
                    'b_mean': float(frame[:, :, 2].mean()),
                })
            
            # Optional: Evolve CPPN weights for "living math" effect
            if evolve_rate > 0 and frame_idx % 10 == 0:
                self.cppn.evolve_weights(mutation_rate=evolve_rate)
            
            # Clear CUDA cache periodically
            if self.device == 'cuda' and frame_idx > 0 and frame_idx % clear_cache_every == 0:
                torch.cuda.empty_cache()
            
            rendered_count += 1
            yield frame
        
        # Log RGB statistics
        print(f"\n[OK] Rendered {rendered_count} frames")
        
        if frame_stats:
            avg_std = np.mean([s['std'] for s in frame_stats])
            print(f"\nFrame variation analysis:")
            print(f"  Average std dev: {avg_std:.1f}")
            
            if avg_std < 1.0:
                print(f"  [!] WARNING: Very low variation - frames are nearly uniform!")
                print(f"      This will produce flat-color outputs.")
                print(f"      Try: --audio-scale 0.1 to reduce audio feature dominance")
            elif avg_std < 10.0:
                print(f"  [!] WARNING: Low variation - limited spatial patterns")
                print(f"      Try: --audio-scale 0.2 for more spatial detail")
            else:
                print(f"  [OK] Good variation - frames have spatial patterns")
            
            # Sample frame stats
            print(f"\nSample frames:")
            for stat in frame_stats[:3]:
                print(f"  Frame {stat['idx']}: mean={stat['mean']:.1f}, std={stat['std']:.1f}, " +
                      f"RGB=({stat['r_mean']:.0f}, {stat['g_mean']:.0f}, {stat['b_mean']:.0f})")
    
    def estimate_memory_usage(self) -> dict:
        """Estimate GPU/RAM memory requirements."""
        pixels_per_batch = self.batch_size
        dtype_bytes = torch.finfo(self.input_dtype).bits // 8
        bytes_per_pixel_input = self.cppn.input_dim * dtype_bytes
        bytes_per_pixel_output = 3 * 4  # RGB float32
        
        batch_memory_mb = (pixels_per_batch * (bytes_per_pixel_input + bytes_per_pixel_output)) / (1024 ** 2)
        
        # Model parameters
        model_params = self.cppn.count_parameters()
        model_memory_mb = (model_params * 4) / (1024 ** 2)
        
        # Frame memory
        frame_memory_mb = (self.total_pixels * 3) / (1024 ** 2)  # uint8 RGB
        
        return {
            'batch_memory_mb': batch_memory_mb,
            'model_memory_mb': model_memory_mb,
            'frame_memory_mb': frame_memory_mb,
            'total_per_frame_mb': batch_memory_mb + model_memory_mb
        }


if __name__ == '__main__':
    # Test renderer
    from cppn import CPPN
    
    print("Testing Renderer...")
    
    # Create CPPN
    cppn = CPPN(input_dim=12, hidden_dim=256, num_layers=10)
    
    # Create renderer
    renderer = Renderer(cppn, resolution=(640, 360), batch_size=5000)
    
    # Estimate memory
    memory = renderer.estimate_memory_usage()
    print(f"\nMemory estimates:")
    for key, value in memory.items():
        print(f"  {key}: {value:.2f} MB")
    
    # Test single frame render
    print("\nRendering test frame...")
    audio_features = np.random.randn(9)
    
    frame = renderer.render_frame(
        time=0.5,
        audio_features=audio_features,
        show_progress=True
    )
    
    print(f"\n[OK] Frame rendered:")
    print(f"  Shape: {frame.shape}")
    print(f"  Dtype: {frame.dtype}")
    print(f"  Memory: {frame.nbytes / (1024**2):.2f} MB")
    
    # Test sequence rendering (small)
    print("\nRendering test sequence...")
    mock_analysis = {
        'features': np.random.randn(10, 9),  # 10 frames
        'duration': 0.33,
        'num_frames': 10
    }
    
    frames = list(renderer.render_sequence(mock_analysis, fps=30))
    
    print(f"\n[OK] Sequence rendered:")
    print(f"  Frames: {len(frames)}")
    print(f"  Total memory: {sum(f.nbytes for f in frames) / (1024**2):.2f} MB")
    
    print("\n[OK] Renderer test complete!")
