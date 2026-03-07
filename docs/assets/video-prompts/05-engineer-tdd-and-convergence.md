# NotebookLM Video Prompt — SE-01 — TDD and the Convergence Gate: An Engineer's Deep Dive

**Target length:** 11–15 minutes
**Audience:** Software Engineers — people who write the code and run the tests daily
**Narrator gender:** Female (SE-01 — odd position in series, per VBP-017)
**Visual theme:** Dark-blue glassmorphism · ECG heartbeat motif · RED/GREEN/BLUE TDD phase colours
**Series position:** Engineer depth-1 — the only video covering the full TDD lifecycle and convergence gate mechanics

---

## 🎯 Identity Mission
This video is the **definitive test-first and convergence deep-dive** for Software Engineers who write code and run tests daily. It confronts a painful, well-understood reality that is rarely treated with the precision it deserves: **post-deployment regressions are exponentially more expensive than commit-time failures** — not marginally more, but orders of magnitude more in debugging time, incident response, and team trust.

It solves the problem of **delayed validation** — the habit of running tests late, or skipping the failing-test phase because "the feature is obvious" — by demonstrating exactly what CORTEX enforces and why each constraint exists:

1. **The test-first contract** — a failing test must exist before any implementation begins. The failing phase is not a formality; it is proof that the requirement is real and the test is live. CORTEX gates implementation on this confirmation.
2. **Failing → Passing → Refactor discipline** — each phase has a distinct contract. Passing means minimum implementation that satisfies the test — not the cleverest solution. Refactor is safe only because the test contract did not move.
3. **The convergence gate** — the detect→fix→rescan loop runs until critical and high violations reach exactly zero, not until "most" are fixed. Maximum 3 cycles. On exhaustion, CORTEX surfaces remaining issues and blocks completion — the engineer decides whether to override; the system does not hide it.
4. **Test tier selection as a zoom dial** — `make test-changed` (test-first inner loop), `make test-smoke` (pre-commit sanity), `make test` (daily baseline), `make test-parallel` (pre-commit full speed). One tool at four zoom levels.

CORTEX does **not** claim "no bugs." It claims: *systematic validation, repeatable process, fail fast before deploy*. This video is the evidence.

---

## ⚠️ ZERO-OVERLAP DECLARATION
This video exclusively owns:
- The full test-first lifecycle: Failing → Passing → Refactor, with CORTEX gate enforcement per phase
- The convergence gate mechanics: detect → fix → rescan loop internals
- The ECG heartbeat metaphor for test health (phase → colour → ambient pulse)
- Test tier selection: changed vs. smoke vs. unit vs. parallel — when to use which
- The "fail fast" value proposition for engineers (catch at commit, not deploy)

Does NOT repeat: what CORTEX is (Video 01), lane comparison (Video 02), MCP tool catalogue (SE-02), sprint outcomes (Video 04), self-learning mechanics (Video 08).

---

## Steering Prompt
*Paste into NotebookLM → Customize → Steering Prompt:*

> "Select the Explainer format to create an 11–15 minute deep-dive technical walkthrough for software engineers. Subject: how CORTEX enforces TDD-first via CORE-008, what each TDD phase (RED/GREEN/REFACTOR) looks like with CORTEX gates, and how the detect→fix→rescan convergence loop (CORE-068) works — including when it loops and when it closes. Show realistic, plausible outputs only. The tone is a staff engineer's internal tech talk: precise, honest about trade-offs, zero hype. Use only the provided sources, and ensure all visual generation uses a persistent ECG heartbeat motif that shifts colors based on the TDD phase (RED/GREEN/BLUE), overlaid on a Dark-blue glassmorphism theme."

---

## Ground-truth constraints
- Test-first contract: a failing test must exist before any implementation. No exceptions.
- Convergence gate: detect→fix→rescan loop runs until critical and high violations = 0 AND baseline test count maintained. Maximum 3 cycles — if exhausted, surfaces remaining issues and blocks completion.
- Test tiers (use exact commands):
  - `make test-changed` — runs only tests covering changed files. Test-first inner loop.
  - `make test-smoke` — preflight + core, <60 seconds. Pre-commit sanity.
  - `make test` — full unit suite, parallel. Daily dev.
  - `make test-parallel` — xdist, pre-commit full speed.
