# NotebookLM Video Prompt — Software Engineer — TDD + Convergence Gate (deep technical)

**Target length:** 10–15 minutes

## Purpose
Generate a technical walkthrough for engineers: how CORTEX pushes tests-first expectations, uses workflow gates, and iterates with detect→fix→rescan until stable.

## Non-negotiable truth constraints
- TDD-first is a core governance rule (CORE-008).
- Show that CORTEX uses workflow gates and test tiers (changed/smoke/unit/parallel).
- Avoid claiming “no bugs”; focus on *systematic validation*.

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create a 10–15 minute technical walkthrough for software engineers on how CORTEX enforces TDD-first expectations (CORE-008) and uses a detect→fix→rescan convergence loop for stability. Show realistic, plausible outputs (no invented coverage/metrics). Calm, technical narrator. Use only the provided sources; don’t speculate."

## Visual ingredients (upload as images for best results)
1) `cortex-docs/assets/diagrams/05-workflow-tdd-cycle-and-fsm.md`
2) `cortex-docs/assets/diagrams/05-workflow-tdd-cycle-and-fsm.md`
3) `cortex-docs/assets/diagrams/04-audit-audit-fix-pipeline.md`

Animation rules:
- Use terminal output as **stylized motion-graphics cards** (not real logs).
- Quick push-in on failure; slow pull-back on green.

## Written Note / storyboard beats (NotebookLM should follow these)
Generate a **time-coded narration** and a **scene/slide outline** including a mini demo story:
1) Write a failing test.
2) Minimal implementation.
3) Run “changed tests”.
4) Run smoke tests.
5) Convergence loop concept: detect → fix → rescan.
Keep outputs generic and plausible. No fake coverage.

Per scene include:
- code overlay focus
- which diagram ingredient is shown (if any)
- which single element is emphasized
- on-screen callouts (short)

## Audio guidance
- Clear technical narration.
- Subtle ambient synth.
- Keyboard/terminal foley.
- Very subtle success chime on green.

## CORTEX voice (engineering, non-salesy)
- Narrator should sound like a **staff engineer**: calm, specific, and skeptical by default.
- Avoid absolute claims; emphasize repeatable validation over “perfect code.”

## SDLC templates visual
- If you show workflow templates or gates, render them as **YAML/JSON** config snippets (primitives, gates, convergence loop), not hand-wavy diagrams.

## Explicitly define Detect → Fix → Rescan
Make the convergence logic explicit in narration:
- **Detect**: run compliance/tests to surface failures.
- **Fix**: apply the smallest change that resolves the failure while staying inside governance rules.
- **Rescan**: re-run the same checks; repeat until stable.

## Recommended hybrid workflow (best quality)
- Use NotebookLM for the narrative + diagram slides.
- Record real terminal/test runs via screen capture.
- Stitch in an editor for pacing and callouts.
