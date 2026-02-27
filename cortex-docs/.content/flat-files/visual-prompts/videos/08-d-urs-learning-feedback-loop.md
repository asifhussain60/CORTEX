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

  ### Visual Physics & Ambience Protocol
  - **Environment:** Dark-blue vacuum (#0a0e27) with ray-traced reflections on glass orbital track
  - **Orbital track:** Circular glassmorphism ring with cyan neon underline and internal bioluminescence
  - **Station nodes:** Frosted glassmorphism with per-station neon filaments (blue/amber/purple/green)
  - **Lighting:** Volumetric fog, ray-traced caustics from orbital neon, bioluminescent particle wake
  - **Feedback cues:** +0.05 holographic green = success signal, -0.08 holographic red = failure signal
  - **Temporal evolution:** Each orbit brighter — transformation timeline from dim/red → amber → green/vibrant

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame, locked on ray-traced glassmorphism floor.
  Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric fog at ground level.
  CORTEX logo (cortex-logo.png) fades in as large central hero image with electric-aura
  glow — cyan pulse radiates outward. Ray-traced reflections shimmer on the floor. Hold 4s.
  Logo shrinks to bottom-right watermark (15% opacity) with ease-out parallax slide.

  **SCENE 2 — "FPV Drone Dive: The Learning Orbit" (0:06–0:14)**
  Camera: FPV drone arrives from above at 45° angle, diving through volumetric fog with
  parallax depth separation. A circular glassmorphism track emerges from the mist with
  time-lapse mechanical assembly — glass segments curve and seal together, forming a
  continuous orbital ring. Four frosted glass station nodes materialize at cardinal points
  with particle condensation: Action (blue neon filaments), Outcome (amber neon filaments),
  Signal (purple neon filaments), Adaptation (green neon filaments).
  Circular track glows with subtle cyan neon underline — ray-traced reflections of the
  orbital neon shimmer on the glass floor below, creating a glowing circle shadow.
  Internal bioluminescent particles drift along the track like a slow current.

  **SCENE 3 — "The Perpetual Orbit" (0:14–0:30)**
  Camera: Orbital tracking — camera follows the particle around the loop with slight
  parallax against station backgrounds. Slow dolly-in during key moments.
  A bioluminescent cyan orb enters at Action with particle condensation animation.
  3 seconds per station with volumetric light bloom and ray-traced caustics:
  At Action: station's blue neon filaments pulse, internal circuitry illuminates.
  At Outcome: amber glow with Lidar measurement sweep — result metrics float as
  holographic data cards.
  At Signal: confidence score animates as a floating holographic number with ray-traced
  glass surface — "+0.05" (green bioluminescent glow, rises and fades) for success,
  "-0.08" (red holographic glitch, sinks and dissipates) for failure.
  At Adaptation: strategy ranking table re-sorts in real-time with glassmorphism panels
  sliding and re-ordering — smooth ease-in-out motion with neon trail effects.
  The particle completes 3 full orbits — temporal evolution in action: Orbit 1 is dim
  with red undertones (early learning), Orbit 2 is amber (calibrating), Orbit 3 is
  bright green (mature confidence). Each orbit leaves a persistent bioluminescent
  trail on the track — three concentric light trails visible, newest brightest.
  Transformation timeline: red violation sparks are physically filtered out with each
  orbit — shed as dissipating ember particles — replaced by a steady green hum that
  intensifies with each rotation.

  **SCENE 4 — "The Compound Effect" (0:30–0:44)**
  Camera: Slow macro zoom out with orbital drift to reveal the wider architecture.
  Three dashboard panels materialize as frosted glassmorphism displays with ray-traced
  surfaces — each panel assembles with time-lapse mechanical construction:
  Transformation Timeline: Week 1 (dim red neon, low bioluminescence — holographic
  metrics float in muted tones), Week 4 (amber neon, warming glow — metrics brighten),
  Week 12 (green neon, full bioluminescent luminosity — metrics pulse with confidence).
  Camera slow dolly-in to Week 12 for emphasis, then pull-back.
  Below: Team A (green glassmorphism, fully lit), Team B (amber, warming), Team C
  (red/dim, just starting) — three node icons with a Shared Knowledge Base (gold #FFD700
  glassmorphism, aureate glow) at center. Bioluminescent arrows flow Team A → Shared KB
  → Team C — knowledge particles travel along ray-traced glass conduits, Team C's node
  brightens as particles arrive. Particle evolution: Team C's red glow begins transforming
  to amber as shared knowledge integrates.

  **SCENE 5 — "Orbital Reveal" (0:44–0:54)**
  Camera: 360-degree orbital pan at 30° downward angle with parallax depth around the
  complete URS architecture — circular orbit (inner), transformation timeline (middle),
  multi-team compound effect (outer). All three layers visible simultaneously with
  ray-traced reflections creating depth. Bioluminescent trails pulse on the orbital track.
  Team knowledge arrows continue flowing. Dashboard metrics continue their temporal
  evolution.
  Glassmorphism "Evidence Bundle" icon materializes center-frame — sealed document with
  cyan checkmark and holographic shimmer — fades to black.
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
