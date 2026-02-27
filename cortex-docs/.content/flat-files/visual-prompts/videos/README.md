# Video Prompts for CORTEX Visual Content

These prompts are designed for **Google Gemini Video Generator** and **NotebookLM Video Editor** to produce a **10-video learning journey** that takes users from zero knowledge to complete CORTEX mastery.

## The Learning Journey

| Phase | Videos | Goal |
|-------|--------|------|
| **Understanding** | 1-7 | Explain *what CORTEX is* and *how it works* |
| **Getting Started** | 8-10 | Show *how to use CORTEX* hands-on |

A new user watches Videos 1-7 to understand the architecture, then Videos 8-10 to start using it. By Video 10, they can customize CORTEX for their team.

## Usage

1. Copy a prompt into Gemini's video generation tool or NotebookLM Video Editor
2. Generated videos should be saved to `cortex-docs/assets/videos/generated/`
3. Reference them in HTML views using: `<video src="assets/videos/generated/<filename>.mp4">`

---

## 🎨 MANDATORY Visual Identity (Apply to ALL Videos)

Every generated video **MUST** follow these rules for brand consistency with the CORTEX documentation site and image prompts.

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

### CORTEX Logo Watermark

- The CORTEX logo (`cortex-logo-128.png`) must appear **embossed in the bottom-right corner** throughout the entire video
- Opacity: 15-25% — visible but not distracting during motion
- Size: ~5-8% of frame width
- Style: Subtle inner shadow, matching the glass aesthetic

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

## Video Index — Complete Learning Journey

### Phase 1: Understanding CORTEX (Videos 1-11)

Videos 1-11 follow a **progressive depth curve** — from executive overview to advanced internals. Each video assumes the viewer has watched the previous ones. **Zero content repetition between videos.**

| # | File | Title | Duration | Audience | Depth |
|---|------|-------|----------|----------|-------|
| 1 | `prompt-01-what-is-cortex.md` | What Is CORTEX? | 7 min | Executives, All | 🟢 Story |
| 2 | `prompt-02-the-request-lifecycle.md` | The Life of a Request | 7 min | PO, Engineers | 🟡 Flow |
| 3 | `prompt-03-intelligence-engine.md` | The Intelligence Engine | 9 min | PO → Engineers | 🟡→🔴 Bridge |
| 4 | `prompt-04-governance-in-action.md` | Governance in Action | 8 min | Engineers, Leads | 🔴 Developer |
| 5 | `prompt-05-tdd-mastery.md` | TDD Mastery | 9 min | Engineers | 🔴 Developer |
| 6 | `prompt-06-mcp-tools-deep-dive.md` | MCP Tools Deep Dive | 10 min | Engineers, Builders | 🔴 Developer |
| 7 | `prompt-07-audit-fix-pipeline.md` | The Audit Fix Pipeline | 10 min | Platform Engineers | 🔴 Advanced |
| 8 | `prompt-08-workflow-template-engine.md` | The Workflow Template Engine | 9 min | Engineers, Platform | 🔴 Architecture |
| 9 | `prompt-09-response-templates-engagement.md` | Response Templates & Orchestrator Engagement | 90s | Engineers | 🔴 Phase 85 |
| 10 | `prompt-10-multi-stack-debugging.md` | Debugging Any Stack | 90s | Engineers | 🔴 Phase 86 |
| 11 | `prompt-11-rca-memory-engine.md` | Never Repeat a Mistake — RCA Memory Engine | 90s | All | 🟡 Phase 87 |

**Videos 9–11** are short-form (90-second) feature spotlights for Phases 85, 86, and 87. They assume familiarity with CORTEX (recommend watching Videos 1–3 first) and focus tightly on one capability each.

### Phase 2: Hands-On Tutorials (separate folder)

Practical screen-recording-style tutorials separated from concept videos. See `tutorials/README.md` for the full index.

| # | File | Title | Duration | Audience | Prerequisites |
|---|------|-------|----------|----------|---------------|
| T1 | `tutorials/tutorial-01-getting-started-installation.md` | Getting Started: Installation | 5 min | Everyone | None |
| T2 | `tutorials/tutorial-02-getting-started-first-commands.md` | Getting Started: Your First Commands | 7 min | Engineers, PO | Tutorial T1 |
| T3 | `tutorials/tutorial-03-getting-started-customization.md` | Getting Started: Customizing CORTEX | 8 min | Leads, Platform | T1-T2 + Videos 04 + 08 |
| T4 | `tutorials/tutorial-04-building-a-feature-end-to-end.md` | Building a Feature End-to-End | 10 min | Engineers | T1-T2 + Videos 02 + 05 |
| T5 | `tutorials/tutorial-05-debugging-with-cortex.md` | Debugging with CORTEX | 9 min | Engineers | T1 + Video 03 |
| T6 | `tutorials/tutorial-06-onboarding-a-repository.md` | Onboarding a New Repository | 8 min | Tech Leads, Platform | T1 + Videos 03 + 04 |

