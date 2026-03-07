# NotebookLM Video Prompt -- Tutorial 06 -- Your First Chat Workflows

**Target length:** ~7 minutes
**Audience:** New users who want to run their first meaningful CORTEX workflow from Copilot Chat
**Visual Theme:** Warm amber/gold glassmorphism (tutorial series accent)
**Prerequisite:** Tutorial 05 complete (MCP active, smoke test passing)
**Narrator gender:** Male (T06 -- even)
**Goal:** Viewer runs their first /audit fix safely and understands the output before it arrives

---

## ZERO-OVERLAP DECLARATION
This tutorial exclusively owns:
- The structured self-introduction prompt pattern: role + goal + constraints + time budget
- The challenge-first gate: CORTEX presenting trade-offs before acting
- Running /audit fix as a deliberate first action from chat -- including the warning framing
- The "first chat" visual: Copilot Chat window as the stage, request cards and workflow cards as the actors

Does NOT repeat: installation (T01), command catalogue intro (T02), E2E TDD build (T03), onboarding (T04), VS Code navigation (T05), result interpretation (T07).

---

## Steering Prompt
Paste into NotebookLM Customize - Steering Prompt:

"Create a ~7 minute hands-on tutorial showing a new user's first meaningful CORTEX chat workflow. Show: a structured introduction message, a challenge-first gate, a safe scan/health command with staged output, and then /audit fix as a deliberate choice with a warning. Narration must explain why structured inputs matter, what the challenge gate does, and how to read staged output -- not read the chat text. Use only provided sources."

---

## NARRATION RULE -- MANDATORY
The narrator never reads chat messages or command output aloud. Every narration line explains the principle behind the interaction, the decision being made, or the consequence of skipping a step.

---

## Cinematic treatment -- "First Chat"

**Unique opening (Copilot Chat as stage -- T06's visual identity):**
A Copilot Chat panel opens in VS Code. It is empty. Cursor blinking.
The chat panel is framed as a stage -- amber spotlight from above, everything else in the frame dimmed.
On-screen label: "Every workflow starts with a message. The quality of the message determines the quality of the outcome."
A naive message types itself: "Fix my code."
The narrator pauses. The message sits unanswered.
Then: the naive message fades. A structured version replaces it -- role + goal + constraints + time budget appearing word by word.
This is T06's visual identity: the contrast between an unstructured and a structured request, shown side-by-side before the tutorial proper begins.

### Visual Physics
- Copilot Chat panel: glassmorphic amber-bordered stage panel
- User messages: "request cards" -- amber glassmorphic pills
- CORTEX responses: "workflow cards" -- cyan-edged glassmorphic panels with stage nodes
- Stage nodes: small amber circles on the workflow card that activate as each pipeline stage completes

---

## Scene-by-scene breakdown

**SCENE 1 -- "The First Chat" [0:00-1:30]**
Naive message appears. Pauses. Fades. Structured message types.
Structured message card: "I am a backend engineer. I want to run a governance audit on the cortex/api/ module. I have 15 minutes. Do not modify files without my confirmation."
Narrator: "CORTEX responds better to constraints. Not because the tool requires them -- but because constraints eliminate ambiguity. An unconstrained request produces an unconstrained audit. A scoped request produces a scoped, reviewable result."

**SCENE 2 -- "The Challenge Gate" [1:30-3:00]**
CORTEX response card materialises: a challenge gate card.
Three options presented:
  Option 1: "Scan only -- I will review violations before any fixes are applied."
  Option 2: "Scan and fix P0 violations only -- no P1 changes without confirmation."
  Option 3: "Full /audit fix -- apply all fixes autonomously, including file modifications."
Narrator: "The challenge gate is not a bureaucratic checkpoint. It is the system presenting the trade-off surface before acting. Option 3 will modify files. Options 1 and 2 will not. The gate exists so that you make this choice deliberately -- not by accident."
User selects Option 1. Scan-only mode activates.

**SCENE 3 -- "First Workflow: Scan and Explain" [3:00-5:15]**
Copilot Chat: scan runs. Workflow card materialises with stage nodes.
Stage nodes activate sequentially:
  Governance check -- 3 P1 violations found (amber nodes)
  Type hint scan -- 12 missing (amber)
  Docstring check -- 4 missing (amber)
  Security scan -- 0 issues (green)
  Test coverage -- 84% (green)
Narrator: "The scan output is a map, not a verdict. P1 violations are significant -- they will block a production release. P0 would halt this workflow entirely. The green stages are already compliant. You now have a prioritised agenda: type hints first, then governance, then docstrings."
Lower-third: "P0 = blocking. P1 = significant. P2 = advisory. P3 = informational."

**SCENE 4 -- "When You Are Ready: /audit fix" [5:15-6:15]**
User types `/audit fix`. Before execution: a warning card appears:
"This will modify files. A git checkpoint will be created before changes. You can roll back with: git stash."
User confirms. /audit fix fires.
9-stage pipeline initiates. Progress bar fills amber.
Narrator: "/audit fix is the full pipeline. It modifies files. That is intentional -- CORTEX creates a git checkpoint first, so you can always roll back. Running it means you trust the governance rules enough to let the system apply them. If you are not ready for that, scan first and review."
Lower-third: "/audit fix creates a git checkpoint automatically before any file changes."

**SCENE 5 -- "What Just Happened" [6:15-End]**
Workflow card shows: all 9 stages green. AC_COMPLETE logged.
Narrator: "You ran your first complete CORTEX workflow. The scan told you what existed. The /audit fix resolved it. The AC marker recorded it. The SQLite trace proves it. Next time, you will know what to expect before the output arrives."
Outro card: "Next: Tutorial 07 -- Reading Results Like an Expert"

---

## Audio direction
- Naive message: a flat, neutral tone -- no engagement
- Naive message fades: a subtle dismiss sound
- Structured message: each word types with a soft amber key sound
- Challenge gate: three distinct amber tones for the three options
- Stage node activation: ascending amber clicks as each stage completes
- AC_COMPLETE: the clean series bell tone

---

## Production note
The naive-vs-structured contrast in Scene 1 is the most important moment in this tutorial. The naive message must genuinely look inadequate -- not cute or self-deprecating. The pause before it fades is essential: let the viewer feel the gap. Screen-capture inserts needed for actual Copilot Chat window in Scenes 1 and 4.
