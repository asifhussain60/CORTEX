# CORTEX Documentation - Automated Discovery, Generation & Cleanup
**Authority:** cortex-impl-map.yaml | **Updated:** 2026-02-25 | **Status:** ✅ PRODUCTION READY  
**Playbook:** `cortex-registry/playbooks/documentation/cortex-docs-playbook.yaml` | **Phase Planning:** `cortex-registry/planning/phases/`

---

## ⚠️ CRITICAL: Response Header + Implementation Truth (TIER 0)

**EVERY response MUST begin with:**
```markdown
## 🧠 CORTEX Documentation
**Author:** Asif Hussain | **Orchestrator:** DocumentationOrchestrator ✅

---
```

**DOCUMENTATION WITH IMPLEMENTATION TRUTH (CORE-030):**
1. **VERIFY IMPLEMENTATION:** Use grep_search/read_file to check actual code
2. **CHECK TEST ISOLATION:** Ensure no test data contamination
3. **VALIDATE API METHODS:** Confirm method names exist in implementation
4. **DOCUMENT WHAT EXISTS:** Only document verified, implemented features

---

## 🎯 Purpose

**CORTEX Documentation** is a comprehensive documentation orchestration system that:

1. **Discovers** new components from codebase analysis
2. **Catalogs** modules with metadata and capabilities
3. **Generates** documentation with mermaid & D3.js diagrams
4. **Validates** mkdocs site integrity and links
5. **Cleans** obsolete, redundant, and duplicate files
6. **Maintains** documentation currency and consistency

---

## 🔄 CORTEX LENS → DoR → Approval Protocol

### One-Shot End-to-End Execution Model

This prompt implements a **unified one-shot execution** model:

**Step 1: Intent Reflection**

Render BLOCK-INTENT-REFLECTION from `.github/templates/cortex-response-templates.md`
§ Intent Reflection Block — plain business language, no technical table.

**Here's what CORTEX heard:**

You've asked CORTEX to perform a full fresh generation of the documentation site:

1. **Scan and discover** — analyse the codebase to inventory all orchestrators, MCP tools, and governance rules that need documentation coverage.
2. **Generate all content** — produce complete markdown documentation across all sections, fresh from source.
3. **Build and validate** — compile the site in strict mode (zero warnings, zero errors) and verify every internal link resolves.
4. **Commit and publish** — stage all output, commit with a conventional message, and push to the current branch.

**CORTEX's confidence in this understanding:** 🟢 High

> ✅ This looks right? Type `proceed`. Need to correct something? Do it now before CORTEX acts.

**Step 2: Wait for User Approval**
- Accept: "proceed", "yes", "approve", "go ahead", "do it"
- Reject: "no", "cancel", "stop", "abort"

**Step 3-10: Automatic End-to-End Execution (NO USER INTERACTION)**
Once approved, execute ALL phases without stopping:
1. **DISCOVERY** → Scan codebase for components
2. **GENERATION** → Generate all markdown documentation
3. **DIAGRAMS** → Generate Mermaid + D3.js diagrams (10 total)
4. **BUILD** → mkdocs build --strict (ZERO warnings/errors)
5. **VALIDATION** → Validate all links and references
6. **REPORTING** → Generate completion report
7. **POST-CLEANUP** → Delete legacy markdown files (final cleanup)
8. **GIT-COMMIT** → Final git commit with all changes

---

## 🎯 Commands

| Command | Action | Execution |
|---------|--------|-----------|
| `/doc-fresh-generate` | Fresh generation: DISCOVERY → GENERATION → DIAGRAMS → BUILD → VALIDATION → REPORTING → POST-CLEANUP → GIT-COMMIT | End-to-End (No stops) |
| `/doc-refresh` | Data-driven site refresh: Discover → Generate JSON catalogs → Validate → Deploy | Full pipeline (DOC-REFRESH-001) |
| `/doc-discover` | Discovery only — surface git/registry/live code gaps | Discovery phase only |
| `/doc-validate` | Validation only — CSS zero-inline, link check, responsive test | Validation phase only |
| `/doc-consolidate` | Consolidate flat-files: merge overlapping content, reduce file count, unify voice, remove code snippets | Content consolidation pipeline |

---

## 📦 Content Consolidation Pipeline (`/doc-consolidate`)

**Purpose:** Reduce flat-files/ from many granular files to fewer comprehensive documents without losing any content. Applies consistent descriptive language throughout, removes raw code snippets, and eliminates cross-file duplication.

### Consolidation Principles

