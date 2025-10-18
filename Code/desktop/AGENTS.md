---
phase: 3
artifact: agents_desktop
project: audiovisuals-desktop
owner: Aitor
updated: 2025-10-18
status: Week 3-4 - Synesthesia Tab Implementation (IN PROGRESS)
sources:
  - PHASE_3_KICKOFF.md
  - TECHNICAL_SPEC.md
  - IMPLEMENTATION_PLAN.md
  - WEEK_3_4_PLAN.md
links:
  profile: ../../docs/Phase0-Alignment/PROFILE.yaml
  context: ../../docs/Phase0-Alignment/CONTEXT.md
  poc: ../../docs/Phase2-POC/POC_PLAN.md
  technical: ../../docs/Phase3-MVP/TECHNICAL_SPEC.md
  implementation: ../../docs/Phase3-MVP/IMPLEMENTATION_PLAN.md
  week_3_4: ./WEEK_3_4_PLAN.md
---

# Desktop Application - Agent Coordination

**Status:** Week 3-4 - Synesthesia Tab Implementation  
**Current Phase:** Building 8-feature Synesthesia Tab (video generation core)  
**Progress:** 7 of 8 features completed (87.5%)  
**Timeline:** Weeks 1-12 (see IMPLEMENTATION_PLAN.md)

---

## Active Agent Roster

### Frontend Developer (React/TypeScript)
**Purpose:** Build React UI components and state management for Synesthesia Tab

**Current Focus:** Features 1-4, 6-7 component implementations  
**Completed:**
- FileDropzone component (Feature 1)
- AudioInfoCard component (Feature 2)
- StyleSelector component (Feature 3)
- SettingsPanel component (Feature 4)
- ProgressBar component (Feature 6)
- VideoPlayer component (Feature 7)

**In Progress:** None (all React components complete)

**Responsibilities:**
- Implement React components with Tailwind styling
- Wire components to Zustand store
- Handle user interactions
- Display real-time updates
- Error boundary and loading states

**Success Metrics:**
- [ ] All components render without TypeScript errors
- [ ] All components styled with Tailwind dark theme
- [ ] Responsive layouts for different screen sizes
- [ ] Hot reload works during development

---

### Backend Developer (Rust/Tauri)
**Purpose:** Build Rust backend for Python integration and IPC

**Current Focus:** Features 1, 3, 5, 8 implementations  
**Completed:**
- file_manager.rs module (Feature 1)
- styles.rs module (Feature 3)
- storage.rs module (Feature 8)
- lib.rs updated with command registration

**In Progress:** Feature 5 (Video Generation Command)

**Responsibilities:**
- Create Python process wrapper
- Implement IPC commands
- Handle file system access
- Manage progress event streaming
- Error handling and process cleanup
- Windows path compatibility

**Success Metrics:**
- [ ] All Rust commands compile without warnings
- [ ] Commands callable from React via Tauri
- [ ] File validation working correctly
- [ ] Style scanning working from directory
- [ ] Storage persistence working

---

### Integration Specialist
**Purpose:** Coordinate React ↔ Rust ↔ Python communication

**Current Focus:** Wiring components to Rust, testing workflows

**Responsibilities:**
- Test end-to-end workflows
- Validate data flow between layers
- Debug communication issues
- Create integration tests
- Verify Windows compatibility

**Success Metrics:**
- [ ] File selection → metadata display works
- [ ] Style selection persists to store
- [ ] Settings changes update UI
- [ ] Video generation end-to-end tested
- [ ] Progress updates flow correctly

---

## Week 3-4 Coordination Plan

### Feature Dependencies

```
Feature 1: File Selection
    ↓ (required by all others)
Features 2-4: Info, Styles, Settings (can test in parallel)
    ↓ (required by)
Feature 5: Video Generation (CRITICAL gate)
    ↓ (required by)
Features 6-7: Progress, Preview (can test in parallel)
    ↓ (optional)
Feature 8: Recent Generations
```

### Daily Coordination

