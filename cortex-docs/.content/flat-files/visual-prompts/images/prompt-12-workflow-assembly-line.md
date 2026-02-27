# Prompt 12 — WorkflowEngine as a Factory Assembly Line

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create a cross-section illustration of a modern automated factory assembly line, reimagined as the CORTEX WorkflowEngine finite state machine (FSM), rendered in the CORTEX dark glassmorphism aesthetic.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with industrial ambient lighting in cyan
- All station panels/frames: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff). Success: Green (#00ff88). Danger: Red (#ff4444). Warning: Amber (#ffa500)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~50px, subtle inner shadow

THE ASSEMBLY LINE (running left to right, conveyor belt glowing with subtle cyan line):

STATION 1 — "PENDING" (glassmorphic panel with muted (#a0a6c0) top accent):
- Raw materials entering the line
- Glassmorphic clipboard with checklist
- JetBrains Mono label: "Workflow created · Waiting"
- Muted analogy: "Like a restaurant order placed but not started"

STATION 2 — "VALIDATED" (glassmorphic panel with blue #3b82f6 top accent):
- QC booth scanning materials with blue beams
- Glassmorphic checklist with green (#00ff88) checkmarks
- JetBrains Mono label: "Inputs verified · Governance pre-checked"
- Muted analogy: "Like ingredients weighed before cooking"

STATION 3 — "EXECUTING" (glassmorphic panel with amber #ffa500 top accent — the longest station):
- Glassmorphic robotic arms (orchestrators) working on the product
- Multiple sub-stations visible, each with a tiny red(#ff4444)-green(#00ff88)-blue(#3b82f6) TDD cycle icon
- Cyan (#00d4ff) sparks from active work
- JetBrains Mono label: "Orchestrator executing · TDD gates active"
- Muted analogy: "Like the main production line — each station adds something"

STATION 4 — "COMPLETED" (glassmorphic panel with green #00ff88 top accent):
- Finished product exits with glassmorphic quality stamp
- "AC_COMPLETE ✅" badge in green
- JetBrains Mono label: "Tests passing · Audit logged"
- Muted analogy: "Like the finished car rolling off with its QC sticker"

BRANCH PATHS (side conveyors branching downward):

BRANCH A — "FAILED" (glassmorphic panel with red #ff4444 accent, branching from EXECUTING):
- Product diverted to repair area
- Rollback mechanism with curved arrow
- JetBrains Mono label: "Error detected · Rollback"

BRANCH B — "BLOCKED" (glassmorphic panel with amber #ffa500 accent, branching from VALIDATED):
- Stop sign gate with governance shield
- JetBrains Mono label: "Governance violation · Cannot proceed"

STATE MACHINE DIAGRAM overlay (top-right corner, glassmorphic panel with JetBrains Mono):
PENDING → VALIDATED → EXECUTING → COMPLETED
                         ↓              ↓
                      BLOCKED        FAILED

Glassmorphic footer:
"WorkflowEngine FSM · 7 States · YAML Templates · cortex/orchestrators/workflow/"
Muted subtitle: "Like an assembly line — every product goes through the same proven process"

Style: Clean industrial illustration with dark glassmorphism overlay. Cyan-glowing conveyor and robotic arms. Frosted glass station panels. Professional and educational.

Dimensions: 800×600
Format: PNG
```

## Notes for Generation
- WorkflowEngine uses a Finite State Machine (FSM) pattern (Phase 67)
- States: PENDING, VALIDATED, EXECUTING, COMPLETED, FAILED, BLOCKED, CANCELLED
- 17 workflow template categories in `cortex-registry/workflows/templates/`
- Templates are composable YAML primitives