1. **Zero content loss** — every concept, metric, and explanation from the source files must appear in the consolidated output
2. **Descriptive language only** — replace all code snippets with plain-language descriptions of what the code does, how it works, and why it matters
3. **Consistent voice** — third-person, professional, accessible; use brain analogies sparingly and consistently; three-role perspective (Business Leader, Product Owner, Developer) woven into narrative, not callout boxes
4. **Single authority per topic** — each concept appears in exactly one file; cross-references link rather than duplicate
5. **Flat-file naming** — consolidated files use `nn-section-topic.md` convention

### Consolidation Map (64 → 12 files)

| Section | Source Files (Current) | Consolidated File | Rationale |
|---------|----------------------|-------------------|-----------|
| **00 Getting Started** | `one-pager`, `how-cortex-works`, `key-concepts`, `cortex-intelligence`, `brain-tier-architecture`, `intelligence-matrix`, `inventory`, `quick-start` (8 files) | `00-platform-overview.md` | One-pager, how-it-works, and key-concepts heavily overlap on request flow, orchestrator counts, and architecture diagrams |
| | | `00-intelligence-architecture.md` | Brain tiers, intelligence matrix, and cortex-intelligence all describe the Perception→Reasoning→Action pipeline and LENS integration |
| | | `00-quick-start.md` | Quick start is procedural (how-to) — distinct from explanatory content |
| **01 Capabilities** | `overview`, `core-platform`, `ai-intelligence`, `decisioning`, `governance-compliance`, `response-formatting`, `workflow-templates`, `workflow-template-tiers`, `extensibility` (9 files) | `01-capabilities.md` | Overview + core-platform + ai-intelligence + decisioning + extensibility describe the six capability domains — one file with six sections |
| | | `01-governance-workflows.md` | Governance-compliance + workflow-templates + workflow-template-tiers + response-formatting are the operational enforcement layer |
| **02 LENS** | `overview`, `architecture`, `analyzers`, `synthesis`, `caching`, `company-domain-synthesis`, `governance-integration` (7 files) | `02-lens-intelligence.md` | All 7 files describe the same subsystem; overview + architecture + analyzers are the core, synthesis/caching/governance-integration are aspects |
| **03 Orchestration** | `overview`, `core-architecture`, `master-orchestrator`, `intent-router`, `tdd-orchestrator`, `domain-orchestrators`, `workflow-engine`, `security-orchestrator`, `sweep-catalogue`, `request-rephrase`, `cross-orchestrator`, `end-to-end-flow` (12 files) | `03-orchestration-system.md` | Overview + core-architecture + master-orchestrator + intent-router + end-to-end-flow + cross-orchestrator + request-rephrase describe the dispatch model |
| | | `03-orchestration-reference.md` | TDD, domain, workflow-engine, security, sweep-catalogue are individual orchestrator deep-dives |
| **04 MCP** | `overview`, `protocol`, `tools-catalog`, `integration`, `versioning`, `work-item-integration` (6 files) | `04-mcp-gateway.md` | All 6 describe the MCP layer; overview + protocol + tools-catalog are the core; integration + versioning + work-items are extensions |
| **05 Infrastructure** | `overview`, `tech-stack`, `deployment`, `ci-cd`, `observability`, `scalability`, `ado-integration` (7 files) | `05-infrastructure.md` | All 7 describe operational infrastructure — one cohesive file with sections |
| **06 FAQ** | `general`, `orchestration`, `governance-tdd`, `lens-intelligence`, `mcp-integration`, `testing-workflow`, `business-product` (7 files) | `06-faq.md` | All 7 are Q&A format on different topics — one unified FAQ with topic headings |
| **07 Diagrams** | `overview`, `high-level-architecture`, `request-flow`, `orchestrator-map`, `lens-pipeline`, `governance-flow`, `mcp-transport`, `testing-pyramid`, `brain-tier-model`, `golden-test-taxonomy` (10 files) | `07-diagrams.md` | Overview is a thin index; each diagram file is a single diagram with description — consolidate into one illustrated reference |

### Execution Steps (autonomous after approval)

1. **Read** all source flat files in the section
2. **Extract** every unique concept, metric, table, and explanation
3. **Deduplicate** — identify content that appears in multiple files
4. **Merge** into the consolidated file using consistent descriptive prose
5. **Remove code snippets** — replace with descriptions of behavior
6. **Write** consolidated file to `flat-files/`
7. **Delete** superseded source files from `flat-files/`
8. **Mirror** changes to `.content/` source folders (update source-of-truth)
9. **Validate** — no broken cross-references, all concepts preserved
10. **Git commit** — `docs: consolidate flat-files 64→12 — zero content loss`

---

## � Planning & Phase Management

