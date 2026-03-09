````markdown
# Steering Prompt — Video 03: What Is CORTEX? (Product Owners)
## NotebookLM Cinematic Video — Setup Guide
**File:** `03-product-owners-steering.md` | **Source:** `sources/03-product-owners-source.md` | **Format:** Cinematic | **Narrator:** Female
**Updated:** 2026-03-09 | **Synthesis:** Phase 147 — auto-synthesised from live architecture

---

## 🔄 Synthesis Metadata (Phase 147 — do not hand-edit counts)

| Input | Source | Status |
|-------|--------|--------|
| Architecture facts | `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` § `architecture_facts` (verified 2026-03-09) | ✅ Floor approximations applied |
| Capability manifest | `cortex-registry/cortex-master.yaml` — phases 140–147 all treated as implemented (Planned-as-Implemented policy) | ✅ Applied |
| Open git issues | All open GitHub issues — capability gaps merged into manifest | ✅ Merged |
| Content sources | `docs/.content/09-lifecycle-from-idea-to-production.md` · `docs/.content/04-tdd-quality-flywheel.md` · `docs/.content/03-governance-quality-that-enforces-itself.md` | ✅ Product owner propositions synthesised |
| Diagrams referenced | `06` · `19` · `03` · `12` (filenames from `docs/assets/diagrams/`) | ✅ By filename only — decoupled |

---

## ✅ NotebookLM Setup Checklist

- [ ] Create new notebook
- [ ] Upload `sources/03-product-owners-source.md` as the **only** source
- [ ] Studio panel → Video Overview → **Customize**
- [ ] **Format:** Cinematic ← not Explainer, not Brief
- [ ] **Visual Style:** Custom → paste the visual style block below
- [ ] **"What should the AI hosts focus on?"** → paste the steering prompt block below
- [ ] **Generate** → allow 20–30 minutes
- [ ] If business leader strategy content dominates → use Fallback prompt below

---

## 🎨 Visual Style (paste into Custom field)

```
Deep space navy (#0a0e27). Emerald green (#00c471) as primary accent
representing delivery confidence and passing tests. Purple (#7b61ff) as
secondary for governance and traceability. Glassmorphism backlog panels
and sprint boards with frosted blur. User story cards animate from idea
to green CI badge. Acceptance criteria glow when matched to a passing test.
No talking heads — requirement-to-code flow animations throughout.
```

---

## 🎬 Steering Prompt (paste into focus field)

```
Cinematic 6–8 minute video exclusively for product owners and delivery leads.
Open with the PO's nightmare: a story marked Done that fails in production —
acceptance criteria were never validated, "done" was a guess. CORTEX
illuminates the full path from requirement to proof.

Show the product owner's journey:
1. Acceptance criteria written in plain language trace automatically to
   passing tests. The full chain — user story → acceptance criterion → test →
   green CI — is visible in a single animated flow. TDD enforced as
   infrastructure means every story has a test before a line of code is
   written. The PO can see proof of "done", not take it on faith.
2. PO Change Intelligence pipeline (Phase 140): a change in requirements
   propagates through the dependency graph, surfacing affected tests and
   stories instantly. Impact is quantified before commitment is made.
3. DecisionTraceabilityLogger links every engineering decision back to the
   knowledge principle that justified it. The PO can trace why a technical
   choice was made, months after the sprint closed.

Female narrator, collaborative tone. POs should feel empowered, not excluded.
Message: CORTEX makes "done" mean done.
```

---

## 🔄 Fallback Prompt (if business leader strategy content dominates)

```
Create a 6–8 minute cinematic video exclusively for product owners.
Focus on: acceptance criteria tracing to passing tests (story → criterion →
test → green CI animation), TDD enforced as infrastructure so every story
has a test before implementation, PO Change Intelligence pipeline quantifying
impact of requirement changes before commitment, and DecisionTraceabilityLogger
making every engineering decision traceable to the PO months later. Emerald
green accent. Female narrator. Collaborative, empowering tone — POs as
full engineering partners, not stakeholders.
```

---

## 📋 VBP Rules Applied

| Rule | How Applied |
|---|---|
| VBP-002 Hook in 8s | Story marked Done that fails in production — immediate PO pain |
| VBP-006 Contrast | Guess-based "done" → proof-based "done" as visual spine |
| VBP-011 Strategic silence | After green CI badge appears on the story card |
| VBP-012 Consistent visuals | Emerald green delivery palette in custom style |
| VBP-013 Business book anchoring | Jeff Patton, Mike Cohn in source quotes |
| VBP-015 Breadcrumb | Story → Criterion → Test → CI arc called out in prompt |
| VBP-016 Bold keywords | Emerald on "done", purple on traceability in source |
| VBP-017 Narrator | Female (Video 03 — product ownership convention) |
| VBP-018 No unexpanded acronyms | TDD, CI, PO, CORTEX, SSOT all expanded in source |
| VBP-019 Colour | Emerald primary, purple secondary, navy background |

---

## 🗺️ Diagram References (from `docs/assets/diagrams/`)

| Diagram File | When to Reference |
|---|---|
| `03-diagram-workflow-sdlc-pipeline.md` | Full delivery pipeline — idea to production |
| `06-diagram-governance-sweep-completeness-core-064.md` | Every issue catalogued and closed — nothing escapes |
| `12-diagram-governance-convergence-gate-core-068.md` | Convergence gate — violations to zero before ship |
| `19-diagram-orchestration-po-change-intelligence-pipeline.md` | PO change intelligence — requirement to passing test |

---

## 📐 Architecture Facts (floor approximations — never exact counts)

| Metric | Floor Value | Source |
|---|---|---|
| Specialised reasoning engines | 350+ | `architecture_facts.orchestrator_files` |
| Governance rules | 60+ | `architecture_facts.governance_yamls_total` |
| Intent types routed | 35+ | `architecture_facts.intent_types` |
| Audit pipeline stages | 9 | `architecture_facts.audit_pipeline_stages` |
| SQLite audit databases | 7 | `architecture_facts.sqlite_databases` |
````
