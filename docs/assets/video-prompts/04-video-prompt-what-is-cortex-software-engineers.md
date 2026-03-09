# Video Prompt 04 — What Is CORTEX? (Software Engineers)

---
**Series:** CORTEX — The Governed AI Engineering Partner
**Video:** 04 of 07 (Role Series)
**Title:** What Is CORTEX? For Software Engineers
**Subtitle:** LENS Intelligence, Enforced TDD, 290+ Orchestrators, and Institutional Memory
**Audience:** Software engineers, developers, architects, tech leads — all experience levels
**Duration:** 7–10 minutes
**Narrator:** 🎙️ Male (VBP-017 — even-numbered video)
**Generator:** Google Gemini Video Generator / NotebookLM Video Editor
**Last Updated:** 2026-03-08
**VBP Rules Applied:** VBP-001 through VBP-019 (full compliance)
**Content Sources:** `01-platform`, `02-intelligence`, `04-tdd-quality-flywheel`, `05-orchestration`, `06-mcp-tools`, `08-learning`
**Series Context:** Video 01 introduced the CORTEX platform and its three mission pillars. This video does NOT repeat that introduction — it goes deep on what CORTEX does for engineers specifically: how LENS analyses your codebase in under one second across nine dimensions, how TDD is structurally enforced (not suggested), how the 290+ orchestrator network routes your intent, and how the learning loop builds institutional memory that survives team turnover.

---

## 🎯 Learning Objective

Software engineers understand that CORTEX functions as a senior engineering partner — nine-dimensional LENS code analysis in under one second, structurally enforced TDD (not a suggestion), a coordinated network of 290+ specialist orchestrators, 35+ IDE-native MCP tools, a multi-stack debug pipeline, and institutional memory that learns from every outcome and prevents recurring failures.

---

## 🎬 MANDATORY Hero Intro Slide (VBP-014 — 5 seconds)

**Scene:** Full-screen `#0a0e27` deep space navy. Cyan data streams flow diagonally. Code characters (`{}`, `=>`, `()`) drift at 8% opacity.

**Centre frame:**
- `cortex-logo-512.png` — large, hero-scale, pulsing cyan glow
- **Above logo:** "What Is CORTEX?" — Space Grotesk Bold, `#ffffff`, 48px
- **Below logo:** "For Software Engineers — The Senior Partner Who Knows Your Codebase" — Inter Regular, `#a0a6c0`, 20px, typewriter reveal

**Hold 5 seconds → logo to watermark → Scene 1 fades in.**

---

## Scene 1 — The Hook: What Your Current Tool Doesn't Know (0:05 – 0:40)

**Visual (VBP-006 — pain before solution):**

Left panel — a generic AI response card:
```
💬 "Implement the authentication middleware."
🤖 "Here's a standard JWT middleware implementation:
    [generic code snippet]"
```
Label beneath: `"Knows: General patterns"` — `#a0a6c0`.

Right panel — CORTEX response card (cyan glow border):
```
💬 "Implement the authentication middleware."
🧠 LENS analysis complete (0.8s):
    ✅ Existing auth: OAuth2 + refresh token pattern
    ✅ Your stack: FastAPI 0.104, Python 3.11
    ✅ Security: 2 existing auth tests — extending pattern
    ✅ Governance: Type hints + docstrings required
    ✅ Complexity hotspot: middleware chain — isolate concern
    → Generating failing test first (TDD: RED phase)...
```
Label beneath: `"Knows: Your codebase"` — `#00d4ff`.

**Narration:**
> "Most AI tools know general patterns. CORTEX knows your codebase. Before generating a single suggestion, nine analysis tools run against your specific code — your architecture, your patterns, your security posture, your test coverage, your complexity distribution — in under one second. What comes back isn't generic. It fits."

**VBP-002:** Hook at 0:07.
**VBP-011:** 1.5s silence after the contrast reveal.

---

## Scene 2 — LENS: Nine Analysers, One Second (0:40 – 1:25)

**Visual:**
A circular diagram — LENS styled as an eye. The iris is divided into nine segments, each a different `rgba()` hue at 0.7 opacity. Each segment glows as narrated:

