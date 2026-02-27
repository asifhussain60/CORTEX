# Video Prompt 03 — Precision Reviews

> **Series:** CORTEX: The Enterprise Intelligence Series (Video 03 of 10)
> **Duration:** 8 minutes · **Audience:** Software Engineers, Security Engineers, Tech Leads
> **Depth:** 🟡→🔴 Starts conceptual, ends with engineering detail — bridging product owners and developers
> **Core Executive Theme:** Visualizing intelligent automated reviews — policy enforcement, vulnerability detection, remediation guidance, and scored quality gates
> **No overlap:** Image prompt-06 (golden test pyramid) is a static quality gate snapshot; image prompt-07 (security layers) is a static concentric ring. This video shows golden tests **promoting and demoting** in real-time, security checks **firing at each SDLC stage**, and intelligent code reviews **catching and fixing issues automatically**

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> See `README.md` for full mandatory palette, motion style, text contrast rules, typography, and watermark.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the slide.** Every narration line must add something the viewer cannot get from reading the screen: the *why*, the *consequence*, the *non-obvious implication*, or the *emotional truth*. If a narration line restates visible text, cut it or rewrite it. See `README.md` §Narration Philosophy for full guidance and examples.

## ⚠️ VIDEO DESIGN BEST PRACTICES — MANDATORY

> **VBP-001:** One idea per frame — golden test pyramid and security layers are SEPARATE scenes, never overlaid.
> **VBP-004:** Progressive disclosure — pyramid builds base→apex; security layers build inner→outer.
> **VBP-006:** Contrast-based storytelling — "80% coverage" vs "golden test validated" distinction.
> **VBP-007:** Scene transitions every ~90-120 seconds to maintain attention.
> **VBP-009:** Data visualizations animated incrementally — quality gate dimensions pulse one at a time.
> **VBP-011:** Strategic silence when golden test audit trace completes (AC_COMPLETE ✅ moment).
> See `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` for the full codified reference.

## ⚠️ HERO INTRO SLIDE — MANDATORY (VBP-014)

