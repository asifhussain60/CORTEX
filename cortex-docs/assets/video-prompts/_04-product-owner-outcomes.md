# NotebookLM Video Prompt — PO-01 — Sprint Intelligence: What CORTEX Means for Delivery

**Target length:** 7–9 minutes
**Audience:** Product Owners, Delivery Leads, Scrum Masters — people who track velocity, DoD, and regression risk
**Narrator gender:** Male (PO-01 — even sequence in series, per VBP-017)
**Visual theme:** Dark-blue glassmorphism · Sprint board metaphor · Gold #FFD700 for milestone moments
**Series position:** Delivery outcomes — the only video translating CORTEX into sprint/product language

---

## 🎯 Identity Mission
This video is the **definitive delivery translation** for Product Owners, Scrum Masters, and Delivery Leads who own sprint predictability and face a recurring, costly pattern: features that pass engineering review but surface regressions at deployment — after the estimation window has already closed.

It addresses two compounding problems:

1. **Estimation failure** — surprises baked into the process inflate actual delivery time well beyond the forecast. The sprint board says Done; production says otherwise.
2. **An undefined Definition of Done** — when DoD shifts per sprint, per team, or per engineer, there is no stable bar to forecast against. Velocity becomes noise.

CORTEX solves this not by adding overhead, but by making the questions teams already ask — *"Is the acceptance criterion defined? Does the full codebase still pass? Is the loop closed?"* — mandatory gates that the code must clear before the card moves. Each gate is a question answered before the code moves, not after.

**The business translation is the entire point of this video:**
- **Golden tests** are acceptance criteria — authored in plain language, validated automatically on every commit.
- **CORE-008** means: *"proof the feature was needed must exist before a line of implementation is written."*
- **CORE-064** means: *"when an issue pattern is found, all instances are fixed — not just the one that was reported."*
- **"Done"** means: zero P0/P1 violations AND tests green — not "the developer says it works."

No architecture internals. No invented ROI numbers. Just delivery outcomes.

---

## ⚠️ ZERO-OVERLAP DECLARATION
This video exclusively owns:
- Sprint-board delivery metaphor (feature card moving from Backlog → Done)
- Golden tests as acceptance criteria in plain business language
- The PO definition of "done": zero critical violations AND tests green
- Azure DevOps work item integration: user stories pulled directly into developer context at the start of every feature — no copy-paste, no context loss
- Safe adoption path: start with smoke + changed-tests, expand gradually

Does NOT repeat: what CORTEX is (Video 01), architecture internals (Video 03), engineering test-first mechanics (SE videos), self-learning mechanics (Video 08).

---

## Steering Prompt
*Paste into NotebookLM → Customize → Steering Prompt:*

> "Select the Explainer format to create a 7–9 minute explainer for product owners, scrum masters, and delivery leads. Focus entirely on delivery outcomes: what does CORTEX mean for definition of done, sprint predictability, regression risk, Azure DevOps work item integration, and adoption safety? Do not explain orchestrator architecture or invent return-on-investment metrics. Use a calm delivery-lead voice — practical, outcomes-focused, and honest about what CORTEX does and does not automate. Frame technical concepts in business language, such as 'Golden tests' as acceptance criteria, and 'work item integration' as user stories automatically surfaced in the developer's editor. Use only the provided sources, and ensure visual generation uses a persistent glassmorphic sprint board metaphor with Dark-blue styling and Gold #FFD700 highlights for milestone moments."

---

## Ground-truth constraints
- Frame everything in delivery language: sprint, definition of done, acceptance criteria, regression, handoff, velocity
- Golden tests = acceptance criteria authored in plain English, validated by CORTEX gates
- CORTEX enforces test-first development and sweep completeness — use business translations:
  - Test-first: *"a failing test must exist before any implementation begins"*
  - Sweep completeness: *"when an issue pattern is found, all instances are fixed — not just the reported one"*
- Azure DevOps integration: `ADOWorkItemProvider` (`cortex/repositories/ado/ado_provider.py`) pulls user stories from Azure DevOps boards directly into developer context via the `cortex_fetch_work_items` tool — the developer sees the acceptance criteria without leaving VS Code
- No invented percentages. No invented return on investment numbers.
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

**SCENE 5 — "Azure DevOps: The Story Arrives With the Developer" [7:00–8:30]**
Visual: An Azure DevOps board card materialises — `"User Story: As a customer, I want rate limiting on the payment API so that my account is protected from abuse."` Acceptance criteria listed below.
The card travels as a neon packet from the board into VS Code — it docks into the developer's chat panel automatically. No copy-paste. No tab switching.
Lower-third: `"cortex_fetch_work_items — Azure DevOps user stories pulled into developer context"`
Narrator: *"When a developer picks up a card from Azure DevOps, CORTEX surfaces the acceptance criteria directly in their editor — without switching tools, without copy-pasting, without losing context. The story is there when they start. The golden test validates whether the story was delivered before the card moves to Done."*
Sprint board: the feature card stays in "In Progress" until the golden test is green. Only then does it advance.
On-screen callout: `"The story defines done. The test proves it."`

**SCENE 6 — "Safe Adoption" [8:30–End]**
Visual: Three adoption tiers materialise as glassmorphic steps (progressive, not overwhelming):
  Step 1: `make test-smoke` — run after every commit. Entry cost: near-zero.
  Step 2: `make test-changed` — test-first inner loop, runs only what changed.
  Step 3: Full audit and fix — pre-release or sprint close. Full convergence.
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