**Playbook Authority:** `cortex-registry/playbooks/documentation/cortex-docs-playbook.yaml`  
**Planning Authority:** `cortex-registry/planning/phases/_template.yaml`

### Phase-Based Planning Workflow

All CORTEX documentation improvements follow a structured phase planning approach:

1. **Identify Need** — User request, Vision API analysis, audit finding, performance issue
2. **Create Phase Plan** — Use `cortex-registry/planning/phases/_template.yaml` scaffold
   - Write ALL detail in dedicated file: `cortex-registry/planning/phases/planned/<phase-id>.yaml`
   - Register thin reference in playbook `active_phases` section
   - Validate YAML syntax and THIN INDEX CONTRACT compliance
3. **TDD Execution** — RED → GREEN → REFACTOR with test suite in `tests/cortex_docs/`
4. **Validation** — Tests pass, accessibility ≥90, performance ≥85, zero inline styles
5. **Completion** — Mark phase COMPLETE, move to `completed/`, update playbook

**Active Phases:**
- `phase-index-html-redesign` — Modern glassmorphism UI with Google Fonts (P1, PLANNED)

**Planning Checkpoints:**
- **checkpoint_create:** Before adding phase — validate dedicated file, thin playbook entry, YAML syntax
- **checkpoint_complete:** Before marking COMPLETE — all AC met, tests passing, file moved to completed/

**Phase Planning Location:** `cortex-registry/planning/phases/`  
**Playbook Coordination:** All phases registered in `cortex-docs-playbook.yaml` `active_phases` section

---

## 🔄 Automated Refresh Pipeline (GitHub Pages Site)

**Workflow Authority:** `cortex-registry/workflows/templates/internal/documentation-refresh-pipeline.yaml`  
**Workflow ID:** DOC-REFRESH-001  
**Playbook:** `cortex-registry/playbooks/documentation/cortex-docs-playbook.yaml`

### Site Architecture (Canonical — Phase 64+)

```
cortex-docs/
├── index.html                    ← SINGLE entry point (role selector — 4 roles)
├── roles/                        ← Role-specific landing pages
│   ├── business-leader.html
│   ├── product-owner.html
│   ├── software-engineer.html
│   └── learner.html              ← 🎓 Curious Learner learning hub
├── learning/                     ← Structured learning tracks
│   ├── index.html                ← Track selector
│   ├── beginner/index.html       ← 8 weeks · 12 modules
│   ├── intermediate/index.html   ← 10 weeks · 15 modules
│   └── advanced/index.html       ← 12 weeks · 18 modules
├── data/                         ← JSON data layer (auto-generated, CORE-002 compliant)
│   ├── content.json              ← From .content/ markdown extraction
│   ├── knowledge-catalog.json    ← From cortex-registry/knowledge/*.yaml
│   ├── learning-paths.json       ← 3-track module metadata
│   ├── orchestrators.json        ← 51 orchestrator cards
│   └── mcp-tools.json            ← 39 MCP tool catalog (29 registered)
├── pipeline/                     ← Discovery & generation scripts
│   ├── discover.py               ← Git + registry + live code scan
│   ├── build.py                  ← YAML → JSON transformer
│   ├── extract-json.py           ← .content/ → content.json
│   ├── extract.py
│   └── validate.py               ← CSS, links, responsive, schema checks
└── assets/css|js|diagrams/       ← Design system (glassmorphism)
```

**⛔ DEPRECATED PATHS (never reference in new code):**
- `cortex-docs/views/` → migrated to `cortex-docs/roles/`
- `cortex-docs/business/`, `product/`, `engineering/` → removed in pre-docgen-restructure commit

### Pipeline Stages (DOC-REFRESH-001)

| Stage | Name | Trigger | Orchestrator |
|-------|------|---------|--------------|
| 0 | Pre-Flight Governance Check | Always | EnforcementOrchestrator |
| 1 | Discovery | full, discovery | DocumentationOrchestrator |
| 2 | Generation | full, generation | DocumentationOrchestrator |
| 3 | Validation | full, validation | EnforcementOrchestrator |
| 4 | Deployment | full only | GitOrchestrator |

**Triggers:**
- Manual: `/doc-refresh` command or `cortex_doc_refresh` MCP tool
- Automated: Push to `cortex-registry/knowledge/**`, `cortex-registry/cortex-master.yaml`, `cortex/**/*.py`
- Cron: Weekly Sunday 02:00 UTC

**Zero Manual Intervention** — runs autonomously on trigger (CORE-049).

### Agent Collaboration Matrix

