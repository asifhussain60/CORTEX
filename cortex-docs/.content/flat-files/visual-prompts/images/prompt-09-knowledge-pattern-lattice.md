# Prompt 09 — Knowledge & Pattern Lattice

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, text contrast rules, typography, and CORTEX logo watermark rules.

## Prompt

```
Create a technical illustration of an interconnected knowledge lattice — a crystalline structure where each node is a piece of institutional knowledge and each connection represents a learned relationship.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with subtle crystalline texture in rgba(0, 212, 255, 0.02)
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff). Success: Green (#00ff88). Warning: Amber (#ffa500)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- TEXT CONTRAST: All labels in #ffffff bold on dark pill backgrounds. Pattern names in cyan #00d4ff JetBrains Mono. Confidence percentages in #00ff88 green
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px

LEFT SECTION — "Enterprise Patterns" (glassmorphic panel, purple #7b61ff accent):

Show a honeycomb grid of pattern icons, each in a glassmorphic hexagonal cell:
- Mediator — "Orchestrators communicate through a central hub"
- Strategy — "Best approach selected from ranked alternatives"
- Observer — "Events published, subscribers react"
- Factory — "Objects created through canonical entry points"
- Template Method — "Lifecycle defined in base, steps customized by subclasses"
- Chain of Responsibility — "Enforcement agents check rules sequentially"
- Adapter — "Orchestrator interfaces adapted to MCP protocol"
- Repository — "YAML-backed configuration managed through a repository pattern"
- Command — "Workflow steps as executable command objects"

Each cell has a confidence bar (0.0–1.0 scale):
- High confidence (≥ 0.9): Bright green bar, "Strong match"
- Medium confidence (0.7–0.89): Amber bar, "Likely match"
- Low confidence (< 0.5): Dim bar, "Insufficient evidence"

RIGHT SECTION — "Knowledge Architecture" (glassmorphic panel, green #00ff88 accent):

Two knowledge stores visualized as interconnected shelves:

SHELF 1 — "Pattern Registry" (upper):
- YAML files glowing with pattern signatures
- Label: "Registered patterns with detection rules and associated strategies"
- Arrows connecting to the Perception tier

SHELF 2 — "Knowledge Base" (lower):
- Company-specific knowledge files, best practices, domain expertise
- Label: "Institutional wisdom — grows with every project interaction"
- Arrows connecting to the Reasoning tier

CENTER — "The Learning Loop" (connecting left and right):
- A circular flow diagram connecting:
  "Pattern Detected" → "Strategy Selected" → "Outcome Measured" → "Confidence Updated" → back to "Pattern Detected"
- Label: "Unified Reinforcement Signal — the system learns from every outcome"
- Successful outcomes: green particles flowing in the loop
- Failed outcomes: red particles flowing, confidence decreasing

BOTTOM SECTION — "Prevention Gate" (glassmorphic panel, red #ff4444 to green #00ff88 gradient):
- Three escalation levels:
  1. Advisory (green eye icon): "First occurrence — information surfaced"
  2. Warning (amber triangle): "Second occurrence — explicit warning"
  3. Blocking (red stop sign): "Repeated critical failure — operation halted"
- Label: "Root Cause Analysis transforms past failures into future prevention rules"

Glassmorphic footer:
"Enterprise Patterns · Knowledge Base · Learning Loop · Prevention Gate"
Caption: "The longer CORTEX runs, the smarter it gets — every outcome teaches the next decision"

Style: Crystalline lattice structure with dark glassmorphism. Interconnected nodes. Professional knowledge-management visualization. Cyan/purple/green highlights.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- CORTEX recognizes enterprise patterns and uses them to guide strategy selection
- The knowledge base contains both framework-level and company-specific knowledge
- The learning loop (URS — Unified Reinforcement Signal) updates confidence scores after every operation
- The Prevention Gate uses root cause analysis to stop recurring mistakes
- This image covers knowledge, patterns, and learning — three capabilities that were missing from the original set
