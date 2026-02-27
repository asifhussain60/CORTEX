# Prompt 02 — 51 Orchestrators as a Galaxy

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create a stunning top-down view of a galaxy where each star represents one of 51 orchestrators in an AI framework.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) — NOT black
- All info panels/legends: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, 10-20px backdrop blur
- Primary glow color: Cyan (#00d4ff) with 0 0 20px rgba(0, 212, 255, 0.3) glow
- Secondary glow: Purple (#7b61ff)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- Heading font: Space Grotesk (bold). Labels: JetBrains Mono (monospace)
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px, with subtle inner shadow

The galaxy has four distinct spiral arms, each representing a tier:

CORE TIER (17 stars, bright cyan #00d4ff, closest to center):
- The largest star at the absolute center is "MasterOrchestrator" — glowing brightest with cyan (#00d4ff) corona
- Surrounding it in a tight orbit: IntentRouter, TDDOrchestrator, EnforcementOrchestrator, WorkflowOrchestrator
- Each star has a tiny JetBrains Mono label
- Glassmorphic caption panel: "The command center — like Mission Control at NASA"

DOMAIN TIER (7 stars, purple #7b61ff, second ring):
- Medium-sized stars: RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator, DashboardOrchestrator
- Spaced evenly in the second spiral arm with purple glow
- Glassmorphic caption panel: "Specialist departments — like hospital wards for different conditions"

SUPPORT TIER (23 stars, amber #ffa500, third ring):
- Smaller but numerous stars forming the widest arm
- Key stars labeled: VacuumOrchestrator, HealthOrchestrator, SweepCatalogueOrchestrator, OnboardingOrchestrator
- Glassmorphic caption panel: "The maintenance crew — like janitors, security guards, and nurses"

GIT TIER (4 stars, green #00ff88, outer ring):
- Four distant stars in the outermost ring with green glow
- Glassmorphic caption panel: "Version control sentinels — like librarians tracking every checkout"

Between all stars, show thin glowing connection lines in rgba(0, 212, 255, 0.2) — like neural pathways showing how orchestrators communicate through the MasterOrchestrator hub.

Glassmorphic legend bar at bottom:
"CORTEX Orchestration Galaxy · 51 Wired · 4 Tiers · IOrchestrator Protocol"
Subtitle in muted text (#a0a6c0): "Every request flows from the center outward — like ripples in a pond"

Style: Cinematic space visualization with glassmorphism UI overlay panels. NOT cartoonish. Deep navy (#0a0e27) space with cyan/purple nebula accents. Professional keynote quality.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- The 51 orchestrators all satisfy the IOrchestrator protocol via a shared base mixin
- Tier distribution: 17 core, 7 domain, 23 support, 4 git
- Every orchestrator is formally wired with declared priority, health endpoint, and MCP adapter
- MasterOrchestrator is the central hub — all requests flow through it
