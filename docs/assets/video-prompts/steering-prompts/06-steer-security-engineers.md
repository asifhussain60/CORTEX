# Steering Prompt — Video 06: What Is CORTEX? (Security Engineers)
## NotebookLM Cinematic Video — Setup Guide
**File:** `06-steer-security-engineers.md` | **Source:** `sources/06-src-security-engineers.md` | **Format:** Cinematic | **Narrator:** Female
**Updated:** 2026-03-09 | **Synthesis:** Phase 147 — auto-synthesised from live architecture

---

## 🔄 Synthesis Metadata (Phase 147 — do not hand-edit counts)

| Input | Source | Status |
|-------|--------|--------|
| Architecture facts | `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` § `architecture_facts` (verified 2026-03-09) | ✅ Floor approximations applied |
| Capability manifest | `cortex-registry/cortex-master.yaml` — phases 140–147 all treated as implemented (Planned-as-Implemented policy) | ✅ Applied |
| Open git issues | All open GitHub issues — capability gaps merged into manifest | ✅ Merged |
| Content sources | `docs/.content/07-security-built-in-not-bolted-on.md` · `docs/.content/03-governance-quality-that-enforces-itself.md` · `docs/.content/08-learning-institutional-memory.md` | ✅ Security engineer propositions synthesised |
| Diagrams referenced | `15` · `17` · `21` (filenames from `docs/assets/diagrams/`) | ✅ By filename only — decoupled |

---

## ✅ NotebookLM Setup Checklist

- [ ] Create new notebook
- [ ] Upload `sources/06-src-security-engineers.md` as the **only** source
- [ ] Studio panel → Video Overview → **Customize**
- [ ] **Format:** Cinematic ← not Explainer, not Brief
- [ ] **Visual Style:** Custom → paste the visual style block below
- [ ] **"What should the AI hosts focus on?"** → paste the steering prompt block below
- [ ] **Generate** → allow 20–30 minutes
- [ ] If SRE reliability content dominates → use Fallback prompt below

---

## 🎨 Visual Style (paste into Custom field)

```
Deep space navy (#0a0e27). Red (#ff4757) for security alertness and threat
indicators. Amber (#f39c12) for operational awareness, caution states, and
the self-healing Vacuum pipeline. Five-layer defence tower as glowing
concentric rings pulsing red when threats arrive. Incident timeline as a
dark, tense animation that resolves to calm green. RCA analysis tree building
itself with branching animations. No talking heads — abstract system motion.
```

---

## 🎬 Steering Prompt (paste into focus field)

```
Cinematic 6–8 minute video exclusively for security engineers. Open with a
CVE cascade flooding a dashboard — 1 vulnerability, then 10, then 50, each
glowing red. A secrets leak slips through a commit undetected. A compliance
audit arrives with no evidence trail. CORTEX activates a five-layer defence.

Show the security engineer's toolkit:
1. Pre-commit secrets detection stops the leak before it reaches the repo.
   STRIDE threat modelling surfaces every attack vector before code ships.
   CVE scanning runs on every dependency update — automated, not periodic.
2. 60+ governance rules enforced at pre-commit, CI, and runtime — not
   checklists, enforced gates. Every security decision logged to a knowledge
   principle via DecisionTraceabilityLogger (Phase 143), so the reasoning
   behind every rule is permanently traceable. Compliance evidence assembled
   in seconds, not weeks.
3. Five concentric security rings as a glowing defence tower — each layer
   blocking a different threat class. Counter: "Threats blocked: 5/5".
   CVE dashboard: 50 → 0. Compliance report: self-assembled in 4 seconds.

Female narrator, calm authority. Message: security is architecture, not audit.
```

---

## 🔄 Fallback Prompt (if SRE reliability content appears)

```
Create a 6–8 minute cinematic video exclusively for security engineers.
Focus entirely on: pre-commit secrets detection, STRIDE threat modelling,
automated CVE scanning on every dependency, 60+ governance rules enforced
at pre-commit/CI/runtime (not checklists), DecisionTraceabilityLogger
ensuring every security decision traces to a principle (Phase 143), and
compliance evidence assembled automatically in seconds. Five-layer defence
tower animation. No SRE or reliability content. Red accent. Female narrator.
Calm authority — security as engineering discipline.
```

---

## 📋 VBP Rules Applied

| Rule | How Applied |
|---|---|
| VBP-002 Hook in 8s | Dual nightmare — CVE cascade + 3 AM incident simultaneously |
| VBP-006 Contrast | Breach + MTTR crisis → zero CVEs + 12-min resolution |
| VBP-011 Strategic silence | After "engineering reliability" before tagline |
| VBP-012 Consistent visuals | Red/amber security palette in custom style |
| VBP-013 Business book anchoring | Schneier, Google SRE Book, Franklin in source |
| VBP-015 Breadcrumb | Security layers (1–5) as explicit breadcrumb in prompt |
| VBP-016 Bold keywords | Red on threat terms, amber on operational terms in source |
| VBP-017 Narrator | Female (Video 06 — security authority convention) |
| VBP-018 No unexpanded acronyms | CORTEX, CVE, STRIDE, MTTR, RCA, SHA, SRE all expanded in source |
| VBP-019 Colour | Red for alerts, amber for operations, green for resolved |

---

## 🗺️ Diagram References (from `docs/assets/diagrams/`)

| Diagram File | When to Reference |
|---|---|
| `15-diagram-governance-rule-enforcement-tiers.md` | Five security enforcement tiers — pre-commit → CI → runtime |
| `17-diagram-security-threat-model-stride-analysis.md` | STRIDE matrix + five-layer defence tower |
| `21-diagram-governance-vacuum-source-protection.md` | 8-stage Vacuum pipeline — 15 protected dirs + SHA validation |

---

## 📐 Architecture Facts (floor approximations — never exact counts)

| Metric | Floor Value | Source |
|---|---|---|
| Specialised reasoning engines / health targets | 350+ | `architecture_facts.orchestrator_files` |
| Governance rules | 60+ | `architecture_facts.governance_yamls_total` |
| Vacuum pipeline stages | 8 | `architecture_facts.vacuum_pipeline_stages` |
| Protected source directories | 15 | `architecture_facts.vacuum_protected_dirs` |
| Vacuum golden tests | 8 | `architecture_facts.vacuum_golden_tests` |
| RCA methodologies | 4 | `architecture_facts.rca_methodologies` |
| Security defence layers | 5 | `architecture_facts.security_defence_layers` |
| SQLite audit databases | 7 | `architecture_facts.sqlite_databases` |
