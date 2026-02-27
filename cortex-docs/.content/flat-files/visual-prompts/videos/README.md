# Video Prompts for CORTEX Visual Content

These prompts are designed for **Google Gemini Video Generator** and **NotebookLM Video Editor** to produce 7 high-value explainer videos (7-10 minutes each) that visually walk users through CORTEX's internal workings.

## Usage

1. Copy a prompt below into Gemini's video generation tool or NotebookLM Video Editor
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

## Video Index — Progressive Depth Series

Videos are ordered from **highest-level overview** to **deepest technical detail**. Each video assumes the viewer has watched the previous ones. **Zero content repetition between videos.**

| # | File | Title | Duration | Depth Level |
|---|------|-------|----------|-------------|
| 1 | `prompt-01-what-is-cortex.md` | What Is CORTEX? | 7 min | 🟢 Executive |
| 2 | `prompt-02-the-request-lifecycle.md` | The Life of a Request | 8 min | 🟡 Product |
| 3 | `prompt-03-intelligence-engine.md` | The Intelligence Engine | 9 min | 🟡 Product→Dev |
| 4 | `prompt-04-governance-in-action.md` | Governance in Action | 8 min | 🔴 Developer |
| 5 | `prompt-05-tdd-mastery.md` | TDD Mastery | 9 min | 🔴 Developer |
| 6 | `prompt-06-mcp-tools-deep-dive.md` | MCP Tools Deep Dive | 10 min | 🔴 Developer |
| 7 | `prompt-07-audit-fix-pipeline.md` | The Audit Fix Pipeline | 10 min | 🔴 Advanced |

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
