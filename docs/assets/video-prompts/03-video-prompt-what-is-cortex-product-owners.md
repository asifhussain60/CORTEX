# Video Prompt 03 — What Is CORTEX? (Product Owners)

---
**Series:** CORTEX — The Governed AI Engineering Partner
**Video:** 03 of 07 (Role Series)
**Title:** What Is CORTEX? For Product Owners
**Subtitle:** AC Traceability, Sweep Completeness, and Code-Backed Decision Intelligence
**Audience:** Product Owners, Business Analysts, Delivery Managers, Scrum Masters
**Duration:** 7–10 minutes
**Narrator:** 🎙️ Female (VBP-017 — odd-numbered video)
**Generator:** Google Gemini Video Generator / NotebookLM Video Editor
**Last Updated:** 2026-03-08
**VBP Rules Applied:** VBP-001 through VBP-019 (full compliance)
**Content Sources:** `01-platform`, `03-governance`, `04-tdd-quality-flywheel`, `05-orchestration`, `09-lifecycle`
**Series Context:** Video 01 introduced the CORTEX platform and its three mission pillars. This video does NOT repeat that introduction — it goes deep on PO-specific workflows: how acceptance criteria become verifiable tests, how every AC is traced end-to-end from intent to evidence, how partial fixes are eliminated structurally, and how CORTEX produces code-backed estimates before you commit to a sprint.

---

## 🎯 Learning Objective

Product Owners understand that CORTEX connects their intent directly to traceable, governed delivery — every acceptance criterion becomes a failing test before implementation, every AC is linked to the code that satisfies it, partial fixes are structurally impossible, and code-backed estimates replace SWAGs before sprint commitment.

---

## 🎬 MANDATORY Hero Intro Slide (VBP-014 — 5 seconds)

**Scene:** Full-screen `#0a0e27` deep space navy. Floating purple (`#7b61ff`) and cyan particles.

**Centre frame:**
- `cortex-logo-512.png` — large, hero-scale, pulsing cyan glow
- **Above logo:** "What Is CORTEX?" — Space Grotesk Bold, `#ffffff`, 48px
- **Below logo:** "For Product Owners — AC Traceability, Sweep Completeness, Decision Intelligence" — Inter Regular, `#a0a6c0`, 20px, typewriter reveal

**Hold 5 seconds → logo to watermark → Scene 1 fades in.**

---

## Scene 1 — The Hook: The Gap Between Intent and Delivery (0:05 – 0:40)

**Visual (VBP-006 — pain before solution):**

A Product Owner's acceptance criterion, displayed on a card (glassmorphism, `rgba(26,31,58,0.85)`):

```
AC-001: "The system must validate the user's email format before submission."
```

Below it, four painful outcomes animate in with red left-border:

```
❌  Developer missed the edge case — empty string passes validation
❌  Fix applied in one endpoint — same bug exists in three others
❌  Test written after the fact — covers the happy path only
❌  Sprint review: "It's done" — production incident two weeks later
```

**Narration:**
> "You write an acceptance criterion. The developer implements it. But does the implementation actually match your intent? Does it cover the edge cases? Is it tested deliberately — before the code, not after? And if the same issue exists elsewhere in the codebase, does the fix go everywhere? CORTEX is built to answer 'yes' to every one of these — structurally, not by convention."

**VBP-002:** Hook in first 8 seconds.
**VBP-011:** 2s silence after the four red outcomes.

---

## Scene 2 — AC to Test: Intent Made Verifiable (0:40 – 1:20)

**Visual:**
An animated flow from the AC card into a test:

```
AC-001
"The system must validate email format before submission."
              ↓
 CORTEX interprets the AC
              ↓
┌───────────────────────────────────────────────────────────┐
│  def test_email_validates_empty_string():                  │
│      # RED — must fail before implementation              │
│      result = validate_email("")                          │
│      assert result.is_valid == False                      │
│      assert result.error == "Email cannot be empty"       │
└───────────────────────────────────────────────────────────┘
CORTEX gate: ✅ Test fails — TDD gate open
```

