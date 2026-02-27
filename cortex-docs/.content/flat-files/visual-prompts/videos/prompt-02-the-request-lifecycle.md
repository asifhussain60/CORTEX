# Video Prompt 02 — The Life of a Request

> **Duration:** 8 minutes · **Audience:** Product Owners, Software Engineers
> **Depth:** 🟡 Product-level — shows the journey, light architecture
> **No overlap:** Image prompt-07 shows a static journey map; this video *animates* a real request flowing through every stage in real-time

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).

---

## PROMPT

Create an 8-minute animated explainer video titled **"The Life of a Request"** using the visual identity above. Track a single user request as a glowing cyan particle that travels through CORTEX's entire processing pipeline.

### Scene 1 — The Request Is Born (0:00 – 1:00)

**Open on:** A glassmorphic text input field centered on the `#0a0e27` void. A cursor blinks in JetBrains Mono.

- Text types in character-by-character: `"Add input validation to the user registration form"`
- When the user presses Enter, the text compresses into a **glowing cyan sphere** — the Request Particle.
- The particle hovers, then a glass pipeline materializes below it — a long translucent tube with 7 station chambers.

**Daily-life analogy overlay** (`#a0a6c0`): *"Think of mailing a package — it enters the postal system, gets sorted, routed, inspected, and delivered. Your request takes the same journey."*

**Narration:** "Every interaction with CORTEX starts the same way — a request. Let's follow one through the entire system."

### Scene 2 — Station 1: Intent Classification (1:00 – 2:00)

The cyan sphere enters the first glass chamber. Inside:

- **IntentRouter** appears as a rotating prism. The sphere enters one side; colored light fans out the other side.
- The prism analyzes the sphere — holographic labels flash: `IMPLEMENT? FIX? REFACTOR? AUDIT?`
- The label `IMPLEMENT` locks in with a cyan flash and chime.
- A routing tag attaches to the sphere like a luggage tag: `intent: IMPLEMENT`

**Inside the chamber**, show the HEXA-MODE selector — six glassmorphic hexagonal tiles arranged in a honeycomb. The `IMPLEMENT` hex glows cyan; the others remain dim.

**Analogy overlay:** *"Like a hospital triage nurse — they assess the urgency and route you to the right specialist."*

**Narration:** "The IntentRouter examines the request and classifies it. This determines which orchestrators will handle it."

### Scene 3 — Station 2: Orchestrator Selection & LENS Scan (2:00 – 3:30)

The tagged sphere exits Station 1 and enters Station 2 — a larger chamber with a rotating ring of 51 small glowing orbs (the orchestrators).

- The `IMPLEMENT` tag acts as a magnet — 3-5 orchestrators light up and detach from the ring, forming a **task chain**.
- Show: `MasterOrchestrator → TDDOrchestrator → EnforcementOrchestrator` linked by cyan connection lines.
- Simultaneously, a **LENS scanning beam** (the diagnostic eye from image prompt-03, but animated) sweeps across a miniature codebase panel on the right side.
- LENS results appear as floating data cards: file count, test coverage %, dependency map. Each card slides in with a glass panel effect.

**Analogy overlay:** *"The restaurant manager reads the order ticket, assigns the chef, prep cook, and quality inspector — then checks the pantry for ingredients."*

**Narration:** "CORTEX selects the right orchestrators for the job and scans the workspace for context. No guesswork."

### Scene 4 — Station 3: TDD — Test First (3:30 – 5:00)

The sphere enters Station 3 — a chamber styled like a heartbeat monitor.

**Three-phase animated sequence:**

1. **RED Phase** — The sphere turns red (`#ff4444`). A test file materializes in a glass code panel (JetBrains Mono). The test runs — a red X appears. The heartbeat line shows a red peak.
   - Code panel shows: `def test_validate_email():` → `assert validate_email("bad") == False` → ❌ `FAIL`
   - **Analogy text:** *"Write the exam questions before studying — now you know exactly what to learn."*

