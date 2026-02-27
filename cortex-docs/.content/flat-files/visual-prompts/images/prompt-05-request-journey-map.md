# Prompt 05 — A Request's Journey Through CORTEX

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, text contrast rules, typography, and CORTEX logo watermark rules.

## Prompt

```
Create a panoramic left-to-right journey map showing a single developer request traveling through the stages of the CORTEX pipeline, styled like an illustrated subway line map.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with subtle horizontal grid lines in rgba(255,255,255,0.02)
- All station panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- TEXT CONTRAST: Station names in #ffffff bold Space Grotesk on dark pill backgrounds. Timing labels in cyan #00d4ff JetBrains Mono. Analogy captions in #ffffff Inter on dark pills
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px, subtle inner shadow

A glowing cyan (#00d4ff) line connects all stations left-to-right. A small glowing cyan orb sits at the start, representing the user's request.

STATION 1 — MCP GATEWAY (cyan accent border):
- Orb passes through a glowing cyan archway
- Label: "MCP Gateway" · "Request received via VS Code"
- Caption on dark pill: "Boarding pass scanned — you're cleared to proceed"

STATION 2 — INTENT CLASSIFICATION (blue #3b82f6 accent):
- A sorting mechanism with labeled chutes: IMPLEMENT, FIX, REFACTOR, AUDIT, DEBUG, PLAN
- Orb gets a colored tag and drops into one chute
- Label: "IntentRouter" · "Classifies your request"
- Caption: "Like a mail sorting center — your request goes to the right specialist"

STATION 3 — LENS ANALYSIS (multi-color accent, largest station):
- Orb enters a circular chamber surrounded by colored laser beams (one per analyzer)
- Holographic results display above
- Label: "LENS" · "Parallel workspace scan"
- Caption: "Like a full-body MRI — multiple scanners reveal everything at once"

STATION 4 — BRAIN INTELLIGENCE (purple accent):
- Three ascending platforms: Perception (cyan) → Reasoning (purple) → Action (amber)
- Orb climbs each, gaining complexity
- Label: "Intelligence Tiers" · "Pattern matching → Strategy → Plan"
- Caption: "Like climbing a decision tree — each level adds insight"

STATION 5 — GOVERNANCE GATE (red/green accent):
- Checkpoint with guard icons checking credentials
- Some ✅ pass, some 🔴 BLOCKED paths
- Label: "Enforcement Engine"
- Caption: "Like security screening — no exceptions, no shortcuts"

STATION 6 — TDD EXECUTION (green #00ff88 accent):
- Launch pad with RED-GREEN-REFACTOR rings around the orb
- Results in a VS Code editor mockup with glassmorphic frame
- Label: "TDD Cycle" · "Test first, implement, refactor"
- Caption: "Quality built into the assembly line"

STATION 7 — DELIVERY & AUDIT TRAIL (green accent, rightmost):
- Commit icon with AC_COMPLETE ✅ badge
- Activity log icon showing the persistent audit trail
- Label: "Governed Commit" · "Auditable, traceable, reversible"
- Caption: "Signed, sealed, delivered, and logged"

TIMELINE BAR (glassmorphic footer):
"Every step auditable · Every step reversible · Typical: under 2 seconds"

Style: Illustrated journey infographic with dark glassmorphism. Each station = a distinct frosted glass panel. Colors progress from cool (left) to warm (right/green). Cyan glow line throughout.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- This maps the complete pipeline from user input to governed commit
- Timing values reflect real system measurements — most requests complete in under two seconds
- All stages emit audit markers to a persistent activity log (SQLite)
- The journey is sequential — each stage must complete before the next begins