A traceability link card appears (glassmorphism, purple border):
```
AC Traceability Map
────────────────────────────────────────
AC-001 → test_email_validates_empty_string
AC-001 → test_email_validates_invalid_format
AC-001 → test_email_validates_unicode_domain
Coverage: 3 tests | AC-001: ✅ Fully covered
```

**Narration:**
> "CORTEX translates your acceptance criteria into a set of failing tests — before implementation begins. Each test is linked back to the originating AC in a traceability map. When someone asks 'is this requirement verified?', the answer is not an opinion — it is the test results. AC-001 has three tests. All three pass. The requirement is satisfied. Not because a developer says so — because the tests prove it."

**VBP-016:** Bold: **"before implementation begins"**, **"traceability map"**, **"tests prove it"** in `#7b61ff`.

---

## Scene 3 — Sweep Completeness: Every Instance, Not Just the First (1:20 – 2:05)

**Visual:**
An AC-level codebase traceability map — a network of file nodes (circles) connected to AC cards.

**THIS IS DIFFERENT FROM THE QUALITY VIDEO.** This is an AC-to-code trace, not a test-file pattern scan.

```
AC-001 (Email Validation)
     │
     ├── auth/validate.py             ○ Implementation
     ├── api/user_endpoints.py        ○ Usage point 1
     ├── forms/registration.py        ○ Usage point 2
     └── utils/email_helpers.py       ○ Usage point 3
```

CORTEX sweep catalogue (AC-scoped):
```
Sweep Catalogue — AC-001 Coverage Audit
─────────────────────────────────────────
Touch points found:  4 files
  ├ auth/validate.py           ○ OPEN — fix required
  ├ api/user_endpoints.py      ○ OPEN — fix required
  ├ forms/registration.py      ○ OPEN — fix required
  └ utils/email_helpers.py     ○ OPEN — fix required
```

Each node turns `#00ff88` green: `● CLOSED`. Final: `AC-001: All 4 touch points resolved ✅`

**Narration:**
> "When an AC has multiple implementation touch points, CORTEX identifies every one. If a fix is required, it is applied everywhere the AC is implemented — not just the file where the bug was first found. This is the Sweep Completeness Contract — CORE-064 — and it is non-negotiable. A fix applied in one place while three others remain broken is not done. CORTEX closes every item before reporting the sweep as complete."

**VBP-009 (Signaling):** Each file node pulses purple then green as it is resolved.

---

## Scene 4 — DoR to DoD: The Governed Pipeline (2:05 – 2:50)

**Visual:**
A horizontal seven-stage pipeline (glassmorphism, purple top-border):

```
[Phase 0: Decision Support] → [Requirements] → [Design] → [TDD Implementation]
→ [Code Review] → [Security Assessment] → [Release Readiness ✅]
```

Each phase has a gate icon — a padlock that turns green when the phase passes. A PO-specific annotation appears at each gate:

- `Phase 0`: "CORTEX provides evidence-backed effort estimate"
- `Requirements`: "AC cards flow in — ambiguity flagged before any code written"
- `Design`: "Architecture decision validated against codebase patterns"
- `TDD Implementation`: "AC→test traceability verified at every commit"
- `Code Review`: "AC coverage checked — uncovered ACs block merge"
- `Security Assessment`: "Security surface of the AC's feature validated"
- `Release Readiness ✅`: "Governance certificate issued — AC→evidence trail complete"

**Narration:**
> "CORTEX structures delivery as a seven-phase pipeline — and at every phase, it knows which acceptance criteria are in scope. Requirements arrive with their ACs. Design decisions are traced back to the ACs they satisfy. Implementation is verified against AC coverage, not just code coverage. At release readiness, a governance certificate is generated that links every AC to the test that proves it, the commit that implemented it, and the review that validated it. This is not a documentation exercise. It is a structural guarantee."

