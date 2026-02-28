# Prompt 02 — Multi-Tier Orchestrator Ecosystem

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, text contrast rules, typography, and CORTEX logo watermark rules.

## Prompt

```
Create a stunning top-down view of a galaxy where each star represents an orchestrator in an AI framework's ecosystem.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) — NOT black
- All info panels/legends: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, 10-20px backdrop blur
- Primary glow color: Cyan (#00d4ff) with 0 0 20px rgba(0, 212, 255, 0.3) glow
- Secondary glow: Purple (#7b61ff)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- TEXT CONTRAST: All labels on dark pill backgrounds rgba(10, 14, 39, 0.8). Heading text bold with text-shadow. Star labels in #ffffff or #00d4ff
- Heading font: Space Grotesk (bold). Labels: JetBrains Mono (monospace)
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px, with subtle inner shadow

The galaxy has four distinct spiral arms, each representing a tier:

CORE TIER (bright cyan #00d4ff, closest to center):
- The largest star at the absolute center is "MasterOrchestrator" — glowing brightest with cyan corona
- Surrounding it in a tight orbit: IntentRouter, TDDOrchestrator, EnforcementOrchestrator, WorkflowOrchestrator
- Each star has a tiny JetBrains Mono label on a dark pill background
- Glassmorphic caption panel: "The command center — routes, governs, and executes every request"

DOMAIN TIER (purple #7b61ff, second ring):
- Medium-sized stars: RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator, DashboardOrchestrator
- Spaced evenly in the second spiral arm with purple glow
- Glassmorphic caption panel: "Specialist expertise — each domain has its own orchestrator"

SUPPORT TIER (amber #ffa500, third ring):
- Numerous smaller stars forming the widest arm
- Key stars labeled: VacuumOrchestrator, HealthOrchestrator, SweepCatalogueOrchestrator, OnboardingOrchestrator, DebuggerOrchestrator
- Glassmorphic caption panel: "Infrastructure support — health, cleanup, debugging, and onboarding"

GIT TIER (green #00ff88, outer ring):
- Distant stars in the outermost ring with green glow
- Key stars: SanitizationOrchestrator, PreCommitOrchestrator
- Glassmorphic caption panel: "Version control sentinels — pre-commit hooks, secret scanning, branch hygiene"

Between all stars, show thin glowing connection lines in rgba(0, 212, 255, 0.2) — neural pathways showing how orchestrators communicate through the central hub.

Glassmorphic legend bar at bottom:
"CORTEX Orchestration Ecosystem · Nine Domains · Unified Protocol · Extensible"
Subtitle in white text: "Every request flows from the center outward — each orchestrator has one job, done exceptionally"

Style: Cinematic space visualization with glassmorphism UI overlay panels. NOT cartoonish. Deep navy (#0a0e27) space with cyan/purple nebula accents. Professional keynote quality.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- All orchestrators satisfy a unified protocol via a shared base mixin
- Tiers provide hierarchical separation: core (routing/governance), domain (specialization), support (infrastructure), git (version control)
- MasterOrchestrator is the central hub — all requests flow through it
- The ecosystem grows over time — new orchestrators plug in without changing existing ones
- **No hardcoded count** — the visual density of stars implies a comprehensive ecosystem
