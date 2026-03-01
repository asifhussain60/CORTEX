# Tutorial 05 — Getting Started in VS Code (Your first 5 minutes)

> **Duration:** ~6 minutes · **Audience:** First-time users who installed CORTEX
> **Visual Theme:** 🟠 Warm amber/gold glassmorphism (tutorial accent)
> **Prerequisite:** Tutorial 01 complete
> **Goal:** Viewer can open the repo in VS Code, confirm MCP is active, and run the first “safe” verification commands

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create a ~6 minute hands-on tutorial for first-time users in VS Code: open the workspace, confirm MCP is wired, and run first safe verification commands. Narration must explain what to look for and common failure modes rather than reading steps. Any true VS Code UI should be captured via screen recording and stitched after export." 

## Visual guidance (NotebookLM-friendly)
- Highlight one VS Code panel at a time.
- Keep motion illustrative and readable.
- Plan on screen-capture inserts for credibility.

## CORTEX voice (tutorial)
- Narrator should sound like a **patient senior engineer**.
- Don’t read menus. Explain the “why”: what MCP unlocks and how verification habits prevent surprises.

## SDLC templates visual
- When templates/gates are referenced, show **YAML/JSON config** cards (structured, reviewable).

## Define the reliability loop
- Call out **Audit → Fix → Rescan** as the default “trust-building” pattern.

---

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the steps or the code.** Narration explains the *why*, the *gotcha*, and the *discipline*.

---

## Cinematic simulation notes (optional; use as inspiration)

### Visual Physics & Ambience Protocol (Tutorial Amber Theme)
- Dark-blue vacuum background (#0a0e27)
- Warm amber accent (#f5a623)
- Frosted-glass panels for: VS Code, Copilot Chat, settings JSON snippet
- Feedback cues: amber pulse (in progress), green flash (verified), red holographic glitch (blocked)

**SCENE 1 — “Open the Workspace” (0:00–0:45)**
- Show VS Code opening the CORTEX workspace.
- File explorer highlights `cortex/`, `cortex-registry/`, and `tests/` as three pillars.
- On-screen callout: “Keep CORTEX runnable before you customize it.”

**SCENE 2 — “Confirm MCP is wired” (0:45–2:00)**
- Macro zoom into `.vscode/settings.json` showing the MCP server block.
- Copilot Chat opens.
- Show a “tools available” moment (generic UI), then a verification call.

**SCENE 3 — “First safe commands” (2:00–4:30)**
- In Copilot Chat, demonstrate:
  - `cortex_verify (op: mcp)` (or the repo’s equivalent verification command exposed in chat)
  - `cortex_tools_catalog` to show discoverability
  - `cortex_load (op: rules)` to show governance rules can be loaded
- Each command appears as a glassmorphic “command card” that lights up when it succeeds.

**SCENE 4 — “Run a fast sanity test” (4:30–5:45)**
- Show an amber terminal card running the smoke test mode (keep output generic, plausible).
- On-screen callout: “Smoke tests are your ‘it’s wired’ contract.”

**SCENE 5 — “What to do next” (5:45–6:00)**
- Outro card: “Next: Tutorial 06 — Your first workflow in chat”.

---

## PROMPT

Create a ~6-minute tutorial video titled **“Getting Started in VS Code (Your first 5 minutes)”** using the amber/gold tutorial theme.

### Step 1 — Open the CORTEX workspace
Show VS Code opening the repo. Highlight these folders:
- `cortex/` (runtime framework)
- `cortex-registry/` (rules + workflows)
- `tests/` (verification)

**Narration intent:** why keeping these three aligned matters for long-term maintainability.

### Step 2 — Confirm MCP is active
Show `.vscode/settings.json` (MCP server config) and Copilot Chat.

**Narration intent:** explain that MCP is how CORTEX becomes “tooling” instead of “prompting”.

### Step 3 — First safe commands in chat
Demonstrate “verification-first” usage:
- verify MCP
- list tools
- load rules

**Narration intent:** explain safe discovery vs running destructive commands.

### Step 4 — Run a smoke-test-style sanity gate
Show the smoke test mode as the final “wired & ready” confirmation.

**Narration intent:** explain why a fast, repeatable test gate is a team collaboration accelerant.

---

## Notes
- Keep everything honest: no claims about cloud deployment or auto-magic.
- Do not show secrets/keys.
- VS Code UI is generic; no third-party logos.
