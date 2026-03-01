# NotebookLM Video Prompt — SE-02 — MCP Tools and Workflow Templates: Architecture in Action

**Target length:** 11–14 minutes
**Audience:** Software Engineers, Platform Engineers — people who extend and operate the system
**Narrator gender:** Male (SE-02 — even position in series, per VBP-017)
**Visual theme:** Dark-blue glassmorphism · X-ray / layer-reveal motif · Neon circuit tracing
**Series position:** Engineer depth-2 — the only video covering MCP tool catalogue, registry architecture, and template composition

---

## ⚠️ ZERO-OVERLAP DECLARATION
This video exclusively owns:
- MCP tool catalogue: 29 registered tools, how they're discovered, how they're called
- Registry architecture: `mcp_registry.py`, stdio transport, tool registration pattern
- Workflow template composition from YAML primitives: how templates are assembled on-the-fly
- WorkflowComposer and WorkflowGateway internals
- Extensibility story: how to add a new MCP tool or workflow template

Does NOT repeat: TDD mechanics (SE-01), business identity (Video 01), architecture overview (Video 03), sprint outcomes (PO-01).

---

## Steering Prompt
*Paste into NotebookLM → Customize → Steering Prompt:*

> "Create an 11–14 minute technical deep-dive for software and platform engineers. Cover: (1) how CORTEX exposes 29 MCP tools via Pylance-style stdio transport, (2) how tools are registered in mcp_registry.py and discovered by VS Code Copilot Chat, (3) how workflow templates are composed from YAML primitives at runtime by WorkflowComposer, and (4) how engineers extend the system by adding new tools or templates. Tone: senior engineer doing an architecture walkthrough — specific file paths, real module names, no abstractions. Use only the provided sources."

---

## Ground-truth constraints
- 29 MCP tools registered in `cortex/mcp/tools/mcp_registry.py`; 35 tool files in `cortex/mcp/tools/`
- MCP transport: Pylance-style stdio, configured in `.vscode/settings.json`, auto-detected by VS Code
- Tool calls use operation-based pattern: `cortex_validate(op="compliance")`, `cortex_load(op="rules")`
- Workflow templates: YAML registry at `cortex-registry/workflows/templates/` (3-tier hierarchy: Primitives → Mode Workflows → Composite Pipelines)
- WorkflowGateway: `cortex/orchestrators/workflow/workflow_gateway.py` — mandatory pre-execution gate
- WorkflowComposer: `cortex/orchestrators/workflow/workflow_composer.py` — template execution, convergence_mode support
- TemplateComposer: `cortex/orchestrators/workflow/template_composer.py` — dynamic primitive composition
- All workflow module names are exact: do not invent module names

---

## Visual ingredients
Upload as PNG/JPG:
1. `cortex-docs/assets/diagrams/02-architecture-mcp-gateway-architecture.md` — MCP gateway (Scene 1)
2. `cortex-docs/assets/diagrams/10-workflow-template-engine.md` — template engine (Scenes 3–4)
3. `cortex-docs/assets/image-prompts/shared/02-lens-intelligence-pipeline.prompt.md` — intelligence pipeline (Scene 2)

**Cinematic treatment — X-ray layer reveal:**
Each architectural layer is rendered as a translucent glassmorphic plane stacked in 3D perspective. The camera slowly rotates around the stack, then "X-rays" through each layer sequentially — making the layer being discussed fully opaque while others become wireframe outlines. This is the defining visual motif of SE-02, not used elsewhere.

Layers (bottom to top):
1. VS Code / Developer layer (dim at rest)
2. MCP stdio transport layer (neon circuit lines, cyan)
3. Tool registry layer (capsule grid, each tool a named node)
4. Orchestrator routing layer (IntentRouter compass rose)
5. Workflow template layer (YAML cards, assembled from primitives)
6. Governance + SQLite trace layer (AC markers, audit trail)

---

## Scene-by-scene breakdown

**SCENE 1 — "What MCP Actually Is" [0:00–2:00]**
Visual: MCP gateway diagram. X-ray layer reveal begins — camera approaches the stack from below at 45°.
Layer 1 (VS Code) is fully opaque. Developer types a tool call in Copilot Chat: `@cortex cortex_verify op=mcp`. The text lifts as a packet and travels the stdio transport layer.
Lower-third: `"stdio transport — no HTTP, no ports, no manual startup"`
Layer 2 (transport) brightens. The packet travels a cyan neon circuit trace across the transport layer.
Narrator (male, architecture-tone): *"MCP is not a REST API. It's a local stdio pipe — the same mechanism that powers Pylance. CORTEX uses this to expose tools directly inside VS Code Copilot Chat without any server configuration by the developer."*
The packet arrives at the tool registry layer — a grid of 29 named capsules materialises.

**SCENE 2 — "Tool Registry: 29 Tools, One Registry" [2:00–4:30]**
Visual: Camera X-rays to Layer 3 (tool registry). The 29 capsule grid becomes fully opaque — others become wireframe.
Each capsule has its tool name in JetBrains Mono. Tool groups highlighted by colour families (same cyan accent, but capsule brightness varies):
  Bright: `cortex_validate`, `cortex_load`, `cortex_verify` — most-used tools
  Medium: `cortex_onboard`, `cortex_refactor`, `cortex_governance` — workflow tools
  Standard: remaining 23 tools
