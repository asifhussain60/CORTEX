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

### Phase 1: Understanding CORTEX (Videos 1-7)

Videos 1-7 follow a **progressive depth curve** — from executive overview to advanced internals. Each video assumes the viewer has watched the previous ones. **Zero content repetition between videos.**

| # | File | Title | Duration | Audience | Depth |
|---|------|-------|----------|----------|-------|
| 1 | `prompt-01-what-is-cortex.md` | What Is CORTEX? | 7 min | Executives, All | 🟢 Story |
| 2 | `prompt-02-the-request-lifecycle.md` | The Life of a Request | 7 min | PO, Engineers | 🟡 Flow |
| 3 | `prompt-03-intelligence-engine.md` | The Intelligence Engine | 9 min | PO → Engineers | 🟡→🔴 Bridge |
| 4 | `prompt-04-governance-in-action.md` | Governance in Action | 8 min | Engineers, Leads | 🔴 Developer |
| 5 | `prompt-05-tdd-mastery.md` | TDD Mastery | 9 min | Engineers | 🔴 Developer |
| 6 | `prompt-06-mcp-tools-deep-dive.md` | MCP Tools Deep Dive | 10 min | Engineers, Builders | 🔴 Developer |
| 7 | `prompt-07-audit-fix-pipeline.md` | The Audit Fix Pipeline | 10 min | Platform Engineers | 🔴 Advanced |

### Phase 2: Getting Started (Videos 8-10)

Videos 8-10 are **practical tutorials** that assume zero prior hands-on experience. They can be watched after Videos 1-7 for context, or standalone for users who want to start immediately.

| # | File | Title | Duration | Audience | Prerequisites |
|---|------|-------|----------|----------|---------------|
| 8 | `prompt-08-getting-started-installation.md` | Getting Started: Installation | 5 min | All | None |
| 9 | `prompt-09-getting-started-first-commands.md` | Getting Started: Your First Commands | 7 min | Engineers, PO | Video 8 |
| 10 | `prompt-10-getting-started-customization.md` | Getting Started: Customizing CORTEX | 8 min | Leads, Platform | Videos 8-9, Video 4 |

### Total Runtime: ~70 minutes

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
Video 8  ██░░░░░░░░  20%  Tutorial — installation (reset)
Video 9  ████░░░░░░  40%  Tutorial — using commands
Video 10 ███████░░░  70%  Tutorial — customization
```

Videos 8-10 "reset" the depth because they're tutorials, not conceptual explanations.

---

## Content Overlap Policy

To ensure **zero repetition**, follow these rules:

| Concept | Canonical Video | Other Videos May... |
|---------|-----------------|---------------------|
| TDD heartbeat | **Video 5** | Forward-reference only (≤30s) |
| Governance shield | **Video 4** | Show passing through without detail |
| MCP tools | **Video 6** | Use as examples, not explain protocol |
| Audit pipeline | **Video 7** | Reference as "single command" |
| AC markers | All | Reinforce — this is a core concept |

**Example:** Video 2 shows a request passing through TDD Station 3, but says: *"See Video 5 for the complete TDD session."* — no code panels, no detailed heartbeat.

---

## Closing Vision (Apply to ALL Videos)

Every video ends with the same vision callback from `index.html`:

> *"CORTEX: $8,600 saved per team, per year. Zero guesswork."*

This reinforces the value proposition across the entire learning journey.

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

---

*All prompts reference actual CORTEX architecture verified against live codebase · 27 February 2026*
