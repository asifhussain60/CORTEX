# Video Prompt 02 — The Life of a Request

> **Duration:** 7 minutes · **Audience:** Product Owners, Software Engineers
> **Depth:** 🟡 Product-level — shows the journey, light architecture
> **No overlap:** Image prompt-05 shows a static journey map; this video animates a particle flowing through the pipeline in real-time

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> See `README.md` for full mandatory palette, motion style, text contrast rules, typography, and watermark.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the slide.** Every narration line must add something the viewer cannot get from reading the screen: the *why*, the *consequence*, the *non-obvious implication*, or the *emotional truth*. If a narration line restates visible text, cut it or rewrite it. See `README.md` §Narration Philosophy for full guidance and examples.

---

## PROMPT

Create a 7-minute animated explainer video titled **"The Life of a Request"**. Track a single user request as a glowing cyan particle traveling through CORTEX's processing pipeline.

### Scene 1 — The Request Is Born (0:00 – 1:00)

A glassmorphic text input. Cursor blinks. Text types: `"Add input validation to the user registration form"`. User presses Enter — text compresses into a **glowing cyan sphere**. A glass pipeline materializes below — a translucent tube with station chambers.

**Narration:** "Most AI tools stop at the answer. What you're about to see is what happens when an answer isn't enough — when quality, traceability, and correctness are non-negotiable."

### Scene 2 — Intent Classification (1:00 – 2:00)

Sphere enters the first chamber. **IntentRouter** appears as a rotating prism. The sphere enters one side; colored light fans out. Labels flash: `IMPLEMENT? FIX? REFACTOR? AUDIT? DEBUG?` — `IMPLEMENT` locks in with a cyan flash. A routing tag attaches like a luggage tag.

**Narration:** "The wrong orchestrator for the job is how AI systems produce plausible-sounding wrong answers. Routing is the first line of quality."

### Scene 3 — Orchestrator Selection & LENS Scan (2:00 – 3:30)

The tagged sphere enters a larger chamber with a ring of glowing orbs (orchestrators). The `IMPLEMENT` tag acts as a magnet — relevant orchestrators light up and form a **task chain** connected by cyan lines. Simultaneously, **LENS scanning beams** sweep a codebase panel. Results appear as floating data cards: file structure, dependencies, test coverage.

**Analogy:** *"The manager reads the order ticket, assigns the team, and checks the inventory."*

### Scene 4 — Intelligence Tiers (3:30 – 4:30)

The sphere enters a brain-shaped chamber with three ascending platforms:
- **Perception** (cyan): Pattern icons light up as the code is matched against known enterprise patterns
- **Reasoning** (purple): A decision tree forms — strategy options appear with confidence scores
- **Action** (amber): A step-by-step execution plan materializes with TDD gates and rollback checkpoints

**Narration:** "Confidence scores matter here. A strategy with 89% historical success on this pattern isn't a guess — it's earned. That's the difference between an opinionated system and an arbitrary one."

### Scene 5 — Governance Gate (4:30 – 5:15)

The sphere approaches a translucent **shield barrier**. A rapid green cascade indicates rules passing. The shield opens, sphere passes through.

**Alternate scenario** (5 seconds): Show a violation — shield stays closed, sphere bounces back with a violation card showing the fix suggestion.

**Narration:** "A governance violation here costs seconds. The same violation caught in production costs days — and trust."

### Scene 6 — TDD Execution (5:15 – 6:00)

The sphere enters a chamber with an ECG monitor. Three quick phases:
- **RED**: Test file created, test runs, fails (red pulse)
- **GREEN**: Implementation written, test passes (green pulse)
- **REFACTOR**: Code improved, test still passes (blue pulse)

The heartbeat rhythm continues: red-green-blue. A growing test count badge: 1 → 2 → 3 → 4 tests.

**Forward-reference:** *"See Video 4 for a complete TDD implementation session."*

### Scene 7 — Delivery & Audit Trail (6:00 – 6:30)

The sphere (now green) enters the final chamber — a **git timeline**. It merges into the commit rail with a satisfying snap. A conventional commit message materializes. AC markers (audit trail) flow into a persistent activity log database icon.

**Narration:** "The audit trail isn't a log file that gets deleted. It's the permanent record that lets you answer the hardest audit question: 'Prove this was done correctly.'"

### Scene 8 — The Big Picture (6:30 – 7:00)

**Camera pulls back** to show the entire pipeline. Multiple spheres flow simultaneously — different colors for different intents. Some bounce back at governance, loop through TDD again. The system is alive — flowing, self-correcting.

**Closing text:** **"Every request. Classified. Analyzed. Tested. Governed. Delivered."**

**Vision callback:** *"Notice what you didn't have to manage. That's the value proposition — not capability, but reclaimed time."*

---

## Notes
- The Request Particle (cyan sphere) is the visual thread throughout — one object, tracked end to end
- This video DOES NOT repeat the governance/TDD deep dive — it previews them and forward-references Video 4
- Timing references are realistic system measurements, not exaggerated
