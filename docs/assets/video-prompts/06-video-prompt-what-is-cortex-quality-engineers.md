# Video Prompt 06 — What Is CORTEX? (Quality Engineers)

---
**Series:** CORTEX — The Governed AI Engineering Partner
**Video:** 06 of 07 (Role Series)
**Title:** What Is CORTEX? For Quality Engineers
**Subtitle:** Enforced TDD, Five-Dimension Test Scoring, Golden Test Contract, and Codebase Health Trending
**Audience:** QA engineers, test engineers, SDET practitioners, quality leads, test architects
**Duration:** 7–10 minutes
**Narrator:** 🎙️ Male (VBP-017 — even-numbered video)
**Generator:** Google Gemini Video Generator / NotebookLM Video Editor
**Last Updated:** 2026-03-08
**VBP Rules Applied:** VBP-001 through VBP-019 (full compliance)
**Content Sources:** `01-platform`, `03-governance`, `04-tdd-quality-flywheel`, `05-orchestration`, `09-lifecycle`
**Series Context:** Video 01 introduced the CORTEX platform and its three mission pillars. This video does NOT repeat that introduction — it goes deep on quality-specific capabilities: how TDD is enforced structurally (not by convention), how every test is scored across five dimensions, how the Golden Test contract prevents regressions, and how sweep completeness eliminates partial fixes. **Note: The sweep completeness visual in this video shows test-file pattern scanning — NOT AC-to-code traceability (that is Video 03's domain).**

---

## 🎯 Learning Objective

Quality engineers understand that CORTEX enforces test-driven development structurally at every commit, scores test quality across five dimensions so that only meaningful tests count, maintains a Golden Test contract where critical behaviours can never regress, eliminates partial fixes through sweep completeness at the test-pattern level, and trends codebase health across five quality dimensions with per-sprint sparklines.

---

## 🎬 MANDATORY Hero Intro Slide (VBP-014 — 5 seconds)

**Scene:** Full-screen `#0a0e27` deep space navy. Floating green (`#00ff88`) and cyan particles — quality signal aesthetic.

**Centre frame:**
- `cortex-logo-512.png` — large, hero-scale, pulsing cyan glow
- **Above logo:** "What Is CORTEX?" — Space Grotesk Bold, `#ffffff`, 48px
- **Below logo:** "For Quality Engineers — Quality That Enforces Itself" — Inter Regular, `#a0a6c0`, 20px, typewriter reveal

**Hold 5 seconds → logo to watermark → Scene 1 fades in.**

---

## Scene 1 — The Hook: The "Test Later" Trap (0:05 – 0:40)

**Visual (VBP-006 — pain before solution):**

Three sprint boards animated in sequence:

**Sprint 1:** `DONE` card with sticky note: `"Tests will be added next sprint."` — italic, `#a0a6c0`.
**Sprint 2:** Same card. Same sticky note. Now yellowed.
**Sprint 3:** Card relabelled: `"Technical debt — no tests."` — `#ff4444`.
**Post-sprint:** A final card: `"Production incident. No test caught the regression."` — red border, `#ff4444`.

Below: a test coverage gauge shows 0% for the untested module, while the rest of the codebase shows 84%.

**Narration:**
> "Every engineering team intends to write tests. Most teams accumulate quality debt because 'we'll add tests later' becomes 'we never had time.' And the tests that never get written are precisely the tests for the most critical behaviours — the ones developers were confident about and didn't think needed verification. CORTEX eliminates this pattern structurally. You cannot proceed without the test. There is no sprint in which 'later' is valid."

**VBP-002:** Hook at 0:07.
**VBP-011:** 2s silence after "no test caught the regression" card.

---

## Scene 2 — Enforced TDD: The Three-Phase Cycle (0:40 – 1:20)

**Visual:**
A circular three-phase TDD flywheel, green (`#00ff88`) dominant. Two gate states:

```
CORTEX TDD Enforcement Gate — OPEN
────────────────────────────────────
✅ Test exists:                     YES
✅ Test fails before implementation: YES
✅ Gate:                            OPEN → proceed
```

```
CORTEX TDD Enforcement Gate — CLOSED
──────────────────────────────────────
❌ Test passes before implementation
❌ Flagged: VACUOUS TEST — tests nothing meaningful
❌ Gate: CLOSED → test must be rewritten before proceeding
```

JetBrains Mono code block (dark panel):
```python
def test_checkout_calculates_tax_correctly():
    # RED phase — MUST fail before implementation
    cart = Cart(items=[Item(price=100.0, qty=2)])
    result = cart.calculate_tax(rate=0.20)
    assert result == 40.0  # fails ✅ — gate open
```

**Breadcrumb (VBP-015, bottom):** `[🔴 RED] → [🟢 GREEN] → [♻️ REFACTOR]` — current phase highlighted green.

**Narration:**
> "CORTEX enforces the three-phase TDD cycle on every change — every feature, every bug fix, every refactoring. The system checks for a failing test before implementation proceeds. A test that passes before any implementation exists is flagged as vacuous: it is testing nothing that isn't already true. It must be rewritten. There is no bypass flag. There is no 'we'll add tests next sprint.' The gate is the gate."

**VBP-016:** Bold: **"vacuous"**, **"no bypass flag"**, **"gate is the gate"** in `#ff4444` and `#00ff88`.

---

## Scene 3 — Test Quality Scoring: Five Dimensions (1:20 – 2:00)

**Visual:**
Two side-by-side radar/pentagon charts animating simultaneously.

**Chart A — High-value test (score: 76/100):**

| Dimension | Score | Colour |
|-----------|-------|--------|
| Impact | 8/10 — protects checkout critical path | `#ff4444` red |
| Likelihood | 7/10 — tax calculation is high-change | `#ffa500` orange |
| Detection | 9/10 — assert on precise output | `#00ff88` green |
| Efficiency | 6/10 — focused, minimal setup | `#3b82f6` blue |
| Maintenance | 8/10 — uses domain constants | `#7b61ff` purple |

Badge: `76/100 — P1 HIGH VALUE` — `#00d4ff` Space Grotesk Bold.

**Chart B — Low-value test (score: 14/100):**

| Dimension | Score |
|-----------|-------|
| Impact | 1/10 — tests a constant |
| Likelihood | 1/10 — cannot fail |
| Detection | 2/10 — no meaningful assertion |
| Efficiency | 5/10 |
| Maintenance | 3/10 — brittle to rename |

Badge: `14/100 — P3 CANDIDATE FOR REMOVAL` — `#ff4444`.

**Narration:**
> "Not all tests provide equal confidence. CORTEX scores every test across five dimensions: Impact — does this test protect a critical behaviour? Likelihood — is this a realistic failure scenario? Detection — does the assertion verify the right output? Efficiency — is the test focused and maintainable? Maintenance — will this test remain valid as the codebase evolves? A test scoring below the threshold for its domain is flagged for improvement or removal. A low-quality test does not provide safety — it provides false confidence. CORTEX does not let false confidence count."

**VBP-009 (Signaling):** Each radar axis highlights as narrated.

---

## Scene 4 — Golden Tests: The Behaviours That Must Never Break (2:00 – 2:45)

**Visual:**
A test suite grid — most nodes are neutral `#a0a6c0`. A curated subset glows gold (`#fbbf24`). The Golden Test promotion lifecycle animates:

```
Test suite (general)
  test_checkout_tax  ──[score: 76, P1]──→ Promoted to Golden ✨
  test_cart_add_item ──[score: 82, P1]──→ Promoted to Golden ✨
  test_auth_middleware──[score: 91, P1]──→ Promoted to Golden ✨
```

Golden Test contract card (glassmorphism, gold border):
```
Golden Test Contract — CORTEX
──────────────────────────────
Coverage:  Critical end-to-end flows
           Governance gate enforcement
           Integration seams (database, API, auth)
           Core workflow executions

Contract:  Must always pass. Zero exceptions.
           Golden test failure = production-blocking event.

Status:    ✅ 847 green | ❌ 0 failed
```

A simulation: one golden node turns red. An immediate block card:
```
🚨 PRODUCTION BLOCK — Golden test regression
   test_checkout_calculates_tax_correctly — FAILED
   No deployment proceeds until resolved.
```

**Narration:**
> "CORTEX promotes tests from the general suite to the Golden set based on quality scores. These tests cover the critical behaviours that, if they regress, indicate something fundamental has broken. The contract is absolute: they must pass on every commit, every build, with zero regressions. A golden test failure stops everything — no deployment proceeds until the regression is resolved and understood. You cannot negotiate with golden tests."

**VBP-013 (Business Book):** Callout: *"Quality is never an accident; it is always the result of intelligent effort."* — John Ruskin. Dark pill.

---

## Scene 5 — Sweep Completeness: Every Test-Level Instance (2:45 – 3:25)

**Visual:**
**THIS IS THE TEST-FILE PATTERN SCAN — distinct from Video 03's AC traceability map.**

A test suite codebase grid. One test file glows red: `tests/api/test_auth.py`.

CORTEX identifies a missing assertion pattern across test files:

```
Sweep Catalogue — Test Pattern Audit
──────────────────────────────────────────
Issue: Missing status code assertion in API tests
Pattern: Response created but status not asserted
Found in: 5 test files (CORE-064: all must be fixed)
  ├ tests/api/test_auth.py           ○ OPEN
  ├ tests/api/test_users.py          ○ OPEN
  ├ tests/integration/test_flow.py   ○ OPEN
  ├ tests/unit/test_validators.py    ○ OPEN
  └ tests/e2e/test_checkout.py       ○ OPEN
```

Each item closes in sequence: `● CLOSED`. A new assertion added to each test file is shown briefly.

Final: `Sweep complete: 5/5 — Missing assertion pattern eliminated (CORE-064 ✅)`

**Narration:**
> "When CORTEX identifies a test quality issue, it does not fix the single test where it was first found. It scans the entire test suite for the same pattern — the same missing assertion, the same vacuous test, the same coverage gap — catalogues every instance, and closes every one. This is the Sweep Completeness Contract: CORE-064. A quality sweep that found five issues and fixed three is not complete. It is an audit with three known-open risks. CORTEX closes every item before marking the sweep complete."

**VBP-009 (Signaling):** Each file node in the grid pulses green as it is resolved.

---

## Scene 6 — Quality Analysis: Five-Dimension Codebase Health (3:25 – 4:05)

**Visual:**
A five-dimension quality dashboard (glassmorphism cards, green domain colour). Each dimension has a current score and a 12-sprint sparkline chart:

| Dimension | Score | Trend | Sparkline |
|-----------|-------|-------|-----------|
| Structural Complexity | 74/100 | ↑ improving | 12-sprint line rising |
| Test Coverage Adequacy | 88/100 | → stable | Flat high line |
| Documentation Completeness | 61/100 | ↑ improving | Line rising from 48 |
| Dependency Health | 92/100 | → stable | Flat high line |
| Governance Compliance | 96/100 | ↑ improving | Line rising from 84 |

**Composite score badge:** `82/100` — Space Grotesk Bold, 48px, `#00ff88`.

A priority signal: `"Structural Complexity (74) — improving but below threshold. 3 modules flagged for refactoring."` — amber pill.

**Narration:**
> "The Quality Analysis Engine evaluates codebase health across five dimensions — structural complexity, test coverage adequacy, documentation completeness, dependency health, and governance compliance — producing a composite score with per-dimension trend sparklines across 12 sprints. A quality finding in a declining-quality module receives higher remediation priority than the same finding in an improving one. Health is not a snapshot — it is a trajectory. CORTEX tracks both."

---

## Scene 7 — Test Failure Triage: The Debug Loop (4:05 – 4:45)

**Visual:**
A test failure triage card (glassmorphism, amber top-border):

```
Test Failure Analysis
──────────────────────────────────────────────────────
Failed:  test_checkout_calculates_tax_correctly
Error:   AssertionError: expected 40.0, got 38.5
LENS:    Tax rate rounding changed in utils/tax.py (line 47)
         Change introduced: Sprint 47, commit a3f9c2

Root Cause: Floating point precision — tax rounded at wrong stage
Pattern:    Seen before (Sprint 14) — prevention rule exists
Prevention: Apply rounding AFTER multiplication, not during

Fix plan:   1. Update rounding order in tax.py
            2. Add floating point precision test
            3. Re-run Golden Test suite
```

**Narration:**
> "When a test fails, CORTEX's debug pipeline analyses the failure with LENS context — surfacing the specific commit, the change that introduced the regression, and whether this failure pattern has been seen before. In this case, a floating-point precision issue was seen in Sprint 14 and a prevention rule was stored. The rule surfaces before the fix is written — pointing directly to the known solution. Test failures are learning events, not just red lights."

---

## Scene 8 — The QA Dashboard: Quality State at Sprint Boundary (4:45 – 5:25)

**Visual:**
A sprint-boundary QA dashboard (glassmorphism, green domain colour):

```
Sprint 47 — Quality Gate Dashboard
────────────────────────────────────────────────────────
TDD Compliance:      ✅ 100% — all new code TDD-verified
Golden Test Suite:   ✅ 847/847 passing — 0 regressions
Test Score (avg):    ✅ 72/100 — above domain threshold (65)
Sweep Status:        ✅ Complete — 5 patterns, 5/5 closed
Quality Score:       ✅ 82/100 — +4 points vs Sprint 46
Low-quality tests:   🟡 3 tests below threshold — flagged for review
Candidate removals:  🟡 2 tests P3 — acknowledgement required
```

**Narration:**
> "At sprint boundary, the CORTEX quality gate dashboard gives you a complete view of the codebase's quality state — not by asking developers to self-report, but by measuring it structurally. TDD compliance is verified at every commit. Golden tests are green or the sprint is not closed. Quality scores are calculated from actual test content, not coverage percentages. Sweep completeness is confirmed before sign-off. This is quality governance at the pace of delivery."

---

## Scene 9 — Vision: Quality as Infrastructure (5:25 – 5:55)

**Visual:**
Full-screen dark navy. A quote card — glassmorphism, green top-border:

> *"Testing can show the presence of bugs, but not their absence."*
> — Edsger W. Dijkstra

Below: a second card:

> **"CORTEX ensures tests are meaningful enough to make their presence count — scored, enforced, and contractually bound to never regress."**

**AUDIO: Strategic Silence — 2 seconds.**

**Narration:**
> "Dijkstra's observation remains true. But CORTEX maximises the signal in every test that exists — ensuring that what is tested is meaningful, what is asserted is correct, and what is golden can never be silently broken. Quality is not a discipline in CORTEX. It is infrastructure."

---

## Scene 10 — Call to Action (5:55 – 6:10)

**Visual:**
Single centred card, glassmorphism, green border:

> **"Enforced TDD. Five-dimension scoring. Golden Test contract. Sweep completeness. Codebase health trending."**

Below: `→ Explore the CORTEX quality flywheel for QA engineers` in `#00d4ff`.
Breadcrumb (bottom): `06/07 — Quality Engineers | 07 → Site Reliability Engineers →`

**Narration:**
> "CORTEX is built so quality is not a discipline that relies on individual engineers remembering to apply it. Quality enforces itself — through structural constraints, scoring, contracts, and completeness guarantees. Every test matters. Every instance gets fixed. Every regression is blocked."

---

## 🎬 Closing Title Card

`cortex-logo-512.png` hero-scale. Tagline: **"CORTEX — Cognitive Real-Time Execution"** — Inter, `#a0a6c0`.

---

## 🎨 Visual Identity Compliance Checklist

| Rule | Applied |
|------|---------|
| VBP-001 One Idea Per Frame | ✅ |
| VBP-002 Hook in 8 seconds | ✅ Sprint boards at 0:07 |
| VBP-003 Narration ≠ slide text | ✅ Narration interprets; slides show data |
| VBP-004 Progressive disclosure | ✅ Radar chart axes animate sequentially; sweep items close one-by-one |
| VBP-005 Z/F pattern | ✅ TDD flywheel centred; sweep catalogue left-to-right |
| VBP-006 Contrast storytelling | ✅ Low-quality test chart vs high-quality test chart Scene 3 |
| VBP-007 2-min visual cycles | ✅ New concept every scene |
| VBP-008 Title + duration + chapters | ✅ Intro slide + pipeline breadcrumbs |
| VBP-009 Signaling | ✅ Radar axes highlight; sweep nodes pulse green; gate states |
| VBP-010 Analogy | ✅ Sprint sticky note series — "later" never comes |
| VBP-011 Strategic silence | ✅ 2s after "no test caught the regression" Scene 1; 2s after Dijkstra quote Scene 9 |
| VBP-012 Consistent visual language | ✅ Green domain colour throughout |
| VBP-013 Business Book | ✅ Ruskin Scene 4; Dijkstra Scene 9 |
| VBP-014 Hero intro slide | ✅ `cortex-logo-512.png`, 5 seconds |
| VBP-015 Breadcrumb | ✅ TDD cycle Scene 2 |
| VBP-016 Bold key words | ✅ Green highlights on quality enforcement terms |
| VBP-017 Male narrator | ✅ Even-numbered video |
| VBP-018 No unexpanded acronyms | ✅ TDD, SDET, CORE-064, LENS, P0/P1/P3, AC, CDR all expanded |
| VBP-019 Strategic colour | ✅ Green (`#00ff88`) for Quality Engineer domain |

---

## 🎵 Audio Direction

- **Background:** Clean ambient electronic — precise, methodical rhythm. Quality-lab aesthetic.
- **Sprint board transitions (Scene 1):** Soft "paper" sound per board; final card: low alarm tone
- **TDD gate OPEN (Scene 2):** Clean ascending chime
- **TDD gate CLOSED (Scene 2):** Sharp low tone — rejection signal
- **Radar chart axes (Scene 3):** Smooth dial-turn sound as each axis fills
- **Golden test promotion (Scene 4):** Gold shimmer chime per promotion
- **Golden test block (Scene 4):** Alarm + deep thud — production-blocking severity
- **Sweep catalogue CLOSED items (Scene 5):** Satisfying click-tick per item — precision signal
- **Composite quality score reveal (Scene 6):** Resonant chime — significant reveal
- **Dijkstra quote silence (Scene 9):** Absolute silence — 2 full seconds, no music, no FX
- **Narration style:** Methodical, precise, evidence-focused. 140 wpm. Calibrated for QA engineers who trust data over claims.


**Visual (VBP-006 — pain before solution):**

A sprint board visualisation. Cards flow left to right: `[TO DO] → [IN PROGRESS] → [DONE] → [BLOCKED]`.

A sticky note on a DONE card: `"Tests will be added next sprint."` — `#a0a6c0`, italic.
Next sprint board — same card, same sticky note.
Third sprint board — card now labelled: `"Technical debt — no tests."` — `#ff4444`.

A final card appears: `"Bug found in production. No tests caught it."` — red border, `#ff4444`.

**Narration:**
> "Every engineering team intends to write tests. Most teams accumulate technical debt because 'we'll add tests later' becomes 'we never got around to it.' The tests that never get written are precisely the tests for the most important behaviours — the ones developers were confident about and didn't think needed verification. CORTEX eliminates this pattern structurally."

**VBP-002:** Hook at 0:07.
**VBP-011:** 1.5s silence after "no tests caught it" card.

---

## Scene 2 — Enforced TDD: The Three-Phase Cycle (0:28 – 1:05)

**Visual:**
A circular three-phase TDD flywheel, green (`#00ff88`) dominant. Tokens travel the track:

```
        🔴 RED
   Write a failing test
       (required)
           ↓
🟢 GREEN              ♻️ REFACTOR
Minimum code to       Improve without
make test pass        breaking anything
```

**Enforcement gate animation:** Before GREEN, a gate icon appears. Text:
```
CORTEX Enforcement Gate
────────────────────────
✅ Test exists: YES
✅ Test fails before implementation: YES
✅ TDD gate: OPEN
```

If the test passes before implementation, an alternate gate fires:
```
❌ Test passes before implementation: NO
❌ Flagged as vacuous test — must rewrite
❌ TDD gate: CLOSED
```

Red border, red glow on gate card.

**Breadcrumb (VBP-015, bottom):** `[🔴 RED] → [🟢 GREEN] → [♻️ REFACTOR]` — current phase highlighted green.

**Narration:**
> "CORTEX enforces the three-phase test-driven cycle on every change. Every new feature. Every bug fix. No exceptions. The system verifies a failing test exists before allowing implementation to proceed. A test that passes before implementation is flagged as vacuous — it tests nothing meaningful — and must be rewritten. You cannot skip to green without earning it."

**VBP-016:** Bold: **"every change"**, **"no exceptions"**, **"vacuous"** in `#ff4444` and `#00ff88`.

---

## Scene 3 — Test Quality Scoring: Five Dimensions (1:05 – 1:40)

**Visual:**
A radar/pentagon chart — five axes, each a quality dimension. Values animate from 0 to their scored level:

| Dimension | Score (example test) | Colour |
|-----------|---------------------|--------|
| Impact | 8/10 | `#ff4444` red |
| Likelihood | 7/10 | `#ffa500` orange |
| Detection | 9/10 | `#00ff88` green |
| Efficiency | 6/10 | `#3b82f6` blue |
| Maintenance | 8/10 | `#7b61ff` purple |

Overall score badge: `76/100 — P1 HIGH VALUE` — Space Grotesk Bold, `#00d4ff`.

A second chart animates beside it — a low-quality test (score: 18/100, P3 — `"Candidate for removal"`).

Caption: **"Not all tests are equal. CORTEX scores every one."** — dark pill.

**Narration:**
> "Writing a test is easy. Writing a meaningful test is harder. CORTEX scores every test across five dimensions: impact — does this protect a critical behaviour? Likelihood — is this a realistic failure path? Detection — does this verify the right output? Efficiency — is this test concise? Maintenance — will this test stay relevant? Tests scoring below the threshold for their domain are flagged for improvement or removal. A low-quality test provides false confidence — CORTEX doesn't let it count."

**VBP-009 (Signaling):** Each axis on the radar chart highlights as narrated.

---

## Scene 4 — Golden Tests: The Behaviours That Must Never Break (1:40 – 2:10)

**Visual:**
A test suite visualisation — a grid of test nodes. Most are neutral `#a0a6c0`. A subset glows gold (`#fbbf24`) — the Golden Tests:

Overlaid card (glassmorphism, gold border):
```
Golden Test Contract
─────────────────────
Coverage: Critical end-to-end flows
          Governance gate enforcement
          Integration seams
          Core workflow executions

Contract: Must always pass. Zero regressions.
          Golden test failure = production-blocking issue.
Status: ✅ 847 green  ❌ 0 failed
```

A golden test fails (simulation): one node turns red. An immediate block card:
```
🚨 PRODUCTION BLOCK — Golden test regression detected
   test_governance_gate_enforces_tdd_sequence — FAILED
   Action required before any deployment proceeds
```

**Narration:**
> "CORTEX maintains a curated set of Golden Tests — promoted from the general suite based on quality scores. These tests cover critical end-to-end flows, governance gate enforcement, integration seams, and core workflows. The contract is absolute: they must always pass, on every commit, in every build, with zero regressions. A golden test failure is a production-blocking issue — it stops everything until resolved. You don't negotiate with golden tests."

**VBP-013 (Business Book):** Callout: *"Quality is never an accident; it is always the result of intelligent effort."* — John Ruskin. Dark pill.

---

## Scene 5 — Sweep Completeness: Fix All Instances, Not One (2:10 – 2:40)

**Visual:**
A codebase grid (same format as Security video Scene 3, green domain colour). One file glows red: `tests/api/test_auth.py`.

CORTEX sweep catalogue opens:
```
Sweep Catalogue — Open
──────────────────────
Issue: Missing assertion on status code
Found: 5 test files
  ├ tests/api/test_auth.py           ○ OPEN
  ├ tests/api/test_users.py          ○ OPEN
  ├ tests/integration/test_flow.py   ○ OPEN
  ├ tests/unit/test_validators.py    ○ OPEN
  └ tests/e2e/test_checkout.py       ○ OPEN
```

Each item closes green in sequence: `● CLOSED`.

Final: `Issues resolved: 5/5 — Sweep Complete ✅ (CORE-064: Sweep Completeness Contract)`

**Narration:**
> "When CORTEX identifies a quality issue in one test, it does not fix just that test. It scans the entire codebase for the same pattern — the same missing assertion, the same vacuous test, the same coverage gap — catalogues every instance, and closes every one. The Sweep Completeness Contract — CORE-064 — guarantees this. An audit that found five instances and fixed three is not an audit. It is a partial fix with a known-open risk. CORTEX doesn't ship partial fixes."

**VBP-009 (Signaling):** Each catalogue item node in the grid pulses green as it closes.

---

## Scene 6 — Quality Analysis Engine: Codebase Health Score (2:40 – 3:10)

**Visual:**
A five-dimension quality dashboard (glassmorphism cards, green domain colour):

| Dimension | Score | Trend |
|-----------|-------|-------|
| Structural Complexity | 74/100 | ↑ improving |
| Test Coverage Adequacy | 88/100 | → stable |
| Documentation Completeness | 61/100 | ↑ improving |
| Dependency Health | 92/100 | → stable |
| Governance Compliance | 96/100 | ↑ improving |

**Composite score:** `82/100` — large badge, Space Grotesk Bold 48px, `#00ff88`.

Trend sparkline charts per dimension animate right-to-left (past 12 sprints).

**Narration:**
> "The Quality Analysis Engine evaluates codebase health across five dimensions — structural complexity, test coverage adequacy, documentation completeness, dependency health, and governance compliance — producing a composite score from zero to 100 with per-dimension breakdowns and trend tracking. A quality finding in a declining-quality module receives higher priority than the same finding in an improving one. Quality is measured, trended, and surfaced — not just asserted."

---

## Scene 7 — Call to Action (3:10 – 3:25)

**Visual:**
Single centred card, glassmorphism, green border:

> **"Enforced TDD. Test quality scoring. Golden Test contract. Sweep completeness. Codebase health trending."**

Below: `→ Explore the CORTEX quality flywheel` in `#00d4ff`.
Breadcrumb (bottom): `06/07 — Quality Engineers | 07 → Site Reliability Engineers →`

**Narration:**
> "CORTEX is designed so quality is not a discipline that relies on individual engineers remembering to apply it. Quality enforces itself — through structural constraints, scoring, contracts, and completeness guarantees. Every test matters. Every instance gets fixed. Every regression is blocked."

---

## 🎬 Closing Title Card (3:25 – 3:30)

CORTEX logo hero-scale. Tagline: **"CORTEX — Cognitive Real-Time Execution"** — Inter, `#a0a6c0`.

---

## 🎨 Visual Identity Compliance Checklist

| Rule | Applied |
|------|---------|
| VBP-001 One Idea Per Frame | ✅ |
| VBP-002 Hook in 8 seconds | ✅ Sprint boards at 0:07 |
| VBP-003 Narration ≠ slide text | ✅ |
| VBP-004 Progressive disclosure | ✅ Radar chart axes animate sequentially |
| VBP-005 Z/F pattern | ✅ TDD flywheel centred; sweep catalogue left-to-right |
| VBP-006 Contrast storytelling | ✅ "Test later" trap → enforced TDD |
| VBP-007 2-min visual cycles | ✅ |
| VBP-008 Title + duration + chapters | ✅ |
| VBP-009 Signaling | ✅ Radar axes, sweep nodes, gate status |
| VBP-010 Analogy | ✅ Scientific experiment analogy for TDD (Red=hypothesis) |
| VBP-011 Strategic silence | ✅ 1.5s after "no tests caught it" |
| VBP-012 Consistent visual language | ✅ Green domain colour throughout |
| VBP-013 Business Book | ✅ Ruskin quality quote Scene 4 |
| VBP-014 Hero intro slide | ✅ |
| VBP-015 Breadcrumb | ✅ TDD cycle Scene 2 |
| VBP-016 Bold key words | ✅ |
| VBP-017 Male narrator | ✅ Even-numbered video |
| VBP-018 No unexpanded acronyms | ✅ TDD, SDET, CORE-064 expanded |
| VBP-019 Strategic colour | ✅ Green (`#00ff88`) for Quality Engineer domain |

---

## 🎵 Audio Direction

- **Background:** Clean ambient electronic — precise, methodical rhythm. Quality-lab aesthetic.
- **Sprint board sticky notes (Scene 1):** Soft "paper tear" sound per sprint board transition
- **TDD gate OPEN (Scene 2):** Clean ascending chime — gate pass
- **TDD gate CLOSED (Scene 2):** Sharp low tone — rejection signal
- **Radar chart animation (Scene 3):** Smooth dial-turn sound as each axis fills
- **Sweep catalogue close (Scene 5):** Satisfying click-tick per item — precision signal
- **Quality composite score reveal (Scene 6):** Resonant chime — significant reveal moment
- **Narration style:** Methodical, precise, evidence-focused. 140 wpm. Calibrated for QA engineers who trust data over claims.
