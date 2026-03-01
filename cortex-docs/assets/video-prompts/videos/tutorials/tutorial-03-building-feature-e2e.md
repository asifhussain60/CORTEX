# NotebookLM Video Prompt -- Tutorial 03 -- Building a Feature End-to-End

**Target length:** ~9 minutes
**Audience:** Engineers who want to see a complete TDD + governance workflow from first test to passing audit
**Visual Theme:** Warm amber/gold glassmorphism (tutorial series accent) with ECG callback
**Prerequisite:** Tutorial 02 complete (command catalogue familiar)
**Narrator gender:** Female (T03 -- odd)
**Goal:** Viewer has built one real feature using the full CORTEX TDD + audit workflow

---

## ZERO-OVERLAP DECLARATION
This tutorial exclusively owns:
- The complete E2E workflow: failing test -> implementation -> governance gate -> audit fix -> AC_COMPLETE
- Showing a real FastAPI endpoint built under CORTEX governance from first keystroke to green audit
- The ECG callback: T03's ECG line is a deliberate visual callback to SE-01, acknowledging that the viewer now practices what SE-01 explained

Does NOT repeat: installation (T01), command catalogue (T02), multi-repo onboarding (T04), VS Code navigation (T05), chat workflow intro (T06), result interpretation (T07).

---

## Steering Prompt
Paste into NotebookLM Customize - Steering Prompt:

"Create a ~9 minute hands-on tutorial showing a complete CORTEX feature build end-to-end. Use a simple FastAPI endpoint as the example feature. Follow the exact TDD sequence: write the failing test first, run make test-changed, implement, run smoke test, then run /audit fix. Show convergence: what happens when the audit finds a violation, and how the loop closes. Narration must explain the discipline behind each step -- not read the code. Use only provided sources."

---

## NARRATION RULE -- MANDATORY
The narrator never reads code. Every line explains the discipline, the principle, or the consequence.

---

## Cinematic treatment -- "ECG Feature Build"

**Unique opening (ECG callback -- deliberate reference to SE-01 concept video):**
The environment is fully amber-lit. A thin neon line appears across the bottom of the frame -- amber coloured (tutorial palette, not SE-01's red/green/blue).
On-screen label: "If you've seen the TDD deep dive, you know this line."
A small SE-01 thumbnail appears briefly beside the ECG label -- a deliberate cross-reference.
The amber ECG line pulses once. On-screen: "Now we build."
This callback is intentional -- T03 is the practice video for the concepts in SE-01. Viewers who watched SE-01 will recognise the motif immediately.

The ECG line persists throughout T03:
- AMBER pulse (steady): planning phase
- RED pulse (sharp spike): test written and failing (correct)
- GREEN pulse (smooth wave): implementation passing
- BLUE flat then smooth: refactor complete
- WHITE long pulse: /audit fix passes, AC_COMPLETE logged

### Visual Physics
- Background: #0a0e27
- Accent: #f5a623 amber (tutorial) + ECG phase colours as above
- Code panels: frosted glassmorphism, amber border
- ECG line: 4px neon line, colour-shifts with phase, always visible

---

## Scene-by-scene breakdown

**SCENE 1 -- "The Feature Spec" [0:00-0:45]**
Amber ECG steady pulse. A single glassmorphic requirement card:
"Add a GET /status endpoint that returns the service version and uptime."
Narrator: "The spec is not the code. Before you write a single line, the test defines what done looks like. This is where TDD discipline begins -- and where most shortcuts happen."

**SCENE 2 -- "Write the Failing Test First" [0:45-2:30]**
ECG line shifts to RED (sharp spike). Code panel materialises:
```python
# tests/api/test_status_endpoint.py
def test_status_returns_version_and_uptime():
    response = client.get("/status")
    assert response.status_code == 200
    assert "version" in response.json()
    assert "uptime_seconds" in response.json()
```
Terminal: `make test-changed` -- test collected, FAILED. Red flash.
Narrator: "A failing test is not a problem. It is evidence that the test is real. If you run your test and it passes before you write any implementation, the test is not testing anything. The red state is the proof of work."
Lower-third: "CORE-008: tests before implementation, no exceptions."

**SCENE 3 -- "Implement to Green" [2:30-4:00]**
ECG shifts to GREEN (smooth wave). Implementation panel appears beside test panel:
```python
# cortex/api/status_endpoint.py
import time
START_TIME = time.time()

@router.get("/status")
async def get_status():
    return {
        "version": settings.VERSION,
        "uptime_seconds": int(time.time() - START_TIME)
    }
```
Terminal: `make test-changed` -- PASSED. Green flash.
Narrator: "Write the minimum implementation that makes the test pass. Nothing more. The refactor phase is where you improve it -- not now. Premature optimisation in the green phase breaks the discipline."

**SCENE 4 -- "Refactor" [4:00-5:00]**
ECG shifts to BLUE (flat then smooth). Code panel shows type hints and docstring added.
Terminal: `make test-changed` -- still PASSED.
Narrator: "Refactor with the test as your safety net. The test still passes -- that's the proof that refactoring didn't break the contract. This is what the green state is for: safe improvement."

**SCENE 5 -- "Smoke Gate" [5:00-5:45]**
`make test-smoke` -- progress bar fills amber. PASSED. ECG: white long pulse.
Narrator: "Before you run the full audit, run smoke. Smoke catches broad integration breaks faster than a full audit. If smoke fails, fix it before paying for the full 9-stage pipeline."

**SCENE 6 -- "/audit fix and Convergence" [5:45-8:00]**
`/audit fix` fires. 9-stage pipeline graphic. Stage 3 (governance): amber violation card appears:
"Missing type hint on get_status return annotation."
CORTEX fix applied. Rescan runs. Green cascade. Stage 9: AC_COMPLETE logged.
ECG: white steady line. Single long green pulse.
Narrator: "The audit found a violation. CORTEX fixed it, then rescanned. That is the convergence loop: detect, fix, rescan, repeat until zero P0/P1 violations remain. You don't manually fix and re-run -- the loop is automatic. Your job is to review the fix, not execute the loop."
Lower-third: "CORE-068: detect -> fix -> rescan until 0 P0/P1. Max 3 cycles."

**SCENE 7 -- "The Completed Feature" [8:00-End]**
All panels visible: test (green), implementation, audit (green), AC trace card.
ECG: stable white heartbeat.
Narrator: "One feature. One test. One audit. Every step traceable. That is a CORTEX workflow -- not perfect, but repeatable. Repeatable is what scales."
Outro card: "Next: Tutorial 04 -- Onboarding and Customisation"

---

## Audio direction
- ECG opening: soft amber pulse sounds, then the familiar sharp tick from SE-01 concept video (deliberate audio callback)
- RED phase: sharp spike sound
- GREEN phase: smooth ascending tone
- AC_COMPLETE: white long pulse + a clean, final bell tone (distinct from the amber chimes in T01)
- No cold start -- environment already lit

---

## Production note
The ECG callback is the most important creative choice in this tutorial. Do not replace it with a generic animation. Viewers who watched SE-01 will feel the connection immediately -- this is intentional cross-video continuity. The FastAPI code is minimal and plausible; do not add framework-specific boilerplate beyond what is shown.
