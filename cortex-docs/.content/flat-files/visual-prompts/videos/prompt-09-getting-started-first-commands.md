```markdown
# Video Prompt 09 — Getting Started: Your First Commands

> **Duration:** 7 minutes · **Audience:** Software Engineers, Product Owners new to CORTEX
> **Depth:** 🟡 Tutorial — practical with explanations
> **Prerequisites:** Video 08 (CORTEX installed and verified)
> **Goal:** User confidently uses 5 essential commands and understands when to use each

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).

---

## PROMPT

Create a 7-minute animated tutorial video titled **"Getting Started: Your First Commands"** using the visual identity above. Introduce 5 essential CORTEX commands through practical scenarios.

### Scene 1 — The Command Palette (0:00 – 0:45)

**Open on:** VS Code with Copilot Chat open. A glassmorphic "command menu" appears.

**The 5 commands we'll learn:**

| Command | Purpose | Icon |
|---------|---------|------|
| `/ask` | Learn about CORTEX concepts | 🎓 |
| `/challenge` | Get alternative approaches | ⚔️ |
| `/audit` | Check code health | 🔎 |
| `/health` | Check orchestrator status | 🩺 |
| `/vacuum` | Clean up workspace | 🧹 |

Each command tile appears with its icon and one-line description. The tiles are glassmorphic cards in a 5-column layout.

**Narration:** "CORTEX has many commands, but these five will handle 80% of your daily work. Let's see each one in action."

### Scene 2 — Command 1: `/ask` — The Learning Tool (0:45 – 2:00)

**Scenario:** You're new to the codebase and want to understand how governance works.

**Copilot Chat input:**
```
/ask How does CORTEX enforce governance rules?
```

**The `cortex_ask` MCP tool activates.** Show:
- Tool selection indicator (glass tile glows)
- Processing animation (thinking dots)
- Response builds in chat:

```
🎓 CORTEX Governance Enforcement

**Short Answer:**
EnforcementOrchestrator runs at pre-commit, CI, and runtime to validate code against 38 CORE rules.

**How It Works:**
1. Rules are defined in YAML files (`cortex-registry/core/tier0-skull/`)
2. Pre-commit hook intercepts `git commit`
3. Each staged file is scanned against all 38 rules
4. Violations block the commit until fixed

**Key Rules:**
- CORE-008: TDD mandatory — write tests before implementation
- CORE-011: Type hints on all functions
- CORE-012: Docstrings on all public APIs

**Learn More:** See Video 4 (Governance in Action) for the full deep dive.
```

**Highlight:** The response includes truth verification — it references actual code paths (`cortex-registry/core/tier0-skull/`), not hallucinated information.

**Analogy overlay** (`#a0a6c0`): *"/ask is your study guide — ask any question about CORTEX, get a verified answer."*

### Scene 3 — Command 2: `/challenge` — The Decision Helper (2:00 – 3:15)

**Scenario:** You're about to implement a feature but want to make sure you're taking the best approach.

**Copilot Chat input:**
```
/challenge I want to add email validation to the registration form
```

**The `cortex_challenge` MCP tool activates.** Response builds:

```
⚔️ MANDATORY CHALLENGE

**Your Approach:**
Add email validation to registration form

**Alternative Approaches:**

| Approach | Pros | Cons | ROI |
|----------|------|------|-----|
| **A: Regex validation in-form** | Fast, no dependencies | Complex regex, hard to maintain | 🟡 Medium |
| **B: Email validation library (e.g., email-validator)** | Battle-tested, handles edge cases | External dependency | 🟢 High |
| **C: Backend validation + async check** | Real-time MX record check | Slower, network dependency | 🔴 Low |

**Recommendation:** Approach B — use a validated library. CORTEX's CORE-035 (no duplicates) discourages re-implementing standard validations.

**Decision:** Type "proceed with B" or describe your preferred approach.
```

**The table renders as a glassmorphic comparison panel** with colored ROI indicators.

**Analogy overlay:** *"/challenge is your architect review — before building, consider all options."*

### Scene 4 — Command 3: `/audit` — The Health Check (3:15 – 4:30)

**Scenario:** You've made some changes and want to verify the codebase is healthy before committing.

**Copilot Chat input:**
```
/audit
```

**The audit pipeline activates.** Show a condensed version of the 9-stage pipeline from Video 7:

**Progress display** (glassmorphic panel):
```
🔎 CORTEX Audit — Quick Scan

[████████░░] 80% Stage 6 of 9

Stage 1: Pre-Flight        ✅ passed
Stage 2: Production Scan   ✅ 19/19 checks
Stage 3: Wiring Contract   ✅ validated
Stage 4: Health            ✅ 22/22 orchestrators
Stage 5: Vacuum            ✅ clean
Stage 6: Meta-Audit        🔵 running...
```

**Final result:**
```
✅ AUDIT COMPLETE

P0 Violations: 0
P1 Violations: 0
P2 Advisories: 2

Advisories (non-blocking):
1. tests/old_test.py — consider moving to archive
2. Missing docstring in cortex/utils/helper.py:45

Status: HEALTHY — ready to commit
```