**Why tutorials are separate:** Concept videos explain *what* and *why*. Tutorial videos show *how* — they are screen-recording walkthroughs, not architectural explainers. Different visual style (VS Code PiP overlay), different pacing, different audience entry points. Mixing them in the same folder creates confusion about learning phase and purpose.

### Total Runtime: ~80 minutes concept + ~47 minutes tutorial

---

## Depth Progression Visualization

```
Video 1  █░░░░░░░░░  10%  Executive overview — no code
Video 2  ██░░░░░░░░  25%  Request flow — light architecture
Video 3  ███░░░░░░░  35%  Intelligence — LENS, pipelines
Video 4  █████░░░░░  50%  Governance — real rules, violations
Video 5  ██████░░░░  60%  TDD — full code session
Video 6  ████████░░  80%  MCP — protocol, tool authoring
Video 7  ██████████  100% Audit — 9-stage pipeline (peak)
Video 8  █████████░  90%  Workflow Template Engine — YAML vs Python interpreter design
──────── tutorials ────────────────────────────────────────────
Tutor 1  ██░░░░░░░░  20%  Installation — step-by-step (depth resets for tutorials)
Tutor 2  ████░░░░░░  40%  First commands — practical with explanations
Tutor 3  ███████░░░  70%  Customization — real rules, real MCP tools
Tutor 4  ██████████  100% Full feature build — ticket to governed commit (peak)
Tutor 5  ████████░░  80%  Debugging — 5-phase diagnostic pipeline
Tutor 6  ███████░░░  70%  Repository onboarding — LENS + security + dashboard
```

Videos 1-8 build steadily to peak architectural depth. Tutorials independently reset depth for hands-on learners. Tutorials 1-3 cover setup basics; Tutorials 4-6 cover advanced workflows.

---

## Content Overlap Policy

To ensure **zero repetition**, follow these rules:

| Concept | Canonical Video | Other Videos May... |
|---------|-----------------|---------------------|
| TDD heartbeat | **Video 5** | Forward-reference only (≤30s) |
| Governance shield | **Video 4** | Show passing through without detail |
| MCP tools | **Video 6** | Use as examples, not explain protocol |
| Audit pipeline | **Video 7** | Reference as "single command" |
| Workflow template engine | **Video 8** | Forward-reference as "blueprint system" |
| AC markers | All | Reinforce — this is a core concept |

**Example:** Video 2 shows a request passing through TDD Station 3, but says: *"See Video 5 for the complete TDD session."* — no code panels, no detailed heartbeat.

---

## Closing Vision Policy

Each video ends with a **unique** closing vision callback that reinforces the value proposition in a distinct way. No two videos share the same closing line. All closings center on the core theme: *CORTEX frees engineers from code legwork so they can focus on envisioning and adding business value.*

See each prompt file's closing section for its specific callback.

---

## Cross-Reference: No Overlap with Image Prompts

| Concept | Images Cover (static) | Videos Cover (dynamic) |
|---------|----------------------|----------------------|
| Brain Tiers | Cross-section anatomy | Animated request flowing through tiers |
| Orchestrators | Galaxy spatial map | Day-in-the-life coordination story |
| LENS | Eye diagram anatomy | Live analysis with results appearing |
| Governance | Shield wall defense posture | Rule catching a real violation |
| TDD | ECG heartbeat rhythm | Full cycle with code transforming |
| MCP | Nervous system anatomy | Live tool invocations and responses |
| Audit | Immune system cellular | 9-stage pipeline progressing in real-time |
| Workflow Assembly | Static factory floor (prompt-12) | Three-layer system in motion — YAML + mixin + orchestrator |

---

## Folder Structure

```
videos/
  README.md                              ← this file
  prompt-01-what-is-cortex.md
  prompt-02-the-request-lifecycle.md
  prompt-03-intelligence-engine.md
  prompt-04-governance-in-action.md
  prompt-05-tdd-mastery.md
  prompt-06-mcp-tools-deep-dive.md
  prompt-07-audit-fix-pipeline.md
  prompt-08-workflow-template-engine.md
  prompt-09-response-templates-engagement.md   ← Phase 85 (new)
  prompt-10-multi-stack-debugging.md           ← Phase 86 (new)
  prompt-11-rca-memory-engine.md               ← Phase 87 (new)
  tutorials/
    README.md                            ← tutorial-specific index and visual identity notes
    tutorial-01-getting-started-installation.md
    tutorial-02-getting-started-first-commands.md
    tutorial-03-getting-started-customization.md
    tutorial-04-building-a-feature-end-to-end.md
    tutorial-05-debugging-with-cortex.md
    tutorial-06-onboarding-a-repository.md
```

---

*All prompts reference actual CORTEX architecture verified against live codebase · Updated 27 February 2026*
