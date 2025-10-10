---
phase: 1
artifact: idea_note
project: audio_feature_explorer
owner: Aitor Patiño Diaz
updated: 2025-01-27
sources:
  - Research Proposal: Audio Feature Explorer (Local Desktop Edition)
  - CV: AI framework designer with audio/video analysis experience
links:
  profile: ./docs/Phase0-Alignment/PROFILE.yaml
  context: ./docs/Phase0-Alignment/CONTEXT.md
---

Objective
- Build a desktop audio-reactive visualization app that uses AI-generated CPPNs (Compositional Pattern-Producing Networks) to create living, evolving visual organisms that respond to audio analysis, representing the neural evolution beyond static MilkDrop presets.

User Preferences (from PROFILE)
- Communication: comprehensive/expert-level/collaborative
- Decision Style: collaborative with immediate feedback

Problem Framing
- Who is the user? Audio enthusiasts, artists, developers seeking next-generation music visualization beyond static presets
- What pain point is addressed? Current audio visualizers (MilkDrop, etc.) use deterministic, hand-written equations that create predictable patterns - users want living, evolving visuals that improvise with the music
- Why now? AI/ML capabilities enable real-time neural field rendering, and users are ready for "living math" vs. static formulas

Goals and Success Metrics
- Goals:
  - Create audio-reactive CPPNs that generate living, emergent visual patterns (vs. static MilkDrop presets)
  - Build real-time neural field renderer that processes audio features through learned mathematical organisms
  - Achieve "improvising with you" experience where visuals mutate in pattern space rather than following preset recipes
- Metrics:
  - Real-time performance: 60 FPS with <16ms latency for audio-to-visual response
  - Visual diversity: Generate unique patterns for each audio track (vs. static preset library)
  - User engagement: "Living math" creates unpredictable but beautiful emergent behaviors

Scope and Constraints
- In-scope:
  - CPPN-based neural field rendering with audio reactivity
  - Local ML models for audio feature extraction (OpenL3, YAMNet, VGGish)
  - Cross-platform desktop app with Tauri architecture
  - Real-time WebGL shader pipeline for neural field visualization
  - Hybrid approach: MilkDrop FFT data stream feeding CPPN inputs
- Out-of-scope:
  - Cloud-based processing (local-first for privacy/performance)
  - Mobile/web versions (desktop-focused)
  - Live audio input (file-based analysis)
  - Traditional static preset library (focus on AI-generated patterns)

Risks and Unknowns
- CPPN computational complexity may exceed real-time constraints on consumer hardware
- Neural field rendering pipeline integration with existing audio analysis workflow
- Training/evolving CPPN weights for audio reactivity without losing visual coherence
- Hybrid MilkDrop-CPPN integration: feeding .milk FFT data into neural inputs

Research Findings
- CPPNs represent evolution from deterministic MilkDrop presets to learned mathematical organisms
- Audio-reactive CPPNs: R,G,B = CPPN(x, y, t, bass, mid, treb, mood) creates emergent vs. parametric behavior
- Neural fields can mutate in pattern space rather than following explicit rules like "zoom = sin(time)"
- ProjectM exists as open-source MilkDrop implementation for potential hybrid integration

Quick Technical Notes
- Stack: Tauri (Rust) + Python sidecar + WebGL frontend
- Key Integration: Audio features → CPPN inputs → Neural field → Pixel rendering
- Feasibility: CPPN rendering possible on modern GPUs, audio analysis proven with existing models
- Unknowns: Real-time CPPN performance, optimal audio feature mapping to neural inputs

Phase 1 Prompt Starters
```text
Refine the idea:
- Validate the main idea against user goals and constraints.
- Extract concrete goals and measurable outcomes.
- Identify unknowns and propose small validation tasks.
Output: Fill this file with the refined objective and plan.
```