**Key point** (highlight box):
> "Notice `/audit` ran without `fix`. It reports but doesn't change anything. Add `fix` to auto-remediate: `/audit fix`"

**Analogy overlay:** *"/audit is your pre-flight checklist — catch issues before they become problems."*

### Scene 5 — Command 4: `/health` — The System Status (4:30 – 5:15)

**Scenario:** Something feels slow or a tool isn't responding. Check if all orchestrators are healthy.

**Copilot Chat input:**
```
/health
```

**The `HealthOrchestrator` activates.** A dashboard grid appears:

```
🩺 ORCHESTRATOR HEALTH CHECK

┌────────────────────────────────────────────┐
│ Orchestrator             Status    Latency │
├────────────────────────────────────────────┤
│ MasterOrchestrator       ✅ healthy   12ms │
│ IntentRouter             ✅ healthy    8ms │
│ TDDOrchestrator          ✅ healthy   15ms │
│ EnforcementOrchestrator  ✅ healthy   11ms │
│ LENSOrchestrator         ✅ healthy   23ms │
│ ... (17 more)            ✅ healthy    <20ms│
└────────────────────────────────────────────┘

Total: 22/22 healthy
Average latency: 14ms
MCP Server: running

Status: ALL SYSTEMS OPERATIONAL
```

All 22 rows appear in rapid succession with green pulses.

**Failure scenario** (brief, 10 seconds): Show what happens if one orchestrator is unhealthy — row turns amber, status shows "degraded", and a fallback activates automatically.

**Analogy overlay:** *"/health is your system monitor — see the pulse of every component."*

### Scene 6 — Command 5: `/vacuum` — The Cleanup Tool (5:15 – 6:15)

**Scenario:** Your workspace has accumulated stale files, logs, and markdown sprawl over time.

**Copilot Chat input:**
```
/vacuum
```

**The `VacuumOrchestrator` activates.** Show a cleanup animation:

**Phase 1: Scan**
```
🧹 VACUUM — Scanning workspace

Found:
- 3 orphaned .md files in root directory
- 2 stale log files (>30 days old)
- 1 empty __pycache__ directory
- 0 duplicate files
```

**Phase 2: Clean** (with confirmation)
```
Proceeding with cleanup...

Archived: NOTES.md → .cortex-runtime/archive/
Archived: TODO.md → .cortex-runtime/archive/
Archived: SCRATCH.md → .cortex-runtime/archive/
Deleted: logs/debug-20260115.log
Deleted: logs/debug-20260120.log
Removed: cortex/utils/__pycache__/

Cleanup complete: 6 items processed
```

Files animate: floating up, sorting into archive folder (amber) or recycling bin (red fade).

**Important note** (glassmorphic info card):
> "Vacuum ARCHIVES, not deletes, when possible. Find archived files in `.cortex-runtime/archive/`."

**Analogy overlay:** *"/vacuum is your workspace janitor — keeps things tidy so you can focus on code."*

### Scene 7 — When to Use Each Command (6:15 – 7:00)

**Decision flowchart** (glassmorphic flow diagram):

```
┌──────────────────────────────────────────────────────┐
│  What do you need?                                    │
└───────────────────────────┬──────────────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
    ▼                       ▼                       ▼
┌─────────┐           ┌─────────┐           ┌─────────┐
│ LEARN   │           │ DECIDE  │           │ VERIFY  │
│ /ask    │           │/challenge│          │ /audit  │
└─────────┘           └─────────┘           └─────────┘
                                                  │
                            ┌─────────────────────┼─────────────────────┐
                            │                                           │
                            ▼                                           ▼
                      ┌─────────┐                                 ┌─────────┐
                      │ STATUS  │                                 │ CLEAN   │
                      │ /health │                                 │ /vacuum │
                      └─────────┘                                 └─────────┘
```

Each command box glows as its use case is described.

**Summary card:**
| Command | Use When... |
|---------|-------------|
| `/ask` | You have a question about CORTEX |
| `/challenge` | You're planning to build something |
| `/audit` | You want to check code health |
| `/health` | Something seems wrong |
| `/vacuum` | Your workspace is cluttered |

**Closing text** (Space Grotesk):
**"Five commands. Complete control. Start using them today."**

**Vision callback:**
> *"CORTEX: $8,600 saved per team, per year. Zero guesswork."*

Logo pulse. End card.

---

## Notes

- This video builds directly on Video 08 — assumes CORTEX is already installed and working.
- Each command is demonstrated with a REAL scenario a developer would encounter.
- Output formats match actual CORTEX responses (same structure, same icons).
- The decision flowchart is the key takeaway — users should screenshot it as a reference.
- Sound design: command input = keystrokes; processing = subtle electronic hum; success = chime.
- NO deep dives into how commands work internally — that's covered in Videos 1-7.

```