| Segment | Label | Glow Colour | What it surfaces |
|---------|-------|-------------|-----------------|
| 1 | Structure | `#00d4ff` cyan | Module dependencies, import graph, architectural layers |
| 2 | History | `#7b61ff` purple | Git blame, change frequency hotspots, ownership |
| 3 | Documentation | `#3b82f6` blue | Docstring coverage, API documentation gaps |
| 4 | Dependencies | `#fbbf24` amber | Package versions, CVE exposure, update risk |
| 5 | Security | `#ff4444` red | Secret patterns, SQL injection, XSS vectors |
| 6 | Patterns | `#00ff88` green | Recurring code patterns, anti-pattern detection |
| 7 | Complexity | `#ffa500` orange | Cyclomatic complexity, cognitive load hotspots |
| 8 | Business Domain | `#a78bfa` violet | Domain model extraction, bounded contexts |
| 9 | Technology Stack | `#67e8f9` sky | Framework versions, runtime environment, build chain |

Pupil centre: `LENS` in Space Grotesk Bold, `#ffffff`. A scan line sweeps clockwise. Results card appears at pupil:
```
Analysis complete: 0.8s
9 analysers | parallel execution | codebase-specific
```

**Breadcrumb (VBP-015, bottom):** `L → E → N → S` (Language → Examination → Navigation → Synthesis), current letter highlighted cyan.

**Narration:**
> "LENS — Language, Examination, Navigation, Synthesis — runs nine specialised analysers simultaneously. Structure tells CORTEX how your modules relate. History tells it where change volatility is high. Security surfaces injection vulnerabilities, exposed secrets, and PII. Complexity scores every function so that refactoring recommendations target the right places. All nine run in parallel, all complete in under one second. This is not a scan of a generic codebase — it is a scan of yours."

**VBP-009 (Signaling):** Each segment glows brighter as narrated; others dim to 30%.

---

## Scene 3 — TDD: Enforced by Structure, Not Suggestion (1:25 – 2:05)

**Visual:**
A three-phase TDD cycle in a circular track:

```
      🔴 RED
  (failing test)
       ↓
🟢 GREEN          ♻️ REFACTOR
(minimum code)    (improve safely)
```

An enforcement gate appears before GREEN. Two gate states:

✅ Gate OPEN:
```
CORTEX TDD Gate
────────────────────────
✅ Test exists: YES
✅ Test fails before implementation: YES
✅ Gate: OPEN → proceed to implementation
```

❌ Gate CLOSED:
```
CORTEX TDD Gate
────────────────────────
❌ Test passes before implementation exists
❌ Vacuous test detected — tests nothing meaningful
❌ Gate: CLOSED → test must be rewritten
```

JetBrains Mono code block (dark panel):
```python
def test_auth_middleware_rejects_expired_token():
    # RED: This test MUST fail before implementation
    response = client.get("/protected", headers={"Authorization": "Bearer expired_token"})
    assert response.status_code == 401  # fails ✅ → gate open
```

**Narration:**
> "CORTEX enforces test-driven development at the structural level. Not as a recommendation. Not as a style guide. The system verifies a failing test exists before allowing implementation to proceed. A test that already passes before implementation exists is flagged as vacuous — it proves nothing — and must be rewritten before the gate opens. There is no configuration option to bypass this. There is no flag for 'small changes.' Every behaviour that matters has a test, written deliberately, before the code."

**VBP-016:** Bold: **"structural level"**, **"vacuous"**, **"before the code"** in `#00d4ff`.

---

## Scene 4 — The Orchestrator Network: 290+ Specialists (2:05 – 2:45)

**Visual:**
A force-directed node graph (glassmorphism). Centre node: `MasterOrchestrator` — large, cyan glow. Surrounding nodes arranged in 14 clusters with individual counts:

```
Core (132+)         ← Command and routing layer
Domain (29+)        ← Code Review, Refactoring, Planning, Security
Support (54+)       ← Health, Debug, Cleanup, Maintenance
Intelligence (16+)  ← LENS, RCA, Learning, Knowledge Synthesis
Health (27+)        ← Monitoring, Vacuum, Validation
Git (4)             ← Version control, sync, checkpoint
```

Intent routing animation: a request orb travels from a developer prompt → `IntentRouter` → classifies in 40ms → routes to `TDDOrchestrator` → returns structured response.

A classification card:
```
Intent Classification — 40ms
────────────────────────────
Input: "add tests for the payment module"
Intent: TDD
Confidence: 0.97
Route: TDDOrchestrator → TDD workflow template
```