**VBP-013 (Business Book):** Brief callout card: *"A requirement without a test is a wish, not a specification."* — Dan North, BDD principles.

---

## Scene 5 — Code-Backed SWAGs: Decision Intelligence Before Sprint Commitment (2:50 – 3:35)

**Visual:**
A Product Owner's conversation bubble: `"How long will this feature take?"`.

CORTEX responds with a structured Change Intelligence card (glassmorphism, purple border):

```
Change Intelligence Report — Sprint Planning Support
──────────────────────────────────────────────────────
Feature:              Email validation overhaul
Codebase analysis:    4 touch points identified
Files affected:       auth/ (2), api/ (1), utils/ (1)
Complexity score:     MODERATE — CDR 4.2
Test delta:           +3 new tests, 1 existing updated
Estimated effort:     3–5 days
Risk factors:         LOW — isolated utility layer, no shared state
Recommendation:       Standalone sprint item — no cross-team dependencies
Prior patterns:       No prior failure history for this module
```

Below: a confidence badge — `"Evidence-backed estimate (not a SWAG)"` — purple pill.

**Narration:**
> "Before you write 'three to five days' on a story card, CORTEX analyses the actual codebase. It identifies every file the change will touch, scores the complexity of those interactions, calculates the test delta — how many new tests are needed, and whether existing tests will need updating — and produces an effort estimate with the evidence to back it up. Not a SWAG. Not a developer's best guess. A code-backed assessment derived from the system as it exists today. When you commit to a sprint, you commit with data."

**VBP-010 (Analogy):** "Like a structural engineer surveying a building before renovation — you see what's behind the walls before you commit to the project scope." Dark pill.

---

## Scene 6 — Change Intelligence: Before and After Governance (3:35 – 4:15)

**Visual:**
A Change Intelligence diff view — two-panel comparison.

**Left — Before CORTEX (ungoverned sprint):**
```
Sprint 47 Commitment
─────────────────────
Feature: Email validation overhaul
Estimate: "Probably 3 days" (developer's guess)
Risk assessment: None
Dependency check: Not done
Test plan: "We'll add tests as we go"
Sprint outcome: 5 days, 3 production bugs, partial fix
```

**Right — With CORTEX:**
```
Sprint 47 Commitment
─────────────────────
Feature: Email validation overhaul
Estimate: 3–5 days (CDR score 4.2, 4 touch points)
Risk: LOW (isolated module, no shared state)
Dependencies: None (CORTEX confirms zero cross-team touch)
Test plan: 3 failing tests generated from ACs, pre-implementation
Sprint outcome: 4 days, 0 production incidents, full AC coverage
```

**Narration:**
> "The difference between a sprint commitment and a sprint guarantee is evidence. With CORTEX, every commitment is made with codebase data behind it. Estimates are code-backed. Dependencies are confirmed, not assumed. Test plans exist before implementation starts. And when the sprint closes, the release certificate documents that every AC was tested, every touch point was fixed, and every governance gate was passed. This is what governed delivery looks like from a Product Owner's perspective."

---

## Scene 7 — Institutional Memory: Your Requirements Don't Forget (4:15 – 4:55)

**Visual:**
A prevention rule card (glassmorphism, amber `#fbbf24` top-border):

```
⚠️ Prior pattern detected — Sprint Planning Signal
Pattern: Email validation changes historically introduce
         async boundary failures in the auth module
Confidence: 0.82
Last occurrence: Sprint 14
AC impact: AC-031 was partially satisfied — edge case missed
Prevention: Include async boundary test in AC acceptance criteria
Status: ADVISORY — surfaces before sprint commitment
```

Below: a timeline showing the learning loop — `Sprint 14 failure → RCA → Prevention Rule → Sprint 47 planning → Rule surfaces → Risk avoided`.

