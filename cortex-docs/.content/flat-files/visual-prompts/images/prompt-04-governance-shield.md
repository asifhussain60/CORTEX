# Prompt 04 — 38 CORE Rules as a Shield Wall

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create an epic technical illustration of a medieval shield wall formation, reimagined as a software governance system with 38 shields. The scene is viewed from the front showing a fortress gate (representing a code repository).

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with dramatic cyan (#00d4ff) uplighting from below
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37) on floating panels
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px, subtle inner shadow

SHIELD ROWS:

ROW 1 — TIER 0: SKULL (10 shields, glowing cyan #00d4ff with amber #ffa500 emblems):
- Large, imposing shields in the front row with cyan aura
- Shield emblems in JetBrains Mono: "CORE-002", "CORE-008", "CORE-011", "CORE-028", "CORE-035", "CORE-049", "CORE-064"
- Glassmorphic caption: "Immutable laws — like the Constitution. Cannot be overridden by anyone."

ROW 2 — TIER 1: BUSINESS (8 shields, purple #7b61ff):
- Medium shields with business rule emblems
- Glassmorphic caption: "Company standards — like office dress code. Set by leadership."

ROW 3 — TIER 2: ENGINEERING (12 shields, blue #3b82f6):
- Slightly smaller shields with technical standard emblems
- Glassmorphic caption: "Team conventions — like a family's house rules."

ROW 4 — TIER 3: LEARNED (8 shields, muted cyan rgba(0,212,255,0.4), semi-translucent glass):
- Glassmorphic semi-transparent shields that glow brighter with use
- Glassmorphic caption: "Patterns learned from experience — like muscle memory."

ABOVE THE SHIELD WALL:
- Glassmorphic banner: "EnforcementOrchestrator" in Space Grotesk
- Subtitle: "10 Enforcement Agents · Pre-Commit · CI · Runtime"

INCOMING ARROWS approaching the gate:
- ✅ Green (#00ff88) checkmark — passing all shields
- 🔴 Red (#ff4444) X — blocked by a shield

PRECEDENCE ARROW (right side, glassmorphic panel):
"Tier 0 WINS → Tier 1 → Tier 2 → Tier 3"
Caption in muted text (#a0a6c0): "When rules conflict, the highest tier always wins — like federal law overriding city ordinances"

Glassmorphic footer: "38 CORE Rules · 4 Tiers · Zero Violations Reach Production"

Style: Dramatic composition mixing medieval imagery with dark glassmorphism tech aesthetic. Cyan glow on shields. Frosted glass info panels. Keynote-ready.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- Rules are defined in `cortex-registry/core/tier0-skull/skull-rules.yaml`
- EnforcementOrchestrator coordinates 10 enforcement agents
- Precedence: Tier 0 (immutable) > Tier 1 (business) > Tier 2 (engineering) > Tier 3 (learned)
- Enforcement happens at three points: pre-commit hooks, CI pipeline, and runtime