**Narration:**
> "CORTEX is not one AI model. It is a coordinated network of 290-plus specialised orchestrators — each an expert at exactly one category of engineering work. Every request is classified into one of 31 intent types in under 40 milliseconds, then routed to the correct specialist. A request to add tests goes to the TDD orchestrator. A request to investigate a failing build goes to the Debug Tracer. A request to audit governance goes to the Audit Coordinator. Like a hospital that routes a patient to cardiology, not the front desk — in under 40 milliseconds."

**VBP-010 (Analogy):** Hospital routing analogy. Dark pill background.

---

## Scene 5 — Multi-Stack Debug Pipeline (2:45 – 3:25)

**Visual:**
A five-phase debug pipeline (cyan-dominant, glassmorphism):

```
[INJECT markers] → [Capture output] → [Analyse with LENS] → [Fix plan] → [CLEANUP]
```

Eight strategy cards arranged in two rows (3 Python + 5 multi-stack):

**Python strategies:**
- `TestFailureStrategy` — test failure root cause
- `RefactorRegressionStrategy` — regressions after refactoring
- `GovernanceViolationStrategy` — governance gate failures

**Multi-stack strategies:**
- `FrontendConsoleStrategy` — JS/TS/React/Angular/Vue console errors
- `HtmlVisionMappingStrategy` — Vision API + DOM layout analysis
- `ApiTraceStrategy` — REST/GraphQL/gRPC request tracing
- `SqlTraceStrategy` — SQL Server/Oracle/PostgreSQL query tracing
- `DotNetTraceStrategy` — C#/.NET event tracing

**Terminal card showing injection:**
```
CORTEX Debug — INJECT phase
────────────────────────────
Strategy:    TestFailureStrategy
Markers:     CORTEX_DEBUG inserted at 3 entry points
Output:      .cortex-debug/traces/session_847.json
Cleanup:     Scheduled — markers removed after analysis
```

**Narration:**
> "When something breaks, CORTEX's debug pipeline injects structured markers into your code, captures execution output, analyses it with LENS context, and generates a prioritised fix plan — across eight strategies covering Python, JavaScript, TypeScript, React, REST APIs, SQL databases, and .NET. After analysis is complete, all markers are automatically removed — leaving no debug artefacts in your codebase."

---

## Scene 6 — 35+ Tools in Your IDE (3:25 – 4:05)

**Visual:**
A VS Code Copilot Chat panel (dark glass simulation). A developer types `cortex_review`.

CORTEX responds with a multi-pass code review card:

```
Code Review — auth/middleware.py
────────────────────────────────
P0 — CRITICAL: Bare exception catch on line 42 (swallows auth failures)
P1 — HIGH: Missing type annotation on validate_token()
P2 — MEDIUM: No docstring on AuthMiddleware class
P3 — ADVISORY: Complexity score 12 — consider extracting token decoder
```

Each severity item has a colour-coded left border: `#ff4444`, `#ffa500`, `#fbbf24`, `#3b82f6`.

A tool catalogue pill list scrolls beneath:
```
cortex_review | cortex_classify | cortex_validate | cortex_learning | cortex_vision
cortex_refactor | cortex_debug | cortex_rca | cortex_workflow | +26 more
```

Server status card (glassmorphism, cyan border):
```
CORTEX MCP Server
────────────────────
Transport: stdio (auto-detected)
Status:    ✅ RUNNING
Tools:     36 registered
Startup:   1.2s — workspace opens, server starts
```

**Narration:**
> "36 CORTEX capabilities are available directly in your IDE through the Model Context Protocol. No context switching. No terminal. No separate tool. A code review. A governance check. A root cause analysis. A visual layout analysis from a screenshot. A refactoring plan. A debug injection. All from the chat interface you already use — and the server starts automatically when you open the workspace."

**VBP-018:** "MCP" expanded on first use as "Model Context Protocol".

---

## Scene 7 — Institutional Memory: Prevention, Not Repetition (4:05 – 4:45)

**Visual:**
A circular learning loop diagram (4 nodes, cyan connecting arcs):

```
Outcome → Reinforce Signal → Confidence Score → Next Recommendation → (repeat)
```

A prevention rule card overlays (amber `#fbbf24` border):

```
⚠️ Prior failure detected — WARNING
Pattern: Missing async boundary in validation chain
Confidence: 0.87
Seen: 3 times across 2 projects
Last occurrence: Sprint 14 — auth module regression
Prevention: Wrap validation coroutines in asyncio.gather()
Status: WARNING — acknowledgement required before proceeding
```

