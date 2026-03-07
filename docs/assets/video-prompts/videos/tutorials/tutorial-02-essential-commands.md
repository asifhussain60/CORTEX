# NotebookLM Video Prompt -- Tutorial 02 -- The Command Landscape

**Target length:** ~7 minutes
**Audience:** Users who completed T01 and want to understand the full command set
**Visual Theme:** Warm amber/gold glassmorphism (tutorial series accent)
**Prerequisite:** Tutorial 01 complete (installation and smoke test passing)
**Narrator gender:** Male (T02 -- even)
**Goal:** Viewer knows which command to use at each stage of their workflow

---

## ZERO-OVERLAP DECLARATION
This tutorial exclusively owns:
- The full command catalogue: all major CORTEX commands mapped to their use-case moments
- The "command landscape" grid motif -- each command a card that illuminates when demonstrated
- When-to-use decision logic for each command (not just what it does, but when it fires)

Does NOT repeat: installation steps (T01), E2E feature build (T03), multi-repo onboarding (T04), VS Code setup (T05), chat workflow sequencing (T06), result interpretation (T07).

---

## Steering Prompt
Paste into NotebookLM Customize - Steering Prompt:

"Create a ~7 minute command-catalogue tutorial for CORTEX users who have a working installation. Cover the key commands grouped by workflow moment: daily TDD loop, pre-commit validation, full audit, health checks, and maintenance. Narration explains when to use each command and what the output means -- not what the command does syntactically. Use only provided sources."

---

## NARRATION RULE -- MANDATORY
The narrator never reads commands aloud. Every narration line explains the when, the why, or the what-to-do-if-it-fails.

---

## Cinematic treatment -- "Command Grid Illumination"

**Unique opening (replaces generic Awakening):**
The environment is already lit from T01 -- full amber glassmorphism. No cold start.
A 3x3 grid of glassmorphic command cards assembles from the centre outward. Each card starts dim (30% luminosity) with only the command name visible through frosted glass.
On-screen label: "8 commands. Every workflow moment covered."
The cards sit dark and waiting. As each command is demonstrated during the tutorial, its card permanently illuminates. By Scene 9, all cards are glowing amber.
This is T02's visual signature: progressive illumination of the command landscape.

### Command Card Grid Layout
Row 1: `/audit fix` | `make test-smoke` | `make test-changed`
Row 2: `/health` | `/vacuum` | `/challenge`
Row 3: `/totalrecall` | `/onboard` | `/debug`

### Visual Physics (Tutorial Amber Theme)
- Background: #0a0e27
- Accent: #f5a623 amber
- Active command card: elevated with amber volumetric spotlight, others dim to 40%
- Card illumination: permanent amber glow after demonstration
- Success output: green flash cascade from card outward

---

## Scene-by-scene breakdown

**SCENE 1 -- "The Grid" [0:00-0:30]**
Cards assemble from centre outward. All dim. Narrator:
"Every CORTEX workflow starts with one of these commands. By the end of this tutorial, you will know which card to reach for at any moment in your development cycle."

**SCENE 2 -- "Daily TDD Loop: make test-changed" [0:30-1:45]**
`make test-changed` card illuminates amber. Terminal output: only tests touching changed files run.
Narrator: "This is your fastest feedback loop. Testmon tracks which tests cover which files. After every save, run this -- not the full suite. Full suite is for commits, not keystrokes."
Lower-third: "make test-changed -- TDD inner loop. Seconds, not minutes."

**SCENE 3 -- "Pre-commit Gate: make test-smoke" [1:45-3:00]**
`make test-smoke` card illuminates. Progress bar fills amber. PASSED green flash.
Narrator: "Smoke tests run before you push. They confirm the framework is coherent -- not just your changes. If smoke fails after a merge, you have an integration issue, not a local issue. That distinction matters."
Lower-third: "make test-smoke -- 60 seconds. Run before every push."

**SCENE 4 -- "Full Audit: /audit fix" [3:00-4:15]**
`/audit fix` card illuminates -- largest card, centre prominence.
9-stage pipeline graphic assembles: governance check, lint, type hints, docstrings, test coverage, security scan, convergence gate, test suite, AC markers.
Narrator: "Audit fix is not a linter. It is a 9-stage pipeline that fixes, validates, and re-scans until zero P0/P1 violations remain. Run it before a PR, before a release, or when you want a production-readiness verdict."
Lower-third: "/audit fix -- full pipeline. Use deliberately, not on every save."

**SCENE 5 -- "Health Check: /health" [4:15-4:45]**
`/health` card illuminates. 22 health endpoint cards cascade in a grid.
Narrator: "Health checks query every orchestrator domain simultaneously. If a domain is degraded, health shows you which one -- before it fails a user request. Run health after major refactors."

**SCENE 6 -- "Maintenance: /vacuum" [4:45-5:15]**
`/vacuum` card illuminates.
Narrator: "Vacuum removes markdown sprawl -- stale documentation, orphaned report files, root clutter. It does not touch source code. Run it monthly or after a large documentation push."

**SCENE 7 -- "Challenge and Totalrecall" [5:15-5:45]**
`/challenge` and `/totalrecall` cards illuminate together.
Narrator: "Challenge surfaces alternatives before you commit to a plan. Totalrecall is a 7-phase holistic refactor -- use it when you want a full production-readiness sweep, not just an audit. These are deliberate, not daily."

**SCENE 8 -- "Onboard and Debug" [5:45-6:15]**
`/onboard` and `/debug` cards illuminate.
Narrator: "Onboard runs LENS analysis on a repository -- use it when adding a new codebase to the CORTEX workspace. Debug injects tracing markers, captures output, and generates a fix plan -- use it when a test failure has no obvious cause."

**SCENE 9 -- "Full Grid Illuminated" [6:15-End]**
All 9 cards glowing amber simultaneously. Camera pulls back to show the complete grid.
Narrator: "That's the landscape. Daily: test-changed and test-smoke. Weekly: audit fix. As needed: health, vacuum, challenge, totalrecall, onboard, debug. The right command at the right moment -- that's the discipline."
Outro card: "Next: Tutorial 03 -- Building a Feature End-to-End"

---

## Audio direction
- Card illumination: a sharp amber "lock-in" click per card
- Full grid illuminated: a rising chord as all 9 cards glow simultaneously
- No cold-start silence -- environment is already warm from T01's universe

---

## Production note
The grid layout is the defining visual. Maintain it throughout -- do not replace with a sequential list. The grid communicates at a glance that these commands are peers, not a hierarchy. NotebookLM slide deck: one card per slide highlight, full grid as final slide.
