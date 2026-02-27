# Prompt 13 — RCA Memory Shield

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create a highly detailed, cinematic technical illustration of a "Root Cause Memory Shield" — 
a powerful protective force field generated from accumulated institutional knowledge.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with subtle radial gradient at center
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, 10-20px backdrop blur
- Primary accent glow: Cyan (#00d4ff) with 0 0 20px rgba(0, 212, 255, 0.3) glow
- Secondary accent: Purple (#7b61ff) for failure history trails
- Warning accent: Amber (#ffa500) for prevention warnings
- Danger accent: Red (#ff4444) for blocked operations
- Success accent: Green (#00ff88) for resolved patterns
- CORTEX logo watermark: Embossed at 20-30% opacity in the bottom-right corner

CENTER PIECE — The Memory Shield:
- A large, luminous hexagonal force field shield (3D perspective, tilted slightly toward viewer)
- Shield surface: Glassmorphic with cyan glow emanating from within
- Shield interior: Dense network of interconnected nodes — each representing a stored RCA analysis
- Node colours: Green (#00ff88) for resolved, amber (#ffa500) for warned, red (#ff4444) for blocked patterns
- Thin connection lines between related nodes (same root cause class) in faint cyan

LEFT PANEL — "How Failures Become Knowledge":
- Glassmorphic tall panel with title "RCA Engine" in Space Grotesk
- Show a vertical pipeline of 4 methodology icons (each in JetBrains Mono labels):
  1. Five Whys — a series of 5 downward arrows, each labeled "WHY?"
  2. Fishbone — a fish skeleton shape with 4 bone branches
  3. Fault Tree — small AND/OR gate tree diagram
  4. Causal Chain — horizontal timeline with event dots
- Bottom of panel: cyan arrow pointing RIGHT toward the shield: "→ MEMORY STORED"

RIGHT PANEL — "Prevention Gate in Action":
- Glassmorphic tall panel with title "Prevention Gate" in Space Grotesk
- Show 3 rows representing the 3 gate levels, stacked vertically:
  Row 1 (Advisory): Single eye icon, text "1st recurrence — Info surfaced", green background tint
  Row 2 (Warning):  Warning triangle, text "2nd recurrence — Gate warns", amber background tint
  Row 3 (Blocking): Stop sign (octagonal), text "3+ P0 — Operation halted", red background tint
- Between rows 2 and 3: a bold red line labeled "P0 THRESHOLD"

TOP SECTION — "Incoming Operations":
- Show 5 small VS Code editor icons descending toward the shield from above
- 3 pass through the shield untouched (green glow as they pass)
- 1 slows down and shows an amber warning bubble: "⚠️ Similar past failure: RCA-2026-001"
- 1 is stopped at the shield surface — red force field ripple effect: "🛑 Blocked — Structured review required"

BOTTOM SECTION — "URS Feedback Loop":
- Small horizontal section below the shield
- Show a flowing circular arrow connecting:
  "Outcome" → "URS Signal" → "Confidence Update" → "Pattern Promoted/Quarantined" → back to shield
- Label the arrow circle: "Unified Reinforcement Signal"
- Left side: label "STRONG_PUNISHMENT (−1.0)" in red for P0 recurrences
- Right side: label "STRONG_REWARD (+1.0)" in green for correct prevention

FOOTER BAR (glassmorphic, full width):
"CORTEX RCA Memory Engine — Phase 87 · Root Cause Analysis · Prevention Gate · Recurrence Detection"
```

## Image Specification

| Property | Value |
|----------|-------|
| Dimensions | 1920×1080 |
| Orientation | Landscape |
| Style | Cinematic technical illustration, glassmorphism |
| Subject | Protective force shield + 4 analysis methodologies + 3-tier prevention gate |
| Audience | Business leaders, developers |
| Emotional tone | Powerful protection, institutional knowledge, prevention over cure |

## Key Elements Checklist

- [ ] Hexagonal force field shield as centerpiece
- [ ] Left panel: 4 RCA methodologies with icons
- [ ] Right panel: 3-tier prevention gate (Advisory / Warning / Blocking)
- [ ] Top: 5 incoming operations — 3 pass, 1 warned, 1 blocked
- [ ] Bottom: URS feedback loop circular diagram
- [ ] CORTEX logo watermark bottom-right (20-30% opacity)
- [ ] Full mandatory color palette applied
- [ ] JetBrains Mono for code labels, Space Grotesk for headings, Inter for body

## Cross-Reference

| Related Content | Location |
|----------------|----------|
| Full RCA architecture | `flat-files/21-rca-memory-engine.md` |
| RCA flow diagram | `flat-files/diagrams/diagram-24-rca-prevention-flow.md` |
| Phase 87 spec | `cortex-registry/_cortex-master/phases/planned/phase-87-rca-memory-engine.yaml` |
| URS architecture | `flat-files/01-intelligence-architecture.md` |
