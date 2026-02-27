# Video Prompt 07 — The Audit Fix Pipeline

> **Duration:** 10 minutes · **Audience:** Advanced Software Engineers, Platform Engineers
> **Depth:** 🔴 Advanced — full 9-stage pipeline, convergence loops, SQLite tracing
> **No overlap:** Image prompt-09 shows the audit as a static immune system; this video walks through all 9 stages of `/audit fix` executing in real-time with live violations being detected, fixed, and rescanned

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).

---

## PROMPT

Create a 10-minute animated explainer video titled **"The Audit Fix Pipeline"** using the visual identity above. Walk through CORTEX's most powerful single command — `/audit fix` — as it executes all 9 stages to bring a codebase to production readiness.

### Scene 1 — One Command to Rule Them All (0:00 – 1:00)

**Open on:** A glassmorphic terminal, cursor blinking. A single command types in:

```
/audit fix
```

The text pulses cyan. Then the terminal expands to reveal a **9-stage pipeline** — nine glassmorphic chambers arranged vertically, each numbered and labeled. They're all dimmed, waiting to activate.

**Pipeline overview card:**
```
Stage -1: Environment Readiness
Stage  0: Inflight Upgrade + Pre-Flight
Stage  1: Governance Pre-Flight
Stage  2: 19-Point Production Scan
Stage  3: Wiring Contract Validation
Stage  4: Orchestrator Health (22 endpoints)
Stage  5: Vacuum Cleanup
Stage  6: Prompt/Agent Meta-Audit
Stage  7-8: Auto-Fix Convergence Loop
Stage  9: Tests + AC_COMPLETE
```

Each stage name appears one by one, stacking downward.

**Analogy overlay** (`#a0a6c0`): *"A spacecraft pre-launch checklist — 9 systems checked, from fuel to navigation to life support. If ANY fails, the launch doesn't proceed until it's fixed."*

**Narration:** "One command. Nine stages. Zero manual steps. This is `/audit fix` — CORTEX's production readiness pipeline."

### Scene 2 — Stages -1 to 1: Pre-Flight (1:00 – 3:00)

The camera zooms into the first three chambers.

**Stage -1: Environment Readiness**
- The `UpgradeOrchestrator` materializes. It checks:
  - Python version: badge shows `3.11.5 ✅` (green)
  - `requirements.txt` packages: progress bar fills — 47/47 packages satisfied (green)
  - A package is missing → auto-install animation: `pip install pytest-xdist` runs, package installs, badge turns green.
- Chamber glows green. ✅ appears.

**Stage 0: Inflight Upgrade**
- `git fetch origin/main` runs — a glassmorphic git graph appears showing local vs remote.
- Remote is 3 commits ahead → auto-merge animation: cyan arrows pull commits in.
- `STAGE-0-GOVERNANCE-AUDIT-SPEC.md` loads — a checklist renders in a glass panel.
- Chamber glows green. ✅ appears.

**Stage 1: Governance Pre-Flight**
- The full spec runs — checking that all governance files exist, rule YAML is valid, no orphaned rules.
- Show: YAML files being validated — each gets a ✅.
- One YAML has a syntax error → amber warning → auto-fix (indentation corrected) → rescan → ✅.
- Chamber glows green. ✅ appears.

**Analogy overlay:** *"Pre-flight: Fuel check, instruments check, runway clear. You don't skip these just because you've flown before."*

### Scene 3 — Stages 2-3: The Deep Scan (3:00 – 5:00)

**Stage 2: 19-Point Production Scan**

A glassmorphic checklist materializes — 19 rows. Each row activates sequentially:

| # | Check | Result |
|---|-------|--------|
| 1 | Import hygiene | ✅ |
| 2 | Circular dependency detection | ✅ |
| 3 | Dead code detection | ⚠️ 2 unused functions |
| 4 | Type hint coverage | ✅ 98.7% |
| 5 | Docstring coverage | ✅ 96.2% |
| 6 | Test coverage | ✅ 94.1% |
| ... | ... | ... |
| 17 | YAML governance alignment | ✅ |
| 18 | Architecture contract integrity | ✅ |
| 19 | SQLite activity log health | ✅ |

Show 5-6 checks in detail, the rest in rapid succession. Each check runs its scan, badges appear.

**For Check #3 (dead code):** Show the 2 unused functions highlighted in a code panel with amber borders. These become items for the convergence loop in Stages 7-8.

**Stage 3: Wiring Contract Validation**

Three tiers of architecture integrity checks:

- **L1: Module boundaries** — Glassmorphic boxes represent major modules. Connection lines are validated — each turns green when verified. One invalid cross-boundary import is flagged (red line).

- **L2: Orchestrator contracts** — All 51 orchestrators checked against `IOrchestrator` protocol. Show 51 small tiles in a grid, each checking off rapidly. All green.

- **L3: Integration tests** — Critical integration paths verified. Green cascade.

**Analogy overlay:** *"A building inspector checking the structure — foundation (L1), walls and wiring (L2), fire exits and safety systems (L3)."*

### Scene 4 — Stages 4-6: Health & Cleanup (5:00 – 6:30)

**Stage 4: Orchestrator Health**

A dashboard grid shows 22 health endpoints — each is a small glassmorphic card:

```
MasterOrchestrator        ✅ healthy (12ms)
IntentRouter              ✅ healthy (8ms)
TDDOrchestrator           ✅ healthy (15ms)
EnforcementOrchestrator   ✅ healthy (11ms)
HealthOrchestrator        ✅ healthy (9ms)
VacuumOrchestrator        ✅ healthy (14ms)
...
```

All 22 check in rapid succession — green pulses ripple across the grid. Total: 22/22 healthy.

