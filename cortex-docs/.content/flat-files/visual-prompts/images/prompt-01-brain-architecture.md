# Prompt 01 — Three-Tier Brain Architecture

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create a highly detailed, cinematic technical illustration of a three-tier cognitive architecture represented as a translucent human brain cross-section.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with subtle grid pattern (rgba(255,255,255,0.03) lines)
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, 10-20px backdrop blur
- Primary accent glow: Cyan (#00d4ff) with 0 0 20px rgba(0, 212, 255, 0.3) glow
- Secondary accent: Purple (#7b61ff) for decorative highlights
- Shadows on all floating elements: 0 8px 32px rgba(0, 0, 0, 0.37)
- Heading font: Space Grotesk (bold, geometric sans-serif)
- Label font: JetBrains Mono (monospace)
- Body font: Inter (clean sans-serif)
- CORTEX logo watermark: Embossed at 20-30% opacity in the bottom-right corner, ~80px wide, with subtle inner shadow matching the glass aesthetic

The brain is divided into three glowing layers, each clearly labeled:

BOTTOM LAYER — "PERCEPTION" (colored cyan #00d4ff):
- Show 9 small geometric icons representing enterprise pattern detectors (mediator, strategy, observer, factory, template-method, chain-of-responsibility, adapter, repository, command)
- Each icon has a thin cyan connection line flowing upward
- Glassmorphic label panel: "Pattern Recognition · Confidence Scoring · 9 Enterprise Patterns"
- Daily-life analogy in muted text (#a0a6c0): "Like your eyes identifying objects in a room"

MIDDLE LAYER — "REASONING" (colored purple #7b61ff):
- Show a glowing decision tree with branching paths
- Each branch has a percentage label (94%, 87%, 72%) representing strategy success rates in cyan text
- Strategies labeled in JetBrains Mono: "tdd-incremental", "refactor-extract-service", "security-audit-first"
- Glassmorphic label panel: "Strategy Selection · Historical Learning · Confidence Ranking"
- Daily-life analogy in muted text: "Like choosing the fastest route on a GPS based on traffic history"

TOP LAYER — "ACTION" (colored amber #ffa500):
- Show a sequential pipeline of numbered steps (1→2→3→4→5) with small checkboxes
- Between each step, show a tiny red(#ff4444)-green(#00ff88)-refactor(#3b82f6) cycle icon
- Small rollback arrows pointing backward from each step
- Glassmorphic label panel: "Execution Planning · TDD Gates · Rollback Points"
- Daily-life analogy in muted text: "Like a chef following a recipe — each step verified before the next"

Between the layers, show flowing particle streams with cyan (#00d4ff) glow (data flowing upward from Perception through Reasoning to Action).

At the very top, a small VS Code editor icon emitting the request downward into the brain.
At the very bottom, a glassmorphic footer bar: "cortex/intelligence/ — Perception → Reasoning → Action"

Style: Dark glassmorphism UI aesthetic. Frosted glass panels with blur. Subtle cyan glow accents. Professional enough for a conference keynote slide. NOT photorealistic — clean technical illustration.

Dimensions: 1920×1080
Format: PNG with deep navy background (#0a0e27)
```

## Notes for Generation
- This image will be used as the hero image on the Intelligence Architecture documentation page
- The three tiers correspond to: `cortex/intelligence/perception/`, `cortex/intelligence/reasoning/`, `cortex/intelligence/action/`
- Confidence scores are real: the system tracks strategy success rates between 0.0–1.0
- The 9 enterprise patterns are registered in `cortex-registry/patterns/`
