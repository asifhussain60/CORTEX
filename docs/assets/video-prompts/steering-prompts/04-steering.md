# Steering Prompt — Video 04: CORTEX for Security & SRE
## NotebookLM Cinematic Video — Setup Guide
**Source:** `sources/04-security-sre-source.md` | **Format:** Cinematic | **Narrator:** Female
**Updated:** 2026-03-09 | **Synthesis:** Phase 147 — auto-synthesised from live architecture

---

## 🔄 Synthesis Metadata (Phase 147 — do not hand-edit counts)

| Input | Source | Status |
|-------|--------|--------|
| Architecture facts | `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` § `architecture_facts` (verified 2026-03-09) | ✅ Floor approximations applied |
| Capability manifest | `cortex-registry/cortex-master.yaml` — phases 140–147 all treated as implemented (Planned-as-Implemented policy) | ✅ Applied |
| Open git issues | All open GitHub issues — capability gaps merged into manifest | ✅ Merged |
| Content sources | `docs/.content/07-security-cortex-as-compliance-layer.md` · `docs/.content/08-learning-rca-institutional-memory.md` · `docs/.content/10-infrastructure-sre-reliability.md` | ✅ Security/SRE propositions synthesised |
| Diagrams referenced | `14` · `17` · `21` (filenames from `docs/assets/diagrams/`) | ✅ By filename only — decoupled |

---

## ✅ NotebookLM Setup Checklist

- [ ] Create new notebook
- [ ] Upload `sources/04-security-sre-source.md` as the **only** source
- [ ] Studio panel → Video Overview → **Customize**
- [ ] **Format:** Cinematic ← not Explainer, not Brief
- [ ] **Visual Style:** Custom → paste the visual style block below
- [ ] **"What should the AI hosts focus on?"** → paste the steering prompt block below
- [ ] **Generate** → allow 20–30 minutes
- [ ] If SRE perspective is underweighted → use Fallback prompt below

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
Cinematic 6–8 minute video for security engineers and SREs. Open with two
parallel nightmares: CVE cascade flooding a dashboard (1 to 50 vulnerabilities)
and a 3 AM incident with MTTR ticking to 4 hours. CORTEX intervenes.

Show two resolution paths:
1. Security: a five-layer defence tower — pre-commit secrets detection,
   STRIDE threat modelling, CVE scanning, automated compliance evidence,
   and runtime enforcement — absorbs every CVE to zero. 60+ governance
   thresholds enforced at pre-commit, CI, and runtime. Knowledge Guidance
   Traceability (Phase 143) logs every security decision to a principle via
   DecisionTraceabilityLogger, so why the rule exists is never lost.
2. SRE: RCA identifies root cause in 12 minutes using four methodologies —
   Five-Whys, Fishbone, Fault-Tree, Causal-Chain — with institutional memory
   that automatically blocks the same incident pattern next time. The 8-stage
   self-healing Vacuum pipeline (Phase 141) guards 15 permanently protected
   source directories with SHA validation and 8 golden tests. Health
   Orchestrator monitors 350+ components. MTTR drops to 12 minutes.

End with RCA memory glowing as the same incident pattern is automatically
blocked. Female narrator, calm under pressure. Message: CORTEX eliminates
surprise.
```

---

## 🔄 Fallback Prompt (if SRE perspective is underweighted)

```
Create a 6–8 minute cinematic video for security and reliability engineers.
Equal split: first half shows CORTEX's five security defence layers catching
threats — pre-commit secrets detection, STRIDE threat modelling, CVE scanning,
automated compliance evidence from seconds not weeks, runtime enforcement via
60+ governance rules. Knowledge Guidance Traceability (Phase 143) ensures
every security decision is logged to a principle via DecisionTraceabilityLogger.
Second half shows CORTEX for SREs: Health Orchestrator monitoring 350+
components, Vacuum 8-stage self-healing pipeline with 15 permanently protected
directories and SHA validation, four RCA methodologies (Five-Whys, Fishbone,
Fault-Tree, Causal-Chain) with institutional memory preventing recurrence.
Red and amber accents. Female narrator. Tone: calm precision under pressure.
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
| VBP-017 Narrator | Female (Video 04 = security gravity convention) |
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
