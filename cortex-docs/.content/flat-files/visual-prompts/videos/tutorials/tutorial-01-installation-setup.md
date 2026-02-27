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
