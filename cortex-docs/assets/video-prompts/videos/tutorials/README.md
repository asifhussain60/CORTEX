# CORTEX Tutorial Prompts -- README

> **Tool:** NotebookLM Video Editor
> **Category:** Hands-on walkthrough tutorials -- visually differentiated from concept videos
> **Updated:** 2026-03-01

---

## VISUAL DIFFERENTIATION -- TUTORIALS vs CONCEPT VIDEOS

Tutorials use **warm amber/gold glassmorphism** to distinguish them from the cyan/purple concept videos. This makes it instantly clear: **cyan/purple = concept, amber/gold = hands-on.**

### Tutorial-Specific Palette (extends base identity)

| Token | Value | Usage |
|---|---|---|
| `--tutorial-accent` | `#f5a623` | Primary amber -- buttons, highlights, step numbers |
| `--tutorial-glow` | `rgba(245, 166, 35, 0.3)` | Warm glow on active elements |
| `--tutorial-step-bg` | `rgba(245, 166, 35, 0.08)` | Subtle warm tint behind active step panels |
| `--tutorial-success` | `#7ed321` | Step completion -- green check |
| `--tutorial-code-border` | `#f5a623` | Code panel border accent |
| `--bg-dark` | `#0a0e27` | SAME background as concept videos |
| `--glass-panel` | `rgba(255, 255, 255, 0.06)` | SAME glassmorphism |

### Tutorial Visual Rules

1. Step numbers use amber circles (`#f5a623` background, dark text)
2. Progress bars fill with amber gradient
3. Active code panels have a warm amber left border (`3px solid #f5a623`)
4. Completed steps transition from amber to green (`#7ed321`)
5. Dark background and glass panels remain identical to concept videos
6. Typography remains the same (Space Grotesk, Inter, JetBrains Mono)

### Text Contrast -- SAME RULES as concept videos

- Dark pill backgrounds `rgba(10, 14, 39, 0.8)` behind ALL text overlaying complex backgrounds
- Never place muted grey text on particle/glow backgrounds
- All headings: `text-shadow: 0 0 20px rgba(245, 166, 35, 0.5)` (amber instead of cyan)

---

## TUTORIAL INVENTORY -- 7 Tutorials

| # | File | Title | Duration | Focus | Unique Opening |
|---|---|---|---|---|---|
| T01 | `tutorial-01-installation-setup.md` | Installation & First Run | ~6 min | Get CORTEX running from zero | Cold start -- dark screen, cursor blinks |
| T02 | `tutorial-02-essential-commands.md` | The Command Landscape | ~7 min | All commands mapped to workflow moments | Command grid -- 9 dim cards assembling |
| T03 | `tutorial-03-building-feature-e2e.md` | Building a Feature End-to-End | ~9 min | TDD, governance, audit -- complete cycle | ECG callback to SE-01 concept video |
| T04 | `tutorial-04-onboarding-customization.md` | Onboarding and Customisation | ~8 min | Bring an external repo into CORTEX | Repository import -- files flow as particles |
| T05 | `tutorial-05-getting-started-in-vscode.md` | Getting Started in VS Code | ~6 min | VS Code workspace navigation + MCP verification | VS Code awakening -- folders illuminate |
| T06 | `tutorial-06-first-chat-workflows.md` | Your First Chat Workflows | ~7 min | First /audit fix from Copilot Chat | First chat -- naive vs structured message contrast |
| T07 | `tutorial-07-reading-results-and-next-steps.md` | Reading Results Like an Expert | ~6 min | Interpreting /audit fix output | Four panels assemble -- result dashboard materialises |

**Total runtime:** ~49 minutes

**Narrator gender alternation (VBP-017):** T01 female, T02 male, T03 female, T04 male, T05 female, T06 male, T07 female.

---

## ZERO-OVERLAP POLICY -- Tutorials

Each tutorial owns specific content. No tutorial re-explains content already covered in another.

| Topic | Tutorial | Exclusively Owns |
|---|---|---|
| Installation, prerequisites, setup-mcp.py | T01 | Cold start setup sequence |
| Command catalogue, when-to-use logic | T02 | Command grid + decision timing |
| E2E TDD + audit fix workflow | T03 | ECG feature build, convergence loop shown |
| External repo onboarding, team rules | T04 | Repository import + YAML extension points |
| VS Code navigation, MCP verification commands | T05 | Folder orientation + 3 verification commands |
| Structured chat input, challenge gate, /audit fix from chat | T06 | Naive vs structured contrast, first run warning |
| Output interpretation, severity map, AC trace reading | T07 | P0/P1/P2/P3 framework, reading order |

