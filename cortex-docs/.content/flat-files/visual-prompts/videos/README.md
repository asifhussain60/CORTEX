# Video Prompts for CORTEX Visual Content — The Enterprise Intelligence Series

These prompts are designed for **Google Gemini Video Generator** and **NotebookLM Video Editor** to produce a **10-video enterprise intelligence series** that takes viewers from zero knowledge of CORTEX to a complete understanding of its strategic and technical value.

## The Learning Journey

The 10 concept videos follow a **progressive depth curve** — from executive overview to strategic ROI. Each video builds on the previous ones. **Zero content repetition between videos.** The first video inspires the viewer to complete the full journey.

| Phase | Videos | Goal |
|-------|--------|------|
| **Foundation** | 01–02 | Explain *what CORTEX is* and *how it builds trust through embedded governance* |
| **Engineering** | 03–06 | Deep dive into *intelligent reviews*, *architectural integrity*, *team collaboration*, and *audit traceability* |
| **Intelligence** | 07–08 | Advanced capabilities: *cross-domain learning* and *the before/after transformation* |
| **Enterprise** | 09–10 | Organizational scale: *managing thousands of repos* and *translating technical excellence into business ROI* |

**After the 10 concept videos**, viewers move to the **Tutorial series** (`tutorials/`) for hands-on practice.

## Video Design Best Practices Reference

All video prompts MUST comply with the codified best practices in:
**`cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml`**

Key rules (mandatory for every video):

| Rule | Title | Impact |
|---|---|---|
| VBP-001 | One Idea Per Frame | P0 — never duplicate text across regions of the same frame |
| VBP-002 | Start Strong — First 8 Seconds | P0 — hook before branding |
| VBP-003 | Narration Never Reads the Slide | P0 — Mayer's Redundancy Principle |
| VBP-004 | Progressive Disclosure | P1 — build complexity through animation |
| VBP-005 | Visual Hierarchy — Z/F Pattern | P1 — important info top-left to center |
| VBP-006 | Contrast-Based Storytelling | P1 — show pain before solution |
| VBP-007 | Segment Duration — 2-Min Cycles | P1 — visual change every 90-120 seconds |
| VBP-008 | User Control and Context | P0 — title, duration, chapters |
| VBP-009 | Signaling Principle | P1 — highlight active element being discussed |
| VBP-010 | Anchoring with Analogies | P2 — one analogy per concept, dark pill |
| VBP-011 | Strategic Silence | P2 — 1-3 sec silence at emotional peaks |
| VBP-012 | Consistent Visual Language | P0 — same icons/colors throughout series |
| VBP-013 | Business Book Anchoring | P2 — max 2-3 per video, governance content |
| VBP-014 | Standardized Hero Intro Slide | P0 — `cortex-logo-200.png` as large central hero image + title |
| VBP-015 | Breadcrumb Navigation | P0 — persistent breadcrumb bar for sequential content |
| VBP-016 | Bold Key Words | P1 — bold 1-3 key words per text card in accent color |
| VBP-017 | Alternate Male/Female Voice | P1 — odd videos = female, even = male narrator |
| VBP-018 | No Unexpanded Acronyms | P0 — full form on first use in every video |
| VBP-019 | Strategic Color Intelligence | P1 — domain-specific color coding (gold for V06, etc.) |

## Animated Diagram Flow Directives

When concept videos reference static diagrams from the `images/` prompts, these animation directives tell the video producer how to bring them to life:

### Brain Architecture (Image Prompt 01)
- **Flow:** Bottom → Top (Perception → Reasoning → Action)
- **Particles:** Cyan data streams flow upward
- **Active tier:** Pulses 3 seconds when narrated; others dim to 30%
- **Entry:** VS Code icon emits request; results flow upward

### Orchestrator Galaxy (Image Prompt 02)
- **Flow:** Center → Outward (MasterOrchestrator → tier spiral arms)
- **Active arm:** Spiral arm glows when tier is discussed
- **Connections:** Neural pathway lines pulse with request flow

### LENS Eye (Image Prompt 03)
- **Flow:** Outside → Center (Iris analyzers → Pupil synthesis)
- **Scan beam:** Sweeps clockwise across iris segments
- **Active analyzer:** Segment glows brighter; others dim
- **Result:** Synthesis point in pupil emits result card

