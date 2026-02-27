# Prompt 07 — Five-Layer Shift-Left Security Architecture

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, text contrast rules, typography, and CORTEX logo watermark rules.

## Prompt

```
Create a dramatic cross-section illustration of five concentric security layers, reimagined as a fortress defense-in-depth system. The scene shows a code commit at the center trying to reach production (the outer world).

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with subtle danger-zone radial gradient at edges
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Danger: Red (#ff4444). Success: Green (#00ff88)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- TEXT CONTRAST: Layer labels in #ffffff bold Space Grotesk on dark pill backgrounds. Detection examples in red #ff4444 JetBrains Mono. Pass indicators in green #00ff88
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px

FIVE CONCENTRIC LAYERS (innermost to outermost):

LAYER 1 — PRE-COMMIT GATE (innermost ring, red #ff4444 glow):
- Glassmorphic ring labeled "Pre-Commit Gate"
- Icons: Secret scanner, PII detector, branch hygiene checker
- Example detection (JetBrains Mono): "Hardcoded API_KEY detected in config.py → BLOCKED"
- Caption: "First barrier — like a metal detector at the entrance"

LAYER 2 — GOVERNANCE RULES (cyan #00d4ff glow):
- Glassmorphic ring with shield icons
- Icons representing: error handling rules, SQLite security mandates, type safety enforcement
- Caption: "Codified security standards — enforced automatically, not by memory"

LAYER 3 — LENS SECURITY ANALYSIS (purple #7b61ff glow):
- Glassmorphic ring with scanning beam icons
- Detection examples: "SQL injection pattern", "XSS vulnerability", "Exposed credential in environment variable"
- Caption: "Deep code analysis — pattern matching against known vulnerability signatures"

LAYER 4 — VULNERABILITY ORCHESTRATION (amber #ffa500 glow):
- Glassmorphic ring with SAST/CVE scanning icons
- Shows: dependency CVE scanning, OWASP Top 10 checks, remediation suggestions
- Caption: "Automated security assessment — finds what manual review misses"

LAYER 5 — RELEASE SECURITY GATE (outermost ring, green #00ff88 border):
- Glassmorphic ring with certificate/seal icons
- Shows: security checklist completed, threat model reviewed, all layers passed
- Caption: "Final clearance — nothing ships without passing all five layers"

CENTER: A code file icon trying to move outward through all five layers. Each layer either lets it pass (green glow) or blocks it (red ripple effect).

RIGHT SIDE PANEL — "SDLC Security Integration" (glassmorphic):
Shows a vertical timeline:
- Requirements → "Threat surface identification"
- Design → "Security-by-design validation"
- Implementation → "Credential scan, SAST analysis"
- Code Review → "Dependency CVE scanning"
- Integration → "Security integration tests"
- Release → "Full security checklist"
Label: "Security at every phase — not bolted on at the end"

Glassmorphic footer:
"Shift-Left Security · Five Layers · Every Phase of the SDLC · Automated Detection"

Style: Fortress defense-in-depth cross-section with dark glassmorphism. Layered rings from red (inner) to green (outer). Professional security-focused illustration.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- Security is infrastructure in CORTEX — not a separate phase or afterthought
- Five security layers provide defense-in-depth from pre-commit to release
- Dedicated security orchestrators handle SAST scanning, CVE detection, and remediation
- Workflow templates provide security-specific pipelines (compliance audit, hardening, threat model)
- **This is a key gap being filled** — security coverage was missing from the original image set
