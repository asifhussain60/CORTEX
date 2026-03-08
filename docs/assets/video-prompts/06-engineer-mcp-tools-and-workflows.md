# NotebookLM Video Prompt — SE-02 — MCP Tools and Workflow Templates: Architecture in Action

**Target length:** 13–16 minutes
**Audience:** Software Engineers, Platform Engineers — people who extend and operate the system
**Narrator gender:** Male (SE-02 — even position in series, per VBP-017)
**Visual theme:** Dark-blue glassmorphism · X-ray / layer-reveal motif · Neon circuit tracing
**Series position:** Engineer depth-2 — the only video covering MCP tool catalogue, registry architecture, and template composition

---

## ⚠️ ZERO-OVERLAP DECLARATION
This video exclusively owns:
- MCP tool catalogue: 35+ registered tools, how they're discovered, how they're called
- Registry architecture: `mcp_registry.py`, stdio transport, tool registration pattern
- Workflow Composer internals: how the `WorkflowComposer`, `WorkflowGateway`, and `TemplateComposer` assemble mode workflows from YAML primitives at runtime
- The cross-cutting intelligence pipeline: how every orchestrator operation feeds a learning loop that extracts patterns, scores them with a reinforcement signal, and refines future recommendations — with architecture-level description only (self-adaptation mechanics owned by Video 08)
- **Intent-aligned response headers:** the `BLOCK-QUOTE-LIBRARY`, how intent classification selects the theme, and how governance philosophy is made visible on every CORTEX interaction
- Extensibility story: how to add a new MCP tool or workflow template

Does NOT repeat: test-first mechanics (SE-01), business identity (Video 01), architecture overview (Video 03), sprint outcomes (Video 04), self-learning details and root cause analysis mechanics (Video 08), knowledge domain profiles (Video 09).

---

## Problem Statement — Why This Video Exists

Software and Platform Engineers who extend and operate AI-augmented systems face a recurring maintenance nightmare: every customisation requires forking core orchestrators, patching modules, and hoping upgrades don't break the fork. CORTEX solves this with three hard architectural guarantees — **55+ MCP tools** exposed through the same stdio pipe that powers Pylance (zero server configuration), **90+ workflow templates** dynamically composed from tested YAML primitives at runtime (zero core-module changes to add a new mode), and a **cross-cutting intelligence pipeline** where every operation automatically feeds a learning loop — so patterns detected today improve recommendations tomorrow, without manual tuning.

**Primary audience pain points addressed:**
- "I need to add a new automation step — do I have to fork the orchestrator?"
- "How do I know a tool call is doing what I think it's doing?"
- "What happens when a governance rule changes — do I update every workflow?"
- "How does CORTEX get smarter about our codebase over time without someone manually updating it?"

---

## Steering Prompt
*Select the **Explainer** format in NotebookLM, then paste into NotebookLM → Customize → Steering Prompt:*

> "Select the Explainer format to create an 11–14 minute technical deep-dive for software and platform engineers. Cover: (1) how CORTEX exposes 55+ MCP tools via Pylance-style stdio transport, (2) how tools are registered in mcp_registry.py and discovered by VS Code Copilot Chat, (3) how the Workflow Composer and Workflow Gateway assemble mode workflows from YAML primitives at runtime, (4) how the cross-cutting intelligence pipeline automatically captures patterns from every operation and feeds a reinforcement learning loop — described at architecture level only, not implementation detail, (5) how CORTEX's intent-aligned response headers surface a governance-anchored business or engineering principle on every interaction — selected by the same intent classification that routes tool calls (the BLOCK-QUOTE-LIBRARY, 120 quotes across 10 themes), and (6) how engineers extend the system by adding new tools or templates. Tone: senior engineer doing an architecture walkthrough — specific file paths, real module names, no abstractions. Use only the provided sources, and ensure all visual generation uses an 'X-ray / layer-reveal' motif with neon circuit tracing overlaid on a Dark-blue glassmorphism theme."

---

