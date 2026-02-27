---
id: 03-d-golden-test-pyramid-and-security-layers
title: Golden Test Pyramid + Five Security Layers
purpose: Shows golden test promotion/demotion lifecycle alongside five concentric security layers — VIDEO 03 hero diagram
audience: [Software Engineers, Security Engineers]
source_of_truth: cortex/testing/ + cortex/governance/
last_verified: 2026-02-27
diagram_type: Flowchart
interactive: false
tier: 3
learning_sequence: 27
video_prompt: 03-p-precision-reviews.md
video_scene: "Scene 2 — Golden Test Pyramid (promotion/demotion) + Scene 4 — Five Security Layers"
animation_notes: |
  ## Cinematic Simulation Prompt — 03: Golden Test Pyramid & Security Layers

  ### Visual Physics & Ambience Protocol
  - **Environment:** Dark-blue vacuum (#0a0e27) with ray-traced reflections on glass floors
  - **Golden elements:** Gold (#FFD700) neon filaments, aureate volumetric glow, gold particle effects
  - **Lighting:** Volumetric fog, bioluminescent trails, ray-traced caustics on glass ring surfaces
  - **Textures:** Frosted glassmorphism with per-layer color filaments (red→amber→cyan→purple→green)
  - **Feedback cues:** Gold shimmer = promotion, glass dims (gold→gray) = demotion, holographic glitch = violation

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame, locked on ray-traced glassmorphism floor.
  Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric gold-tinted fog.
  CORTEX logo (cortex-logo.png) fades in as large central hero image with electric-aura
  glow — gold (#FFD700) pulse replaces standard cyan for this video's identity.
  Ray-traced reflections of the gold aura shimmer on the glass floor. Hold 4s.
  Logo shrinks to bottom-right watermark with ease-out parallax slide.

  **SCENE 2 — "FPV Drone Dive: The Golden Pyramid" (0:06–0:22)**
  Camera: FPV drone dives at steep 60° through volumetric fog — fog layers part with
  parallax depth separation. A three-tier glassmorphism pyramid emerges from below with
  time-lapse mechanical construction — glass panels fold and lock into place.
  Base (Standard Tests): gray neon filaments, wide foundation, dim internal glow.
  Middle (Promoted): amber neon filaments, narrower, warming internal bioluminescence.
  Apex (Golden): GOLD (#FFD700) neon filaments casting warm aureate volumetric glow —
  ray-traced gold caustics dance on adjacent surfaces. Internal bioluminescent circuitry
  pulses like a living heartbeat.
  A bioluminescent test orb (initially gray) ascends through 5 quality gate gauges
  rendered as holographic radial indicators (Determinism, Coverage, Independence, Speed,
  Diagnostic Value) — each gauge fills with a Lidar scan sweep and green confirmation
  flash. As the orb passes each gate, it evolves: gray → amber → bright gold with a
  gold shimmer trail and particle wake.
  Flaky test scenario: a golden orb at the apex stutters with holographic glitch effect —
  surface cracks appear, gold neon dims. The orb drops back to Standard tier with a
  particle devolution — gold sparks shed and dissipate, glass dims from gold to gray.
  Strategic silence (1.5s) as the orb settles at the base.

  **SCENE 3 — "The Five Security Rings" (0:22–0:38)**
  Camera: Slow parallax pan with dolly-in to five concentric glassmorphism rings, each
  assembling with magnetic iris animation from the outermost inward.
  Ring 1 (Pre-Commit): red neon filaments with internal bioluminescent danger-pulse.
  Ring 2 (Governance): amber filaments with holographic rule-text floating on surface.
  Ring 3 (LENS): cyan filaments with a Lidar laser sweep orbiting the ring circumference.
  Ring 4 (Vulnerability Orchestration): purple filaments with ray-traced reflections.
  Ring 5 (Release Gate): green filaments with a steady bioluminescent hum.
  A code particle enters from center — strikes Ring 1 (secret detected), holographic
  glitch effect with red flash and particle fragmentation. Particle reforms with
  particle evolution animation (red sparks re-condense with a corrective green pulse).
  Passes each subsequent ring via iris animation — each ring's neon brightens on passage
  then dims to 40%. Final exit: particle emerges with a green corona glow and
  bioluminescent wake trail.

  **SCENE 4 — "Unified Architecture" (0:38–0:48)**
  Camera: Wide dolly pull-back with slow orbital drift revealing both structures.
  Pyramid (left) and Security Rings (right) visible simultaneously. A glassmorphism
  bridge — the Governance Engine (purple neon filaments) — assembles between both
  structures with time-lapse mechanical construction. Neon conduit tubes connect
  the bridge to both pyramid and rings, pulsing with data particles.
  SDLC Timeline renders as a horizontal glassmorphism bar at bottom with ray-traced
  surface: Coding → Commit → Analysis → Planning → Deploy. Each stage illuminates
  sequentially with cyan pulse propagation.

  **SCENE 5 — "Orbital Reveal" (0:48–0:58)**
  Camera: 360-degree orbital pan at 20° downward angle with parallax depth — pyramid
  rotates slower than rings, creating cinematic layering. Golden tests glow with aureate
  volumetric luminosity. Security rings pulse in sequence (red→amber→cyan→purple→green).
  Ray-traced reflections of both structures shimmer on the glass floor.
  Glassmorphism "Evidence Bundle" icon materializes — sealed document with cyan checkmark
  and holographic gold shimmer — fades to black.
related_diagrams:
  - 02-d-governance-tdd-enforcement-flow.md
  - 04-d-audit-pipeline-stages.md
---

## Golden Test Pyramid + Five Security Layers

### Part A — Golden Test Pyramid

```
                        /\
                       /  \
                      / ⭐ \
                     /GOLDEN\          ← Essential correctness
                    / TESTS  \           If broken = system wrong
                   /──────────\
                  /            \
                 / 🟡 PROMOTED  \      ← Critical path coverage
                /     TESTS      \       Architectural contracts
               /──────────────────\
              /                    \
             /  🔘 STANDARD TESTS   \  ← Regular unit tests
            /    Wide Foundation     \   Largest count
           /────────────────────────--\

  Promotion path:  Standard  ──[Score ≥ threshold]──►  Promoted  ──[Sustained pass]──►  Golden
  Demotion path:   Golden    ··[Flaky/intermittent]··►  Standard  (glass dims, trail fades)
```

### Quality Gate Dimensions (must pass all 5 to promote)

```
  ┌────────────────────────────────────────────────────────┐
  │  1. Determinism     — same result every run            │
  │  2. Coverage        — meaningful code paths covered    │
  │  3. Independence    — no shared state between tests    │
  │  4. Speed           — executes in < 2 seconds          │
  │  5. Diagnostic Value— failure points to the real bug   │
  └────────────────────────────────────────────────────────┘
```

### Part B — Five Security Layers

```
  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │   Code enters ──►  🔴 Layer 1: Pre-Commit               │
  │                         Secret scanning, blocked commits │
  │                         │                               │
  │                         ▼                               │
  │                    🟠 Layer 2: Governance Rules          │
  │                         No eval(), no deprecated crypto  │
  │                         │                               │
  │                         ▼                               │
  │                    🔵 Layer 3: LENS Security Scan        │
  │                         SQL injection, CVEs, input val.  │
  │                         Vulnerability badges: P0/P1/P2   │
  │                         │                               │
  │                         ▼                               │
  │                    🟣 Layer 4: Vulnerability Orchestration│
  │                         Aggregate, prioritize, auto-fix  │
  │                         │                               │
  │                         ▼                               │
  │                    🟢 Layer 5: Release Gate              │
  │                         Final security score threshold   │
  │                         │                               │
  │                         ▼                               │
  │                    Deploy ✅  (or block + fix)           │
  └──────────────────────────────────────────────────────────┘
```

### Part C — SDLC Timeline Mapping

```
  Coding ──► Commit ──► Analysis ──► Planning ──► Deploy
    │            │           │            │           │
    ▼            ▼           ▼            ▼           ▼
  Layer 1    Layer 2     Layer 3      Layer 4     Layer 5
 Pre-Commit  Gov Rules  LENS Scan    Vuln Orch  Release Gate
```

### Part D — Shared Infrastructure

```
  ┌──────────────────────────────────────────────┐
  │  Governance Engine  ──►  Golden Tests         │
  │  Governance Engine  ──►  Layer 2 (Gov Rules)  │
  │  Audit Trail        ──►  Golden Tests         │
  │  Audit Trail        ──►  Layer 5 (Gate log)   │
  │  Enforcement Pipeline connects both halves    │
  └──────────────────────────────────────────────┘
```
