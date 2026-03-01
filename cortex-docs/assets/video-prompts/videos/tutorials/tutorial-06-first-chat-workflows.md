# Tutorial 06 — Your First Chat Workflows (introduce yourself → first run)

> **Duration:** ~7 minutes · **Audience:** New users who want to “do something real” immediately
> **Visual Theme:** 🟠 Warm amber/gold glassmorphism (tutorial accent)
> **Prerequisite:** Tutorial 05 complete
> **Goal:** Viewer runs their first meaningful chat-based workflow safely (starting with a self-intro prompt and then a guided scan)

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create a ~7 minute hands-on tutorial that shows a safe first chat workflow: a structured self-introduction prompt, a challenge/proceed gate, and a guided scan. Narration must explain why structured inputs matter and how to interpret staged outputs—not read the chat text. Keep examples realistic and plausible. For real Copilot Chat visuals, plan to use screen capture inserts and stitch after export." 

## Visual guidance (NotebookLM-friendly)
- Show one stage/result card at a time.
- Use simple highlighting.
- Prefer screen capture for real chat UI moments.

## CORTEX voice (tutorial)
- Narrator should sound like a **staff engineer**: calm, specific, and grounded.
- Avoid “magic” framing; describe observable gates, checks, and outcomes.

## SDLC templates visual
- Any workflow template shown should look like **YAML/JSON config**.

## Define the trust loop explicitly (Audit → Fix → Rescan)
- **Audit**: find violations.
- **Fix**: apply constrained changes.
- **Rescan**: verify until critical violations are **0**.

---

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the steps or the code.** Narration explains the *why*, the *gotcha*, and the *discipline*.

---

## Cinematic simulation notes (optional; use as inspiration)

### Visual Physics & Ambience Protocol (Tutorial Amber Theme)
- Dark-blue vacuum (#0a0e27)
- Warm amber accent (#f5a623)
- Glassmorphic Copilot Chat panel as the “stage”
- Each user message becomes a “request card”; each CORTEX response becomes a “workflow card” with stage nodes

**SCENE 1 — “The moment: say hello the right way” (0:00–1:30)**
- Show the user typing an “introduce yourself” message.
- Then show a better “structured intro” version that includes:
  - role
  - goals
  - constraints
  - time budget
- On-screen callout: “Better inputs → better automation.”

**SCENE 2 — “Challenge-first, not hype-first” (1:30–3:00)**
- Demonstrate that before doing heavy work, CORTEX surfaces:
  - what it will change
  - what it will verify
  - what it won’t claim
- Show a “proceed” gate moment (without implying runtime guarantees).

**SCENE 3 — “First workflow: scan and explain” (3:00–5:30)**
- Show a safe scan/health-style command.
- Show staged progress (glass nodes lighting up), then a small results summary.

**SCENE 4 — “Second workflow: audit fix (when you’re ready)” (5:30–6:45)**
- Demonstrate `/audit fix` as the “big hammer” with a warning card: “This may change files; run it when you’re ready.”

**SCENE 5 — “Wrap-up” (6:45–7:00)**
- Next card: “Tutorial 07 — Reading results like an expert”.

---

## PROMPT

Create a ~7-minute amber-theme tutorial video titled **“Your First Chat Workflows (introduce yourself → first run)”**.

### Step 1 — A good intro message
Show two versions:
- naive: “Introduce yourself”
- structured: role + goal + constraints + time budget

**Narration intent:** explain that chat workflow quality depends on constraints and clarity.

### Step 2 — Challenge-first framing
Show CORTEX presenting trade-offs and a “proceed” gate.

**Narration intent:** explain governance and zero-regression intent (validation gates, tests) as a collaboration tool.

### Step 3 — First safe workflow
Demonstrate a safe scan/health workflow and how to read the output.

### Step 4 — When to use `/audit fix`
Demonstrate it as a deliberate choice.

**Narration intent:** explain that automation must be gated by validation and intent.

---

## Notes
- Keep claims factual.
- Do not show secrets.
- Depict output as plausible, not cherry-picked “perfect runs”.
