# Video Prompt 08 — The Workflow Template Engine

> **Duration:** 9 minutes · **Audience:** Software Engineers, Platform Engineers
> **Depth:** 🔴 Developer-level — architecture internals, three-layer system, real code paths
> **Prerequisites:** Video 02 (request lifecycle), Video 03 (LENS intelligence), Video 07 (audit-fix pipeline)
> **No overlap:** Image prompt-12 shows the workflow assembly line as a static factory floor; this video shows *the three-layer system in motion* — YAML templates as blueprints, WorkflowTemplateMixin as the bridge, and orchestrators as the interpreters that give the templates life

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).

---

## PROMPT

Create a 9-minute animated explainer video titled **"The Workflow Template Engine"** using the visual identity above. The central question this video answers is: *"YAML files are just data — so where does the intelligence come from?"*

---

### Scene 1 — The Question (0:00 – 1:00)

**Open on:** A single glassmorphic panel floating in the `#0a0e27` void. Inside it, a YAML file renders character-by-character in JetBrains Mono:

```yaml
workflow:
  id: sdlc-implementation-execution
  steps:
    - id: red-phase
      action: write_failing_tests
    - id: green-phase
      action: implement_minimum_code
  gates:
    - id: coverage-gate
      threshold: 80%
      blocks_next: true
```

The YAML finishes rendering. Then — **nothing happens.** The panel just floats there, static.

**Narration:** *"CORTEX has dozens of workflow template YAML files. But YAML is just data. It doesn't run. It doesn't decide. It doesn't enforce gates or choose which steps to execute. So... how does any of this actually work?"*

A question mark glyph (`?`) pulses cyan in the center of the panel, then expands into a glowing ring that kicks off the rest of the video.

---

### Scene 2 — The Blueprint Analogy (1:00 – 2:30)

**Transition:** The YAML panel morphs into an architectural blueprint — blueprint-paper texture in `#1a1f3a`, grid lines in dim cyan. The YAML fields are annotated like an architect's notation:

- `steps:` label → annotated as *"sequence of tasks"*
- `gates:` label → annotated as *"quality checkpoints"*
- `action: write_failing_tests` → annotated as *"what to do — not how"*

**Narration:** *"Think of a YAML workflow template like an architect's blueprint. A blueprint tells you what to build — the rooms, the walls, the load-bearing columns. But the blueprint doesn't build anything. You need workers who know how to read it and act on it."*

**Visual:** Three figures materialize around the blueprint: a construction worker (labelled `Orchestrator`), a foreman with a clipboard (labelled `WorkflowTemplateMixin`), and the blueprint itself (labelled `YAML Template`). They glow with their respective tier colors:
- YAML Template → soft amber (`#ffa500`) — the data
- WorkflowTemplateMixin → purple (`#7b61ff`) — the bridge
- Orchestrator → cyan (`#00d4ff`) — the executor

**Text overlay:** *"Three layers. Three responsibilities."*

---

### Scene 3 — Layer 1: The Data (YAML Templates) (2:30 – 4:00)

**Camera zooms into the YAML panel.** The directory tree materializes:

```
workflow-templates/
  tdd/
    feature-implementation.yaml    ← development work
  sdlc/
    sdlc-implementation-execution.yaml
    sdlc-code-review-gate.yaml
  debugging/
    multi-stack-debug-pipeline.yaml ← debugging work
  testing/
    test-quality-enforcement.yaml   ← testing work
  security/
    compliance-audit.yaml
  audit/
    audit-fix-pipeline.yaml
```

Each folder glows a different accent color as it's named. Cyan for `tdd/`, purple for `sdlc/`, amber for `debugging/`, green for `testing/`, red for `security/`.

**Narration:** *"Layer 1 is the library. Dozens of YAML files organized by purpose — development, debugging, testing, security, audit. Each file declares: what steps to run, in what order, with what gates. Pure structured data. Zero execution logic."*

