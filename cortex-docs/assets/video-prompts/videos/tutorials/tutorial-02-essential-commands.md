# Tutorial 02 — Essential Commands

> **Duration:** ~7 minutes · **Audience:** Daily users learning the workflow
> **Visual Theme:** 🟠 Warm amber/gold glassmorphism (tutorial accent)
> **Prerequisite:** Tutorial 01 complete — CORTEX installed and running
> **Goal:** Viewer knows the core commands for daily development

## Steering Prompt (paste into NotebookLM → Customize → Steering Prompt)
"Create a ~7 minute hands-on tutorial that introduces the core daily CORTEX commands (audit, health, vacuum, tests). The narrator never reads the command text; they explain why each command matters and how to interpret outputs. Use realistic, plausible outputs. Any true VS Code interactions should be treated as screen-capture inserts later—don’t fabricate precise UI behavior." 

---

## ⚠️ VISUAL IDENTITY — TUTORIAL THEME

> See tutorials `README.md` for amber/gold palette and tutorial visual rules.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the steps or the code.** Every narration line must add something the viewer cannot get from reading the screen: the *why it matters*, the *gotcha to watch for*, the *non-obvious implication*, or the *discipline behind the mechanic*. See tutorials `README.md` §Narration Philosophy for full guidance and examples.

---

## Visual guidance (NotebookLM-friendly)

NotebookLM tends to generate **illustration-style narrated slides**, not a deterministic 3D camera film.

- Keep visuals as simple “command cards” and “output panels”.
- Highlight one concept at a time.
- If you want “real terminal + real VS Code”, plan to screen record and stitch.

## CORTEX voice (tutorial)
- Narrator should sound like a **senior engineer** teaching workflow discipline.
- Avoid hype and superlatives. Prefer concrete verbs: *scan, validate, fix, rescan, interpret*.

## SDLC templates visual (when relevant)
- If a workflow template is shown, render it as a **YAML/JSON config** card (readable keys + indentation), not an abstract diagram.

## Make the trust loop explicit (Audit → Fix → Rescan)
- **Audit**: surface violations (severity + file + remediation hint).
- **Fix**: apply changes under workflow/governance constraints.
- **Rescan**: re-run validation/tests; close the loop only when critical violations are **0**.

## Cinematic notes (optional; use as inspiration)

