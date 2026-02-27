---
id: 05-d-common-utilities-overview
title: Tier 1 Common Utilities Architecture — Foundation Layer
purpose: Shows the foundational utility modules all CORTEX components depend on — VIDEO 05 Scene 2 extension point context
audience: [Software Developers, Product Owners]
source_of_truth: cortex/common/__init__.py
last_verified: 2026-02-27
diagram_type: C4-Component
interactive: false
tier: 1
learning_sequence: 01
video_prompt: 05-p-the-collaborative-engine.md
video_scene: "Scene 2 — Extension Points (shows the stable foundation that extensions build on)"
animation_notes: |
  ## Cinematic Simulation Prompt — 05: Tier 1 Foundation Layer

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame. CORTEX logo fades in with electric-aura glow. Hold 4s.
  Logo shrinks to bottom-right watermark.

  **SCENE 2 — "FPV Drone Dive: The Stable Core" (0:06–0:16)**
  Camera: FPV drone descends to the lowest level — Tier 1 Foundation. Four frosted
  glassmorphism blocks materialize as bedrock: Validators (cyan neon), Exception Hierarchy
  (cyan), File Operations (cyan), Structured Logging (cyan). A Lidar laser sweep scans
  all four simultaneously. Info-pill floats center: "Extend, Don't Fork — this layer
  never changes."

  **SCENE 3 — "Extensions Grow Above" (0:16–0:30)**
  Camera: Slow dolly upward. Dependent modules materialize above — Models, Config, Storage,
  Infrastructure — each as a frosted glass capsule with purple neon filaments. Dependency
  arrows render as bioluminescent conduits connecting each down to its foundation block.

  **SCENE 4 — "Extension Points" (0:30–0:40)**
  Camera: Pulls back. Seven extension point capsules materialize in a semicircle above —
  each a frosted glass node. Dendrite-like neon connections grow outward from the stable
  core. Foundation blocks remain rock-solid — no movement — while extensions animate above.

  **SCENE 5 — "Orbital Reveal" (0:40–0:50)**
  Camera: 360-degree orbital pan. Foundation blocks glow steady cyan. Extension points
  pulse with varied domain colors. Glassmorphism "Evidence Bundle" icon materializes
  — sealed document with cyan checkmark — fades to black.
related_diagrams:
  - 01-d-c4-container-full-system.md
  - 07-d-orchestrator-dispatch-flow.md
---

## Tier 1 Common Utilities — Foundation Layer

### The Stable Bedrock

```
  ┌──────────────────────────────────────────────────────────────────┐
  │                  TIER 1 FOUNDATION — Never Changes               │
  │                  "Extend, Don't Fork"                            │
  │                                                                  │
  │  ┌──────────────────┐  ┌──────────────────┐                      │
  │  │   Validators     │  │Exception Hierarchy│                      │
  │  │                  │  │                  │                      │
  │  │ · Schema checks  │  │ · CortexError    │                      │
  │  │ · Type checking  │  │ · ValidationError│                      │
  │  │ · Input guards   │  │ · BaseException  │                      │
  │  └──────────────────┘  └──────────────────┘                      │
  │                                                                  │
  │  ┌──────────────────┐  ┌──────────────────┐                      │
  │  │ File Operations  │  │ Structured Logging│                      │
  │  │                  │  │                  │                      │
  │  │ · Safe I/O       │  │ · Correlation IDs│                      │
  │  │ · Path abstracts │  │ · Context prop.  │                      │
  │  │ · Atomic writes  │  │ · Structured JSON│                      │
  │  └──────────────────┘  └──────────────────┘                      │
  └──────────────────────────────────────────────────────────────────┘
```

### Dependency Graph — What Builds on the Foundation

```
                 ┌──────────┐  ┌──────────────┐
                 │ 02-Models│  │  03-Config   │
                 └────┬─────┘  └──────┬───────┘
                      │               │
   ┌──────────────────┴───────────────┴──────────────────┐
   │                                                      │
   │  Validators ──────────────────────────────────────►  Models
   │  Validators ──────────────────────────────────────►  Config
   │  Exception Hierarchy ─────────────────────────────►  Models
   │  Exception Hierarchy ─────────────────────────────►  Infrastructure
   │  File Operations  ────────────────────────────────►  Storage
   │  File Operations  ────────────────────────────────►  Config
   │  Structured Logging ──────────────────────────────►  Infrastructure
   │                                                      │
   └──────────────────────────────────────────────────────┘

             ┌─────────────┐  ┌──────────────────┐
             │ 04-Storage  │  │ 08-Infrastructure │
             └─────────────┘  └──────────────────┘
```

### Extension Points — What You Can Add Without Touching the Core

```
                    ┌────────────────────────────┐
                    │      STABLE CORE (Tier 1)  │
                    └────────────┬───────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │          │           │           │           │
          ▼          ▼           ▼           ▼           ▼
    MCP Tools  Orchestrators  Governance  Workflows  Knowledge
    (extend)   (extend)       (extend)    (extend)   (extend)
                    │                         │
                    ▼                         ▼
            Company Overrides          Patterns Registry
            (override)                 (register)

  Rule: add capabilities ABOVE the foundation — never modify Tier 1
```