**Emphasis beat:** The word **"Zero execution logic"** appears in white Space Grotesk on the dark background. The YAML panel pulses amber — it's a passive document, not an actor.

---

### Scene 4 — Layer 2: The Bridge (WorkflowTemplateMixin) (4:00 – 5:30)

**Visual:** A new glassmorphic component slides into frame — a Python class panel. The class name renders in JetBrains Mono:

```python
class WorkflowTemplateMixin:
    TEMPLATE_ORCHESTRATOR_MAP = {
        "TDDOrchestrator":      "tdd/feature-implementation",
        "SDLCWorkflowOrchestrator": "sdlc-implementation-execution",
        "DebuggerOrchestrator": "debugging/multi-stack-debug-pipeline",
        "EnforcementOrchestrator": "security/compliance-audit",
    }

    def discover_templates(self, category=None): ...
    def load_template(self, template_id: str): ...
    def get_recommended_template(self): ...
```

**Animated explanation:** Three methods light up one at a time in cyan as the narration mentions each:

1. `discover_templates()` → *"Scans the entire YAML library and lists what's available"* — a mini file-browser animation plays
2. `load_template(id)` → *"Parses the YAML file and returns a live Python dictionary"* — a YAML file melts into a glowing `{}` dict object
3. `get_recommended_template()` → *"Returns None in the base class — subclasses override this"* — the return value fades grey, awaiting override

**Narration:** *"Layer 2 is the bridge. `WorkflowTemplateMixin` is inherited by every orchestrator in CORTEX — all 51 of them. It lazily loads the YAML library on first use, maps orchestrator names to their preferred templates, and gives every orchestrator three capabilities: discover, load, and recommend."*

**Key insight callout** — a glassmorphic card pulses into view:

> *"The mixin does NOT change how orchestrators execute. Orchestrators remain the HOW. Templates remain the WHAT and WHEN. The mixin is the bridge between them."*

---

### Scene 5 — Layer 3: The Intelligence (Orchestrators) (5:30 – 7:15)

**Scene shift:** Pull back to show the full orchestrator galaxy from Video 2. But now each orchestrator has a small YAML blueprint icon attached to it, glowing amber.

**Zoom into `SDLCWorkflowOrchestrator`.** The Python intent map renders:

```python
_SDLC_INTENT_MAP = {
    "IMPLEMENT":  "sdlc-implementation-execution",  # → development template
    "FIX":        "sdlc-code-review-gate",           # → debugging template
    "SECURITY_AUDIT": "sdlc-security-assessment",   # → security template
    "RELEASE":    "sdlc-release-readiness",         # → release template
}
```

**Animation:** A user request flows in — `"Fix the broken auth module"`. Watch the chain:

1. **IntentRouter** classifies it → `FIX` (cyan beam fires)
2. **MasterOrchestrator** routes to `SDLCWorkflowOrchestrator` (purple beam)
3. `_resolve_template("FIX")` → looks up `_SDLC_INTENT_MAP` → returns `"sdlc-code-review-gate"` (amber glow)
4. `load_template("sdlc-code-review-gate")` → reads and parses the YAML file (blueprint materializes)
5. Orchestrator reads `steps:` and `gates:` from the loaded dict → **executes them in Python** (cyan sparks fire from each step)

**Narration:** *"Layer 3 is the intelligence. The orchestrator's Python code holds the routing logic — which template for which kind of work. FIX routes to the code-review-gate template. IMPLEMENT routes to implementation-execution. SECURITY_AUDIT routes to the security-assessment template. This Python dictionary IS the decision logic."*

**Critical distinction** — the camera holds on the final step — sparks firing from the parsed dict:

**Narration:** *"The YAML is consulted, not executed. The orchestrator reads the gates declared in the YAML and enforces them in Python. Without the orchestrator, the YAML is a blueprint in an empty room. With it, the blueprint becomes action."*

---

### Scene 6 — Why This Design? (7:15 – 8:15)

**Three glassmorphic benefit cards slide in from the bottom:**

