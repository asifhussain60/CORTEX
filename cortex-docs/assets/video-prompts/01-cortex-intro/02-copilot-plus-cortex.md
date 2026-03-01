# NotebookLM Video Prompt — 02 — Copilot + CORTEX: the practical difference

**Target length:** 6–10 minutes

## What this is
NotebookLM input to generate a **comparison video script + storyboard**.

## Purpose
Show a concrete, fair comparison: **assistant code suggestions** vs **governed workflow with validation gates**.

## Ground-truth constraints
- Speak in terms of **workflow**, **repeatability**, and **risk control**.
- Do not claim CORTEX is “smarter than Copilot.”
- No fabricated metrics. Show realistic sequences.

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create a 6–10 minute comparison video for business and engineering leaders. Compare assistant-only code suggestions with a governed workflow that includes validation gates (governance audit, TDD expectation, tests, and a detect→fix→rescan convergence loop). Be fair and non-hype. Use a calm professional narrator. Use only the provided sources; don’t invent metrics."

## Visual ingredients (upload as images for best results)
1) `cortex-docs/assets/diagrams/04-audit-audit-fix-pipeline.md`
2) `cortex-docs/assets/diagrams/05-workflow-tdd-cycle-and-fsm.md`
3) `cortex-docs/assets/diagrams/06-governance-sweep-completeness-core-064.md`

Visual guidance:
- Split-screen is encouraged: **left = “Assistant suggestions”** / **right = “Workflow + gates”**.
- Keep emphasis simple: highlight one element at a time.
- Overlay readable callouts: “Stage 0: Governance Audit”, “Convergence: Detect → Fix → Rescan”.

## Visual language
- Clean split-screen, consistent typography.
- Slow pans across diagram cards, subtle parallax.
- Neutral VS Code-like editor (no branding).

## Written Note / storyboard beats (NotebookLM should follow these)
Generate a **time-coded narration** and a **scene/slide outline** covering:
1) Setup: a small change request that risks regressions.
2) Lane 1 (assistant-only): quick suggestion, but missing enforceable checkpoints.
3) Lane 2 (CORTEX): staged flow with gates: governance audit → TDD expectation → tests → rescan loop.
4) Why leaders care: accountability, fewer surprises, clearer “done”.

Include per scene:
- which lane(s) are shown
- which diagram ingredient is shown (if any)
- which single element is emphasized
- on-screen callouts

## Audio guidance
- Narrator: instructional, calm.
- Subtle ambient music.
- Gentle UI click + typing foley.

## CORTEX voice (non-salesy)
- Narrator sounds like a **senior project lead / staff engineer**: calm, factual, and direct.
- Don’t praise the tool. Describe the **process change**: constraints, validation, and accountability.

## SDLC template visual guidance
- When you show “workflow templates”, render them as **YAML/JSON config** cards (structured keys, readable indentation) to reinforce “governance as code.”

## Make the loop unmissable (Audit → Fix → Rescan)
Ensure the narration explicitly defines the three steps so NotebookLM doesn’t compress them:
- **Audit**: produce a violations list (severity + file + remediation).
- **Fix**: changes are generated under workflow + governance constraints.
- **Rescan**: re-run compliance/tests; only close the loop when critical violations are **0**.

## Recommended hybrid workflow (best quality)
- Use NotebookLM for narrative + first-cut slides.
- Use a real screen recording for any VS Code “demo.”
- Stitch and time-control in an editor (e.g., Google Vids).
