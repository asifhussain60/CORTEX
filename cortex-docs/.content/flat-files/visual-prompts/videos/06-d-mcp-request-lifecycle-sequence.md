---
id: 06-d-mcp-request-lifecycle-sequence
title: MCP Request Lifecycle — Full Sequence
purpose: Illustrates the complete flow of an MCP tool request from gateway to execution — VIDEO 06 hero diagram
audience: [Software Developers, Product Owners]
source_of_truth: cortex/mcp/__wiring_contract__.yaml
last_verified: 2026-02-27
diagram_type: Sequence
interactive: false
tier: 2
learning_sequence: 19
video_prompt: 06-p-traceability-and-transparency.md
video_scene: "Scene 2–4 — The Request Particle tracks this exact sequence"
animation_notes: |
  ## Cinematic Simulation Prompt — 06: MCP Request Lifecycle

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame. CORTEX logo fades in with electric-aura glow. Hold 4s.
  Logo shrinks to bottom-right watermark.

  **SCENE 2 — "FPV Drone Dive: The Gateway" (0:06–0:12)**
  Camera: FPV drone swoops into a horizontal glass corridor — six frosted glassmorphism
  participant stations arranged left-to-right: Client, MCP Gateway, Intent Router, Master
  Orchestrator, MCP Tool, Governance Engine. Purple filaments for Gateway and Orchestrator,
  cyan for Router and Tool.

  **SCENE 3 — "The Request Particle's Journey" (0:12–0:32)**
  A bioluminescent cyan orb spawns at Client, 2-second pause per station with volumetric
  light bloom. At Governance: shield flash green (approved ✅). At Tool: spinner animation,
  result emerges as a green-tinted orb. Each station's activation bar glows on arrival.

  **SCENE 4 — "The Return Path" (0:32–0:42)**
  Result particle reverses right-to-left. Each station dims to 40% after particle passes.
  Particle arrives at Client and expands into a delivered response card. Latency badge
  fades in: "50–150ms typical."

  **SCENE 5 — "Orbital Reveal" (0:42–0:50)**
  Camera: 360-degree orbital pan around the horizontal request corridor. All six stations
  glow at full luminosity. Bioluminescent trail persists. Glassmorphism "Evidence Bundle"
  icon materializes — sealed document with cyan checkmark — fades to black.
related_diagrams:
  - 01-d-c4-container-full-system.md
  - 07-d-orchestrator-dispatch-flow.md
---

## MCP Request Lifecycle — Full Sequence

### Request Flow (left → right)

```
  Client        MCP Gateway     Intent Router   Master Orch.    MCP Tool    Governance
    │                │                │               │              │            │
    │  JSON-RPC Req  │                │               │              │            │
    │───────────────►│                │               │              │            │
    │                │                │               │              │            │
    │                │ Validate Proto │               │              │            │
    │                │◄──────────────►│               │              │            │
    │                │                │               │              │            │
    │                │  Route Intent  │               │              │            │
    │                │───────────────►│               │              │            │
    │                │                │               │              │            │
    │                │                │ Classify +    │              │            │
    │                │                │ Dispatch      │              │            │
    │                │                │──────────────►│              │            │
    │                │                │               │              │            │
    │                │                │               │ Check Gov.   │            │
    │                │                │               │─────────────────────────►│
    │                │                │               │              │            │
    │                │                │               │   ✅ Approved│            │
    │                │                │               │◄─────────────────────────│
    │                │                │               │              │            │
    │                │                │               │  Execute Tool│            │
    │                │                │               │─────────────►│            │
    │                │                │               │              │            │
    │                │                │               │    Result    │            │
    │                │                │               │◄─────────────│            │
    │                │                │               │              │            │
    │                │   Response     │               │              │            │
    │                │◄──────────────────────────────│              │            │
    │                │                │               │              │            │
    │ JSON-RPC Resp  │                │               │              │            │
    │◄───────────────│                │               │              │            │
    │                │                │               │              │            │

  Typical latency: 50–150ms end-to-end
```

### Governance Decision Paths

```
  Governance Engine receives request
          │
          ▼
  ┌──────────────────────────────┐
  │  Check 38 CORE Rules         │
  │  + validate context          │
  └──────────┬───────────────────┘
             │
      ┌──────┴───────┐
      │              │
   APPROVED        REJECTED
      │              │
      ▼              ▼
  Continue      Return error
  to Tool       to Orchestrator
                (logged to SQLite)
```

### Participant Roles

```
  ┌────────────────────┬──────────────────────────────────────────────┐
  │ Client             │ VS Code + Copilot Chat — initiates request    │
  │ MCP Gateway        │ JSON-RPC entry point, protocol validation     │
  │ Intent Router      │ Classifies request, selects orchestrator type │
  │ Master Orchestrator│ Coordinates execution, owns lifecycle         │
  │ Governance Engine  │ Enforces 38 CORE rules before any action      │
  │ MCP Tool           │ Performs the actual operation (29 tools)      │
  └────────────────────┴──────────────────────────────────────────────┘
```