- CORTEX does NOT claim "no bugs" — it claims: *systematic validation, repeatable process, fail fast before deploy*.
- Any terminal output shown must be plausible, not fabricated metrics or fake coverage percentages.

---

## Visual ingredients
Upload as PNG/JPG:
1. `cortex-docs/assets/diagrams/05-diagram-workflow-tdd-cycle-and-fsm.md` — TDD FSM (Scenes 2–4)
2. `cortex-docs/assets/diagrams/04-diagram-audit-audit-fix-pipeline.md` — convergence pipeline (Scene 5)
3. `cortex-docs/assets/image-prompts/software-engineer/01-orchestrator-ecosystem-hero.prompt.md` — ecosystem map (Scene 1)

**Cinematic treatment — ECG heartbeat motif:**
A thin neon ECG line runs across the bottom of every frame throughout this video. Its colour and rhythm reflect the current TDD phase:
- RED phase: red neon (#ff4757), fast erratic pulse — the test is failing, the system is alert
- GREEN phase: green neon (#2ecc71), steady even pulse — implementation passes, system stable
- REFACTOR phase: blue neon (#00d4ff), slow calm pulse — improvement in progress
- Convergence loop: amber neon (#f5a623), cycling pulse — detect → fix → rescan iterating
- AC_COMPLETE: white neon flatline then a single long green pulse — done

This ECG line is the defining visual of SE-01. It is NOT used in any other video.

---

## Scene-by-scene breakdown

**SCENE 1 — "The Engineer's Problem" [0:00–1:30]**
Visual: A commit history — 14 commits. Three of them have red ❌ markers added at the bottom (post-deploy regressions found). Each red marker has a timestamp: 2 hours after deploy, 5 hours after deploy, next morning.
No CORTEX yet. ECG line is flat — not yet active.
Narrator (female, staff-engineer tone): *"Regressions found after deploy cost more than regressions found at commit. Not marginally more — orders of magnitude more. The question isn't whether to validate — it's where in the cycle."*
ECG line ignites — starts a neutral amber pulse as CORTEX enters the picture.

**SCENE 2 — "Failing Phase: The Test First Contract" [1:30–4:30]**
ECG shifts to RED neon — fast pulse.
Visual: Code panel (glassmorphic, JetBrains Mono, dark background). Test file opens. Test function types character by character with a red bioluminescent cursor trail:

```python
def test_payment_rate_limit_blocks_excess_requests():
    client = TestClient(app)
    for _ in range(5):
        client.post("/payment", json={"amount": 100})
    response = client.post("/payment", json={"amount": 100})
    assert response.status_code == 429  # Too Many Requests
```

`make test-changed` executes. RED ❌ failure output appears as a holographic glitch card:
  `FAILED test_payment.py::test_payment_rate_limit_blocks_excess_requests - AssertionError`
The failure card pulses red. ECG flatlines briefly, then resumes red pulse — proof the test is real.

CORTEX test-first gate card materialises: `TEST-FIRST GATE: Failing test confirmed. Implementation permitted.`
Narrator: *"That failure is not a problem. It's proof. The test is real, the requirement is real, and you'll know when the implementation passes for the right reason — because the test told it to."*

Cinematic: Camera does a push-in on the failure message, then pull-back as the gate card lights green. The YAML governance rule appears briefly: the rule name and gate description visible — no internal code numbers shown.

**SCENE 3 — "Passing Phase: The Minimum That Satisfies" [4:30–7:00]**
ECG shifts to GREEN neon — steady pulse.
Visual: Implementation file opens. Minimal rate-limiting middleware types with a green cursor trail. No over-engineering — only what the test demands.
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/payment")
@limiter.limit("5/minute")
async def payment_endpoint(request: Request, ...):
    ...
```

`make test-changed` runs. GREEN ✅. Bioluminescent green particle rise — sparks from test output, fade upward.
ECG holds steady green. Heartbeat calm.
Narrator: *"Minimum implementation. Not the cleverest solution — the simplest one that makes the test pass. You don't refactor before passing. That's the contract."*
Stage tracker card: `Failing ✓ → Passing ✓ → Refactor ⚪`

**SCENE 4 — "Refactor Phase: Improve Without Fear" [7:00–9:00]**
ECG shifts to BLUE neon — slow, confident pulse.
Visual: Code restructuring — `PaymentRateLimiter` class extracts from the inline decorator. Panels rearrange with glassmorphic slide animations (detach, reposition, re-seal). New unit tests for edge cases type with a blue cursor trail.
`make test-changed` — all GREEN ✅. ECG holds blue, steady.
Narrator: *"Refactoring is safe because the test didn't change. You can restructure the code aggressively — the test is the contract, and it didn't move. This is the confidence that test-first development actually buys you."*
Stage tracker card: `Failing ✓ → Passing ✓ → Refactor ✓`

**SCENE 5 — "The Convergence Gate: Detect → Fix → Rescan" [9:00–12:30]**
ECG shifts to AMBER neon — cycling pulse.
Visual: `/audit fix` runs. The 9-stage convergence pipeline materialises as a vertical neon track. Stages activate sequentially.
Violation catalogue emerges as a glassmorphic table:
  `High | Type hints missing on payment_endpoint | add: Request, PaymentRequest → Response`
  `High | PaymentRateLimiter docstring missing | add docstring to __init__`

Iteration 1: Fix applied — type hints added, docstring written. Rescan runs.
Violation counter: `2 → 0`. Stage 9 illuminates green. Completion badge materialises with timestamp.

Narrator: *"The loop doesn't close until the count is zero — not until 'most' violations are fixed. Not at 'good enough'. At zero. If the loop exhausts three cycles without reaching zero, CORTEX surfaces the remaining issues and blocks completion. You decide whether to override. The system doesn't hide it."*

Cinematic: Violation counter holographically descends `2 → 0`. Each decrement: a small red particle fragment dissolves. At 0: ECG line shifts from amber to white flatline, then a single long green pulse. Completion badge glows.

**SCENE 6 — "Test Tier Selection" [12:30–End]**
ECG returns to neutral cyan — steady background hum.
Visual: Four command cards materialise as a 2×2 grid, each with a speed gauge and scope indicator:
  `make test-changed` — ⚡ fastest · scope: files you touched · use: every save during TDD
  `make test-smoke` — 🔵 <60s · scope: preflight + core · use: before every commit
  `make test` — 🟢 full suite · scope: all unit tests, parallel · use: daily baseline
  `make test-parallel` — ⚡⚡ fastest full · scope: all, xdist · use: pre-commit at full speed

Narrator: *"These aren't four different tools. They're one tool at four zoom levels. During the test-first loop you live in 'changed'. Before you push, you run smoke. The full suite is your team's daily truth. Parallel is when you need speed without losing coverage."*
Final lower-third: `"Systematic validation. Fail fast. Ship with confidence."`

---

## Audio direction
- ECG foley: subtle heartbeat rhythm that physically changes tempo/timbre with TDD phase — this is the audio signature of this video
- RED phase: faster, slightly anxious electronic pulse
- GREEN phase: even, calm electronic heartbeat
- REFACTOR phase: slow, almost meditative pulse
- Convergence loop: cycling amber rhythm — loop sound design (iterate and resolve)
- AC_COMPLETE: brief silence, then a single clean resonant tone

---

## Production note
Use NotebookLM for narrative + architecture slides. The code panels in Scenes 2–4 should use actual Python patterns plausible for FastAPI rate-limiting — not invented APIs. For the convergence loop in Scene 5, record a real `/audit fix` run against the CORTEX repo and screenshot the violation table (redact any sensitive paths). The ECG line can be an animated SVG overlay.