| Agent | Role in Doc Pipeline | Workflow Stage |
|-------|---------------------|----------------|
| `cortex-documentation-architect.md` | Content extraction + `.content/` generation | Stage 1, 2 |
| `cortex-gitpages-builder.md` | JSON catalog → HTML rendering, site validation | Stage 2, 3 |
| `cortex-auditor.md` | CSS zero-inline validation, link checking | Stage 0, 3 |
| `cortex-vacuum.md` | Cleanup deprecated HTML files, stale assets | Post-deployment |

### Quality Gates (enforced per pipeline run)

| Gate | Expect | Severity |
|------|--------|----------|
| `grep -r 'style=' cortex-docs/**/*.html` | 0 matches | P0 |
| `grep -r '<style' cortex-docs/**/*.html` | 0 matches | P0 |
| `jq length cortex-docs/data/orchestrators.json` | 27 | P1 |
| `jq length cortex-docs/data/mcp-tools.json` | 26 | P1 |
| `jq '.tech_stacks | length' cortex-docs/data/knowledge-catalog.json` | ≥30 | P1 |
| Internal link checker | 0 broken | P1 |
| CSS zero-inline (all HTML) | 0 violations | P0 |
| CSS zero-style-blocks (all HTML) | 0 violations | P0 |
| Generated image placeholders present | Per-role coming-soon SVG | P1 |

---

## 🎨 CSS Enforcement Standards (P0 — Zero Tolerance)

**All CSS must live in `.css` files under `cortex-docs/assets/css/`. No exceptions.**

| Rule | Description | Severity |
|------|-------------|----------|
| **No `style=` attributes** | Zero inline `style=` in any HTML element | P0 |
| **No `<style>` blocks** | Zero `<style>...</style>` blocks in any HTML file | P0 |
| **External CSS only** | All styles via `<link rel="stylesheet" href="assets/css/...">` | P0 |
| **Design token usage** | Use CSS custom properties from `glass-design-tokens.css` | P1 |

**Validation commands:**
```bash
# P0: Zero inline styles
grep -rn 'style=' cortex-docs/roles/**/*.html cortex-docs/*.html
# P0: Zero style blocks
grep -rn '<style' cortex-docs/roles/**/*.html cortex-docs/*.html
# Expected: 0 matches for both
```

**Remediation:** Extract all inline/block CSS to the appropriate layout CSS file:
- `business-leader.html` → `assets/css/layouts/business-leader.css`
- `product-owner.html` → `assets/css/layouts/product-owner.css`
- `software-engineer.html` → `assets/css/layouts/software-engineer.css`
- `learner.html` → `assets/css/layouts/learning-path.css`

---

## 📐 D3.js & Mermaid Diagram Standards

**All interactive diagrams must be large, centered, and visually prominent.**

### Sizing Rules
| Container Type | Min Height | Min Width | Centering |
|---------------|-----------|-----------|-----------|
| D3.js chart panel | `400px` | `100%` of parent | `margin: 0 auto` via CSS class |
| Mermaid diagram | `350px` | `100%` of parent | `text-align: center` via CSS class |
| Hero diagram (full-width) | `500px` | `100%` viewport | CSS grid full-span |

### CSS Classes (defined in `glassmorphism.css` or layout CSS)
```css
.diagram-panel {
    min-height: 400px;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 2rem 0;
}

.diagram-panel svg {
    width: 100%;
    max-width: 1200px;
    height: auto;
    min-height: 350px;
}
```

### Role-Specific Diagram Strategy

| Role | D3.js Interactive | Mermaid Static | DALL-E Generated Images |
|------|------------------|----------------|------------------------|
| **Software Engineer** | ✅ REQUIRED — inner workings, architecture deep-dives | ✅ REQUIRED — sequence diagrams, class diagrams | 🎨 Hero/banner only — never replaces technical diagrams |
| **Business Leader** | ⚡ Optional — can be replaced by generated images | ⚡ Optional — can be replaced | ✅ PREFERRED — executive infographics, ROI dashboards |
| **Product Owner** | ⚡ Optional — can be replaced by generated images | ⚡ Optional — can be replaced | ✅ PREFERRED — sprint dashboards, pipeline flows |
| **Learner** | ⚡ Optional — can be replaced by generated images | ⚡ Optional — can be replaced | ✅ PREFERRED — journey maps, concept maps |

**Rule:** Software Engineer views MUST retain D3.js and Mermaid for technical accuracy. Other roles may use DALL-E-generated images for visual impact.

---

## 🖼️ DALL-E Image Prompt Generation System

### Purpose
Generate high-value visual assets for cortex-docs role views using ChatGPT DALL-E. Image prompts are stored as `.prompt.md` files; generated images replace coming-soon placeholders at the same path.

