---
phase: 3
artifact: prd
project: Audio Feature Explorer Desktop App
owner: Aitor
updated: 2025-10-17
sources: 
  - UX_RESEARCH.md
  - TECHNICAL_SPEC.md
  - IMPLEMENTATION_PLAN.md
  - synesthesia research
  - PHASE_3_KICKOFF.md
links:
  profile: ./docs/Phase0-Alignment/PROFILE.yaml
  context: ./docs/Phase0-Alignment/CONTEXT.md
  idea: ./docs/Phase1-Ideation/IDEA_NOTE.md
  poc: ./docs/Phase2-POC/POC_PLAN.md
  architecture: ./ARCHITECTURE_INTEGRATION.md
---

# Product Requirements Document - Phase 3 MVP

## Product Summary

Audio Feature Explorer is a **fully local desktop application** that transforms audio files into stunning visual content using ML-powered synesthetic generation. Built on top of proven Phase 2 CLI tools, the MVP provides an intuitive GUI for three core workflows: (1) generating audio-reactive videos using CLIP-trained CPPN networks with the optimal 3L×4D architecture, (2) analyzing music semantics through 5 specialized analyzers (tempo, key, chords, structure, genre), and (3) managing a visual style library. The application runs entirely on the user's machine with no internet dependency, targeting music producers, researchers, and visual artists who want intelligent, customizable audio visualization without cloud subscriptions or manual After Effects work.

**Key Innovation:** Combines music understanding (semantic analysis) with learned aesthetics (CLIP-trained styles) and computational efficiency (3L×4D optimal architecture) in a single desktop app.

---

## Users and Use Cases

### Primary Users

**1. Music Producers & Content Creators** (Alex persona)
- Generate visualizations for tracks, albums, social media
- Quick turnaround needed (< 5 minutes per video)
- Technical skill: Low to medium

**2. Music Researchers & Analysts** (Dr. Morgan persona)
- Extract semantic features for academic research
- Analyze musical structure, harmony, rhythm
- Technical skill: High, but prefers GUI over CLI

**3. Visual Artists & VJ Performers** (Jamie persona)
- Explore parameter spaces for live visuals
- Create custom aesthetic styles
- Technical skill: Medium to high

### Top Use Cases

**UC1: Generate Music Video**
- User drops audio file → selects style preset → generates video
- Time: < 2 minutes to first video
- Output: MP4 with synced audio, 720p-1080p @ 60fps

**UC2: Analyze Music Semantics**
- User loads track → runs 5 analyzers → views interactive charts
- Time: < 30 seconds for 6-minute track
- Output: JSON data + HTML reports + Plotly visualizations

**UC3: Train Custom Style**
- User inputs text prompt → trains CLIP style → applies to videos
- Time: 6-8 minutes training
- Output: Reusable .pth weight file

**UC4: Explore Parameters**
- User adjusts sliders → generates quick previews → saves presets
- Time: < 30 seconds per preview
- Output: 10-second video clips, saved presets

---

## Requirements

### Must Have (MVP Launch Blockers)

**Core Functionality:**
1. **Synesthesia Tab** - Complete video generation workflow
   - File picker (drag & drop + native dialog)
   - Style preset selector (minimum 3 trained styles)
   - Resolution/FPS settings (480p/720p/1080p, 24/30/60fps)
   - Generate button with real-time progress (0-100%)
   - Video preview player (Video.js integration)
   - Uses 3L×4D optimal architecture by default

2. **Analysis Tab** - All 5 semantic analyzers working
   - Analyzer selection (tempo, key, chords, structure, genre)
   - Parallel execution (all 5 run simultaneously)
   - Interactive Plotly visualizations
   - Export to JSON/CSV/HTML

3. **Styles Tab** - Basic library management
   - Grid display of available styles with thumbnails
   - Style metadata (params, similarity, date)
   - Apply style to Synesthesia tab
   - Delete style (with confirmation)

4. **Python Integration** - Robust backend wrapper
   - Rust spawns Python processes
   - STDOUT/STDERR capture for progress
   - Process cleanup on cancel/error
   - File path handling (Windows/Mac/Linux)

5. **Error Handling** - User-friendly failure modes
   - Missing dependencies detection
   - File format validation
   - GPU/CPU fallback messaging
   - Clear error dialogs with troubleshooting

**Quality Requirements:**
- App launches < 2 seconds
- No crashes during normal use
- All existing CLI tools work via GUI
- Cross-platform (Windows first, then Mac/Linux)

### Nice to Have (Post-MVP)

1. **Explorer Tab** - Parameter space exploration with sliders
2. **Projects Tab** - File management and organization
3. **Style Training Wizard** - New style creation in GUI
4. **Batch Processing** - Generate videos for multiple tracks
5. **Keyboard Shortcuts** - Power user efficiency
6. **Real-time Preview** - Live parameter adjustment
7. **Advanced Controls** - Custom architecture configuration (layers, hidden_dim)
8. **Synesthesia Research Integration** - Emotion-guided mappings, cross-modal correspondences, RL adaptation (Phase 4+)

