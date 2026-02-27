---
id: 08-d-urs-learning-feedback-loop
title: Unified Reinforcement Signal (URS) — Learning Feedback Loop
purpose: Shows how CORTEX learns from outcomes via the URS confidence scoring cycle — VIDEO 08 hero diagram
audience: [Everyone — executives, engineers, curious learners]
source_of_truth: cortex/intelligence/learning/ + cortex/orchestrators/core/master_orchestrator.py
last_verified: 2026-02-27
diagram_type: Flowchart
interactive: false
tier: 3
learning_sequence: 30
video_prompt: 08-p-cortex-vs-the-status-quo.md
video_scene: "Scene 2 — The Learning Feedback Loop (URS circular diagram)"
animation_notes: |
  ## Cinematic Simulation Prompt — 08: URS Learning Feedback Loop

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame. CORTEX logo fades in with electric-aura glow. Hold 4s.
  Logo shrinks to bottom-right watermark.

  **SCENE 2 — "FPV Drone Dive: The Learning Orbit" (0:06–0:14)**
  Camera: FPV drone arrives at a circular glassmorphism track — four frosted glass station
  nodes in a ring: Action (blue), Outcome (amber), Signal (purple), Adaptation (green).
  Circular track glows with subtle cyan neon underline. Ray-traced reflections shimmer below.

  **SCENE 3 — "The Perpetual Orbit" (0:14–0:30)**
  A bioluminescent cyan orb enters at Action. 3 seconds per station.
  At Signal: confidence score animates as a floating holographic number — "+0.05" (green)
  for success, "-0.08" (red) for failure. At Adaptation: strategy ranking table re-sorts
  in real-time. The particle completes 3 full orbits, each brighter than the last.

  **SCENE 4 — "The Compound Effect" (0:30–0:44)**
  Camera: Zooms out. Three dashboard panels materialize — Transformation Timeline:
  Week 1 (red metrics, dim), Week 4 (amber, improving), Week 12 (green, full luminosity).
  Below: Team A (green), Team B (amber), Team C (red) with a Shared Knowledge Base (gold)
  at center. Bioluminescent arrows flow Team A → Shared KB → Team C.

  **SCENE 5 — "Orbital Reveal" (0:44–0:54)**
  Camera: 360-degree orbital pan around the complete URS architecture — circular orbit,
  transformation timeline, multi-team compound effect. Glassmorphism "Evidence Bundle"
  icon materializes — sealed document with cyan checkmark — fades to black.
related_diagrams:
  - 07-d-orchestrator-dispatch-flow.md
  - 09-d-platform-saas-architecture.md
---

## URS Learning Feedback Loop

### Part A — The Learning Cycle

```
  ┌─────────────────────────────────────────────────────────────┐
  │                  URS Learning Cycle                         │
  │                  (perpetual — every operation)              │
  │                                                             │
  │                    ┌───────────────────┐                    │
  │                    │                   │                    │
  │                    ▼                   │                    │
  │          ┌──────────────────────┐      │                    │
  │          │    🎯 ACTION         │      │                    │
  │          │  Execute the task    │      │                    │
  │          │  implement/fix/refact│      │                    │
  │          └──────────┬───────────┘      │                    │
  │                     │                  │                    │
  │                     ▼                  │                    │
  │          ┌──────────────────────┐      │                    │
  │          │    📊 OUTCOME        │      │                    │
  │          │  Measure result      │      │                    │
  │          │  test / gov / deploy │      │                    │
  │          └──────────┬───────────┘      │                    │
  │                     │                  │                    │
  │                     ▼                  │                    │
  │          ┌──────────────────────┐      │                    │
  │          │    📡 SIGNAL         │      │                    │
  │          │  Update confidence   │      │                    │
  │          │  +0.05 success       │      │                    │
  │          │  -0.08 failure       │      │                    │
  │          └──────────┬───────────┘      │                    │
  │                     │                  │                    │
  │                     ▼                  │                    │
  │          ┌──────────────────────┐      │                    │
  │          │    🔄 ADAPTATION     │      │                    │
  │          │  Re-rank strategies  │      │                    │
  │          │  next request        │──────┘                    │
  │          │  benefits immediately│                           │
  │          └──────────────────────┘                           │
  │                                                             │
  │   Signal ·····feeds·····►  Shared Knowledge Base            │
  │   Adaptation ···informs·►  Week 1 baseline calibration      │
  └─────────────────────────────────────────────────────────────┘
```

### Part B — Transformation Timeline

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  Week 1              Week 4              Week 12                 │
  │  ──────────────      ──────────────      ──────────────          │
  │  Coverage:  42%      Coverage:  68%      Coverage:  91%          │
  │  Violations:187      Violations: 23      Violations:  0          │
  │  MTTF:  4.2 days     MTTF:  1.8 days     MTTF:  0.4 days         │
  │                                                                  │
  │  [🔴 dim]            [🟠 improving]      [🟢 full luminosity]    │
  │       │                    │                    │                │
  │       └────────────────────┴────────────────────┘                │
  │  TDD enforced → Governance auto → Patterns compound              │
  └──────────────────────────────────────────────────────────────────┘
```

### Part C — Compound Effect (Multi-Team)

```
  ┌────────────────────────────────────────────────────────────────┐
  │                                                                │
  │   Team A (Week 12)                     Team C (Week 1)        │
  │   🟢 Fully Green                       🔴 Just Starting       │
  │        │                                    ▲                 │
  │        │  contributes patterns              │  receives        │
  │        ▼                                    │  patterns        │
  │   ┌────────────────────────────────────┐    │                 │
  │   │   ⭐ Shared Knowledge Base          │────┘                 │
  │   │   Patterns + Confidence Scores      │                     │
  │   │   Cross-team learning persists      │                     │
  │   └────────────────────────────────────┘                     │
  │        ▲                                                      │
  │        │  contributes patterns                                │
  │   Team B (Week 6)                                             │
  │   🟡 Improving                                                │
  │                                                               │
  │   Key insight: Team C starts at Week 12 quality from day 1   │
  │   because Team A's patterns are already in the shared KB.     │
  └────────────────────────────────────────────────────────────────┘
```