**Stage 5: Vacuum Cleanup**

The `VacuumOrchestrator` activates — it scans for:
- Orphaned `.md` files in root → 2 found → archived to `.cortex-runtime/archive/`
- Stale log files older than 30 days → 5 cleaned
- Root directory clutter → organized

Animation: Files float up from their locations, get sorted into a glassmorphic recycling system, and either archive (amber glow) or delete (fade out).

**Stage 6: Meta-Audit**

23 meta-audit checks on prompts and agents:
- `.github/prompts/` files validated for format compliance
- Agent configurations checked for completeness
- Show the 23 checks as a rapid checklist — 21 pass, 2 warnings (amber).

### Scene 5 — Stages 7-8: The Convergence Loop (6:30 – 8:30)

**This is the most important stage. Show it in detail.**

**The detect-fix-rescan loop** is CORTEX's signature capability. A glassmorphic flow diagram appears:

```
       ┌─────────────┐
       │   DETECT     │ ← Find P0/P1 violations
       └──────┬──────┘
              │
       ┌──────▼──────┐
       │    FIX       │ ← Auto-remediate
       └──────┬──────┘
              │
       ┌──────▼──────┐
       │   RESCAN     │ ← Verify fix + check for new issues
       └──────┬──────┘
              │
         P0/P1 == 0?
        ╱           ╲
      YES            NO ──→ Loop back to DETECT
       │
    ┌──▼──┐
    │ DONE │
    └─────┘
```

**Animated loop execution:**

**Iteration 1:**
- **DETECT:** Violations from Stages 2-6 are collected. Show a glassmorphic table:
  - P0: 1 violation (dead import in `tools/legacy.py`) — red row
  - P1: 2 violations (unused functions from Check #3, invalid cross-boundary import from Stage 3) — amber rows
  - P2: 3 violations — blue rows (not blocking)
- **FIX:** Each P0/P1 violation gets an auto-fix applied:
  - Dead import → removed (file edit animation)
  - Unused functions → removed with deprecation notice
  - Cross-boundary import → refactored to use proper API
- **RESCAN:** All affected files rescanned. P0 count: 0. P1 count: 1 (the refactored import introduced a new issue).

**Iteration 2:**
- **DETECT:** 1 remaining P1 — the refactored import needs a test update.
- **FIX:** Test updated.
- **RESCAN:** P0: 0. P1: 0. ✅

**Convergence achieved!** The loop diagram glows green. A glassmorphic stamp appears: "CONVERGED — 2 iterations."

**CORE-064 callout:** A governance badge highlights: "Sweep Completeness Contract — every issue in the catalogue was addressed. No partial sweeps."

**Analogy overlay:** *"A doctor treating an infection — give antibiotics (fix), run blood tests (rescan). If infection persists, adjust treatment and test again. Repeat until healthy."*

**Narration:** "Stages 7-8 don't run once — they loop until every P0 and P1 is resolved. Not one pass. Convergence."

### Scene 6 — Stage 9: Tests + Completion (8:30 – 9:30)

**Stage 9 activates.** The final gate.

1. **Test suite runs:** `make test-preflight` → glassmorphic progress bar fills. Show test output:
   ```
   486 golden tests passed ✅
   177 phase tests passed ✅
   16,942 total tests — all green
   ```

2. **SQLite cleanup:** Activity log is pruned — records older than 30 days removed. `VACUUM` command runs on the database. A glassmorphic database icon compresses slightly.

3. **AC_COMPLETE marker:**
   ```
   AC_START: AC-AUDIT-20260227T170000
   Stages: 9 complete
   Iterations: 2 convergence cycles
   Violations resolved: 3 P0/P1, 3 P2
   Duration: 4m 23s
   AC_COMPLETE: AC-AUDIT-20260227T170000 ✅ (263,000ms)
   ```

4. **SQLite write:** The audit session record flows into the database. Show the schema tables: `audit_sessions`, `audit_stage_log`, `audit_violations`, `workflow_cycles`.

### Scene 7 — The Result (9:30 – 10:00)

**Camera pulls back.** All 9 stage chambers glow green. The pipeline is complete.

**Final summary card** (large, centered, glassmorphic):

```
/audit fix — COMPLETE

Stages Executed:     9/9
Environment:         ✅ verified
Governance:          ✅ 38 rules passing
Production Scan:     ✅ 19/19 checks
Architecture:        ✅ L1-L3 validated
Health:              ✅ 22/22 orchestrators
Vacuum:              ✅ 7 files cleaned
Meta-Audit:          ✅ 23 checks (21 pass, 2 advisory)
Convergence:         ✅ 2 iterations, 0 P0/P1
Tests:               ✅ 16,942 passing

Status: PRODUCTION READY
```

The card has a green border glow. A satisfying chime plays.

**Closing text** (Space Grotesk): **"One command. Nine stages. Production ready."**

Logo pulse. End card.

---

## Notes

- Image prompt-09 shows the audit as a static immune system with cellular defenders. This video shows the **full 9-stage `/audit fix` pipeline executing** with real violations being caught, fixed, and rescanned in a convergence loop — completely different content.
- The convergence loop (Stages 7-8) is the unique visual centerpiece — no other video or image covers this loop mechanism.
- Real stage numbers, check counts, and rule IDs match the actual CORTEX architecture.
- The SQLite schema tables are real — `audit_sessions`, `audit_stage_log`, `audit_violations`, `workflow_cycles`, `workflow_runs`.
- Sound design: each stage completion = ascending tone (9 tones form a rising scale); convergence loop iteration = heartbeat pulse; final completion = orchestral resolve chord.
- This is the longest video (10 min) because `/audit fix` is CORTEX's most comprehensive command.