> **Scene 0 — Title Card (0:00 – 0:05):** Full-screen `#0a0e27` deep navy background. CORTEX logo (`cortex-docs/assets/images/cortex-logo-200.png`) displayed as a **large central hero image** with a subtle **gold (#FFD700) glow pulse** (not cyan — gold is this video's accent). Above the logo: **"Precision Reviews"** in Space Grotesk Bold, white. Below the logo: **"Intelligent Review Automation. Vulnerability Detection. Scored Quality."** in Inter, `#a0a6c0`. Hold 5 seconds. Transition: logo shrinks to watermark position as Scene 1 fades in.

## ⚠️ BREADCRUMB NAVIGATION — MANDATORY (VBP-015)

> **Scene 2 (Golden Test Pyramid) presents 3 tiers sequentially.** Display a breadcrumb:
> `Base (Standard) → Middle (Promoted) → Apex (Golden)`
> - Current tier: Full brightness, tier-specific color (gray → amber → **gold**)
> - Completed tiers: ✅ checkmark, dimmed
>
> **Scene 4 (Five Security Layers) presents 5 concentric layers.** Display a persistent breadcrumb:
> `Layer 1: Pre-Commit → Layer 2: Governance → Layer 3: LENS Scan → Layer 4: Vulnerability Orchestration → Layer 5: Release Gate`
> - **Current layer:** Full brightness, bold, layer-specific color (red → amber → cyan → purple → green)
> - **Completed layers:** ✅ checkmark, dimmed to 60% opacity
> - **Upcoming layers:** Muted outlines at 30% opacity

## ⚠️ TYPOGRAPHY, COLOR & VOICE — MANDATORY (VBP-016, VBP-017, VBP-018, VBP-019)

> **Bold Key Words:** On every text card, **bold the 1–3 most important words**. Use **gold (#FFD700)** for golden test terminology and cyan for general highlights.
> **🏆 GOLD COLOR INTELLIGENCE — THIS IS THE PRIMARY GOLD VIDEO:**
> - **Gold (#FFD700)** is the dominant accent for ALL golden test elements: gold glass panels, gold glow on pyramid apex, golden particle effects for promoted tests, gold shimmer on the "Golden" label
> - Golden test pyramid edges: gold (#FFD700), not cyan
> - Quality gate dimensions: Gold radial indicators
> - Promotion animation: Standard (gray) → Promoted (amber) → **Golden (bright gold #FFD700 with glow)**
> - Demotion animation: Gold dims to gray — visual loss of golden status
> - The gold/gray contrast is the visual metaphor: earned vs lost trust
> **Standard Colors:** Red for violations/Layer 1, amber for Layer 2, cyan for LENS/Layer 3, purple for orchestration/Layer 4, green for release gate/Layer 5.
> **Voice:** 🎙️ **Female narrator** (odd-numbered video). Confident, conversational, honest tone.
> **Acronym Expansion (first use in this video):**
> - CORTEX = **CO**gnitive **R**eal-**T**ime **EX**ecution (Scene 1)
> - TDD = **T**est-**D**riven **D**evelopment (Scene 2 context)
> - SDLC = **S**oftware **D**evelopment **L**ife**c**ycle (Scene 4 timeline)
> - CVE = **C**ommon **V**ulnerabilities and **E**xposures (Scene 4, Layer 3)
> - AC = **A**udit **C**ompletion markers (Scene 3, trace visualization)
> - LENS = **L**anguage → **E**xamination → **N**avigation → **S**ynthesis (Scene 4, Layer 3)
> - CSP = **C**ontent **S**ecurity **P**olicy (if referenced)

---

## PROMPT

Create an 8-minute animated explainer video titled **"Precision Reviews — Intelligent Review Automation, Vulnerability Detection, and Scored Quality"**. This video visualizes how CORTEX transforms code review from a manual bottleneck into an automated, intelligent process — with policy enforcement, risk detection, remediation guidance, and scored golden tests.

### Scene 1 — Beyond "Tests Pass": The Review Problem (0:00 – 1:15)

**Open on:** A glassmorphic test results panel. Green bar: "247 tests passed." Developer smiles.

But wait — zoom into the results:
- 30% test one trivial getter
- 15% are duplicates with slight variations
- Coverage metric says 80% — but critical error paths are untested
- No test validates the complete end-to-end audit trail
- **No automated review** caught the SQL injection in line 47

**A second panel slides in:** A code review queue. Three PR (Pull Request) reviews pending — each waiting 2+ days for a human reviewer. A red notification: "Reviewer on vacation. No backup assigned."

**Narration:** "80% coverage sounds like rigor. But coverage measures which lines were touched — not whether the important things were actually validated. And that manual code review queue? It's the bottleneck nobody budgets for."

### Scene 2 — Golden Test Architecture (1:15 – 3:15)

**A pyramid materializes** — three tiers, glass with **golden (#FFD700) edges**:

- **Base — Standard Tests:** Wide foundation. Regular unit tests. Gray glass.
- **Middle — Promoted Tests:** Tests that have consistently passed, cover critical paths, and demonstrate architectural contracts. **Amber glass**. Fewer in number.
- **Apex — Golden Tests:** The essential tests. If these break, the system is fundamentally wrong. **Gold (#FFD700) glass with a radiant glow**. A curated, small set.

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
  - Outdated dependency with known CVE (Common Vulnerabilities and Exposures)
- Each finding has a severity badge (P0/P1/P2).

**Layer 4 — Vulnerability Orchestration (purple):**
- Dedicated orchestrator aggregates findings from layers 1–3.
- Prioritizes by risk. Generates a remediation plan.
- Auto-fixes where safe. Flags for human review where not.

**Layer 5 — Release Gate (green, outermost):**
- Final checkpoint before deployment.
- Aggregated security score. Must meet minimum threshold.
- If threshold not met: release blocked with detailed findings.

**Software Development Lifecycle (SDLC) timeline** along the bottom shows when each layer fires:
- Coding → Layer 1
- Commit → Layer 2
- Analysis → Layer 3
- Planning → Layer 4
- Deploy → Layer 5

**Narration:** "Security isn't a final check. It's five layers, embedded in every stage. Shift-left isn't a buzzword — it's the architecture."

**Narration (on the SDLC timeline):** "Watch where Layer 1 sits on that timeline. It fires while you're still coding. Not at code review. Not at deploy. While you're coding. That's the shift."

### Scene 5 — Intelligent Code Review: The Precision Engine (6:30 – 7:30)

**This is what makes CORTEX reviews "precision" — not just detection, but remediation.**

**Split the screen:**

- **Left:** Golden test pyramid (scored quality) — tests that PROVE correctness
- **Right:** Security concentric rings (risk detection) — layers that PREVENT vulnerabilities
- **Center bridge: The Precision Review Pipeline** — They share the same governance engine, the same audit trail, the same enforcement pipeline.

**The Precision Review Pipeline animates as a 4-step flow:**

1. **Standards Enforcement** — Every code change checked against governance rules (naming, types, docstrings, secure patterns)
2. **Risk Detection** — LENS scan identifies vulnerabilities, anti-patterns, and architectural violations
3. **Remediation Guidance** — Not just "violation found" — CORTEX shows the exact fix with a code diff preview
4. **Review Transparency** — Full review history logged: what was flagged, what was fixed, who approved, when

**Animation:** A code change enters. It passes through golden test validation (left) AND security scan (right) AND automated review (center) simultaneously. All three must pass for the change to proceed. A remediation card appears for a flagged issue — showing the problem AND the suggested fix side by side.

**Key insight card:** *"Quality without security is **fragile**. Security without review is **theater**. Precision reviews combine all three — scored, scanned, and remediated."*

**Narration:** "They share the same enforcement engine. The same audit trail. The same governance rules. That unification is intentional — it's what prevents 'security team,' 'review team,' and 'engineering team' from working at cross-purposes. And the remediation guidance means developers fix issues in seconds, not hours."

### Scene 6 — Closing (7:30 – 8:00)

**Three principles:**

1. **Earned, Not Assigned** — "**Golden** status is scored, not hand-picked"
2. **Shift-Left** — "**Security** checks embedded from first keystroke to deployment"
3. **Review with Remediation** — "Every finding comes with a **fix**, not just a flag"

**Closing text:** **"Precision Reviews. Scored. Scanned. Remediated. Every change."**

**Narration:** "Precision means not just finding problems — but fixing them. Not just scoring quality — but proving it. CORTEX makes that proof automatic."

Series badge: **"CORTEX: The Enterprise Intelligence Series — Video 03 of 10"**

---

## Animated Diagram Flow Directives

### 📐 Mermaid Diagram Sources (bundle with this prompt in NotebookLM)

| Diagram File | Type | Scene Reference | Purpose |
|---|---|---|---|
| `03-d-golden-test-pyramid-and-security-layers.mmd` | Flowchart | Scenes 2 + 4 + 5 | Golden test promotion/demotion pyramid + five security layers + SDLC timeline + shared infrastructure |

> **Video Producer:** Import `03-d-golden-test-pyramid-and-security-layers.mmd` alongside this prompt in NotebookLM. This diagram contains FOUR sub-graphs that map to different scenes: (1) Golden Test Pyramid → Scene 2, (2) Quality Gate Dimensions → Scene 2 radial indicators, (3) Five Security Layers + SDLC Timeline → Scene 4, (4) Shared Infrastructure → Scene 5 bridge. Animate Part A first (pyramid promotion/demotion), then Part B (security rings), then Part C (unified view). The frontmatter `animation_notes` have frame-by-frame rendering instructions.

---

## Notes
- Reframed from "Golden Tests & Security" to "Precision Reviews" — emphasizes intelligent review automation, the enterprise value proposition
- Scene 5 (Precision Review Pipeline) is the NEW hero content: standards enforcement → risk detection → remediation guidance → review transparency
- The remediation guidance (showing the fix, not just the finding) is the key differentiator over static linting tools
- The audit trace visualization (Scene 3) makes CORTEX's test infrastructure tangible
- **No hardcoded counts** for rules or layers — described by function
- Security layers are realistic and match actual CORTEX capabilities — no exaggeration