**Narration:**
> "CORTEX remembers. When a similar feature was built in Sprint 14, an async boundary failure caused a partial AC satisfaction — the happy path passed, but an edge case was missed in production. That root cause was analysed, a prevention rule was stored, and when Sprint 47 planning touches the same module, the pattern surfaces automatically. Your team's hard-won knowledge about this codebase persists across sprints, across developer turnover, and across the entire history of the project."

---

## Scene 8 — The PO Dashboard: Delivery Confidence at a Glance (4:55 – 5:35)

**Visual:**
A release readiness dashboard (glassmorphism, purple domain colour):

```
Sprint 47 — Release Dashboard
────────────────────────────────────────────────
Acceptance Criteria Status:
  AC-001  ✅  3 tests passing  |  traced  |  reviewed
  AC-002  ✅  2 tests passing  |  traced  |  reviewed
  AC-003  ✅  4 tests passing  |  traced  |  reviewed
  AC-004  🟡  1 test pending   |  traced  |  code review open
  AC-005  ✅  2 tests passing  |  traced  |  reviewed

Sweep Status:    ✅ Complete (0 open items)
Governance:      ✅ 60+ rules satisfied
Security:        ✅ 5 layers passed
Release cert:    🎖️ Ready to generate
```

**Narration:**
> "At sprint close, the CORTEX release dashboard shows you exactly what is ready and what is not — by acceptance criterion, not by task or story point. Four of five ACs are fully traced, tested, and reviewed. One is waiting for a code review to close. You know what is ready to release and what is not, before you enter the sprint review. No surprises. No 'it works on my machine.'"

---

## Scene 9 — Vision: The Delivery You've Always Intended (5:35 – 6:05)

**Visual:**
Full-screen dark navy. A quote card — glassmorphism, purple top-border:

> *"A goal without a plan is just a wish."*
> — Antoine de Saint-Exupéry

Below: a second card:

> **"An acceptance criterion without a test is a wish. CORTEX makes it a commitment."**

**AUDIO: Strategic Silence — 2 seconds.**

**Narration:**
> "CORTEX closes the gap between what you intend and what gets built. It doesn't improve a process — it changes the structure. Acceptance criteria become tests. Tests become evidence. Evidence becomes the governance certificate that proves your sprint delivered what you promised."

---

## Scene 10 — Call to Action (6:05 – 6:20)

**Visual:**
Single centred card, glassmorphism, purple border:

> **"Intent traced to code. Code traced to evidence. Evidence traced to confidence."**

Below: `→ Explore the full CORTEX delivery lifecycle for Product Owners` in `#00d4ff`.
Breadcrumb (bottom): `03/07 — Product Owners | 04 → Software Engineers →`

**Narration:**
> "CORTEX is the governed delivery partner that makes your acceptance criteria traceable, your estimates evidence-backed, and your releases verifiably complete."

---

## 🎬 Closing Title Card

`cortex-logo-512.png` hero-scale. Tagline: **"CORTEX — Cognitive Real-Time Execution"** — Inter, `#a0a6c0`.

---

## 🎨 Visual Identity Compliance Checklist

