# Image Prompts for CORTEX Visual Assets# Image Prompts for CORTEX Visual Assets



These prompts are designed for **Google Gemini Image Editor** and **NotebookLM** to generate high-value images that illustrate CORTEX capabilities for training and adoption materials.These prompts are designed for **Google Gemini Image Editor** and **NotebookLM** to generate high-value images that illustrate and depict the internal workings of CORTEX.



## Usage## Usage



1. Copy a prompt into Gemini's image generation tool1. Copy a prompt below into Gemini's image generation tool

2. Generated images should be saved to `cortex-docs/assets/images/generated/`2. Generated images should be saved to `cortex-docs/assets/images/generated/`

3. Reference them in HTML views using relative paths: `assets/images/generated/<filename>.png`3. Reference them in HTML views using relative paths: `assets/images/generated/<filename>.png`



------



## 🎨 MANDATORY Visual Identity (Apply to ALL Prompts)## 🎨 MANDATORY Visual Identity (Apply to ALL Prompts)



Every generated image **MUST** follow these rules for brand consistency with the CORTEX documentation site (`index.html`).Every generated image **MUST** follow these rules for brand consistency with the CORTEX documentation site (`index.html`).



### Color Palette (from `glass-design-tokens.css` + `main.css`)### Color Palette (from `glass-design-tokens.css` + `main.css`)



| Token | Hex | Usage || Token | Hex | Usage |

|-------|-----|-------||-------|-----|-------|

| `--bg-primary` | `#0a0e27` | Background — deep space navy || `--bg-primary` | `#0a0e27` | Background — deep space navy |

| `--bg-secondary` | `#1a1f3a` | Glass panels, cards || `--bg-secondary` | `#1a1f3a` | Glass panels, cards |

| `--glass-bg` | `rgba(26, 31, 58, 0.7)` | Frosted glass surfaces || `--glass-bg` | `rgba(26, 31, 58, 0.7)` | Frosted glass surfaces |

| `--accent-primary` | `#00d4ff` | Cyan — primary brand accent || `--accent-primary` | `#00d4ff` | Cyan — primary brand accent |

| `--accent-secondary` | `#7b61ff` | Purple — secondary accent || `--accent-secondary` | `#7b61ff` | Purple — secondary accent |

| `--success` | `#00ff88` | Green — success states || `--success` | `#00ff88` | Green — success states |

| `--warning` | `#ffa500` | Amber — warning states || `--warning` | `#ffa500` | Amber — warning states |

| `--danger` | `#ff4444` | Red — danger/error states || `--danger` | `#ff4444` | Red — danger/error states |

| `--info` | `#3b82f6` | Blue — informational || `--info` | `#3b82f6` | Blue — informational |

| `--text-primary` | `#ffffff` | White text || `--text-primary` | `#ffffff` | White text |

| `--text-secondary` | `#a0a6c0` | Muted text || `--text-secondary` | `#a0a6c0` | Muted text |



### Glassmorphism Style### Glassmorphism Style



- **Glass panels:** Semi-transparent (`rgba(26, 31, 58, 0.7)`) with 10-20px backdrop blur- **Glass panels:** Semi-transparent (`rgba(26, 31, 58, 0.7)`) with 10-20px backdrop blur

- **Borders:** `rgba(255, 255, 255, 0.1)` — 1px subtle white borders on glass surfaces- **Borders:** `rgba(255, 255, 255, 0.1)` — 1px subtle white borders on glass surfaces

- **Glow effects:** `0 0 20px rgba(0, 212, 255, 0.3)` — cyan glow on key elements- **Glow effects:** `0 0 20px rgba(0, 212, 255, 0.3)` — cyan glow on key elements

- **Shadows:** `0 8px 32px rgba(0, 0, 0, 0.37)` — deep ambient shadows- **Shadows:** `0 8px 32px rgba(0, 0, 0, 0.37)` — deep ambient shadows

- **Corner radius:** 12-16px on panels and cards- **Corner radius:** 12-16px on panels and cards



### 🔤 Text Contrast & Readability (MANDATORY)### CORTEX Logo Watermark



All overlaid text **MUST** be clearly legible against the background:- The CORTEX logo (`cortex-logo-128.png`) must appear **embossed in the bottom-right corner** of every image

- Opacity: 20-30% — visible but not distracting

- **Text on dark backgrounds (`#0a0e27`):** Use `#ffffff` (white) or `#00d4ff` (cyan) — never muted gray- Size: ~5-8% of total image width

- **Text on glass panels:** Use `#ffffff` primary text. Secondary/caption text uses `#a0a6c0` **only** when the glass panel background provides sufficient contrast- Style: Embossed/debossed with subtle inner shadow, matching the glass aesthetic

- **Labels on colored elements:** Add a dark pill background (`rgba(10, 14, 39, 0.8)`) behind any text overlaid on glowing, gradient, or particle-heavy areas

- **Heading text:** Always bold weight, minimum 18pt equivalent, with subtle text-shadow (`0 2px 4px rgba(0,0,0,0.5)`) for depth### Typography

- **Code/monospace labels:** JetBrains Mono in `#00d4ff` (cyan) on dark backgrounds, or `#ffffff` on glass panels

- **NEVER** place `#a0a6c0` muted text directly on complex backgrounds (particles, glows, gradients) — it becomes invisible- Headings: **Space Grotesk** (bold) — or nearest geometric sans-serif

- Body text: **Inter** — or nearest clean sans-serif

### CORTEX Logo Watermark- Code/labels: **JetBrains Mono** — or nearest monospace font



