# Prompt 10 — Sweep Completeness as Forensic Investigation

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, typography, and CORTEX logo watermark rules. All images must match the dark-blue glassmorphism theme of the CORTEX documentation site.

## Prompt

```
Create a noir-style forensic investigation scene showing the Sweep Completeness Contract (CORE-064) as a detective who refuses to close a case until every lead is followed. Rendered in the CORTEX dark glassmorphism aesthetic.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with dramatic spotlight in cyan (#00d4ff) from above
- All panels/boards: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Success: Green (#00ff88). Danger: Red (#ff4444)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~50px, subtle inner shadow

THE INVESTIGATION BOARD (center, large, glassmorphic frame):
- A glassmorphic board covered with connected evidence cards
- Each card = a discovered issue, rendered as small glassmorphic cards
- Cyan (#00d4ff) string connecting related issues
- Cards stamped "CLOSED ✅" in green (#00ff88) or "OPEN 🔴" in red (#ff4444)
- NO cards stamped "IGNORED" — this is the key visual point
- JetBrains Mono label: "SweepCatalogueOrchestrator — Every issue catalogued"

THE DETECTIVE (silhouette standing, examining board):
- Dark glassmorphic trench coat figure with "CORE-064" badge glowing cyan
- Holding a magnifying glass with cyan lens glow
- Muted caption (#a0a6c0): "The detective who never closes a case early"

LEFT PANEL — "Partial Sweep ❌" (glassmorphic, red #ff4444 border):
- Incomplete board with 3/7 issues fixed, 4 left hanging
- Big red X overlay
- Muted caption: "Like a surgeon who removes 3 of 7 tumors — unacceptable"

RIGHT PANEL — "Complete Sweep ✅" (glassmorphic, green #00ff88 border):
- Same board with ALL 7 issues resolved
- Green checkmark approval
- Muted caption: "Like a thorough home inspection — every room checked"

BOTTOM PANEL — The process (5 glassmorphic step cards in a row):
1. "DETECT" — Magnifying glass icon (cyan)
2. "CATALOGUE" — Filing cabinet icon (purple #7b61ff)
3. "FIX" — Wrench icon (amber #ffa500)
4. "RESCAN" — Radar sweep icon (blue #3b82f6)
5. "VERIFY EXHAUSTED" — Checkmark icon (green #00ff88)

Two escape hatches (small glassmorphic locked door icons):
- JetBrains Mono: "approve_wont_fix" — requires justification
- JetBrains Mono: "assert_exhausted" — confirms catalogue complete

Glassmorphic footer:
"CORE-064 · No Partial Sweeps · Every FIX/REFACTOR/AUDIT exhausts its full catalogue"
Muted subtitle: "Like cleaning your house — you can't just vacuum the living room and call it done"

Style: Film noir detective aesthetic with dark glassmorphism tech overlay. Dramatic cyan spotlight. Frosted glass panels. High contrast.

Dimensions: 800×600
Format: PNG
```

## Notes for Generation
- CORE-064 is enforced by `SweepCatalogueOrchestrator` at `cortex/orchestrators/support/sweep_catalogue_orchestrator.py`
- Sweep tracking uses SQLite — every issue gets a row
- The only way to close a sweep without fixing everything is `approve_wont_fix` (explicit) or `assert_exhausted` (verified)
- This rule prevents the "fix 3 bugs, leave 7" antipattern