Below: a learning timeline bar — Week 1, Week 4, Week 12. Confidence score graph line rises. Low-confidence approaches are demoted (dashed line descends).

**Narration:**
> "CORTEX learns from every outcome across your codebase's lifetime. Approaches that consistently produce working code gain confidence and are recommended first. Approaches that lead to rework are demoted. And patterns that cause recurring failures — the ones that cost your team two days in Sprint 14, then again in Sprint 22 — are stored as prevention rules with a confidence score. The next time a similar change is attempted, the rule surfaces automatically. Your team's hard-won knowledge doesn't leave when a developer does."

**VBP-013 (Business Book):** Callout: *"Those who cannot remember the past are condemned to repeat it."* — George Santayana, **The Life of Reason**. Dark pill.

---

## Scene 8 — RCA Memory Engine: Four Methodologies (4:45 – 5:25)

**Visual:**
A four-panel RCA methodology card (glassmorphism, amber top-border):

```
Root Cause Analysis Engine — 4 Methodologies
──────────────────────────────────────────────────────────────────
Five-Whys         → Technology failures (linear causal chain)
Fishbone (Ishikawa) → Process & people failures (category mapping)
Fault-Tree        → Data failures (logical decomposition)
Causal-Chain      → Complex multi-factor failures

Auto-selection: Category → Methodology (95% accuracy)
Persistence:    SQLite-backed prevention rules
Output:         ADVISORY prevention rule — reviewed, not auto-applied
```

An example Five-Whys trace:
```
Production incident: Auth middleware returning 500
  Why? → Bare exception catch swallowing auth failures
    Why? → No TDD gate — test written after implementation
      Why? → No enforcement gate on this module at the time
        Why? → CORTEX not yet applied to auth module
          Prevention: Add TDD gate to all new modules — APPLIED ✅
```

**Narration:**
> "When failures do occur, CORTEX's Root Cause Analysis engine applies one of four structured methodologies — Five-Whys, Fishbone, Fault-Tree, or Causal-Chain — selected automatically based on the failure category. The result is a structured prevention rule stored in the RCA database, surfaced at planning time the next time a similar change is proposed. Root causes are not just found — they are recorded and prevented."

---

## Scene 9 — Vision: The Engineering Partner You've Always Needed (5:25 – 5:55)

**Visual:**
Full-screen dark navy. A quote card — glassmorphism, cyan top-border:

> *"The most effective debugging tool is still careful thought, coupled with judiciously placed print statements."*
> — Brian Kernighan, **Unix for Beginners**

Below: a second card:

> **"CORTEX is the senior engineer who has already read your codebase, knows where the landmines are, and wrote the test before you asked."**

**AUDIO: Strategic Silence — 2 seconds.**

**Narration:**
> "The senior engineer you want on every project is the one who knows the codebase deeply, asks the right questions before implementation begins, enforces the standards without micromanaging, and remembers every lesson the team ever learned. CORTEX is that engineer — available on every project, from the first commit."

---

## Scene 10 — Call to Action (5:55 – 6:10)

**Visual:**
Single centred card, glassmorphism, cyan border:

> **"Nine analysers. 290+ orchestrators. 36 tools. Enforced TDD. Institutional memory that never forgets."**

Below: `→ Explore the CORTEX engineering guide for software engineers` in `#00d4ff`.
Breadcrumb (bottom): `04/07 — Software Engineers | 05 → Security Engineers →`

**Narration:**
> "CORTEX is the senior engineering partner that knows your codebase, enforces your standards, catches your blind spots, and remembers every lesson your team has ever learned. All without leaving your editor."

---

## 🎬 Closing Title Card

`cortex-logo-512.png` hero-scale. Tagline: **"CORTEX — Cognitive Real-Time Execution"** — Inter, `#a0a6c0`.

---

## 🎨 Visual Identity Compliance Checklist