| Rule | Applied |
|------|---------|
| VBP-001 One Idea Per Frame | ✅ |
| VBP-002 Hook in 8 seconds | ✅ AC gap pain Scene 1, 0:07 |
| VBP-003 Narration ≠ slide text | ✅ Narration interprets; slides show data |
| VBP-004 Progressive disclosure | ✅ AC traceability map, pipeline gates animate sequentially |
| VBP-005 Z/F pattern | ✅ AC→test flow left-to-right; pipeline left-to-right |
| VBP-006 Contrast storytelling | ✅ Red outcomes Scene 1 → evidence green Scene 5 |
| VBP-007 2-min visual cycles | ✅ New concept every scene |
| VBP-008 Title + duration + chapters | ✅ Intro slide + pipeline breadcrumbs |
| VBP-009 Signaling | ✅ AC nodes pulse purple then green as resolved |
| VBP-010 Analogy | ✅ Structural engineer survey Scene 5; dark pill |
| VBP-011 Strategic silence | ✅ 2s after four red outcomes Scene 1; 2s after Saint-Exupéry quote Scene 9 |
| VBP-012 Consistent visual language | ✅ Purple domain colour throughout |
| VBP-013 Business Book | ✅ Dan North Scene 4; Antoine de Saint-Exupéry Scene 9 |
| VBP-014 Hero intro slide | ✅ `cortex-logo-512.png`, 5 seconds |
| VBP-015 Breadcrumb | ✅ DoR→DoD pipeline Scene 4; phase gates highlight purple |
| VBP-016 Bold key words | ✅ Purple highlights on key delivery terms |
| VBP-017 Female narrator | ✅ Odd-numbered video |
| VBP-018 No unexpanded acronyms | ✅ AC, DoR, DoD, CDR, SWAG, TDD, BDD, CORE-064 all expanded |
| VBP-019 Strategic colour | ✅ Purple (`#7b61ff`) for Product Owner domain |

---

## 🎵 Audio Direction

- **Background:** Purposeful ambient synth — measured, professional, slightly warm. Strategic rhythm (not dramatic).
- **Red outcome cards (Scene 1):** Subtle pulse per reveal — escalating tension signal
- **AC traceability map nodes (Scene 2):** Soft connecting tone per link animated
- **Sweep catalogue items (Scene 3):** Ascending chime per `● CLOSED` resolution
- **Pipeline gate opens (Scene 4):** Clean padlock-click sound per gate
- **Change Intelligence card (Scene 5):** Single structured reveal — no dramatic FX
- **Saint-Exupéry quote silence (Scene 9):** Absolute silence — 2 full seconds, no music, no FX
- **Narration style:** Thoughtful, purposeful, outcome-focused. 128 wpm — calibrated for delivery professionals. No engineering jargon. Every claim framed in delivery outcomes.


**Visual (VBP-006 — pain before solution):**

A Product Owner's acceptance criterion, displayed on a card (glassmorphism, `rgba(26,31,58,0.85)`):

```
AC-001: "The system must validate the user's email format before submission."
```

Below it, three painful outcomes animate in with red left-border:

```
❌  Developer missed the edge case — empty string passes validation
❌  Fix applied in one endpoint — same bug exists in three others
❌  Test written after the fact — covers the happy path only
```

**Narration:**
> "You write an acceptance criterion. The developer implements it. But does the implementation actually match what you meant? Does it cover the edge cases? Is it tested correctly — before the code, not after? And if the same issue exists elsewhere in the codebase, does the fix go everywhere? CORTEX is designed to answer 'yes' to all of these — automatically."

**VBP-002:** Hook in first 8 seconds.
**VBP-011:** 1.5s silence after the three red outcomes.

---

## Scene 2 — Requirements to Tests: The Red-Green-Refactor Cycle (0:28 – 1:05)

**Visual:**
A three-phase cycle diagram, circular, glassmorphism, with a purple accent (`#7b61ff`):

```
        🔴 RED
   Write a failing test
    (from your AC)
        ↓
🟢 GREEN              ♻️ REFACTOR
Minimum code          Improve without
to pass the test      breaking anything
```

The AC card from Scene 1 flows into the RED phase as an arrow. The failing test appears in a JetBrains Mono card: `"test_email_validates_empty_string — FAIL"`. Arrows animate each transition.

**Breadcrumb bar (VBP-015, bottom):** `[🔴 RED] → [🟢 GREEN] → [♻️ REFACTOR]` — current phase highlighted purple.

**Narration:**
> "CORTEX enforces test-driven development on every change. Your acceptance criterion becomes a failing test — written before a single line of implementation. The developer then writes the minimum code to pass that test. Then improves it. CORTEX verifies the sequence. There is no configuration option to skip it. There is no flag for 'small changes.' Every behaviour that matters has a test — written deliberately, before the code."

