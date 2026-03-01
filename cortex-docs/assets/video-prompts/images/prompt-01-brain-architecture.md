# Prompt 01 — Three-Tier Brain Architecture

## Target Tool
Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```text
Create a highly detailed, cinematic technical illustration of a three-tier cognitive architecture represented as a translucent human brain cross-section.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with subtle grid pattern (rgba(255,255,255,0.03) lines)
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12–16px corner radius, 10–20px backdrop blur
- Primary accent glow: Cyan (#00d4ff) with 0 0 20px rgba(0, 212, 255, 0.3) glow
- Secondary accent: Purple (#7b61ff) for decorative highlights
- Shadows on floating elements: 0 8px 32px rgba(0, 0, 0, 0.37)
- TEXT CONTRAST: All text on dark backgrounds in #ffffff or #00d4ff. Labels on glowing areas must have a dark pill background rgba(10, 14, 39, 0.8). Headings bold with text-shadow 0 2px 4px rgba(0,0,0,0.5)
- Heading font: Space Grotesk (bold, geometric sans-serif)
- Label font: JetBrains Mono (monospace, cyan #00d4ff)
- Body font: Inter (clean sans-serif)
- CORTEX logo watermark: Embossed at 20–30% opacity in the bottom-right corner, ~80px wide, with subtle inner shadow matching the glass aesthetic

The brain is divided into three glowing layers, each clearly labeled:
BOTTOM LAYER — "PERCEPTION" (colored cyan #00d4ff):
- Show 9 small geometric icons representing enterprise pattern detectors (mediator, strategy, observer, factory, template-method, chain-of-responsibility, adapter, repository, command)
- Each icon has a thin cyan connection line flowing upward
- Glassmorphic label panel: "Pattern Recognition · Confidence Scoring · 9 Enterprise Patterns"
- Daily-life analogy in white text on dark pill: "Like your eyes identifying objects in a room"

MIDDLE LAYER — "REASONING" (colored purple #7b61ff):
- Show a glowing decision tree with branching paths
- Each branch has a percentage label (94%, 87%, 72%) representing strategy success rates in cyan text
- Strategies labeled in JetBrains Mono: "tdd-incremental", "refactor-extract-service", "security-audit-first"
- Glassmorphic label panel: "Strategy Selection · Historical Learning · Confidence Ranking"
- Daily-life analogy in white text on dark pill: "Like choosing the fastest route on a GPS based on traffic history"

TOP LAYER — "ACTION" (colored amber #ffa500):
- Show a sequential pipeline of numbered steps (1→2→3→4→5) with small checkboxes
- Between each step, show a tiny red(#ff4444)-green(#00ff88)-refactor(#3b82f6) cycle icon
- Small rollback arrows pointing backward from each step
- Glassmorphic label panel: "Execution Planning · TDD Gates · Rollback Points"
- Daily-life analogy in white text on dark pill: "Like a chef following a recipe — each step verified before the next"

Between the layers, show flowing particle streams with cyan (#00d4ff) glow (data flowing upward from Perception through Reasoning to Action).
At the very top, a small VS Code editor icon emitting a request downward into the brain.

At the very bottom, a glassmorphic footer bar:
"CORTEX Intelligence Engine — Perception → Reasoning → Action"
Style: Dark glassmorphism UI aesthetic. Frosted glass panels with blur. Subtle cyan glow accents. Professional enough for a conference keynote slide. NOT photorealistic — clean technical illustration.

Dimensions: 1920×1080
Format: PNG with deep navy background (#0a0e27)
```

## Notes for Generation

