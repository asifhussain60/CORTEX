# Prompt 06 — Golden Test Pyramid — Scoring, Promotion, and End-to-End Verification

## Target Tool: Google Gemini Image Editor / NotebookLM

## Visual Identity

> ⚠️ **Before generating:** Read `README.md` in this folder for the MANDATORY color palette, glassmorphism style, text contrast rules, typography, and CORTEX logo watermark rules.

## Prompt

```
Create a detailed technical illustration of a test quality pyramid, reimagined as a gem-cutting and promotion system for CORTEX's golden test architecture.

VISUAL IDENTITY — MANDATORY:
- Background: Deep space navy (#0a0e27) with subtle upward gradient
- All info panels: Glassmorphic — rgba(26, 31, 58, 0.7) fill, 1px rgba(255,255,255,0.1) border, 12-16px corner radius, backdrop blur
- Primary glow: Cyan (#00d4ff). Secondary: Purple (#7b61ff). Success: Green (#00ff88). Warning: Amber (#ffa500). Danger: Red (#ff4444)
- Shadows: 0 8px 32px rgba(0, 0, 0, 0.37)
- TEXT CONTRAST: All labels in #ffffff bold on dark pill backgrounds. Score numbers in cyan #00d4ff JetBrains Mono. Dimension names in #ffffff Space Grotesk
- Heading font: Space Grotesk. Labels: JetBrains Mono. Body: Inter
- CORTEX logo watermark: Embossed at 20-30% opacity in bottom-right corner, ~80px, subtle inner shadow

THE PYRAMID (center, large, three tiers):

TOP TIER — "GOLDEN" (bright amber/gold #ffa500 glow, glass surface):
- Polished gem-like tests at the summit, each glowing with gold/amber aura
- Tests labeled: "Orchestrator Chain E2E", "Governance Gate Verification", "LENS Pipeline Integration"
- Glassmorphic caption: "Golden tests — must ALWAYS pass. Any failure is a production blocker."
- An audit trail line descends from each golden test to a small SQLite DB icon at the base, with cyan connection lines labeled "AC_START → AC_COMPLETE ✅"

MIDDLE TIER — "REVIEW" (amber #ffa500 tint, semi-transparent):
- Tests undergoing evaluation, some with upward arrows (promotion candidates)
- Glassmorphic caption: "Under review — improving toward golden promotion"

BOTTOM TIER — "REGULAR" (muted cyan, large base):
- Many small test icons forming the broad base
- Some with downward arrows and red X (deletion candidates)
- Glassmorphic caption: "Regular tests — the foundation. Low-scoring tests are pruned."

THE SCORING ENGINE (right side, large glassmorphic panel):
Title in Space Grotesk: "Quality Gate — Five Scoring Dimensions"

Five horizontal bars stacked vertically, each representing a scoring dimension:
1. "Impact" (cyan bar, 0–5 range) — "Does this test guard a critical business invariant?"
2. "Likelihood" (purple bar, 0–3 range) — "How likely is this scenario to occur?"
3. "Detection" (green bar, 0–3 range) — "Would we catch this failure otherwise?"
4. "Efficiency" (blue bar, 0–2 range) — "Is the test lean and focused?"
5. "Maintenance Penalty" (red bar, 0 to -2 range) — "Heavy mocking lowers the score"

Below the bars: "Score = Impact + Likelihood + Detection + Efficiency − Maintenance"
Three verdict badges:
- ≥ 7: "KEEP — Golden candidate" (green badge)
- 4–6: "REVIEW — Needs improvement" (amber badge)
- < 4: "DELETE — Insufficient value" (red badge)

THE END-TO-END VERIFICATION TRAIL (left side, vertical flow):
Title: "Golden Test → Audit Trace"

Show a vertical flow of 4 glassmorphic cards connected by a cyan line:
1. "Test Created (RED Phase)" — red border, test_tube icon
2. "Scored by Quality Gate" — purple border, gauge showing score ≥ 7
3. "Promoted to Golden Tier" — gold border, star icon, file moved to tests/golden/
4. "AC_COMPLETE ✅ Audit Logged" — green border, shows audit trace entry with timestamp

Below: "Every golden test failure triggers a P0 investigation — the chain is unbreakable"

THE DEMOTION PATH (bottom-left, small):
- A faded arrow pointing downward: "Score drops below 7 → Demoted to regular"
- Caption: "Golden tests are earned, not permanent — quality must be maintained"

Glassmorphic footer bar:
"Golden Tests · Quality Scoring · Promotion & Demotion · End-to-End Audit Trace"

Style: Pyramid hierarchy with gem/crystal aesthetic overlaid on dark glassmorphism. Gold/amber highlights on golden tests. Professional and educational.

Dimensions: 1920×1080
Format: PNG
```

## Notes for Generation
- Golden tests are CORTEX's immune system — they must always pass across every commit
- The quality gate uses a 5-dimension scoring formula (0-9 scale) to objectively evaluate test value
- Tests scoring ≥ 7 are promoted to golden tier; below 7 can be demoted
- Every golden test creates a complete audit trail from creation through execution
- The end-to-end chain (test → score → promote → audit) is a KEY differentiator — show it prominently
- **No hardcoded count** — the growing golden tier is implied through visual pyramid height
