# Tutorial 06 — Onboarding a New Repository

> **Duration:** 8 minutes · **Audience:** Tech Leads, Platform Engineers
> **Depth:** 🔴 Tutorial — hands-on repository onboarding session
> **Prerequisites:** Tutorial 01 (installation), concept Videos 03 (intelligence) + 04 (governance)
> **Goal:** User takes an existing, ungoverned repository and brings it under CORTEX governance using `/onboard` — experiencing LENS analysis, gap detection, security assessment, and automated dashboard generation
> **No overlap:** Concept Video 03 explains LENS *theory*; Video 04 covers governance *rules*. This tutorial shows the **hands-on act of adopting CORTEX** in an existing codebase — the migration experience, not the architecture

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).
>
> **Tutorial-specific:** Simulated VS Code UI as a PiP (picture-in-picture) overlay in the bottom-left corner throughout, showing actual commands being typed in Copilot Chat and terminal output.

---

## PROMPT

Create an 8-minute animated tutorial video titled **"Onboarding a New Repository"** using the visual identity above. The viewer will take a real-world Python API service — ungoverned, partially tested, with some tech debt — and bring it under full CORTEX governance in a single session. This is the tutorial for teams adopting CORTEX on existing projects.

**Opening hook — start with the reality of what most codebases look like.**

---

### Scene 1 — The Repo Before CORTEX (0:00 – 1:00)

**Open on:** A glassmorphic file tree of a typical Python API project. No introduction — we're examining the patient.

```
payment-service/
├── app/
│   ├── main.py
│   ├── routes/
│   │   ├── payments.py      (412 lines, 0 type hints)
│   │   ├── webhooks.py      (287 lines, 3 type hints)
│   │   └── health.py        (18 lines)
│   ├── models/
│   │   ├── transaction.py   (156 lines, no docstrings)
│   │   └── customer.py      (89 lines)
│   └── services/
│       ├── stripe_client.py (203 lines, hardcoded API key ⚠️)
│       └── fraud_check.py   (167 lines)
├── tests/
│   ├── test_payments.py     (4 tests — covers ~15%)
│   └── test_health.py       (1 test)
├── requirements.txt
└── README.md                (last updated: 8 months ago)
```

**Warning badges pulse** next to files:
- 🔴 `stripe_client.py` — hardcoded secret
- 🟡 `payments.py` — zero type hints
- 🟡 `transaction.py` — no docstrings
- 🟡 Test coverage: ~15%

A readiness gauge at the top: **Governance Readiness: 12%**

**Narration:** *"A payment service. Twelve hundred lines of code that processes real money. Four tests. A hardcoded API key. A README nobody's updated in eight months. Sound familiar? This is what most codebases look like before governance. Let's change that."*

---

### Scene 2 — Launch Onboarding (1:00 – 2:15)

**PiP: Copilot Chat.** The user types:

```
/onboard payment-service/
```

**The onboarding pipeline activates.** A progress card renders:

```
🔍 ONBOARDING: payment-service/

Phase 1: LENS Analysis        ░░░░░░░░░░  scanning...
Phase 2: Security Assessment   ░░░░░░░░░░  queued
Phase 3: Gap Catalogue         ░░░░░░░░░░  queued
Phase 4: Dashboard Generation  ░░░░░░░░░░  queued
```

**Narration:** *"One command. Four phases. CORTEX is about to understand this codebase better than the team that wrote it."*

---

### Scene 3 — Phase 1: LENS Analysis (2:15 – 3:45)

**LENS eye animation** scans the codebase. Four quadrants populate:

```
🔤 LANGUAGE
  Python 3.11 | FastAPI | SQLAlchemy | Pydantic
  Lines: 1,332 | Files: 9 | Avg complexity: 14.2 (HIGH)
  Import graph: 23 dependencies, 3 circular references ⚠️

🔎 EXAMINATION
  Type coverage: 2.3% (3/132 functions)
  Docstring coverage: 8.1% (2/25 public APIs)
  Dead code: 4 unreachable functions detected
  Duplication: 2 copy-paste blocks (fraud_check ↔ stripe_client)

🧭 NAVIGATION
  Entry points: main.py → routes/ → services/
  Hot paths: payments.py:process_payment() (87% of traffic)
  Dependency depth: 4 layers max
  Orphan modules: 0

🧬 SYNTHESIS
  Architecture: Layered (routes → services → models)
  Patterns: Repository pattern (partial), no DI container
  Tech debt density: 3.2 issues/100 LOC (MODERATE-HIGH)
  Estimated remediation: 14 engineering-hours
```

Each quadrant fills with a satisfying cascade animation. The "14 engineering-hours" estimate glows cyan.

**Narration:** *"In twelve seconds, CORTEX has mapped every function, traced every import path, measured type coverage, identified circular dependencies, and estimated remediation effort. That analysis would take a senior engineer half a day of manual code review."*

---

### Scene 4 — Phase 2: Security Assessment (3:45 – 5:00)

**A security shield materializes.** Findings slide in by priority:

```
🛡️ SECURITY ASSESSMENT

P0 — CRITICAL (block deployment):
  SEC-001: Hardcoded API key in stripe_client.py:17
           "sk_live_XXXX...XXXX" ← placeholder shown for illustration
           → Must move to environment variable / secrets manager

  SEC-002: No input validation on webhook payload (webhooks.py:34)
           → Raw JSON passed to process_webhook() without schema validation

P1 — HIGH (fix before next release):
  SEC-003: SQL query string concatenation in transaction.py:89
           → Potential SQL injection — use parameterized queries

  SEC-004: No rate limiting on payment endpoints
           → Add rate limiter middleware

P2 — MEDIUM (schedule for remediation):
  SEC-005: Debug mode enabled in main.py (debug=True)
  SEC-006: CORS allows all origins ("*")
  SEC-007: No request logging / audit trail
```

**The P0 findings pulse red.** A glassmorphic summary bar:

```
P0: 2 | P1: 2 | P2: 3 | Total: 7 findings
Deployment ready: ❌ (P0 must be resolved)
```

**Narration:** *"Two critical findings that would block any production deployment. A hardcoded API key sitting in source code and an unvalidated webhook endpoint — both discovered automatically, both with specific remediation guidance. No security audit scheduled. No external consultant hired."*

---

### Scene 5 — Phase 3: Gap Catalogue (5:00 – 6:15)

**A governance gap catalogue assembles.** Each CORE rule shows its status:

```
📋 GOVERNANCE GAP CATALOGUE — 38 CORE Rules

✅ Passing (8/38):
  CORE-028 snake_case naming ✅
  CORE-035 No duplicate implementations ✅
  ... (6 more)

⚠️ Gaps (22/38):
  CORE-008 TDD: 5 tests for 9 modules (coverage: 15%) .......... 🟡
  CORE-011 Type hints: 3/132 functions typed (2.3%) ............. 🟡
  CORE-012 Docstrings: 2/25 public APIs documented (8%) ......... 🟡
  CORE-002 Inline output: 3 report files found in repo .......... 🟡
  ... (18 more)

❌ Violations (8/38):
  CORE-048 Holistic validation: no pre-commit hooks ............. 🔴
  CORE-049 Silent execution: verbose debug logging in production  🔴
  ... (6 more)

GOVERNANCE READINESS: 21% → target 85%
ESTIMATED EFFORT: 14 engineering-hours
```

**A remediation roadmap card** renders below:

```
📍 RECOMMENDED ONBOARDING SEQUENCE

Week 1 (P0 — Critical):
  □ Fix hardcoded secrets (SEC-001)
  □ Add webhook validation (SEC-002)
  □ Install pre-commit hooks (CORE-048)

Week 2 (P1 — High):
  □ Add type hints to hot-path functions (CORE-011, 12 functions)
  □ Parameterize SQL queries (SEC-003)
  □ Write tests for payment flow (CORE-008, 8 tests needed)

Week 3-4 (P2 — Medium):
  □ Type hints for remaining functions (120 functions)
  □ Docstrings for public APIs (23 APIs)
  □ Rate limiting + CORS hardening
```

