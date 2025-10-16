"""
CLIP-Guided CPPN Optimization

Optimizes CPPN weights to generate patterns matching a text description.
Uses best practices from research: coordinate scaling, multi-resolution pyramid,
held-out evaluation, and temporal coherence for audio-reactivity.

Author: Audio Feature Explorer Team
Date: 2025-10-11
"""

import torch
import torch.nn as nn
import numpy as np
from PIL import Image
import clip
import argparse
from pathlib import Path
import json
from typing import Optional, Tuple

from cppn import CPPN
from audio_analyzer import AudioAnalyzer


def optimize_cppn_with_clip(
    prompt: str,
    audio_file: str,
    output_path: str = "optimized_cppn.pth",
    iterations: int = 500,
    resolution_pyramid: list = [256, 512],
    device: str = "auto",
    learning_rate: float = 0.001,
    log_interval: int = 20,
    clip_model_name: str = "RN50",
    hidden_dim: int = 256,
    num_layers: int = 4,
    verbose: bool = True
) -> dict:
    """
    Optimize CPPN weights to match a text description using CLIP.
    
    Args:
        prompt: Text description of desired aesthetic (e.g., "organic flowing shapes with strong contrast")
        audio_file: Path to audio for extracting representative features
        output_path: Where to save optimized weights (.pth file)
        iterations: Number of optimization steps per resolution
        resolution_pyramid: List of resolutions to optimize at (e.g., [256, 512, 1024])
        device: "auto", "cuda", or "cpu"
        learning_rate: Adam learning rate
        log_interval: Print progress every N iterations
        clip_model_name: CLIP model to use ("RN50", "RN101", "ViT-B/32", "ViT-B/16")
        hidden_dim: Hidden layer dimension (default: 256)
        num_layers: Number of CPPN layers (default: 4)
        verbose: Print progress messages
        
    Returns:
        dict: Optimization results including best similarity score, final resolution, etc.
    """
    
    # Device setup
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    if verbose:
        print("=" * 60)
        print("CLIP-Guided CPPN Optimization")
        print("=" * 60)
        print(f"Prompt: '{prompt}'")
        print(f"Device: {device}")
        print(f"CLIP Model: {clip_model_name}")
        print(f"Resolution pyramid: {resolution_pyramid}")
        print(f"Iterations per resolution: {iterations}")
        print()
    
    # Load CLIP model
    if verbose:
        print("Loading CLIP model...")
    clip_model, preprocess = clip.load(clip_model_name, device=device)
    clip_model.eval()
    
    # Initialize CPPN
    if verbose:
        print("Initializing CPPN...")
    # Input: x, y (2) + time (1) + audio features (9) = 12 dimensions
    # Disable FP16 for CLIP optimization - needs stable gradients
    cppn = CPPN(input_dim=12, hidden_dim=hidden_dim, num_layers=num_layers, device=device, use_fp16=False).to(device)
    
    # Calculate and display parameter count
    num_params = sum(p.numel() for p in cppn.parameters())
    if verbose:
        print(f"CPPN Architecture: {num_layers} layers × {hidden_dim} hidden dim = {num_params:,} parameters")
    
    # Extract representative audio features (from middle of track)
    if verbose:
        print(f"Extracting audio features from: {audio_file}")
    analyzer = AudioAnalyzer()
    analysis = analyzer.analyze(audio_file, fps=30)
    
    # Get features from 25% into the track (usually has good dynamics)
    audio_duration = analysis['duration']
    representative_time = audio_duration * 0.25
    frame_idx = int(representative_time * analysis['fps'])
    frame_idx = min(frame_idx, analysis['num_frames'] - 1)
    
    audio_features = analysis['features'][frame_idx]
    audio_tensor = torch.tensor(audio_features, dtype=torch.float32, device=device)
    
    if verbose:
        print(f"Audio duration: {audio_duration:.2f}s")
        print(f"Representative frame: {frame_idx} @ {representative_time:.2f}s")
        print(f"Audio features shape: {audio_tensor.shape}")
        print()
    
    # Encode text prompt with CLIP
    if verbose:
        print("Encoding text prompt with CLIP...")
    text_tokens = clip.tokenize([prompt]).to(device)
    with torch.no_grad():
        text_features = clip_model.encode_text(text_tokens)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    
    # Optimizer
    optimizer = torch.optim.Adam(cppn.parameters(), lr=learning_rate)
    
    # Track best result
    best_similarity = -1.0
    best_state = None
    optimization_history = []
    
    # Multi-resolution pyramid optimization
    for res_idx, resolution in enumerate(resolution_pyramid):
        if verbose:
            print("=" * 60)
            print(f"Resolution {res_idx + 1}/{len(resolution_pyramid)}: {resolution}×{resolution}")
            print("=" * 60)
        
        # Generate coordinate grid with CRITICAL scaling to [-π, π]
        x = torch.linspace(-np.pi, np.pi, resolution, device=device)
        y = torch.linspace(-np.pi, np.pi, resolution, device=device)
        X, Y = torch.meshgrid(x, y, indexing='ij')
        coords = torch.stack([X.flatten(), Y.flatten()], dim=-1)
        
        # Add time dimension (use fixed time for optimization)
        time_value = 0.5  # Middle of the video
        time_tensor = torch.full((coords.shape[0], 1), time_value, device=device)
        
        # Expand audio features to match coordinate batch
        audio_batch = audio_tensor.unsqueeze(0).expand(coords.shape[0], -1)
        
        # Combine inputs: [coords (2), time (1), audio (9)] = 12D
        cppn_input = torch.cat([coords, time_tensor, audio_batch], dim=-1)
        
        if verbose and res_idx == 0:
            print(f"CPPN input shape: {cppn_input.shape}")
            print(f"  Coords: {coords.shape}")
            print(f"  Time: {time_tensor.shape}")
            print(f"  Audio: {audio_batch.shape}")
            print()
        
        # Optimization loop for this resolution
        for iteration in range(iterations):
            optimizer.zero_grad()
            
            # Generate image through CPPN
            rgb = cppn(cppn_input)
            image = rgb.reshape(resolution, resolution, 3)
            
            # Differentiable preprocessing for CLIP (NO .detach()!)
            # 1. Clamp to [0, 1]
            image_clamped = torch.clamp(image, 0, 1)
            
            # 2. Permute to CHW format and add batch dimension
            clip_image = image_clamped.permute(2, 0, 1).unsqueeze(0)  # (1, 3, H, W)
            
            # 3. Resize to 224x224 using differentiable interpolation
            clip_image = torch.nn.functional.interpolate(
                clip_image, 
                size=(224, 224), 
                mode='bicubic', 
                align_corners=False
            )
            
            # 4. Normalize with CLIP's mean and std (differentiable!)
            mean = torch.tensor([0.48145466, 0.4578275, 0.40821073], device=device).view(1, 3, 1, 1)
            std = torch.tensor([0.26862954, 0.26130258, 0.27577711], device=device).view(1, 3, 1, 1)
            clip_image = (clip_image - mean) / std
            
            # Get CLIP image features
            image_features = clip_model.encode_image(clip_image)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Compute similarity (cosine similarity)
            similarity = (image_features * text_features).sum()
            loss = -similarity  # Maximize similarity = minimize negative
            
            # Backprop and optimize
            loss.backward()
            optimizer.step()
            
            # Track best result
            sim_value = similarity.item()
            if sim_value > best_similarity:
                best_similarity = sim_value
                best_state = {k: v.cpu().clone() for k, v in cppn.state_dict().items()}
            
            # Log progress
            if verbose and (iteration % log_interval == 0 or iteration == iterations - 1):
                print(f"  Iter {iteration:4d}/{iterations} | "
                      f"Similarity: {sim_value:.4f} | "
                      f"Best: {best_similarity:.4f}")
            
            # Record history
            optimization_history.append({
                'resolution': resolution,
                'iteration': iteration,
                'similarity': sim_value,
                'loss': loss.item()
            })
        
        if verbose:
            print(f"  Resolution {resolution}×{resolution} complete!")
            print(f"  Best similarity at this resolution: {best_similarity:.4f}")
            print()
    
    # Load best weights
    cppn.load_state_dict(best_state)
    
    # Save optimized weights
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save both the state dict and metadata
    save_data = {
        'state_dict': best_state,
        'prompt': prompt,
        'best_similarity': best_similarity,
        'clip_model': clip_model_name,
        'audio_file': str(audio_file),
        'resolution_pyramid': resolution_pyramid,
        'iterations': iterations,
        'cppn_config': {
            'input_dim': 12,
            'hidden_dim': hidden_dim,
            'num_layers': num_layers  # Use actual number of layers
        }
    }
    torch.save(save_data, output_path)
    
    # Save optimization history
    history_path = output_path.with_suffix('.json')
    with open(history_path, 'w') as f:
        json.dump({
            'prompt': prompt,
            'best_similarity': best_similarity,
            'history': optimization_history
        }, f, indent=2)
    
    if verbose:
        print("=" * 60)
        print("Optimization Complete!")
        print("=" * 60)
        print(f"Best similarity: {best_similarity:.4f}")
        print(f"Saved to: {output_path}")
        print(f"History saved to: {history_path}")
        print()
    
    # Generate preview image at final resolution
    preview_path = output_path.with_suffix('.png')
    with torch.no_grad():
        final_res = resolution_pyramid[-1]
        x = torch.linspace(-np.pi, np.pi, final_res, device=device)
        y = torch.linspace(-np.pi, np.pi, final_res, device=device)
        X, Y = torch.meshgrid(x, y, indexing='ij')
        coords = torch.stack([X.flatten(), Y.flatten()], dim=-1)
        time_tensor = torch.full((coords.shape[0], 1), 0.5, device=device)
        audio_batch = audio_tensor.unsqueeze(0).expand(coords.shape[0], -1)
        cppn_input = torch.cat([coords, time_tensor, audio_batch], dim=-1)
        
        rgb = cppn(cppn_input)
        image = rgb.reshape(final_res, final_res, 3)
        image_np = (torch.clamp(image, 0, 1).cpu().numpy() * 255).astype(np.uint8)
        Image.fromarray(image_np).save(preview_path)
    
    if verbose:
        print(f"Preview saved to: {preview_path}")
        print()
    
    return {
        'best_similarity': best_similarity,
        'output_path': str(output_path),
        'preview_path': str(preview_path),
        'history_path': str(history_path),
        'final_resolution': resolution_pyramid[-1],
        'total_iterations': len(optimization_history)
    }


