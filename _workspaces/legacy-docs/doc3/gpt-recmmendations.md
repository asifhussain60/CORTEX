# CORTEX 6.0 Documentation Generation — Corrections, Enhancements, and Copilot Build Prompt  
**Purpose:** Provide a single authoritative instruction set for GitHub Copilot to upgrade the documentation system to generate **comprehensive Level 1 and Level 2 views** (technical, richly illustrated, modern HTML) using the **approved orchestrator Level 1 view** as the design baseline, and to implement/repair the **Python-driven real-time documentation generation** pipeline.

---

## 0. What I unpacked from `docs.zip` (current state + issues)

### 0.1 Observed documentation structure (output site)
The zip contains an already-built GitHub Pages site rooted under `docs/` with content such as:
- `docs/README.md` describing a tiered doc model but leaving key details unfinished (`...` placeholder).
- Many HTML pages under `docs/architecture/` and `docs/orchestrators/`.
- Multiple orchestrator pages exist only as `.html.bak` rather than as active `.html` (example: `docs/orchestrators/cortex-lens.html.bak` and several `docs/orchestrators/ado-v2/*.html.bak`).

### 0.2 Critical gap: generator scripts not present in `docs.zip`
I did **not** find any `*.py` scripts inside this `docs.zip`. That means:
- Either the Python doc generator lives elsewhere in the repo (outside `docs/`), or  
- It is missing from the published source package, which prevents others from reproducing the documentation build.

✅ **Action:** Copilot must locate the doc generator Python scripts in the repository (likely outside `/docs`), and if they don’t exist, create them (see Prompt section).

### 0.3 UX/system issues in current HTML output
These issues are visible in existing pages (especially the `.bak` orchestrator pages):
- **Inline everything**: styles and scripts appear embedded per-page, making consistency and performance hard.
- **No shared components**: repeated header/nav/footers likely duplicated.
- **Inconsistent publishing**: `.bak` indicates orphaned pages not actually linked/deployed.
- **No unified data contract**: pages appear authored, not generated from a single structured plan/context schema.
- **Missing “truth signals”**: current docs explain systems but don’t provide a deterministic “what’s active / blocked / wired” runtime view.

---

## 1. Enhancements required for CORTEX 6.0 docs (Level 1 + Level 2)

### 1.1 Level 1: Orchestrator view (approved baseline)
**Level 1** is the executive/architectural “operating picture” that must remain consistent across orchestrators:

**Must include:**
- **System intent**: what the orchestrator does + non-goals.
- **Operating model**: phases/stages, gate checks, invariants.
- **Architecture overview**: component map + data flow.
- **Lifecycle**: inputs → processing → outputs → verification.
- **Truth surfaces**: “Active / Partially active / Dormant / Blocked” status.

**Visual-first requirements (Level 1):**
- Mermaid diagrams for fast, static flow / sequence / state diagrams.
- A D3-driven interactive graph for dependency + architecture wiring.
- A “phase health” dashboard with semantic status colors:
  - ✅ Green: Done/Verified
  - 🟧 Orange: In progress
  - 🟥 Red: Blocked/Violation
  - ⬜ Grey: Not started/Dormant

### 1.2 Level 2: Deep technical view (rich, deterministic, reproducible)
**Level 2** must be the “engine room” documentation: implementation semantics and wiring.

**Must include:**
- **API & Interfaces**: signatures, contracts, schemas.
- **State and lifecycle semantics**: mutation rules, event ordering, idempotency.
- **Governance enforcement**: what rules exist, what they block, where they apply.
- **Verification layer**: tests, coverage, truth signals, confidence.
- **Failure modes**: realistic edge cases, recovery patterns, rollback strategy.
- **Traceability**: provenance metadata (who created what, when, from what evidence).

**Visual-first requirements (Level 2):**
- Interactive D3 graph(s):
  - module/component dependency
  - plan → orchestrator → outputs mapping
- SVG sequence diagrams or Mermaid sequence diagrams (static is fine).
- Tables generated from schemas (not hand-written): inputs/outputs/states/rules.
- “Runtime-ish” panels: show active features, inactive, blocked, last updated timestamps.

---

## 2. Modern HTML / Web Dev requirements for docs pages

### 2.1 Hard requirements (non-negotiable)
- Use **semantic HTML**: `header`, `nav`, `main`, `article`, `section`, `aside`, `footer`.
- Use `details/summary` for collapsible Level 2 deep sections.
- Use `dialog` for drilldown panels (diagram node click → modal details).
- Use `popover` API where supported (fallback to `dialog` if needed).
- Use `content-visibility: auto;` for performance on large pages.
- Use CSS variables + design tokens:
  - `--status-done`, `--status-progress`, `--status-blocked`, `--status-not-started`
