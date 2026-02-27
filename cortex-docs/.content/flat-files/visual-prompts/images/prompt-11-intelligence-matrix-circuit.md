# Prompt 11 — Intelligence Matrix as a Circuit Board

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create a technical illustration of a printed circuit board (PCB) where each component represents an intelligence capability and each trace = a connection in the Intelligence Matrix.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27)
- The PCB rendered in deep navy (#1a1f3a) substrate with cyan (#00d4ff) traces instead of traditional green/gold
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px, subtle inner shadow

THE PCB LAYOUT:

COLUMNS (Intelligence Providers, along top edge):
- 7 chip components in glassmorphic housings with cyan (#00d4ff) LED indicators
- JetBrains Mono labels: "LENS", "Brain Perception", "Brain Reasoning", "Brain Action", "KnowledgeIndexer", "DomainBrain", "URS"
- Each chip glows cyan

ROWS (Intelligence Consumers, along left edge):
- 7 chip components in glassmorphic housings with amber (#ffa500) LED indicators
- JetBrains Mono labels: "TDDOrchestrator", "AuditFix Pipeline", "MCP Tools", "EnforcementOrchestrator", "IntentRouter", "PlanningOrchestrator", "RefactoringOrchestrator"
- Each chip glows amber

THE TRACES (connections on the PCB):
- CRITICAL (P0): Thick bright cyan (#00d4ff) traces with glow, "P0" label
- HIGH (P1): Medium purple (#7b61ff) traces, "P1" label
- MEDIUM (P2): Thin blue (#3b82f6) traces, "P2" label
- MISSING/GAP: Dashed rgba(255,255,255,0.15) traces with "GAP" label

COVERAGE METER (top-right corner, glassmorphic circular gauge):
- "50% Coverage Gate" in Space Grotesk
- Gauge filled to appropriate level with cyan fill
- Muted caption (#a0a6c0): "Like a circuit board QA test — every connection must be verified"

LEGEND PANEL (bottom-left, glassmorphic):
- Cyan line: "CRITICAL (P0) — System breaks without it"
- Purple line: "HIGH (P1) — Reduced capability without it"
- Blue line: "MEDIUM (P2) — Enhanced capability"
- Dashed gray line: "GAP — Not yet wired"

Muted analogy caption:
"Like the wiring in your car's dashboard — every gauge needs a sensor connection."

Glassmorphic footer:
"15×15 Intelligence Matrix · 50% Coverage Gate · cortex/intelligence/cross_cutting/"

Style: Realistic dark PCB photography style with glassmorphism overlay. Cyan traces instead of traditional gold. Deep navy substrate. Engineering-grade precision.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- The Intelligence Matrix lives at `cortex/intelligence/cross_cutting/`
- It ensures all intelligence subsystems are wired to all consumers
- The 50% coverage gate means at least half of possible connections must be active
- Phase 65/66 established the matrix wiring