**Narration:** *"Twenty-two governance gaps, eight violations, and a prioritized roadmap to fix them all. Not a generic checklist — a sequence specifically ordered for this codebase, with the critical security issues first. Fourteen hours of work, mapped out in seconds."*

---

### Scene 6 — Phase 4: Dashboard Generation (6:15 – 7:00)

**A SQLite database icon materializes:** `.cortex-runtime/dashboards/payment-service.db`

**The dashboard builds in real-time** — a glassmorphic HTML dashboard assembles:

```
┌─────────────────────────────────────────────┐
│  PAYMENT-SERVICE — CORTEX GOVERNANCE DASHBOARD │
├─────────────────────────────────────────────┤
│                                             │
│  Readiness: ██████░░░░ 21%                  │
│  Security:  ██░░░░░░░░ P0: 2 blockers      │
│  Coverage:  █░░░░░░░░░ 15%                  │
│  Type Hints:░░░░░░░░░░ 2.3%                 │
│                                             │
│  [Remediation Plan] [LENS Report] [History] │
└─────────────────────────────────────────────┘
```

The dashboard is interactive — each bar is clickable, showing per-file breakdowns. The history tab shows "Day 1" as the baseline. Over time, the bars will fill as the team remediates.

**Narration:** *"A living dashboard. Every fix your team makes will update these numbers. In four weeks, those bars should be at eighty-five percent or above. The dashboard holds the team accountable — without a single status meeting."*

---

### Scene 7 — The Transformation Timeline (7:00 – 7:30)

**Camera pulls back.** A horizontal timeline shows the complete onboarding:

```
/onboard  →  LENS  →  Security  →  Gaps  →  Dashboard
 (0:00)     (12s)     (8s)        (5s)      (3s)
```

Total onboarding scan time: **~28 seconds.**

**A fast-forward animation** shows the dashboard evolving over 4 weeks:

```
Day 1:   21% ██░░░░░░░░
Week 1:  45% ████░░░░░░  (P0s resolved)
Week 2:  67% ██████░░░░  (P1s resolved, tests added)
Week 4:  89% ████████░░  (full governance)
```

Each milestone glows green as it's reached.

---

### Scene 8 — Close (7:30 – 8:00)

**Closing text** (Space Grotesk):
**"Meet your codebase where it is. Lift it to where it should be."**

**Vision callback:**
> *"That legacy service your team avoids touching? CORTEX doesn't judge it. It maps it, secures it, and gives you a clear path forward. No rewrites. No blame. Just progress."*

Logo pulse. End card.

---

## Notes

- This tutorial targets **adoption** — the moment a team decides to bring CORTEX into an existing project. It's the most important tutorial for enterprise customers.
- The `payment-service` example is deliberately realistic: FastAPI + SQLAlchemy, partial tests, a hardcoded secret, tech debt. Every engineering team recognises this codebase.
- The security findings (P0 hardcoded key, unvalidated webhook) are real-world vulnerabilities that create urgency — viewers will feel the value immediately.
- The 4-week dashboard evolution (Scene 7) is the emotional payoff — viewers see the transformation arc, not just the scan.
- **No governance re-explanation.** Video 04 covers what rules are. This tutorial shows rules applied to a real codebase — forward references only.
- The "14 engineering-hours" estimate grounds the conversation in business terms — leadership can budget for this.
- Sound design: scan start = initialisation hum; LENS quadrant fills = data whoosh (one per quadrant); P0 findings = alert tone; gap catalogue = rhythmic list build; dashboard build = assembly clicks; 4-week evolution = time-lapse whoosh; close = satisfying completion tone.
