# NotebookLM Video Prompt — 03 — How CORTEX Works: Architecture Tour (Technical Leaders)

**Target length:** 9–12 minutes
**Audience:** Staff Engineers, Architects, CTOs — people who need to understand the system before adopting it
**Narrator gender:** Female (Video 03 — odd, per VBP-017)
**Visual theme:** Dark-blue glassmorphism · Request-journey camera (moves with the data)
**Series position:** Architecture depth — the only video doing a full request-path walkthrough

---

## ⚠️ ZERO-OVERLAP DECLARATION
This video exclusively owns:
- The 4-stage pipeline internals (Interaction → Intent → Intelligence → Execution)
- The MCP stdio transport model and how it auto-configures in VS Code
- LENS Analysis mechanics (Language → Examination → Navigation → Synthesis)
- Workflow template engine and primitive composition

Does NOT repeat: business identity (Video 01), lane comparison (Video 02), TDD loop details (SE Video 01), MCP tool catalogue (SE Video 02).

---

## Steering Prompt
*Paste into NotebookLM → Customize → Steering Prompt:*

> "Create a 9–12 minute architecture walkthrough for staff engineers and technical leads. Trace a single request from the developer's chat message through Stage 0 governance audit, intent routing (28 intent types), LENS context gathering (Language → Examination → Navigation → Synthesis), workflow template execution, and convergence validation. Define every technical term on first use. Tone: senior architect delivering an internal design review — measured, exact, non-promotional. Use only the provided sources."

---

## Ground-truth constraints
- Single canonical Python package: `cortex.*`
- MCP server: Pylance-style stdio transport, auto-starts when VS Code opens the workspace (`.vscode/settings.json`)
- 4-stage pipeline: Interaction → Intent → Intelligence → Execution
- 28 intent types routed via IntentRouter (`cortex/orchestrators/core/intent_router.py`)
- LENS: 8 analyzers — Language → Examination → Navigation → Synthesis
- Workflow templates: YAML registry at `cortex-registry/workflows/templates/` — composed from primitives
- All runtime data: `.cortex-runtime/` (SQLite traces, logs — never sidebar paths)

---

## Visual ingredients
Upload as PNG/JPG:
1. `cortex-docs/assets/diagrams/02-architecture-mcp-gateway-architecture.md` — MCP transport (Scene 1)
2. `cortex-docs/assets/diagrams/08-architecture-package-and-directory-map.md` — package map (Scene 2)
3. `cortex-docs/assets/diagrams/09-orchestration-request-sequence.md` — request sequence (Scene 3)
4. `cortex-docs/assets/diagrams/10-workflow-template-engine.md` — template engine (Scene 4)

**Cinematic treatment — "Request journey" camera:**
The camera IS the request. It travels with the data from VS Code → MCP gateway → IntentRouter → LENS → orchestrator → output. Each architectural node the request enters becomes the focal point, with surrounding nodes dimming (VBP-009 signaling). This is the defining visual motif of this video — not used in any other video.

---

## Scene-by-scene breakdown

**SCENE 1 — "The Request Enters" [0:00–2:00]**
Visual: Developer types `/audit fix` in VS Code Copilot Chat. The message text lifts off the screen as a glowing cyan particle packet.
The MCP gateway diagram materialises — the packet travels the stdio transport pipe. Lower-third: `"Pylance-style stdio transport — no manual server startup"`
Camera (the request POV): approaches the MCP gateway node. The node illuminates. Gateway routes to Stage 0.
Stage 0 panel materialises: 3 governance checks flash green in sequence (MD file scope, TDD bypass, audit trail). Packet clears Stage 0 — gateway opens.
Narrator (female, architect-tone): *"Before any code is touched, every request passes a governance pre-flight. Stage 0 cannot be bypassed."*