| Rule | Applied |
|------|---------|
| VBP-001 One Idea Per Frame | ✅ |
| VBP-002 Hook in 8 seconds | ✅ Generic vs CORTEX contrast Scene 1, 0:07 |
| VBP-003 Narration ≠ slide text | ✅ Code shown; narration explains the enforcement contract |
| VBP-004 Progressive disclosure | ✅ LENS segments light up sequentially; RCA trace unfolds step-by-step |
| VBP-005 Z/F pattern | ✅ Left-to-right debug pipeline; LENS eye centred |
| VBP-006 Contrast storytelling | ✅ Generic AI vs CORTEX Scene 1 |
| VBP-007 2-min visual cycles | ✅ New concept every scene |
| VBP-008 Title + duration + chapters | ✅ Intro slide + phase breadcrumbs |
| VBP-009 Signaling | ✅ LENS segments dim when inactive; TDD gate states |
| VBP-010 Analogy | ✅ Hospital routing Scene 4; dark pill |
| VBP-011 Strategic silence | ✅ 1.5s after contrast reveal Scene 1; 2s after Kernighan quote Scene 9 |
| VBP-012 Consistent visual language | ✅ Cyan dominant throughout |
| VBP-013 Business Book | ✅ Santayana Scene 7; Kernighan Scene 9 |
| VBP-014 Hero intro slide | ✅ `cortex-logo-512.png`, 5 seconds |
| VBP-015 Breadcrumb | ✅ LENS letters Scene 2; debug pipeline Scene 5 |
| VBP-016 Bold key words | ✅ Cyan highlights on enforcement terms |
| VBP-017 Male narrator | ✅ Even-numbered video |
| VBP-018 No unexpanded acronyms | ✅ LENS, TDD, MCP, RCA, IDE, SAST, CVE, AC, VBP all expanded |
| VBP-019 Strategic colour | ✅ Cyan (`#00d4ff`) as primary — software engineer domain |

---

## 🎵 Audio Direction

- **Background:** Calm electronic ambient — focused, technical, slightly pulsing rhythm
- **LENS scan sweep (Scene 2):** Subtle electromagnetic sweep sound per segment
- **TDD gate block (Scene 3):** Sharp low tone — block signal; ascending tone when gate passes
- **Orchestrator routing orb (Scene 4):** Data-stream whoosh as orb travels nodes
- **Debug marker injection (Scene 5):** Structured click-click per marker inserted
- **Code review severity items (Scene 6):** Descending tone per severity: P0 = deep alert, P3 = soft ping
- **Prevention rule alert (Scene 7):** Amber chime — advisory, not alarm
- **Kernighan quote silence (Scene 9):** Absolute silence — 2 full seconds, no music, no FX
- **Narration style:** Peer-to-peer engineering tone. 145 wpm. Technical but never academic. Shows the work, explains the reasoning.


**Visual (VBP-006 — pain before solution):**

Left panel — a generic AI response card:
```
💬 "Implement the authentication middleware."
🤖 "Here's a standard JWT middleware implementation:
    [generic code snippet]"
```
Label beneath: `"Knows: General patterns"` — `#a0a6c0`.

Right panel — CORTEX response card (cyan glow border):
```
💬 "Implement the authentication middleware."
🧠 LENS analysis complete (0.8s):
    ✅ Existing auth: OAuth2 + refresh token pattern
    ✅ Your stack: FastAPI 0.104, Python 3.11
    ✅ Security: 2 existing auth tests — extending pattern
    ✅ Governance: Type hints + docstrings required
    → Generating test first (TDD: RED phase)...
```
Label beneath: `"Knows: Your codebase"` — `#00d4ff`.

**Narration:**
> "Most AI tools know general patterns. CORTEX knows your codebase. Before generating a single suggestion, nine analysis tools run against your specific code — your architecture, your patterns, your security posture, your test coverage — in under one second. What comes back isn't generic. It fits."

**VBP-002:** Hook at 0:07.

---

## Scene 2 — LENS: The Nine Analyzers (0:28 – 1:05)

**Visual:**
A circular diagram — LENS styled as an eye. The iris is divided into nine segments, each a different `rgba()` hue at 0.7 opacity. Each segment glows as narrated:

| Segment | Label | Glow Colour |
|---------|-------|-------------|
| 1 | Structure | `#00d4ff` cyan |
| 2 | History | `#7b61ff` purple |
| 3 | Documentation | `#3b82f6` blue |
| 4 | Dependencies | `#fbbf24` amber |
| 5 | Security | `#ff4444` red |
| 6 | Patterns | `#00ff88` green |
| 7 | Complexity | `#ffa500` orange |
| 8 | Business Domain | `#a78bfa` violet |
| 9 | Technology Stack | `#67e8f9` sky |

Pupil centre: `LENS` in Space Grotesk Bold, `#ffffff`. A scan line sweeps clockwise. Results card appears at pupil: `"Analysis complete: 0.8s"`.

