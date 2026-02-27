# Prompt 05 — TDD Cycle as a Heartbeat

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create a medical-style illustration showing the TDD (Test-Driven Development) cycle visualized as a heartbeat on an ECG/EKG monitor.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27)
- All panels/frames: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~50px, subtle inner shadow

A glowing ECG line runs left to right across the center on a glassmorphic monitor frame.

THE HEARTBEAT PATTERN repeats three times, each beat = one TDD cycle:

BEAT 1 — RED PHASE (downward spike, colored #ff4444):
- ECG line drops sharply
- JetBrains Mono label: "RED — Write failing test"
- Tiny icon: broken test tube
- Muted caption (#a0a6c0): "Like a doctor ordering a blood test before prescribing medicine"

BEAT 2 — GREEN PHASE (sharp upward spike, colored #00ff88):
- ECG line shoots to peak
- JetBrains Mono label: "GREEN — Write minimum code to pass"
- Tiny icon: glowing green checkmark
- Muted caption: "Like taking exactly the right antibiotic — not more, not less"

BEAT 3 — REFACTOR PHASE (smooth recovery curve, colored #3b82f6):
- ECG line smoothly returns to baseline
- JetBrains Mono label: "REFACTOR — Improve while tests stay green"
- Tiny icon: polishing cloth
- Muted caption: "Like organizing your closet after buying new clothes — everything still fits"

ABOVE THE ECG LINE (glassmorphic panel):
- Space Grotesk heading: "CORE-008: TDD Mandatory — No Exceptions"
- Subtitle in Inter: "Every IMPLEMENT and FIX request goes through this cycle"

BELOW THE ECG LINE (glassmorphic panel):
- JetBrains Mono label: "TDDOrchestrator · Governance-Enforced TDD"
- Three small glassmorphic stat boxes with cyan borders:
  - "Tests Written First: 100%"
  - "Governance Gate: Active"
  - "Rollback: Automatic"

Style: Medical illustration crossed with dark glassmorphism tech. Frosted glass panels, cyan glow accents.

Dimensions: 800×600
Format: PNG
```

## Notes for Generation
- TDD is enforced by CORE-008 — the most important governance rule
- The cycle is mandatory for all IMPLEMENT and FIX intents — no bypass possible
- A suite of golden regression tests must always pass to confirm system health
- The heartbeat metaphor is central — a system without tests is a system without a pulse