### Shield Wall (Image Prompt 04)
- **Flow:** Front → Back (commit → Tier 0 → Tier 3)
- **Green path:** Particle passes through (smooth glow accumulation)
- **Red path:** Particle bounces at violation tier (red flash + shake)
- **Active tier:** Shields pulse cyan when narrated

### Request Journey (Image Prompt 05)
- **Flow:** Left → Right (MCP Gateway → Governed Commit)
- **Cyan orb:** Travels station to station with ease-in-out
- **Active station:** 2× scale on label, full brightness
- **Inactive:** Dim to 30% opacity

### Extensibility Neural Growth (Image Prompt 08)
- **Flow:** Core → Outward (stable brain → growing dendrites)
- **New capability:** Dendrite extends with growth animation
- **Hot-reload badge:** Green pulse when extension registers

## Usage

1. Copy a prompt into Gemini's video generation tool or NotebookLM Video Editor
2. Generated videos should be saved to `cortex-docs/assets/videos/generated/`
3. Reference them in HTML views using: `<video src="assets/videos/generated/<filename>.mp4">`

---

## 🎨 MANDATORY Visual Identity (Apply to ALL Concept Videos)

Every generated video **MUST** follow these rules for brand consistency.

### Color Palette (from `glass-design-tokens.css` + `main.css`)

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#0a0e27` | Background — deep space navy |
| `--bg-secondary` | `#1a1f3a` | Glass panels, cards |
| `--glass-bg` | `rgba(26, 31, 58, 0.7)` | Frosted glass surfaces |
| `--accent-primary` | `#00d4ff` | Cyan — primary brand accent |
| `--accent-secondary` | `#7b61ff` | Purple — secondary accent |
| `--success` | `#00ff88` | Green — success states |
| `--warning` | `#ffa500` | Amber — warning states |
| `--danger` | `#ff4444` | Red — danger/error states |
| `--info` | `#3b82f6` | Blue — informational |
| `--text-primary` | `#ffffff` | White text |
| `--text-secondary` | `#a0a6c0` | Muted text |

### Glassmorphism Motion Style

- **Transitions:** Smooth ease-in-out (300ms for panels, 200ms for elements)
- **Glass panels:** Semi-transparent with animated blur (10-20px backdrop)
- **Borders:** `rgba(255, 255, 255, 0.1)` — 1px, subtle glow on hover/focus
- **Glow effects:** Pulsing cyan glow (`0 0 20px rgba(0, 212, 255, 0.3)`) on active elements
- **Particle effects:** Cyan/purple floating particles for data flow
- **Camera:** Smooth dolly/zoom — no jerky cuts. Ken Burns for static scenes.

### 🔤 Text Contrast & Readability (MANDATORY)

