# Steering Prompt — Video 04: What Is CORTEX? (Software Engineers)
## NotebookLM Cinematic Video — Setup Guide
**File:** `04-software-engineers-steering.md` | **Source:** `sources/04-software-engineers-source.md` | **Format:** Cinematic | **Narrator:** Male
**Updated:** 2026-03-09 | **Synthesis:** Phase 147 — auto-synthesised from live architecture

---

## 🔄 Synthesis Metadata (Phase 147 — do not hand-edit counts)

| Input | Source | Status |
|-------|--------|--------|
| Architecture facts | `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` § `architecture_facts` (verified 2026-03-09) | ✅ Floor approximations applied |
| Capability manifest | `cortex-registry/cortex-master.yaml` — phases 140–147 all treated as implemented (Planned-as-Implemented policy) | ✅ Applied |
| Open git issues | All open GitHub issues — capability gaps merged into manifest | ✅ Merged |
| Content sources | `docs/.content/02-intelligence-how-cortex-understands-code.md` · `docs/.content/04-tdd-quality-flywheel.md` · `docs/.content/05-orchestration-the-engine-room.md` | ✅ Software engineer propositions synthesised |
| Diagrams referenced | `05` · `07` · `11` · `16` · `18` (filenames from `docs/assets/diagrams/`) | ✅ By filename only — decoupled |

---

## ✅ NotebookLM Setup Checklist

- [ ] Create new notebook
- [ ] Upload `sources/04-software-engineers-source.md` as the **only** source
- [ ] Studio panel → Video Overview → **Customize**
- [ ] **Format:** Cinematic ← not Explainer, not Brief
- [ ] **Visual Style:** Custom → paste the visual style block below
- [ ] **"What should the AI hosts focus on?"** → paste the steering prompt block below
- [ ] **Generate** → allow 20–30 minutes
- [ ] If quality engineering content dominates → use Fallback prompt below

---

## 🎨 Visual Style (paste into Custom field)

```
Deep space navy (#0a0e27). Cyan (#00d4ff) as engineering accent with gold
(#FFD700) for quality and golden tests. Glassmorphism code panels with
frosted blur and neon borders. TDD phases as distinct animated neon rings:
red, then green, then cyan refactor. Data streams through the LENS pipeline
with particle animations. Code transforms and morphs — nothing is static.
```

---

## 🎬 Steering Prompt (paste into focus field)

```
Cinematic 6–8 minute video exclusively for software engineers. Open with AI
generating code at zero context — CI fails, the terminal floods with errors,
the engineer stares at output that means nothing. CORTEX activates: LENS
pipeline illuminates the codebase layer by layer, context fills to 100%
from 140+ knowledge files across 15 engineering domains before a single
line is written.

Show three capabilities every software engineer gains:
1. TDD as a glowing neon loop (RED→GREEN→REFACTOR), enforced as infrastructure
   via CORE-008 — not suggested, not optional. SubPhaseComposer DRY refactor
   means every workflow step is composed once and reused everywhere.
   WorkflowGateway is the single source of truth for all step definitions,
   eliminating fork drift across the codebase.
2. 40+ MCP tools surfaced directly in VS Code — context, governance, and
   intent routing available without leaving the editor. 35+ intent types
   routed to the right orchestrator automatically.
3. Convergence gate dropping violations from 15 to zero — detect, fix, rescan
   loop (CORE-068) stamping SWEEP COMPLETE. Not a one-pass check. Eight debug
   injection strategies covering Python, Frontend, API, SQL, and .NET.

Male narrator, peer-to-peer tone. Engineers should feel understood, not sold to.
```

---

## 🔄 Fallback Prompt (if quality engineering content dominates)

```
Create a 6–8 minute cinematic video exclusively for software engineers.
Focus on: LENS pipeline giving full codebase context from 140+ knowledge
files across 15 domains before any keystroke; TDD enforced as infrastructure
(RED→GREEN→REFACTOR via CORE-008) with WorkflowGateway as single SSOT;
40+ MCP tools in VS Code; 8 debug injection strategies (Python, Frontend,
API, SQL, .NET); convergence gate (CORE-068) sweeping issues to zero.
Cyan accent. Male narrator. Peer-to-peer technical tone — respect the craft.
```

---

## 📋 VBP Rules Applied

| Rule | How Applied |
|---|---|
| VBP-002 Hook in 8s | AI at zero context, CI failure — immediate engineer pain |
| VBP-006 Contrast | Zero context → 100% context as visual spine |
| VBP-011 Strategic silence | After convergence reaches zero and gold seal stamps |
| VBP-012 Consistent visuals | Cyan + gold palette in custom style |
| VBP-013 Business book anchoring | Kent Beck, Deming in source quotes |
| VBP-015 Breadcrumb | LENS → TDD → Quality → Convergence arc in prompt |
| VBP-016 Bold keywords | Cyan on LENS/TDD, gold on golden tests in source |
| VBP-017 Narrator | Male (Video 03 = engineering audience convention) |
| VBP-018 No unexpanded acronyms | LENS, TDD, CORE-008, SSOT, DRY, CI all expanded in source |
| VBP-019 Colour | Cyan engineering, gold quality, red/green TDD phases |

---

## 🗺️ Diagram References (from `docs/assets/diagrams/`)

| Diagram File | When to Reference |
|---|---|
| `05-diagram-workflow-tdd-cycle-and-fsm.md` | TDD neon loop — RED→GREEN→REFACTOR enforced by CORE-008 |
| `07-diagram-testing-testing-strategy-pyramid.md` | Golden test → acceptance criterion traceability chain |
| `11-diagram-intelligence-lens-analysis-pipeline.md` | LENS four-layer pipeline filling to 100% context |
| `16-diagram-quality-code-review-multi-pass-pipeline.md` | Multi-pass code review — quality gates before merge |
| `18-diagram-quality-analysis-engine-scoring-dashboard.md` | Quality radar chart — 5 dimensions + composite score |

---

## 📐 Architecture Facts (floor approximations — never exact counts)

| Metric | Floor Value | Source |
|---|---|---|
| Specialised reasoning engines | 350+ | `architecture_facts.orchestrator_files` |
| Engineering knowledge domains | 15 | `architecture_facts.orchestrator_domains` |
| Knowledge files | 140+ | Stable figure — sourced from `.content/` manifest |
| Response rendering rules | 14 | `architecture_facts.response_rendering_rules` |
| Quality radar dimensions | 5 | `architecture_facts.quality_radar_dimensions` |
| Intent types routed | 35+ | `architecture_facts.intent_types` |
| Debug injection strategies | 8 | `architecture_facts.debug_strategies` |
