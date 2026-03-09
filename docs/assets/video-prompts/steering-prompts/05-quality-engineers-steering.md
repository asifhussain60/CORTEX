````markdown
# Steering Prompt — Video 05: What Is CORTEX? (Quality Engineers)
## NotebookLM Cinematic Video — Setup Guide
**File:** `05-quality-engineers-steering.md` | **Source:** `sources/05-quality-engineers-source.md` | **Format:** Cinematic | **Narrator:** Female
**Updated:** 2026-03-09 | **Synthesis:** Phase 147 — auto-synthesised from live architecture

---

## 🔄 Synthesis Metadata (Phase 147 — do not hand-edit counts)

| Input | Source | Status |
|-------|--------|--------|
| Architecture facts | `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` § `architecture_facts` (verified 2026-03-09) | ✅ Floor approximations applied |
| Capability manifest | `cortex-registry/cortex-master.yaml` — phases 140–147 all treated as implemented (Planned-as-Implemented policy) | ✅ Applied |
| Open git issues | All open GitHub issues — capability gaps merged into manifest | ✅ Merged |
| Content sources | `docs/.content/04-tdd-quality-flywheel.md` · `docs/.content/02-intelligence-how-cortex-understands-code.md` · `docs/.content/03-governance-quality-that-enforces-itself.md` | ✅ Quality engineer propositions synthesised |
| Diagrams referenced | `07` · `16` · `18` · `12` · `06` (filenames from `docs/assets/diagrams/`) | ✅ By filename only — decoupled |

---

## ✅ NotebookLM Setup Checklist

- [ ] Create new notebook
- [ ] Upload `sources/05-quality-engineers-source.md` as the **only** source
- [ ] Studio panel → Video Overview → **Customize**
- [ ] **Format:** Cinematic ← not Explainer, not Brief
- [ ] **Visual Style:** Custom → paste the visual style block below
- [ ] **"What should the AI hosts focus on?"** → paste the steering prompt block below
- [ ] **Generate** → allow 20–30 minutes
- [ ] If software engineering implementation content dominates → use Fallback prompt below

---

## 🎨 Visual Style (paste into Custom field)

```
Deep space navy (#0a0e27). Gold (#FFD700) as primary accent for golden tests
and quality standards. Cyan (#00d4ff) as secondary for intelligence and
analysis pipelines. Glassmorphism test panels with glowing gold borders.
Quality radar chart fills five dimensions in sequence. Golden test cards
materialise with a stamp animation. Defect counts animate to zero with
a SWEEP COMPLETE gold seal. Nothing is static.
```

---

## 🎬 Steering Prompt (paste into focus field)

```
Cinematic 6–8 minute video exclusively for quality engineers and QA leads.
Open with the quality engineer's burden: manual test matrices, flaky tests
nobody trusts, a regression suite that takes 4 hours and still misses bugs.
CORTEX transforms quality from gatekeeping into engineering.

Show three capabilities every quality engineer gains:
1. Golden tests as first-class citizens — each golden test card glows and
   traces directly back to its acceptance criterion and the business rule it
   protects. The golden test is the proof of correct behaviour, not the
   assertion. Quality radar chart fills five dimensions to a composite score
   of 87/100, with the weakest dimension highlighted as a growth opportunity.
2. Response Rendering Rules (Phase 146) validate all 14 response formatting
   constraints before output leaves CORTEX — quality gates at the output
   layer, not just the input. Multi-pass code review pipeline with explicit
   quality gates before merge.
3. Convergence gate (CORE-068) dropping violations from 15 to zero — detect,
   fix, rescan loop that iterates until the sweep is clean. SWEEP COMPLETE
   seal stamps in gold. Sweep Completeness Contract (CORE-064) ensures no
   partial sweeps — every issue in the catalogue must be CLOSED.

Female narrator, quality-focused peer tone. QEs should feel their craft
is respected. Message: quality is architecture, not afterthought.
```

---

## 🔄 Fallback Prompt (if software implementation content dominates)

```
Create a 6–8 minute cinematic video exclusively for quality engineers.
Focus on: golden tests tracing to acceptance criteria and business rules,
5-dimension quality radar chart with composite scoring, 14-rule Response
Rendering validation (Phase 146), multi-pass code review pipeline with
quality gates before merge, convergence gate (CORE-068) sweeping to zero
with SWEEP COMPLETE gold seal, and Sweep Completeness Contract (CORE-064)
ensuring no partial sweeps. Gold accent. Female narrator. Quality-craft
tone — engineering rigour, not policing.
```

---

## 📋 VBP Rules Applied

| Rule | How Applied |
|---|---|
| VBP-002 Hook in 8s | Manual test matrices + flaky tests nobody trusts — immediate QE pain |
| VBP-006 Contrast | Gatekeeping burden → quality as engineering discipline |
| VBP-011 Strategic silence | After SWEEP COMPLETE gold seal stamps |
| VBP-012 Consistent visuals | Gold quality palette in custom style |
| VBP-013 Business book anchoring | Deming, Weinberg, Bach in source quotes |
| VBP-015 Breadcrumb | Golden tests → Radar → Rendering → Convergence arc |
| VBP-016 Bold keywords | Gold on "golden test", cyan on intelligence in source |
| VBP-017 Narrator | Female (Video 05 — quality craft convention) |
| VBP-018 No unexpanded acronyms | TDD, CORE-064, CORE-068, QA, CI, SSOT all expanded in source |
| VBP-019 Colour | Gold primary, cyan secondary, navy background |

---

## 🗺️ Diagram References (from `docs/assets/diagrams/`)

| Diagram File | When to Reference |
|---|---|
| `06-diagram-governance-sweep-completeness-core-064.md` | Sweep Completeness Contract — every issue catalogued and CLOSED |
| `07-diagram-testing-testing-strategy-pyramid.md` | Golden test hierarchy — unit → integration → golden |
| `12-diagram-governance-convergence-gate-core-068.md` | Convergence gate — violations to zero, SWEEP COMPLETE seal |
| `16-diagram-quality-code-review-multi-pass-pipeline.md` | Multi-pass code review with explicit quality gates before merge |
| `18-diagram-quality-analysis-engine-scoring-dashboard.md` | Quality radar — 5 dimensions, composite score, weakest axis highlighted |

---

## 📐 Architecture Facts (floor approximations — never exact counts)

| Metric | Floor Value | Source |
|---|---|---|
| Specialised reasoning engines | 350+ | `architecture_facts.orchestrator_files` |
| Governance rules | 60+ | `architecture_facts.governance_yamls_total` |
| Response rendering rules | 14 | `architecture_facts.response_rendering_rules` |
| Quality radar dimensions | 5 | `architecture_facts.quality_radar_dimensions` |
| Intent types routed | 35+ | `architecture_facts.intent_types` |
| Engineering knowledge domains | 15 | `architecture_facts.orchestrator_domains` |
````
