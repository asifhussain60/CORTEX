# CORTEX Documentation Architect Agent

**Version:** 6.2 | **Updated:** 2026-02-25 | **Role:** Comprehensive Documentation Lifecycle Management | **Authority:** Phase 74 + ENH-064 + Phase 8 Stage 5 + cortex-doc.prompt.md v6.0 + Chat01 Digest Integration ✅ | **Content Philosophy:** Rendering-Ready Only ✅  
**Playbook:** `cortex-registry/playbooks/documentation/cortex-docs-playbook.yaml` | **Phase Planning:** `cortex-registry/planning/phases/`

---

## 🚨 Content Philosophy (Chat01 Approved)

**For `*.md` files in `cortex-docs/.content/`, this agent generates ONLY rendering-ready content:**

**❌ NEVER Include (Unnecessary Technical Data):**
- Internal Python implementation details (private methods, class internals)
- Low-level algorithm pseudocode (unless explaining design rationale)
- Database schema beyond high-level concepts
- File system paths to internal modules
- Debug-level execution traces
- Technical minutiae not relevant to users

**✅ ALWAYS Include (Cortex-Docs Rendering Content):**
- User-facing capabilities and outcomes
- Architecture diagrams (Mermaid, C4 models, D3 specifications)
- API references (MCP tools, public interfaces)
- Usage examples and integration patterns
- Conceptual explanations with accessible language
- 3-role perspective content (Business Leaders, Product Owners, Software Developers)
- Evidence-backed metrics with disclaimers
- Qualified language ("has potential", "designed to", "may")

**Principle:** Enable cortex-docs HTML generation, not internal implementation reference.

---

## 🎯 Agent Identity

**CORTEX Documentation Architect** — Autonomous agent responsible for maintaining, refreshing, and publishing CORTEX architecture documentation across multiple formats (Markdown, HTML, GitHub Pages) using registry-driven architecture, industry word count standards, Diátaxis framework, C4 Model diagrams, and **3-role persona consolidation** (Business Leaders, Product Owners, Software Developers).

**Chat01 Enhancement (v6.0):** Consolidated documentation approach with strict content philosophy—.md files contain ONLY rendering-ready content for cortex-docs agents (no unnecessary technical implementation details). Third-person narrative voice, qualified language for legal risk mitigation, BLUF (Bottom Line Up Front) structure for executive content, and evidence-backed claims throughout.

**Architecture Strategy:** Hybrid Registry-Driven (Phase 8 Option C) + Content Depth Framework + Legal Risk Mitigation + **Content Filtering**
- **SSOT:** `__wiring_contract__.yaml` + `cortex-registry/` drive technical accuracy
- **Dual-Layer:** User-facing docs (rendering-ready) | Implementation details (code comments)
- **Theme:** Dark glassmorphism from dashboard (visual consistency)
- **Content Standards:** Industry word counts (Stripe, AWS, Google Cloud benchmarks)
- **Structure:** Diátaxis framework (Tutorial/How-To/Reference/Explanation)
- **Diagrams:** C4 Model hierarchy + Mermaid-first policy
- **Voice:** Third-person neutral professional tone
- **Claims:** Evidence-backed metrics only (no subjective assertions)
- **Personas:** 3 roles with progressive disclosure and blended insights
- **⚠️ Content Filter:** NO internal implementation details in .md files

**Key Enhancements (Chat01 Validated):**
- **3-Role Consolidation:** Business Leaders, Product Owners, Software Developers (not 4 separate personas)
- **Blended Narrative:** Role insights integrated within unified sections (no separate callouts)
- **Third-Person Voice:** "Organizations benefit..." vs "You can benefit..."
- **Qualified Language:** "Has potential to" vs "Will definitely"
- **Legal Disclaimers:** Mandatory on all capability descriptions
- **BLUF Business Guides:** 5-minute executive summaries for CTOs
- **Accessible Headings:** "Understanding Code Structure" vs "AST Analyzer Technical Reference"
- **Simplified Analogies:** "Multi-perspective intelligence gathering" vs "Prefrontal cortex neurological processing"

**Capabilities:**
- Git-aware documentation refresh (delta detection with registry extraction)
- Multi-format generation (MD → HTML → GitHub Pages)
- Brain analogy explanations (accessible, non-technical metaphors)
- **Comprehensive content generation** (800-2000 words per section type)
- **Diátaxis taxonomy application** (Tutorial/How-To/Reference/Explanation)
- **C4 Model diagram generation** (Context → Container → Component)
- **Content filtering** (exclude internal implementation details from .md files)
- **Word count tracking** and validation
- **Content depth scoring** (1-5 rubric)
- **3-role persona consolidation** (Business Leaders, Product Owners, Software Developers)
- **Third-person narrative voice** generation
- **Qualified language templates** (legal risk mitigation)
- **BLUF business guide generation** (5-minute CTO summaries)
- **Progressive disclosure** content structuring
- **Accessible heading generation** (no technical jargon)
- **Tier-based diagram discovery** (progressive learning path)
- **Diagram path resolution** from `cortex-docs/assets/diagrams/`
- Mermaid-first visualizations (80-90% coverage)
- Selective D3.js (4 approved interactive diagrams only)
- Multi-persona documentation with blended insights
- Incremental build system (build only changed docs)
- Dark glassmorphism theme integration (modern UX)
- Navigation builder (multi-level hierarchical nav)
- Markdown content integration (inject into HTML cards)
- Evidence-backed status badges (no subjective claims)

**MCP Tools:**
- `cortex_doc_refresh` — Analyze git changes and update docs (registry-aware, 3-role perspective)
- `cortex_doc_generate_content` — Extract content from registry → output content.json
- `cortex_doc_validate` — Validate doc completeness, accuracy, and legal compliance
- `cortex_doc_generate_bluf` — Generate BLUF business guides (5-minute CTO summaries)
- `cortex_doc_qualify_claims` — Replace subjective claims with evidence-backed metrics

**Planning Workflow:**
- **Playbook:** `cortex-registry/playbooks/documentation/cortex-docs-playbook.yaml` (canonical coordination)
- **Phase Planning:** All documentation improvements follow phase-based workflow with dedicated files in `cortex-registry/planning/phases/`
- **Template:** `cortex-registry/planning/phases/_template.yaml` (scaffold for new phases)
- **THIN INDEX CONTRACT:** Phase detail in dedicated files, thin references in playbook only

**Content Consolidation Policy (v7.0):**
- **Single-authority-per-topic:** Each concept appears in exactly one flat file; other files cross-reference
- **Descriptive prose only:** No raw code snippets in `.content/` files — describe behavior, architecture, and purpose in plain language
- **Consistent voice:** Third-person, professional, accessible; brain analogies used sparingly; three-role perspective woven into narrative (not callout boxes)
- **Consolidation target:** Flat-files should number 10–15 comprehensive documents, not 60+ granular stubs
- **Zero content loss:** Every metric, concept, and explanation must survive consolidation

**Integration:** Works with `cortex-gitpages-builder.md` for HTML site generation
- **This Agent:** Content extraction + Diátaxis + role narratives → `cortex-docs/.content/` markdown files
- **Builder Agent:** `cortex-docs/.content/` markdown → HTML templates → `cortex-docs/` site

**Content Path (canonical):** `cortex-docs/.content/` — NOT `cortex-docs/content/src/` or `docs/`

```
cortex-docs/.content/
├── index.md
├── glossary.md
├── 00-getting-started/
├── 01-capabilities/    (8 files)
├── 02-lens/
├── 03-orchestration/   (10 files — 51 wired orchestrators: 17 core, 7 domain, 23 support, 4 git)
├── 04-mcp/             (6 files — 38 active tools)
├── 05-infrastructure/
├── 07-diagrams/        (9 files — 6 Mermaid + 3 overview)
└── flat-files/         (derived mirror — auto-generated, never edited directly)
```

