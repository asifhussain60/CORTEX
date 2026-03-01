# Prompt 10 — Before/After Codebase Transformation

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, text contrast rules, typography, and CORTEX logo watermark rules.

## Prompt

```
Create a dramatic split-screen illustration showing a codebase BEFORE and AFTER CORTEX transformation, styled as a building restoration project.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27)
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Danger: Red (#ff4444). Success: Green (#00ff88)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- TEXT CONTRAST: All labels in #ffffff bold on dark pill backgrounds. Anti-pattern names in red #ff4444. Fix names in green #00ff88. Section headers in #ffffff Space Grotesk bold with text-shadow
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px
- A bold vertical dividing line through the center: left side slightly red-tinted, right side slightly cyan-tinted

LEFT SIDE — "BEFORE" (red-tinted, dim, chaotic):
Header in Space Grotesk: "Before CORTEX" with red (#ff4444) underline

Show a crumbling code building with visible anti-patterns:

1. "God Classes" (red badge) — A massive, bloated class icon taking up too much space, with complexity metrics showing dangerously high numbers
2. "No Tests" (red badge) — Empty test directory, broken test tube icon
3. "Hardcoded Credentials" (red flashing) — API keys visible in a config file panel
4. "Circular Imports" (red arrows) — Tangled dependency arrows forming a loop
5. "Mixed Naming" (amber badge) — Files showing camelCase, PascalCase, snake_case mixed
6. "No Documentation" (gray badge) — Empty docstring panels
7. "Duplicated Logic" (red badge) — Same code block shown in three different files

At the bottom: A glassmorphic "health card" showing:
- Test Coverage: Not established
- Type Hint Coverage: Inconsistent
- Security Issues: Critical findings present
- Governance: Not enforced

RIGHT SIDE — "AFTER" (cyan-tinted, vibrant, organized):
Header in Space Grotesk: "After CORTEX" with green (#00ff88) underline

Show the same building, now restored and glowing:

1. "Clean Architecture" (green badge) — Well-separated modules with clear boundaries
2. "Comprehensive Tests" (green badge) — Full test directory with golden test badges
3. "Secrets Removed" (green badge) — Config file with environment variable references
4. "Clean Dependencies" (green badge) — One-directional arrows, no loops
5. "Consistent Naming" (green badge) — All files in uniform snake_case
6. "Full Documentation" (green badge) — Docstring panels filled with descriptions
7. "Single Canonical" (green badge) — One implementation, properly abstracted

At the bottom: A glassmorphic "health card" showing:
- Test Coverage: High confidence (green)
- Type Hint Coverage: Consistent (green)
- Security Issues: No critical findings (green)
- Governance: Fully enforced ✅

CENTER DIVIDER — CORTEX logo with arrows pointing right:
- "LENS Scan → Challenge → Refactor → Govern"
- Each step has a small icon

BOTTOM FOOTER (glassmorphic, spanning both sides):
"From anti-patterns to production-ready · LENS analysis identifies · TDD enforces · Governance protects"
Caption: "The same codebase. The same team. Different discipline."

Style: Dramatic before/after split. Left side dim, chaotic, red-tinted. Right side vibrant, organized, cyan-tinted. The contrast tells the story. Dark glassmorphism throughout. Keynote-ready.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- This image shows CORTEX's real-world value proposition — transforming messy codebases into governed, tested, production-ready systems
- The anti-patterns on the left are all things CORTEX actually detects and remediates
- The "after" metrics are achievable — CORTEX teams typically reach these levels
- The Sharpen The Saw (STS) repository provides live examples of this exact transformation
- This is the most persuasive image in the set — it answers "What will CORTEX actually DO for my team?"
- **Honest and accurate** — metrics shown are realistic achievable targets, not exaggerated
