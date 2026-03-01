# Tutorial 07 — Reading Results Like a Pro (what to trust, what to do next)

> **Duration:** ~8 minutes · **Audience:** Users who ran their first workflows and now feel overwhelmed
> **Visual Theme:** 🟠 Warm amber/gold glassmorphism (tutorial accent)
> **Prerequisite:** Tutorial 06 complete
> **Goal:** Viewer can interpret stage output, severity levels, and knows exactly what to do next

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create a ~8 minute hands-on tutorial teaching how to read CORTEX outputs: stage progress, violations, convergence loop, and tests summary—then decide what to do next. Narration must teach decision-making and mental models, not read the output. Use realistic, plausible examples. For real UI, plan to use screen capture inserts and stitch after export." 

## Visual guidance (NotebookLM-friendly)
- Use clean output panels with callouts.
- Highlight one section at a time.
- Keep motion simple; prioritize readability.

## CORTEX voice (tutorial)
- Narrator should sound like a **calm reviewer**: “here’s what this output means and what to do next.”
- Avoid hype; focus on interpretation and decision-making.

## SDLC templates visual
- When referencing gates/templates, show them as **YAML/JSON config** cards.

## Make the convergence closure rule explicit
- “Done” means: issues found → fixed → **rescanned** until critical violations are **0**.

---

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the output.** Narration explains *how to think* about it.

---

## Cinematic simulation notes (optional; use as inspiration)

### Visual Physics & Ambience Protocol (Tutorial Amber Theme)
- Dark-blue vacuum (#0a0e27)
- Warm amber accent (#f5a623)
- Output becomes “result panels” that snap into a grid: stages, violations, tests, audit trail

**SCENE 1 — “Four panels that matter” (0:00–1:30)**
- Show a 2×2 grid:
  1) stage progress
  2) violations table
  3) convergence loop summary
  4) tests summary

**SCENE 2 — “Severity is prioritization, not drama” (1:30–3:15)**
- Demonstrate P0/P1/P2 as shelves:
  - P0 = stop the line
  - P1 = fix soon
  - P2 = plan

**SCENE 3 — “Convergence loop: why it exists” (3:15–5:00)**
- Animate detect → fix → rescan as a loop with a counter.
- On-screen callout: “Trust outputs that are re-validated.”

**SCENE 4 — “Good next steps” (5:00–7:15)**
- Show a decision tree:
  - If P0 exists → address first
  - If only P2 → schedule improvements
  - If tests fail → reproduce with the smallest tier

**SCENE 5 — “Wrap-up” (7:15–8:00)**
- Next: “Tutorial 08 — Onboarding your repo”.

---

## PROMPT

Create an ~8-minute tutorial video titled **“Reading Results Like a Pro (what to trust, what to do next)”** using the amber tutorial theme.

### Step 1 — Teach the four key panels
Stage progress, violations, convergence summary, tests.

### Step 2 — Explain severity levels
Make “severity = prioritization” the key lesson.

### Step 3 — Explain the convergence loop
Teach detect → fix → rescan as the trust mechanic.

### Step 4 — Provide a simple next-step decision tree
Show what to do depending on what you see.

---

## Notes
- Keep examples plausible, not perfect.
- Use diagrams sparingly; focus on interpretation skills.