**SCENE 2 — "Intent Routing" [2:00–3:30]**
Visual: IntentRouter node — 28 intent types fan out like a compass rose, each as a glassmorphic capsule. Camera zooms toward AUDIT intent as confidence score builds: 0.62 → 0.78 → 0.94.
Lower-third: `"28 intent types · Confidence threshold: 0.85 for direct route"`
The 27 other intents dim to 15% opacity. AUDIT capsule brightens to full cyan.
Narrator: *"The IntentRouter doesn't guess. It builds confidence from the request semantics. At 0.85 or above, it routes directly. Below that threshold, it asks for clarification."*
Orchestrator selection card materialises: `AuditCoordinator — cortex/orchestrators/core/`

**SCENE 3 — "LENS Analysis" [3:30–6:00]**
Visual: The LENS eye diagram animates — four concentric iris rings, each labeled one at a time:
  Ring 1 — Language: file type detection, Python AST parse, syntax map
  Ring 2 — Examination: complexity analysis, dependency graph, pattern scoring
  Ring 3 — Navigation: cross-file reference tracing, orchestrator routing map
  Ring 4 — Synthesis: context package assembled, confidence scores attached
Camera: slow spiral inward through the iris as each ring activates. The pupil centre is where the synthesised context "compiles" — a holographic context card assembles there.
Lower-third: `"LENS — 8 analyzers · Targeted tier: <2 seconds"`
Narrator: *"LENS doesn't read the whole codebase every time. It reads exactly what the current request needs — no more, no less. The result is a precision context package, not a noise dump."*
The assembled context card drifts from the LENS eye to the workflow engine.

**SCENE 4 — "Workflow Template Execution" [6:00–8:30]**
Visual: Template engine diagram. `audit-fix-pipeline.yaml` materialises as a YAML config card — actual structure visible: `stages`, `primitives`, `convergence_loop`, `ac_markers`.
Nine stage nodes materialise in sequence — each a glassmorphic sphere connected by neon lines. As each stage activates: amber pulse → execution → green completion glow. Inactive stages remain at 30% opacity.
Primitive injection shown at key stages: `holistic-validation-gate.yaml`, `detect-fix-rescan-loop.yaml`, `ac-marker-emit.yaml` — each appears as a small inset card when injected.
Convergence loop sub-sequence: violation counter descends 4 → 2 → 0. On reaching 0: AC_COMPLETE badge materialises with timestamp logged to `.cortex-runtime/traces/orchestrator-traces.db`.
Lower-third: `"Workflow templates are YAML — inspectable, versionable, auditable"`
Narrator: *"The pipeline is declarative. Every stage, every gate, every convergence check is defined in YAML — not hardcoded. That means teams can read it, review it, and extend it without modifying orchestrator code."*

**SCENE 5 — "The Output and the Trace" [8:30–End]**
Visual: Output card materialises — diff showing changes. Alongside: SQLite trace panel with four rows: `AC_START`, `AC_STAGE_7_COMPLETE`, `AC_STAGE_9_COMPLETE`, `AC_COMPLETE` with timestamps and ms durations.
Narrator: *"Every orchestrator invocation leaves a trace. Not as a side effect — as a contract. The audit trail is what separates a well-engineered AI system from a fast one."*
Final architectural summary: the full request journey replays as a fast particle flow — 5 seconds, no narration — then fades.
Lower-third on fade: `"Single package. Four stages. Zero ambiguity."`

---

## Audio direction
- "Data centre hum" ambience: low-frequency background drone during architecture shots — distinct from the business video's synth bed
- Light electronic risers on each scene transition (not on every stage — only scene-level)
- LENS iris animation: subtle resonance tone as each ring activates (inward-sweep sound design)
- Silence during the 5-second replay at Scene 5 end

---

## Production note
Use NotebookLM for narrative + architecture slide generation. For the SQLite trace panel in Scene 5, export a real `.cortex-runtime/traces/orchestrator-traces.db` query result and screenshot it. The LENS iris spiral can be an animated SVG or a slow camera push on the static diagram.
