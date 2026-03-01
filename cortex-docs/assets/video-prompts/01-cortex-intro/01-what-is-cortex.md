# NotebookLM Video Prompt — 01 — What is CORTEX? (Business-friendly, honest)

**Target length:** 5–8 minutes

## What this is (important)
NotebookLM’s **Steering Prompt** box is best for a *short mission statement*.

Use this doc as a **Written Note / storyboard source** inside the notebook. Keep it as guidance you can refine after NotebookLM generates a first cut.

## Audience
Business leaders / engineering leadership.

## Purpose
Explain CORTEX plainly: what it is, what it is not, and why it exists.

## Ground-truth constraints (stay factual)
- CORTEX is a **production-grade AI engineering framework** inside this repo.
- Describe scale using **stable lower bounds** (avoid exact counts):
  - **250+ orchestrators** (Python)
  - **25+ MCP tools** (VS Code MCP stdio integration)
  - **30+ governance YAML rules** (validation gates, TDD-first expectations, sweep completeness)
- CORTEX **orchestrates the host LLM** (e.g., Copilot Chat) rather than embedding its own ML model.
- Do **not** claim CORTEX replaces Copilot; position it as **workflow + governance + reliability** that augments AI assistance.

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create a 5–8 minute technical documentary for business leaders. Explain what CORTEX is (production-grade orchestration + governance), what it is not (not a replacement IDE or magical model), and why it exists (reliability, repeatability, auditability, team alignment). Use a calm professional narrator. Emphasize SDLC workflow templates and governance YAML rules. Use only the provided sources; don’t speculate beyond them."

## Visual ingredients (upload as images for best results)
NotebookLM works best when diagrams are available as **PNG/JPG ingredients**.

If you only have these as Markdown, export screenshots/renders and upload as images:

1) `cortex-docs/assets/diagrams/01-architecture-system-architecture-layers.md`
2) `cortex-docs/assets/diagrams/02-architecture-mcp-gateway-architecture.md`
3) `cortex-docs/assets/diagrams/03-workflow-sdlc-pipeline.md`

Visual guidance (high-level):
- Keep diagrams readable (clean background, crisp type).
- Prefer simple emphasis (one highlighted area at a time).
- Avoid “precise camera choreography” requirements; treat motion as illustrative, not deterministic.

## Visual language (cinematic but neutral)
- Establishing shots: modern office + engineering floor, tasteful, neutral, non-branded.
- UI: a VS Code-like editor (generic) used only to illustrate flow.
- Camera: slow dolly, gentle parallax, occasional crane move for transitions.
- Lighting: realistic, soft rim lighting; documentary feel.

## Audio + pacing guidance
- Calm, confident narrator.
- Subtle ambient synth bed.
- Light keyboard/mouse foley during the demo.
- No trailer-style dramatic music.

### CORTEX voice (keep it business-friendly)
- Narrator sounds like a **senior project lead / staff engineer**: calm, precise, and practical.
- Avoid marketing language and superlatives. Prefer engineering verbs: *validate, constrain, rescan, converge, audit, trace*.

### If you show “SDLC templates”, show them as config
- Any “workflow template” visual should look like a structured **YAML/JSON config file** (glassmorphic code card), not a vague diagram blob.

### Define the core loop explicitly (Audit → Fix → Rescan)
- **Audit**: run a scan that produces a concrete list of violations (with severity + file path + remediation hint).
- **Fix**: apply changes constrained by workflow templates + governance rules (tests-first where applicable).
- **Rescan**: re-run the same scan/tests until critical violations are **0** and tests are green (close the loop only at zero).

## Written Note / storyboard beats (NotebookLM should follow these)
Generate a **time-coded narration** and a **scene/slide outline** (you’ll do final editing after export).

Narration should cover:
1) Hook: “AI can write code fast… but production software is a system.”
2) What CORTEX is: orchestration + governance + testing habits.
3) What it isn’t: not a replacement IDE, not a magical model.
4) The problem it solves: reliability, repeatability, auditability, team alignment.
5) One concrete walkthrough (conceptual, honest): “audit → fix → rescan” loop.
6) Close: how leaders evaluate value (fewer regressions, clearer delivery discipline).

Scene/slide outline should include:
- scene name
- duration target
- on-screen callouts (use only): “250+ orchestrators”, “25+ MCP tools”, “30+ governance rules”
- which diagram ingredient is shown
- which single element is emphasized (one at a time)

## Demo beats (show, don’t exaggerate)
- Show a VS Code-like editor with a request such as: “/audit fix”.
- Show staged progress (generic, plausible).
- Briefly show governance rule YAML files (no secrets).
- Show a smoke-test-style summary (generic, plausible).

## Recommended hybrid workflow (best quality)
- Let NotebookLM produce the narrative + first-cut slides.
- Record the real “/audit fix” loop in VS Code via screen capture.
- Stitch in an editor (e.g., Google Vids) for timing, overlays, and the demo insert.

## Safety / brand
- No third-party logos.
- No claims like “guarantees” or “always.”
