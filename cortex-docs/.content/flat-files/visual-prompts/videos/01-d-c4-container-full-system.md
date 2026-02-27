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

  ### Visual Physics & Ambience Protocol
  - **Environment:** Dark-blue vacuum (#0a0e27) with ray-traced reflections on glass floors
  - **Data flows:** Cyan neon filaments (#00d4ff) for primary paths, purple (#7b61ff) for connections
  - **Lighting:** Volumetric fog at floor level, bioluminescent particle trails, internal neon glow on glass blocks
  - **Textures:** Frosted glassmorphism (backdrop-blur 10-20px) with 1px border `rgba(255,255,255,0.1)`
  - **Feedback cues:** Green flash = confirmed/healthy, holographic glitch = error, Lidar scan = validation sweep

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame, locked on a ray-traced glassmorphism floor.
  Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric blue fog drifting at ground level.
  A high-resolution CORTEX logo (cortex-logo.png) fades in, centered — large hero scale.
  An 'electric-aura' animation ignites — concentric cyan (#00d4ff) and purple (#7b61ff)
  pulse-glows radiate outward in concentric rings, casting volumetric light into the fog.
  Ray-traced reflections of the aura shimmer across the glass floor. Hold 4 seconds.
  Logo shrinks to bottom-right watermark (15% opacity) with an ease-out parallax slide.

  **SCENE 2 — "FPV Drone Dive: Foundation Layer" (0:06–0:14)**
  Camera: First-person FPV drone dive from 50m above, plunging downward through
  volumetric fog layers — each fog layer parts with parallax depth as the drone punches
  through. Terminal velocity feel — motion blur on peripheral fog particles.
  Tier 1 (Foundation) emerges from the mist below. Three frosted glassmorphism blocks
  materialize with a mechanical unfolding animation — Deep Cobalt with internal cyan
  neon filaments pulsing like living circuitry: "Common Utilities," "Data Models," "Storage Layer."
  A Lidar laser sweep scans left-to-right across all three blocks, each confirmed with
  a green flash and a subtle chime. Ray-traced reflections of the blocks ripple on the
  glass floor beneath them.

  **SCENE 3 — "Core Ignition" (0:14–0:22)**
  Camera: Slow dolly upward with slight parallax shift — foreground fog layers drift
  faster than background elements, creating depth. Tier 2 (Core) assembles on top of
  Tier 1 with a time-lapse mechanical construction animation — glass panels slide into
  place and seal with magnetic iris animations. MCP Gateway glows with purple neon
  filaments as the entry point — internal neon pulses rhythmically like a heartbeat.
  A bioluminescent request particle (cyan orb, ~15px diameter) enters at MCP Gateway
  and pauses, casting volumetric light into surrounding fog — light rays penetrate the
  frosted glass, revealing internal structure.

  **SCENE 4 — "Intelligence Awakens" (0:22–0:32)**
  Camera: Continues rising with a slow barrel roll (15°) to add cinematic dynamism.
  Tier 3 (Intelligence) materializes with particle evolution — thousands of micro-particles
  condense from fog into solid glassmorphism blocks: Brain, LENS Analyzers, Orchestrators,
  Learning Loop. The request particle ascends from MCP Gateway into the Orchestrator node,
  splits into three tracer beams (Brain = cyan, LENS = purple, Governance = amber), each
  beam leaving a persistent bioluminescent trail with ray-traced reflections on adjacent
  surfaces. Beams reconverge at the Orchestrator with a brief light burst.

  **SCENE 5 — "Infrastructure Crown" (0:32–0:40)**
  Camera: Final macro zoom ascent — camera close to glass surfaces showing ray-traced
  reflections and internal neon filament detail, then pulls back to reveal the full tower.
  Tier 4 (Infrastructure) caps the stack — API, CLI, Deploy — each block sealing into
  place with a magnetic iris animation. The full 4-tier tower is now visible.
  The request particle completes its full vertical journey — a bright cyan streak from
  User → MCP → Orchestrator → Brain → Storage and back, leaving a persistent
  bioluminescent trail that pulses once as a standing wave when the circuit completes.

  **SCENE 6 — "Orbital Reveal" (0:40–0:50)**
  Camera: 360-degree orbital pan around the complete 4-tier architecture at a 30° downward
  angle, maintaining parallax depth — nearer tiers move faster than distant ones. All tiers
  glow at full luminosity with ray-traced reflections shimmering on the glass floor.
  Volumetric fog swirls gently at the base. Camera completes the orbit and slowly pulls
  back with a dolly-out. The architecture fades to 40% opacity. A glassmorphism
  "Evidence Bundle" icon materializes center-frame — a sealed document with a cyan
  checkmark and subtle holographic shimmer — then fades to black.
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