**VBP-016:** Bold: **"failing test"**, **"before a single line"**, **"deliberately"** in `#7b61ff`.

---

## Scene 3 — Sweep Completeness: No Partial Fixes (1:05 – 1:40)

**Visual:**
A codebase map — a grid of file nodes (small circles), all neutral `#a0a6c0`. One file node pulses red: `auth/validate.py`.

**Step 1:** CORTEX scans. All instances of the email validation bug glow red simultaneously: 4 nodes across the grid.

**Step 2:** A sweep catalogue card appears (glassmorphism):
```
Sweep Catalogue — Open
Issues found: 4
  ├ auth/validate.py         ○ OPEN
  ├ api/user_endpoints.py    ○ OPEN
  ├ forms/registration.py    ○ OPEN
  └ utils/email_helpers.py   ○ OPEN
```

**Step 3:** Each item turns `#00ff88` green in sequence as CORTEX fixes them: `● CLOSED`.

**Step 4:** Catalogue shows: `Issues resolved: 4/4 — Sweep Complete ✅`

**Narration:**
> "When CORTEX finds an issue, it doesn't fix the instance you showed it. It scans the entire codebase for the same pattern, catalogues every occurrence, and closes every one. The sweep is not complete because CORTEX ran through the checklist. It's complete because the checklist is empty. No partial fixes. No 'we'll catch the others next sprint.'"

**VBP-009 (Signaling):** Each file node pulses as it is fixed.

---

## Scene 4 — The DoR → DoD Pipeline (1:40 – 2:10)

**Visual:**
A horizontal pipeline with seven glassmorphism stages, purple top-border, animated entry left-to-right:

```
[Decision Support] → [Requirements] → [Design] → [TDD Implementation]
→ [Code Review] → [Security Assessment] → [Release Readiness ✅]
```

**Breadcrumb (VBP-015, bottom):** Stage names with current stage highlighted purple.

At "Release Readiness", a governance certificate card appears:
```
🎖️ Governance Certificate
  Tests: ✅ All ACs covered
  Security: ✅ 5 layers passed
  Governance: ✅ 60+ rules satisfied
  Sweep: ✅ No open issues
```

**Narration:**
> "CORTEX structures delivery as a seven-phase pipeline. Requirements flow into design. Design flows into test-driven implementation. Implementation flows into automated code review, security assessment, and release readiness. Each phase gates the next. A feature reaches production not because a developer said it's ready — but because evidence exists at every phase that it is."

**VBP-013 (Business Book):** Brief callout card: *"Definition of Done is not a checkbox — it's a proof."* — Dan North, BDD principles.

---

## Scene 5 — Code-Backed SWAGs: Decision Support Before You Commit (2:10 – 2:40)

**Visual:**
A Product Owner's conversation bubble: `"How long will this take to build?"`.

CORTEX responds with a structured card (glassmorphism, purple border):

```
Change Intelligence Report
────────────────────────────
Feature: Email validation overhaul
Codebase analysis: 4 touch points identified
Estimated complexity: MODERATE (CDR score: 4.2)
Estimated effort: 3–5 days
Risk: Low — isolated utility layer
Recommendation: Implement as standalone sprint item
```

**Narration:**
> "Before you commit to a sprint, CORTEX provides evidence-backed estimates. The Change Intelligence engine analyses the actual codebase — identifying every touch point, complexity score, and risk factor — and produces a structured recommendation. Not a SWAG. A code-backed assessment. So when you say 'three to five days', you have the evidence to back it up."

**VBP-010 (Analogy):** "Like a structural survey before you renovate — you see what's behind the walls before you pick up a hammer." Dark pill.

---

## Scene 6 — Institutional Memory: Failures Don't Repeat (2:40 – 3:10)

