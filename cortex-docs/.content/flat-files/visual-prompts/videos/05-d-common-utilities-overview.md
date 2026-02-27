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

  ### Visual Physics & Ambience Protocol
  - **Environment:** Dark-blue vacuum (#0a0e27) with ray-traced reflections on glass bedrock surface
  - **Foundation blocks:** Frosted glassmorphism with cyan neon filaments — rock-solid, zero movement
  - **Extension points:** Purple/domain-colored neon filaments, dendrite growth animations
  - **Lighting:** Volumetric fog at bedrock level, bioluminescent dependency conduits, ray-traced caustics
  - **Feedback cues:** Lidar scan = validation, green pulse = confirmed dependency, dendrite growth = extension

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame, locked on ray-traced glassmorphism floor.
  Environment: Absolute dark-blue vacuum (#0a0e27) with dense volumetric fog at ground
  level — the fog represents the bedrock upon which everything is built.
  CORTEX logo (cortex-logo.png) fades in as large central hero image with electric-aura
  glow — cyan pulse radiates outward. Ray-traced reflections shimmer on the floor. Hold 4s.
  Logo shrinks to bottom-right watermark (15% opacity) with ease-out parallax slide.

  **SCENE 2 — "FPV Drone Dive: The Stable Core" (0:06–0:16)**
  Camera: FPV drone descends slowly through volumetric fog — a deliberate, measured descent
  (not terminal velocity — this is bedrock, stability, permanence). Fog parts with parallax
  depth as the drone approaches Tier 1 Foundation.
  Four frosted glassmorphism blocks materialize as bedrock with time-lapse geological
  formation — rising from the glass floor like tectonic plates assembling. Each block has
  internal cyan neon filaments pulsing in a slow, steady rhythm (heartbeat of stability):
  Validators (cyan), Exception Hierarchy (cyan), File Operations (cyan), Structured Logging
  (cyan). A Lidar laser sweep scans all four simultaneously — green flash confirmation
  on each block with ray-traced green caustics reflecting off adjacent blocks.
  Info-pill floats center in glassmorphism dark pill: "Extend, Don't Fork — this layer
  never changes." — text materializes with typewriter reveal.

  **SCENE 3 — "Extensions Grow Above" (0:16–0:30)**
  Camera: Slow dolly upward with parallax depth — foundation blocks remain rock-solid
  (zero movement, zero vibration) while the camera rises. Dependent modules materialize
  above with particle evolution animation — micro-particles condense from fog into solid
  frosted glass capsules: Models, Config, Storage, Infrastructure. Each capsule has
  purple neon filaments with internal bioluminescent glow.
  Dependency arrows render as bioluminescent conduit tubes growing organically from each
  capsule down to its foundation block — like neural dendrites extending and connecting.
  Ray-traced reflections of the conduit light play across the frosted glass surfaces of
  both source and target blocks. Each connection solidifies with a green pulse confirmation.

  **SCENE 4 — "Extension Points" (0:30–0:40)**
  Camera: Dolly pull-back with slow orbital drift to reveal the full architecture.
  Seven extension point capsules materialize in a semicircle above — each a frosted
  glassmorphism node with domain-specific neon color (matching V05 dendrite assignments).
  Dendrite-like neon connections grow outward from the stable core with organic growth
  animation — each dendrite extends, branches, and solidifies with ray-traced reflections.
  Foundation blocks remain rock-solid — zero movement — creating visual contrast: the
  immovable bedrock beneath the living, growing extensions above. Each dendrite pulses
  with bioluminescent data particles flowing outward.

  **SCENE 5 — "Orbital Reveal" (0:40–0:50)**
  Camera: 360-degree orbital pan at 25° downward angle with parallax depth — extension
  points rotate faster than the foundation blocks below (visual hierarchy: stable base,
  dynamic surface). Foundation blocks glow steady cyan with ray-traced reflections.
  Extension points pulse with varied domain colors, dendrite connections carrying
  bioluminescent particle streams.
  Glassmorphism "Evidence Bundle" icon materializes — sealed document with cyan checkmark
  and holographic shimmer — fades to black.
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
