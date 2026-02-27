---
id: 02-d-governance-tdd-enforcement-flow
title: Governance & TDD Enforcement Pipeline
purpose: Shows how 38 CORE governance rules are enforced at pre-commit, CI, and runtime with TDD gates — VIDEO 02 hero diagram
audience: [Software Developers, Tech Leads, Engineering Managers]
source_of_truth: cortex/governance/ + cortex/orchestrators/core/enforcement_orchestrator.py
last_verified: 2026-02-27
diagram_type: Flowchart
interactive: false
tier: 2
learning_sequence: 25
video_prompt: 02-p-the-trust-layer.md
video_scene: "Scene 2 — The Shield Wall (governance layers) + Scene 3 — TDD Heartbeat"
animation_notes: |
  ## Cinematic Simulation Prompt — 02: Governance & TDD Enforcement

  ### Visual Physics & Ambience Protocol
  - **Environment:** Dark-blue vacuum (#0a0e27) with ray-traced reflections on glass floors
  - **Shield textures:** Frosted glassmorphism with internal neon filaments (red/amber/green per layer)
  - **Lighting:** Volumetric fog, bioluminescent particle trails, ray-traced caustics on shield surfaces
  - **Feedback cues:** Holographic glitch = violation detected, green pulse = rule passed, Lidar scan = validation
  - **ECG monitor:** Glassmorphism surface with persistent neon traces at RED/GREEN/BLUE peaks

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame, locked on ray-traced glassmorphism floor.
  Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric fog at ground level.
  CORTEX logo (cortex-logo.png) fades in as large central hero image with electric-aura
  pulse-glows radiating outward — concentric cyan and purple rings cast volumetric light
  into the fog. Ray-traced reflections shimmer across the glass floor. Hold 4s.
  Logo shrinks to bottom-right watermark (15% opacity) with ease-out parallax slide.

  **SCENE 2 — "FPV Drone Dive: The Shield Wall" (0:06–0:20)**
  Camera: FPV drone dives at 45° through volumetric fog — fog layers part with parallax
  depth, peripheral motion blur. Three concentric glassmorphism shield walls emerge from
  the mist with time-lapse mechanical assembly — glass panels fold and seal with magnetic
  iris animations.
  Inner Shield (Pre-Commit): red neon filaments pulse like living circuitry, internal
  bioluminescent glow casts volumetric light outward.
  Middle Shield (CI): amber neon filaments with ray-traced reflections on adjacent shields.
  Outer Shield (Runtime): green neon filaments with holographic surface shimmer.
  A bioluminescent code particle strikes the Pre-Commit shield — holographic glitch
  effect: shield surface ripples, RED flash with particle fragmentation into red sparks.
  Particle bounces back, reforms with a particle evolution animation (sparks re-condense
  into a corrected cyan orb with a green pulse confirmation), passes through all three
  shields with magnetic iris open-close animations. Each successful passage leaves a
  bioluminescent trail on the shield surface.

  **SCENE 3 — "TDD Heartbeat: The ECG of Quality" (0:20–0:34)**
  Camera: Slow dolly pull-back with parallax depth to reveal a glassmorphism ECG monitor
  hovering in the dark-blue vacuum. Ray-traced reflections of the ECG glow on the floor.
  RED peak: failing test capsule materializes from particle condensation — red neon
  filaments pulse, holographic glitch on the waveform. Strategic silence (1s).
  GREEN peak: implementation passes — green bioluminescent burst, capsule solidifies
  with a satisfying mechanical snap. ECG trace leaves persistent green neon trail.
  BLUE peak: refactor capsule restructures with a time-lapse mechanical animation —
  internal components re-arrange while maintaining structural integrity.
  The rhythm loops 3 cycles, each cycle brighter than the last — a transformation
  timeline showing RED violation sparks being physically filtered out and replaced by
  a steady green hum over multiple rotations. Persistent bioluminescent neon traces
  accumulate at each peak, creating a visible history of improvement.

  **SCENE 4 — "Unified View" (0:34–0:44)**
  Camera: Slow macro zoom out with orbital drift. Shield Wall (top) and TDD ECG (bottom)
  merge into a unified glassmorphism architecture. The Governance Rules Engine appears
  as a frosted glass slab: "38 CORE Rules" in purple neon filaments with internal
  bioluminescent circuitry. EnforcementOrchestrator connects to all three shields via
  neon conduit tubes — each conduit pulsing with data particles traveling along ray-traced
  glass corridors. SQLite Audit Log receives entries from every interaction as particle
  streams flowing into a crystalline database icon with volumetric glow.

  **SCENE 5 — "Orbital Reveal" (0:44–0:54)**
  Camera: 360-degree orbital pan at 25° downward angle around the combined Shield Wall +
  TDD ECG architecture. Parallax depth — shields rotate faster than background fog.
  All shields glow with ray-traced reflections. ECG heartbeat continues with persistent
  bioluminescent trails. Camera completes orbit with slow dolly-out.
  Glassmorphism "Evidence Bundle" icon materializes center-frame — sealed document with
  cyan checkmark and holographic shimmer — fades to black.
related_diagrams:
  - 04-d-audit-pipeline-stages.md
  - 03-d-golden-test-pyramid-and-security-layers.md
---

## Governance & TDD Enforcement Pipeline

### Part A — The Shield Wall

```
  Developer Workspace
  ───────────────────
  Code Change
       │
       ▼
  ┌────────────────────────────────────────────────────────────┐
  │                SHIELD WALL — Governance Enforcement        │
  │                                                            │
  │  ┌──────────────────────────────────────────────────────┐  │
  │  │   🔴 Pre-Commit Hook  (EnforcementOrchestrator)      │  │
  │  │   38 CORE rules checked before any commit lands      │  │
  │  └─────────┬────────────────────────┬───────────────────┘  │
  │            │ PASS                   │ BLOCK                 │
  │            │                        ▼                       │
  │            │                  ┌──────────────┐              │
  │            │                  │ Fix Violation│◄─────────┐   │
  │            │                  └──────┬───────┘          │   │
  │            │                         └──────────────────┘   │
  │            ▼                                                 │
  │  ┌──────────────────────────────────────────────────────┐   │
  │  │   🟠 CI Pipeline                                     │   │
  │  │   Full suite: lint, type-check, governance scan      │   │
  │  └─────────┬────────────────────────┬───────────────────┘   │
  │            │ PASS                   │ BLOCK                  │
  │            │                        ▼                        │
  │            │                  ┌──────────────┐               │
  │            │                  │ Fix Violation│◄──────────┐   │
  │            │                  └──────┬───────┘           │   │
  │            │                         └───────────────────┘   │
  │            ▼                                                  │
  │  ┌──────────────────────────────────────────────────────┐    │
  │  │   🟢 Runtime Validation                              │    │
  │  │   Continuous guard — governance checks at runtime    │    │
  │  └─────────┬────────────────────────┬───────────────────┘    │
  │            │ PASS                   │ BLOCK                   │
  └────────────┼────────────────────────┼───────────────────────-┘
               ▼                        ▼
          Deploy ✅              Fix Violation ──► loop back
```

### Part B — Governance Rules Engine

```
  ┌─────────────────────────────────────────────────────┐
  │            Governance Rules Engine                  │
  │                                                     │
  │   ┌────────────────────────┐                        │
  │   │  38 CORE Rules         │                        │
  │   │  YAML Registry         │                        │
  │   └────────────┬───────────┘                        │
  │                │                                    │
  │                ▼                                    │
  │   ┌────────────────────────┐    ┌────────────────┐  │
  │   │ EnforcementOrchestrator│───►│ SQLite Audit   │  │
  │   └────┬──────┬──────┬─────┘    │ Log            │  │
  │        │      │      │          └────────────────┘  │
  │        ▼      ▼      ▼                              │
  │  Pre-Commit   CI   Runtime                          │
  └─────────────────────────────────────────────────────┘
```

### Part C — TDD Heartbeat (CORE-008)

```
  ┌────────────────────────────────────────────────────┐
  │              TDD Cycle — Repeats Forever           │
  │                                                    │
  │        ┌──────────────────────────────┐            │
  │        │                              │            │
  │        ▼                              │            │
  │  ┌───────────┐                        │            │
  │  │ 🔴 RED    │  Write the failing     │            │
  │  │           │  test first            │            │
  │  └─────┬─────┘                        │            │
  │        │                              │            │
  │        ▼                              │            │
  │  ┌───────────┐                        │            │
  │  │ 🟢 GREEN  │  Implement minimum     │            │
  │  │           │  code to pass          │            │
  │  └─────┬─────┘                        │            │
  │        │                              │            │
  │        ▼                              │            │
  │  ┌───────────┐                        │            │
  │  │ 🔵 BLUE   │  Refactor + clean up   │            │
  │  │ REFACTOR  │  (all tests still pass)│            │
  │  └─────┬─────┘                        │            │
  │        │                              │            │
  │        └──────────────────────────────┘            │
  └────────────────────────────────────────────────────┘

  Every change validated → SQLite Audit Log
```
