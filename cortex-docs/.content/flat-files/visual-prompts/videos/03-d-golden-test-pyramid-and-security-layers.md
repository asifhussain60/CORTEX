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

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame. CORTEX logo fades in with electric-aura glow. Hold 4s.
  Logo shrinks to bottom-right watermark.

  **SCENE 2 — "FPV Drone Dive: The Golden Pyramid" (0:06–0:22)**
  Camera: FPV drone dives into a three-tier glassmorphism pyramid. Base (Standard Tests):
  gray neon filaments. Middle (Promoted): amber filaments. Apex (Golden): GOLD neon
  filaments casting warm aureate glow. A bioluminescent test orb ascends through 5 quality
  gate gauges (Determinism, Coverage, Independence, Speed, Diagnostic Value), ascending to
  Golden tier with a gold shimmer trail. Flaky test scenario: golden orb drops back to
  Standard tier (glass dims from gold to gray).

  **SCENE 3 — "The Five Security Rings" (0:22–0:38)**
  Camera: Pans to five concentric glassmorphism rings. Ring 1 (Pre-Commit): red filaments.
  Ring 2 (Governance): amber filaments. Ring 3 (LENS): cyan filaments with laser sweep.
  Ring 4 (Vulnerability Orchestration): purple filaments. Ring 5 (Release Gate): green
  filaments. A code particle enters from center, bounces off Ring 1 (secret detected),
  reforms with fix, passes each ring via iris animation, exits with green corona.

  **SCENE 4 — "Unified Architecture" (0:38–0:48)**
  Camera: Wide pull-back. Pyramid (left) and Security Rings (right) visible. A glassmorphism
  bridge — the Governance Engine (purple) — connects both structures. SDLC Timeline renders
  as a horizontal bar at bottom: Coding → Commit → Analysis → Planning → Deploy.

  **SCENE 5 — "Orbital Reveal" (0:48–0:58)**
  Camera: 360-degree orbital pan. Golden tests glow with aureate luminosity. Security rings
  pulse in sequence. Glassmorphism "Evidence Bundle" icon materializes — sealed document
  with cyan checkmark — fades to black.
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