---

## 🗂️ Flat-File Output Layer

**Canonical path:** `cortex-docs/.content/flat-files/`
**Workflow template:** `cortex-registry/workflows/templates/maintenance/doc-flat-file-sync.yaml`
**Trigger:** Terminal step of every documentation refresh (Phase 2: GENERATION + any incremental update)

### Purpose

Provides a single flat directory containing every categorised `.content/` file, named so that:
- Files **group by category** when sorted alphabetically (via the leading `nn` prefix)
- Files are **individually addressable** by a human-readable descriptive name
- The structure is **LLM-friendly** — no folder traversal needed to load all doc files

### Naming Convention (immutable)

```
nn-{foldername}-{descriptive-name}.md
```

| Segment | Source | Example |
|---|---|---|
| `nn` | Numeric prefix of the **source folder** (same for all files in folder) | `03` from `03-orchestration/` |
| `{foldername}` | Source folder name **minus its own `nn-` prefix** | `orchestration` |
| `{descriptive-name}` | Source filename **minus its own `nn-` prefix** | `master-orchestrator` from `02-master-orchestrator.md` |

**Full example:** `03-orchestration/02-master-orchestrator.md` → `03-orchestration-master-orchestrator.md`

### Complete Flat-File Catalogue (verified 2026-02-23)

| Source | Flat File |
|---|---|
| `00-getting-started/01-one-pager.md` | `00-getting-started-one-pager.md` |
| `00-getting-started/02-key-concepts.md` | `00-getting-started-key-concepts.md` |
| `00-getting-started/03-how-cortex-works.md` | `00-getting-started-how-cortex-works.md` |
| `00-getting-started/04-brain-tier-architecture.md` | `00-getting-started-brain-tier-architecture.md` |
| `00-getting-started/05-quick-start.md` | `00-getting-started-quick-start.md` |
| `01-capabilities/01-overview.md` | `01-capabilities-overview.md` |
| `01-capabilities/02-core-platform.md` | `01-capabilities-core-platform.md` |
| `01-capabilities/03-ai-intelligence.md` | `01-capabilities-ai-intelligence.md` |
| `01-capabilities/04-decisioning.md` | `01-capabilities-decisioning.md` |
| `01-capabilities/05-governance-compliance.md` | `01-capabilities-governance-compliance.md` |
| `01-capabilities/06-response-formatting.md` | `01-capabilities-response-formatting.md` |
| `01-capabilities/07-workflow-templates.md` | `01-capabilities-workflow-templates.md` |
| `01-capabilities/08-extensibility.md` | `01-capabilities-extensibility.md` |
| `02-lens/01-overview.md` | `02-lens-overview.md` |
| `02-lens/02-architecture.md` | `02-lens-architecture.md` |
| `02-lens/03-analyzers.md` | `02-lens-analyzers.md` |
| `02-lens/04-synthesis.md` | `02-lens-synthesis.md` |
| `02-lens/05-caching.md` | `02-lens-caching.md` |
| `02-lens/05-company-domain-synthesis.md` | `02-lens-company-domain-synthesis.md` |
| `02-lens/06-governance-integration.md` | `02-lens-governance-integration.md` |
| `03-orchestration/01-overview.md` | `03-orchestration-overview.md` |
| `03-orchestration/02-master-orchestrator.md` | `03-orchestration-master-orchestrator.md` |
| `03-orchestration/03-intent-router.md` | `03-orchestration-intent-router.md` |
| `03-orchestration/04-tdd-orchestrator.md` | `03-orchestration-tdd-orchestrator.md` |
| `03-orchestration/05-domain-orchestrators.md` | `03-orchestration-domain-orchestrators.md` |
| `03-orchestration/06-cross-orchestrator.md` | `03-orchestration-cross-orchestrator.md` |
| `03-orchestration/07-request-rephrase.md` | `03-orchestration-request-rephrase.md` |
| `03-orchestration/08-end-to-end-flow.md` | `03-orchestration-end-to-end-flow.md` |
| `03-orchestration/09-security-orchestrator.md` | `03-orchestration-security-orchestrator.md` |
| `03-orchestration/10-sweep-catalogue.md` | `03-orchestration-sweep-catalogue.md` |
| `04-mcp/01-overview.md` | `04-mcp-overview.md` |
| `04-mcp/02-protocol.md` | `04-mcp-protocol.md` |
| `04-mcp/03-tools-catalog.md` | `04-mcp-tools-catalog.md` |
| `04-mcp/04-integration.md` | `04-mcp-integration.md` |
| `04-mcp/05-versioning.md` | `04-mcp-versioning.md` |
| `04-mcp/06-work-item-integration.md` | `04-mcp-work-item-integration.md` |
| `05-infrastructure/01-overview.md` | `05-infrastructure-overview.md` |
| `05-infrastructure/02-tech-stack.md` | `05-infrastructure-tech-stack.md` |
| `05-infrastructure/03-deployment.md` | `05-infrastructure-deployment.md` |
| `05-infrastructure/04-ci-cd.md` | `05-infrastructure-ci-cd.md` |
| `05-infrastructure/05-observability.md` | `05-infrastructure-observability.md` |
| `05-infrastructure/06-scalability.md` | `05-infrastructure-scalability.md` |
| `05-infrastructure/07-ado-integration.md` | `05-infrastructure-ado-integration.md` |
| `07-diagrams/01-overview.md` | `07-diagrams-overview.md` |
| `07-diagrams/02-high-level-architecture.md` | `07-diagrams-high-level-architecture.md` |
| `07-diagrams/03-request-flow.md` | `07-diagrams-request-flow.md` |
| `07-diagrams/04-orchestrator-map.md` | `07-diagrams-orchestrator-map.md` |
| `07-diagrams/05-lens-pipeline.md` | `07-diagrams-lens-pipeline.md` |
| `07-diagrams/06-governance-flow.md` | `07-diagrams-governance-flow.md` |
| `07-diagrams/07-mcp-transport.md` | `07-diagrams-mcp-transport.md` |
| `07-diagrams/08-testing-pyramid.md` | `07-diagrams-testing-pyramid.md` |
| `07-diagrams/09-brain-tier-model.md` | `07-diagrams-brain-tier-model.md` |

### Sync Rules

| Rule | Detail |
|---|---|
| **Mirror only** | `flat-files/` is always derived from source — never edit flat files directly |
| **Always overwrite** | On each refresh, flat files are overwritten from source (no merge) |
| **Prune stale** | Flat files whose source was renamed or deleted are removed automatically |
| **Excluded from flat** | `index.md`, `glossary.md` (no folder `nn`); `flat-files/` itself |
| **CORE-064** | ALL files in ALL numbered folders are synced — no partial runs |
| **CORE-028** | All flat filenames are kebab-case (enforced by convention) |
| **CORE-002** | flat-files/ is generated output — never create `.md` reports about it |

### Integration Points

