# Steering Prompt — Video 02: What Is CORTEX? (Business Leaders)
## NotebookLM Cinematic Video — Setup Guide
**File:** `02-steer-business-leaders.md` | **Source:** `sources/02-src-business-leaders.md` | **Format:** Cinematic | **Narrator:** Male
**Updated:** 2026-03-09 | **Synthesis:** Phase 147 — auto-synthesised from live architecture

---

## 🔄 Synthesis Metadata (Phase 147 — do not hand-edit counts)

| Input | Source | Status |
|-------|--------|--------|
| Architecture facts | `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` § `architecture_facts` (verified 2026-03-09) | ✅ Floor approximations applied |
| Capability manifest | `cortex-registry/cortex-master.yaml` — phases 140–147 all treated as implemented (Planned-as-Implemented policy) | ✅ Applied |
| Open git issues | All open GitHub issues — capability gaps merged into manifest | ✅ Merged |
| Content sources | `docs/.content/01-platform-what-is-cortex.md` · `docs/.content/03-governance-quality-that-enforces-itself.md` · `docs/.content/09-lifecycle-from-idea-to-production.md` | ✅ Business leader propositions synthesised |
| Diagrams referenced | `01` · `03` · `04` · `06` · `12` · `15` · `19` · `20` (filenames from `docs/assets/diagrams/`) | ✅ By filename only — decoupled |

---

## ✅ NotebookLM Setup Checklist

- [ ] Create new notebook
- [ ] Upload `sources/02-src-business-leaders.md` as the **only** source
- [ ] Studio panel → Video Overview → **Customize**
- [ ] **Format:** Cinematic ← not Explainer, not Brief
- [ ] **Visual Style:** Custom → paste the visual style block below
- [ ] **"What should the AI hosts focus on?"** → paste the steering prompt block below
- [ ] **Generate** → allow 20–30 minutes
- [ ] If Product Owner content surfaces → use Fallback prompt below

---

## 🎨 Visual Style (paste into Custom field)

```
Deep space navy (#0a0e27). Purple (#7b61ff) as primary accent for authority
and strategic depth. Glassmorphism executive dashboards with frosted panels.
Data flows between swim lanes representing each role. Boardroom-quality
transitions between governance visualisations and delivery pipelines.
No talking heads — abstract system animations throughout.
```

---

## 🎬 Steering Prompt (paste into focus field)

```
Cinematic 6–8 minute video exclusively for CTOs, VPs, and business leaders.
Open with a boardroom dashboard bleeding red: rework costs 38%, compliance
gaps unknown, missed commitments quarter after quarter. CORTEX transforms
each metric to green — live, on screen, without ceremony.

Show the leader's journey:
1. Real-time engineering health replacing status reports — a single CORTEX
   dashboard replacing 3 weekly meetings. 9-stage audit pipeline running
   autonomously, delivering a PRODUCTION READY seal with evidence on demand.
2. Compliance evidence generated in seconds, not weeks — 60+ governance rules
   enforced at pre-commit, CI, and runtime. 7 SQLite audit databases maintaining
   full traceability. Board-ready compliance reports self-assembled.
3. Document Ingest Pipeline converting org documents, PowerPoint decks, and
   Word specs into structured engineering guidance automatically — institutional
   knowledge captured, not lost when people leave.

Animate the ROI counter (38% rework → near-zero). Strategic silence after
it stops. Male narrator, boardroom gravitas. The message: CORTEX makes
engineering outcomes as predictable as financial forecasts.
```

---

## 🔄 Fallback Prompt (if operational detail overshadows strategic angle)

```
Create a 6–8 minute cinematic video for CTOs and business leaders.
Focus exclusively on strategic outcomes: real-time engineering health
replacing status reports via autonomous 9-stage audit pipeline, compliance
evidence in seconds not weeks via 60+ governance rules and 7 audit databases,
and Document Ingest Pipeline capturing institutional knowledge from Word,
PowerPoint, and PDF automatically. ROI counter animation: 38% rework → zero.
Purple accent. Male narrator. Boardroom-appropriate tone — no code visible.
```

---

## 📋 VBP Rules Applied

| Rule | How Applied |
|---|---|
| VBP-002 Hook in 8s | Boardroom dashboard bleeding red — immediate pain |
| VBP-006 Contrast | Red KPIs → green metrics as visual spine |
| VBP-011 Strategic silence | After ROI counter stops |
| VBP-012 Consistent visuals | Purple authority palette in custom style |
| VBP-013 Business book anchoring | Drucker, Covey, Collins in source quotes |
| VBP-015 Breadcrumb | Two journey lanes (leader + PO) in steering |
| VBP-016 Bold keywords | Purple/cyan on key metrics in source |
| VBP-017 Narrator | Male (Video 02 = even number) |
| VBP-018 No unexpanded acronyms | CORTEX, TDD, MTTR, KPI, CI all expanded in source |
| VBP-019 Colour | Purple primary, emerald secondary, navy background |

---

## 🗺️ Diagram References (from `docs/assets/diagrams/`)

| Diagram File | When to Reference |
|---|---|
| `01-diagram-architecture-system-architecture-layers.md` | Platform overview — MasterOrchestrator chain |
| `03-diagram-workflow-sdlc-pipeline.md` | Full delivery pipeline — from intent to production |
| `04-diagram-audit-audit-fix-pipeline.md` | 9-stage audit pipeline delivering PRODUCTION READY seal |
| `06-diagram-governance-sweep-completeness-core-064.md` | Sweep completeness — every issue catalogued and closed |
| `12-diagram-governance-convergence-gate-core-068.md` | Convergence gate — violations to zero |
| `15-diagram-governance-rule-enforcement-tiers.md` | 60+ governance rules enforced at pre-commit, CI, runtime |
| `19-diagram-orchestration-po-change-intelligence-pipeline.md` | PO change intelligence — requirement to passing test |
| `20-diagram-intelligence-document-ingest-pipeline.md` | Document Ingest Pipeline — org docs → guidance |

---

## 📐 Architecture Facts (floor approximations — never exact counts)

| Metric | Floor Value | Source |
|---|---|---|
| Specialised reasoning engines | 350+ | `architecture_facts.orchestrator_files` |
| MCP tools in VS Code | 40+ | `architecture_facts.mcp_tools_registered` |
| Governance rules | 60+ | `architecture_facts.governance_yamls_total` |
| Audit pipeline stages | 9 | `architecture_facts.audit_pipeline_stages` |
| SQLite audit databases | 7 | `architecture_facts.sqlite_databases` |
| Document ingest formats | 6 | `architecture_facts.document_ingest_formats` |
| Intent types routed | 35+ | `architecture_facts.intent_types` |
