# CORTEX Execution Agent

**Version:** 1.0.0  
**Date:** 2026-01-13  
**Author:** Asif Hussain

## Overview

The CORTEX Execution Agent is an autonomous executor that maintains perfect synchronization between:
- **master-plan.yaml** (architecture SSOT)
- **progress-tracker.json** (execution SSOT)
- **plan-viewer.html** (dashboard display)
- **Audit trail** (evidence verification)

## Architecture

```
SINGLE SOURCE OF TRUTH (SSOT):
master-plan.yaml (architecture) + progress-tracker.json (execution)
        ↓ (read by)
CortexExecutionAgent (autonomous loop)
        ↓ (triggers)
regenerate_plan_viewer_data.py (sync script)
        ↓ (writes)
plan-viewer-data.json (derived feed)
        ↓ (displays in)
plan-viewer.html (browser dashboard)
```

## Installation

No additional dependencies required. Uses Python stdlib only.

```bash
# Make executable
chmod +x cortex-exec.py

# Verify installation
python3 cortex-exec.py status
```

## Usage

### Check Current Status
```bash
python3 cortex-exec.py status
```

Output:
```
============================================================
📊 CORTEX EXECUTION STATUS
============================================================

📍 Current Phase: 2 - Orchestration Core
📈 Completion: 24.6%
🔖 Status: in_progress

📋 Remaining AC-IDs: 42

Next to implement:
  • AC-ORCH-001: MasterOrchestrator (Central Controller)
  • AC-ORCH-002: Request evaluation engine
  • AC-ORCH-003: Dependency resolution
  ... and 39 more
============================================================
```

### Validate Evidence
```bash
python3 cortex-exec.py validate
```

Validates audit trail evidence for completed AC-IDs. Requires ≥80% verification rate to pass.

### Sync Dashboard
```bash
python3 cortex-exec.py sync
```

Manually trigger dashboard sync from SSOT (master-plan + progress-tracker).

### Execute Autonomous Loop
```bash
python3 cortex-exec.py continue
```

**This is the main execution mode.** Runs continuous loop until:
- Phase reaches 100% completion
- Evidence gate blocks (<80% verification)
- Blocker detected
- Max iterations reached (default: 100)

## Autonomous Execution Loop

```python
while not_complete:
    1. Load SSOT state (master-plan + progress-tracker)
    2. Validate evidence (gate: ≥80% verification rate)
    3. Get incomplete AC-IDs from current phase
    4. For each AC-ID:
       a. Implement via TDD (delegate to MasterOrchestrator)
       b. Run tests
       c. Collect evidence
       d. Update progress-tracker.json (atomic)
    5. Auto-sync dashboard (regenerate_plan_viewer_data.py)
    6. Check phase gate (100% → next phase)
```

**NO approval loops.** Executes until phase complete or blocker detected.

## SSOT Enforcement

### Authority Hierarchy (Highest to Lowest):
1. **master-plan.yaml** (ABSOLUTE) → Defines architecture
2. **progress-tracker.json** (HIGH) → Tracks execution
3. **AC-INDEX.yaml** (MEDIUM) → Defines acceptance criteria
4. **core-rules.yaml** (MEDIUM) → Enforces behavior

### Protected Files (NEVER Delete):
- ✅ `cortex-brain/cx6-plan/master-plan.yaml`
- ✅ `cortex-brain/tier1/tracking/progress-tracker.json`
- ✅ `cortex-brain/tier0/governance/core-rules.yaml`
- ✅ `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
- ✅ `scripts/regenerate_plan_viewer_data.py`

### Redundant Files (DELETE if found):
- ❌ `phases/phase-X-tracking.json` (duplicates progress-tracker.json)
- ❌ `scripts/sync_plan_viewer_*.py` (replaced by regenerate script)
- ❌ `cx6-plan/phases/phase-*-plan.yaml` (duplicates master-plan.yaml)

## Evidence Validation

Evidence validation runs automatically before each execution cycle:

```bash
# Validation workflow
1. Run: scripts/audit_based_evidence_validator.py
2. Check: verification_rate ≥ 80%
3. If pass → Execute AC-IDs
4. If fail → Block until false positives fixed
```

Results saved to: `cortex-brain/documents/validation/evidence-validation-results.json`

## Dashboard Sync

Dashboard sync is **automatic** after every state change:

```
MasterOrchestrator updates progress-tracker.json
    ↓