- The CORTEX logo (`cortex-logo-128.png`) must appear **embossed in the bottom-right corner** of every image---

- Opacity: 20-30% — visible but not distracting

- Size: ~5-8% of total image width## Prompt Index

- Style: Embossed/debossed with subtle inner shadow, matching the glass aesthetic

| # | File | Subject | Dimensions |

### Typography|---|------|---------|------------|

| 1 | `prompt-01-brain-architecture.md` | Three-tier brain architecture | 1920×1080 |

- Headings: **Space Grotesk** (bold) — or nearest geometric sans-serif| 2 | `prompt-02-orchestrator-galaxy.md` | Orchestrators as a galaxy | 1920×1080 |

- Body text: **Inter** — or nearest clean sans-serif| 3 | `prompt-03-lens-eye.md` | LENS as a diagnostic eye | 1920×1080 |

- Code/labels: **JetBrains Mono** — or nearest monospace font| 4 | `prompt-04-governance-shield.md` | CORE rules as a shield wall | 1920×1080 |

| 5 | `prompt-05-tdd-heartbeat.md` | TDD cycle as a heartbeat | 800×600 |

---| 6 | `prompt-06-mcp-nervous-system.md` | MCP as a nervous system | 1920×1080 |

| 7 | `prompt-07-request-journey.md` | A request's journey through CORTEX | 1920×1080 |

## Prompt Index| 8 | `prompt-08-registry-library.md` | Git-backed registry as an ancient library | 800×600 |

| 9 | `prompt-09-audit-immune-system.md` | Audit pipeline as immune response | 1920×1080 |

| # | File | Subject | Dimensions || 10 | `prompt-10-sweep-completeness.md` | Sweep completeness as forensic investigation | 800×600 |

|---|------|---------|------------|| 11 | `prompt-11-intelligence-matrix-circuit.md` | Intelligence Matrix as a circuit board | 1920×1080 |

| 1 | `prompt-01-brain-architecture.md` | Three-tier intelligence architecture | 1920×1080 || 12 | `prompt-12-workflow-assembly-line.md` | WorkflowEngine as a factory assembly line | 800×600 |

| 2 | `prompt-02-orchestration-ecosystem.md` | Multi-tier orchestrator ecosystem | 1920×1080 || 13 | `prompt-13-rca-memory-shield.md` | RCA Memory Engine as a force field shield | 1920×1080 |

| 3 | `prompt-03-lens-analysis-engine.md` | LENS workspace analysis engine | 1920×1080 |

| 4 | `prompt-04-governance-shield-wall.md` | Tiered governance enforcement | 1920×1080 |---

| 5 | `prompt-05-request-journey-map.md` | A request's full journey through the pipeline | 1920×1080 |

| 6 | `prompt-06-golden-test-pyramid.md` | Golden test scoring, promotion, and end-to-end verification | 1920×1080 |## Cross-Reference: No Overlap with Video Prompts

| 7 | `prompt-07-security-layers.md` | Five-layer shift-left security architecture | 1920×1080 |

| 8 | `prompt-08-extensibility-neural-growth.md` | Extension points and hot-reload capability growth | 1920×1080 |These image prompts focus on **static architectural concepts** — the "what it is" snapshots.  

| 9 | `prompt-09-knowledge-pattern-lattice.md` | Enterprise patterns, knowledge architecture, and learning | 1920×1080 |Video prompts (in `../videos/`) focus on **dynamic flows and processes** — the "how it works" stories.

| 10 | `prompt-10-before-after-transformation.md` | Real-world codebase transformation (anti-patterns → clean architecture) | 1920×1080 |

| Concept | Image Covers | Video Covers |

---|---------|-------------|-------------|

| Brain Tiers | Static 3-layer cross-section | Animated request flowing through all 3 tiers |

## Cross-Reference: Zero Overlap with Video Prompts| Orchestrators | Galaxy map (spatial layout) | Day-in-the-life orchestrator coordination |

| LENS | Eye diagram (anatomy) | Live analysis with results appearing in real-time |

These image prompts focus on **static architectural concepts** — the "what it is" snapshots.| Governance | Shield wall (defense posture) | Rule enforcement catching a violation |

Video prompts (in `../videos/`) focus on **dynamic flows and processes** — the "how it works" stories.| TDD | ECG heartbeat (rhythm) | Full RED→GREEN→REFACTOR cycle animated |

| MCP | Nervous system (anatomy) | Messages flowing through the nervous system |

| Concept | Image Covers | Video Covers || Audit | Immune system (cellular view) | 9-stage pipeline progressing through stages |

|---------|-------------|-------------|

| Brain Tiers | Static 3-layer cross-section anatomy | Animated intelligence making a live decision |---

| Orchestrators | Ecosystem map (spatial layout of tiers) | Orchestrators coordinating on a real request |

| LENS | Diagnostic eye with analyzer segments | Live workspace scan with results appearing |*All prompts reference actual CORTEX architecture verified against live codebase*

| Governance | Shield wall defense posture | Rule enforcement catching a violation live |
| Request Journey | Panoramic station-to-station infographic | Particle tracking through pipeline (animated) |
| Golden Tests | Pyramid with scoring and audit trace | End-to-end test lifecycle from creation to audit |
| Security | Layered defense architecture diagram | Security gates catching a vulnerability |
| Extensibility | Neural growth metaphor (static anatomy) | Building a new capability live |
| Knowledge | Pattern lattice and knowledge graph | Repository onboarding with pattern detection |
| Transformation | Before/after split panel snapshot | Full refactoring session animated |

---

*All prompts reference actual CORTEX capabilities*