**Day 1-2: File Selection Testing**
- Test FileDropzone component
- Test file validation (React + Rust)
- Wire to store
- Fix any issues

**Day 3-4: Audio Info, Styles, Settings Testing**
- Test AudioInfoCard displays
- Test StyleSelector loading
- Test SettingsPanel controls
- Integrate all into SynesthesiaTab

**Day 5-7: Video Generation (BLOCKING)**
- Review Python CLI arguments
- Implement generate_video command
- Create useVideoGeneration hook
- Test with actual audio
- **GATE:** If this fails, pause other features

**Day 8-9: Progress & Preview**
- Implement progress parsing
- Display progress bar updates
- Test VideoPlayer with generated video
- Wire all together

**Day 10: Recent Generations & Polish**
- Create GenerationListItem component
- Implement storage persistence
- Full end-to-end testing
- Performance optimization

---

## Integration Testing Protocol

### Layer 1: Component Testing
Each React component tested individually:
- [ ] FileDropzone renders and accepts files
- [ ] AudioInfoCard displays metadata
- [ ] StyleSelector loads and filters
- [ ] SettingsPanel updates all controls
- [ ] ProgressBar animates smoothly
- [ ] VideoPlayer controls work

### Layer 2: Store Integration
Test Zustand store updates:
- [ ] File selection updates store
- [ ] Style selection updates store
- [ ] Settings changes propagate
- [ ] Progress state updates
- [ ] Generation history persists

### Layer 3: React-Rust Integration
Test Tauri IPC communication:
- [ ] validate_audio_file works from React
- [ ] list_styles returns data
- [ ] generate_video command functional
- [ ] Events stream to React correctly
- [ ] Errors handled gracefully

### Layer 4: End-to-End Workflow
Complete user journey:
1. Select audio file
2. View audio metadata
3. Choose style
4. Adjust settings
5. Click generate
6. Watch progress
7. Play generated video
8. See in recent list

---

## State Management Architecture

### SynesthesiaStore (Zustand)

```typescript
useSynesthesiaStore contains:

// Feature 1: File Selection
selectedAudioFile: AudioFile | null
audioMetadata: AudioFileMetadata | null
isValidatingFile: boolean
fileError: string | null

// Feature 3: Style Selector
selectedStyle: Style | null
availableStyles: StyleInfo[]
isLoadingStyles: boolean
styleError: string | null

// Feature 4: Settings Panel
generationSettings: GenerationSettings | null

// Feature 6: Progress Tracking
generationProgress: ProgressState | null
isGenerating: boolean
generationError: string | null

// Feature 8: Recent Generations
recentGenerations: Generation[]
isLoadingGenerations: boolean
```

### Data Flow

```
User Action
  ↓
React Component (FileDropzone, StyleSelector, etc.)
  ↓
useSynesthesiaStore setter
  ↓
Zustand state update
  ↓
Component re-renders
  ↓
Optional: invoke Rust command (validate_audio_file, list_styles, etc.)
  ↓
Rust command executes
  ↓
Event emitted back to React (progress events)
  ↓
Store updated with new data
  ↓
Component re-renders with new data
```

---

## Python CLI Integration

### Bridge Between React and Python

```
React Component
  ↓
usePythonCommand hook
  ↓
invoke('generate_video', params)
  ↓
Tauri commands.rs
  ↓
PythonProcess::spawn("Code\\backend\\cli.py", args)
  ↓
Python subprocess execution
  ↓
Python CLI generates video
  ↓
Rust reads stdout for progress
  ↓
emit("python-progress", event)
  ↓
React receives progress event
  ↓
Store updated
  ↓
ProgressBar component re-renders
```

### CLI Arguments Mapping

```
React GenerationSettings:
{
  audioPath: string;
  outputPath: string;
  styleName: string;
  resolution: '480p' | '720p' | '1080p';
  fps: 24 | 30 | 60;
  quality: number;
}

Maps to Python CLI:
python cli.py <audio_path> <output_path> \
  --resolution 720p \
  --fps 30 \
  --style-name "default"
```

---

## Rust Module Architecture

