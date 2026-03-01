# NotebookLM Video Prompt — Curious Users — Learn engineering concepts with CORTEX

**Target length:** 8–12 minutes

## Purpose
Entice curious users (new or improving engineers) by teaching real software engineering habits that CORTEX reinforces: testing, workflows, architecture thinking.

## Ground-truth constraints
- Don’t imply CORTEX teaches everything automatically; it provides structure, prompts, and guardrails.
- Keep examples beginner-friendly but not childish.

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create an 8–12 minute learning-focused video for curious or early-career engineers. Teach practical habits CORTEX reinforces—workflows, TDD basics, and why the testing pyramid matters—without hype. Position CORTEX as structure and guardrails that augment Copilot. Warm, clear narrator. Use only the provided sources; don’t speculate."

## Visual ingredients (upload as images for best results)
1) `cortex-docs/assets/diagrams/07-testing-testing-strategy-pyramid.md`
2) `cortex-docs/assets/diagrams/05-workflow-tdd-cycle-and-fsm.md`
3) `cortex-docs/assets/diagrams/09-orchestration-request-sequence.md`

Visual guidance:
- Blend “animated whiteboard” readability with gentle motion.
- Highlight one concept at a time (avoid overwhelming beginners).

## Written Note / storyboard beats (NotebookLM should follow these)
Generate a **time-coded narration** and a **scene/slide outline** teaching:
1) What beginners struggle with: “what do I do next?”
2) Workflows: repeatable steps, not magic.
3) TDD basics in plain English.
4) Testing pyramid: why not all tests are equal.
5) Growth path: start small, run smoke tests, iterate.

Per scene include:
- which diagram ingredient is shown
- which single element is emphasized
- on-screen chapter title

## Audio guidance
- Warm narrator.
- Light inspiring ambient music.
- Subtle whiteboard marker + keyboard foley.

## CORTEX voice (beginner-friendly, not childish)
- Narrator should sound like a **calm mentor**: clear, practical, and not salesy.
- Avoid hype adjectives; use concrete verbs: *practice, verify, iterate, validate*.

## SDLC templates visual
- When you mention “workflow templates”, show a simple **YAML/JSON config card** (with a few keys) so viewers understand it’s structured, not vibes.

## Define what “Audit → Fix → Rescan” means
- **Audit**: find issues.
- **Fix**: change the code.
- **Rescan**: re-check and re-test until critical issues are **0**.

## Recommended hybrid workflow (best quality)
- Use NotebookLM for narrative + slides.
- If you want real code/terminal, use screen capture and stitch afterward.
