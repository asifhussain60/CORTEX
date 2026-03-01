# Prompt 04 — Tiered Governance Shield Wall

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, text contrast rules, typography, and CORTEX logo watermark rules.

## Prompt

```
Create an epic technical illustration of a medieval shield wall formation, reimagined as a software governance system. The scene is viewed from the front showing a fortress gate (representing a code repository).

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with dramatic cyan (#00d4ff) uplighting from below
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37) on floating panels
- TEXT CONTRAST: Shield labels in #ffffff bold on dark pill backgrounds. Caption text in #ffffff with text-shadow. Rule IDs in cyan #00d4ff JetBrains Mono
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px, subtle inner shadow

SHIELD ROWS — arranged in ascending tiers:

ROW 1 — TIER 0: IMMUTABLE (front row, glowing cyan #00d4ff with amber #ffa500 emblems):
- Large, imposing shields in the front row with cyan aura
- Key shield emblems: "TDD Mandatory", "Type Hints", "No Duplicates", "Sweep Completeness"
- Glassmorphic caption: "Immutable laws — like the Constitution. Cannot be overridden by anyone."

ROW 2 — TIER 1: BUSINESS (purple #7b61ff):
- Medium shields with business rule emblems
- Glassmorphic caption: "Company standards — set by leadership. Customize for your organization."

ROW 3 — TIER 2: ENGINEERING (blue #3b82f6):
- Slightly smaller shields with technical standard emblems
- Glassmorphic caption: "Team conventions — the agreed-upon engineering practices."

ROW 4 — TIER 3: LEARNED (muted cyan, semi-translucent glass):
- Glassmorphic semi-transparent shields that glow brighter with use
- Glassmorphic caption: "Patterns learned from experience — grow stronger over time."

ABOVE THE SHIELD WALL:
- Glassmorphic banner: "Enforcement Engine" in Space Grotesk bold
- Subtitle in white: "Multiple Enforcement Agents · Pre-Commit · CI · Runtime"

INCOMING ARROWS approaching the gate:
- ✅ Green (#00ff88) arrow passing all shields — clean commit
- 🔴 Red (#ff4444) arrow blocked by a shield — violation detected

PRECEDENCE ARROW (right side, glassmorphic panel):
"Tier 0 WINS → Tier 1 → Tier 2 → Tier 3"
Caption in white on dark pill: "When rules conflict, the highest tier always wins — like federal law overriding city ordinances"

Glassmorphic footer: "Tiered Governance · Automated Enforcement · Zero Violations Reach Production"

Style: Dramatic composition mixing medieval imagery with dark glassmorphism tech aesthetic. Cyan glow on shields. Frosted glass info panels. Keynote-ready.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- Governance rules are defined in YAML and organized by tier
- Enforcement happens at three checkpoints: pre-commit hooks, CI pipeline, and runtime
- Precedence: Tier 0 (immutable) > Tier 1 (business) > Tier 2 (engineering) > Tier 3 (learned)
- Companies can add their own rules at Tier 1 and Tier 2 without modifying the framework
- **No hardcoded rule count** — the wall implies comprehensive coverage through visual density