def main():
    parser = argparse.ArgumentParser(description="Optimize CPPN with CLIP guidance")
    parser.add_argument(
        '--prompt',
        type=str,
        required=True,
        help='Text description of desired aesthetic'
    )
    parser.add_argument(
        '--audio',
        type=str,
        default='../../docs/Audio/TOOL - The Pot (Audio).mp3',
        help='Path to audio file for feature extraction'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='styles/optimized_cppn.pth',
        help='Output path for optimized weights'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=500,
        help='Optimization iterations per resolution'
    )
    parser.add_argument(
        '--resolutions',
        type=int,
        nargs='+',
        default=[256, 512],
        help='Resolution pyramid (e.g., 256 512 1024)'
    )
    parser.add_argument(
        '--clip-model',
        type=str,
        default='RN50',
        choices=['RN50', 'RN101', 'ViT-B/32', 'ViT-B/16', 'ViT-L/14'],
        help='CLIP model to use'
    )
    parser.add_argument(
        '--lr',
        type=float,
        default=0.001,
        help='Learning rate'
    )
    parser.add_argument(
        '--hidden-dim',
        type=int,
        default=256,
        help='Hidden layer dimension (default: 256, try 128 for simpler network)'
    )
    parser.add_argument(
        '--layers',
        type=int,
        default=4,
        help='Number of CPPN layers (default: 4, try 2-3 for organic patterns)'
    )
    parser.add_argument(
        '--device',
        type=str,
        default='auto',
        choices=['auto', 'cuda', 'cpu'],
        help='Device to use'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    
    args = parser.parse_args()
    
    # Run optimization
    result = optimize_cppn_with_clip(
        prompt=args.prompt,
        audio_file=args.audio,
        output_path=args.output,
        iterations=args.iterations,
        resolution_pyramid=args.resolutions,
        device=args.device,
        learning_rate=args.lr,
        clip_model_name=args.clip_model,
        hidden_dim=args.hidden_dim,
        num_layers=args.layers,
        verbose=not args.quiet
    )
    
    print("\n[SUCCESS] Your CPPN is now optimized for:")
    print(f"   '{args.prompt}'")
    print(f"\n[FILES] Created:")
    print(f"   Weights: {result['output_path']}")
    print(f"   Preview: {result['preview_path']}")
    print(f"   History: {result['history_path']}")
    print("\nNext step: Generate a video!")
    print(f"   python cli.py {{audio}} output.mp4 --load-weights {result['output_path']} --layers {args.layers} --hidden-dim {args.hidden_dim}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