## Ground-truth constraints
- 36 MCP tools registered in `cortex/mcp/mcp_registry.py`; 60 tool files in `cortex/mcp/tools/` (use "35+" as the public floor-approximation)
- MCP transport: Pylance-style stdio, configured in `.vscode/settings.json`, auto-detected by VS Code
- Tool calls use operation-based pattern: `cortex_validate(op="compliance")`, `cortex_load(op="rules")`
- Workflow templates: YAML registry at `cortex-registry/workflows/templates/` (3-tier hierarchy: Primitives → Mode Workflows → Composite Pipelines)
- WorkflowGateway: `cortex/orchestrators/workflow/workflow_gateway.py` — mandatory pre-execution gate
- WorkflowComposer: `cortex/orchestrators/workflow/workflow_composer.py` — template execution, convergence mode support
- TemplateComposer: `cortex/orchestrators/workflow/template_composer.py` — dynamic primitive composition at runtime
- Cross-cutting intelligence pipeline: `cortex/intelligence/learning/universal_learning_loop.py` — every orchestrator operation feeds pattern capture (`PatternType`: TECHNICAL, BUSINESS, GOVERNANCE, INTERACTION, PERFORMANCE); reinforcement signal (`cortex/intelligence/learning/reinforcement_signal.py`) scores each pattern; patterns are promoted into active recommendations or quarantined out of them based on accumulated confidence — scoring thresholds and lifecycle mechanics are owned by Video 08
- **Intent-aligned response headers:** Every CORTEX response header now emits a contextually selected business or engineering principle — drawn from a curated `BLOCK-QUOTE-LIBRARY` in `.github/templates/cortex-response-templates.md`. The selection is driven by the same intent classification that routes tool calls: a TDD or testing request surfaces a quality principle (Kent Beck, Pragmatic Programmer); a security request surfaces a trust or resilience principle (Nygard, SRE book); a refactoring request surfaces a lean or improvement principle (Poppendieck, Fowler). The quote, author, and book are rendered as a Markdown blockquote inside the response header — making CORTEX's governance philosophy visible and teachable on every interaction, not just when violations are flagged. Library location: `.github/templates/cortex-response-templates.md § BLOCK-QUOTE-LIBRARY`. Theme→intent routing table is co-located in that section.
- All workflow module names are exact: do not invent module names

---

## Visual ingredients
Upload as PNG/JPG:
1. `cortex-docs/assets/diagrams/02-diagram-architecture-mcp-gateway-architecture.md` — MCP gateway (Scene 1)
2. `cortex-docs/assets/diagrams/10-diagram-workflow-template-engine.md` — template engine (Scenes 3–4)
3. `cortex-docs/assets/diagrams/14-diagram-debugging-multi-stack-pipeline.md` — 8 debug strategies as an example of the extensibility pattern (Scene 5)
4. `cortex-docs/assets/image-prompts/shared/02-lens-intelligence-pipeline.prompt.md` — intelligence pipeline (Scene 6)

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
The packet arrives at the tool registry layer — a grid of 30 named capsules materialises.

**SCENE 2 — "Tool Registry: 30 Tools, One Registry" [2:00–4:30]**
Visual: Camera X-rays to Layer 3 (tool registry). The 30 capsule grid becomes fully opaque — others become wireframe.
Each capsule has its tool name in JetBrains Mono. Tool groups highlighted by colour families (same cyan accent, but capsule brightness varies):
  Bright: `cortex_validate`, `cortex_load`, `cortex_verify` — most-used tools
  Medium: `cortex_onboard`, `cortex_refactor`, `cortex_governance` — workflow tools
  Standard: remaining 24 tools
`mcp_registry.py` YAML snippet materialises as a config card — actual registration pattern:
```python
@registry.tool("cortex_validate")
async def validate_compliance(operation: str, ...):
    ...
```
Lower-third: `"cortex/mcp/mcp_registry.py — single source of truth for all 30 tools"`
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

**SCENE 5 — "Extending CORTEX: Adding a Tool or Template" [9:30–11:30]**
Visual: A new tool file appears: `cortex/mcp/tools/my_custom_tool.py`. The registration pattern types into `mcp_registry.py`. No restart shown — tool capsule materialises in the registry grid with a brief pulse.
Then: a new primitive YAML card types into `cortex-registry/workflows/templates/primitives/custom/`. A new mode workflow card assembles from it.
WorkflowGateway resolve call: `gw.resolve_template("MY_MODE", {}, strict=True)` — the new template resolves.
Lower-third: `"Extension points: mcp_registry.py + cortex-registry/workflows/templates/primitives/"`
Narrator: *"Extension is additive. You add a tool to the registry. You add a primitive to the template library. The framework discovers both. You don't fork orchestrators, you don't patch core modules. The extension points are designed for this."*

**SCENE 6 — "The Cross-Cutting Intelligence Pipeline" [11:30–13:30]**
Visual: A thin neon thread runs from the Workflow Template layer (Scene 4) downward to a new layer beneath all others — the intelligence layer. It pulses gently, always active.
Camera X-rays to this layer. Three sub-panels materialise side by side:
  Panel 1 — Pattern Capture: `UniversalLearningLoop` — every orchestrator operation is captured automatically. Pattern types visible as labelled capsules: `Technical`, `Business`, `Governance`, `Interaction`, `Performance`. Each capsule fills with data as operations complete.
  Panel 2 — Reinforcement Signal: A scoring dial materialises. The dial moves as each operation resolves — toward reward when governance passes, toward punishment when violations are detected. No numeric scale shown — scoring mechanics are owned by Video 08.
  Panel 3 — Promote / Quarantine: A pattern with sufficient accumulated confidence lights green and moves to a "Promoted" tier. A pattern with accumulated negative signal turns amber and moves to "Quarantined". No scoring numbers shown — this layer shows the outcome, not the thresholds.