`mcp_registry.py` YAML snippet materialises as a config card — actual registration pattern:
```python
@registry.tool("cortex_validate")
async def validate_compliance(operation: str, ...):
    ...
```
Lower-third: `"cortex/mcp/tools/mcp_registry.py — single source of truth for all 29 tools"`
Narrator: *"Every tool is registered in one file. Adding a new tool means registering it here — the framework discovers it automatically. No restart. No configuration change beyond the registry entry."*

**SCENE 3 — "A Tool Call in Flight" [4:30–6:30]**
Visual: Camera follows a tool call end-to-end. `cortex_validate(op="compliance")` typed in chat.
Packet travels: Layer 2 (transport) → Layer 3 (registry lookup → `cortex_validate` capsule brightens) → Layer 4 (orchestrator — `EnforcementOrchestrator`) → Layer 5 (workflow template: `audit-fix-pipeline.yaml`) → Layer 6 (AC_START logged).
Each layer transition: camera dolly through the layer boundary — a subtle glass-refraction visual as the packet crosses each plane.
Response returns: compliance result card materialises at Layer 1 (VS Code), assembled from the output.
Lower-third: `"Every tool call: registry → orchestrator → template → AC marker → response"`
Narrator: *"What looks like a simple tool call is actually a fully traceable pipeline. The registry routes it, the orchestrator executes it, the template governs it, and the AC marker records it. The SQLite trace is not a side effect — it's the contract."*

**SCENE 4 — "Workflow Templates: Assembled, Not Hardcoded" [6:30–9:30]**
Visual: Camera X-rays to Layer 5 (workflow templates). A 3-tier hierarchy materialises:
  Tier 1 (Primitives) — shown as small atomic cards: `ac-marker-emit.yaml`, `detect-fix-rescan-loop.yaml`, `holistic-validation-gate.yaml`, `git-checkpoint.yaml`
  Tier 2 (Mode Workflows) — assembled cards: `implement-workflow.yaml`, `fix-workflow.yaml`, `refactor-workflow.yaml`
  Tier 3 (Composite Pipelines) — composed assemblies: `audit-fix-pipeline.yaml`, `totalrecall-workflow.yaml`

TemplateComposer animation: a mode workflow card opens. Primitives flow into it as particles — each primitive card shrinks and docks into the mode workflow card. The composed workflow seals.
YAML config card visible for `implement-workflow.yaml`:
```yaml
primitives:
  - governance/holistic-validation-gate.yaml
  - governance/challenge-gate.yaml
  - governance/sweep-catalogue-open.yaml
  - validation/detect-fix-rescan-loop.yaml
  - execution/ac-marker-emit.yaml
  - execution/git-checkpoint.yaml
```
Narrator: *"Workflow templates are not generated on-the-fly from scratch. They're composed from validated primitives at runtime. Every primitive is a tested, versioned YAML contract. When you add a new mode, you compose it from existing primitives — you don't rewrite the plumbing."*

**SCENE 5 — "Extending CORTEX: Adding a Tool or Template" [9:30–12:00]**
Visual: A new tool file appears: `cortex/mcp/tools/my_custom_tool.py`. The registration pattern types into `mcp_registry.py`. No restart shown — tool capsule materialises in the registry grid with a brief pulse.
Then: a new primitive YAML card types into `cortex-registry/workflows/templates/primitives/custom/`. A new mode workflow card assembles from it.
WorkflowGateway resolve call: `gw.resolve_template("MY_MODE", {}, strict=True)` — the new template resolves.
Lower-third: `"Extension points: mcp_registry.py + cortex-registry/workflows/templates/primitives/"`
Narrator: *"Extension is additive. You add a tool to the registry. You add a primitive to the template library. The framework discovers both. You don't fork orchestrators, you don't patch core modules. The extension points are designed for this."*

**SCENE 6 — "What This Buys You" [12:00–End]**
Visual: All 6 layers fully opaque simultaneously — the complete X-ray stack in 3D perspective, rotating slowly. Each layer glows at its characteristic colour.
Four outcome cards materialise beside the stack:
  `"Predictable automation"` — same tool call, same governance, every time
  `"Codebase-scale consistency"` — 29 tools apply the same rules to every file
  `"Observable by design"` — every call traced, every template logged
  `"Extensible without forking"` — add tools and templates; core stays stable
Narrator: *"This is what it means to build a governed AI workflow — not a script, not a plugin, but a system with contracts at every layer. Inspectable. Versionable. Auditable."*
Final lower-third: `"29 tools. YAML primitives. Observable by design."`

---

## Audio direction
- Electronic ambience: low circuit-hum drone, distinct from Scenes in SE-01
- X-ray layer transition sound: a subtle glass-resonance chime as camera passes each layer boundary
- Registry capsule pulse: a soft "lock-in" click when a tool is discovered
- Template composition animation: a rising crystalline tone as primitives dock into the workflow card

---

## Production note
Use NotebookLM for narrative + layer-reveal slides. The 3D layer stack can be rendered as a series of stacked slide layers with opacity transitions — NotebookLM will treat these as progressive disclosure (VBP-004). For the YAML config cards, use actual file content from `cortex-registry/workflows/templates/sdlc/implement-workflow.yaml`. For the registration pattern, use the actual registration decorator from `cortex/mcp/tools/mcp_registry.py`.