**Visual:**
A prevention rule card (glassmorphism, amber `#fbbf24` top-border):

```
⚠️ Prior failure pattern detected
Pattern: Email validation missing async boundary
Confidence: 0.82
Last occurrence: Sprint 14 — auth module
Prevention rule: Add await to validation calls
Status: ADVISORY
```

Beneath it: a cycle diagram — `Failure → RCA → Prevention Rule → Next Request → Prevented`.

**Narration:**
> "When something goes wrong, CORTEX doesn't just fix it. It analyses the root cause — using four structured methodologies — and stores a prevention rule. The next time a similar operation is attempted, that historical knowledge surfaces automatically. The tenth occurrence of a root cause is prevented before it happens. Your team's institutional knowledge doesn't leave when a developer does."

---

## Scene 7 — Call to Action (3:10 – 3:25)

**Visual:**
Single centred card, glassmorphism, purple border:

> **"Your acceptance criteria become tests. Your tests become evidence. Your evidence becomes confidence."**

Below: `→ Explore the full CORTEX delivery lifecycle` in `#00d4ff`.
Breadcrumb (bottom): `03/07 — Product Owners | 04 → Software Engineers →`

**Narration:**
> "CORTEX connects intent to traceable delivery. Your acceptance criteria become tests — written before implementation. Your tests become the evidence that every requirement shipped correctly. That evidence becomes the confidence you need to say 'done' — and mean it."

---

## 🎬 Closing Title Card (3:25 – 3:30)

CORTEX logo hero-scale. Tagline: **"CORTEX — Cognitive Real-Time Execution"** — Inter, `#a0a6c0`.

---

## 🎨 Visual Identity Compliance Checklist

| Rule | Applied |
|------|---------|
| VBP-001 One Idea Per Frame | ✅ |
| VBP-002 Hook in 8 seconds | ✅ Pain AC gap at 0:07 |
| VBP-003 Narration ≠ slide text | ✅ |
| VBP-004 Progressive disclosure | ✅ Sweep catalogue reveals one-by-one |
| VBP-005 Z/F pattern | ✅ AC card top-left; pipeline left-to-right |
| VBP-006 Contrast storytelling | ✅ Three red ACs → green outcomes |
| VBP-007 2-min visual cycles | ✅ |
| VBP-008 Title + duration + chapters | ✅ |
| VBP-009 Signaling | ✅ File nodes pulse during sweep |
| VBP-010 Analogy | ✅ Structural survey analogy, dark pill |
| VBP-011 Strategic silence | ✅ 1.5s after three red outcomes |
| VBP-012 Consistent visual language | ✅ Purple domain colour throughout |
| VBP-013 Business Book | ✅ Dan North DoD quote |
| VBP-014 Hero intro slide | ✅ |
| VBP-015 Breadcrumb | ✅ TDD cycle Scene 2, lifecycle pipeline Scene 4 |
| VBP-016 Bold key words | ✅ Purple highlights |
| VBP-017 Female narrator | ✅ Odd-numbered video |
| VBP-018 No unexpanded acronyms | ✅ AC, TDD, DoR, DoD, SWAG expanded |
| VBP-019 Strategic colour | ✅ Purple (`#7b61ff`) for Product Owner domain |

---

## 🎵 Audio Direction

- **Background:** Focused ambient pad — deliberate, rhythmic undertone, slightly progressive
- **Red AC outcomes (Scene 1):** Subtle low-register tone per item — tension building
- **TDD cycle transitions (Scene 2):** Distinct chime per phase: RED = low tone, GREEN = ascending tone, REFACTOR = resonant chord
- **Sweep catalogue CLOSED (Scene 3):** Satisfying click-tick per item — completion signal
- **Governance certificate (Scene 4):** Distinct "certified" chime
- **Narration style:** Energetic, clear, evidence-focused. Pace: 145 wpm. Calibrated for POs who think in outcomes and evidence.