---

## Acceptance Criteria

### AC1: First Video Generation (Critical Path)

**Scenario: User generates first video**
- **Given** the app is launched and Python backend is detected
- **When** user drags audio file (MP3/WAV), selects "Cosmic Galaxy" style, resolution "720p", clicks "Generate Full Video"
- **Then**:
  - Progress bar updates every 1-2 seconds (0% → 100%)
  - Estimated time remaining displayed and updating
  - Video generation completes in < 10 minutes for 6-min track
  - Output MP4 file is playable and has synced audio
  - Video plays in preview player
  - Recent generations list updates with new entry

**Success Metric:** 100% completion rate in user testing (n=5 users)

---

### AC2: Music Analysis Workflow

**Scenario: User analyzes track semantics**
- **Given** an audio file is selected
- **When** user checks all 5 analyzers and clicks "Run Analysis"
- **Then**:
  - All analyzers execute in parallel
  - Progress indicators show per-analyzer status
  - Total completion time < 30s for 6-min track
  - Summary panel displays: tempo (BPM), key (note + scale), genre (top 3), time signature
  - Interactive Plotly charts render correctly (tempo timeline, chord progression, structure segments)
  - Export buttons produce valid JSON/CSV/HTML files

**Success Metric:** All 5 analyzers complete without errors 95% of the time

---

### AC3: Style Library Management

**Scenario: User browses and applies styles**
- **Given** the Styles tab is open
- **When** user views library (minimum 3 presets: Cosmic Galaxy, Cellular, Organisms)
- **Then**:
  - Grid displays style cards with thumbnail previews
  - Each card shows: name, architecture (3L×4D), parameter count (~200), training date
  - Clicking a style highlights it
  - "Apply to Synesthesia" button enables
  - Clicking "Apply" switches to Synesthesia tab with style pre-selected
  - Delete button shows confirmation dialog before removing

**Success Metric:** Users can apply a style in < 30 seconds from app launch

---

### AC4: Error Recovery

**Scenario: User encounters missing dependency**
- **Given** Python backend is not found or dependencies missing
- **When** user attempts to generate video or run analysis
- **Then**:
  - Clear error dialog appears: "Python backend not found. Please ensure Python 3.12+ is installed and dependencies are available."
  - Dialog includes "Show Setup Guide" button
  - Setup guide opens with troubleshooting steps
  - App does not crash
  - User can retry after fixing dependencies

**Success Metric:** 0 crashes during error conditions

---

### AC5: Progress Tracking

**Scenario: Long-running operation with feedback**
- **Given** video generation is in progress
- **When** processing takes >10 seconds
- **Then**:
  - Progress bar visible and updating (not frozen)
  - Progress message shows current stage: "Analyzing audio features...", "Rendering frames...", "Encoding video..."
  - Estimated time remaining updates every 5 seconds
  - Cancel button is visible and functional
  - Clicking cancel stops Python process cleanly
  - UI remains responsive (60fps animations)

**Success Metric:** Users report feeling informed about progress (survey >4/5)

---

## Non-Functional Requirements

### Performance

**Targets:**
- **App Launch:** < 2 seconds from click to UI ready
- **Tab Switch:** < 100ms, instant feel
- **Video Generation:** 720p @ 60fps in ~6-10 minutes for 6-min audio (0.6-1.0× realtime)
- **Music Analysis:** < 30 seconds for 6-min track (all 5 analyzers)
- **Memory Usage:** < 500 MB idle, < 2 GB during generation
- **UI Responsiveness:** 60 FPS animations, no lag

**Optimizations:**
- 3L×4D architecture (200 params) guarantees real-time rendering
- Parallel analyzer execution
- Lazy loading for large file lists
- Debounced parameter sliders

### Security

**Considerations:**
- **Sandboxed Python:** Processes spawned via Rust std::process, no direct shell access
- **File System:** Tauri FS allowlist restricts access to project directories only
- **No Internet:** Fully local execution, no telemetry, no cloud uploads
- **User Privacy:** All data stays on user's machine, no logging to external services
- **Process Limits:** Timeout enforcement, memory limits to prevent runaway processes

### Reliability

**Targets:**
- **Uptime:** App should not crash during normal workflows (target: 0 critical bugs in production)
- **Process Management:** Clean Python process cleanup on cancel, crash, or app exit
- **Error Handling:** Graceful degradation, user-friendly error messages
- **Data Integrity:** Generated files not corrupted, metadata consistent
- **Cross-platform:** Works on Windows 10/11, macOS 11+, Ubuntu 20.04+