### Folder Structure
```
cortex-docs/assets/
├── doc-image-prompts/              # DALL-E prompt files (.prompt.md)
│   ├── business-leader/            # BL-specific: ROI dashboards, governance shields
│   ├── product-owner/              # PO-specific: sprint dashboards, pipelines
│   ├── software-engineer/          # SE: hero/banner ONLY (keeps D3/Mermaid)
│   ├── learner/                    # Learner: journey maps, concept maps
│   └── shared/                     # Cross-role: architecture overview, LENS pipeline
├── images/generated/               # Output images (PNG/SVG)
│   ├── business-leader/            # Production-named placeholder PNGs (1:1 with prompts)
│   ├── product-owner/              # Production-named placeholder PNGs (1:1 with prompts)
│   ├── software-engineer/          # Production-named placeholder PNGs (1:1 with prompts)
│   ├── learner/                    # Production-named placeholder PNGs (1:1 with prompts)
│   ├── shared/                     # Production-named placeholder PNGs (1:1 with prompts)
│   ├── coming-soon-placeholder.png # Master placeholder PNG (root reference)
│   └── coming-soon-placeholder.svg # Master placeholder SVG (root reference)
```

### Image Prompt File Format
```markdown
# CORTEX Image Prompt: {Title}
# Role: {role}
# Output: cortex-docs/assets/images/generated/{role}/{filename}.png
# Size: 1200x675 (16:9 landscape)
# Style: Dark glassmorphism, {audience-specific qualities}

## DALL-E Prompt
{Detailed prompt text with color codes, layout description, style guidance}
```

### Production-Named Placeholder Strategy
- Every `images/generated/{role}/` folder contains **production-named `.png` placeholders** (copies of `coming-soon-placeholder.png`)
- Placeholder filenames match the `# Output:` path in the corresponding `.prompt.md` file exactly
- **1:1 parity rule:** `count(images/generated/{role}/*.png) == count(doc-image-prompts/{role}/*.prompt.md)` — no orphans, no gaps
- **Drop-in replacement:** Generate DALL-E image → save/overwrite the `.png` at the same path → zero HTML/CSS/JS changes
- Master placeholders (`coming-soon-placeholder.svg` + `.png`) remain at `images/generated/` root as reference only

### HTML Embedding Pattern
```html
<div class="generated-image-panel">
    <img src="assets/images/generated/{role}/{image-name}.png"
         alt="{Descriptive alt text}"
         class="generated-diagram"
         loading="lazy">
    <p class="image-caption">{Caption text}</p>
</div>
```

