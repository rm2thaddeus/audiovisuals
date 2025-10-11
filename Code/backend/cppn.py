"""
CPPN (Compositional Pattern-Producing Network) - Neural Field for Audio Visualization

A neural network that maps (x, y, time, audio_features) → (R, G, B) to create
living, evolving visual organisms that respond to audio.

Key features:
- Bio-inspired activations: sine, cosine, gaussian, tanh
- CUDA acceleration with CPU fallback
- Weight evolution for "living math" effect

Usage:
    cppn = CPPN(input_dim=12, hidden_dim=256, num_layers=10)
    rgb = cppn(coordinates, audio_features)
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, List


class CPPN(nn.Module):
    """Compositional Pattern-Producing Network for audio-reactive visuals."""
    
    def __init__(
        self,
        input_dim: int = 12,  # x, y, time + 9 audio features
        hidden_dim: int = 256,
        num_layers: int = 10,
        output_dim: int = 3,  # RGB
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
        use_fp16: bool = True  # Disable for CLIP optimization (needs stable gradients)
    ):
        """
        Initialize CPPN.
        
        Args:
            input_dim: Number of input features (coordinates + audio)
            hidden_dim: Hidden layer dimension
            num_layers: Number of hidden layers
            output_dim: Output dimension (3 for RGB)
            device: 'cuda' or 'cpu'
        """
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.output_dim = output_dim
        self.device = device
        self.use_fp16 = use_fp16
        
        # Build network layers
        self.layers = nn.ModuleList()
        
        # Input layer
        self.layers.append(nn.Linear(input_dim, hidden_dim))
        
        # Hidden layers
        for _ in range(num_layers - 1):
            self.layers.append(nn.Linear(hidden_dim, hidden_dim))
        
        # Output layer
        self.output_layer = nn.Linear(hidden_dim, output_dim)
        
        # Initialize weights for interesting patterns
        self._initialize_weights()
        
        # Move to device (with fallback check)
        try:
            self.to(device)
            # Test CUDA with a dummy operation
            if device == 'cuda':
                test_tensor = torch.randn(1, 1).to(device)
                _ = torch.sin(test_tensor)
                print(f"CPPN initialized on {device}")
        except RuntimeError as e:
            if 'CUDA' in str(e) and device == 'cuda':
                print(f"WARNING: CUDA error detected")
                print(f"  Error: {e}")
                print("  Falling back to CPU...")
                self.device = 'cpu'
                self.to('cpu')
                device = 'cpu'
            else:
                raise
        
        # Enable FP16 for GPU acceleration (if requested)
        if self.device == 'cuda' and self.use_fp16:
            self.half()  # Convert to FP16
            print(f"  FP16 precision enabled for GPU acceleration")
        elif self.device == 'cuda':
            print(f"  FP32 precision (FP16 disabled for stable gradients)")
        
        print(f"CPPN running on: {self.device}")
        print(f"  Layers: {num_layers}, Hidden dim: {hidden_dim}")
        print(f"  Total parameters: {self.count_parameters():,}")
    
    def _initialize_weights(self):
        """Initialize weights with larger gain to prevent signal vanishing."""
        # Use gain=5.0 to maintain signal strength through sine/cos/tanh activations
        for layer in self.layers:
            nn.init.xavier_uniform_(layer.weight, gain=5.0)
            nn.init.zeros_(layer.bias)
        
        nn.init.xavier_uniform_(self.output_layer.weight, gain=1.0)
        nn.init.zeros_(self.output_layer.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through CPPN.
        
        Args:
            x: Input tensor (batch_size, input_dim)
               Expected: [x_coord, y_coord, time, audio_features...]
        
        Returns:
            RGB output (batch_size, 3) in range [0, 1]
        """
        # Apply mixed activations through hidden layers
        for i, layer in enumerate(self.layers):
            x = layer(x)
            
            # Alternate between different activation functions
            # This creates complex, bio-inspired patterns
            if i % 4 == 0:
                x = torch.sin(x)  # Sine wave patterns
            elif i % 4 == 1:
                x = torch.cos(x)  # Cosine wave patterns
            elif i % 4 == 2:
                x = self._gaussian(x)  # Gaussian blobs
            else:
                x = torch.tanh(x)  # Smooth transitions
        
        # Output layer with sigmoid for RGB [0, 1]
        x = self.output_layer(x)
        x = torch.sigmoid(x)
        
        return x
    
    def _gaussian(self, x: torch.Tensor) -> torch.Tensor:
        """Gaussian activation function."""
        return torch.exp(-x**2)
    
    def count_parameters(self) -> int:
        """Count total trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def evolve_weights(self, mutation_rate: float = 0.01):
        """
        Evolve network weights for "living math" effect.
        
        Args:
            mutation_rate: Amount of random mutation to apply
        """
        with torch.no_grad():
            for param in self.parameters():
                noise = torch.randn_like(param) * mutation_rate
                param.add_(noise)
    
    def render_frame(
        self,
        width: int,
        height: int,
        time: float,
        audio_features: np.ndarray,
        batch_size: int = 10000
    ) -> np.ndarray:
        """
        Render a single frame.
        
        Args:
            width: Frame width in pixels
            height: Frame height in pixels
            time: Current time (0 to 1)
            audio_features: Audio features vector (9D for baseline)
            batch_size: Number of pixels to process at once
        
        Returns:
            RGB image (height, width, 3) as numpy array uint8
        """
        # Generate pixel coordinates with reduced magnitude to balance with time/audio
        # Scale coordinates to [-0.5, 0.5] instead of [-1, 1] to equalize influence
        coord_scale = 0.5
        x_coords = np.linspace(-coord_scale, coord_scale, width)
        y_coords = np.linspace(-coord_scale, coord_scale, height)
        
        xx, yy = np.meshgrid(x_coords, y_coords)
        
        # Flatten coordinates
        x_flat = xx.flatten()
        y_flat = yy.flatten()
        
        total_pixels = len(x_flat)
        
        # Prepare output
        rgb_output = np.zeros((total_pixels, 3), dtype=np.float32)
        
        # Process in batches for memory efficiency
        num_batches = (total_pixels + batch_size - 1) // batch_size
        
        self.eval()
        with torch.no_grad():
            for i in range(num_batches):
                start_idx = i * batch_size
                end_idx = min((i + 1) * batch_size, total_pixels)
                batch_len = end_idx - start_idx
                
                # Prepare batch input
                batch_x = x_flat[start_idx:end_idx]
                batch_y = y_flat[start_idx:end_idx]
                
                # Create input tensor: [x, y, time, audio_features...]
                batch_input = np.zeros((batch_len, self.input_dim), dtype=np.float32)
                batch_input[:, 0] = batch_x
                batch_input[:, 1] = batch_y
                batch_input[:, 2] = time
                
                # Add audio features (broadcast to all pixels)
                batch_input[:, 3:3+len(audio_features)] = audio_features
                
                # Convert to torch tensor
                batch_tensor = torch.from_numpy(batch_input).to(self.device)
                
                # Forward pass
                batch_output = self(batch_tensor)
                
                # Store output
                rgb_output[start_idx:end_idx] = batch_output.cpu().numpy()
        
        # Reshape to image
        rgb_image = rgb_output.reshape(height, width, 3)
        
        # Convert to uint8 [0, 255]
        rgb_image = (rgb_image * 255).astype(np.uint8)
        
        return rgb_image


if __name__ == '__main__':
    # Test CPPN
    print("Testing CPPN...")
    
    # Create CPPN
    cppn = CPPN(
        input_dim=12,  # x, y, time + 9 audio features
        hidden_dim=256,
        num_layers=10
    )
    
    # Test forward pass
    batch_size = 1000
    test_input = torch.randn(batch_size, 12).to(cppn.device)
    
    output = cppn(test_input)
    
    print(f"\nTest output:")
    print(f"  Shape: {output.shape}")
    print(f"  Range: [{output.min().item():.3f}, {output.max().item():.3f}]")
    print(f"  Mean: {output.mean().item():.3f}")
    
    # Test frame rendering
    print("\nRendering test frame...")
    audio_features = np.random.randn(9)  # Random audio features
    
    frame = cppn.render_frame(
        width=128,
        height=128,
        time=0.5,
        audio_features=audio_features,
        batch_size=5000
    )
    
    print(f"Frame rendered:")
    print(f"  Shape: {frame.shape}")
    print(f"  Dtype: {frame.dtype}")
    print(f"  Range: [{frame.min()}, {frame.max()}]")
    
    # Test weight evolution
    print("\nTesting weight evolution...")
    original_params = sum(p.sum().item() for p in cppn.parameters())
    cppn.evolve_weights(mutation_rate=0.01)
    evolved_params = sum(p.sum().item() for p in cppn.parameters())
    
    print(f"  Parameter sum before: {original_params:.3f}")
    print(f"  Parameter sum after: {evolved_params:.3f}")
    print(f"  Changed: {abs(evolved_params - original_params) > 0}")
    
    print("\n[OK] CPPN test complete!")

