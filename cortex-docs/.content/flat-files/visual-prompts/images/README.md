# Image Prompts for CORTEX Visual Assets

These prompts are designed for **Google Gemini Image Editor** and **NotebookLM** to generate high-value images that illustrate and depict the internal workings of CORTEX.

## Usage

1. Copy a prompt below into Gemini's image generation tool
2. Generated images should be saved to `cortex-docs/assets/images/generated/`
3. Reference them in HTML views using relative paths: `assets/images/generated/<filename>.png`

---

## 🎨 MANDATORY Visual Identity (Apply to ALL Prompts)

Every generated image **MUST** follow these rules for brand consistency with the CORTEX documentation site (`index.html`).

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

### Glassmorphism Style

- **Glass panels:** Semi-transparent (`rgba(26, 31, 58, 0.7)`) with 10-20px backdrop blur
- **Borders:** `rgba(255, 255, 255, 0.1)` — 1px subtle white borders on glass surfaces
- **Glow effects:** `0 0 20px rgba(0, 212, 255, 0.3)` — cyan glow on key elements
- **Shadows:** `0 8px 32px rgba(0, 0, 0, 0.37)` — deep ambient shadows
- **Corner radius:** 12-16px on panels and cards

### CORTEX Logo Watermark

- The CORTEX logo (`cortex-logo-128.png`) must appear **embossed in the bottom-right corner** of every image
- Opacity: 20-30% — visible but not distracting
- Size: ~5-8% of total image width
- Style: Embossed/debossed with subtle inner shadow, matching the glass aesthetic

### Typography

- Headings: **Space Grotesk** (bold) — or nearest geometric sans-serif
- Body text: **Inter** — or nearest clean sans-serif
- Code/labels: **JetBrains Mono** — or nearest monospace font

---

## Prompt Index

| # | File | Subject | Dimensions |
|---|------|---------|------------|
| 1 | `prompt-01-brain-architecture.md` | Three-tier brain architecture | 1920×1080 |
| 2 | `prompt-02-orchestrator-galaxy.md` | 51 orchestrators as a galaxy | 1920×1080 |
| 3 | `prompt-03-lens-eye.md` | LENS as a diagnostic eye | 1920×1080 |
| 4 | `prompt-04-governance-shield.md` | 38 CORE rules as a shield wall | 1920×1080 |
| 5 | `prompt-05-tdd-heartbeat.md` | TDD cycle as a heartbeat | 800×600 |
| 6 | `prompt-06-mcp-nervous-system.md` | MCP as a nervous system | 1920×1080 |
| 7 | `prompt-07-request-journey.md` | A request's journey through CORTEX | 1920×1080 |
| 8 | `prompt-08-registry-library.md` | Git-backed registry as an ancient library | 800×600 |
| 9 | `prompt-09-audit-immune-system.md` | Audit pipeline as immune response | 1920×1080 |
| 10 | `prompt-10-sweep-completeness.md` | Sweep completeness as forensic investigation | 800×600 |
| 11 | `prompt-11-intelligence-matrix-circuit.md` | Intelligence Matrix as a circuit board | 1920×1080 |
| 12 | `prompt-12-workflow-assembly-line.md` | WorkflowEngine as a factory assembly line | 800×600 |
| 13 | `prompt-13-rca-memory-shield.md` | RCA Memory Engine as a force field shield | 1920×1080 |

---

## Cross-Reference: No Overlap with Video Prompts

These image prompts focus on **static architectural concepts** — the "what it is" snapshots.  
Video prompts (in `../videos/`) focus on **dynamic flows and processes** — the "how it works" stories.

| Concept | Image Covers | Video Covers |
|---------|-------------|-------------|
| Brain Tiers | Static 3-layer cross-section | Animated request flowing through all 3 tiers |
| Orchestrators | Galaxy map (spatial layout) | Day-in-the-life orchestrator coordination |
| LENS | Eye diagram (anatomy) | Live analysis with results appearing in real-time |
| Governance | Shield wall (defense posture) | Rule enforcement catching a violation |
| TDD | ECG heartbeat (rhythm) | Full RED→GREEN→REFACTOR cycle animated |
| MCP | Nervous system (anatomy) | Messages flowing through the nervous system |
| Audit | Immune system (cellular view) | 9-stage pipeline progressing through stages |

---

*All prompts reference actual CORTEX architecture verified against live codebase · 27 February 2026*