**Breadcrumb (VBP-015, bottom):** `L → E → N → S` (Language → Examination → Navigation → Synthesis), current letter highlighted cyan.

**Narration:**
> "LENS — Language, Examination, Navigation, Synthesis — runs nine specialised analysers simultaneously. Structure, history, documentation, dependencies, security, patterns, complexity, business domain, technology stack. All in parallel. All complete in under one second. This is not a scan of a generic codebase. It is a scan of yours."

**VBP-009 (Signaling):** Each segment glows brighter as narrated; others dim to 30%.
**VBP-016:** Bold: **"nine analysers"**, **"simultaneously"**, **"under one second"** in `#00d4ff`.

---

## Scene 3 — TDD: Enforced, Not Suggested (1:05 – 1:40)

**Visual:**
A three-phase TDD cycle in a circular track. The cycle is animated — a cyan token travels the track:

```
      🔴 RED
  (failing test)
       ↓
🟢 GREEN          ♻️ REFACTOR
(minimum code)    (improve safely)
```

An enforcement gate appears before GREEN: a shield icon with text `"CORTEX verified: test fails ✅"`. A second card: `"Test passes before implementation? NO → Blocked."` — red border, `#ff4444`.

JetBrains Mono code block (dark panel `rgba(26,31,58,0.9)`):
```python
def test_auth_middleware_rejects_expired_token():
    # RED: This test MUST fail before implementation
    response = client.get("/protected", headers={"Authorization": "Bearer expired_token"})
    assert response.status_code == 401  # fails → TDD gate passes
```

**Narration:**
> "CORTEX enforces test-driven development — not as a suggestion, not as a style guide. The system checks for a failing test before allowing any implementation to proceed. There is no configuration option to disable this. There is no flag for small changes. A test that passes before implementation exists is flagged and must be rewritten. CORTEX doesn't let you skip to the code."

**VBP-003 (Narration ≠ slide):** Code block shown; narration explains the enforcement contract, not the code syntax.

---

## Scene 4 — The Orchestrator Network: 290+ Specialists (1:40 – 2:10)

**Visual:**
A force-directed node graph (glassmorphism). Centre node: `MasterOrchestrator` — large, cyan glow. Surrounding nodes arranged in 14 clusters:

Key labelled clusters (labelled on hover effect simulation):
- `Core (130+)` — Command layer
- `Domain (25+)` — Specialists (Code Review, Refactoring, Planning)
- `Support (50+)` — Health, Debug, Cleanup
- `Intelligence (15+)` — LENS, RCA, Learning
- `Git (5)` — Version control

Request orb (cyan) travels: centre → `Request Classifier` → `TDD Orchestrator` → result card.

**Narration:**
> "CORTEX is not one AI system. It is a coordinated network of 290-plus specialised orchestrators — each an expert at one category of engineering work. Every request is classified into one of 30-plus intent types in under 40 milliseconds and routed to the correct specialist. Like a hospital routing a patient to the right department — cardiology, not dentistry — in under 40 milliseconds."

**VBP-010 (Analogy):** Hospital routing analogy. Dark pill background.

---

## Scene 5 — 35+ Tools in Your IDE (2:10 – 2:40)

**Visual:**
A VS Code Copilot Chat panel (dark glass simulation). A developer types:

`cortex_review`

CORTEX responds with a multi-pass code review card:

```
Code Review — auth/middleware.py
────────────────────────────────
P0 — CRITICAL: Bare exception catch on line 42 (swallows auth failures)
P1 — HIGH: Missing type annotation on validate_token()
P2 — MEDIUM: No docstring on AuthMiddleware class
P3 — ADVISORY: Complexity score 12 — consider extracting token decoder
```

Each severity item has a colour-coded left border: `#ff4444`, `#ffa500`, `#fbbf24`, `#3b82f6`.

Below: a tool catalogue pill list: `cortex_classify | cortex_review | cortex_validate | cortex_learning | cortex_vision | cortex_refactor | +29 more`

**Narration:**
> "35-plus CORTEX capabilities are available directly in your IDE through the Model Context Protocol. No context switching. No terminal. No separate tool. A code review, a governance check, a root cause analysis, a refactoring suggestion, a visual layout analysis from a screenshot — all from the chat interface you already use. The server starts automatically when you open the workspace."

**VBP-018:** "MCP" expanded on first use as "Model Context Protocol".

---

