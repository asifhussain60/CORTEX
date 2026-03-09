````markdown
# Steering Prompt — Video 07: What Is CORTEX? (Site Reliability Engineers)
## NotebookLM Cinematic Video — Setup Guide
**File:** `07-sre-steering.md` | **Source:** `sources/07-sre-source.md` | **Format:** Cinematic | **Narrator:** Male
**Updated:** 2026-03-09 | **Synthesis:** Phase 147 — auto-synthesised from live architecture

---

## 🔄 Synthesis Metadata (Phase 147 — do not hand-edit counts)

| Input | Source | Status |
|-------|--------|--------|
| Architecture facts | `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` § `architecture_facts` (verified 2026-03-09) | ✅ Floor approximations applied |
| Capability manifest | `cortex-registry/cortex-master.yaml` — phases 140–147 all treated as implemented (Planned-as-Implemented policy) | ✅ Applied |
| Open git issues | All open GitHub issues — capability gaps merged into manifest | ✅ Merged |
| Content sources | `docs/.content/10-infrastructure-built-to-last.md` · `docs/.content/08-learning-institutional-memory.md` · `docs/.content/03-governance-quality-that-enforces-itself.md` | ✅ SRE propositions synthesised |
| Diagrams referenced | `04` · `12` · `21` · `17` (filenames from `docs/assets/diagrams/`) | ✅ By filename only — decoupled |

---

## ✅ NotebookLM Setup Checklist

- [ ] Create new notebook
- [ ] Upload `sources/07-sre-source.md` as the **only** source
- [ ] Studio panel → Video Overview → **Customize**
- [ ] **Format:** Cinematic ← not Explainer, not Brief
- [ ] **Visual Style:** Custom → paste the visual style block below
- [ ] **"What should the AI hosts focus on?"** → paste the steering prompt block below
- [ ] **Generate** → allow 20–30 minutes
- [ ] If security engineering content dominates → use Fallback prompt below

---

## 🎨 Visual Style (paste into Custom field)

```
Deep space navy (#0a0e27). Amber (#f39c12) as primary accent for operational
awareness, alert states, and the self-healing Vacuum pipeline. Emerald green
(#00c471) for resolved incidents and healthy system states. Incident timeline
animates as a dark tense bar that resolves to calm green. RCA tree builds
itself with branching node animations. Health dashboard with 350+ monitored
components pulses in real time. No talking heads — abstract ops motion.
```

---

## 🎬 Steering Prompt (paste into focus field)

```
Cinematic 6–8 minute video exclusively for site reliability engineers. Open
with the 3 AM nightmare: a production incident with MTTR ticking toward 4
hours, runbooks that don't match the system, and the same failure pattern
that happened 6 months ago. CORTEX eliminates the repeat.

Show three capabilities every SRE gains:
1. Health Orchestrator monitoring 350+ components in real time — not periodic
   polling but continuous signal. Anomaly surfaces before it becomes incident.
   The dashboard shows health, not just uptime.
2. RCA Memory Engine identifies root cause in 12 minutes using four
   methodologies — Five-Whys, Fishbone, Fault-Tree, Causal-Chain — matched
   automatically to incident category. Every RCA generates a Prevention Rule
   stored in institutional memory. The same incident pattern is automatically
   blocked next time. MTTR drops to 12 minutes. Recurrence: zero.
3. Vacuum pipeline (Phase 141): 8-stage self-healing workspace guardian
   running autonomously — naming, root clutter, empty files, orphan modules,
   markdown sprawl, build artefacts, OS artefacts. 15 permanently protected
   source directories guarded by SHA validation and 8 golden tests. Rollback
   checkpoint before every sweep. Workspace health: 100%.

Male narrator, SRE peer tone. Calm precision under pressure. Message: CORTEX
turns institutional memory into a system component, not a person.
```

---

## 🔄 Fallback Prompt (if security engineering content appears)

```
Create a 6–8 minute cinematic video exclusively for site reliability engineers.
Focus on: Health Orchestrator monitoring 350+ components continuously (not
periodic), RCA Memory Engine with four methodologies (Five-Whys, Fishbone,
Fault-Tree, Causal-Chain) reducing MTTR to 12 minutes and preventing
recurrence via institutional memory, and Vacuum 8-stage self-healing pipeline
guarding 15 protected directories with SHA validation. No security CVE content.
Amber accent. Male narrator. Calm precision — SRE peer tone.
```

---

## 📋 VBP Rules Applied

| Rule | How Applied |
|---|---|
| VBP-002 Hook in 8s | 3 AM incident + MTTR ticking — immediate SRE pain |
| VBP-006 Contrast | Repeat incident nightmare → institutional memory blocking recurrence |
| VBP-011 Strategic silence | After MTTR counter drops to 12 min and locks |
| VBP-012 Consistent visuals | Amber ops palette in custom style |
| VBP-013 Business book anchoring | Google SRE Book, Limoncelli in source quotes |
| VBP-015 Breadcrumb | Health → RCA → Vacuum → Prevention arc in prompt |
| VBP-016 Bold keywords | Amber on incident terms, green on resolved states in source |
| VBP-017 Narrator | Male (Video 07 — SRE peer convention) |
| VBP-018 No unexpanded acronyms | MTTR, RCA, SRE, SHA, CORTEX, SSOT all expanded in source |
| VBP-019 Colour | Amber for operations/alerts, green for resolved, navy background |

---

## 🗺️ Diagram References (from `docs/assets/diagrams/`)

| Diagram File | When to Reference |
|---|---|
| `04-diagram-audit-audit-fix-pipeline.md` | Autonomous audit pipeline — continuous health enforcement |
| `12-diagram-governance-convergence-gate-core-068.md` | Convergence gate — CORTEX iterates until system is clean |
| `17-diagram-security-threat-model-stride-analysis.md` | Threat surface awareness — security feeds into SRE posture |
| `21-diagram-governance-vacuum-source-protection.md` | 8-stage Vacuum pipeline — 15 protected dirs + SHA + rollback |

---

## 📐 Architecture Facts (floor approximations — never exact counts)

| Metric | Floor Value | Source |
|---|---|---|
| Components monitored by Health Orchestrator | 350+ | `architecture_facts.orchestrator_files` |
| Governance rules | 60+ | `architecture_facts.governance_yamls_total` |
| Vacuum pipeline stages | 8 | `architecture_facts.vacuum_pipeline_stages` |
| Protected source directories | 15 | `architecture_facts.vacuum_protected_dirs` |
| Vacuum golden tests | 8 | `architecture_facts.vacuum_golden_tests` |
| RCA methodologies | 4 | `architecture_facts.rca_methodologies` |
| SQLite audit databases | 7 | `architecture_facts.sqlite_databases` |
````