- Prefer `prefers-reduced-motion` support.
- Accessibility:
  - keyboard navigation for diagrams
  - ARIA labeling for charts
  - sufficient contrast (WCAG-minded)
- No per-page duplicated CSS. Centralize:
  - `docs/assets/css/site.css`
  - `docs/assets/js/site.js`
  - `docs/assets/js/graphs.js`
- Do not exceed performance budget:
  - load Mermaid and D3 efficiently
  - defer heavy scripts
  - lazy render large sections

### 2.2 Recommended modern pattern
Use **one shared layout** + **data-driven content**:
- Generate JSON models per orchestrator:
  - `docs/_data/orchestrators/<name>.json`
- Generate pages from a template:
  - `docs/_templates/orchestrator.html`
- Output:
  - `docs/orchestrators/<name>.html`

---

## 3. The missing piece: a deterministic documentation data contract

### 3.1 Required schema (authoritative)
Define a single schema used by Python generation scripts:

`docs/_schemas/orchestrator.schema.json`:
- `id`, `name`, `version`, `status`
- `level1`: overview + flows + invariants + gates
- `level2`: interfaces + modules + states + rules + tests + failure_modes
- `features`: list of capabilities with activation state
- `architecture`: components, edges, protocols, ownership
- `progress`: metrics by phase, % done, blockers, last_updated

**Copilot must generate/validate docs off this schema**. No freehand HTML.

### 3.2 Status semantics
Every feature/task/component must have:
- `state`: `done | in_progress | blocked | not_started`
- `reason` (required if blocked)
- `evidence`: links to file(s), tests, or commits (if available)
- `last_updated`

---

## 4. Python doc generation pipeline — required behavior

Because `docs.zip` does not include scripts, the generator must be enforced explicitly.

### 4.1 Required scripts
Copilot must implement or repair these scripts (or adapt existing ones if found):

- `tools/docs/generate_docs.py`  
  **Entry point:** builds Level 1 + Level 2 pages for each orchestrator.

- `tools/docs/collect_signals.py`  
  Extracts real signals (tests/coverage/config flags, module presence, file existence, TODO markers) to determine active vs inactive vs blocked.

- `tools/docs/render_orchestrator.py`  
  Renders orchestrator pages from templates + JSON model.

- `tools/docs/validate_schema.py`  
  Validates orchestrator JSON against schema.

- `tools/docs/watch.py` (optional but recommended)  
  Watches files and regenerates docs on change.

### 4.2 “Real-time documentation” definition (practical)
Real-time does not mean live server integration. It means:
- regenerate docs deterministically on file changes or CI runs
- embed last generated timestamp + signal snapshot
- display a “truth panel” with evidence

### 4.3 Build targets
- Local: `python tools/docs/generate_docs.py --all`
- CI: run generation and fail if:
  - schema invalid
  - required orchestrators missing L1 or L2 sections
  - pages are stale relative to source content

---

## 5. Concrete gaps and corrections Copilot must address

### 5.1 Publishing gaps
- `.html.bak` pages must be reconciled:
  - either promote them to `.html` and link them in index/nav
  - or delete if deprecated
- Ensure orchestrator index pages enumerate all orchestrators consistently.

### 5.2 Content completeness gaps
- `docs/README.md` has an incomplete orchestrator tier description (`...`). Fill it, and make it match actual generation workflow.

### 5.3 Structural gaps
- There is no obvious `assets/` folder in the zip; add a proper shared asset pipeline.
- Add a single source of truth for nav + footer.
- Add a global search index (optional but valuable):
  - generate `docs/search-index.json`
  - client-side search UI

### 5.4 Observability gap
Docs currently describe architecture, but don’t show:
- what is actually implemented vs planned
- what is wired vs stubbed
- what is active vs dormant
- what is blocked and why

Fix via “Truth Panel” + signal extraction in Python generator.

---

## 6. GitHub Copilot prompt (copy/paste)  
**Use this as the instruction to Copilot. It must create a VS Code to-do list and complete work incrementally.**

### ✅ Copilot Prompt: CORTEX 6.0 Documentation Generator Upgrade

You are working in the CORTEX repository. Your task is to repair and enhance the documentation generation system so it can generate **comprehensive Level 1 and Level 2 orchestrator documentation** using a consistent “approved orchestrator Level 1 view” layout, plus deep technical Level 2 views, with rich visuals and modern HTML capabilities. Create a VS Code Copilot Todo list first, then implement the work in small, testable increments. Use deterministic schemas and avoid hand-authored HTML.

**Phase 0 — Discovery and Safety**
1) Scan the repo to locate existing Python doc generation scripts and any existing templates or JSON models used for docs generation. If none exist, create them under `tools/docs/`.  
2) Identify current docs output structure under `/docs/` and reconcile `.html.bak` files (promote to `.html` if active, or delete if deprecated).  
3) Preserve existing visual design patterns from the approved orchestrator Level 1 view (glass cards, mermaid sections, section titles, etc.) but refactor into shared assets/templates.