2. **GREEN Phase** — The sphere shifts to green (`#00ff88`). An implementation file appears next to the test. Minimum code types in. The test reruns — green ✅ appears. Heartbeat shows green peak.
   - Code panel shows: `def validate_email(email):` → implementation → ✅ `PASS`
   - **Analogy text:** *"Study just enough to pass the exam — no wasted effort."*

3. **REFACTOR Phase** — The sphere shifts to blue (`#3b82f6`). The implementation code reshuffles — cleaner variable names, extracted helper. Tests rerun — still green ✅. Heartbeat shows blue peak.
   - **Analogy text:** *"Now clean your desk while keeping everything working."*

The heartbeat line continues pulsing: red-green-blue, red-green-blue — the TDD rhythm.

**Narration:** "CORE-008: write the test first. Always. The RED-GREEN-REFACTOR cycle is CORTEX's heartbeat."

### Scene 5 — Station 4: Governance Gate (5:00 – 6:00)

The sphere exits TDD and approaches a translucent **shield barrier** spanning the pipeline. The shield shimmers with 38 tiny rule badges embedded in it.

- The sphere approaches — rule badges light up one by one as they check:
  - `CORE-011 Type Hints` → ✅ green flash
  - `CORE-012 Docstrings` → ✅ green flash
  - `CORE-028 File Naming` → ✅ green flash
  - `CORE-008 TDD` → ✅ green flash (already passed)
  - Show 34 more in rapid succession — a cascade of green flashes.
- The shield opens (panels slide apart) and the sphere passes through.

**Alternate scenario** (brief 10-second branch): Show what happens if a rule fails — `CORE-011` badge turns red, shield stays closed, sphere bounces back. An `EnforcementOrchestrator` tag attaches: `violation: missing type hints`. The sphere loops back to Station 3 for a fix.

**Analogy overlay:** *"Airport security — every bag gets scanned. If something's wrong, you go back and fix it before boarding."*

### Scene 6 — Station 5: Commit & Integration (6:00 – 7:00)

The sphere (now glowing green after passing governance) enters the final chamber — a **git timeline** rendered as a glassmorphic horizontal rail.

- Previous commits appear as smaller spheres on the rail — a history line.
- The new sphere merges into the rail with a satisfying snap and cyan pulse.
- A conventional commit message materializes: `feat(auth): add email validation to registration form`
- AC markers appear:
  ```
  AC_START: AC-IMPLEMENT-20260227T143022
  ...
  AC_COMPLETE: AC-IMPLEMENT-20260227T143022 ✅ (2,340ms)
  ```
- These markers flow into a miniature SQLite database icon — activity logging.

**Analogy overlay:** *"The package arrives at its destination — signed, sealed, delivered, and logged in the ledger."*

### Scene 7 — The Big Picture (7:00 – 8:00)

**Camera pulls back** to show the entire pipeline from above — all 7 stations in a row, connected by the glowing tube.

- Multiple spheres are now flowing through simultaneously — different colors for different intent types (cyan=IMPLEMENT, purple=REFACTOR, amber=FIX, red=AUDIT).
- Some spheres bounce back at the governance gate and loop through TDD again.
- The system is alive — a flowing, self-correcting pipeline.

**Final text** (Space Grotesk, large):
**"Every request. Classified. Tested. Governed. Delivered."**

**Stats overlay** (glassmorphic card):
- 51 orchestrators available
- 38 governance rules enforced
- 28 MCP tools at the ready
- Zero manual steps required

Logo watermark pulses once. End card with CORTEX logo and URL.

---

## Notes

- Image prompt-07 shows a **static** journey map (stations as waypoints). This video **animates the particle flowing through each station in real-time** — completely different visual treatment.
- The Request Particle is the visual thread — viewers follow ONE object through the entire system.
- Code panels show realistic but simple Python — enough to understand, not enough to overwhelm.
- Each station has its own ambient sound texture layered on top of the base synth pad.
- Transition between stations: sphere exits one glass chamber → travels through connecting tube → enters next chamber.
