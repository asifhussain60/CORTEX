# Video Prompts for CORTEX Visual Content

These prompts are designed for **Google Gemini Video Generator** and **NotebookLM Video Editor** to produce an **8-video learning journey** that takes users from zero knowledge to complete CORTEX mastery.

## The Learning Journey

The 8 concept videos follow a **progressive depth curve** — from executive overview to advanced internals. Each video assumes the viewer has watched the previous ones. **Zero content repetition between videos.** The first video encourages the viewer to complete the full journey.

| Phase | Videos | Goal |
|-------|--------|------|
| **Foundation** | 1–3 | Explain *what CORTEX is*, *how requests flow*, and *how intelligence works* |
| **Engineering** | 4–6 | Deep dive into *governance*, *TDD discipline*, and *production readiness* |
| **Mastery** | 7–8 | Advanced capabilities: *extensibility*, *golden tests*, and *continuous learning* |

**After the 8 concept videos**, viewers move to the **Tutorial series** (`tutorials/`) for hands-on practice.

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

## Video Index — Complete Learning Journey

| # | File | Title | Duration | Depth |
|---|------|-------|----------|-------|
| 1 | `prompt-01-what-is-cortex.md` | What Is CORTEX? | 7 min | 🟢 Story |
| 2 | `prompt-02-the-request-lifecycle.md` | The Life of a Request | 7 min | 🟡 Flow |
| 3 | `prompt-03-intelligence-engine.md` | The Intelligence Engine | 8 min | 🟡→🔴 Bridge |
| 4 | `prompt-04-governance-and-tdd.md` | Governance and TDD — Quality as Infrastructure | 9 min | 🔴 Developer |
| 5 | `prompt-05-production-readiness.md` | Production Readiness — Audit, Sweep, and Convergence | 9 min | 🔴 Advanced |
| 6 | `prompt-06-golden-tests-and-security.md` | Golden Tests and Security-First Development | 8 min | 🔴 Developer |
| 7 | `prompt-07-extensibility-and-onboarding.md` | Extensibility and Repository Onboarding | 8 min | 🔴 Platform |
| 8 | `prompt-08-learning-and-transformation.md` | Continuous Learning and Real-World Transformation | 7 min | 🟡 Capstone |

**Total Concept Video Runtime:** ~63 minutes (industry standard for a comprehensive platform walkthrough)

### Hands-On Tutorials (separate folder)

After the concept videos, see `tutorials/README.md` for practical, screen-recording-style walkthroughs.

---

## Zero Overlap Policy

| Capability | Video Covers | Image Covers |
|-----------|-------------|-------------|
| Architecture | Animated intelligence decision (V3) | Static brain cross-section (I1) |
| Orchestrators | Live coordination on a request (V2) | Galaxy ecosystem map (I2) |
| LENS | Live workspace scan (V3) | Diagnostic eye anatomy (I3) |
| Governance + TDD | Violation caught, TDD cycle enforced (V4) | Shield wall posture (I4) |
| Request Pipeline | Particle tracking animated (V2) | Station-to-station infographic (I5) |
| Golden Tests | End-to-end creation to audit trace (V6) | Pyramid with scoring (I6) |
| Security | Security gate catching vulnerability (V6) | Five-layer defense diagram (I7) |
| Extensibility | Building new capability live (V7) | Neural growth anatomy (I8) |
| Knowledge/Learning | Onboarding + learning loop (V7, V8) | Pattern lattice (I9) |
| Transformation | Full refactoring session (V8) | Before/after split (I10) |

---

*All prompts reference actual CORTEX capabilities*
