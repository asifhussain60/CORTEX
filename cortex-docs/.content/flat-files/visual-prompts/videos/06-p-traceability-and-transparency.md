# Video Prompt 06 — Traceability & Transparency
### CORTEX: The Enterprise Intelligence Series

> **Duration:** 7 minutes · **Audience:** Product Owners, Software Engineers, Compliance Officers, Engineering Managers
> **Depth:** 🟡 Product-level — shows the journey, light architecture
> **Core Executive Theme:** End-to-end audit trail, decision provenance, compliance-ready traceability for every AI-generated change
> **No overlap:** Image prompt-05 shows a static journey map; this video animates a particle flowing through the pipeline in real-time
> **Video Design:** Applies VBP-001, VBP-002, VBP-004 (progressive disclosure), VBP-007, VBP-009 (signaling), VBP-011 (silence)

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> See `README.md` for full mandatory palette, motion style, text contrast rules, typography, and watermark.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the slide.** Every narration line must add something the viewer cannot get from reading the screen: the *why*, the *consequence*, the *non-obvious implication*, or the *emotional truth*. If a narration line restates visible text, cut it or rewrite it. See `README.md` §Narration Philosophy for full guidance and examples.

## ⚠️ VIDEO DESIGN BEST PRACTICES — MANDATORY

> **VBP-001:** One idea per frame. **VBP-004:** Progressive disclosure — reveal pipeline stages sequentially.
> **VBP-007:** Scene transitions every ~90-120 seconds. **VBP-009:** Signal the active station — pulse it, dim others.
> **VBP-011:** Strategic silence when the request completes its journey.
> See `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml`.

## ⚠️ HERO INTRO SLIDE — MANDATORY (VBP-014)

> **Scene 0 — Title Card (0:00 – 0:05):** Full-screen `#0a0e27` deep navy background. CORTEX logo (`cortex-docs/assets/images/cortex-logo-200.png`) displayed as a **large central hero image** with a subtle cyan glow pulse. Above the logo: **"Traceability & Transparency"** in Space Grotesk Bold, white. Below the logo: **"Every decision. Every change. Every proof."** in Inter, `#a0a6c0`. Series badge top-right: `06 of 10 · The Enterprise Intelligence Series`. Hold 5 seconds. Transition: logo shrinks to watermark position as Scene 1 fades in.

## ⚠️ BREADCRUMB NAVIGATION — MANDATORY (VBP-015)

> **This video follows a request particle through 8 sequential stations.** Display a persistent **breadcrumb bar** at the bottom of the frame showing all 8 stations:
> `Intent → Orchestrator → LENS → Brain → Governance → TDD → Delivery → Big Picture`
> - **Current station:** Full brightness, bold, cyan highlight, 1.5× label scale
> - **Completed stations:** ✅ checkmark, dimmed to 60% opacity
> - **Upcoming stations:** Muted outlines at 30% opacity
> - As the particle advances to each new scene, the breadcrumb animates: current station checks off, next station highlights.
> This prevents context loss — the viewer always knows where the request is in the pipeline.

## ⚠️ TYPOGRAPHY, COLOR & VOICE — MANDATORY (VBP-016, VBP-017, VBP-018, VBP-019)

> **Bold Key Words:** On every text card and glassmorphic panel, **bold the 1–3 most important words** in cyan (`#00d4ff`) to draw scanning eyes to the key concept.
> **Color Intelligence:** Standard CORTEX palette — cyan for the request particle, purple for orchestrator connections, red for violations, green for passing states.
> **Voice:** 🎙️ **Male narrator** (even-numbered video — V06). Confident, conversational, honest tone.
> **Acronym Expansion (first use in this video):**
> - CORTEX = **CO**gnitive **R**eal-**T**ime **EX**ecution (Scene 1 intro text)
> - LENS = **L**anguage → **E**xamination → **N**avigation → **S**ynthesis (Scene 3)
> - TDD = **T**est-**D**riven **D**evelopment (Scene 6)
> - MCP = **M**odel **C**ontext **P**rotocol (Diagram directives)
> - AC = **A**udit **C**ompletion markers (Scene 7)
> - ECG = **E**lectro**c**ardio**g**ram rhythm analogy (Scene 6)

---

## PROMPT

Create a 7-minute animated explainer video titled **"Traceability & Transparency"**. Track a single user request as a glowing cyan particle traveling through CORTEX's processing pipeline — every station it touches creates a permanent, auditable record. The viewer should understand: this isn't just a workflow, it's a compliance-ready chain of evidence.

### Scene 1 — The Request Is Born (0:00 – 1:00)

A glassmorphic text input. Cursor blinks. Text types: `"Add input validation to the user registration form"`. User presses Enter — text compresses into a **glowing cyan sphere**. A glass pipeline materializes below — a translucent tube with station chambers.

**As the sphere forms, a subtle timestamp and unique request ID attach to it** — a glass tag reading `REQ-2026-0142 · 14:23:07 UTC`. This ID will persist through every station, creating the traceability thread.

**Narration:** "Most AI tools stop at the answer. What you're about to see is what happens when an answer isn't enough — when quality, traceability, and correctness are non-negotiable. Every station this request touches will leave a record. Not because we chose to log it — because the architecture makes invisible decisions impossible."

### Scene 2 — Intent Classification (1:00 – 2:00)

Sphere enters the first chamber. **IntentRouter** appears as a rotating prism. The sphere enters one side; colored light fans out. Labels flash: `IMPLEMENT? FIX? REFACTOR? AUDIT? DEBUG?` — `IMPLEMENT` locks in with a cyan flash. A routing tag attaches like a luggage tag.