- This image will be used as the hero image on the Intelligence Architecture documentation page.
- This image depicts how CORTEX processes intelligence through three cognitive tiers.
- The three tiers correspond to: Perception (pattern recognition), Reasoning (strategy selection), and Action (execution planning).
- Confidence scores are illustrative UI elements; **don’t claim they are measured metrics** unless provided as a source.
- The 9 enterprise patterns are formally registered, validated, and scored at startup.
- **No hardcoded counts beyond “9 patterns” in this image prompt** — the growing pattern library is implied through visual density.
BOTTOM LAYER — "PERCEPTION" (colored cyan #00d4ff):- Show 9 small geometric icons representing enterprise pattern detectors (mediator, strategy, observer, factory, template-method, chain-of-responsibility, adapter, repository, command)

- Show small geometric icons representing enterprise pattern detectors (mediator, strategy, observer, factory, adapter, repository, command, and more)- Each icon has a thin cyan connection line flowing upward

- Each icon has a thin cyan connection line flowing upward- Glassmorphic label panel: "Pattern Recognition · Confidence Scoring · 9 Enterprise Patterns"

- Glassmorphic label panel: "Pattern Recognition · Confidence Scoring · Enterprise Pattern Detection"- Daily-life analogy in muted text (#a0a6c0): "Like your eyes identifying objects in a room"

- Daily-life analogy in white text on dark pill: "Like your eyes identifying objects in a room"

MIDDLE LAYER — "REASONING" (colored purple #7b61ff):

MIDDLE LAYER — "REASONING" (colored purple #7b61ff):- Show a glowing decision tree with branching paths

- Show a glowing decision tree with branching paths- Each branch has a percentage label (94%, 87%, 72%) representing strategy success rates in cyan text

- Each branch has a percentage label representing strategy success rates in cyan text on dark pills- Strategies labeled in JetBrains Mono: "tdd-incremental", "refactor-extract-service", "security-audit-first"

- Strategies labeled in JetBrains Mono: "tdd-incremental", "refactor-extract-service", "security-audit-first"- Glassmorphic label panel: "Strategy Selection · Historical Learning · Confidence Ranking"

- Glassmorphic label panel: "Strategy Selection · Historical Learning · Confidence Ranking"- Daily-life analogy in muted text: "Like choosing the fastest route on a GPS based on traffic history"

- Daily-life analogy in white text on dark pill: "Like choosing the fastest route on a GPS based on traffic history"

TOP LAYER — "ACTION" (colored amber #ffa500):

TOP LAYER — "ACTION" (colored amber #ffa500):- Show a sequential pipeline of numbered steps (1→2→3→4→5) with small checkboxes

- Show a sequential pipeline of numbered steps (1→2→3→4→5) with small checkboxes- Between each step, show a tiny red(#ff4444)-green(#00ff88)-refactor(#3b82f6) cycle icon

- Between each step, show a tiny red(#ff4444)-green(#00ff88)-refactor(#3b82f6) cycle icon- Small rollback arrows pointing backward from each step

- Small rollback arrows pointing backward from each step- Glassmorphic label panel: "Execution Planning · TDD Gates · Rollback Points"

- Glassmorphic label panel: "Execution Planning · TDD Gates · Rollback Points"- Daily-life analogy in muted text: "Like a chef following a recipe — each step verified before the next"

- Daily-life analogy in white text on dark pill: "Like a chef following a recipe — each step verified before the next"

Between the layers, show flowing particle streams with cyan (#00d4ff) glow (data flowing upward from Perception through Reasoning to Action).

Between the layers, show flowing particle streams with cyan (#00d4ff) glow (data flowing upward from Perception through Reasoning to Action).

At the very top, a small VS Code editor icon emitting the request downward into the brain.

At the very top, a small VS Code editor icon emitting the request downward into the brain.At the very bottom, a glassmorphic footer bar: "CORTEX Intelligence Engine — Perception → Reasoning → Action"

At the very bottom, a glassmorphic footer bar: "CORTEX Intelligence Engine — Perception → Reasoning → Action"

Style: Dark glassmorphism UI aesthetic. Frosted glass panels with blur. Subtle cyan glow accents. Professional enough for a conference keynote slide. NOT photorealistic — clean technical illustration.

Style: Dark glassmorphism UI aesthetic. Frosted glass panels with blur. Subtle cyan glow accents. Professional enough for a conference keynote slide. NOT photorealistic — clean technical illustration.

Dimensions: 1920×1080

Dimensions: 1920×1080Format: PNG with deep navy background (#0a0e27)

Format: PNG with deep navy background (#0a0e27)```

```

## Notes for Generation

## Notes for Generation- This image will be used as the hero image on the Intelligence Architecture documentation page

- This image depicts how CORTEX processes intelligence through three cognitive tiers- The three tiers correspond to: Perception (pattern recognition), Reasoning (strategy selection), and Action (execution planning)

- The tiers are: Perception (pattern matching), Reasoning (strategy selection), Action (execution planning)- Confidence scores in the Reasoning layer reflect real strategy success rates tracked between 0.0 and 1.0

- Confidence scores reflect real strategy success rates tracked continuously- The 9 enterprise patterns are formally registered and validated at startup

- Enterprise patterns are formally registered, validated, and scored at startup
- **No hardcoded counts** — the growing pattern library is implied through visual density
