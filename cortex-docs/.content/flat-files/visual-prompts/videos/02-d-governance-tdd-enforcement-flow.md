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

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame. Environment: Absolute dark-blue vacuum (#0a0e27).
  CORTEX logo fades in with electric-aura pulse-glows radiating outward. Hold 4s.
  Logo shrinks to bottom-right watermark (15% opacity).

  **SCENE 2 — "FPV Drone Dive: The Shield Wall" (0:06–0:20)**
  Camera: FPV drone dives through volumetric fog into three concentric glassmorphism
  shield walls. Inner Shield (Pre-Commit): red neon filaments. Middle Shield (CI): amber
  filaments. Outer Shield (Runtime): green filaments. A bioluminescent code particle
  strikes the Pre-Commit shield — RED flash, particle bounces back (violation detected).
  It reforms with a fix, passes through all three shields with magnetic iris animations.

  **SCENE 3 — "TDD Heartbeat: The ECG of Quality" (0:20–0:34)**
  Camera: Pulls back to reveal a glassmorphism ECG monitor.
  RED peak: failing test capsule materializes. GREEN peak: implementation passes the test.
  BLUE peak: refactor capsule restructures. The rhythm loops 3 cycles with bioluminescent
  neon traces leaving persistent light at each peak.

  **SCENE 4 — "Unified View" (0:34–0:44)**
  Shield Wall (top) and TDD ECG (bottom) merge. The Governance Rules Engine appears:
  "38 CORE Rules" in a frosted glass slab with purple neon filaments. EnforcementOrchestrator
  connects to all three shields via neon conduits. SQLite Audit Log receives entries from
  every interaction.

  **SCENE 5 — "Orbital Reveal" (0:44–0:54)**
  Camera: 360-degree orbital pan around the combined Shield Wall + TDD ECG architecture.
  All shields glow. ECG heartbeat continues. Glassmorphism "Evidence Bundle" icon
  materializes center-frame — sealed document with cyan checkmark — fades to black.
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