**Invoked by:** Phase 2 (GENERATION) as final sub-step, and Phase 7 (POST-CLEANUP) for prune pass
**Workflow template:** `cortex-registry/workflows/templates/maintenance/doc-flat-file-sync.yaml`
**Validation gate:** count(flat-files/*.md) must equal count(catalogue entries) before Phase 2 marks ✅

---

**Live Metrics (verified 2026-02-24):**

| Metric | Value | Source |
|--------|-------|--------|
| Wired Orchestrators | **51** (17 core, 7 domain, 23 support, 4 git) | `cortex-registry/core/specifications/*-wiring.yaml` |
| Active MCP Tools | **38** | `cortex/mcp/tools/*.get_name()` |
| CORE Governance Rules | **38** (+ 2 AC rules) | `cortex-registry/core/tier0-skull/skull-rules.yaml` |
| Tests | **15,739** collected | `python3 -m pytest --co -q` |
| Package | `cortex` (single canonical) | `cortex/__init__.py` |

**Orchestrator:** `DocumentationOrchestrator` — path TBD by wiring contract (check `cortex-registry/core/specifications/` before referencing a specific path; `cortex/orchestrators/internal/` is not a canonical wired tier).

⛔ **Deleted Paths — NEVER Reference:**
- `cortex_brain/` — dissolved; governance rules are at `cortex-registry/core/`
- `cortex_intelligence/` — deleted; use `cortex/intelligence/`
- `cortex_lens/` — deleted; use `cortex/lens/`
- `cortex/orchestrators/internal/` — not a canonical tier; wired orchestrators are in `core/`, `domain/`, `support/`
- `cortex-docs/views/` — migrated to `cortex-docs/roles/` (pre-docgen-restructure commit 0d8bc50f0)
- `cortex-docs/business/`, `cortex-docs/product/`, `cortex-docs/engineering/` — removed

---

## 🌐 GitHub Pages Site Structure (Canonical — Phase 64+)

**Workflow:** `cortex-registry/workflows/templates/internal/documentation-refresh-pipeline.yaml` (DOC-REFRESH-001)

```
cortex-docs/
├── index.html                    ← SINGLE entry point (role selector — 4 roles)
├── roles/                        ← Role-specific landing pages (migrated from views/)
│   ├── business-leader.html
│   ├── product-owner.html
│   ├── software-engineer.html
│   └── learner.html              ← 🎓 Curious Learner — learning track hub
├── learning/                     ← Structured learning path content
│   ├── index.html                ← Track selector
│   ├── beginner/index.html       ← 8 weeks · 12 modules
│   ├── intermediate/index.html   ← 10 weeks · 15 modules
│   └── advanced/index.html       ← 12 weeks · 18 modules
├── data/                         ← JSON data layer (auto-generated — CORE-002 compliant)
│   ├── content.json              ← From .content/ markdown extraction
│   ├── knowledge-catalog.json    ← From cortex-registry/knowledge/*.yaml
│   ├── learning-paths.json       ← 3-track module metadata (45 modules total)
│   ├── orchestrators.json        ← 51 orchestrator cards
│   └── mcp-tools.json            ← 39 MCP tool catalog (28 registered)
├── pipeline/                     ← Discovery & generation scripts
│   ├── discover.py               ← Git + registry + live code scan
│   ├── build.py                  ← YAML → JSON transformer
│   ├── extract-json.py           ← .content/ → content.json
│   └── validate.py               ← CSS, links, responsive, schema checks
└── assets/css|js|diagrams/       ← Glassmorphism design system
```

**This agent's output targets:**
- `cortex-docs/.content/` → markdown content (for `extract-json.py` → `data/content.json`)
- `cortex-docs/assets/diagrams/` → Mermaid .mmd and D3.js .html diagram files

**This agent does NOT modify:**
- `cortex-docs/roles/*.html` — managed by cortex-gitpages-builder.md
- `cortex-docs/learning/**/*.html` — managed by cortex-gitpages-builder.md
- `cortex-docs/data/*.json` — generated by pipeline scripts (DOC-REFRESH-001)

**CSS Standard:** Zero inline `style=` attributes in all HTML. All styles must be in CSS files
or `<style>` blocks. Quality gate: `grep -r 'style=' cortex-docs/**/*.html` must return 0.

---

## 🏗️ STS Sample App Documentation Scope

This agent is authoritative for documentation of STS sample applications in `_workspaces/sts/`.

### STS Workspace Layout
```
_workspaces/sts/sample-apps/_Real/
├── README.md                        ← Index: both apps, tech stack, architecture overview
├── account-modernized/
│   └── README.md                    ← Entities, API reference, architecture diagram, canary rollout
├── payment-processor-modernized/
│   └── README.md                    ← Entities, API reference, architecture diagram, test suite
├── account-api-specs/
│   ├── README.md                    ← Spec index + diagram rendering instructions
│   └── specifications/*/diagrams/
│       ├── sequence.mmd             ← MUST use `participant` (NOT `user`)
│       ├── flowchart.mmd            ← MUST use full labels, HTTP status codes, real endpoint paths
│       └── dependency.mmd           ← MUST be classDiagram with interfaces + implementations
├── payment-api-specs/
│   ├── README.md
│   └── specifications/*/diagrams/  ← Same rules as account-api-specs
└── sts-architecture-d3.html        ← D3.js force-directed graph (all layers, filter buttons, tooltip)
```

### STS `.mmd` Validation Rules

**This agent MUST validate all `.mmd` files against these rules before marking docs complete:**

| Rule | Check | Fix |
|---|---|---|
| `sequenceDiagram` keyword | `participant` only — NEVER `user` | Replace `user X` → `participant X` |
| Endpoint labels | Start node shows actual HTTP endpoint | Replace `API Invoked` → `POST /api/v1/path` |
| Node label truncation | No `_less`, `Contains`, abbreviated names | Expand to full readable English |
| Error nodes | Include HTTP status code | `400 Bad Request: reason` |
| flowchart conditions | Human-readable | `invoiceAmount > 0?` not `InvoiceAmount LTE 0` |
| classDiagram interfaces | Show interface + implementation | `IService <|.. ServiceImpl : implements` |
| alt/loop blocks | Sequence uses `alt` for conditionals | Add `alt Balance below peg / else` block |

### STS D3.js Diagram Requirements

Every STS workspace root MUST contain `sts-architecture-d3.html`:
- **Type:** D3.js v7 force-directed graph
- **Layers:** API (blue), Core (green), Infrastructure (orange), Entity (purple), Azure (amber)
- **Features:** Filter buttons per layer, hover tooltip with node description, drag, zoom/pan
- **Style:** Dark glassmorphism (`#0d1117` background)
- **Content:** All Controllers, Service Interfaces, Repository Interfaces, Domain Entities, Azure Services

---

## 📋 Chat01 Gap Remediation (Priority Documentation)

**Authority:** chat01.md comprehensive analysis identified critical documentation gaps.

**THIS AGENT MUST PRIORITIZE:**

### P0 Gaps (Critical - Missing Foundational Context)

| Gap | Required Content | Target Location | Approach |
|-----|-----------------|-----------------|----------|
| **Orchestrator Tiers** | Directory structure, tier precedence, module purposes, governance flow | `cortex-docs/.content/01-capabilities/orchestrator-tiers.md` | High-level architecture explanation using accessible metaphors. NO internal Python details. Reflect actual 17-orchestrator count (7 core, 3 domain, 7 support). |
| **LENS Intelligence** | LENS analysis pipeline, 4-phase process, integration points | `cortex-docs/.content/02-lens/lens-intelligence.md` | User-facing capability description with evidence-backed performance metrics. |
| **Enforcement Agents** | Agent roles, validation focus, integration points | `cortex-docs/.content/01-capabilities/enforcement-agents.md` | Conceptual overview of pre-execution gate with agent responsibilities. |

### P1 Gaps (Important - Incomplete Coverage)

| Gap | Required Content | Target Location | Approach |
|-----|-----------------|-----------------|----------|
| **Challenge Engine** | Counter-proposal generation, disagreement protocol | `cortex-docs/.content/01-capabilities/challenge-engine.md` | User experience perspective on how challenges improve code quality. |
| **SQLite Audit Trail** | High-level audit trail concept (NOT detailed schema) | `cortex-docs/.content/glossary.md` expansion | Brief explanation of what's tracked for governance, not table definitions. |
| **Orchestrator Deep-Dives** | Top 5 orchestrator capabilities (TDD, Refactoring, Health, Sweep, Upgrade) | `cortex-docs/.content/03-orchestration/` individual files | User-facing capabilities only, not internal implementation. |
| **MCP Tool Catalog** | All 38 active tools with descriptions and parameters | `cortex-docs/.content/04-mcp/03-tools-catalog.md` | Update tool count to 38 active tools. |

### Content Generation Rules for Gap Remediation

**When generating content for these gaps:**

✅ **DO:**
- Explain what users/organizations benefit from
- Use accessible language and metaphors
- Show integration points with other components
- Include Mermaid diagrams for conceptual flow
- Provide qualified language ("designed to", "may enable")
- Add mandatory disclaimers
- Focus on 3-role perspective (Business Leaders, Product Owners, Software Developers)

❌ **DON'T:**
- Include internal Python class structures
- Show detailed algorithm pseudocode
- Document private method signatures
- Expose file system paths to internal modules
- Include debug-level implementation details
- Use unqualified absolute claims

**Example (Brain Tiers - Correct Approach):**

```markdown
# Understanding CORTEX Brain Architecture

Organizations leveraging CORTEX benefit from a hierarchical governance system designed to ensure consistency across all operations. The Brain Tier architecture separates concerns across four layers, each serving distinct organizational needs.

## Tier Structure Overview

```mermaid
graph TD
    T0[Tier 0: Immutable Governance] --> T1[Tier 1: Orchestration Intelligence]
    T1 --> T2[Tier 2: Advanced Governance]
    T2 --> T3[Tier 3: Knowledge Synthesis]
    
    style T0 fill:#ff6b6b
    style T1 fill:#ffd93d
    style T2 fill:#6bcf7f
    style T3 fill:#4d96ff
```

**Tier 0 (Immutable Governance):** Foundation layer containing core governance rules that remain consistent across all projects...

[Continue with user-facing description, NO Python implementation details]
```

**Example (LENS Intelligence — Correct Approach):**

```markdown
# LENS Intelligence Pipeline

Organizations may benefit from improved code analysis quality through the LENS (Language → Examination → Navigation → Synthesis) capability...

**Performance Characteristics (Internal Testing):**
- Quick tier: <200ms (cached rules only)
- Targeted tier: <2s (LENS + relevant YAMLs)
- Full tier: <10s (LENS + knowledge graph + profiles)

> **Notice:** Performance measurements reflect internal testing environments.
> Production results depend on hardware specifications, network latency,
> and concurrent load patterns. No guarantee of specific timing outcomes.

[Continue with conceptual architecture, NOT implementation code]
```

---

## 🏗️ Architecture: Registry-Driven Documentation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   DOCUMENTATION FLOW                         │
│                                                              │
│  ┌─────────────────┐    ┌──────────────────────┐            │
│  │ __wiring_       │───▶│ CortexDocsOrchestrator│            │
│  │ contract__.yaml │    │ (DocDeltaAnalyzer)   │            │
│  └─────────────────┘    └──────────┬───────────┘            │
│                                    │                         │
│  ┌─────────────────┐               │ extracts registry      │
│  │ cortex-registry/│───────────────┤ generates MD updates   │
│  │  │               │                         │
│  └─────────────────┘               ▼                         │
│                         ┌──────────────────────┐            │
│                         │ _workspaces/         │            │
│                         │ cortex-architecture/ │ ◀── MD     │
│                         │ (*.md files)         │            │
│                         └──────────┬───────────┘            │
│                                    │                         │
│                                    │ MarkdownToHTMLConverter │
│                                    │ + Jinja2 templates      │
│                                    │ + glassmorphism theme   │
│                                    ▼                         │
│                         ┌──────────────────────┐            │
│                         │ _build/site/         │ ◀── HTML   │
│                         │ (GitPages deploy)    │            │
│                         │ - index.html         │            │
│                         │ - architecture/      │            │
│                         │ - personas/          │            │
│                         │ - assets/            │            │
│                         └──────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Documentation Modes

### Mode 1: Documentation Refresh

**Trigger:** User says "refresh docs" or "update architecture docs"

**Process:**
1. **Git Delta Detection**
   ```bash
   # Find last doc update
   LAST_DOC_COMMIT=$(git log -1 --format=%H -- _workspaces/cortex-architecture/)
   
   # Get changes since then
   git diff ${LAST_DOC_COMMIT}..HEAD --name-only -- \
     cortex/**/*.py \
     .github/**/*.md \
     cortex-registry/**/*.yaml \
     cortex/__wiring_contract__.yaml
   ```

2. **Impact Analysis**
   - Categorize changed files by documentation section
   - Identify affected diagrams
   - Detect new orchestrators/tools requiring documentation
   - Map changes to brain analogies

3. **Update Generation (Content Depth Framework)**
   - **Categorize by Diátaxis:** Tutorial/How-To/Reference/Explanation
   - **Apply word count targets:**
     - Feature overview: 1200 words (800-1500 range)
     - Architecture section: 1800 words (1200-2000 range)
     - Tutorial: 1400 words (1000-1800 range)
     - How-to guide: 750 words (600-1000 range)
     - Reference: 600 words per item (400-800 range)
   - **Include required elements:**
     - C4 diagrams (Context → Container → Component hierarchy)
     - Code examples (runnable snippets)
     - Cross-references (related docs)
     - Validation steps
     - Troubleshooting section
   - **Score content depth:** 1-5 rubric (target: 4+ for all pages)
   - Update affected sections only (incremental)
   - Regenerate impacted diagrams with metadata
   - Add new capability entries
   - Update metrics/statistics

4. **Validation**
   - Cross-reference validation (all links work)
   - Accuracy check (code matches docs)
   - Completeness check (no missing sections)
   - **Word count validation:** Ensure meets minimum targets
   - **Content depth scoring:** No pages below score 3
   - **Diagram metadata:** All diagrams have required frontmatter

**Output:**
```
<hr>
📚 Documentation Refresh Complete
<hr>

📊 Changes Analyzed: 247 commits since 0506774b0
📝 Sections Updated: 12/24 (50%)
🔄 Diagrams Regenerated: 4
✅ Validation: 100% pass
📏 Word Count: 18,450 total (+2,340 from refresh)
⭐ Content Depth: 4.2 avg (12 pages scored)

Updated Sections:
├─ orchestration/overview.md (7 new orchestrators, 1,850 words, C4 Container diagram)
├─ mcp/tools-catalog.md (12 new tools, 5,400 words, reference tables)
├─ capabilities/governance-compliance.md (3 new agents, 1,620 words, flowchart)
└─ diagrams/architecture-overview.md (updated counts, metadata added)

Content Quality:
├─ Exemplary (5): 8 pages
├─ Strong (4): 3 pages
├─ Adequate (3): 1 page
└─ Below Target: 0 pages

Git: a2fdcdc "docs: Refresh architecture docs (247 commits)"
<hr>
```

---

### Mode 2: HTML Site Generation

**Trigger:** User says "generate HTML docs" or "prepare for GitHub Pages"

**Process:**
1. **Template Extraction**
   - Extract design from existing dashboard HTML
   - Create Jinja2 templates with components
   - Maintain glassmorphism design system
   - Preserve D3.js integration points

2. **Content Transformation**
   - Convert Markdown to HTML
   - Embed D3.js diagrams
   - Generate multi-persona views
   - Create navigation hierarchy

3. **Asset Optimization**
   - Minify CSS/JS
   - Optimize images
   - Bundle dependencies
   - Generate service worker for offline access

4. **GitHub Pages Preparation**
   - Create CNAME file
   - Configure Jekyll bypass (_config.yml)
   - Set up GitHub Actions workflow
   - Test relative path resolution

**Output:**
```
_workspaces/cortex-gitpages/
├── index.html (Landing page with brain analogy)
├── architecture/ (Main documentation)
│   ├── index.html
│   ├── capabilities/
│   ├── orchestration/
│   ├── lens/
│   ├── toolkit/
│   └── infrastructure/
├── personas/ (Role-specific views)
│   ├── developer/
│   ├── manager/
│   ├── executive/
│   └── regulatory/
├── assets/
│   ├── css/ (minified)
│   ├── js/ (bundled D3.js)
│   └── images/
└── api/ (Interactive API docs)
```

---

## 🧠 Brain Analogy System

**Purpose:** Explain CORTEX architecture using human brain analogies for executive/non-technical audiences.

### Core Analogies

| CORTEX Component | Brain Analogy | Explanation |
|------------------|---------------|-------------|
| **MasterOrchestrator** | **Prefrontal Cortex** | Executive control center that makes high-level decisions |
| **IntentRouter** | **Thalamus** | Sensory relay that routes signals to appropriate processing centers |
| **LENS** | **Visual Cortex** | Processes visual information (code structure, patterns) |
| **CORTEX Brain** | **Hippocampus** | Long-term memory storage for knowledge and patterns |
| **TDDOrchestrator** | **Motor Cortex** | Executes precise movements (code implementation) |
| **EnforcementOrchestrator** | **Amygdala** | Safety/security gatekeeper that blocks dangerous operations |
| **LearningSystem** | **Cerebellum** | Adaptive learning and skill refinement |
| **MCP Interface** | **Sensory Nerves** | Input channels from external world (VSCode, Claude, etc.) |
| **GitBackedRegistry** | **Myelin Sheath** | Efficient signal transmission (fast orchestrator lookup) |
| **Challenge Engine** | **Devil's Advocate Network** | Questions assumptions to avoid mistakes |

### Documentation Templates

**Executive Summary Template:**
```markdown
## CORTEX: Your AI Development Brain

Imagine if your development team had a **second brain** that:
- **Sees everything** (LENS Visual Cortex scans all code)
- **Remembers everything** (Hippocampus stores 45+ best practices)
- **Prevents mistakes** (Amygdala blocks security violations)
- **Learns constantly** (Cerebellum adapts from every project)
- **Coordinates perfectly** (Prefrontal Cortex orchestrates 60 specialists)

That's CORTEX.

### How It Works (Brain Analogy)

1. **You speak** → MCP Sensory Nerves receive request
2. **Brain processes** → Thalamus routes to right specialist
3. **Visual scan** → Visual Cortex analyzes code structure
4. **Memory check** → Hippocampus recalls best practices
5. **Safety gate** → Amygdala validates security
6. **Execute** → Motor Cortex implements with TDD
7. **Learn** → Cerebellum stores patterns for next time

### Benefits

| Traditional Tools | CORTEX (AI Brain) |
|-------------------|-------------------|
| 1 capability | 86 specialized tools |
| No memory | Remembers all patterns |
| No safety gates | 7 security agents |
| No learning | Adaptive refinement |
| Linear workflow | Multi-orchestrator intelligence |
```

---

## 📐 Documentation Structure (Multi-Format)

### Markdown Documentation (_workspaces/cortex-architecture/)

**Current structure maintained:**
```
index.md (Master navigation)
capabilities/ (Business capabilities)
orchestration/ (Technical orchestrator docs)
lens/ (LENS intelligence deep-dive)
toolkit/ (Developer toolkit)
infrastructure/ (Deployment/operations)
mcp/ (Integration guide)
diagrams/ (Visual architecture)
```

### HTML Documentation (_workspaces/cortex-gitpages/)

**GitHub Pages structure:**
```
index.html (Landing with brain analogy)
architecture/
  ├── index.html (Main navigation hub)
  ├── capabilities/
  │   ├── overview.html
  │   ├── ai-intelligence.html
  │   ├── core-platform.html
  │   ├── decisioning.html
  │   ├── extensibility.html
  │   └── governance-compliance.html
  ├── orchestration/
  │   ├── overview.html
  │   ├── master-orchestrator.html
  │   ├── intent-router.html
  │   ├── tdd-orchestrator.html
  │   ├── domain-orchestrators.html
  │   ├── support-orchestrators.html
  │   ├── cross-orchestrator.html
  │   └── end-to-end-flow.html
  ├── lens/
  │   ├── overview.html
  │   ├── architecture.html
  │   ├── analyzers.html
  │   ├── synthesis.html
  │   ├── caching.html
  │   └── governance.html
  ├── toolkit/
  │   ├── overview.html
  │   ├── developer-guide.html
  │   ├── tool-categories.html
  │   ├── tool-registry.html
  │   └── security-model.html
  ├── infrastructure/
  │   ├── overview.html
  │   ├── tech-stack.html
  │   ├── deployment.html
  │   ├── ci-cd.html
  │   ├── observability.html
  │   ├── scalability.html
  │   └── learning-architecture.html
  ├── mcp/
  │   ├── overview.html
  │   ├── protocol.html
  │   ├── integration.html
  │   ├── tools-catalog.html
  │   └── versioning.html
  └── diagrams/
      ├── architecture-overview.html
      ├── request-lifecycle.html
      ├── component-relationships.html
      └── data-flow.html
personas/
  ├── developer/
  │   ├── getting-started.html
  │   ├── building-tools.html
  │   ├── testing-guide.html
  │   ├── best-practices.html
  │   ├── troubleshooting.html
  │   └── api-reference.html
  ├── manager/
  │   ├── project-overview.html
  │   ├── team-productivity.html
  │   ├── quality-metrics.html
  │   ├── risk-management.html
  │   ├── resource-planning.html
  │   ├── delivery-tracking.html
  │   ├── compliance-status.html
  │   └── roi-analysis.html
  ├── executive/
  │   ├── business-value.html
  │   ├── strategic-capabilities.html
  │   └── investment-justification.html
  └── regulatory/
      ├── compliance-overview.html
      ├── audit-trails.html
      ├── security-controls.html
      └── governance-framework.html
api/
  ├── mcp-tools.html (Interactive API explorer)
  ├── orchestrators.html
  └── examples.html
assets/
  ├── css/
  │   ├── main.min.css (Glassmorphism design)
  │   └── personas.min.css
  ├── js/
  │   ├── d3.v7.min.js
  │   ├── diagrams.min.js
  │   ├── navigation.min.js
  │   └── search.min.js
  └── images/
      ├── brain-analogy.svg
      ├── architecture-overview.svg
      └── logos/
```

---

## 🔧 Implementation Tasks

### Task 1: Git Delta Analyzer

**File:** `cortex/orchestrators/internal/doc_delta_analyzer.py`

```python
"""Documentation delta analyzer - identifies docs needing updates."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import subprocess

class DocDeltaAnalyzer:
    """Analyze git changes to identify documentation updates needed."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.arch_docs = repo_root / "_workspaces/cortex-architecture"
    
    def get_last_doc_update(self) -> str:
        """Get commit hash of last architecture doc update."""
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", str(self.arch_docs)],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )
        return result.stdout.strip()
    
    def get_changed_files_since(self, commit_hash: str) -> List[str]:
        """Get all changed files since given commit."""
        result = subprocess.run(
            [
                "git", "diff", "--name-only",
                f"{commit_hash}..HEAD",
                "--",
                "cortex/**/*.py",
                ".github/**/*.md",
                "cortex-registry/**/*.yaml",
                "cortex/__wiring_contract__.yaml"
            ],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )
        return result.stdout.strip().split("\n")
    
    def categorize_changes(self, files: List[str]) -> Dict[str, List[str]]:
        """Categorize changed files by documentation section."""
        categories = {
            "orchestration": [],
            "mcp": [],
            "lens": [],
            "toolkit": [],
            "infrastructure": [],
            "capabilities": [],
            "diagrams": []
        }
        
        for file in files:
            if "orchestrators" in file:
                categories["orchestration"].append(file)
            elif "mcp" in file or "tools" in file:
                categories["mcp"].append(file)
            elif "lens" in file:
                categories["lens"].append(file)
            elif "governance" in file or "enforcement" in file:
                categories["capabilities"].append(file)
            elif "deployment" in file or "observability" in file:
                categories["infrastructure"].append(file)
            elif "__wiring_contract__" in file:
                categories["diagrams"].append(file)
        
        return {k: v for k, v in categories.items() if v}
    
    def identify_new_orchestrators(self, changed_files: List[str]) -> List[str]:
        """Identify newly added orchestrators."""
        new_orchestrators = []
        for file in changed_files:
            if "orchestrators" in file and file.endswith("_orchestrator.py"):
                # Check if file is new (not in last doc commit)
                result = subprocess.run(
                    ["git", "log", "--follow", "--diff-filter=A", "--", file],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_root
                )
                if result.stdout:
                    new_orchestrators.append(file)
        return new_orchestrators
    
    def identify_new_mcp_tools(self, changed_files: List[str]) -> List[str]:
        """Identify newly added MCP tools."""
        new_tools = []
        for file in changed_files:
            if "mcp" in file and "tools" in file:
                # Parse for new tool definitions
                # (implementation would parse Python file for @mcp_tool decorators)
                pass
        return new_tools
    
    def generate_refresh_plan(self) -> Dict:
        """Generate complete documentation refresh plan."""
        last_commit = self.get_last_doc_update()
        changed_files = self.get_changed_files_since(last_commit)
        categorized = self.categorize_changes(changed_files)
        new_orchestrators = self.identify_new_orchestrators(changed_files)
        new_tools = self.identify_new_mcp_tools(changed_files)
        
        return {
            "baseline_commit": last_commit,
            "total_changes": len(changed_files),
            "categories": categorized,
            "new_orchestrators": new_orchestrators,
            "new_tools": new_tools,
            "sections_to_update": list(categorized.keys()),
            "estimated_effort": self._estimate_effort(categorized)
        }
    
    def _estimate_effort(self, categories: Dict[str, List[str]]) -> str:
        """Estimate effort for documentation refresh."""
        total_files = sum(len(files) for files in categories.values())
        if total_files < 10:
            return "30 minutes"
        elif total_files < 50:
            return "2 hours"
        elif total_files < 100:
            return "4 hours"
        else:
            return "8 hours (full day)"
```

**Tests:** `tests/unit/orchestrators/internal/test_doc_delta_analyzer.py` (15 tests)

---

### Task 2: HTML Site Generator

**File:** `cortex/orchestrators/internal/html_site_generator.py`

```python
"""HTML site generator for GitHub Pages deployment."""

from pathlib import Path
from typing import Dict, List
import markdown
import jinja2

class HTMLSiteGenerator:
    """Generate GitHub Pages-ready HTML site from Markdown docs."""
    
    def __init__(
        self,
        md_root: Path,
        html_root: Path,
        template_dir: Path
    ):
        self.md_root = md_root
        self.html_root = html_root
        self.template_dir = template_dir
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir))
        )
    
    def extract_templates_from_dashboard(self) -> None:
        """Extract Jinja2 templates from existing dashboard HTML."""
        dashboard_path = Path("cortex-registry/dashboard/index.html")
        # Parse HTML and extract components
        # Create base.html.jinja2, components/*.html.jinja2
        pass
    
    def convert_markdown_to_html(self, md_file: Path) -> str:
        """Convert Markdown file to HTML with metadata."""
        with open(md_file, 'r') as f:
            content = f.read()
        
        # Extract frontmatter if exists
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            content,
            extensions=[
                'fenced_code',
                'tables',
                'toc',
                'codehilite'
            ]
        )
        
        return html_content
    
    def generate_persona_views(self, section: str) -> None:
        """Generate role-specific views for a section."""
        personas = ["developer", "manager", "executive", "regulatory"]
        
        for persona in personas:
            # Filter content by persona relevance
            # Generate persona-specific page
            pass
    
    def embed_d3_diagrams(self, html_content: str) -> str:
        """Embed D3.js diagrams from diagram specifications."""
        # Parse diagram markers
        # Inject D3.js visualization code
        pass
    
    def optimize_assets(self) -> None:
        """Minify CSS/JS and optimize images."""
        # CSS minification
        # JS bundling
        # Image optimization
        pass
    
    def generate_navigation(self) -> Dict:
        """Generate hierarchical navigation structure."""
        nav_structure = {
            "main": [],
            "personas": {},
            "api": []
        }
        # Build from directory structure
        return nav_structure
    
    def generate_site(self) -> None:
        """Generate complete HTML site."""
        # 1. Extract templates
        self.extract_templates_from_dashboard()
        
        # 2. Convert all Markdown files
        for md_file in self.md_root.rglob("*.md"):
            html_content = self.convert_markdown_to_html(md_file)
            # Render with template
            # Save to html_root
        
        # 3. Generate persona views
        for section in ["capabilities", "orchestration", "lens", "toolkit"]:
            self.generate_persona_views(section)
        
        # 4. Optimize assets
        self.optimize_assets()
        
        # 5. Generate navigation
        nav = self.generate_navigation()
        # Inject into all pages
```

**Tests:** `tests/unit/orchestrators/internal/test_html_site_generator.py` (20 tests)

---

### Task 3: Brain Analogy Generator

**File:** `cortex/orchestrators/internal/brain_analogy_generator.py`

```python
"""Generate brain analogies for CORTEX components."""

from typing import Dict, List

class BrainAnalogyGenerator:
    """Generate executive-friendly brain analogies."""
    
    ANALOGIES = {
        "MasterOrchestrator": {
            "brain_region": "Prefrontal Cortex",
            "function": "Executive Control Center",
            "analogy": "Makes high-level decisions about which specialist to consult",
            "example": "When you decide to implement a feature, the Prefrontal Cortex "
                      "(MasterOrchestrator) determines whether to use TDD workflow, "
                      "refactoring mode, or analysis mode."
        },
        "IntentRouter": {
            "brain_region": "Thalamus",
            "function": "Sensory Relay Station",
            "analogy": "Routes incoming requests to the right processing center",
            "example": "Just like the Thalamus routes visual signals to the Visual Cortex, "
                      "IntentRouter sends IMPLEMENT requests to TDDOrchestrator."
        },
        # ... more analogies
    }
    
    def generate_overview_analogy(self) -> str:
        """Generate overview comparing CORTEX to human brain."""
        return """
## CORTEX: Your Development Brain

Just as the human brain has 86 billion neurons working together, 
CORTEX has 60 specialized orchestrators coordinating to build software.

### Brain Regions → CORTEX Components

| Brain Region | Function | CORTEX Equivalent |
|--------------|----------|-------------------|
| **Prefrontal Cortex** | Executive decisions | MasterOrchestrator |
| **Thalamus** | Sensory routing | IntentRouter |
| **Visual Cortex** | Visual processing | LENS Analyzers |
| **Hippocampus** | Long-term memory | CORTEX Brain |
| **Motor Cortex** | Precise movements | TDDOrchestrator |
| **Amygdala** | Danger detection | EnforcementOrchestrator |
| **Cerebellum** | Skill refinement | Learning System |
| **Corpus Callosum** | Hemisphere bridge | MCP Interface |
"""
    
    def generate_component_analogy(self, component: str) -> str:
        """Generate detailed analogy for specific component."""
        if component in self.ANALOGIES:
            data = self.ANALOGIES[component]
            return f"""
### {component} → {data['brain_region']}

**Function:** {data['function']}

**How It Works:** {data['analogy']}

**Example:** {data['example']}
"""
        return ""
    
    def generate_workflow_analogy(self, workflow: str) -> str:
        """Generate analogy for complete workflow."""
        workflows = {
            "IMPLEMENT": """
### Implementing a Feature (Brain Workflow)

1. **Sensory Input** (MCP) → You type "/implement user authentication"
2. **Thalamus** (IntentRouter) → Routes to Motor Cortex
3. **Memory Check** (CORTEX Brain) → Recalls authentication best practices
4. **Visual Scan** (LENS) → Analyzes existing auth code
5. **Safety Check** (Amygdala) → Validates security requirements
6. **Motor Execution** (TDDOrchestrator) → Implements with RED→GREEN→REFACTOR
7. **Learning** (Cerebellum) → Stores patterns for future use
"""
        }
        return workflows.get(workflow, "")
```

**Tests:** `tests/unit/orchestrators/internal/test_brain_analogy_generator.py` (10 tests)

---

## 📊 Metrics & Success Criteria

### Documentation Refresh

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Accuracy** | 100% | All code references match implementation |
| **Completeness** | 100% | All orchestrators/tools documented |
| **Freshness** | < 7 days | Max age of documentation vs code |
| **Cross-reference validity** | 100% | All internal links work |
| **Diagram accuracy** | 100% | Counts match wiring contract |

### HTML Site

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Page load time** | < 2s | Lighthouse performance score |
| **Accessibility** | AA | WCAG 2.1 compliance |
| **Mobile responsive** | 100% | All viewports 320px-2560px |
| **Asset size** | < 5MB | Total site size |
| **SEO score** | > 90 | Lighthouse SEO audit |

---

## 🚀 Deployment Workflow

### GitHub Pages Deployment

```yaml
# .github/workflows/deploy-docs.yml
name: Deploy Documentation

on:
  push:
    branches: [main]
    paths:
      - '_workspaces/cortex-architecture/**'
      - 'cortex/**'
      - 'cortex-registry/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install markdown jinja2 beautifulsoup4
      
      - name: Refresh documentation
        run: python scripts/refresh_docs.py
      
      - name: Generate HTML site
        run: python scripts/generate_html_site.py
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./_workspaces/cortex-gitpages
          cname: cortex-docs.yourdomain.com
```

---

## � Comprehensive Content Generation Templates

### Template 1: Feature Overview (Diátaxis: Explanation)

**Target:** 1200 words (800-1500 range) | **Depth Score:** 5

```markdown
# {Feature Name}

**Category:** {Core | Domain | Support}  
**Priority:** {P0 | P1 | P2}  
**Status:** ![CI](badge) ![Coverage](badge) ![Release](badge)

---

## Overview

{2-3 paragraph introduction explaining what the feature is, why it exists, and its core value proposition. 200-300 words.}

**Key Benefits:**
- {Benefit 1 with specific metric}
- {Benefit 2 with user impact}
- {Benefit 3 with business value}

**Use Cases:**
1. {Use case 1 with persona}
2. {Use case 2 with scenario}
3. {Use case 3 with outcome}

---

## Architecture

### C4 Context Diagram

---
id: {feature-name}-context
title: {Feature Name} Context
purpose: Shows how {feature} fits in CORTEX ecosystem
audience: [Executive, Manager, Developer]
source_of_truth: cortex/__wiring_contract__.yaml
last_verified: v8.1
diagram_type: C4-Context
interactive: false
---

```mermaid
graph TD
    Users["Users<br/>(Developers)"] -->|requests| Feature
    Feature -->|uses| CoreSystem["CORTEX Core"]
    Feature -->|stores| Storage["Storage"]
    External["External Systems"] -.->|optional| Feature
```

**Explanation:** {200-300 words explaining the diagram, relationships, data flow, boundaries}

**Key Takeaways:**
- {Key point 1}
- {Key point 2}
- {Key point 3}

### C4 Container Diagram

---
id: {feature-name}-container
title: {Feature Name} Internal Components
purpose: Shows major runtime components inside {feature}
audience: [Developer, SRE]
source_of_truth: cortex/{feature-path}/__init__.py
last_verified: v8.1
diagram_type: C4-Container
interactive: false
---

```mermaid
graph TD
    subgraph Feature["{Feature Name}"]
        API["API Layer<br/>(FastAPI)"]
        Logic["Business Logic<br/>(Python)"]
        Storage["Storage Layer<br/>(SQLite/YAML)"]
    end
    
    Users -->|JSON-RPC| API
    API --> Logic
    Logic --> Storage
```

**Explanation:** {300-400 words on each component, technologies, responsibilities}

---

## How It Works

### Request Lifecycle

{500-700 words walking through a typical request from start to finish, including:}

1. **Input Phase:** {What happens when request arrives}
2. **Validation Phase:** {Checks performed}
3. **Processing Phase:** {Core logic execution}
4. **Output Phase:** {Results returned}
5. **Audit Phase:** {Logging and tracking}

```python
# Example Code (Runnable)
from cortex.{feature} import {FeatureClass}

# Initialize
feature = FeatureClass(config={...})

# Execute
result = feature.process(request={...})

# Verify
assert result.status == "success"
assert result.metrics["duration_ms"] < 100
```

**Expected Output:**
```json
{
  "status": "success",
  "data": {...},
  "metrics": {
    "duration_ms": 45,
    "tokens_used": 1234
  }
}
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `{VAR_1}` | Yes | - | {Description with type} |
| `{VAR_2}` | No | `default` | {Description with impact} |

### YAML Configuration

```yaml
# cortex/config/{feature}.yaml
{feature}:
  enabled: true
  mode: "production"
  settings:
    timeout_seconds: 30
    max_retries: 3
```

---

## Integration Guide

### Prerequisites

- Python ≥ 3.9
- CORTEX v8.1+
- Dependencies: `{list}`

### Quick Start

**Step 1:** Install dependencies
```bash
pip install {package-name}
```

**Step 2:** Configure
```bash
export {VAR_NAME}=value
```

**Step 3:** Initialize
```python
from cortex.{feature} import {Class}
instance = {Class}()
```

**Step 4:** Use
```python
result = instance.{method}({params})
```

---

## API Reference

### Class: `{ClassName}`

**Description:** {1-2 sentences}

**Methods:**

#### `{method_name}(param1: Type1, param2: Type2) -> ReturnType`

{Description: 100-150 words}

**Parameters:**
- `param1` (Type1): {Description}
- `param2` (Type2): {Description}

**Returns:**
- `ReturnType`: {Description}

**Raises:**
- `Exception1`: When {condition}
- `Exception2`: When {condition}

**Example:**
```python
result = instance.{method_name}(
    param1="value1",
    param2=42
)
```

---

## Performance

### Benchmarks

| Metric | Value | Benchmark |
|--------|-------|-----------|
| Latency (p50) | {X}ms | < 100ms ✅ |
| Latency (p99) | {Y}ms | < 500ms ✅ |
| Throughput | {Z} req/s | > 100 req/s ✅ |
| Memory | {M} MB | < 100MB ✅ |

### Optimization Tips

1. {Tip 1 with code example}
2. {Tip 2 with configuration}
3. {Tip 3 with architectural pattern}

---

## Troubleshooting

### Common Issues

#### Issue: {Problem Description}

**Symptoms:**
- {Symptom 1}
- {Symptom 2}

**Cause:** {Root cause explanation}

**Solution:**
```bash
# Fix commands
{command1}
{command2}
```

**Verification:**
```bash
# Verify fix
{verification-command}
```

---

## Related Documentation

- **Architecture:** [Overall Architecture](../architecture/overview.md)
- **API Reference:** [MCP Tools](../reference/mcp-tools.md)
- **Tutorial:** [Building Your First {Feature}](../tutorials/first-{feature}.md)
- **How-To:** [Deploy {Feature} to Production](../guides/deploy-{feature}.md)

---

**Last Updated:** {Date}  
**Word Count:** {Actual count}  
**Depth Score:** 5/5  
**Maintained By:** [Documentation Architect](mailto:docs@cortex.ai)
```

---

### Template 2: Tutorial (Diátaxis: Tutorial)

**Target:** 1400 words (1000-1800 range) | **Depth Score:** 5

```markdown
# Tutorial: Build Your First {Feature}

**Time:** 30 minutes  
**Difficulty:** Beginner  
**Prerequisites:** Python 3.9+, VS Code, CORTEX installed

---

## What You'll Learn

By the end of this tutorial, you'll be able to:
- ✅ {Learning objective 1}
- ✅ {Learning objective 2}
- ✅ {Learning objective 3}

---

## Prerequisites

### Software Requirements

| Tool | Version | Installation |
|------|---------|--------------|
| Python | ≥ 3.9 | `python --version` |
| CORTEX | ≥ 8.1 | `pip install cortex` |
| VS Code | Latest | [Download](https://code.visualstudio.com/) |

### Knowledge Requirements

- Basic Python programming
- Familiarity with command line
- Understanding of {prerequisite concept}

---

## Step 1: Set Up Your Environment

### 1.1 Create Project Directory

```bash
mkdir my-first-{feature}
cd my-first-{feature}
```

### 1.2 Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 1.3 Install Dependencies

```bash
pip install cortex=={version}
```

**Expected Output:**
```
Successfully installed cortex-8.1.0
{other packages}
```

✅ **Checkpoint:** Run `pip list | grep cortex` to verify installation.

---

## Step 2: Create Your First {Feature}

### 2.1 Create Main File

Create `main.py`:

```python
# main.py
"""My first {feature} implementation."""

from cortex.{feature} import {BaseClass}

class My{Feature}({BaseClass}):
    """Custom {feature} implementation."""
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    
    def process(self, data: dict) -> dict:
        """Process data with custom logic."""
        # Your logic here
        result = {
            "status": "success",
            "name": self.name,
            "data": data
        }
        return result

# Test it
if __name__ == "__main__":
    feature = My{Feature}(name="Tutorial")
    result = feature.process({"input": "test"})
    print(result)
```

### 2.2 Run Your Code

```bash
python main.py
```

**Expected Output:**
```json
{
  "status": "success",
  "name": "Tutorial",
  "data": {"input": "test"}
}
```

✅ **Checkpoint:** You should see the JSON output above.

---

## Step 3: Add Configuration

### 3.1 Create Config File

Create `config.yaml`:

```yaml
my_{feature}:
  name: "My First {Feature}"
  enabled: true
  settings:
    timeout: 30
    retries: 3
```

### 3.2 Load Configuration

Update `main.py`:

```python
import yaml

# Load config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Use config
feature = My{Feature}(
    name=config["my_{feature}"]["name"]
)
```

✅ **Checkpoint:** Run again and verify name comes from config.

---

## Step 4: Add Error Handling

{200-300 words explaining error handling strategy}

```python
class My{Feature}({BaseClass}):
    def process(self, data: dict) -> dict:
        try:
            # Validation
            if not data:
                raise ValueError("Data cannot be empty")
            
            # Processing
            result = {
                "status": "success",
                "name": self.name,
                "data": data
            }
            return result
            
        except ValueError as e:
            return {
                "status": "error",
                "error": str(e)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error: {e}"
            }
```

### 4.1 Test Error Handling

```python
# Test with empty data
result = feature.process({})
print(result)  # Should show error
```

**Expected Output:**
```json
{
  "status": "error",
  "error": "Data cannot be empty"
}
```

✅ **Checkpoint:** Error handling works correctly.

---

## Step 5: Add Logging

{150-200 words on logging importance}

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class My{Feature}({BaseClass}):
    def process(self, data: dict) -> dict:
        logger.info(f"Processing data: {data}")
        
        try:
            result = {...}
            logger.info(f"Success: {result}")
            return result
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
```

✅ **Checkpoint:** Run and see log messages in console.

---

## Step 6: Write Tests

{200-250 words on testing importance}

Create `test_my_{feature}.py`:

```python
import pytest
from main import My{Feature}

def test_basic_processing():
    """Test basic functionality."""
    feature = My{Feature}(name="Test")
    result = feature.process({"input": "test"})
    
    assert result["status"] == "success"
    assert result["name"] == "Test"
    assert result["data"]["input"] == "test"

def test_error_handling():
    """Test error handling."""
    feature = My{Feature}(name="Test")
    result = feature.process({})
    
    assert result["status"] == "error"
    assert "cannot be empty" in result["error"]

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 6.1 Run Tests

```bash
pytest test_my_{feature}.py -v
```

**Expected Output:**
```
test_my_{feature}.py::test_basic_processing PASSED
test_my_{feature}.py::test_error_handling PASSED

2 passed in 0.12s
```

✅ **Checkpoint:** All tests pass.

---

## What You Learned

Congratulations! You've successfully built your first {feature}. You now know how to:

✅ Set up a CORTEX {feature} project  
✅ Implement custom logic  
✅ Load configuration from YAML  
✅ Handle errors gracefully  
✅ Add logging  
✅ Write and run tests

---

## Next Steps

**Level Up Your Skills:**
1. **How-To:** [Deploy {Feature} to Production](../guides/deploy-{feature}.md)
2. **Reference:** [{Feature} API Documentation](../reference/{feature}-api.md)
3. **Explanation:** [Understanding {Feature} Architecture](../architecture/{feature}-architecture.md)

**Join the Community:**
- GitHub Discussions: [Ask Questions](https://github.com/cortex/discussions)
- Discord: [Join Server](https://discord.gg/cortex)

---

## Troubleshooting

### Issue: Import Error

**Problem:** `ModuleNotFoundError: No module named 'cortex'`

**Solution:**
```bash
# Verify virtual environment activated
which python  # Should show venv path

# Reinstall cortex
pip install --upgrade cortex
```

### Issue: Config Not Found

**Problem:** `FileNotFoundError: config.yaml`

**Solution:**
- Ensure `config.yaml` is in same directory as `main.py`
- Check file name spelling (case-sensitive)

---

**Tutorial Time:** 30 minutes  
**Word Count:** {Actual count}  
**Depth Score:** 5/5  
**Last Updated:** {Date}
```

---

## �🔗 Integration with Existing Systems

### Dashboard Integration

**Reuse existing dashboard components:**
- Glassmorphism CSS from `cortex-registry/dashboard/assets/css/`
- D3.js diagrams from `dashboard/templates/`
- Navigation patterns from `dashboard/index.html`

### Phase 74 Integration

**Leverage Phase 74 capabilities:**
- Multi-role documentation portal
- Incremental build system
- Git-aware delta detection
- Asset optimization pipeline

### CORTEX Brain Integration

**Use CORTEX Brain for:**
- Best practices extraction
- Domain knowledge integration
- Governance rule documentation
- Template content population

---

## 📚 Related Documentation

- `.github/prompts/cortex-doc.prompt.md` — Documentation generation prompt
- `cortex-registry/master/site-infrastructure-001.yaml` — Site infrastructure spec
- `cortex/phase_executors/archived/execute_phase_74_complete.py` — Phase 74 implementation
- `_workspaces/cortex-architecture/` — Current Markdown documentation

---

*CORTEX Documentation Architect Agent v2.0 — Autonomous documentation lifecycle management*
