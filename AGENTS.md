---
title: Repo-wide Agent Rules and Creation Logic
updated: 2025-10-11
scope: /
links:
  phase0_profile: ./docs/Phase0-Alignment/PROFILE.yaml
  phase0_context: ./docs/Phase0-Alignment/CONTEXT.md
  phase0_guides:
    - ./docs/Phase0-Alignment/PROGRESSIVE_DISCLOSURE.md
    - ./docs/Phase0-Alignment/EXPERTISE_ASSESSMENT.md
  phases:
    - ./docs/Phase0-Alignment/agents.md
    - ./docs/Phase1-Ideation/agents.md
    - ./docs/Phase2-POC/agents.md
    - ./docs/Phase3-MVP/agents.md
---

Purpose
- Define how agents are created, scoped, and coordinated across this template.
- Establish minimal, repeatable rules for edits, handoffs, and gating between phases.

Scope Rules
- Each AGENTS.md governs its directory subtree. Place one per phase folder.
- Deeper AGENTS.md takes precedence for files in its subtree.
- Follow YAML frontmatter in all artifacts to preserve context across phases.

Link Policy (Template Repos)
- Use repo-root style paths in frontmatter links for cross-phase references: `./docs/<PhaseX>/<File>`.
- Use local relative paths only for files within the same folder when the artifact will not be moved.
- Keep paths stable when copying this template; adjust only the `<project_name>` and owners.

Agent Creation Logic
- Start at Phase 0. Instantiate the minimum set of agents needed for that phase’s outcome.
- Create agents at the subfolder level with:
  - Purpose, Triggers, Inputs, Outputs (P/T/I/O)
  - Protocol (timeboxes, escalation rules, gating checks)
  - Handoffs (explicit next-state prompts + expected artifacts)
- Prefer few agents with crisp handoffs over many overlapping roles.

Subroles Standard
- Each phase `agents.md` includes a Subroles section to condense behavior per folder.
- Example subroles:
  - Phase 0: Greeter, Listener, Profiler, Synthesizer, Guide
  - Phase 1: Facilitator, Elicitor, Framer, Scribe, Gatekeeper
  - Phase 2: Researcher, Architect, Spike Planner, UX Planner, Coordinator
  - Phase 3: Planner/Gatekeeper/Summarizer (PM), Designer/Evaluator/Reviewer (Tech), Builder/Tester/Docu (Dev), Criteria Author/Verifier/Reporter (QA)

Edit Rules
- Make small, reviewable diffs; avoid broad refactors in docs.
- Update frontmatter `updated` on every change.
- Mirror user preferences from `PROFILE.yaml` (verbosity, tone, review style).
- Record assumptions in `CONTEXT.md`; confirm or remove later.

Progressive Disclosure
 - Always begin Phase 0 Level 1 with a conversational opener (5–10 minutes): “What brought you here? What would you like to use AI to help you code?” Ask at most one follow‑up (constraints or preference). See `./docs/Phase0-Alignment/PROGRESSIVE_DISCLOSURE.md`.
- Always begin with Phase 0 Level 1 questions (5–10 minutes) per `PROGRESSIVE_DISCLOSURE.md`.
- Escalate to Level 2/3 only with explicit user opt‑in or complexity demands.
- Gate a phase only when its “Success Criteria” checklist is satisfied in the phase README and verified in the codebase.

Conversation Rules
- One question at a time; user‑paced, friendly tone.
- Confirm before writing; keep diffs tiny; update `updated` field.
- Capture assumptions in `CONTEXT.md` and mark them for later confirmation.

Handoff Protocol
- Every handoff specifies P/T/I/O and a short next prompt.
- Handoffs end with an explicit update target (e.g., `PROFILE.yaml`, `CONTEXT.md`, `IDEA_NOTE.md`, `POC_PLAN.md`, `PRD.md`).
- Coordinators reconcile open questions and propose the next step with 1–2 options.

Validation
- Use the phase README checklists to confirm readiness to proceed.
- Keep references (sources) minimal but sufficient for future readers.

Quick Start
1) Open `docs/Phase0-Alignment/agents.md` and run the prompt in “Prompt Starters”.
2) Update `PROFILE.yaml` and `CONTEXT.md` minimally; set `updated`.
3) Decide whether to continue Level 2/3 or proceed to Phase 1.
4) Repeat for each phase, using its `agents.md` roles and prompts.

Notes
- This AGENTS.md codifies consistent, low-friction collaboration so that future AI tools and humans can coordinate via the same artifacts.

---

## Project Status (Updated 2025-10-11)

### Phase 2 POC - Complete

**Status:** Backend implementation complete with parameter exploration tools

**What Was Built:**
- Full audio-to-video pipeline (FFT → CPPN → GPU → MP4)
- GPU-accelerated rendering (0.61x realtime @ 720p on RTX 5070)
- Complete CLI with multiple configuration options
- Parameter exploration tools for discovering visual styles

**Critical Note:** CPPN network is untrained (random weights)
- Pipeline works technically but lacks learned aesthetics
- Visual output determined by random initialization + parameters
- See `docs/Phase2-POC/backend/CURRENT_STATE.md` for full context

**Exploration Tools:**
- `Code/backend/quick_explore.py` - Automated parameter testing
- `Code/backend/PARAMETER_EXPLORATION_GUIDE.md` - Complete guide
- `Code/backend/QUICK_TESTS.md` - Copy/paste commands

**Documentation:**
- All backend docs moved to `docs/Phase2-POC/backend/`
- See `docs/Phase2-POC/backend/README.md` for navigation

**Next Steps:**
- Parameter exploration underway (finding "happy accidents")
- Phase B direction TBD: train network, use pre-trained models, or manual tuning
- See `docs/Phase2-POC/backend/NEXT_STEPS.md` for 5 development paths