**Testing:**
- Integration tests for IPC commands
- End-to-end tests for full workflows
- Manual testing on all 3 platforms

### Observability

**Logging:**
- App-level logs: Tauri events, IPC messages, errors
- Python process logs: STDOUT/STDERR captured and stored
- User actions: Button clicks, file selections (local only, no telemetry)

**Metrics (Local Only):**
- Generation success/failure rates
- Average processing times
- Error frequency by type

**No Cloud Telemetry:** All logging stays local for debugging, no external servers

---

## Rollout Plan

### Milestones

**M1: Foundation Complete (Week 2)**
- Goal: Tauri project runs, tabs navigate, Python wrapper works
- Deliverables:
  - App launches and displays 5 tabs
  - Rust can spawn Python and capture output
  - IPC communication functional
- Acceptance: Developer can manually test Python CLI calls from Rust

**M2: Synesthesia MVP (Week 4)**
- Goal: Core video generation workflow end-to-end
- Deliverables:
  - File selection working
  - Style selector populated with 3 presets
  - Video generation completes successfully
  - Progress tracking functional
  - Video preview plays
- Acceptance: User can generate video from start to finish in < 2 minutes

**M3: Analysis Tab (Week 6)**
- Goal: All 5 analyzers working with visualizations
- Deliverables:
  - Analyzer selection UI
  - Parallel execution working
  - Plotly charts rendering
  - Export functionality
- Acceptance: All analyzers complete in < 30s, charts display correctly

**M4: Styles Tab (Week 8)**
- Goal: Style library management functional
- Deliverables:
  - Style grid display
  - Apply to Synesthesia works
  - Delete with confirmation
  - Minimum 5 trained styles (Cosmic series)
- Acceptance: User can browse and apply styles easily

**M5: Polish & Testing (Week 12)**
- Goal: Beta-ready application
- Deliverables:
  - Error handling comprehensive
  - Performance optimized
  - User testing complete (5 users)
  - Critical bugs fixed
  - User documentation written
- Acceptance: User satisfaction >4.5/5, task completion >90%, 0 critical bugs

### Release Criteria (MVP Launch)

**Technical:**
- ✅ All 3 must-have tabs functional (Synesthesia, Analysis, Styles)
- ✅ Python integration reliable (no zombie processes, clean errors)
- ✅ Performance targets met (see targets above)
- ✅ Cross-platform tested (Windows + Mac at minimum)
- ✅ No critical bugs, < 5 high-priority bugs

**User Experience:**
- ✅ First video generation < 2 minutes
- ✅ Task completion rate > 90% (user testing)
- ✅ User satisfaction > 4.5/5 (post-use survey)
- ✅ Error rate < 5%

**Documentation:**
- ✅ User guide (getting started, features, troubleshooting)
- ✅ Developer docs (architecture, build instructions)
- ✅ README with clear installation steps

**Packaging:**
- ✅ Windows installer (.msi)
- ✅ macOS bundle (.dmg) - optional for MVP
- ✅ Linux AppImage/deb - optional for MVP
- ✅ < 50 MB installer size

---

## Future Enhancements (Post-MVP)

### Phase 4+: Advanced Synesthesia Features

Inspired by `synesthesia research`:

1. **Emotion-Guided Mappings**
   - Integrate valence/arousal classifier
   - Map harmonic tension → color saturation
   - Use Music2Palette dataset for training

2. **Cross-Modal Correspondences**
   - Default mappings: pitch → brightness, timbre → hue
   - Spectral centroid → color warmth
   - Roughness → saturation levels

3. **Personalized Mappings**
   - User-configurable sound → color associations
   - Learn from user preferences via RL
   - DNN-based personal mapping classifier

4. **Bi-Directional Control**
   - Paint colors to affect audio synthesis (Sonicolour-inspired)
   - Co-creative loop: visual adjustments modify audio parameters

5. **Research Collaborations**
   - Integrate MuCED dataset (music → palette pairs)
   - Collaborate with synesthesia research groups
   - Contribute to cross-modal research

**Timeline:** Phase 4 (Months 4-6 after MVP launch)

---

## Phase 3 Prompt Starters

```text
Define MVP requirements:
- ✅ Product summary: Audio Feature Explorer desktop app
- ✅ Users: Creators, Researchers, Artists
- ✅ Must-have requirements: 3 tabs (Synesthesia, Analysis, Styles)
- ✅ Acceptance criteria: 5 key scenarios with Given/When/Then
- ✅ Non-functional requirements: Performance, security, reliability
- ✅ Rollout plan: 5 milestones over 12 weeks

Outputs: PRD.md complete and ready for implementation.
```

---

**Updated:** 2025-10-17  
**Status:** ✅ PRD Complete - Ready for Development  
**Next:** Set up development environment (Week 1 tasks)


