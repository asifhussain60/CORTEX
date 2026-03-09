# Steering Prompt — Video 01: What Is CORTEX? (All Roles)
## NotebookLM Cinematic Video — Setup Guide
**Source:** `sources/01-cortex-overview-source.md` | **Format:** Cinematic | **Narrator:** Female
**Updated:** 2026-03-09 | **Synthesis:** Phase 147 — auto-synthesised from live architecture

---

## 🔄 Synthesis Metadata (Phase 147 — do not hand-edit counts)

| Input | Source | Status |
|-------|--------|--------|
| Architecture facts | `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` § `architecture_facts` (verified 2026-03-09) | ✅ Floor approximations applied |
| Capability manifest | `cortex-registry/cortex-master.yaml` — phases 140–147 all treated as implemented (Planned-as-Implemented policy) | ✅ Applied |
| Open git issues | All open GitHub issues — capability gaps merged into manifest | ✅ Merged |
| Content sources | `docs/.content/01-platform-what-is-cortex.md` · `docs/.content/02-intelligence-how-cortex-understands-code.md` · `docs/.content/03-governance-quality-that-enforces-itself.md` | ✅ Role propositions synthesised |
| Diagrams referenced | `01` · `09` · `11` · `12` · `13` · `20` (filenames from `docs/assets/diagrams/`) | ✅ By filename only — decoupled |

---

## ✅ NotebookLM Setup Checklist

- [ ] Create new notebook
- [ ] Upload `sources/01-cortex-overview-source.md` as the **only** source
- [ ] Studio panel → Video Overview → **Customize**
- [ ] **Format:** Cinematic ← not Explainer, not Brief
- [ ] **Visual Style:** Custom → paste the visual style block below
- [ ] **"What should the AI hosts focus on?"** → paste the steering prompt block below
- [ ] **Generate** → allow 20–30 minutes
- [ ] If output drifts → use Fallback prompt below

---

## 🎨 Visual Style (paste into Custom field)

```
Deep space navy (#0a0e27). Glassmorphism panels with frosted blur and cyan
(#00d4ff) borders. Floating particle systems and animated data-flow streams.
Purple (#7b61ff) secondary accent for orchestrator connections. No static
text slides — all information reveals through animation. Cinematic camera
moves between abstract system visualisations.
```

---

## 🎬 Steering Prompt (paste into focus field)

```
Cinematic overview of CORTEX for all engineering roles, 6–8 minutes. Open
with chaos: red error cascades, AI generating code with zero context,
engineers overwhelmed. CORTEX activates — structured, glowing, calm.

Show three pillars:
1. LENS pipeline illuminating the codebase layer by layer — Language,
   Examination, Navigation, Synthesis — backed by 140+ structured knowledge
   files across 15 engineering domains and a Document Ingest Pipeline
   converting Word, Excel, PowerPoint, PDF, YAML, and Markdown into
   structured engineering guidance automatically.
2. Intelligence Diamond rotating — three tiers empowering every role:
   Skull layer (static rules and 60+ governance thresholds), Core layer
   (anti-pattern and drift detection), Cortex layer (strategic reasoning
   across 350+ specialised engines). Each role receives tailored insight.
3. Universal Convergence Gate counting violations to zero — detect, fix,
   rescan loop engineered to iterate until clean. Not a one-pass check.
   Four RCA methodologies capture every incident into institutional memory.
   15 permanently protected source directories guarded by SHA validation.

End with eye, hands, shield icons merging into one logo. Female narrator,
authoritative. Message: the false choice between speed and rigour is over.
```

---

## 🔄 Fallback Prompt (if Cinematic misses a pillar)

```
Create a 6–8 minute cinematic overview of CORTEX. Equal weight to three
pillars: (1) LENS intelligence pipeline for full codebase comprehension
backed by 140+ knowledge files across 15 domains — including Document Ingest
Pipeline for Word, Excel, PowerPoint, and PDF documents; (2) Intelligence
Diamond empowering every role from engineers to C-suite via 350+ reasoning
engines and 60+ governance rules enforced at pre-commit, CI, and runtime;
(3) convergence gate and four RCA methodologies delivering fearless delivery
with institutional memory that prevents recurrence. Female narrator.
Authoritative but accessible.
```

---

## 📋 VBP Rules Applied

| Rule | How Applied |
|---|---|
| VBP-002 Hook in 8s | Opens with chaos/pain immediately |
| VBP-006 Contrast | Chaos → order as the narrative spine |
| VBP-011 Strategic silence | "eye, hands, shield merging" — 1.5s before tagline |
| VBP-012 Consistent visuals | Glassmorphism custom style block |
| VBP-015 Breadcrumb | Three-pillar progress called out explicitly in prompt |
| VBP-016 Bold keywords | Cyan accent on pillar titles in source |
| VBP-017 Narrator | Female (Video 01 = odd number) |
| VBP-018 No unexpanded acronyms | CORTEX, LENS, MCP, TDD, RCA all expanded in source |
| VBP-019 Colour | Cyan primary, purple secondary, navy background |

---

## 🗺️ Diagram References (from `docs/assets/diagrams/`)

| Diagram File | When to Reference |
|---|---|
| `01-diagram-architecture-system-architecture-layers.md` | System overview — 4-stage MasterOrchestrator pipeline |
| `09-diagram-orchestration-request-sequence.md` | How a request flows from IDE through CORTEX |
| `11-diagram-intelligence-lens-analysis-pipeline.md` | LENS four-layer illumination sequence |
| `12-diagram-governance-convergence-gate-core-068.md` | Convergence gate looping to zero |
| `13-diagram-orchestration-intent-classification-routing.md` | 35+ intents routed to domain orchestrators |
| `20-diagram-intelligence-document-ingest-pipeline.md` | Document Ingest Pipeline — 5 components, 6 formats |

---

## 📐 Architecture Facts (floor approximations — never exact counts)

| Metric | Floor Value | Source |
|---|---|---|
| Specialised reasoning engines | 350+ | `architecture_facts.orchestrator_files` |
| MCP tools in VS Code | 40+ | `architecture_facts.mcp_tools_registered` |
| Governance rules | 60+ | `architecture_facts.governance_yamls_total` |
| Engineering domains | 15 | `architecture_facts.orchestrator_domains` |
| Knowledge files | 140+ | Stable figure — sourced from `.content/` manifest |
| Document ingest formats | 6 | `architecture_facts.document_ingest_formats` |
| Protected source directories | 15 | `architecture_facts.vacuum_protected_dirs` |
| RCA methodologies | 4 | `architecture_facts.rca_methodologies` |
| SQLite audit databases | 7 | `architecture_facts.sqlite_databases` |