**Card 1 — Auditability** (`#00d4ff` border)
*"Every workflow is visible and human-readable. Your team can review what CORTEX will do before it does it — just read the YAML."*
Icon: Magnifying glass over a YAML file.

**Card 2 — Company Override** (`#7b61ff` border)
*"Your company places custom YAML templates in a dedicated company override directory. They automatically take precedence over CORTEX defaults — no code change required."*
Icon: Company building overlaid on the template library, glowing brighter.

**Card 3 — Separation of Concerns** (`#00ff88` border)
*"Change the sequence of steps without touching orchestrator code. Change the execution logic without touching templates. Each layer evolves independently."*
Icon: Two interlocked gears — one labelled YAML, one labelled Python — rotating independently but in sync.

**Narration:** *"This separation is intentional. It gives you three benefits: auditability because anyone can read the YAML; extensibility because you can override any template without forking CORTEX; and stability because the execution engine never changes when you update workflows."*

---

### Scene 7 — The Complete Picture (8:15 – 9:00)

**Pull back to show all three layers simultaneously** — a vertical stack:

```
┌─────────────────────────────────────────────┐
│  Layer 3: Orchestrators (Python)            │ ← cyan  — the interpreters
│  51 wired orchestrators · intent maps ·     │
│  get_recommended_template() overrides       │
├─────────────────────────────────────────────┤
│  Layer 2: WorkflowTemplateMixin (Python)    │ ← purple — the bridge
│  discover · load · map · lazy registry      │
├─────────────────────────────────────────────┤
│  Layer 1: YAML Templates (Data)             │ ← amber  — the blueprints
│  workflow-templates/ (categorized library)  │
│  steps · gates · convergence · criteria     │
└─────────────────────────────────────────────┘
```

A cyan request beam enters the top, flows through all three layers, exits as a green ✅ at the bottom.

**Text overlay** (Space Grotesk, white, full width):

> *"YAMLs are blueprints. Mixins are bridges. Orchestrators are builders."*

**Narration:** *"The workflow template engine isn't magic — it's a disciplined three-layer design. YAML provides the contract, the mixin provides the vocabulary, and the orchestrator provides the judgment. Together they make CORTEX's behaviour transparent, extensible, and production-safe."*

**Outro:** The CORTEX logo pulses into frame. Closing vision callback:

> *"The workflows your team debates, documents, and forgets — CORTEX encodes them permanently. Change the blueprint, change the behaviour. No code rewrites."*

---

## Technical Accuracy Notes (for Animators)

All code shown in this video is drawn directly from the live CORTEX codebase:

| Code Shown | Source File |
|-----------|-------------|
| `TEMPLATE_ORCHESTRATOR_MAP` | `cortex/core/workflow_template_mixin.py` — class-level dict |
| `discover_templates()`, `load_template()`, `get_recommended_template()` | WorkflowTemplateMixin — three public methods |
| `_SDLC_INTENT_MAP` | SDLCWorkflowOrchestrator — module-level intent routing dict |
| Template directory tree | CORTEX workflow templates — organized by category |
| Company override path | Company customization directory — takes precedence over defaults |

**Do not fabricate** template IDs or orchestrator names. Use only those shown above — they are verified against the live codebase.

---

## Cross-Reference: No Overlap with Other Videos or Images

| Concept | This Video Covers | Other Asset |
|---------|-------------------|-------------|
| Three-layer design | ✅ Full explanation | Image prompt-12 — static assembly line diagram |
| Request routing | Forward-reference only | Video 02 — The Life of a Request (full routing) |
| LENS analysis | Forward-reference only | Video 03 — The Intelligence Engine |
| TDD cycle | Template step names only | Video 05 — TDD Mastery (full cycle) |
| Audit pipeline | "audit-fix-pipeline" example only | Video 07 — The Audit Fix Pipeline |
| MCP tools | Not covered | Video 06 — MCP Tools Deep Dive |

---

*Drawn from live architecture conversation — 27 February 2026 · Verified against the live CORTEX codebase*