- **Text on dark backgrounds:** Always `#ffffff` or `#00d4ff` — never muted gray directly on complex backgrounds
- **Text over particles/glows/animations:** Add a dark pill background `rgba(10, 14, 39, 0.85)` behind text
- **Animated text reveals:** Ensure text is fully opaque (#ffffff) by the end of the animation, not stuck at low opacity
- **Code blocks:** JetBrains Mono on solid `rgba(26, 31, 58, 0.9)` panels — high contrast guaranteed
- **Captions/analogies:** Use `#a0a6c0` ONLY on solid glass panels, never floating on animated backgrounds

### CORTEX Logo Watermark

- CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video

### Typography (animated text)

- Headings: **Space Grotesk** (bold) — fade in with subtle upward slide
- Body text: **Inter** — typewriter reveal or fade
- Code/labels: **JetBrains Mono** — terminal-style character-by-character reveal

### Audio Direction

- Background: Ambient electronic/synth pad — calm, futuristic, NOT distracting
- Transitions: Soft "whoosh" sound on panel transitions
- Key moments: Subtle chime/ping on ✅ checkmarks and completions
- Narration: Clear, professional, conversational — NOT robotic

### 🎬 Standardized Hero Intro Slide (VBP-014 — MANDATORY)

**Every video opens with the same 5-second title card** before Scene 1 content begins:

1. Full-screen `#0a0e27` deep navy background with floating particles
2. **CORTEX logo** (`cortex-docs/assets/images/cortex-logo-200.png`) — large, centered, hero-style, with subtle cyan glow pulse
3. **Video title** in Space Grotesk Bold, white, positioned ABOVE the logo
4. **Subtitle** in Inter, `#a0a6c0`, positioned BELOW the logo
5. Hold 5 seconds → logo shrinks to watermark position → Scene 1 fades in

This creates instant series recognition. The viewer knows they're watching a CORTEX video before any content appears.

> **Exception:** The hero intro slide does NOT conflict with VBP-002 (hook in 8 seconds). The 5-second title card IS brand establishment, and the hook must begin within 3 seconds of Scene 1 starting (total: 8 seconds from video start).

### 🧭 Breadcrumb Navigation for Sequential Content (VBP-015 — MANDATORY)

**When a video presents steps, stages, layers, or any sequential process**, a persistent **breadcrumb bar** must remain visible throughout the sequence:

| Element | Appearance |
|---------|-----------|
| **Current step** | Full brightness, bold, cyan highlight, 1.5× label scale |
| **Completed steps** | ✅ green checkmark, dimmed to 60% opacity |
| **Upcoming steps** | Muted outlines at 30% opacity |

**Breadcrumb placement:** Bottom of frame (horizontal) or right side (vertical for long sequences like V05's 9 stages).

**Videos with breadcrumb requirements:**

| Video | Breadcrumb Content | Scenes |
|-------|-------------------|--------|
| V01 | 5 contrast cards (Raw AI vs CORTEX) | Scene 3 |
| V02 | 4 governance tiers + 3 TDD phases + 6-step enforcement flow | Scenes 2, 3, 4 |
| V03 | 3 test pyramid tiers + 5 security layers + review pipeline | Scenes 2, 3, 4 |
| V04 | **9 audit stages** (PRIMARY breadcrumb video) + wiring checks | Scene 2 (entire stage sequence) |
| V05 | 7 extension dendrites + 3-repo onboarding + team workflow | Scenes 2, 3, 4 |
| V06 | 8 pipeline stations (Intent → Audit Trail → Governed Commit) | Scenes 2–7 |
| V07 | LENS letters (L-E-N-S) + 4 onboarding steps + pattern library | Scenes 2, 4 |
| V08 | Week 1→4→12 timeline + 4-station URS loop + before/after | Scenes 1/3/4, Scene 2 |
| V09 | 5 REAL capabilities + 3 FUTURE capabilities + multi-repo scale | Scenes 2, 3, 4 |
| V10 | 4 ROI dimensions + 10-video journey recap | Scenes 2, 5 |

### 🎙️ Voice Alternation Schedule (VBP-017 — MANDATORY)

| Video | Narrator | Rationale |
|-------|----------|-----------|
| V01 — The CORTEX Paradigm | 🎙️ **Female** | Odd-numbered |
| V02 — The Trust Layer | 🎙️ **Male** | Even-numbered |
| V03 — Precision Reviews | 🎙️ **Female** | Odd-numbered |
| V04 — Architectural Integrity | 🎙️ **Male** | Even-numbered |
| V05 — The Collaborative Engine | 🎙️ **Female** | Odd-numbered |
| V06 — Traceability & Transparency | 🎙️ **Male** | Even-numbered |
| V07 — Cross-Domain Intelligence | 🎙️ **Female** | Odd-numbered |
| V08 — CORTEX vs. The Status Quo | 🎙️ **Male** | Even-numbered |
| V09 — Scaling the Enterprise | 🎙️ **Female** | Odd-numbered |
| V10 — The Strategic ROI | 🎙️ **Male** | Even-numbered |

Both voices share the same tone: confident, conversational, honest, not salesy. Within a single video, the voice does NOT switch.

### 🎨 Strategic Color Intelligence (VBP-019 — MANDATORY)

Colors carry meaning across the entire series. Once a color association is established, it must never be broken:

| Color | Hex | Meaning | Primary Video |
|-------|-----|---------|---------------|
| Cyan | `#00d4ff` | CORTEX identity, headings, active highlights | All videos |
| Purple | `#7b61ff` | Connections, paths, orchestrator tier | V06, V07, V09 |
| **Gold** | **`#FFD700`** | **Golden tests, premium quality, earned trust** | **V03 (primary)** |
| Red | `#ff4757` | Violations, failures, TDD RED, security alerts | V02, V03, V04 |
| Green | `#2ecc71` | Passing tests, TDD GREEN, healthy states | V02, V04, V08 |
| Blue | `#3b82f6` | TDD REFACTOR, informational | V02 |
| Amber | `#f39c12` | Warnings, P1, caution, promoted tests | V02, V03, V04 |

**V03 is the GOLD video.** Golden test elements use gold (#FFD700) as the primary accent — gold glass panels, gold glow on pyramid apex, golden particle effects. All other videos use cyan as primary.

---

## 🎙️ NARRATION PHILOSOPHY — MANDATORY FOR ALL VIDEOS

**The viewer can read the slides. The narrator must never read them.**

This is the single most important rule for narration quality. Every line of narration must pass this test:

> *"Does this add something the viewer cannot get simply by reading the screen?"*

If the answer is no, cut it or rewrite it.

### What "Speaking TO the slide" means

The visual shows the WHAT. The narration delivers the WHY, the SO WHAT, the FEEL, and the CONSEQUENCE — things that cannot be conveyed by text on a screen alone.

| Visual on screen | ❌ Reading the slide (WRONG) | ✅ Speaking to it (RIGHT) |
|---|---|---|
| Governance tiers animate: P0, P1, P2 | *"There are three severity tiers: P0, P1, and P2."* | *"P0 violations stop the commit. Not slow it down — stop it. That's what makes it structural, not aspirational."* |
| TDD ECG: RED → GREEN → BLUE | *"The three phases are red, green, and blue."* | *"Most engineers write tests after the fact, if at all. CORTEX makes that impossible — and that discomfort is the point."* |
| Convergence loop iterates until 0 violations | *"The loop runs until there are zero violations."* | *"Traditional CI gives you a report and moves on. CORTEX doesn't move on. That's not a small difference."* |
| LENS scanning animation runs | *"LENS scans your codebase."* | *"By the time you've typed the feature request, CORTEX already knows which files it will touch."* |
| Split screen: Without vs With CORTEX | *"On the left is without CORTEX. On the right is with CORTEX."* | *"The left column is how engineering feels right now for most teams. The right is what it should feel like."* |

### Narration Principles

1. **Add insight, not description.** If the screen shows a metric improving, the narrator explains *why that metric matters*, not that it improved.
2. **Surface the consequence.** When a governance rule fires, the narrator speaks to the real-world cost of not having that rule — not what the rule says.
3. **Anticipate the question.** A viewer watching LENS scan code will wonder: "How fast is this? Is it accurate?" Answer that before they ask.
4. **Use contrast and stakes.** The most compelling narration names what would happen without CORTEX — making the benefit feel real, not theoretical.
5. **Trust the animation.** When an animation makes something visually obvious, the narrator says nothing, or adds an emotional/conceptual beat — never a description.
6. **Let silence work.** On key moments (a convergence loop reaching zero, a golden test passing), a beat of silence lands harder than narration.

### Tone

- Confident, not salesy
- Honest about what CORTEX is and isn't (it orchestrates AI; it doesn't embed it)
- Uses the second person ("you") to keep it personal
- Respects the viewer's intelligence — no hand-holding on things they can plainly see

---

## Video Index — CORTEX: The Enterprise Intelligence Series

| # | File | Title | Duration | Depth | Voice |
|---|------|-------|----------|-------|-------|
| 01 | `01-p-the-cortex-paradigm.md` | The CORTEX Paradigm | 8 min | 🟢 Story | 🎙️ Female |
| 02 | `02-p-the-trust-layer.md` | The Trust Layer | 9 min | 🟡 Governance | 🎙️ Male |
| 03 | `03-p-precision-reviews.md` | Precision Reviews | 8 min | 🟡→🔴 Bridge | 🎙️ Female |
| 04 | `04-p-architectural-integrity.md` | Architectural Integrity | 9 min | 🔴 Advanced | 🎙️ Male |
| 05 | `05-p-the-collaborative-engine.md` | The Collaborative Engine | 8 min | 🔵 Platform | 🎙️ Female |
| 06 | `06-p-traceability-and-transparency.md` | Traceability & Transparency | 8 min | 🔴 Developer | 🎙️ Male |
| 07 | `07-p-cross-domain-intelligence.md` | Cross-Domain Intelligence | 8 min | 🔴 Intelligence | 🎙️ Female |
| 08 | `08-p-cortex-vs-the-status-quo.md` | CORTEX vs. The Status Quo | 7 min | 🟡 Capstone | 🎙️ Male |
| 09 | `09-p-scaling-the-enterprise.md` | Scaling the Enterprise | 8 min | 🔴 Vision | 🎙️ Female |
| 10 | `10-p-the-strategic-roi.md` | The Strategic ROI | 7 min | 🔵 Executive | 🎙️ Male |

**Total Concept Video Runtime:** ~80 minutes (comprehensive enterprise intelligence walkthrough + strategic ROI)

## 📐 Mermaid Diagram Files — Co-located for NotebookLM Bundling

Each video prompt has co-located Mermaid (`.mmd`) diagram files numbered to match. **Bundle each prompt + its matching diagram files together as sources in NotebookLM** for proper video rendering. Every `.mmd` file contains frontmatter with `animation_notes` describing frame-by-frame rendering instructions.

| Diagram File | Maps to Video | Diagram Type | Key Content |
|---|---|---|---|
| `01-d-c4-container-full-system.mmd` | V01 — The CORTEX Paradigm | C4-Container | Full system architecture — 4-tier stack, animate bottom→top |
| `02-d-governance-tdd-enforcement-flow.mmd` | V02 — The Trust Layer | Flowchart | Shield wall (Pre-commit→CI→Runtime) + TDD RED/GREEN/BLUE |
| `03-d-golden-test-pyramid-and-security-layers.mmd` | V03 — Precision Reviews | Flowchart | Test pyramid promotion + 5 security layers + SDLC timeline |
| `04-d-audit-pipeline-stages.mmd` | V04 — Architectural Integrity | Flowchart | 9-stage `/audit fix` pipeline with convergence loop |
| `05-d-common-utilities-overview.mmd` | V05 — The Collaborative Engine | C4-Component | Tier 1 stable foundation — "Extend, Don't Fork" context |
| `06-d-mcp-request-lifecycle-sequence.mmd` | V06 — Traceability & Transparency | Sequence | MCP request flow — Client→Gateway→Router→Orchestrator→Tool |
| `07-d-orchestrator-dispatch-flow.mmd` | V07 — Cross-Domain Intelligence | Flowchart | Intent classification → intelligence tiers → target orchestrator |
| `07-d-c4-component-master-orchestrator.mmd` | V07 — Cross-Domain Intelligence | C4-Component | Master Orchestrator internals — zoom-in detail view |
| `08-d-urs-learning-feedback-loop.mmd` | V08 — CORTEX vs. The Status Quo | Flowchart | URS cycle + Week 1→12 transformation + compound effect |
| `09-d-platform-saas-architecture.mmd` | V09 — Scaling the Enterprise | Flowchart | ✅ REAL MCP server + 🔮 VISION SaaS architecture |

> **NotebookLM Workflow:** When generating Video N, import `NN-p-*.md` AND all matching `NN-d-*.mmd` files as sources. The prompt describes the narrative and scenes. The diagrams provide the exact visual structure with animation notes. Together they give the video producer everything needed.

> **File Naming for NotebookLM:** Use the prefix `01_CORTEX_[Topic]`, `02_CORTEX_[Topic]`, etc. when uploading to NotebookLM. This ensures it processes context in the exact order of the narrative arc.

### Hands-On Tutorials (separate folder)

After the concept videos, see `tutorials/README.md` for practical, screen-recording-style walkthroughs.

---

## Zero Overlap Policy

| Capability | Video Covers | Image Covers |
|-----------|-------------|-------------|
| Paradigm & Security-by-Design | Strategic orchestration vs raw AI (V01) | Static brain cross-section (I1) |
| Governance & Trust | Embedded compliance, TDD discipline (V02) | Shield wall posture (I4) |
| Code Reviews & Security | Intelligent review automation, golden tests (V03) | Pyramid with scoring (I6), Five-layer defense (I7) |
| Architectural Integrity | Continuous validation, convergence pipeline (V04) | Station-to-station infographic (I5) |
| Team Collaboration | Shared context, cross-functional workflows (V05) | Neural growth anatomy (I8) |
| Traceability & Audit Trail | Request particle → governed commit with full history (V06) | Galaxy ecosystem map (I2) |
| Cross-Domain Intelligence | LENS scan, pattern recognition across domains (V07) | Diagnostic eye anatomy (I3) |
| Before/After Transformation | Raw Copilot vs CORTEX-governed output (V08) | Before/after split (I10) |
| Enterprise Scale | Multi-repo, multi-team, platform architecture (V09) | — (no static image) |
| Strategic ROI | Business value, speed-to-market, risk reduction (V10) | — (no static image) |

---

*All prompts reference actual CORTEX capabilities*
