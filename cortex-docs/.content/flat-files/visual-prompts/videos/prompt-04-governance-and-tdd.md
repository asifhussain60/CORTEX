# Video Prompt 04 — Governance and TDD — Quality as Infrastructure

> **Duration:** 9 minutes · **Audience:** Software Engineers, Tech Leads
> **Depth:** 🔴 Deep engineering — shows code-level patterns and workflows
> **No overlap:** Image prompt-04 (shield wall anatomy) and prompt-06 (golden test pyramid) are static snapshots; this video shows governance rules **firing** in real-time and TDD cycles **executing** with ECG heartbeat rhythm

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> See `README.md` for full mandatory palette, motion style, text contrast rules, typography, and watermark.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the slide.** Every narration line must add something the viewer cannot get from reading the screen: the *why*, the *consequence*, the *non-obvious implication*, or the *emotional truth*. If a narration line restates visible text, cut it or rewrite it. See `README.md` §Narration Philosophy for full guidance and examples.

---

## PROMPT

Create a 9-minute animated explainer video titled **"Governance and TDD — Quality as Infrastructure"**. Two disciplines, unified by one principle: quality isn't an afterthought — it's embedded in every action.

### Scene 1 — Why Quality Breaks (0:00 – 1:30)

**Open on:** A familiar story. Glassmorphic panels show:
1. Developer writes code (glass card: ✅)
2. Developer skips tests — "I'll add them later" (card turns amber: ⚠️)
3. PR merged without governance check (card turns red: ❌)
4. Production bug. Rollback. Post-mortem. Two weeks lost.

The four cards fall like dominoes in slow motion.

**Narration:** "Notice it wasn't a bug that caused this. It was four reasonable decisions made in isolation. That's how quality breaks — not with a disaster, but with a sequence of shortcuts that each seemed fine at the time."

**Redesign:** The dominoes reassemble and fuse into a single **reinforced wall** — governance + TDD.

### Scene 2 — Governance Architecture (1:30 – 3:30)

**The shield wall materializes.** Four concentric tiers animate from outside in:

- **Tier 0 — Immutable Core** (red): Rules that NEVER bend. Examples: `CORE-002` (inline output only), `CORE-008` (TDD mandatory). Glass cards show the rule ID and one-sentence description.
- **Tier 1 — Business Logic** (amber): Company-specific policies. Examples: naming standards, import restrictions.
- **Tier 2 — Engineering Standards** (cyan): Best practices. Examples: type hints required, docstring coverage.
- **Tier 3 — Learned Patterns** (purple): Rules generated from historical data. Examples: "This pattern historically causes 3× more regressions."

**Enforcement timeline** (horizontal glass bar):
1. **Pre-commit hook** — rules fire before `git commit`
2. **CI pipeline** — rules fire in automated builds
3. **Runtime** — enforcement orchestrator validates during execution

**Animation:** A code change particle tries to pass through each tier. Most pass (green shimmer). One violation — the particle bounces back with a violation card: rule ID, severity, file path, remediation suggestion. The developer applies the fix; the particle passes on retry.

**Narration:** "P0 rules don't bend. Not because the system is rigid — because some decisions, once made wrong, are expensive to unmake. The immutable tier is protection against future-you making a shortcut."

### Scene 3 — TDD: The Heartbeat (3:30 – 5:30)

**ECG monitor fills the screen.** Heartbeat rhythm: red-green-blue.

**Full TDD cycle animation:**

1. **RED (test first):**
   - Glassmorphic code editor. Test file appears FIRST (highlighted).
   - Test runs. Red X. ECG spikes red.
   - Dark pill: `"CORE-008: Write the test before the implementation. No exceptions."`

2. **GREEN (make it pass):**
   - Implementation file opens alongside. Minimum code typed.
   - Test runs again. Green check. ECG spikes green.
   - Code count badge: just enough to pass.

3. **REFACTOR (improve with confidence):**
   - Code restructures — variable renames, extraction, cleanup.
   - Tests run automatically. All green. ECG spikes blue.
   - Badge: "All tests passing — safe to improve."

**Repeat the cycle 3 times** at increasing speed to show the rhythm becoming natural.

**Narration:** "Most engineers who've written tests after the fact will tell you the same thing: the test taught them something the implementation missed. Writing it first makes that lesson arrive before the mistake, not after."

**Analogy on dark pill:** *"Write a recipe (test), cook it (implement), taste-test it (verify), then plate it beautifully (refactor). Always taste before serving."*


### Scene 4 — Governance + TDD Together (5:30 – 7:00)

**Split the screen:** Left panel is governance shields, right panel is ECG heartbeat.

A new feature request enters:
1. **Intent classified** → `IMPLEMENT`
2. **Governance pre-check:** Are there test patterns for this module? (shield shimmer)
3. **TDD begins:** RED → GREEN → REFACTOR (heartbeat pulses)
4. **Governance post-check:** Type hints present? Docstrings present? Naming conventions followed? (shield cascade)
5. **Pre-commit hook fires:** All rules validated (shield wall glows green)
6. **Commit accepted.** Conventional commit message materializes.

**Key insight card:** *"TDD ensures correctness. Governance ensures compliance. Together, they ensure quality is structural — not aspirational."*

**Narration:** "These two things don't compete for time. They compound. Every test you write makes governance cheaper. Every rule you enforce makes tests more meaningful."

### Scene 5 — Enforcement Orchestrator in Action (7:00 – 8:00)

**A "day in the life" of the Enforcement Orchestrator:**

- It runs silently (no popups, no interruptions — per `CORE-049`)
- Only surfaces when something fails
- Shows a violation dashboard: severity distribution (P0/P1/P2), file paths, trending violations
- Auto-remediation: some violations auto-fix and re-validate

**Narration:** "The best governance system is one you forget is there — until it saves you. That's not passivity; it's design."

### Scene 6 — Closing (8:00 – 9:00)

**Three principles as glassmorphic cards:**

1. **Test First** — "If it's not tested, it doesn't exist"
2. **Govern Always** — "Rules are enforced automatically, not manually"
3. **Quality as Infrastructure** — "Quality is load-bearing, not decorative"

**Closing text:** **"Quality as infrastructure. Tested. Governed. Every commit."**

**Narration:** "Quality as infrastructure means it carries load. When the next engineer joins your team, they can't accidentally skip this. That's what structural means."

---

## Notes
- This video merges what were previously two separate videos (governance + TDD) — they are two halves of the same quality discipline
- The ECG heartbeat is the signature visual for TDD — recognizable and intuitive
- **No hardcoded rule counts** — rules shown by example and tier, not enumerated
- The enforcement orchestrator scene emphasizes SILENT operation (CORE-049)
