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

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame. CORTEX logo fades in with electric-aura glow. Hold 4s.
  Logo shrinks to bottom-right watermark.

  **SCENE 2 — "FPV Drone Dive: The Vertical Pipeline" (0:06–0:14)**
  Camera: FPV drone dives downward through volumetric fog. A vertical glass pipeline
  materializes — eleven frosted glassmorphism stage chambers stacked top-to-bottom,
  connected by luminous glass conduits. Ray-traced reflections ripple down the tower.

  **SCENE 3 — "The Audit Particle Descends" (0:14–0:32)**
  A bioluminescent cyan orb enters at "/audit fix." It descends through each stage,
  each chamber glowing green on pass. Stage 2 (19-Point Scan) is the HERO MOMENT —
  the chamber expands 3×, a scanning grid of 19 laser beams fans out, a violations
  HUD populates (red P0, amber P1, blue P2). Camera pauses here 4 seconds.

  **SCENE 4 — "The Convergence Loop" (0:32–0:46)**
  Camera: Tracks the particle entering the circular convergence track (amber neon).
  Iteration 1: counter shows 12 → 5. Iteration 2: 5 → 1. Iteration 3: 1 → 0 —
  GREEN EXPLOSION. Badge materializes: "p0 == 0 AND p1 == 0." Particle exits the loop.

  **SCENE 5 — "Test Gate & Completion" (0:46–0:52)**
  Stage 9 glows green. Hundreds of tiny orbs race through (parallel test execution).
  AC_COMPLETE badge materializes. The entire vertical pipeline illuminates top-to-bottom.

  **SCENE 6 — "Orbital Reveal" (0:52–1:00)**
  Camera: 360-degree orbital pan. All stages green. Bioluminescent audit trail persists.
  Glassmorphism "Evidence Bundle" icon materializes — sealed document with cyan checkmark
  — fades to black.
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
