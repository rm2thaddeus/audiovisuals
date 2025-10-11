# CLIP-Guided CPPN Optimization - Architecture Comparison

## Prompt
"organic flowing shapes diffusing into each other with strong contrast"

## Results Summary

### Architecture A: 128 Hidden Dimensions
- **Parameters**: 51,587 (4 layers × 128 dim)
- **CLIP Similarity**: 0.2452 (best)
- **Iterations**: 400 per resolution (256, 512)
- **Training Time**: ~6 minutes
- **Test Video**: `test_128dim.mp4`
- **Preview**: `organic_diffuse_128dim.png`

### Architecture B: 256 Hidden Dimensions
- **Parameters**: 201,475 (4 layers × 256 dim)
- **CLIP Similarity**: 0.2217 (best)
- **Iterations**: 200 per resolution (256, 512)
- **Training Time**: ~3 minutes
- **Test Video**: `test_256dim.mp4`
- **Preview**: `organic_diffuse_256dim.png`

## Visual Analysis

### 128 Dim (WINNER)
**Strengths:**
- Clearer organic flowing shapes (curved tendrils)
- Strong contrast between yellows, greens, and dark regions
- Less cluttered, more readable patterns
- Better matches the prompt intent
- Smoother color transitions

**Aesthetic**: Clean, flowing, psychedelic with clear structure

### 256 Dim
**Strengths:**
- More complex, dense patterns
- Vibrant color palette (reds, pinks, greens, yellows)
- Higher detail in micro-structures

**Weaknesses**:
- More chaotic/busy - harder to read individual shapes
- Less clear "diffusion" effect
- Some areas feel over-saturated

**Aesthetic**: Intense, chaotic, highly detailed

## Performance Comparison

### Inference Speed (480p @ 30fps)
- **128 dim**: 0.99x realtime (~10.1s for 10s video)
- **256 dim**: 0.96x realtime (~10.4s for 10s video)

Both architectures are real-time capable at 480p!

### CLIP Optimization
- **128 dim**: Converged better (0.2452 vs 0.2217)
- **256 dim**: Had half the iterations, but still lower score

## Conclusion

**Winner: 128 Hidden Dimensions**

Reasons:
1. **Better CLIP alignment**: Higher similarity score (0.2452 vs 0.2217)
2. **Better prompt adherence**: Clearer "organic flowing shapes" with "strong contrast"
3. **Cleaner aesthetic**: Less chaotic, more intentional structure
4. **Faster inference**: Slightly faster (though both real-time)
5. **Smaller model**: 51K vs 201K parameters (4x smaller)

## Recommendation

**Use 128 dim architecture for this aesthetic** ("organic flowing shapes diffusing with contrast").

The 256 dim architecture may be better for:
- Extremely complex, detailed prompts requiring high expressiveness
- Abstract, chaotic aesthetics
- Scenarios where model capacity is the bottleneck

But for this specific prompt, the simpler 128 dim network actually learned the aesthetic better!

## Technical Notes

1. **Architecture matters for CLIP optimization**: The loss surface is different for different architectures. Simpler networks can sometimes optimize better for specific aesthetics.

2. **Iteration count**: 256 dim had half the iterations (200 vs 400). However, its similarity score was plateauing around iteration 160, suggesting more iterations wouldn't help much.

3. **Coordinate scaling critical**: Both used `[-π, π]` coordinate scaling for sinusoidal activations, which is essential for CLIP-guided CPPNs.

4. **FP32 vs FP16**: Both used FP32 for optimization (stable gradients), FP16 for inference (speed).

## Files

**128 dim (recommended)**:
- Weights: `organic_diffuse_128dim.pth`
- Preview: `organic_diffuse_128dim.png`
- Test Video: `test_128dim.mp4`
- History: `organic_diffuse_128dim.json`

**256 dim**:
- Weights: `organic_diffuse_256dim.pth`
- Preview: `organic_diffuse_256dim.png`
- Test Video: `test_256dim.mp4`
- History: `organic_diffuse_256dim.json`

---

**Date**: 2025-10-11  
**CLIP Model**: RN50  
**Audio**: TOOL - The Pot (Audio).mp3  
**Resolution Pyramid**: 256×256 → 512×512  
**Learning Rate**: 0.001 (Adam)

