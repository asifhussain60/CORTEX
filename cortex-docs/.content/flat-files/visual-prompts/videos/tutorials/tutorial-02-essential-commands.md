# Tutorial 02 — Essential Commands

> **Duration:** ~7 minutes · **Audience:** Daily users learning the workflow
> **Visual Theme:** 🟠 Warm amber/gold glassmorphism (tutorial accent)
> **Prerequisite:** Tutorial 01 complete — CORTEX installed and running
> **Goal:** Viewer knows the core commands for daily development

---

## ⚠️ VISUAL IDENTITY — TUTORIAL THEME

> See tutorials `README.md` for amber/gold palette and tutorial visual rules.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the steps or the code.** Every narration line must add something the viewer cannot get from reading the screen: the *why it matters*, the *gotcha to watch for*, the *non-obvious implication*, or the *discipline behind the mechanic*. See tutorials `README.md` §Narration Philosophy for full guidance and examples.

---

## PROMPT

Create a ~7-minute tutorial video titled **"Essential Commands"** using the amber/gold tutorial theme. Walk through the commands a developer uses every day.

### Step 1 — The Command Landscape (0:00 – 1:00)

**Glassmorphic command grid** — 8 command cards arranged in a 2×4 grid. Each has an amber icon and a one-line description. This is the overview — we'll explore each one.

| Command | Purpose |
|---|---|
| `/audit fix` | Full production-readiness scan + autonomous fix |
| `/audit` | Scan only, no auto-fix |
| `/vacuum` | Clean up markdown sprawl and root clutter |
| `/health` | Check all orchestrator health endpoints |
| `/digest {path}` | Intelligent content ingestion |
| `/onboard {repo}` | Analyze and onboard a repository |
| `/challenge {request}` | Generate alternatives with trade-offs |
| `/debug {path}` | Multi-stack debug pipeline |

**Narration:** "Eight commands. That's a deliberately small surface area. The goal was one command per intent — not a command for every possible variation."

### Step 2 — `/audit fix` — The Daily Driver (1:00 – 2:15)

**Quick recap** (not a full repeat of Tutorial 01):
- Run before committing significant changes
- 9 stages, convergence loop, test suite
- Show a CLEAN run: all stages green, zero violations, tests pass

**Then show a FAILING run:**
- A governance violation detected (missing type hint)
- Convergence loop fixes it automatically
- Re-scan: clean

**Dark pill:** *"Run this before every significant commit. It catches what you miss."*

**Narration:** "The difference between a clean run and a failing run isn't just output — it's what the failure tells you. A governance catch at commit time is a five-minute fix. The same issue in a PR review is a conversation. In production, it's an incident."

### Step 3 — `/audit` — Scan Without Fix (2:15 – 2:45)

- Same scan, but violations are REPORTED, not fixed
- Use when you want to see the state without automated changes
- Show output: violations table with "Remediation suggested" column

**Narration:** "Use `/audit` when you want to make a deliberate choice about what to fix and in what order. Use `/audit fix` when you want the system to decide. Both are valid — knowing which to use is judgment."

### Step 4 — `/vacuum` — Clean Up Sprawl (2:45 – 3:30)

- Show a workspace with orphaned markdown files, duplicate docs, root-level clutter
- `/vacuum` identifies them, categorizes (archive/delete/consolidate), and cleans
- Before/after: file tree with red highlights → clean tree

**Narration:** "Documentation sprawl accumulates invisibly. By the time it's a problem, the cost of cleaning it is already high. Running vacuum weekly means it never becomes a project."

### Step 5 — `/health` — Orchestrator Health Check (3:30 – 4:00)

- Show the health grid: each orchestrator pings and reports status
- All green: healthy system
- One amber: warning (e.g., orchestrator responding slowly)
- Show the summary: healthy count, warning count, error count

### Step 6 — `/digest {path}` — Content Ingestion (4:00 – 4:45)

- Point `/digest` at a documentation folder or a large file
- Show the 3-pipeline ingestion: structure analysis, content extraction, knowledge integration
- Result: content is now searchable and integrated into CORTEX's knowledge base

**Narration:** "Feed CORTEX your existing documentation. It doesn't just store it — it understands and integrates it."

**Narration (on the 3-pipeline output):** "The result isn't a file import. It's integration — which means LENS can now surface this content when it's relevant to a scan or a request."

### Step 7 — `/challenge {request}` — Generate Alternatives (4:45 – 5:30)

**Powerful but underused command:**

- Developer types: `/challenge "Implement caching with Redis"`
- CORTEX responds with ≥2 alternatives:
  1. **Redis** — pros, cons, complexity estimate
  2. **In-memory LRU** — pros, cons, complexity estimate
  3. **HTTP caching headers** — pros, cons, complexity estimate
- Trade-off matrix with recommended approach highlighted

**Narration:** "The trade-off matrix is the part most developers skip — and then spend two weeks regretting. The challenge command surfaces the alternatives before you've written a line of code."

### Step 8 — `/debug {path}` — Multi-Stack Debug (5:30 – 6:15)

- Point `/debug` at a failing test or problematic file
- Show the 5-phase pipeline:
  1. **INJECT** — Debug markers placed (non-destructive)
  2. **CAPTURE** — Execution data collected
  3. **ANALYZE** — Root cause identified
  4. **FIX-PLAN** — Remediation plan generated
  5. **CLEANUP** — All debug markers removed automatically

**Narration:** "The cleanup phase is the one most debug tools skip. Injected markers that don't get removed become noise, then become tech debt. CORTEX removes what it adds — by design."

### Step 9 — Testing Commands (6:15 – 6:45)

**Quick reference for test modes:**

```bash
make test-preflight    # < 10s — audit gate
make test-changed      # TDD loop — only changed files
make test-smoke        # < 60s — pre-commit sanity
make test              # Full unit suite
make test-parallel     # Full suite, multi-core
```

**Dark pill:** *"Always use `make test-*` or `scripts/run_tests.py`. Never raw `pytest` — CORTEX test runner handles import modes, parallelism, and reporting."*

**Narration:** "Raw pytest bypasses the settings that make CORTEX's test suite fast and deterministic. The make commands aren't convenience aliases — they're what ensures the results match what CI sees."

### Step 10 — Closing Reference Card (6:45 – 7:00)

**Glassmorphic reference card** — all 8 commands with icons, one-line descriptions, and "when to use" context. This is the takeaway.

**Next:** "Tutorial 3 — Building a Feature End-to-End" (amber arrow)

---

## Notes
- Each command is shown with REAL output, not mock output
- The `/challenge` demo is a highlight — it shows CORTEX thinking, not just executing
- Test commands use `make` (macOS/Linux) with Windows alternatives noted
- Pacing: ~45 seconds per command — enough to show, not enough to bore