Auto-triggers: regenerate_plan_viewer_data.py
    ↓
Reads: master-plan.yaml + progress-tracker.json + AC-INDEX.yaml
    ↓
Writes: plan-viewer-data.json (atomic)
    ↓
Browser refreshes → sees current state (zero staleness)
```

Manual sync is available but rarely needed:
```bash
python3 cortex-exec.py sync
```

## Multi-Machine Development

Agent supports parallel development on MAC + WIN:

**Platform Compatibility:** 90% cross-platform (9/11 phases fully portable)
- 🟢 **CROSS-PLATFORM:** Phases 1, 1.5, 2, 4-10
- 🟡 **PLATFORM-AWARE:** Phases 3, 11 (minor platform-specific components)

**Best Practices:**
- ✅ Use `pathlib.Path` for ALL file operations (CORE-005)
- ✅ Test on BOTH platforms before merging
- ✅ Use platform detection for optional features
- ❌ Never hardcode `/Users/` or `C:\\` paths

## Governance Enforcement

Agent enforces 19 SKULL rules (CORE-001 to CORE-019):

**Key Rules:**
- **CORE-001:** Incremental execution (<500 lines per operation)
- **CORE-002:** No summary files
- **CORE-005:** Path portability (use `pathlib.Path`)
- **CORE-008:** TDD enforcement
- **CORE-009:** Plan file organization
- **CORE-017:** Governance enforcement
- **CORE-019:** TDD-Master required (no direct coding)

Violations are blocked at runtime by MasterOrchestrator.

## Response Format

Agent reports in executive bullet format:

```markdown
✅ OUTCOMES

• Hash chain integrity validation operational (5/5 tests passing)
• Phase 2 at 35% (15/42 capabilities complete)

⚙️ IN PROGRESS

• Implementing lifecycle state management

⚠️ RISKS

• None detected

🎯 IMPACT

• Tamper-proof audit trail enforceable
• Orchestrators can validate state transitions
```

**Critical Rules:**
- ✅ Each bullet on separate line
- ✅ Human-readable capability names (NO AC-ID codes alone)
- ✅ Translate AC-IDs to plain English
- ✅ Readable in <1 minute
- ❌ NO code snippets in user-facing output

## Troubleshooting

### "Phase X not found in master-plan.yaml"
**Cause:** Phase definition missing or renamed  
**Fix:** Check `master-plan.yaml` for phase key format (e.g., `phase_2_orchestration_core`)

### "Evidence validation failed"
**Cause:** Verification rate < 80%  
**Fix:** Run `python3 scripts/audit_based_evidence_validator.py` and fix false positives

### "Dashboard sync failed"
**Cause:** `regenerate_plan_viewer_data.py` error  
**Fix:** Check script output for YAML/JSON parsing errors

### "Path not found" (cross-platform)
**Cause:** Hardcoded paths (CORE-005 violation)  
**Fix:** Replace with `pathlib.Path` operations

## Integration with CORTEX.prompt.md

Agent is invoked by main CORTEX gateway:

```markdown
User request → CORTEX.prompt.md (clarify intent)
    ↓
User confirms → python3 cortex-exec.py continue
    ↓
Autonomous loop → Implement AC-IDs via MasterOrchestrator
    ↓
Report results → Executive bullet format
```

## API Reference

### SSotManager
- `load_master_plan()` → Load architecture SSOT
- `load_progress_tracker()` → Load execution SSOT
- `load_ac_index()` → Load acceptance criteria SSOT
- `load_core_rules()` → Load governance SSOT

### EvidenceValidator
- `validate()` → Run evidence validator, return (verification_rate, results)

### DashboardSyncer
- `sync()` → Sync dashboard from SSOT

### CortexExecutionAgent
- `get_current_state()` → Load current execution state
- `get_ac_title(ac_id)` → Get human-readable title for AC-ID
- `validate_evidence_gate()` → Validate evidence (≥80% gate)
- `get_incomplete_ac_ids(state)` → Get incomplete AC-IDs for current phase
- `sync_dashboard()` → Sync dashboard from SSOT
- `display_status()` → Display current execution status
- `execute_autonomous_loop(max_iterations)` → Execute autonomous loop

## Version History

- **1.0.0** (2026-01-13): Initial release
  - Autonomous execution loop
  - SSOT enforcement
  - Evidence validation
  - Dashboard sync integration
  - Multi-machine support

## License

Copyright © 2025-2026 Asif Hussain. All rights reserved.