### Tutorials vs Concept Videos -- Overlap Boundary

| Topic | Concept Video | Tutorial Approach |
|---|---|---|
| Orchestration architecture | Video 03 -- how it works | T02 -- how to invoke it |
| TDD discipline | SE-01 -- theory + ECG | T03 -- practice with real code |
| Governance enforcement model | Video 02 -- lane comparison | T06 -- first experience of a gate |
| LENS analysis internals | Video 03 -- request journey | T04 -- running /onboard |
| 9-stage audit pipeline | Video 02 / SE-01 | T06 -- running it for the first time |
| Output panel interpretation | Not covered in concept videos | T07 -- exclusively |

---

## UNIQUE OPENINGS -- ZERO DUPLICATION

Each tutorial has a visually distinct opening sequence. The generic "CORTEX logo fades in" (The Awakening) was removed from all tutorials. Each opening establishes the tutorial's specific learning focus:

| Tutorial | Opening | Visual Identity |
|---|---|---|
| T01 | Dark screen, cursor blinks, `python3 --version` types, logo expands from cursor | Nothing exists until prerequisites are verified |
| T02 | 9 dim command cards assemble from centre outward | Commands are peers, not a hierarchy |
| T03 | Amber ECG line appears -- deliberate callback to SE-01 | Practice what SE-01 explained |
| T04 | External repo box floats in, particle stream flows rightward | Transformation as files cross the boundary |
| T05 | VS Code opens, three folders illuminate sequentially | IDE activates around CORTEX |
| T06 | Copilot Chat empty, naive message types then fades, structured message replaces it | Message quality determines outcome quality |
| T07 | Empty 2x2 panel grid, each panel fills with data one by one | Interpretation is the skill, not execution |

---

## PROGRESSIVE LEARNING PATH

```
T01 (Setup) -> T02 (Commands) -> T03 (Full Feature Build) -> T04 (Customise)
                                                                     |
T07 (Read Results) <- T06 (First Chat) <- T05 (VS Code)  <----------+
```

Concept video prerequisite: viewers should have watched Videos 01-03 before T01.
T03 deliberately references SE-01 (ECG callback) -- viewers who watched the concept series will recognise it.

---

## NARRATION PHILOSOPHY -- MANDATORY FOR ALL TUTORIALS

The viewer can read the code and the steps. **The narrator must never read them.**

### The test for every narration line

"If I muted this video, would the viewer lose something important?"

If they would lose nothing -- because the screen already says it -- cut the line or replace it with context they cannot get from the screen alone.

### What tutorial narration adds

| On screen | WRONG -- reading it | RIGHT -- speaking to it |
|---|---|---|
| `make test-smoke` command | "Now we run make test-smoke." | "Smoke tests are your handshake before you commit. Fast, broad, and merciless about obvious breaks." |
| RED test failure | "The test fails because the code doesn't exist yet." | "That failure is the point. It's proof the test is real." |
| Governance violation card | "A governance violation was detected." | "This is what it feels like when your team's standards enforce themselves." |
| Zero violations | "Zero violations. The audit is complete." | "That's the finish line. Not 'fewer problems' -- zero critical ones. You're cleared to commit." |

---

## AUDIO CONTINUITY -- SERIES SOUND DESIGN

Tutorial audio is distinct from concept videos (warmer, slower, more musical). Series-wide continuity:

- **Amber pulse**: action in progress (all tutorials)
- **Green chime**: step complete (all tutorials -- same tone)
- **Series bell**: AC_COMPLETE or major milestone (first introduced T01, recurring T03, T06, final use T07)
- **Cold start silence**: T01 only (1.5 seconds silence -- signature moment)
- **ECG tick**: T03 only (callback to SE-01 concept video)

---

## WATERMARK

`CORTEX` in Space Grotesk, 10% opacity, bottom-right. Tutorials add a small amber label `TUTORIAL` next to the watermark. The amber label differentiates tutorial frames from concept video frames in any screenshot or thumbnail.