### Visual Physics & Ambience Protocol (Tutorial Amber Theme)
- **Environment:** Dark-blue vacuum (#0a0e27) with ray-traced reflections on glass floor
- **Accent neon:** Warm amber (#f5a623) neon filaments for command card borders, highlights, progress
- **Command cards:** Frosted glassmorphism with amber icon glow, ray-traced surface reflections, internal neon circuitry
- **Transitions:** Active command card elevates with parallax depth + amber volumetric spotlight; inactive cards dim to 40% opacity
- **Lighting:** Volumetric amber fog, ray-traced caustics from active command neon, bioluminescent data particles
- **Feedback cues:** Green flash = success output, holographic glitch = violation/error, amber pulse = command executing
- **Temporal evolution:** Command grid starts dark; each demonstrated command permanently illuminates its card — by Scene 10 the full grid glows

**SCENE 1 — "The Awakening" (0:00–0:04)**
Camera: Static center-frame, locked on ray-traced glassmorphism floor.
Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric amber fog at ground level.
CORTEX logo (cortex-logo.png) fades in as large central hero image with electric-aura
glow — amber (#f5a623) pulse radiates outward. Ray-traced reflections shimmer in warm
tones. Hold 3s. Logo shrinks to bottom-right watermark (15% opacity) with ease-out
parallax slide. Amber "TUTORIAL" label materializes beside watermark.

**SCENE 2 — "The Command Landscape" (0:04–1:00)**
Camera: Slow orbital drift above, looking down at 45° angle.
8 glassmorphic command cards materialize in a 2×4 grid with time-lapse mechanical
assembly — each card frame constructs first, then frosted glass fills in, then amber
icon ignites with neon filament glow. Cards are initially dim (30% luminosity) —
they will illuminate as each command is demonstrated.
Ray-traced reflections of the card grid shimmer on the glass floor below. Volumetric
amber fog drifts between cards. Each card has a small amber icon and one-line description
visible through the frosted glass.
Camera: Slow macro zoom on the grid, then pull-back to establish the landscape.

**SCENE 3 — "/audit fix Deep Dive" (1:00–2:15)**
Camera: Dolly-in toward the `/audit fix` card — card elevates with parallax depth
separation and amber volumetric spotlight illuminates from above. Other cards dim.
Split demonstration: LEFT panel shows clean run (all stages green with bioluminescent
cascade), RIGHT panel shows failing run (governance violation with holographic glitch →
convergence loop with transformation timeline: red sparks shed → green stabilization).
Ray-traced caustics from the violation-to-fix transition ripple across the glass floor.
Card permanently illuminates to full amber glow after demonstration. Camera pulls back
to grid — 1 of 8 cards now lit.

**SCENE 4 — "/audit Scan-Only" (2:15–2:45)**
Camera: Dolly-in to `/audit` card — elevates with amber spotlight.
Glassmorphic output panel materializes with particle condensation — violations table
with "Remediation suggested" column. Rows populate with amber text and severity badges
(P0 red, P1 amber, P2 blue). No auto-fix animation — violations remain visible,
emphasizing deliberate choice.
Card illuminates. Pull-back to grid — 2 of 8 lit.

**SCENE 5 — "/vacuum Cleanup" (2:45–3:30)**
Camera: FPV tracking shot to `/vacuum` card — elevates with spotlight.
Before/after split: LEFT shows cluttered file tree with red holographic highlights on
orphaned files, RIGHT shows clean tree with green glow. Transition: orphaned files
fragment into particles and dissolve — particle stream flows to an amber "ARCHIVED"
badge. Bioluminescent cleanup sweep moves through the tree.
Card illuminates — 3 of 8 lit.

**SCENE 6 — "/health Check" (3:30–4:00)**
Camera: Dolly-in to `/health` card.
Glassmorphic health grid materializes — 22 orchestrator nodes in a honeycomb layout.
Each node pings with amber pulse and returns green (healthy), amber (warning), or red
(error) with appropriate neon glow. Lidar sweep across the grid confirms status.
Summary badge materializes as holographic floating card with counts.
Card illuminates — 4 of 8 lit.

**SCENE 7 — "/digest Ingestion" (4:00–4:45)**
Camera: Slow dolly to `/digest` card.
Three-pipeline visualization: three parallel glassmorphic tubes with amber neon,
bioluminescent data particles flow through each (structure analysis, content extraction,
knowledge integration). Particles converge at a central knowledge node that brightens
with each particle absorbed — particle evolution from raw amber to rich gold.
Card illuminates — 5 of 8 lit.

**SCENE 8 — "/challenge Alternatives" (4:45–5:30)**
Camera: FPV approach to `/challenge` card — macro zoom hero moment.
Developer request materializes as holographic text. Three glassmorphic alternative cards
fan out with time-lapse assembly — each card has amber neon border with pros/cons lists
visible through frosted glass. Trade-off matrix materializes as a holographic grid with
ray-traced reflections — recommended approach highlighted with amber volumetric pulse.
Card illuminates — 6 of 8 lit.

**SCENE 9 — "/debug Pipeline" (5:30–6:15)**
Camera: Tracking shot to `/debug` card.
Five-phase pipeline materializes as a linear track of glassmorphic nodes: INJECT →
CAPTURE → ANALYZE → FIX-PLAN → CLEANUP. Bioluminescent particle travels through
each phase — at INJECT, debug markers appear as amber holographic pins; at CLEANUP,
the pins dissolve with particle fragmentation, leaving no trace. Ray-traced caustics
emphasize the clean removal.
Card illuminates — 7 of 8 lit.

**SCENE 10 — "Testing Commands & Reference Card" (6:15–7:00)**
Camera: Pull-back orbital view of the full grid.
Final card (testing commands) illuminates — 8 of 8 now lit. The full command grid
glows with warm amber luminosity. Ray-traced reflections of the fully-lit grid create
a warm amber pool on the glass floor below.
Glassmorphic reference card assembles with time-lapse construction — all 8 commands
with icons, descriptions, and "when to use" context. Holographic shimmer on the card
surface. Amber arrow with particle trail: "Tutorial 3 →"
Fade to black with ray-traced reflections dimming last.

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

**Dark pill:** *"Prefer `make test-*` or `scripts/run_tests.py` over raw `pytest` — the CORTEX test runner standardizes import modes, parallelism, and reporting."*

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
