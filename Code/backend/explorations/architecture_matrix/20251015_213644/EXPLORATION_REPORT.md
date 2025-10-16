# Architecture Matrix Exploration Report

**Date:** 2025-10-15 21:46:32  
**Status:** 36/36 configurations completed successfully

---

## Matrix Configuration

**Layers tested:** 2, 3, 4, 5  
**Hidden dimensions:** 32, 64, 128  
**Seeds per config:** 3  
**Total configurations:** 36

---

## Results Summary

| Layers | Hidden Dim | Params | Seeds Tested | Success | Avg Size (MB) |
|--------|-----------|--------|--------------|---------|---------------|
| 2 | 32 | 1,571 | 3 | ✅ | 2.9 |
| 2 | 64 | 5,187 | 3 | ✅ | 2.7 |
| 2 | 128 | 18,563 | 3 | ✅ | 2.6 |
| 3 | 32 | 2,627 | 3 | ✅ | 4.1 |
| 3 | 64 | 9,347 | 3 | ✅ | 3.9 |
| 3 | 128 | 35,075 | 3 | ✅ | 3.3 |
| 4 | 32 | 3,683 | 3 | ✅ | 6.5 |
| 4 | 64 | 13,507 | 3 | ✅ | 6.0 |
| 4 | 128 | 51,587 | 3 | ✅ | 5.4 |
| 5 | 32 | 4,739 | 3 | ✅ | 16.9 |
| 5 | 64 | 17,667 | 3 | ✅ | 12.9 |
| 5 | 128 | 68,099 | 3 | ✅ | 11.7 |

---

## Failed Configurations

None - all configurations succeeded! ✅

---

## Next Steps

1. **Visual Review** - Open videos in `20251015_213644` and review visual quality
2. **Rating** - Use `rate_architectures.py` to rate each configuration on:
   - Organic quality (spirals, cells, fluid forms)
   - Coherence (spatial continuity)
   - Audio reactivity (responsiveness)
   - Aesthetic appeal (subjective beauty)
3. **Selection** - Identify top 3-5 configurations for CLIP training
4. **Documentation** - Update ARCHITECTURE_CATALOG.md with findings

---

## Files Generated

**Videos:** 36 × 10-second clips  
**Frames:** 36 representative frames (at t=5s)  
**Location:** `..\explorations\architecture_matrix\20251015_213644`

---

**Generated:** 2025-10-15 21:46:32
