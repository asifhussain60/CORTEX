# NotebookLM Video Prompt — PO-01 — Sprint Intelligence: What CORTEX Means for Delivery

**Target length:** 7–9 minutes
**Audience:** Product Owners, Delivery Leads, Scrum Masters — people who track velocity, DoD, and regression risk
**Narrator gender:** Male (PO-01 — even sequence in series, per VBP-017)
**Visual theme:** Dark-blue glassmorphism · Sprint board metaphor · Gold #FFD700 for milestone moments
**Series position:** Delivery outcomes — the only video translating CORTEX into sprint/product language

---

## ⚠️ ZERO-OVERLAP DECLARATION
This video exclusively owns:
- Sprint-board delivery metaphor (feature card moving from Backlog → Done)
- Golden tests as acceptance criteria in plain business language
- The PO definition of "done": zero P0/P1 violations AND tests green
- Safe adoption path: start with smoke + changed-tests, expand gradually

Does NOT repeat: what CORTEX is (Video 01), architecture internals (Video 03), engineering TDD mechanics (SE videos).

---

## Steering Prompt
*Paste into NotebookLM → Customize → Steering Prompt:*

> "Create a 7–9 minute explainer for product owners, scrum masters, and delivery leads. Focus entirely on delivery outcomes: what does CORTEX mean for Definition of Done, sprint predictability, regression risk, and adoption safety? Do not explain orchestrator architecture. Do not invent ROI metrics or percentages. Use a calm delivery-lead voice — practical, outcomes-focused, honest about what CORTEX does and does not automate. Use only the provided sources."

---

## Ground-truth constraints
- Frame everything in delivery language: sprint, DoD, acceptance criteria, regression, handoff, velocity
- Golden tests = acceptance criteria authored in plain English, validated by CORTEX gates
- CORTEX enforces TDD-first (CORE-008) and sweep completeness (CORE-064) — use business translations:
  - CORE-008: *"a failing test must exist before any implementation begins"*
  - CORE-064: *"when an issue pattern is found, all instances are fixed — not just the reported one"*
- No invented percentages. No invented ROI numbers.
- Safe adoption framing: smoke tests + changed-tests loop is the lowest-risk entry point

---

## Visual ingredients
Upload as PNG/JPG:
1. `cortex-docs/assets/diagrams/03-workflow-sdlc-pipeline.md` — SDLC pipeline (Scene 2)
2. `cortex-docs/assets/diagrams/07-testing-testing-strategy-pyramid.md` — test pyramid (Scene 3)
3. `cortex-docs/assets/image-prompts/product-owner/01-sprint-intelligence-dashboard.prompt.md` — sprint view (Scene 4)
4. `cortex-docs/assets/image-prompts/product-owner/03-dor-dod-compliance.prompt.md` — DoD compliance (Scene 5)

**Cinematic treatment — Sprint board metaphor:**
The persistent background is a glassmorphic sprint board: columns Backlog → In Progress → In Review → Done. A feature card (`feat: rate-limiting`) travels across the board throughout the video as CORTEX stages complete. The card only enters "Done" when violations = 0. This card is the visual anchor of the entire video.

---

## Scene-by-scene breakdown

**SCENE 1 — "The Estimation Problem" [0:00–1:30]**
Visual: A sprint planning card appears: estimated 3 days, actual 11 days. Three late-night red timeline markers. A post-mortem comment card: *"Found regression in payment service at deploy time."*
No CORTEX yet. Just the pain.
Narrator (male, delivery-tone): *"Estimation fails when surprises are baked into the process. CORTEX doesn't eliminate surprises — it moves them earlier, where they're cheaper."*
Sprint board materialises in the background — the feature card sits in Backlog, dormant.

**SCENE 2 — "What Changes with CORTEX" [1:30–4:00]**
Visual: SDLC pipeline diagram — but narrated entirely in PO language, not engineering language:
  Gate 1 — "Is the acceptance criterion defined?" (golden test)
  Gate 2 — "Is a failing test written before code?" (TDD gate — plain language: "proof the feature was needed")
  Gate 3 — "Does the implementation pass?" (green tests)
  Gate 4 — "Does the full codebase still pass?" (smoke tests)
  Gate 5 — "Does it satisfy the governance rulebook?" (compliance check)
  Gate 6 — "Is the loop closed?" (zero critical violations)
The sprint board card advances one column for each gate that turns green.
Narrator: *"Each gate is a question your team already asks — CORTEX just makes sure the question gets answered before the code moves, not after."*

**SCENE 3 — "The Testing Pyramid — A PO's View" [4:00–5:30]**
Visual: Test pyramid diagram — but each tier annotated in business language:
  Base (Unit/Changed): `"Fast signal — catches breaks in seconds, not hours"`
  Middle (Smoke): `"Sprint confidence — runs in under 60 seconds before any commit"`
  Top (Integration/Golden): `"Acceptance proof — your DoD in code form"`
Narrator: *"Golden tests are your acceptance criteria — written in code, validated automatically on every commit. When golden tests are green, the feature behaves exactly as specified."*
One golden test materialises as a glassmorphic card: `test_payment_rate_limit_blocks_excess_requests` — plain English intent visible as a comment above the assertion.

**SCENE 4 — "A Sprint Story" [5:30–7:00]**
Visual: Feature card travels the board in real-time sequence with timestamps:
  Monday 9am — card enters In Progress. Golden test written: RED (by design). `"1 failing test — expected"`
  Monday 2pm — implementation complete. GREEN. `"Tests pass. Feature earns its place."`
  Monday 3pm — smoke tests run. GREEN. `"Codebase still intact."`
  Monday 4pm — `/audit fix` runs. 2 violations found. Fixed. Rescanned. 0 violations. AC_COMPLETE.
  Monday 4:30pm — card enters Done. No surprises.
Narrator: *"The feature took half a day — and arrived clean. Not because the team worked faster. Because the process eliminated the rework loop."*

**SCENE 5 — "Safe Adoption" [7:00–End]**
Visual: Three adoption tiers materialise as glassmorphic steps (progressive, not overwhelming):
  Step 1: `make test-smoke` — run after every commit. Entry cost: near-zero.
  Step 2: `make test-changed` — TDD inner loop, testmon-powered. Runs only what changed.
  Step 3: Full `/audit fix` — pre-release or sprint close. Full convergence.
Narrator: *"You don't adopt CORTEX all at once. Start with the smoke test. Add the changed-test loop. When your team trusts those, the full audit becomes a natural sprint-close ritual — not an interruption."*
Final card: `"Fewer surprises. Clearer done. Safer handoffs."` Fade.

---

## Audio direction
- Ambient: subtle office ambience (keyboard clicks, low murmur) under Scenes 1–2
- Score: minimal uplift (not cinematic) — enter only at Scene 5 adoption path, quiet
- No dramatic music. This is a delivery conversation, not a keynote.

---

## Production note
Use NotebookLM for narrative + sprint-board slide generation. The sprint board card progression is the key visual — if NotebookLM cannot animate it, treat each card position as a separate slide with a timestamp callout. The golden test card in Scene 3 should be a real test name from the CORTEX repo (e.g., from `tests/golden/`).
