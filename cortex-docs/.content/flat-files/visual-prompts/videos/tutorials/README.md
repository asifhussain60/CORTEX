# CORTEX Tutorial Prompts — README

> **Tool:** NotebookLM Video Editor
> **Category:** Hands-on walkthrough tutorials — visually differentiated from concept videos
> **Updated:** 2026-02-27

---

## VISUAL DIFFERENTIATION — TUTORIALS vs CONCEPT VIDEOS

Tutorials use a **warm amber/gold glassmorphism** accent theme to distinguish them from the cyan/purple concept videos. This makes it instantly clear: **cyan/purple = concept, amber/gold = hands-on.**

### Tutorial-Specific Palette (extends the base identity)

| Token | Value | Usage |
|---|---|---|
| `--tutorial-accent` | `#f5a623` | Primary amber — buttons, highlights, step numbers |
| `--tutorial-glow` | `rgba(245, 166, 35, 0.3)` | Warm glow on active elements |
| `--tutorial-step-bg` | `rgba(245, 166, 35, 0.08)` | Subtle warm tint behind active step panels |
| `--tutorial-success` | `#7ed321` | Step completion — green check |
| `--tutorial-code-border` | `#f5a623` | Code panel border accent |
| `--bg-dark` | `#0a0e27` | SAME background as concept videos — consistency |
| `--glass-panel` | `rgba(255, 255, 255, 0.06)` | SAME glassmorphism — consistency |

### Tutorial Visual Rules

1. **Step numbers** use amber circles (`#f5a623` background, dark text) instead of cyan
2. **Progress bars** fill with amber gradient instead of cyan→purple
3. **Active code panels** have a warm amber left border (`3px solid #f5a623`)
4. **Completed steps** transition from amber → green (`#7ed321`)
5. **The dark background and glass panels remain identical** to concept videos for brand cohesion
6. **Typography remains the same** (Space Grotesk, Inter, JetBrains Mono)

### Text Contrast — SAME RULES as concept videos

- Dark pill backgrounds `rgba(10, 14, 39, 0.8)` behind ALL text overlaying complex backgrounds
- Never place muted gray text on particle/glow backgrounds
- All headings: `text-shadow: 0 0 20px rgba(245, 166, 35, 0.5)` (amber instead of cyan)

---

## TUTORIAL INVENTORY — 4 Tutorials

| # | File | Title | Duration | Focus |
|---|---|---|---|---|
| T1 | `tutorial-01-installation-setup.md` | Installation & First Run | ~6 min | Get CORTEX running from zero |
| T2 | `tutorial-02-essential-commands.md` | Essential Commands | ~7 min | Daily workflow commands |
| T3 | `tutorial-03-building-feature-e2e.md` | Building a Feature End-to-End | ~9 min | TDD, governance, audit — complete cycle |
| T4 | `tutorial-04-onboarding-customization.md` | Onboarding & Customization | ~8 min | Bring your own repo, extend CORTEX |

**Total runtime:** ~30 minutes

---

## PROGRESSIVE LEARNING PATH

Tutorials assume the viewer has watched the concept videos (or at least Videos 1–3). They build on each other:

```
T1 (Setup) → T2 (Commands) → T3 (Full Feature) → T4 (Customize)
   ↓              ↓                ↓                    ↓
 "Running"    "Navigating"    "Building"          "Owning"
```

---

## ZERO-OVERLAP POLICY — Tutorials vs Concept Videos

| Topic | Concept Videos Cover | Tutorials Cover |
|---|---|---|
| Orchestration | How orchestrators work (architecture) | How to invoke orchestrators (commands) |
| TDD | The discipline and ECG metaphor | A live TDD session with real code |
| Governance | Shield wall tiers and enforcement model | What happens when you violate a rule — and how to fix it |
| LENS | The scanning engine internals | Running a scan and reading results |
| Audit | The 9-stage pipeline animation | Running `/audit fix` and interpreting output |
| Onboarding | Multi-repo scenario overview | Step-by-step onboarding of YOUR repository |

---

## TUTORIAL MOTION STYLE

- **Pacing:** Slower than concept videos. Pause on each step. Allow viewer to follow along.
- **Code panels:** Larger. JetBrains Mono at readable size. Amber left border.
- **Step transitions:** Amber progress bar fills between steps. Completed steps get a green checkmark.
- **Voiceover tone:** Warm, instructional, patient. "Let's do this together" energy.
- **NO montage sequences** — every step is shown in real-time.

---

## 🎙️ NARRATION PHILOSOPHY — MANDATORY FOR ALL TUTORIALS

**The viewer can read the code and the steps. The narrator must never read them.**

Tutorials are hands-on — the viewer is following along, reading each command and output themselves. Narration that reads the screen breaks concentration and feels condescending.

### The test for every narration line

> *"If I muted this video, would the viewer lose something important?"*

If they'd lose nothing — because the screen already says it — cut the line or replace it with context they can't get from the screen alone.

### What tutorial narration adds

| On screen | ❌ Reading it (WRONG) | ✅ Speaking to it (RIGHT) |
|---|---|---|
| `make test-smoke` command shown | *"Now we run make test-smoke."* | *"Smoke tests are your handshake before you commit. Fast, broad, and merciless about obvious breaks."* |
| RED test failure displayed | *"The test fails because the code doesn't exist yet."* | *"That failure is the point. It's proof the test is real and that you'll know when it passes for the right reason."* |
| Green test output shown | *"All tests are now passing."* | *"Now the implementation earns its place — it didn't exist until something proved it was needed."* |
| Governance violation card appears | *"A governance violation was detected."* | *"This is what it feels like when your team's standards enforce themselves. No review comment. No Slack message. Just a rule doing its job."* |
| Convergence loop reaches 0 violations | *"Zero violations. The audit is complete."* | *"That's the finish line. Not 'fewer problems' — zero critical ones. You're cleared to commit."* |

### Tutorial narration principles

1. **Name what the viewer is feeling, not what they're seeing.** When the first audit runs and violations appear, acknowledge the potential surprise — don't just describe the output.
2. **Explain the discipline, not the mechanics.** When running TDD, the narration reinforces *why* the discipline exists, not what each command does (the screen shows that).
3. **Add the shortcut or the gotcha.** Tutorial viewers want to learn faster than a manual. The narrator's job is to surface the non-obvious: what to watch for, what commonly goes wrong, what the output is telling them.
4. **Celebrate milestones honestly.** When something works, the narration marks the achievement without overselling it. "You're not done — but that's a real milestone."
5. **Trust the step labels.** If step numbers and progress bars are on screen, the narrator does not count steps out loud.



Same as concept videos: `CORTEX` in Space Grotesk, 10% opacity, bottom-right. Tutorials add a small amber label: `TUTORIAL` next to the watermark.
