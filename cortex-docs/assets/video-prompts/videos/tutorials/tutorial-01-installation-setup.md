# NotebookLM Video Prompt — Tutorial 01 — Installation & First Run

**Target length:** ~6 minutes
**Audience:** First-time users — no prior CORTEX experience
**Visual Theme:** Warm amber/gold glassmorphism (tutorial series accent)
**Prerequisite:** None — this is the starting point
**Narrator gender:** Female (T01 — odd)
**Goal:** Viewer has CORTEX installed, MCP wired, and has run their first smoke test

---

## ZERO-OVERLAP DECLARATION
This tutorial exclusively owns:
- The prerequisites checklist (Python 3.9+, VS Code, Git, GitHub Copilot)
- The `git clone` + `pip install -r requirements.txt` + `setup-mcp.py` sequence
- The "cold start" visual metaphor: everything dark until prerequisites are verified

Does NOT repeat: command catalogue (T02), E2E feature build (T03), multi-repo onboarding (T04), VS Code deep-dive (T05), chat workflows (T06), result reading (T07).

---

## Steering Prompt
Paste into NotebookLM Customize - Steering Prompt:

"Create a ~6 minute hands-on installation tutorial for first-time CORTEX users. Cover prerequisites, clone/setup, MCP configuration, and first smoke test. Narration must explain why each step matters and call out common gotchas -- never read commands aloud. Tone: warm and instructional. Use only provided sources."

---

## NARRATION RULE -- MANDATORY
The narrator never reads the steps or the code. Every narration line adds the why it matters, the gotcha, or the non-obvious implication.

---

## Cinematic treatment -- "Cold Start Illumination"

**Unique opening (replaces generic Awakening scene used nowhere else):**
The screen is completely dark. No logo. No text. Silence for 1.5 seconds.
Then: a single amber dot blinks in the centre. A soft terminal cursor.
Text types character-by-character: `$ python3 --version`
Output appears: `Python 3.9.7`
The amber cursor transforms into the CORTEX logo -- expanding from the cursor position outward with warm amber radiance. The environment brightens from nothing to full amber-lit glassmorphism.
On-screen label: "Prerequisites met. Let's begin."
This opening is T01's signature -- the idea that nothing exists until the environment is verified. Other tutorials open in an already-lit environment.

### Visual Physics (Tutorial Amber Theme)
- Background: #0a0e27 dark-blue
- Accent: #f5a623 amber -- step borders, progress bars, active highlights
- Code panels: frosted glassmorphism, 3px amber left border, JetBrains Mono
- Completed steps: amber circle transitions to green (#7ed321) checkmark with soft flash
- Error state: holographic red glitch overlay

---

## Scene-by-scene breakdown

**SCENE 1 -- "Cold Start" [0:00-0:30]**
Dark screen. Terminal cursor blinks amber. `python3 --version` types. Logo expands from cursor position. Environment illuminates progressively.
Narrator: "Before CORTEX does anything, your environment must be ready. The framework checks before it runs -- so should you."

**SCENE 2 -- "Prerequisites Checklist" [0:30-1:15]**
Four glassmorphic checklist rows assemble: Python 3.9+, VS Code, Git, GitHub Copilot subscription.
Each row has an amber check-circle. As the narrator describes each item, the circle transitions to green.
Narrator: "GitHub Copilot is not optional -- CORTEX orchestrates it as the AI engine. Without it, the MCP tools have no LLM to call."

**SCENE 3 -- "Clone and Configure" [1:15-3:00]**
Terminal panel: `git clone` command. Progress particles flow amber. `pip install -r requirements.txt` -- packages appear as stacking glassmorphic cards.
`python3 scripts/setup-mcp.py` runs -- three config cards materialise confirming the MCP server block in `.vscode/settings.json`.
Narrator: "setup-mcp.py does one thing: writes the MCP server configuration. Cross-platform -- it detects Windows, macOS, Linux. Run it once; VS Code picks it up on next reload."
Lower-third: "Never edit .vscode/settings.json manually for MCP -- always use setup-mcp.py"

**SCENE 4 -- "First Smoke Test" [3:00-4:30]**
Amber terminal card: `make test-smoke`
Progress bar fills amber. Output scrolls. Green flash: PASSED. Amber environment fully lit.
Narrator: "The smoke test is your 'it's wired' contract. Not a performance benchmark -- a confirmation that the framework and its tests are coherent. If this fails, nothing else is trustworthy."

**SCENE 5 -- "Verify MCP is Active" [4:30-5:30]**
Copilot Chat panel opens. User types @cortex -- tool suggestions appear.
`cortex_verify op=mcp` call -- green confirmation card materialises.
Narrator: "MCP tools appear in Copilot Chat automatically when the server is configured. You don't start a server. You don't open a port. If you see the tool suggestions, MCP is active."

**SCENE 6 -- "What's Next" [5:30-End]**
Simple amber card: "Environment verified. MCP active. Smoke tests green."
Then: "Next: Tutorial 02 -- The Command Landscape"
Narrator: "A working installation is the foundation everything else runs on. Protect it: do not customise before you can run the smoke test clean."

---

## Audio direction
- Opening: 1.5 seconds complete silence, then soft amber pulse as cursor blinks
- Prerequisites: gentle chime per green checkmark
- Smoke test: rising tone on PASSED
- Pacing: slower than concept videos -- first-time users need processing time

---

## Production note
The cold-start opening must be the first 30 seconds. Do not replace with a generic logo fade. For VS Code UI, plan screen-capture inserts stitched after NotebookLM export.
