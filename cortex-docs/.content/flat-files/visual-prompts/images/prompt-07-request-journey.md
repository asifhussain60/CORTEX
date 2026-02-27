# Prompt 07 — A Request's Journey Through CORTEX

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create a panoramic left-to-right journey map showing a single developer request traveling through 7 stages of the CORTEX pipeline, styled like an illustrated airport terminal or subway line map.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with subtle horizontal grid lines in rgba(255,255,255,0.02)
- All station panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px, subtle inner shadow

The "request" is a small glowing cyan (#00d4ff) orb that transforms at each stage. A continuous glowing cyan line connects all stations left-to-right.

STAGE -1 — REQUEST PRE-PROCESSOR (far left):
- Glassmorphic station panel with purple (#7b61ff) accent border on top
- The orb enters as a plain white sphere, exits wrapped in a golden (#ffa500) governance shield
- JetBrains Mono label: "RequestRephraseOrchestrator · 15-35ms"
- Muted caption (#a0a6c0): "Like a GPS recalculating your route before you start driving"

STAGE 0 — MCP GATEWAY:
- Glassmorphic station with cyan accent border
- Orb passes through a glowing cyan archway
- JetBrains Mono label: "MCP Gateway · 5-15ms"
- Muted caption: "Boarding pass scanned — you're cleared to proceed"

STAGE 1 — INTENT CLASSIFICATION:
- Glassmorphic station with blue (#3b82f6) accent border
- A sorting mechanism with 12 labeled chutes below: IMPLEMENT, FIX, REFACTOR, AUDIT, etc.
- Orb gets a colored tag and drops into one chute
- JetBrains Mono label: "IntentRouter · 20-40ms"
- Muted caption: "Like a mail sorting center — your letter goes to the right department"

STAGE 2 — LENS ANALYSIS:
- Glassmorphic station with multi-color accent (the largest station)
- Orb enters a circular chamber surrounded by 10 colored laser beams (one per analyzer)
- Holographic results display above
- JetBrains Mono label: "LENS · 300-800ms"
- Muted caption: "Like a full-body MRI — 10 scanners reveal everything at once"

STAGE 3 — BRAIN INTELLIGENCE:
- Glassmorphic station with purple accent
- Three ascending platforms: Perception (cyan) → Reasoning (purple) → Action (amber)
- Orb climbs each, gaining complexity
- JetBrains Mono label: "Brain Tiers · 50-200ms"
- Muted caption: "Like climbing a decision tree — each level adds insight"

STAGE 4 — GOVERNANCE GATE:
- Glassmorphic station with red (#ff4444) / green (#00ff88) accent
- Checkpoint with 10 guard icons checking credentials
- Some ✅, some 🔴 BLOCKED paths
- JetBrains Mono label: "EnforcementOrchestrator · <150ms"
- Muted caption: "Like TSA security — no exceptions, no shortcuts"

STAGE 5 — EXECUTION & DELIVERY:
- Glassmorphic station with green (#00ff88) accent (rightmost)
- Launch pad with RED-GREEN-REFACTOR rings around the orb
- Results in a VS Code editor mockup with glassmorphic frame
- JetBrains Mono label: "TDDOrchestrator · Variable"
- Muted caption: "Liftoff — your solution is delivered inline, with an audit trail"

TIMELINE BAR (glassmorphic footer):
"Total: 450ms - 1.2s (typical) · Every step auditable · Every step reversible"

Style: Illustrated journey infographic with dark glassmorphism. Each station = a distinct frosted glass panel. Colors progress from cool (left/purple) to warm (right/green). Cyan glow throughout.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- This maps to the pipeline in the CORTEX "How It Works" documentation page
- Timing values are from live system measurements
- The journey is sequential — each stage must complete before the next begins
- All stages emit audit markers to a persistent activity log