### Enforcement Rules
| Rule | Description | Severity |
|------|-------------|----------|
| **High-value generation** | Every role view must have ≥2 image prompts | P1 |
| **1:1 parity** | Each prompt file has a matching production-named `.png` placeholder; counts must match per role | P0 |
| **SE D3/Mermaid preserved** | Software Engineer views never replace D3/Mermaid with images | P0 |
| **Prompt file per image** | Each generated image has a corresponding `.prompt.md` file | P1 |
| **Design consistency** | All prompts specify dark navy (#0a0e27) glassmorphism theme | P1 |
| **Production naming** | Placeholder PNGs use the same filename as the DALL-E output — not a generic `coming-soon-*` copy | P1 |

---

## 📄 `.content/` Template Integration

### Pipeline: `.content/` → `content.json` → HTML Views

**Canonical content source:** `cortex-docs/.content/` (markdown files organized by topic)

**Pipeline stages:**
1. `cortex-documentation-architect.md` generates/updates `.content/*.md` files
2. `pipeline/extract-json.py` extracts structured data → `data/content.json`
3. `cortex-gitpages-builder.md` renders HTML views from `content.json` + templates
4. HTML views reference CSS files, D3.js libraries, and generated images

**Template wiring rules:**
- HTML views load content dynamically via `content-loader.js` or embed from `content.json`
- Role-specific pages use pre-built CSS layouts from `assets/css/layouts/`
- Diagrams embedded as D3.js `<script>` blocks (SE) or `<img>` tags (BL/PO/Learner)
- Content updates only require re-running `extract-json.py` — no HTML file changes

---

## 🎯 7-Phase End-to-End Execution Pipeline

Once user approves with "proceed" or "yes", execute ALL phases automatically via **WorkflowComposer** delegation.

### Workflow Templates (SSOT — never inline execution logic in prompts/agents)

| Phase | Workflow Template | Composer Step |
|-------|------------------|---------------|
| 1. DISCOVERY | `internal/documentation-refresh-pipeline.yaml` (Stage 1) | `content_extraction` |
| 2. GENERATION | `internal/documentation-refresh-pipeline.yaml` (Stage 2) | `content_extraction` |
| 2b. FLAT-FILE SYNC | `maintenance/doc-flat-file-sync.yaml` | `flat_file_sync` |
| 3. DIAGRAMS | `internal/documentation-refresh-pipeline.yaml` (Stage 2) | `asset_validation` |
| 4. BUILD | `frontend/html-view-lifecycle.yaml` → `build` operation | `html_modification` |
| 5. VALIDATION | `frontend/html-view-lifecycle.yaml` → `validate` operation | `convergence_gate` |
| 6. CLEANUP | `maintenance/cleanup-deduplication.yaml` | `cleanup` |
| 7. GIT-COMMIT | `internal/documentation-refresh-pipeline.yaml` (Stage 4) | `deployment` |

### Invocation

```python
from pathlib import Path
from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer

# Full doc-refresh pipeline
composer = WorkflowComposer(
    template_path=Path("cortex-registry/workflows/templates/internal/documentation-refresh-pipeline.yaml")
)
result = composer.execute()

# HTML view build/enhance/refactor
composer = WorkflowComposer(
    template_path=Path("cortex-registry/workflows/templates/frontend/html-view-lifecycle.yaml")
)
result = composer.execute()  # Runs: preflight → content → HTML → CSS → assets → convergence
```

### Phase Execution Rules

- **All HTML modifications** route through `frontend/html-view-lifecycle.yaml` — never edit HTML inline in prompts
- **CSS compliance** enforced by `frontend/css-zero-inline-workflow.yaml` (delegated from lifecycle)
- **DOM validation** enforced by `frontend/html-refactor-validation.yaml` (delegated from lifecycle)
- **Visual regression** captured via Vision API baseline → compare (delegated from lifecycle)
- **Convergence gate** (CORE-068): detect→fix→rescan loop until 0 P0/P1 violations

### Discovery Orchestrator Scan Targets

```yaml
orchestrator_discovery:
  scan: cortex/orchestrators/
  source_of_truth: cortex-registry/core/specifications/  # wiring YAML files

mcp_tool_discovery:
  scan: cortex/mcp/tools/

governance_discovery:
  scan: cortex-registry/core/  # ✅ CANONICAL (cortex_brain/ is DELETED)

sts_app_discovery:
  scan: _workspaces/sts/sample-apps/_Real/
```
### Generated Content Locations

- `cortex-docs/.content/00-getting-started/` - Installation, quickstart
- `cortex-docs/.content/01-capabilities/` - Platform capabilities (8 files)
- `cortex-docs/.content/02-lens/` - LENS intelligence pipeline
- `cortex-docs/.content/03-orchestration/` - 51 wired orchestrators across 4 tiers (10 files)
- `cortex-docs/.content/04-mcp/` - 39 MCP tools catalog (29 registered) (6 files)
- `cortex-docs/.content/05-infrastructure/` - Deployment, observability
- `cortex-docs/.content/07-diagrams/` - Architecture diagrams (9 files)
- `cortex-docs/.content/glossary.md` - Terminology reference

### Flat-File Sync

**Workflow template:** `cortex-registry/workflows/templates/maintenance/doc-flat-file-sync.yaml`

Mirrors `.content/<nn-category>/` → `cortex-docs/.content/flat-files/` using `nn-{foldername}-{descriptive}.md` naming.
Runs automatically after GENERATION. Flat-files are derived — never edit directly.

### Execution Rules

- **NO STOPPING, NO CHOICES, NO PAUSES** — fully automated end-to-end pipeline
- All phases delegated to WorkflowComposer via YAML templates
- `AC_START` logged at entry, `AC_COMPLETE` at exit
- CORE-068 convergence gate applied before final commit

---

## �️ STS Sample Application Documentation

### Scope

The **Software Transformation Studio (STS)** sample apps live at `_workspaces/sts/sample-apps/_Real/`.
When documenting STS workspaces, this agent applies the following rules:

**Canonical STS Structure:**
```
_workspaces/sts/sample-apps/_Real/
├── README.md                        ← Top-level STS index (REQUIRED)
├── account-modernized/
│   └── README.md                    ← App architecture + API reference (REQUIRED)
├── payment-processor-modernized/
│   └── README.md                    ← App architecture + API reference (REQUIRED)
├── account-api-specs/
│   ├── README.md                    ← Spec index with table of contents (REQUIRED)
│   └── specifications/*/diagrams/  ← .mmd diagram files
├── payment-api-specs/
│   ├── README.md                    ← Spec index with table of contents (REQUIRED)
│   └── specifications/*/diagrams/  ← .mmd diagram files
└── sts-architecture-d3.html        ← D3.js interactive dependency graph (REQUIRED)
```

### STS `.mmd` Diagram Standards

**CRITICAL syntax rules for all `.mmd` files in STS:**

```yaml
sequence_diagrams:
  keyword: participant     # ✅ CORRECT
  never: user              # ❌ INVALID — breaks Mermaid rendering
  required_participants: [Client, Controller, Service, Repository, Database]
  use_alt_block: true      # For conditional paths (balance check, peg logic)
  use_loop_block: true     # For batch operations (for each subaccountId)
  endpoint_format: "HTTP METHOD /api/v1/path"  # Not "Execute" or "API Invoked"

flowchart_diagrams:
  start_label: "HTTP METHOD /api/v1/path"   # ✅ Not "API Invoked"
  node_labels: full_english                  # ✅ No truncated labels (no "InvoiceAmount_less")
  decision_labels: plain_condition           # ✅ "invoiceAmount > 0?" not "Condition: InvoiceAmount LTE 0"
  error_nodes: include_http_status_codes     # ✅ "400 Bad Request: reason"
  success_nodes: include_http_status_codes   # ✅ "201 Created: ResponseDto"

dependency_diagrams:
  type: classDiagram                         # ✅ Use classDiagram not component diagram
  show_interfaces: true                      # IService, IRepository interfaces
  show_methods: true                         # Key public methods with return types
  show_relationships: implements|depends_on  # <|.. for implements, --> for depends on
  clean_architecture: true                   # Controller → Interface ← Implementation
```

### STS D3.js Interactive Diagram

Every STS workspace MUST include a `sts-architecture-d3.html` file providing an interactive
force-directed graph of the full clean-architecture dependency map across both domains:

```yaml
d3_diagram_requirements:
  file: sts-architecture-d3.html
  type: force-directed graph
  layers:
    - API: controllers (blue #63c7ff)
    - Core: service interfaces, repo interfaces, UoW (green #7ee787)
    - Infrastructure: EF Core repos, mock repos, DataLayerRouter (orange #ffa657)
    - Entity: domain entities (purple #d2a8ff)
    - Azure: Azure Key Vault, App Configuration, Application Insights (amber #f0883e)
  features:
    - Layer filter buttons (show/hide by layer)
    - Tooltip on hover (node description, tags, methods)
    - Drag nodes to rearrange
    - Zoom/pan (D3 zoom behavior)
    - Arrow markers per layer color
    - Glow filter for visual depth
  style: dark glassmorphism (#0d1117 background, rgba glass panels)
```

### STS Documentation Quality Gates

Before marking STS docs complete, verify:

| Check | Requirement |
|---|---|
| `README.md` exists | Every subdirectory has a README |
| `.mmd` syntax valid | No `user` keyword in sequenceDiagram — only `participant` |
| Truncated labels fixed | No `InvoiceAmount_less`, `stringIsNullOrEmptyc`, etc. |
| HTTP codes present | Error/success nodes include status codes |
| D3.js diagram present | `sts-architecture-d3.html` exists with all layers |
| Entities documented | Domain model diagrams use classDiagram with fields |
| HIPAA noted | PHI entity fields and audit trail marked |
| Canary rollout shown | DataLayerRouter + feature flag pattern documented |
| WCF origin mapped | Legacy class → REST endpoint mapping table present |

---

## 🎨 Diagram Generation System

### Diagram Locations

| Type | Location | Count |
|------|----------|-------|
| Mermaid (static) | `cortex-docs/.content/07-diagrams/` | 6 diagrams |
| D3.js (interactive) | `cortex-docs/assets/diagrams/d3/` | 4 diagrams |

**Mermaid diagrams:** approval-gate-decision-tree, error-recovery-paths, circuit-breaker-state-machine, master-orchestrator-sequence, tdd-workflow-phases, governance-rule-categories

**D3.js visualizations:** governance-pyramid (sunburst), request-lifecycle-sankey, tdd-knowledge-cycle (circular), orchestrator-tier-map (layered)

**Generation:** Delegated to `internal/documentation-refresh-pipeline.yaml` Stage 2. Sizing and compliance enforced by `frontend/html-view-lifecycle.yaml` gates.

---

## 🧹 Documentation Cleanup Cycle

**Workflow template:** `cortex-registry/workflows/templates/maintenance/cleanup-deduplication.yaml`

| Trigger | Scope |
|---------|-------|
| `/doc-cleanup` | Manual — full redundancy scan + cleanup |
| Post-generation | Automatic — after every doc-refresh pipeline |
| Weekly cron | Sunday 02:00 UTC |

**Cleanup categories:** duplicate component docs, completion reports, session files, intermediate files, duplicate diagrams, obsolete features, redundant guidance

**Safety:** Dry-run mode, user confirmation required, git history preserved, rollback via `git revert`.

---

## 🔗 Integration Points

All orchestrators invoked via WorkflowComposer — not directly from prompts/agents.

| Component | Workflow Template |
|-----------|------------------|
| Content discovery + generation | `internal/documentation-refresh-pipeline.yaml` |
| HTML view build/enhance/refactor | `frontend/html-view-lifecycle.yaml` |
| CSS extraction + compliance | `frontend/css-zero-inline-workflow.yaml` |
| DOM validation + refactoring | `frontend/html-refactor-validation.yaml` |
| Flat-file sync | `maintenance/doc-flat-file-sync.yaml` |
| Cleanup + dedup | `maintenance/cleanup-deduplication.yaml` |
| Visual regression (Vision API) | `internal/cortex-site-validation.yaml` |

---

## 📊 Documentation Lifecycle

### Full Maintenance Cycle (`/doc-maintenance`)

Delegated to `internal/documentation-refresh-pipeline.yaml` (DOC-REFRESH-001):

1. **DISCOVERY** → Scan codebase for new components
2. **GENERATION** → Generate markdown + diagrams via `documentation-refresh-pipeline.yaml`
3. **VALIDATION** → CSS, links, responsive via `html-view-lifecycle.yaml` → `validate` operation
4. **CLEANUP** → Redundancy removal via `cleanup-deduplication.yaml`
5. **COMMIT** → Git commit with summary

---

## 📋 Approval Workflow

### Before Cleanup Execution

1. **Analyze Phase** (Automatic)
   - Scan for redundancies, orphans, obsolete content
   - Generate cleanup report
   
2. **Review Phase** (User approval required)

   Render BLOCK-INTENT-REFLECTION from `.github/templates/cortex-response-templates.md`
   § Intent Reflection Block — plain business language, no technical table.

   **Here's what CORTEX heard:**

   You've asked CORTEX to clean up the documentation folder:

   1. **Identify redundancies** — find duplicate, orphaned, and obsolete files across the docs tree ({n} files, {size} MB estimated).
   2. **Archive safely** — move redundant content to `_archive/` rather than deleting, preserving git history.
   3. **Validate the result** — confirm the site still builds cleanly after cleanup.
   4. **Commit the changes** — stage and commit all archived/removed files with a conventional message.

   **CORTEX's confidence in this understanding:** 🟢 High

   > ✅ This looks right? Type `proceed`. Need to correct something? Do it now before CORTEX acts.

3. **Execution Phase** (After approval)
   - Archive redundant files
   - Remove orphaned files
   - Update mkdocs.yml
   - Validate build
   - Commit changes

4. **Report Phase** (Final status)
   - Generate cleanup completion report
   - Show space freed
   - Provide rollback instructions

---

## ⚠️ Safety Guardrails

All cleanup operations include:
- ✅ Dry-run mode (show what would happen)
- ✅ User confirmation (require explicit approval)
- ✅ Git integrity (preserve history)
- ✅ Validation (verify mkdocs builds)
- ✅ Audit trail (log all changes)
- ✅ Rollback capability (easy git revert)

---

## 🚀 Phase 5: Fresh Documentation Generation

**Command:** `/doc-fresh-generate`

**Workflow template:** `internal/documentation-refresh-pipeline.yaml` (DOC-REFRESH-001)

### Pipeline Steps

1. **Pre-cleanup** — clear `docs/` except `serve-docs.bat`, `serve-docs.sh`, `_archive/`, `assets/`, `theme/`
2. **Generate markdown** — all `.content/` sections from codebase introspection
3. **Generate diagrams** — 6 Mermaid + 4 D3.js (see Diagram Locations table above)
4. **Build** — `mkdocs build --strict --clean` (ZERO warnings, ZERO errors)
5. **Validate links** — all internal `href` references resolve
6. **Report** — inline completion summary (CORE-002)

### Key Guarantees

- ✅ Always fresh — clears docs/ before generation
- ✅ Serve scripts safe — never deletes `serve-docs.bat` / `serve-docs.sh`
- ✅ Zero warnings — `mkdocs --strict` enforcement
- ✅ Links verified — all internal references validated
- ✅ Reproducible — same output every run

### CLI

```bash
/doc-fresh-generate          # Full pipeline
/doc-maintenance             # Discovery + generation + validation + cleanup + commit
```

