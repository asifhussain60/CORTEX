---
id: 01-d-c4-container-full-system
title: CORTEX System Architecture (C4 Container Level)
purpose: High-level view of major runtime components — VIDEO 01 primary architecture diagram
audience: [Business Leaders, Product Owners, Software Developers]
source_of_truth: cortex-registry/master/__wiring_contract__.yaml
last_verified: 2026-02-27
diagram_type: C4-Container
interactive: false
tier: all
learning_sequence: 00
video_prompt: 01-p-the-cortex-paradigm.md
video_scene: "Scene 3 — The Architecture (animate tier-by-tier, bottom→top)"
animation_notes: |
  ## Cinematic Simulation Prompt — 01: Full System Architecture

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame. Environment: Absolute dark-blue vacuum (#0a0e27).
  A high-resolution CORTEX logo fades in, centered on a ray-traced glassmorphism floor.
  An 'electric-aura' animation ignites — concentric cyan (#00d4ff) and purple (#7b61ff)
  pulse-glows radiate outward. Volumetric blue fog drifts at floor level. Hold 4 seconds.
  Logo shrinks to bottom-right watermark (15% opacity).

  **SCENE 2 — "FPV Drone Dive: Foundation Layer" (0:06–0:14)**
  Camera: First-person drone dive from above, plunging downward through volumetric fog
  into Tier 1 (Foundation). Three frosted glassmorphism blocks materialize — Deep Cobalt
  with cyan neon filaments: "Common Utilities," "Data Models," "Storage Layer."
  A Lidar laser sweep scans left-to-right, confirming each block with a green flash.

  **SCENE 3 — "Core Ignition" (0:14–0:22)**
  Camera: Slow dolly upward. Tier 2 (Core) assembles on top of Tier 1. MCP Gateway
  glows with purple neon filaments as the entry point. A bioluminescent request particle
  (cyan orb) enters at MCP Gateway and pauses, casting volumetric light into surrounding fog.

  **SCENE 4 — "Intelligence Awakens" (0:22–0:32)**
  Camera: Continues rising. Tier 3 (Intelligence) materializes — Brain, LENS Analyzers,
  Orchestrators, Learning Loop. The request particle ascends from MCP Gateway into the
  Orchestrator node, splits into three tracer beams (Brain, LENS, Governance), then
  reconverges. Bioluminescent trail persists behind each path.

  **SCENE 5 — "Infrastructure Crown" (0:32–0:40)**
  Camera: Final ascent. Tier 4 (Infrastructure) caps the stack — API, CLI, Deploy.
  The full 4-tier tower is now visible. The request particle completes its full vertical
  journey — a bright cyan streak from User → MCP → Orchestrator → Brain → Storage and
  back, leaving a persistent bioluminescent trail.

  **SCENE 6 — "Orbital Reveal" (0:40–0:50)**
  Camera: 360-degree orbital pan around the complete 4-tier architecture. All tiers glow
  at full luminosity. Camera completes the orbit and slowly pulls back. The architecture
  fades to 40% opacity. A glassmorphism "Evidence Bundle" icon materializes center-frame
  — a sealed document with a cyan checkmark — then fades to black.
related_diagrams:
  - 06-d-mcp-request-lifecycle-sequence.md
  - 07-d-orchestrator-dispatch-flow.md
  - 05-d-common-utilities-overview.md
---

## CORTEX System Architecture — C4 Container Level

```
┌─────────────────────────────────────────────────────────┐
│                       EXTERNAL                          │
│                                                         │
│   ┌─────────────────┐        ┌──────────────────┐       │
│   │  User / IDE     │        │  Git Repositories│       │
│   │  VS Code Copilot│        │                  │       │
│   └────────┬────────┘        └────────┬─────────┘       │
└────────────┼─────────────────────────┼─────────────────-┘
             │ JSON-RPC                │
┌────────────▼─────────────────────────────────────────────┐
│                    CORTEX SYSTEM                         │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Tier 4: Infrastructure                 │ │
│  │  ┌───────────┐   ┌───────────┐   ┌───────────────┐ │ │
│  │  │ REST API  │   │ CLI Tools │   │  Deployment   │ │ │
│  │  │ (FastAPI) │   │ (Python)  │   │ (Kubernetes)  │ │ │
│  │  └─────┬─────┘   └─────┬─────┘   └───────┬───────┘ │ │
│  └────────┼───────────────┼─────────────────┼─────────┘ │
│           │               │                 │            │
│  ┌────────▼───────────────▼─────────────────▼─────────┐ │
│  │              Tier 3: Intelligence                   │ │
│  │  ┌──────────┐ ┌────────────┐ ┌──────────────────┐  │ │
│  │  │  CORTEX  │ │   LENS     │ │  Orchestrators   │  │ │
│  │  │  Brain   │ │ Analyzers  │ │   (51 Total)     │  │ │
│  │  │ Intel Hub│ │ (15 comps) │ │                  │  │ │
│  │  └────┬─────┘ └────────────┘ └──────────────────┘  │ │
│  │       │          ┌───────────────────────────────┐  │ │
│  │       │          │   Learning Loop               │  │ │
│  │       │          │   Pattern Extraction          │  │ │
│  │       │          └───────────────────────────────┘  │ │
│  └───────┼─────────────────────────────────────────────┘ │
│          │                                                │
│  ┌───────▼───────────────────────────────────────────--┐ │
│  │              Tier 2: Core                           │ │
│  │  ┌──────────────┐ ┌─────────────┐ ┌─────────────┐  │ │
│  │  │ MCP Gateway  │ │   CORTEX    │ │  Governance │  │ │
│  │  │  (JSON-RPC)  │ │  Registry   │ │   Engine    │  │ │
│  │  │ ◄── ENTRY ──►│ │(Git YAML)   │ │  (7 Agents) │  │ │
│  │  └──────────────┘ └─────────────┘ └─────────────┘  │ │
│  └─────────────────────────────────────────────────----┘ │
│                                                          │
│  ┌───────────────────────────────────────────────────--┐ │
│  │              Tier 1: Foundation                     │ │
│  │  ┌──────────────┐ ┌─────────────┐ ┌─────────────┐  │ │
│  │  │Common Utils  │ │ Data Models │ │Storage Layer│  │ │
│  │  │  (Python)    │ │  (Py/YAML)  │ │(SQLite/File)│  │ │
│  │  └──────────────┘ └─────────────┘ └─────────────┘  │ │
│  └─────────────────────────────────────────────────----┘ │
└──────────────────────────────────────────────────────────┘
```

### Data Flow

```
User/IDE  ──JSON-RPC──►  MCP Gateway  ──►  Orchestrators  ──►  Brain
                                                 │                │
                                                 ▼                ▼
                                           Governance        Registry
                                                 │                │
                                                 ▼                ▼
                                          LENS ──►  Storage ◄──  Learning Loop
                                                 ▲
                                                 │
                                           Git Repositories

API / CLI  ──────────►  Orchestrators
Deploy     ──────────►  API

All tiers  ··depends on··►  Common Utilities (Tier 1)
```

### Tier Summary

| Tier | Components | Role |
|------|-----------|------|
| **Tier 1 — Foundation** | Common Utils, Data Models, Storage | Immutable bedrock; never changes |
| **Tier 2 — Core** | MCP Gateway, Registry, Governance | Entry point and rule enforcement |
| **Tier 3 — Intelligence** | Brain, LENS, Orchestrators, Learning | Routing, analysis, adaptation |
| **Tier 4 — Infrastructure** | REST API, CLI, Kubernetes | Deployment and external access |