Lower-third: `"Every operation feeds the intelligence pipeline — automatically, without configuration"`
Narrator: *"This is the cross-cutting intelligence pipeline. It does not require manual tuning. Every time an orchestrator completes an operation — whether it's an audit pass, a governance fix, or a test run — the result flows into a learning loop. Successful patterns accumulate confidence and get promoted. Patterns that consistently fail are quarantined. The framework becomes more accurate the longer it runs — not because someone updated a config file, but because the signal is built into the architecture."*
On-screen callout: `"Signal in. Confidence out. No manual tuning."`

**SCENE 7 — "Governance Made Visible: Intent-Aligned Quotes" [13:30–14:30]**
Visual: A single CORTEX response header materialises in VS Code Copilot Chat. The header renders: tool name, author line, then — after a brief pause — a blockquote fades in beneath it. The quote is not static: camera cuts to three different response headers side-by-side, each showing a different quote matched to a different intent.
  Example 1 (TDD request): *"Make it work, make it right, make it fast — in that order."* — Kent Beck, **Test-Driven Development**
  Example 2 (Refactor request): *"Waste is anything that does not add value to the customer."* — Poppendieck, **Lean Software Development**
  Example 3 (Security request): *"Design for failure. Plan for recovery."* — Nygard, **Release It!**
Camera reveals: the same IntentRouter compass rose from Scene 3 — the routing decision that selects the orchestrator also selects the quote theme. `quality` → TDD quotes. `security` → resilience quotes. `improvement` → lean/refactor quotes.
Lower-third: `"BLOCK-QUOTE-LIBRARY — 120 quotes · 10 themes · matched by intent"`
Narrator: *"Every response CORTEX emits carries a principle from the engineering literature that anchors the governance rule being applied. This is not decoration — it's the philosophy of the system made visible on every interaction. The quote is selected by the same intent classification that chose the orchestrator."*
On-screen callout: `"Governance shouldn't be invisible — it should be instructive."`

**SCENE 8 — "What This Buys You" [14:30–End]**
Visual: All 6 layers fully opaque simultaneously — the complete X-ray stack in 3D perspective, rotating slowly. Each layer glows at its characteristic colour.
Four outcome cards materialise beside the stack:
  `"Predictable automation"` — same tool call, same governance, every time
  `"Codebase-scale consistency"` — 30 tools apply the same rules to every file
  `"Observable by design"` — every call traced, every template logged
  `"Extensible without forking"` — add tools and templates; core stays stable
Narrator: *"This is what it means to build a governed AI workflow — not a script, not a plugin, but a system with contracts at every layer. Inspectable. Versionable. Auditable."*
Final lower-third: `"30 tools. YAML primitives. Observable by design."`

---

## Audio direction
- Electronic ambience: low circuit-hum drone, distinct from Scenes in SE-01
- X-ray layer transition sound: a subtle glass-resonance chime as camera passes each layer boundary
- Registry capsule pulse: a soft "lock-in" click when a tool is discovered
- Template composition animation: a rising crystalline tone as primitives dock into the workflow card

---

## Production note
Use NotebookLM for narrative + layer-reveal slides. The 3D layer stack can be rendered as a series of stacked slide layers with opacity transitions — NotebookLM will treat these as progressive disclosure (VBP-004). For the YAML config cards, use actual file content from `cortex-registry/workflows/templates/sdlc/implement-workflow.yaml`. For the registration pattern, use the actual registration decorator from `cortex/mcp/mcp_registry.py`.

---

## NotebookLM Setup Checklist

Follow these steps in order before generating video content:

| Step | Action | Detail |
|------|--------|--------|
| 1 | **Select format** | Choose **Explainer** (not Overview or FAQ) in NotebookLM format picker |
| 2 | **Set narrator** | Male voice — SE-02 is even-position in series (VBP-017) |
| 3 | **Upload sources** | Upload all 4 visual ingredients listed above as PNG/JPG |
| 4 | **Paste steering prompt** | Copy the full steering prompt above verbatim into Customize → Steering Prompt |
| 5 | **Set length target** | 13–16 minutes |
| 6 | **Verify visual theme** | Confirm X-ray / layer-reveal motif is active — dark-blue glassmorphism background, cyan neon circuit traces |
| 7 | **Lock source-only mode** | Enable "Use only provided sources" to prevent hallucinated module names |
| 8 | **Preview Scene 1 first** | Render Scene 1 alone to confirm the 6-layer stack renders correctly before generating the full sequence |
| 9 | **Verify Scene 6 framing** | The cross-cutting intelligence pipeline scene must describe the learning loop at architecture level — no implementation detail, no internal scoring numbers in narration |
