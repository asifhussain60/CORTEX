---
id: 04-d-audit-pipeline-stages
title: 9-Stage Audit Pipeline — Production Readiness
purpose: Visualizes the complete /audit fix pipeline with convergence loop — VIDEO 04 hero diagram
audience: [Software Engineers, DevOps, Tech Leads]
source_of_truth: cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml
last_verified: 2026-02-27
diagram_type: Flowchart
interactive: false
tier: 2
learning_sequence: 26
video_prompt: 04-p-architectural-integrity.md
video_scene: "Scene 2 — The 9-Stage Pipeline (the entire vertical pipeline with convergence loop)"
animation_notes: |
  ## Cinematic Simulation Prompt — 04: 9-Stage Audit Pipeline

  ### Visual Physics & Ambience Protocol
  - **Environment:** Dark-blue vacuum (#0a0e27) with ray-traced reflections on glass conduits
  - **Pipeline:** Vertical glassmorphism tower — frosted chambers connected by luminous glass tubes
  - **Lighting:** Volumetric fog, ray-traced light caustics on conduit walls, internal neon glow per stage
  - **Convergence loop:** Amber neon circular track with counter HUD, green explosion at zero
  - **Feedback cues:** Green flash = stage passed, red P0 badges with holographic glitch, Lidar fan = scan grid

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame, locked on ray-traced glassmorphism floor.
  Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric fog at ground level.
  CORTEX logo (cortex-logo.png) fades in as large central hero image with electric-aura
  glow — cyan (#00d4ff) pulse radiates outward in concentric rings. Ray-traced
  reflections shimmer on the glass floor. Hold 4s.
  Logo shrinks to bottom-right watermark (15% opacity) with ease-out parallax slide.

  **SCENE 2 — "FPV Drone Dive: The Vertical Pipeline" (0:06–0:14)**
  Camera: FPV drone dives downward at terminal velocity through volumetric fog — each
  fog layer parts with parallax depth separation, peripheral motion blur intensifies.
  A vertical glass pipeline materializes from the mist with time-lapse mechanical
  assembly — eleven frosted glassmorphism stage chambers stack top-to-bottom, each
  sealing into place with magnetic iris animation. Luminous glass conduits connect
  chambers with internal neon filaments pulsing cyan. Ray-traced reflections ripple
  down the tower surface — each chamber catches and refracts light from its neighbors.

  **SCENE 3 — "The Audit Particle Descends" (0:14–0:32)**
  Camera: Tracking dolly follows the particle with slight parallax against the pipeline.
  A bioluminescent cyan orb enters at "/audit fix" with a particle condensation animation
  — micro-particles from the fog converge and solidify into the orb. It descends through
  each stage — each chamber's internal neon ignites green on successful passage, ray-traced
  green caustics bloom on adjacent conduit walls.
  Stage 2 (19-Point Production Scan) is the HERO MOMENT — the chamber expands 3× with
  a macro zoom camera push. A scanning grid of 19 Lidar laser beams fans out in a
  holographic display, each beam sweeping across a code visualization. A violations HUD
  populates with holographic text: red P0 badges pulse with holographic glitch effect,
  amber P1 badges glow steady, blue P2 badges dim. Camera holds here 4 seconds with
  strategic silence. Ray-traced light from the scanning grid casts moving shadows through
  the frosted glass.

  **SCENE 4 — "The Convergence Loop" (0:32–0:46)**
  Camera: Slow orbital tracking follows the particle entering the circular convergence
  track — a glassmorphism ring with amber neon filaments, hovering in the vacuum with
  volumetric fog drifting through its center.
  Transformation timeline: the particle orbits the loop, and with each rotation, red
  violation sparks are physically filtered out — shed as dissipating ember particles that
  fall away into the fog. The orb grows progressively greener.
  Iteration 1: holographic counter shows 12 → 5 (red sparks shed, amber glow).
  Iteration 2: counter 5 → 1 (fewer sparks, green emerging).
  Iteration 3: counter 1 → 0 — GREEN EXPLOSION with volumetric light burst, bioluminescent
  shockwave radiates outward. Badge materializes in glassmorphism: "p0 == 0 AND p1 == 0"
  with green pulse confirmation. Particle exits the loop with a steady green hum.

  **SCENE 5 — "Test Gate & Completion" (0:46–0:52)**
  Camera: Slow dolly-in to Stage 9. The chamber glows green with internal bioluminescence.
  Hundreds of tiny cyan orbs race through the chamber — a particle storm representing
  parallel test execution with ray-traced trails creating a web of light. Orbs converge
  into a single green orb. AC_COMPLETE badge materializes with holographic shimmer.
  Camera pulls back — the entire vertical pipeline illuminates top-to-bottom in a cascade
  of green neon, each stage igniting sequentially like a standing wave.

  **SCENE 6 — "Orbital Reveal" (0:52–1:00)**
  Camera: 360-degree orbital pan at 30° downward angle with parallax depth — the pipeline
  tower rotates against volumetric fog backdrop. All stages glow green with ray-traced
  reflections. Bioluminescent audit trail persists as a permanent vertical light column.
  Glassmorphism "Evidence Bundle" icon materializes center-frame — sealed document with
  cyan checkmark and holographic shimmer — fades to black.
related_diagrams:
  - 02-d-governance-tdd-enforcement-flow.md
  - 03-d-golden-test-pyramid-and-security-layers.md
---

## 9-Stage Audit Pipeline — `/audit fix`

### Main Pipeline

```
  ┌──────────────────────────────────────────────────────────────┐
  │                                                              │
  │   /audit fix  ◄─── single command triggers full pipeline    │
  │        │                                                     │
  │        ▼                                                     │
  │  ┌───────────────────────────────────────────────────────┐   │
  │  │  Stage -1  │  Environment Readiness                   │   │
  │  │            │  validate_requirements() preflight       │   │
  │  └─────────────────────────────┬─────────────────────────┘   │
  │                                ▼                             │
  │  ┌───────────────────────────────────────────────────────┐   │
  │  │  Stage  0  │  Inflight Upgrade + Pre-Flight           │   │
  │  │            │  git fetch origin/main, merge check      │   │
  │  └─────────────────────────────┬─────────────────────────┘   │
  │                                ▼                             │
  │  ┌───────────────────────────────────────────────────────┐   │
  │  │  Stage  1  │  Governance Pre-Flight                   │   │
  │  │            │  STAGE-0-GOVERNANCE-AUDIT-SPEC full spec  │   │
  │  └─────────────────────────────┬─────────────────────────┘   │
  │                                ▼                             │
  │  ┌───────────────────────────────────────────────────────┐   │
  │  │  Stage  2  │  ★ 19-Point Production Scan ★            │   │
  │  │            │  Checks #1–#19, incl. SQLite health      │   │
  │  │            │  P0 (critical) / P1 (high) / P2 (medium) │   │
  │  └─────────────────────────────┬─────────────────────────┘   │
  │                                ▼                             │
  │  ┌───────────────────────────────────────────────────────┐   │
  │  │  Stage  3  │  Wiring Contract Validation              │   │
  │  │            │  architecture-integrity-agent L1→L3      │   │
  │  └─────────────────────────────┬─────────────────────────┘   │
  │                                ▼                             │
  │  ┌───────────────────────────────────────────────────────┐   │
  │  │  Stage  4  │  Orchestrator Health (22 checked)        │   │
  │  │            │  HealthOrchestrator.run_health_check()   │   │
  │  └─────────────────────────────┬─────────────────────────┘   │
  │                                ▼                             │
  │  ┌───────────────────────────────────────────────────────┐   │
  │  │  Stage  5  │  Vacuum Cleanup                          │   │
  │  │            │  VacuumOrchestrator + cortex_vacuum      │   │
  │  └─────────────────────────────┬─────────────────────────┘   │
  │                                ▼                             │
  │  ┌───────────────────────────────────────────────────────┐   │
  │  │  Stage  6  │  Prompt/Agent Meta-Audit                 │   │
  │  │            │  cortex-meta-auditor.md, 23 checks       │   │
  │  └─────────────────────────────┬─────────────────────────┘   │
  │                                ▼                             │
  │  ┌───────────────────────────────────────────────────────┐   │
  │  │  Stages 7-8│  ★ Convergence Loop ★                   │   │
  │  │  (circular)│  detect-fix-rescan until P0=0 AND P1=0   │   │
  │  └─────────────────────────────┬─────────────────────────┘   │
  │                                ▼                             │
  │  ┌───────────────────────────────────────────────────────┐   │
  │  │  Stage  9  │  Tests + AC_COMPLETE                     │   │
  │  │            │  run_tests.py preflight → SQLite cleanup  │   │
  │  └─────────────────────────────┬─────────────────────────┘   │
  │                                ▼                             │
  │                        Production Ready ✅                   │
  └──────────────────────────────────────────────────────────────┘
```

### Convergence Loop Detail (Stages 7–8)

```
  Enter loop
      │
      ▼
  ┌──────────────────────────────────┐
  │  Detect violations               │
  │  P0 count + P1 count             │
  └────────────┬─────────────────────┘
               │
    ┌──────────┴───────────┐
    │ P0 > 0 OR P1 > 0?    │
    └──────────┬───────────┘
               │ YES                        NO
               ▼                            │
    ┌──────────────────────┐                ▼
    │  Auto-Fix Violations │         Exit loop ──► Stage 9
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Re-Scan             │
    └──────────┬───────────┘
               │
               └────────────────────────────► (loop back to detect)

  Iteration 1: 12 violations → 5
  Iteration 2:  5 violations → 1
  Iteration 3:  1 violation  → 0  ✅  exit
```

### Audit Trail (SQLite)

```
  .cortex-runtime/traces/orchestrator-traces.db
  ┌────────────────────────────────────────────┐
  │  audit_sessions    — 1 row per run         │
  │  audit_stage_log   — 1 row per stage       │
  │  audit_violations  — 1 row per violation   │
  │  workflow_cycles   — 1 row per loop iter.  │
  │  workflow_runs     — 1 row per invocation  │
  └────────────────────────────────────────────┘
  Stage 9 → SQLite log  ·····►  30-day retention + VACUUM
  Each loop cycle       ·····►  audit_violations (pattern detection)
```