### file_manager.rs
- validate_audio_file(path) → FileValidationResult
- get_file_metadata(path) → AudioFileMetadata
- get_audio_duration(path) → f32

### styles.rs
- list_styles() → Vec<StyleInfo>
- get_style_details(name) → StyleDetails
- get_style_thumbnail(name) → String

### storage.rs
- load_recent_generations() → Vec<Generation>
- save_generation(gen) → ()
- delete_generation(id) → ()
- clear_all_generations() → ()

### commands.rs (existing)
- generate_video(params) → CommandResult (TO IMPLEMENT)
- test_python() → CommandResult (working)

### python.rs (existing)
- PythonProcess (struct)
- spawn(), wait(), kill() methods
- Progress parsing from stdout

---

## Error Handling Strategy

### User-Facing Errors

**File Selection:**
- "Unsupported format" → Show accepted formats
- "File too large" → Show max size
- "File not found" → Show friendly message

**Style Selection:**
- "Styles directory not found" → Show empty list
- "Failed to load styles" → Show retry button

**Video Generation:**
- "Invalid audio file" → Suggest file selection
- "Python not found" → Show setup instructions
- "Generation timeout" → Offer cancel + retry
- "Disk full" → Show storage info

### Developer Logging

- All Rust command inputs validated
- Progress events logged to console (dev mode)
- File I/O errors logged with context
- Python subprocess stderr captured

---

## Windows Compatibility Checklist

- [x] Path handling (backslash vs forward slash)
- [x] Python executable detection
- [x] UTF-8 encoding for special characters
- [x] Long paths support (> 260 chars)
- [x] File permissions handling
- [ ] CUDA GPU detection (Phase 2 responsibility)
- [x] No Unix-specific commands

---

## Performance Targets

| Target | Value | Priority |
|--------|-------|----------|
| File validation | < 1s | HIGH |
| Style loading | < 1s | MEDIUM |
| Video generation (3 min audio) | < 5 min | HIGH |
| Progress update frequency | 1-2s | HIGH |
| Video preview load | < 500ms | MEDIUM |
| Memory (idle) | < 200MB | MEDIUM |
| Memory (generating) | < 500MB | MEDIUM |

---

## Deployment Gates

### After Feature 1 (File Selection)
- [ ] File validation working end-to-end
- [ ] Store state persisting
- [ ] No TypeScript errors
- Proceed to Features 2-4

### After Feature 4 (Settings)
- [ ] All components rendering
- [ ] Store fully populated
- [ ] Layout responsive
- Proceed to Feature 5

### After Feature 5 (Video Generation) ⚠️ CRITICAL
- [ ] Python CLI integration working
- [ ] Video actually generated
- [ ] Output file created
- [ ] Errors handled
- **NO GO:** Pause all work, fix blocking issues
- **GO:** Proceed to Features 6-8

### After Feature 8 (Recent Generations)
- [ ] Full workflow tested
- [ ] All features polished
- [ ] Performance within targets
- Mark Week 3-4 COMPLETE

---

## Communication Protocol

### Daily Standup
**Time:** Start of work day  
**Duration:** 5-10 minutes  
**Topics:**
- Yesterday's completion
- Today's focus
- Blockers/risks

### Issue Resolution
**Process:**
1. Document issue in Discord/Slack
2. Record in WEEK_3_4_PLAN.md
3. Assign priority (CRITICAL / HIGH / MEDIUM / LOW)
4. Plan workaround
5. Update status daily

---

## Sign-Off

**Week 3-4 Kickoff:** 2025-10-18  
**Status:** Implementation in progress  
**Features Completed:** 7/8 (87.5%)  
**Blocker Features:** Feature 5 (Video Generation) - in progress  
**Estimated Completion:** 2025-10-25 (target)

**Next Phases:**
- Week 5-6: Analysis Tab
- Week 7-8: Styles Tab
- Week 9-12: Polish & Testing

---

**Last Updated:** 2025-10-18  
**Updated By:** AI Assistant  
**Next Review:** Daily at start of work
