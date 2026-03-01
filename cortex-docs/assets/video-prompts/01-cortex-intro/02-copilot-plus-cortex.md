# NotebookLM Video Prompt — 02 — Copilot + CORTEX: Governed Workflow vs. Raw Suggestions

**Target length:** 7–9 minutes
**Audience:** Engineering Managers, Senior Developers — people who already use Copilot daily
**Narrator gender:** Male (Video 02 — even, per VBP-017)
**Visual theme:** Dark-blue glassmorphism · Side-by-side split (cyan LEFT, amber RIGHT)
**Series position:** Contrast video — the only video doing a direct lane-vs-lane comparison

---

## ⚠️ ZERO-OVERLAP DECLARATION
This video exclusively owns:
- The lane-vs-lane comparison (Copilot suggestion vs. CORTEX-governed workflow)
- The "governance as code" framing (YAML templates as the enforcement mechanism)
- The business case for *adding* governance on top of Copilot (not replacing it)

Does NOT repeat: CORTEX identity (Video 01), architecture internals (Video 03), TDD mechanics (Videos 04/SE01).

---

## Steering Prompt
*Paste into NotebookLM → Customize → Steering Prompt:*

> "Create a 7–9 minute comparison video for engineering managers and senior developers who already use GitHub Copilot. Compare two lanes: Lane 1 — assistant suggestions only (fast, unconstrained); Lane 2 — CORTEX-governed workflow (constrained, validated, auditable). Be scrupulously fair: Lane 1 is not 'bad', it's incomplete for production requirements. Narrate like a senior engineer presenting at an internal tech talk — factual, non-promotional. Use only provided sources. Do not invent metrics."

---

## Ground-truth constraints
- Neither lane is framed as "wrong" — Lane 1 is adequate for exploration; Lane 2 is required for production.
- CORTEX adds: Stage 0 governance audit, IntentRouter, SDLC workflow templates, TDD gate, detect→fix→rescan loop.
- Workflow templates live at `cortex-registry/workflows/templates/` — show as YAML/JSON config cards, not abstract diagrams.
- The loop closes only when P0 + P1 violations = 0 AND tests pass — never at "good enough".

---

## Visual ingredients
Upload as PNG/JPG:
1. `cortex-docs/assets/diagrams/04-audit-audit-fix-pipeline.md` — the 9-stage pipeline (Lane 2 centre)
2. `cortex-docs/assets/diagrams/06-governance-sweep-completeness-core-064.md` — sweep completeness (Lane 2 close)
3. `cortex-docs/assets/image-prompts/shared/01-platform-architecture-overview.prompt.md` — architecture overview (Scene 2)

**Cinematic treatment — Split-screen identity:**
- LEFT panel (Lane 1): warm white #f8f8f0 text, subtle amber tint — represents "assistant speed"
- RIGHT panel (Lane 2): cyan #00d4ff text, deep navy glassmorphism — represents "governed discipline"
- Centre divider: a thin neon vertical line, cyan on the right half, amber on the left
- Each lane has its own persistent "Stage Tracker" — Lane 2's stages light green as they complete
- Camera: alternates dolly-in to the active lane; never stays on one lane longer than 90 seconds (VBP-007)

---

## Scene-by-scene breakdown

**SCENE 1 — "Same starting point" [0:00–1:00]**
Visual: A single feature request card materialises in the centre: `"Add rate-limiting to the payment API endpoint"`. It's identical for both lanes.
Both lane panels dim and wait. The request card pulses once.
Narrator (male, measured): *"Same request. Two paths. One goes fast. One goes far."*
The request card splits — half slides to Lane 1, half to Lane 2. The divider neon line ignites.

**SCENE 2 — "Lane 1: The Fast Path" [1:00–3:00]**
Visual: Lane 1 panel brightens. Copilot suggestion appears — code generates, fast, clean.
No governance stage. No test gate. Code goes directly to commit.
Speed callout: `"Suggestion in 4 seconds"`
Stage tracker (Lane 1): SUGGEST → COMMIT — two steps, both green, nothing in between.
Narrator: *"This is the right tool for exploration, for prototyping, for getting unstuck. It moves fast because it's not constrained."*
Brief pause. Then: *"In a production codebase, 'unconstrained' has a cost."*
A red incident marker materialises quietly at the bottom of the Lane 1 panel — no drama, just present.

**SCENE 3 — "Lane 2: The Governed Path" [3:00–6:30]**
Visual: Lane 2 panel brightens. Six glassmorphic stage nodes materialise as a vertical pipeline (one at a time, VBP-004):
  Stage 0 — Governance Audit: checks against 32 YAML rules. Violations card shows: `CORE-008: TDD gate required`
  Stage 1 — IntentRouter: classifies intent as IMPLEMENT. Confidence: 0.94.
  Stage 2 — LENS Analysis: scans codebase — dependency on `payment_service.py` detected.
  Stage 3 — Workflow Template: `implement-workflow.yaml` loaded — YAML config card visible: gates, primitives, convergence loop.
  Stage 4 — TDD Gate (RED→GREEN→REFACTOR): failing test written first. Implementation follows. All tests pass.
  Stage 5 — Rescan: `/audit fix` confirms 0 P0/P1 violations. AC_COMPLETE timestamp logged.
Each stage node illuminates as the narration reaches it — others dim to 40% (VBP-009).
YAML snippet visible at Stage 3: `rule_id: CORE-008`, `gate: test_must_fail_before_implementation`.
Narrator: *"Every stage is a checkpoint. Not a speed bump — a contract. The code only moves forward when the contract is satisfied."*

**SCENE 4 — "Why Both Matter" [6:30–End]**
Visual: Both lanes visible simultaneously. Side-by-side summary table materialises:
  | | Lane 1 | Lane 2 |
  | Speed | ⚡ Fast | Measured |
  | Audit trail | ✗ None | ✓ Full SQLite log |
  | TDD enforced | ✗ Optional | ✓ Gate-blocked |
  | Convergence | ✗ Single pass | ✓ Loop until zero |
  | Right for | Exploration | Production |
Narrator: *"The goal isn't to slow down Lane 1. It's to know when you're in each lane — and to make Lane 2 as repeatable and automatic as Lane 1 feels today."*
Final callout: `"Governed workflows. Verifiable outputs."` Fade to dark.

---

## Audio direction
- Ambient synth bed: dual-timbre — Lane 1 slightly warmer tonally when active, Lane 2 slightly cooler
- UI foley: subtle click on each stage gate passing (Lane 2 only) — not Lane 1
- No music at the "why both matter" close — let the comparison breathe

---

## Production note
Use NotebookLM for narrative + split-screen slide generation. For Lane 2 Stage 4 (TDD), record a real `make test-changed` run and stitch in. The suggestion animation in Lane 1 can be a simple typewriter effect on a static code sample.
