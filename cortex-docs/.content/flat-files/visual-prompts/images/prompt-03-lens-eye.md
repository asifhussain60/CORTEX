# Prompt 03 — LENS as a Diagnostic Eye

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create a dramatic technical illustration of a single large human eye, reimagined as a code analysis engine called "LENS" (Language → Examination → Navigation → Synthesis).

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with subtle radial gradient toward rgba(26, 31, 58, 0.5) at edges
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, 10-20px backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px, subtle inner shadow

The eye is rendered in cross-section:

THE IRIS — divided into 10 colored segments like a precision instrument dial:
1. AST Analyzer (cyan #00d4ff) — "Code structure, classes, functions"
2. Git History (green #00ff88) — "Change frequency, author patterns"
3. Comment Analyzer (light cyan rgba(0,212,255,0.6)) — "Documentation coverage, TODOs"
4. Import Analyzer (purple #7b61ff) — "Dependency graph, circular imports"
5. Security Scanner (red #ff4444) — "SQL injection, XSS, credentials"
6. Pattern Detector (amber #ffa500) — "Framework signatures, architecture"
7. Metrics Calculator (blue #3b82f6) — "Complexity, coupling, cohesion"
8. Domain Analyzer (teal rgba(0,212,255,0.4)) — "Business domain detection"
9. Quality Assessor (warm amber rgba(255,165,0,0.8)) — "Test quality scoring 0-9"
10. Knowledge Resolver (white #ffffff) — "Context assembly, best practices"

Each iris segment emits a thin beam of its color inward toward the pupil with a subtle glow effect.

THE PUPIL — a dark center (#0a0e27) labeled "SYNTHESIS" in Space Grotesk where all 10 beams converge into a single cyan (#00d4ff) point of light. From this convergence, a glassmorphic JSON-like card emerges labeled "Unified Context".

THE SCLERA — shows flowing binary/code characters in rgba(255,255,255,0.05), suggesting the eye is "reading" source code.

FOUR CORNER PANELS — glassmorphic panels with blur:
- Top-left: "L — Language: What language/framework is this?"
- Top-right: "E — Examination: What patterns and issues exist?"
- Bottom-left: "N — Navigation: How do components connect?"
- Bottom-right: "S — Synthesis: What does it all mean together?"

Glassmorphic footer bar: "10 Analyzers · 300-800ms · Parallel Execution"
Muted caption (#a0a6c0): "Like an ophthalmologist examining your eye with 10 instruments simultaneously"

Style: Dark glassmorphism. Anatomical precision meets tech diagram. Frosted glass panels. Cyan glow accents.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- LENS is CORTEX's workspace analysis engine
- The 10 analyzers run in parallel (not sequentially)
- Synthesis produces a unified context object consumed by the Brain tiers
- Typical analysis completes in 300-800ms