**Phase 1 — Data Contract and Validation**
4) Create `docs/_schemas/orchestrator.schema.json` defining orchestrator documentation structure with:
   - `level1` (overview, phases, invariants, gates, architecture diagram nodes/edges)
   - `level2` (interfaces, states, rules, tests, failure modes, traceability)
   - `features` with activation states (done/in_progress/blocked/not_started)
   - `progress` metrics per phase with blockers and evidence
5) Implement `tools/docs/validate_schema.py` to validate orchestrator JSON against the schema and fail build on violations.

**Phase 2 — Signal Extraction (“Truth Panel”)**
6) Implement `tools/docs/collect_signals.py` that extracts real signals (file presence, module presence, config flags, tests/coverage output if available, TODO markers, known stubs) and produces:
   - `docs/_data/signals.json`
   - per-orchestrator activation summaries
7) Ensure each orchestrator page renders a “Truth Panel” showing:
   - active features
   - inactive/dormant features
   - blocked items with reasons and evidence links
   - last generated timestamp

**Phase 3 — Shared Assets + Modern HTML**
8) Create `docs/assets/css/site.css` using CSS variables for status colors:
   - green = done, orange = in progress, red = blocked, grey = not started  
   Ensure accessibility (contrast) and `prefers-reduced-motion` support.
9) Create `docs/assets/js/site.js` for shared page behavior (nav, theme, search hooks).
10) Create `docs/assets/js/graphs.js` using D3.js to render:
   - dependency graph (components/modules)
   - plan → feature activation map
   Make nodes clickable to open `dialog` with details. Provide keyboard support.

**Phase 4 — Templates + Rendering**
11) Create `docs/_templates/orchestrator.html` as the canonical layout:
   - semantic HTML structure
   - Level 1 and Level 2 sections
   - `details/summary` for deep sections
   - Mermaid blocks for diagrams
   - D3 SVG container(s) for interactive graphs
12) Implement `tools/docs/render_orchestrator.py` to render HTML from template + JSON data.
13) Implement `tools/docs/generate_docs.py` to generate:
   - `docs/orchestrators/<name>.html`
   - `docs/orchestrators/index.html` listing all orchestrators
   - `docs/search-index.json` (optional but recommended)

**Phase 5 — Quality gates**
14) Add generation checks:
   - schema validation passes
   - no orphan `.bak` files left in active directories
   - all orchestrators have Level 1 and Level 2 sections
   - pages load shared assets and avoid per-page duplicated CSS
15) Document the pipeline in `docs/README.md` and include commands to regenerate docs locally and in CI.

**Implementation Rules**
- Prefer data-driven generation. Do not hand-write huge HTML pages.
- Keep Mermaid for static diagrams; use D3 for interactive graphs.
- Use modern HTML features: `details/summary`, `dialog`, `popover` (with fallback), `content-visibility`.
- Enforce the status color scheme (green/orange/red/grey) via CSS variables and `data-state` attributes.
- Create and maintain a VS Code Copilot Todo list and keep it updated as tasks complete or scope changes.
- Commit in small increments; each increment must run generation successfully.

**Deliverables**
- Schema + validators
- Python scripts under `tools/docs/`
- Shared assets under `docs/assets/`
- Template(s) under `docs/_templates/`
- Generated orchestrator pages under `docs/orchestrators/`
- Updated `docs/README.md` describing the workflow

---

## 7. Recommended Todo list breakdown (what Copilot should create)

1) Inventory current docs structure + identify “approved Level 1” baseline page(s)  
2) Locate or create doc generator scripts in `tools/docs/`  
3) Define orchestrator schema + validator  
4) Create shared CSS tokens + base layout template  
5) Build signal collector + Truth Panel JSON outputs  
6) Implement renderer + generator entrypoint  
7) Implement D3 graphs + dialog drilldowns + accessibility  
8) Reconcile `.bak` pages + rebuild orchestrator index  
9) Add optional search index  
10) Update docs/README.md and add CI check step

---

## 8. Outcome definition (acceptance criteria)

The work is done when:
- Running `python tools/docs/generate_docs.py --all` reliably regenerates all orchestrator pages.
- Every orchestrator page contains:
  - Level 1 view (consistent layout)
  - Level 2 view (deep technical content + diagrams + truth panel)
  - D3 interactive graphs with dialog drilldowns
- Status colors are consistent across site using CSS variables and `data-state`.
- `.html.bak` pages are either promoted to active pages or removed, with navigation updated.
- Documentation generation is deterministic, schema-validated, and reproducible.

---
