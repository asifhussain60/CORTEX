# Tutorial 01 — Installation & First Run

> **Duration:** ~6 minutes · **Audience:** First-time users
> **Visual Theme:** 🟠 Warm amber/gold glassmorphism (tutorial accent)
> **Prerequisite:** None — this is the starting point
> **Goal:** Viewer has CORTEX installed and has run their first command

---

## ⚠️ VISUAL IDENTITY — TUTORIAL THEME

> See tutorials `README.md` for the amber/gold tutorial palette, step numbering, code panel styling, and text contrast rules. Dark background and glass panels are shared with concept videos; accent color shifts to amber.

## ⚠️ NARRATION RULE — MANDATORY

> **The narrator never reads the steps or the code.** Every narration line must add something the viewer cannot get from reading the screen: the *why it matters*, the *gotcha to watch for*, the *non-obvious implication*, or the *discipline behind the mechanic*. See tutorials `README.md` §Narration Philosophy for full guidance and examples.

---

## CINEMATIC SIMULATION NOTES — T01: Installation & First Run

### Visual Physics & Ambience Protocol (Tutorial Amber Theme)
- **Environment:** Dark-blue vacuum (#0a0e27) — SAME as concept videos — with ray-traced reflections on glass floor
- **Accent neon:** Warm amber (#f5a623) neon filaments replace cyan for step borders, highlights, and progress bars
- **Code panels:** Frosted glassmorphism with 3px amber left border, JetBrains Mono at readable size, ray-traced surface reflections
- **Step transitions:** Amber progress bar fills with particle condensation between steps; completed steps emit green (#7ed321) checkmark with bioluminescent flash
- **Lighting:** Volumetric amber fog at ground level, ray-traced caustics from amber neon sources
- **Feedback cues:** Green flash + chime = step complete, amber pulse = in progress, holographic glitch = error state
- **Temporal evolution:** Each completed step brightens the environment — Scene 1 is dim, Scene 6 is fully lit with warm amber luminosity

**SCENE 1 — "The Awakening" (0:00–0:04)**
Camera: Static center-frame, locked on ray-traced glassmorphism floor.
Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric amber fog drifting at ground level.
CORTEX logo (cortex-logo.png) fades in as large central hero image with electric-aura glow —
amber (#f5a623) pulse radiates outward instead of cyan (tutorial identity). Ray-traced
reflections shimmer on the floor in warm tones. Hold 3s.
Logo shrinks to bottom-right watermark (15% opacity) with ease-out parallax slide.
Small amber label "TUTORIAL" materializes next to the watermark with particle condensation.

**SCENE 2 — "Prerequisites Checklist" (0:04–1:00)**
Camera: Slow dolly-in toward a glassmorphic checklist panel assembling with time-lapse
mechanical construction — glass panes slide in from edges and seal together. Four checklist
rows with amber step-number circles (#f5a623 background, dark text). Each row materializes
with particle condensation: Python 3.9+, VS Code, Git, GitHub Copilot.
Code panel appears beside each item with amber left border — `python3 --version` output
types character by character with bioluminescent cursor trail.
As each prerequisite verifies, the amber circle transforms to green (#7ed321) checkmark
with a bioluminescent flash and ray-traced caustics rippling across the glass surface.

**SCENE 3 — "Clone & Configure" (1:00–3:15)**
Camera: FPV tracking shot following amber particle stream from checklist to a new
glassmorphic terminal panel. Terminal materializes with time-lapse mechanical assembly —
frame first, then frosted glass fills in.
`git clone` command types with amber cursor trail. Output scrolls with volumetric light
bloom on each line. Progress bar fills amber with particle condensation animation.
`pip install` output scrolls — packages appear as small glassmorphic cards that stack
and settle with parallax physics, each glowing amber briefly on arrival.
MCP setup: `setup-mcp.py` runs — three glassmorphic info cards materialize with particle
condensation (OS detection, settings.json config, stdio transport). Each card has amber
neon filaments. Lidar sweep across all three confirms configuration with green flash.
Camera: Macro zoom on `.vscode/settings.json` — the MCP configuration block highlights
with amber glow, internal JSON structure visible through frosted glass.

**SCENE 4 — "First Command: /audit fix" (3:15–5:30)**
Camera: Slow dolly-out revealing a VS Code workspace panel (glassmorphic representation).
Copilot Chat opens — `/audit fix` types with amber cursor. The 9-stage pipeline materializes
as a vertical track of glassmorphic nodes with amber neon connections (callbacks to Video 05
diagram, but in tutorial amber instead of concept cyan).
Temporal evolution in action: Each stage node illuminates sequentially — amber pulse on
active stage, green (#7ed321) flash on completion, stages dim to 60% opacity once passed.
Ray-traced caustics from each active stage ripple across the glass floor.
If violations appear: holographic glitch on violation cards (red neon flicker), then
convergence loop animation — red sparks physically filter out with each iteration,
replaced by steady amber hum. Transformation timeline: violation count descends
holographically (3 → 1 → 0) with each loop.
AC_COMPLETE materializes as a holographic badge with amber shimmer and timestamp.

**SCENE 5 — "Output Comprehension" (4:30–5:30)**
Camera: Macro zoom hero moment on the output panel. Five sections highlight sequentially
with slow dolly-in on each: stage progress, violations table, convergence log, test results,
audit trail. Each section gains amber neon border emphasis when active, dims when camera
moves on. Ray-traced reflections of the active section shimmer on adjacent glass panels.

**SCENE 6 — "Smoke Test Victory" (5:30–6:00)**
Camera: Pull-back to full workspace view. `make test-smoke` types. Green output cascades
with bioluminescent particle celebration — green sparks rise and fade. Duration badge
materializes as holographic floating card: "< 60 seconds."
Closing glassmorphic completion card assembles with time-lapse mechanical construction:
four checkmark rows (installed, MCP configured, first audit complete, tests passing)
each illuminate green with bioluminescent flash.
Amber arrow pointing right materializes with particle trail: "Tutorial 2 →"
Final fade to black with ray-traced reflections dimming.

---

## PROMPT

Create a ~6-minute tutorial video titled **"Installation & First Run"** using the amber/gold tutorial theme.

### Step 1 — Prerequisites Check (0:00 – 1:00)

**Glassmorphic checklist with amber step numbers:**

- [ ] Python 3.9+ installed → show `python3 --version` in a code panel with amber border
- [ ] VS Code installed → show VS Code icon
- [ ] Git installed → show `git --version`
- [ ] GitHub Copilot extension (optional, recommended) → show extension marketplace

Each item checks off with a green checkmark as verified. If something's missing, show a brief "how to install" tooltip.

**Narration:** "If any of these fail, don't skip them. The first command you run in CORTEX relies on all three. Start clean."

### Step 2 — Clone and Setup (1:00 – 2:15)

**Code panel (amber left border, JetBrains Mono):**

```bash
git clone <repository-url>
cd CORTEX
```

**Virtual environment setup:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows (shown as secondary option)
```

**Dependencies:**
```bash
pip install -r requirements.txt
```

Show the output scrolling — packages installing. Progress bar fills amber.

**Narration:** "This is the only step that looks like standard Python setup — because it is. After this, CORTEX takes over."

### Step 3 — MCP Configuration (2:15 – 3:15)

**Show the automated setup:**
```bash
python3 scripts/setup-mcp.py
```

**Explain what happens** (glassmorphic info cards):
1. Detects your OS (macOS, Linux, or Windows)
2. Configures `.vscode/settings.json` with MCP server settings
3. Sets up stdio transport — CORTEX auto-starts like Pylance

**Verification:** Open VS Code. Open Copilot Chat. Type a CORTEX command — if MCP is running, you'll see CORTEX tools available.

**Dark pill:** *"CORTEX uses Pylance-style MCP — it starts automatically when VS Code opens. No manual server startup needed."*

**Narration:** "The Pylance comparison is worth understanding: once configured, it's invisible infrastructure. You don't start it. It's just there — the same way language intelligence is just there."

### Step 4 — Your First Command (3:15 – 4:30)

**The moment of truth.** Copilot Chat panel open. Type:

```
/audit fix
```

**Show what happens:**
- Stage indicators appear (the 9-stage pipeline from Video 5, but now you're seeing it live)
- Environment validates
- Governance rules load
- Production scan runs
- Violations appear (if any) with severity badges
- Convergence loop iterates
- Tests run
- **AC_COMPLETE ✅**

**Narration:** "If violations appear here, that's not a bad first run — it's CORTEX doing its job. A violation on day one is infinitely cheaper than the same violation in production."

### Step 5 — Understanding the Output (4:30 – 5:30)

**Pause on the output.** Explain the key sections:

1. **Stage progress** — numbered stages with status (✅/⚠️/❌)
2. **Violations table** — severity, file, description, remediation
3. **Convergence log** — how many iterations the fix loop ran
4. **Test results** — pass/fail counts
5. **Audit trail** — AC markers with timestamps

**Highlight:** The violations table is actionable — each row tells you exactly what to fix and how.

**Narration:** "The stage breakdown isn't decoration. When something fails, you'll know which stage it failed at — and that narrows the investigation immediately."

### Step 6 — Quick Smoke Test (5:30 – 6:00)

**Run the smoke tests to verify everything is wired:**

```bash
make test-smoke
```

or (Windows):
```bash
python scripts/run_tests.py smoke
```

Green output. Tests pass. Duration badge: < 60 seconds.

**Narration:** "Under 60 seconds for broad coverage. That's the smoke test contract — fast enough to run before every commit, thorough enough to catch the obvious failures."

**Closing card:**
- ✅ CORTEX installed
- ✅ MCP configured
- ✅ First audit fix complete
- ✅ Tests passing

**Next:** "Tutorial 2 — Essential Commands" (amber arrow pointing right)

---

## Notes
- This tutorial is deliberately simple — no architecture explanation, no theory
- Every command is shown in full, not abbreviated
- Windows alternatives are shown as secondary options (not primary)
- The `/audit fix` output should be realistic, not cherry-picked to look perfect
