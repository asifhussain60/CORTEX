# NotebookLM Video Prompt — Product Owner — Outcomes & adoption (role-targeted)

**Target length:** 6–10 minutes

## Purpose
Generate a Product Owner / delivery lead explainer that makes CORTEX adoption feel safe, measurable, and non-hype.

## Ground-truth constraints
- Emphasize *process quality* and *repeatability*.
- Avoid invented ROI numbers.
- Show that CORTEX enforces practices (tests, validation gates) and creates consistent structure.

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create a 6–10 minute explainer for product owners and delivery leaders. Focus on outcomes: consistent definition of done, fewer last-minute regressions, and clearer handoffs—without inventing ROI metrics. Explain CORTEX as workflow templates + validation gates that augment Copilot (not replace it). Calm, professional narrator. Use only the provided sources; don’t speculate."

## Visual ingredients (upload as images for best results)
1) `cortex-docs/assets/diagrams/03-workflow-sdlc-pipeline.md`
2) `cortex-docs/assets/diagrams/07-testing-testing-strategy-pyramid.md`
3) `cortex-docs/assets/diagrams/07-testing-testing-strategy-pyramid.md`

Visual guidance:
- A “delivery board” metaphor works well (feature card moves across columns).
- Keep emphasis simple: highlight one concept at a time.

## Written Note / storyboard beats (NotebookLM should follow these)
Generate a **time-coded narration** and a **scene/slide outline** covering:
1) PO pain points: unclear estimation, last-minute regressions, inconsistent definitions of done.
2) CORTEX concept: workflow templates that bake in readiness + validation gates.
3) Golden tests as acceptance criteria (plain English).
4) A sprint story: request → tests → implementation → smoke checks → done.
5) Safe adoption: start small (smoke + changed-tests loop).

Per scene include:
- board moment (which column)
- which diagram ingredient is shown (if any)
- which single element is emphasized
- on-screen callout text (short)

## Audio guidance
- Professional narrator.
- Subtle office ambience.
- Minimal uplifting score.

## CORTEX voice (product/delivery-friendly)
- Narrator should sound like a **senior delivery lead**: calm, practical, and outcomes-focused.
- Avoid hype language. Prefer: *definition of done, audit trail, validation gates, fewer surprises*.

## SDLC templates visual (make it concrete)
- When you reference workflow templates, show a **YAML/JSON config card** that looks like something a team could review in a PR.

## Define the loop (Audit → Fix → Rescan)
- **Audit**: produce an actionable list of violations and readiness gaps.
- **Fix**: implement changes under governance constraints (tests, standards, templates).
- **Rescan**: re-run checks/tests; the loop closes only when critical violations are **0**.

## Recommended hybrid workflow (best quality)
- Use NotebookLM for narrative + slides.
- Use a real screen recording for any VS Code “demo.”
- Stitch in an editor (e.g., Google Vids) for pacing and inserts.
