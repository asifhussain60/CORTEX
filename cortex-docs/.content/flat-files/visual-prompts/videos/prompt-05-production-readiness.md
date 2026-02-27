# Video Prompt 05 — Production Readiness — Audit, Sweep, and Convergence

> **Duration:** 9 minutes · **Audience:** Software Engineers, DevOps, Tech Leads
> **Depth:** 🔴 Advanced — shows the 9-stage audit pipeline and convergence loop
> **No overlap:** Image prompts show static architecture; this video animates the `/audit fix` pipeline end-to-end with stage transitions and the convergence loop cycling until zero violations

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> See `README.md` for full mandatory palette, motion style, text contrast rules, typography, and watermark.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the slide.** Every narration line must add something the viewer cannot get from reading the screen: the *why*, the *consequence*, the *non-obvious implication*, or the *emotional truth*. If a narration line restates visible text, cut it or rewrite it. See `README.md` §Narration Philosophy for full guidance and examples.

---

## PROMPT

Create a 9-minute animated explainer video titled **"Production Readiness — Audit, Sweep, and Convergence"**. Show how CORTEX ensures a codebase is production-ready through its multi-stage audit pipeline.

### Scene 1 — The Problem with "Ship It" (0:00 – 1:15)

**Open on:** A glassmorphic deployment panel. Big green button: "DEPLOY". A developer's cursor hovers. Hesitation.

Mental checklist floats as glass cards:
- "Did I run all the tests?" → ❓
- "Are the governance rules passing?" → ❓
- "Is the documentation updated?" → ❓
- "Did I check for security issues?" → ❓
- "Is the health endpoint working?" → ❓

Cards multiply — 10, 15, 20 concerns. Stack wobbles.

**Narration:** "That hesitation before hitting deploy is a symptom. It means you know something could be wrong, but you can't verify it without running through a checklist no one has fully memorized."

**Transition:** Cards snap into a single command: `/audit fix`

### Scene 2 — The 9-Stage Pipeline (1:15 – 5:30)

**A vertical glass pipeline materializes.** Nine stages, each a glassmorphic chamber with a connecting tube. A glowing audit particle enters Stage -1.

**Stage -1: Environment Readiness (1:15 – 1:45)**
- Quick scan: Python version, dependencies, development tools
- Green badges appear for each validated requirement
- If something's missing: auto-install attempt with progress indicator
- Particle turns green, moves to Stage 0

**Stage 0: Inflight Upgrade (1:45 – 2:15)**
- Git icon. Fetch from origin/main. Check: are we behind?
- If behind: merge animation (two glass branches joining)
- If current: fast green check
- Particle descends to Stage 1

**Stage 1: Governance Pre-Flight (2:15 – 2:45)**
- Shield wall scan. Governance rule index loads.
- Quick validation of the audit spec itself — "Is the auditor configured correctly?"
- Green cascade. Particle descends.

**Stage 2: Production Scan (2:45 – 3:30)**
- **The core.** A scanning grid spreads across a codebase visualization.
- Check badges appear in sequence — each one a production readiness criterion:
  - Architecture integrity, wiring contracts, import health, test coverage, documentation, etc.
- Some checks: green ✅. Some: amber ⚠️. Occasional red ❌.
- Results aggregate into a **violations table**: severity (P0/P1/P2), file path, description.
- Dark pill: *"Each check has a specific remediation — not just 'fix it.'"*

**Narration:** "The violations table isn't a wall of shame. It's a prioritized work order — severity first, with exactly what to do. The difference between overwhelming and actionable."

**Stage 3: Wiring Validation (3:30 – 3:50)**
- Architecture integrity scan. Import chains visualize as a directed graph.
- Broken connections flash red. Valid ones glow green.

**Stage 4: Health Checks (3:50 – 4:10)**
- A grid of orchestrator icons. Each pings and returns a health status.
- Grid fills with green dots. A few amber — warnings logged.

