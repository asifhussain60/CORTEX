# Video Prompt 06 — Golden Tests and Security-First Development

> **Duration**Dark pill:** *"The cheapest security fix is the one that never reaches the repository."*

**Narration:** "A hardcoded secret that reaches GitHub is not a development mistake anymore. It's a security incident. The cost difference between those two things is why this layer exists."** 8 minutes · **Audience:** Software Engineers, Security Engineers
> **Depth:** 🔴 Deep engineering — shows golden test lifecycle and security layer integration
> **No overlap:** Image prompt-06 (golden test pyramid) is a static quality gate snapshot; image prompt-07 (security layers) is a static concentric ring. This video shows golden tests **promoting and demoting** in real-time, and security checks **firing at each SDLC stage**

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> See `README.md` for full mandatory palette, motion style, text contrast rules, typography, and watermark.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the slide.** Every narration line must add something the viewer cannot get from reading the screen: the *why*, the *consequence*, the *non-obvious implication*, or the *emotional truth*. If a narration line restates visible text, cut it or rewrite it. See `README.md` §Narration Philosophy for full guidance and examples.

---

## PROMPT

Create an 8-minute animated explainer video titled **"Golden Tests and Security-First Development"**. Two engineering practices that together ensure correctness and safety.

### Scene 1 — Beyond "Tests Pass" (0:00 – 1:15)

**Open on:** A glassmorphic test results panel. Green bar: "247 tests passed." Developer smiles.

But wait — zoom into the results:
- 30% test one trivial getter
- 15% are duplicates with slight variations
- Coverage metric says 80% — but critical error paths are untested
- No test validates the complete end-to-end audit trail

**Narration:** "80% coverage sounds like rigor. But coverage measures which lines were touched — not whether the important things were actually validated. Golden tests solve the right problem."

### Scene 2 — Golden Test Architecture (1:15 – 3:15)

**A pyramid materializes** — three tiers, glass with golden edges:

- **Base — Standard Tests:** Wide foundation. Regular unit tests. Gray glass.
- **Middle — Promoted Tests:** Tests that have consistently passed, cover critical paths, and demonstrate architectural contracts. Amber glass. Fewer in number.
- **Apex — Golden Tests:** The essential tests. If these break, the system is fundamentally wrong. Gold glass with a glow. A curated, small set.

**Quality Gate dimensions** appear as 5 radial indicators on the pyramid face:
1. **Determinism** — "Does it produce the same result every time?"
2. **Coverage** — "Does it cover a critical, non-trivial path?"
3. **Independence** — "Can it run in isolation?"
4. **Speed** — "Does it execute in under 2 seconds?"
5. **Diagnostic Value** — "When it fails, does the error message tell you exactly what broke?"

**Promotion animation:** A standard test glows amber → golden based on score across these 5 dimensions.

**Demotion animation:** A golden test that becomes flaky (fails intermittently) loses its golden status — drops back to standard tier. Glass dims from gold → gray.

**Narration:** "A test that was golden last month and is flaky today is telling you something. Demotion isn't failure — it's the system being honest about the state of your code."

### Scene 3 — The End-to-End Audit Trace (3:15 – 4:30)

**This is the KEY capability — what makes golden tests trustworthy.**

A golden test executes. At each step, an **audit marker** appears:

```
AC_START: AC-GOLDEN-2026-01-15T14:30:00
  → Test: test_orchestrator_routes_implement_intent
  → Quality Score: 4.8/5.0
  → Dimensions: [determinism: ✅, coverage: ✅, independence: ✅, speed: 0.3s ✅, diagnostic: ✅]
  → Execution: GREEN
AC_COMPLETE: AC-GOLDEN-2026-01-15T14:30:00 ✅ (312ms)
```

The trace writes to a **persistent database** (SQLite icon). Arrow from the database to a **queryable dashboard**: "Show me all golden test failures in the last 30 days."

**Narration:** "When a golden test fails, you don't need to dig through logs to understand what broke. The trace tells the story. That diagnostic value is engineered in — it doesn't happen by accident."

### Scene 4 — Security-First: The Five Layers (4:30 – 6:30)

**Transition:** From test integrity to code integrity. Five concentric security layers build outward:

**Layer 1 — Pre-Commit (innermost, red):**
- Secret scanning. A hardcoded API key detected — red flash, commit blocked.
- Pattern: regex matching against known secret formats.
- Dark pill: *"The cheapest security fix is the one that never reaches the repository."*

**Layer 2 — Governance Rules (amber):**
- Security-specific governance rules enforce: no `eval()`, no unsanitized inputs, no deprecated crypto.
- Violation card appears with remediation.

**Layer 3 — LENS Security Scan (cyan):**
- LENS beam sweeps across the codebase. Vulnerability indicators light up:
  - SQL injection risk in a query builder
  - Unvalidated user input in a form handler
  - Outdated dependency with known CVE
- Each finding has a severity badge (P0/P1/P2).

**Layer 4 — Vulnerability Orchestration (purple):**
- Dedicated orchestrator aggregates findings from layers 1–3.
- Prioritizes by risk. Generates a remediation plan.
- Auto-fixes where safe. Flags for human review where not.

**Layer 5 — Release Gate (green, outermost):**
- Final checkpoint before deployment.
- Aggregated security score. Must meet minimum threshold.
- If threshold not met: release blocked with detailed findings.

**SDLC timeline** along the bottom shows when each layer fires:
- Coding → Layer 1
- Commit → Layer 2
- Analysis → Layer 3
- Planning → Layer 4
- Deploy → Layer 5

**Narration:** "Security isn't a final check. It's five layers, embedded in every stage. Shift-left isn't a buzzword — it's the architecture."

**Narration (on the SDLC timeline):** "Watch where Layer 1 sits on that timeline. It fires while you're still coding. Not at code review. Not at deploy. While you're coding. That's the shift."

### Scene 5 — Together: Quality + Safety (6:30 – 7:30)

**Split the screen:**

- **Left:** Golden test pyramid (quality)
- **Right:** Security concentric rings (safety)
- **Center bridge:** They share the same governance engine, the same audit trail, the same enforcement pipeline.

**Animation:** A code change enters. It passes through golden test validation (left) AND security scan (right) simultaneously. Both must pass for the change to proceed.

**Key insight card:** *"Quality without security is fragile. Security without quality is theater. Together, they're engineering discipline."*

**Narration:** "They share the same enforcement engine. The same audit trail. The same governance rules. That unification is intentional — it's what prevents 'security team' and 'engineering team' from working at cross-purposes."

### Scene 6 — Closing (7:30 – 8:00)

**Three principles:**

1. **Earned, Not Assigned** — "Golden status is scored, not hand-picked"
2. **Shift-Left** — "Security checks embedded from first keystroke to deployment"
3. **Auditable** — "Every test, every scan, every finding — permanently logged"

**Closing text:** **"Correct and secure. Scored and verified. Every change."**

**Narration:** "Both of those words — correct and secure — require proof. Not confidence. Not hope. CORTEX makes that proof automatic."

---

## Notes
- This video merges golden tests + security (previously separate topics) — unified by the theme of "verified trust"
- The audit trace visualization (Scene 3) is the standout scene — makes CORTEX's test infrastructure tangible
- **No hardcoded counts** for rules or layers — described by function
- Security layers are realistic and match actual CORTEX capabilities — no exaggeration