**Narration:** "The wrong orchestrator for the job is how AI systems produce plausible-sounding wrong answers. Routing is the first line of quality."

### Scene 3 — Orchestrator Selection & LENS Scan (2:00 – 3:30)

The tagged sphere enters a larger chamber with a ring of glowing orbs (orchestrators). The `IMPLEMENT` tag acts as a magnet — relevant orchestrators light up and form a **task chain** connected by cyan lines. Simultaneously, **LENS** (**L**anguage → **E**xamination → **N**avigation → **S**ynthesis) scanning beams sweep a codebase panel. Results appear as floating data cards: file structure, dependencies, test coverage.

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

The sphere enters a chamber with an ECG (electrocardiogram) monitor. Three quick **Test-Driven Development (TDD)** phases:
- **RED**: Test file created, test runs, fails (red pulse)
- **GREEN**: Implementation written, test passes (green pulse)
- **REFACTOR**: Code improved, test still passes (blue pulse)

The heartbeat rhythm continues: red-green-blue. A growing test count badge: 1 → 2 → 3 → 4 tests.

**Forward-reference:** *"See Video 4 for a complete TDD implementation session."*

### Scene 7 — Delivery & Audit Trail: The Permanent Record (6:00 – 6:30)

The sphere (now green) enters the final chamber — a **git timeline**. It merges into the commit rail with a satisfying snap. A conventional commit message materializes. AC markers (audit trail) flow into a persistent activity log database icon.

**Below the git timeline, a "Traceability Summary" panel materializes** showing the full chain for REQ-2026-0142:
- 🔵 **Classified:** IMPLEMENT (IntentRouter, 14:23:07)
- 🟢 **Analyzed:** LENS scan complete, 4 files mapped (14:23:08)
- 🟢 **Governed:** 38 rules passed, 0 violations (14:23:09)
- 🟢 **Tested:** 4 TDD cycles, 4/4 GREEN (14:23:12)
- 🟢 **Committed:** `feat(auth): add input validation` (14:23:14)

**Narration:** "The audit trail isn't a log file that gets deleted. It's the permanent record that lets you answer the hardest audit question: 'Prove this was done correctly.' Every decision — why this orchestrator, why this strategy, why this test — is traceable back to this single request ID. For compliance officers, this is the chain of evidence. For engineers, this is the 'what happened and why' that saves hours of archaeology."

### Scene 8 — The Big Picture: Transparency at Scale (6:30 – 7:00)

**Camera pulls back** to show the entire pipeline. Multiple spheres flow simultaneously — different colors for different intents. Some bounce back at governance, loop through TDD again. The system is alive — flowing, self-correcting. Each sphere trails its own request ID — a living audit dashboard.

**A glass panel appears to the right** showing a real-time "Transparency Dashboard":
- **Active requests:** 12 in pipeline
- **Governance blocks (today):** 3 (all remediated)
- **Compliance coverage:** 100% — every change has full provenance

**Closing text:** **"Every request. Classified. Analyzed. Tested. Governed. Delivered. Proven."**

**Vision callback:** *"Notice what you didn't have to manage — and notice what you CAN prove. That's the difference between a tool and a trust layer."*

---

## Notes
- **Traceability & Transparency framing** — The original "Life of a Request" video is preserved in full (8 stations, cyan particle, ECG metaphor). The transparency theme adds a *provenance* layer: the request ID that tracks through every station, the traceability summary panel, the transparency dashboard. This reframing elevates the same pipeline walkthrough for compliance-minded audiences and auditors.
- The Request Particle (cyan sphere) is the visual thread throughout — one object, tracked end to end
- This video DOES NOT repeat the governance/TDD deep dive — it previews them and forward-references Video 2
- Timing references are realistic system measurements, not exaggerated
- **Voice:** Male (V06 — even-numbered)

## Animated Diagram Flow Directives

### 📐 Mermaid Diagram Sources (bundle with this prompt in NotebookLM)

| Diagram File | Type | Scene Reference | Purpose |
|---|---|---|---|
| `06-d-mcp-request-lifecycle-sequence.mmd` | Sequence | Scenes 2–4 — The Request Particle Journey | Full MCP request lifecycle — the request particle tracks this exact sequence |
| `01-d-c4-container-full-system.mmd` | C4-Container | Scene 4 cameo | System context showing where the request flows within the 4-tier stack |

> **Video Producer:** Import `06-d-mcp-request-lifecycle-sequence.mmd` as the PRIMARY source alongside this prompt in NotebookLM. The sequence diagram shows the exact participant-to-participant flow the request particle follows. Each activation bar becomes the "station" where the cyan orb pauses. Import `01-d-c4-container-full-system.mmd` as supplementary context for the architecture overview cameo in Scene 4.

**Diagram: Request Journey Map (Image Prompt 05) — PRIMARY DIAGRAM FOR THIS VIDEO**
- This video IS the animated version of Image Prompt 05
- Flow direction: Left → Right (MCP Gateway → Governed Commit)
- Cyan orb: Ease-in-out between stations, pauses 3 seconds at each
- Active station: Full brightness, label scales 1.5×; inactive stations dim to 30%
- Governance station: Show green pass AND brief red bounce-back alternate path
- TDD station: ECG heartbeat plays (brief cameo — 5 seconds)

**Diagram: Brain Architecture (Image Prompt 01) — Scene 4 cameo**
- Three platforms light up sequentially (Perception → Reasoning → Action)
- Each platform shows 3-second activity before passing to the next
- Particle climbs upward gaining complexity (size increases slightly per tier)

**Diagram: Shield Wall (Image Prompt 04) — Scene 5 cameo**
- Quick 5-second shield barrier visualization
- Particle passes through (green) or bounces back (red) — both paths shown
