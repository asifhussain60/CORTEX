# Tutorial 03 — Building a Feature End-to-End

> **Duration:** ~9 minutes · **Audience:** Software Engineers ready to build
> **Visual Theme:** 🟠 Warm amber/gold glassmorphism (tutorial accent)
> **Prerequisite:** Tutorials 01–02 complete
> **Goal:** Viewer builds a complete feature using TDD, governance, and audit — the full CORTEX workflow

---

## ⚠️ VISUAL IDENTITY — TUTORIAL THEME

> See tutorials `README.md` for amber/gold palette and tutorial visual rules.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the steps or the code.** Every narration line must add something the viewer cannot get from reading the screen: the *why it matters*, the *gotcha to watch for*, the *non-obvious implication*, or the *discipline behind the mechanic*. See tutorials `README.md` §Narration Philosophy for full guidance and examples.

---

## CINEMATIC SIMULATION NOTES — T03: Building a Feature End-to-End

### Visual Physics & Ambience Protocol (Tutorial Amber Theme)
- **Environment:** Dark-blue vacuum (#0a0e27) with ray-traced reflections on glass floor
- **Accent neon:** Warm amber (#f5a623) for step borders and progress; RED (#ff4757) / GREEN (#2ecc71) / BLUE (#00d4ff) for TDD phase heartbeat
- **Code panels:** Frosted glassmorphism with 3px amber left border, JetBrains Mono at readable size; active line highlighted with amber glow
- **ECG heartbeat:** Thin neon line across bottom of frame — pulses RED during failing tests, GREEN during passing, BLUE during refactor (callbacks to Video 04 concept)
- **Lighting:** Volumetric fog, ray-traced caustics from TDD phase colors, bioluminescent test particles
- **Feedback cues:** RED flash = test failure (expected in TDD), GREEN flash = test pass, holographic glitch = governance violation, Lidar sweep = LENS scan
- **Temporal evolution:** Environment evolves through TDD phases: dim red (RED phase) → warm green (GREEN phase) → cool blue (REFACTOR) → amber (governance) → full amber luminosity (commit)

**SCENE 1 — "The Awakening" (0:00–0:04)**
Camera: Static center-frame, locked on ray-traced glassmorphism floor.
Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric amber fog at ground level.
CORTEX logo fades in as hero image with amber electric-aura. Hold 3s. Logo shrinks to
bottom-right watermark with amber "TUTORIAL" label. ECG heartbeat line ignites across
bottom of frame — flat amber line, waiting for TDD to begin.

**SCENE 2 — "The Scenario" (0:04–0:30)**
Camera: Slow dolly-in toward a glassmorphic brief card assembling with time-lapse
mechanical construction. Feature description materializes with particle condensation:
"Add input validation to a user registration endpoint." Stack badges (Python, FastAPI)
glow with amber neon. Workflow preview appears as a faint holographic roadmap beneath:
TEST → IMPLEMENT → REFACTOR → GOVERN → LENS → AUDIT → COMMIT — seven stations,
all dim, waiting to illuminate.

**SCENE 3 — "RED Phase: Write the Test First" (0:30–2:00)**
Camera: Slow dolly-in to code panel. ECG heartbeat shifts to RED neon (#ff4757) —
pulsing rhythm. Volumetric red fog rises at floor level.
Code panel materializes with time-lapse assembly — amber left border, JetBrains Mono.
Test code types character by character with bioluminescent red cursor trail. Each line
of assertion code gains a subtle red neon underline.
`make test-changed` executes — RED ❌ failure output with holographic glitch effect.
The failure message floats as a holographic card with ray-traced red glass surface.
ECG heartbeat flatlines briefly, then resumes red pulse — the test is real.
Workflow roadmap: "TEST" station illuminates red.

**SCENE 4 — "GREEN Phase: Implement the Minimum" (2:00–3:30)**
Camera: Tracking shot, code panel scrolls. ECG heartbeat transitions RED → GREEN
(#2ecc71) with a color-shift wave along the neon line.
Implementation code types with green cursor trail. Pydantic model assembles —
`EmailStr` highlights with green neon emphasis (this is the key validation).
`make test-changed` executes — GREEN ✅. Bioluminescent green particle celebration:
sparks rise from the test output and fade. ECG heartbeat pulses steady green.
Ray-traced green caustics ripple across the glass floor.
Workflow roadmap: "IMPLEMENT" station illuminates green.

**SCENE 5 — "REFACTOR Phase: Improve with Confidence" (3:30–4:30)**
Camera: Slow dolly-out with parallax shift. ECG heartbeat transitions to BLUE (#00d4ff).
Volumetric blue fog replaces green.
Code refactors: `InputValidator` class materializes — code blocks rearrange with
smooth glassmorphic slide animations (panels detach, reconfigure, and re-seal).
New test methods appear with blue cursor trail. `make test-changed` — all GREEN ✅.
ECG heartbeat pulses blue — stable, confident rhythm.
Workflow roadmap: "REFACTOR" station illuminates blue.

**SCENE 6 — "Governance Validation" (4:30–5:30)**
Camera: Pull-back to workspace view. ECG returns to amber (tutorial accent).
`/audit` runs — governance check results materialize as glassmorphic cards:
✅ checks appear with green flash, ⚠️ warning appears with holographic glitch
(missing edge case test). The warning card pulses amber — not red (it's a catch,
not a failure).
Fix: additional test types with amber cursor trail. Re-run governance: all GREEN ✅.
Holographic glitch clears — steady amber glow replaces it.
Workflow roadmap: "GOVERN" station illuminates amber.

**SCENE 7 — "LENS Intelligence" (5:30–6:15)**
Camera: Macro zoom on LENS scan output panel.
LENS beam sweeps across the codebase (Lidar scan animation — amber laser line sweeps
left to right). Pattern detection cards materialize with particle condensation:
"Validator pattern (0.87)" floats as holographic confidence badge with ray-traced
glass surface. Dependency check and coverage estimate appear as smaller holographic cards.
Bioluminescent knowledge particles flow from LENS scan into the pattern card,
brightening it — particle evolution from dim amber to rich gold.
Workflow roadmap: "LENS" station illuminates gold.

**SCENE 8 — "Full Audit Fix" (6:15–7:30)**
Camera: Slow orbital drift around the workspace.
`/audit fix` runs — 9-stage pipeline materializes as vertical track (amber neon,
tutorial identity). Each stage illuminates sequentially with amber pulse → green
completion flash. Ray-traced caustics cascade from each stage to the next.
Convergence counter: holographic "1 iteration → 0 violations" with green flash.
AC_COMPLETE badge materializes with holographic shimmer and amber glow.
Workflow roadmap: "AUDIT" station illuminates green.

**SCENE 9 — "The Commit" (7:30–8:15)**
Camera: Dolly-in to terminal panel.
`git commit` command with conventional message types — commit message is visible
through frosted glass with amber neon emphasis on the `feat(auth):` prefix.
Pre-commit hook fires: governance rules flash green in rapid sequence (Lidar sweep).
Commit accepted — green flash with bioluminescent celebration particles.
Git timeline materializes as a glassmorphic horizontal track — the new commit glows
amber at the head, previous commits dim behind it with parallax depth.
Workflow roadmap: "COMMIT" station illuminates green — all 7 stations now lit.

**SCENE 10 — "The Complete Workflow" (8:15–9:00)**
Camera: 360-degree orbital pan at 30° downward angle with parallax depth.
Full workflow roadmap now fully illuminated: TEST (red→green) → IMPLEMENT (green) →
REFACTOR (blue) → GOVERN (amber) → LENS (gold) → AUDIT (green) → COMMIT (green).
ECG heartbeat pulses steady green — healthy, complete. All glassmorphic panels and
code panels visible in the background with ray-traced reflections creating depth.
Glassmorphic completion card assembles — workflow steps listed with checkmarks.
Amber arrow with particle trail: "Tutorial 4 →"
Fade to black with ECG flatline (gentle, not dramatic) and ray-traced reflections dimming.

---

## PROMPT

Create a ~9-minute tutorial video titled **"Building a Feature End-to-End"** using the amber/gold tutorial theme. Walk through implementing a real feature from request to commit using CORTEX's full engineering discipline.

### Intro — The Scenario (0:00 – 0:30)

**Glassmorphic brief card:**

> **Feature:** Add input validation to a user registration endpoint
> **Stack:** Python (FastAPI)
> **What we'll use:** TDD (RED-GREEN-REFACTOR), governance validation, LENS scan, audit fix, conventional commit

**Narration:** "Notice the scenario: not 'hello world.' A real feature, a real stack, real governance requirements. Everything you're about to see applies directly to production work."

### Step 1 — Start with the Test (0:30 – 2:00)

**CORE-008 in action.** Code panel with amber border.

**Write the test FIRST:**
```python
def test_registration_rejects_invalid_email():
    """Registration endpoint should reject malformed email addresses."""
    response = client.post("/register", json={
        "email": "not-an-email",
        "username": "validuser",
        "password": "SecureP@ss123"
    })
    assert response.status_code == 422
    assert "email" in response.json()["detail"][0]["loc"]
```

**Run the test:**
```bash
make test-changed
```

**Result:** RED ❌ — test fails because the validation doesn't exist yet.

**ECG heartbeat pulses red.**

**Dark pill:** *"The test defines the behavior we WANT. It fails because the code doesn't exist yet. This is the discipline — test first, always."*

**Narration:** "That red failure is a good sign. It means the test is real — it will actually tell you something when the implementation exists. A test that passes before you've written anything is not a test."

### Step 2 — Implement the Minimum (2:00 – 3:30)

**Write just enough code to pass:**

```python
from pydantic import BaseModel, EmailStr

class RegistrationRequest(BaseModel):
    email: EmailStr  # Pydantic validates email format
    username: str
    password: str

@app.post("/register")
async def register(request: RegistrationRequest):
    # ... registration logic
    return {"status": "registered"}
```

**Run the test again:**
```bash
make test-changed
```

**Result:** GREEN ✅ — test passes.

**ECG heartbeat pulses green.**

**Narration:** "Resist the urge to write more. The test is the contract — it defines exactly what 'done' means. Writing beyond the test means writing beyond your proof of correctness."

### Step 3 — Refactor with Confidence (3:30 – 4:30)

**Now improve the code** knowing the test protects you:

- Extract validation into a separate validator class
- Add password strength validation
- Add username format validation
- Add type hints and docstrings (governance requirements)

```python
class InputValidator:
    """Validates registration input against business rules."""

    @staticmethod
    def validate_password(password: str) -> list[str]:
        """Check password meets security requirements."""
        errors: list[str] = []
        if len(password) < 12:
            errors.append("Password must be at least 12 characters")
        # ... additional checks
        return errors
```

**Add more tests for the new validations. Run:**
```bash
make test-changed
```

**Result:** All GREEN ✅. ECG pulses blue (refactor phase).

**Narration:** "This is the refactor phase's secret: you're not adding features. You're improving the code for the next person who reads it — which might be you in three months."

### Step 4 — Governance Validation (4:30 – 5:30)

**Run the governance check:**
```bash
/audit
```

**Show what governance checks:**
- ✅ Type hints on all functions (CORE-011)
- ✅ Docstrings on public APIs (CORE-012)
- ✅ File naming: snake_case (CORE-028)
- ⚠️ Missing test for password validation edge case (detected by LENS)

**Fix the warning** — add the missing edge case test:

```python
def test_registration_rejects_weak_password():
    """Registration should reject passwords under 12 characters."""
    response = client.post("/register", json={
        "email": "user@example.com",
        "username": "validuser",
        "password": "short"
    })
    assert response.status_code == 422
```

**Re-run governance:** All GREEN ✅.

**Narration:** "The governance warning wasn't a failure. It was CORTEX catching an edge case you hadn't thought of yet. That's the system working correctly — not a disruption to your workflow."

### Step 5 — LENS Intelligence (5:30 – 6:15)

**LENS scan runs as part of the audit.** Show the findings:

- **Pattern detected:** Validator pattern (0.87 confidence) — matches enterprise pattern library
- **Suggestion:** Consider Strategy pattern for extensible validation rules
- **Dependency check:** `pydantic` version is current, no known CVEs
- **Coverage estimate:** New code is 94% covered by tests

**Dark pill:** *"LENS doesn't just check syntax. It understands architecture patterns and suggests improvements based on your codebase's history."*

**Narration:** "A confidence score of 0.87 on a pattern means LENS has seen enough evidence to be certain this pattern is present — not just that a few signatures matched. That's what makes the suggestion trustworthy rather than speculative."

### Step 6 — Full Audit Fix (6:15 – 7:30)

**Run the complete pipeline:**
```
/audit fix
```

**Show each stage progressing** (amber progress bar):
- Environment ready ✅
- Governance pre-flight ✅
- Production scan ✅ — 0 violations
- Wiring validation ✅
- Health checks ✅
- Vacuum ✅ (nothing to clean)
- Meta-audit ✅
- Convergence: 1 iteration, 0 violations → exit
- Tests: all passing ✅

**AC markers visible:** `AC_START` → `AC_COMPLETE ✅ (2,847ms)`

**Narration:** "Zero violations. That's not luck — it's the result of running governance checks throughout the workflow rather than saving them for the end."

### Step 7 — Commit (7:30 – 8:15)

**Conventional commit message:**
```bash
git add .
git commit -m "feat(auth): add input validation to registration endpoint

- Email format validation via Pydantic EmailStr
- Password strength enforcement (12+ chars, complexity)
- Username format validation
- Full test coverage with edge cases
- LENS pattern: Validator (0.87 confidence)"
```

**Pre-commit hook fires** — governance rules validate one final time. Green. Commit accepted.

**Show the commit in the git timeline** — clean, descriptive, traceable.

**Narration:** "The commit message isn't documentation overhead. It's the audit trail entry that tells the next engineer — or the next you — exactly what changed and why the LENS pattern score was relevant."

### Step 8 — Recap: The Complete Workflow (8:15 – 9:00)

**Glassmorphic workflow summary:**

```
1. Write test (RED)        → Defines expected behavior
2. Implement (GREEN)       → Minimum code to pass
3. Refactor (BLUE)         → Improve with test safety net
4. Governance check        → Standards enforced automatically
5. LENS analysis           → Pattern detection + suggestions
6. Audit fix               → Full production readiness scan
7. Commit                  → Pre-commit hook + conventional message
```

**Narration:** "Seven steps. One feature. Production-ready. This workflow doesn't feel slow once it's muscle memory — it feels like the only way you'd want to build."

**Next:** "Tutorial 4 — Onboarding & Customization" (amber arrow)

---

## Notes
- This tutorial uses a REALISTIC feature (input validation) that every developer understands
- The code is intentionally simple — the focus is on the WORKFLOW, not the implementation complexity
- Every command is shown with real output
- The governance warning in Step 4 is deliberately included — it shows that CORTEX catches things you miss, which is the point
- ECG heartbeat visual from concept Video 4 makes a brief cameo — connecting the tutorial to the concept video