## Scene 6 — Institutional Memory: The Learning Loop (2:40 – 3:15)

**Visual:**
A circular learning loop diagram (4 nodes, cyan connecting arcs):

```
Outcome → Reinforce Signal → Confidence Score → Next Recommendation → (repeat)
```

A prevention rule card overlays (amber `#fbbf24` border):

```
⚠️ Prior failure detected
Pattern: Missing async boundary in validation chain
Confidence: 0.87
Seen: 3 times across 2 projects
Prevention: Wrap validation coroutines in asyncio.gather()
Status: WARNING — acknowledgement required
```

Below: a learning timeline bar — Week 1, Week 4, Week 12 markers. Confidence score graph line rises left-to-right.

**Narration:**
> "CORTEX learns from every outcome. Approaches that consistently produce working code gain confidence and are recommended first. Approaches that consistently require rework are demoted. Patterns that cause recurring failures are stored as prevention rules — and surface automatically before you make the same mistake. Your team's institutional knowledge persists even when the engineer who discovered the pattern has moved on."

**VBP-013 (Business Book):** Callout card: *"Those who cannot remember the past are condemned to repeat it."* — George Santayana, **The Life of Reason**. Dark pill.

---

## Scene 7 — Call to Action (3:15 – 3:30)

**Visual:**
Single centred card, glassmorphism, cyan border:

> **"Nine analysers. 290+ orchestrators. 35+ tools. Enforced TDD. Institutional memory that never forgets."**

Below: `→ Explore the CORTEX engineering guide` in `#00d4ff`.
Breadcrumb (bottom): `04/07 — Software Engineers | 05 → Security Engineers →`

**Narration:**
> "CORTEX is designed to function as the senior engineering partner on every project — the one who knows your architecture, enforces your standards, catches your blind spots, and remembers every lesson your team has ever learned. All without leaving your editor."

---

## 🎬 Closing Title Card (3:30 – 3:45)

CORTEX logo hero-scale. Tagline: **"CORTEX — Cognitive Real-Time Execution"** — Inter, `#a0a6c0`.

---

## 🎨 Visual Identity Compliance Checklist

| Rule | Applied |
|------|---------|
| VBP-001 One Idea Per Frame | ✅ |
| VBP-002 Hook in 8 seconds | ✅ Generic vs CORTEX contrast at 0:07 |
| VBP-003 Narration ≠ slide text | ✅ Code shown; narration explains contract |
| VBP-004 Progressive disclosure | ✅ LENS segments light up sequentially |
| VBP-005 Z/F pattern | ✅ Left-to-right pipeline, LENS eye centred |
| VBP-006 Contrast storytelling | ✅ Generic AI vs CORTEX Scene 1 |
| VBP-007 2-min visual cycles | ✅ |
| VBP-008 Title + duration + chapters | ✅ |
| VBP-009 Signaling | ✅ LENS segments dim when inactive |
| VBP-010 Analogy | ✅ Hospital routing, dark pill |
| VBP-011 Strategic silence | ✅ After TDD enforcement block |
| VBP-012 Consistent visual language | ✅ Cyan dominant throughout |
| VBP-013 Business Book | ✅ Santayana quote Scene 6 |
| VBP-014 Hero intro slide | ✅ |
| VBP-015 Breadcrumb | ✅ LENS letters Scene 2, TDD cycle Scene 3 |
| VBP-016 Bold key words | ✅ |
| VBP-017 Male narrator | ✅ Even-numbered video |
| VBP-018 No unexpanded acronyms | ✅ LENS, TDD, MCP, RCA, IDE expanded |
| VBP-019 Strategic colour | ✅ Cyan (`#00d4ff`) as primary — engineer domain |

---

## 🎵 Audio Direction

- **Background:** Calm electronic ambient — focused, technical, slightly pulsing rhythm
- **LENS scan sweep (Scene 2):** Subtle electromagnetic sweep sound
- **TDD gate block (Scene 3):** Sharp low tone — block signal; then ascending tone when gate passes
- **Orchestrator routing orb (Scene 4):** Data-stream whoosh as orb travels nodes
- **Code review severity items (Scene 5):** Descending tone severity: P0 = deep alert, P3 = soft ping
- **Prevention rule alert (Scene 6):** Amber chime — advisory, not alarm
- **Narration style:** Conversational peer-to-peer. Slightly faster pace (150 wpm). Technical but never academic. Calibrated for engineers who trust tools that show their work.