**Stage 5: Vacuum Cleanup (4:10 – 4:30)**
- Markdown files, orphaned documents, root clutter — identified and archived.
- Glass dust particles swept away by a translucent vacuum beam.

**Stage 6: Meta-Audit (4:30 – 4:50)**
- The auditor audits itself. Prompt files, agent definitions, configuration consistency.
- Self-referential loop icon with checkmarks.

**Stages 7–8: Convergence Loop (4:50 – 5:30)**
- **KEY SCENE.** This is the differentiator.
- A circular glass track. The audit particle enters the loop.
- **Iteration 1:** Detect violations → apply auto-fix → re-scan → still 3 P0s remaining
- **Iteration 2:** Fix remaining → re-scan → 1 P1 remaining
- **Iteration 3:** Fix → re-scan → **ZERO P0, ZERO P1**
- Loop exit condition illuminates: `p0 == 0 AND p1 == 0`
- Dark pill: *"Not a single pass. Not 'good enough.' The loop continues until zero critical violations."*

**Narration:** "This is the architectural decision that most CI systems never make: don't accept partial. Most pipelines report and move on. This one doesn't move on until it's done."

### Scene 3 — Stage 9: Tests and Completion (5:30 – 6:30)

- Full test suite fires. Progress bar fills.
- Results: passed count, failed count (zero), coverage percentage.
- **AC markers** flash: `AC_START` at the beginning, `AC_COMPLETE ✅` with timing.
- Activity logged to persistent database (SQLite icon with write animation).

**Narration:** "Every audit run is a permanent record. Not just for compliance — for learning. When you see the same fix appearing in iteration 3 every time, you know what the next governance rule should be."

### Scene 4 — Sweep Completeness (6:30 – 7:30)

**The Sweep Completeness Contract:**

A catalogue of issues visualized as a glass checklist. As each item is addressed, it transitions from red → amber → green. The contract is simple:

**Glassmorphic rule card:** *"Every fix sweep must exhaust its full catalogue. No partial sweeps. No 'we'll get the rest later.'"*

**Counter animation:** Issues remaining: 12 → 8 → 5 → 2 → 0. ✅ Sweep complete.

**Analogy:** *"If you're cleaning a house, you don't stop at the living room. Sweep completeness means every room, every corner."*

### Scene 5 — Convergence Guarantee (7:30 – 8:15)

**Contrast two approaches:**

**Left (dim): Traditional CI**
- Single pass. "47 warnings." Developer sighs. Merges anyway.
- Badge: "Technical debt: accumulating."

**Right (vibrant): CORTEX Convergence**
- Loop runs. Violations decrease each iteration. Exits only at zero critical.
- Badge: "Technical debt: addressed."

**Narration:** "Most tools report problems. CORTEX fixes them — and keeps fixing until they're gone."

**Narration (on the dim/vibrant contrast):** "The left column is honest about what most teams ship with. The right is what shipping with confidence actually requires."

### Scene 6 — Closing (8:15 – 9:00)

**The audit pipeline zooms out.** All 9 stages visible as a complete glass column. Green glow throughout. A single command floats above: `/audit fix`.

**Three principles:**
1. **Comprehensive** — "Every aspect of production readiness, checked"
2. **Convergent** — "Loops until zero critical violations"
3. **Auditable** — "Every action logged permanently"

**Closing text:** **"Production-ready isn't a feeling. It's a verified state."**

**Narration:** "That closing line is worth sitting with. The feeling of being ready and the verified state of being ready are very different things. One depends on memory. The other doesn't."

---

## Notes
- The convergence loop (Stages 7–8) is the hero scene — it's what differentiates CORTEX from static linters
- **No hardcoded check counts** — checks described by category, not number
- The sweep completeness contract is a key governance concept that should resonate with engineering leaders
- Stage timing is realistic — the full pipeline typically runs in minutes, not hours
