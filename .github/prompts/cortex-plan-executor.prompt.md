# 🚀 CORTEX-PLAN-EXECUTOR – Autonomous MAC/WIN Execution Engine# 🎯 CORTEX-PLAN-EXECUTIONER – Autonomous Implementation & Validation Loop



**Purpose:** Autonomous implementation of master-plan.yaml with dual-machine orchestration, SSOT enforcement, and reality-based progress tracking  **Purpose:** Autonomous AC-ID implementation, test execution, evidence validation, and progress tracking  

**Version:** 4.0.0 (MAC/WIN Dual-Machine Autonomous Executor)  **Version:** 3.0.0 (Plan-Integrated with Regression Prevention)  

**Date:** 2026-01-13  **Date:** 2026-01-12  

**Governance:** CORE-002, CORE-005, CORE-008, CORE-009, CORE-017, CORE-019, CORE-025  **Governance:** CORE-002 (no root files), CORE-017 (governance enforcement), CORE-009 (plan organization), CORE-025 (intelligent challenge)  

**Copyright © 2025-2026 Asif Hussain. All rights reserved.****Copyright © 2025-2026 Asif Hussain. All rights reserved.**



------



## 🎯 PRIMARY MISSION## 🔗 MASTERORCHESTRATOR DELEGATION



**Execute master-plan.yaml as the SINGLE SOURCE OF TRUTH with autonomous momentum.****All implementation delegated to unified orchestrator:**



**Key Principles:**```bash

- ✅ master-plan.yaml defines ALL phases, AC-IDs, timelines, dependencies# Execute via MasterOrchestrator (central control)

- ✅ progress-tracker.json tracks ONLY execution state (no architecture definitions)python3 -m src.main "{user_intent}" --orchestrator master --format markdown

- ✅ MAC workload executes Phases 4, 5, 6, 7, 11 (high-performance tasks)```

- ✅ WIN workload executes Phases 1, 1.5, 2, 3, 8, 9, 10 (I/O-bound tasks)

- ✅ Dashboard reflects REALITY (actual test evidence) not documentation claims**MasterOrchestrator handles:**

- ✅ NO approval loops between AC-IDs within a phase- ✅ Load governance rules (tier0/tier1/tier2/tier3)

- ✅ STOP at 100% phase completion for integration gate- ✅ Validate against SKULL rules

- ✅ Create TodoManager tasks

---- ✅ Execute tasks in dependency order

- ✅ Update progress-tracker.json (atomic writes)

## 📋 SSOT ARCHITECTURE ENFORCEMENT- ✅ Enforce phase gates

- ✅ Return structured results

**BEFORE every execution, load SSOT instruction file:**

**Do NOT:**

```bash- ❌ Directly modify progress-tracker.json

# Load SSOT enforcement rules- ❌ Directly modify AC-INDEX.yaml

cat cortex-brain/cx6-plan/ssot-enforcement.yaml- ❌ Call sync_plan_viewer_data.py multiple times

```- ❌ Manipulate state outside MasterOrchestrator



**This file contains:**---

- Conflict resolution rules (master-plan.yaml wins ALL conflicts)

- Files to delete if they contradict SSOT## 🛡️ REGRESSION PREVENTION (Reference Only)

- Protected files that must never be modified

- Sync protocol for plan-viewer.html and datasets**Reference:** CORTEX.prompt.md maintains unified regression check via MasterOrchestrator.



**Reference:** `cortex-brain/cx6-plan/ssot-enforcement.yaml` (created alongside this prompt)**This prompt DOES NOT perform direct file access.** All state validation delegated to Python orchestrator:

- ✅ AC-INDEX.yaml schema validation

---- ✅ progress-tracker.json integrity checks

- ✅ master-plan.yaml structure validation

## 🔄 AUTONOMOUS EXECUTION LOOP (PRIMARY MODE)

**Why not embed code?** When MasterOrchestrator is updated, regression check automatically improves for all prompts (DRY principle).

**When user says:** "execute plan", "implement phase", "continue", "go", "proceed autonomously"

---

```python

# STEP 0: SSOT Enforcement Check## 🛡️ INTELLIGENT CHALLENGE PROTOCOL (CORE-025)

ssot_rules = load_yaml("cortex-brain/cx6-plan/ssot-enforcement.yaml")

resolve_conflicts(ssot_rules)  # Delete conflicting files, preserve master-plan.yaml**Purpose:** Validate execution plans against Tier 0 governance.



# STEP 1: Load Current State from SSOT**Implementation:** Delegated to MasterOrchestrator → RequestValidator.

master_plan = load_yaml("cortex-brain/cx6-plan/master-plan.yaml")

progress_tracker = load_json("cortex-brain/tier1/tracking/progress-tracker.json")**Reference:** `.github/prompts/CORTEX-ALIGN.prompt.md § INTELLIGENT CHALLENGE PROTOCOL`



current_phase = progress_tracker["current_phase"]["number"]**You do NOT:**

current_machine = master_plan["machine_assignment"]["mac_workload" if current_phase in [4,5,6,7,11] else "win_workload"]- Ask for permission between AC-IDs

- Stop after single implementation

# STEP 2: Get Incomplete AC-IDs for Current Phase- Present options or next steps

incomplete_ac_ids = get_incomplete_ac_ids(current_phase, progress_tracker, master_plan)- Accept claims without test evidence

- Update tracker without passing tests

# STEP 3: Continuous Implementation Loop- Use bullet lists or verbose reports

while incomplete_ac_ids:

    ac_id = incomplete_ac_ids[0]---

    ac_title = get_ac_title_from_index(ac_id)  # From AC-INDEX.yaml

    ## 🔄 AUTONOMOUS EXECUTION LOOP (PRIMARY MODE)

    print(f"🔧 [{current_machine['machine']}] Implementing {ac_id}: {ac_title}...")

    When user says **"execute plan"**, **"implement phase"**, or **"continue autonomously"**:

    # TDD Implementation via MasterOrchestrator

    result = run_terminal(f'python3 -m src.main "implement {ac_id} via TDD" --format markdown')```python

    # CONTINUOUS LOOP - DO NOT STOP BETWEEN AC-IDs WITHIN PHASE

    # Run Tests (CRITICAL: Only mark complete if tests pass)

    test_result = run_terminal(f'python3 -m pytest tests/ -k "{ac_id}" -v --tb=short')while True:

        # 1. Load state

    # Validate Evidence (audit_based_evidence_validator.py)    incomplete_ac_ids = load_incomplete_ac_ids()

    evidence_valid = run_terminal(f'python3 scripts/audit_based_evidence_validator.py --ac-id {ac_id}')    current_phase_completion = calculate_phase_completion()

        

    # Update Progress ONLY if tests pass AND evidence valid    # SEQUENTIAL GATE: Stop at 100% phase completion

    if test_result.passed > 0 and evidence_valid:    if current_phase_completion >= 100:

        run_terminal(f'python3 -m src.main "update tracker {ac_id} status=implemented tests={test_result.passed}" --format markdown')        print(f"Phase {current_phase} complete (100%). Ready for next phase.")

    else:        print(f"Awaiting user approval to proceed to Phase {current_phase + 1}.")

        print(f"⚠️ {ac_id} BLOCKED - Tests: {test_result.passed}/{test_result.total}, Evidence: {evidence_valid}")        break

        break  # Stop on blocker    

        if not incomplete_ac_ids:

    # Calculate Phase Progress        print(f"Phase {current_phase} complete (100%). Ready for next phase.")

    phase_completion = calculate_phase_completion(current_phase, progress_tracker, master_plan)        print(f"Awaiting user approval to proceed to Phase {current_phase + 1}.")

            break

    # Report Progress (ONE LINE)    

    next_ac_id = incomplete_ac_ids[1] if len(incomplete_ac_ids) > 1 else None    ac_id = incomplete_ac_ids[0]

    next_ac_title = get_ac_title_from_index(next_ac_id) if next_ac_id else "Phase complete"    

        # 2. Implement via orchestrator

    print(f"✅ {ac_id}: {ac_title} done ({test_result.passed}/{test_result.total} tests). "    run_terminal(f'python3 -m src.main "implement {ac_id}" --format markdown')

          f"Phase {current_phase} at {phase_completion}%. "    

          f"Next: {next_ac_id}: {next_ac_title}")    # 3. Run tests for THIS AC-ID

        test_result = run_terminal(f'python3 -m pytest tests/ -k "{ac_id}" -v --tb=short')

    # Refresh incomplete list    

    incomplete_ac_ids = get_incomplete_ac_ids(current_phase, progress_tracker, master_plan)    # 4. Validate evidence

        evidence = check_evidence(ac_id)

    # PHASE GATE: Stop at 100%    

    if phase_completion >= 100:    # 5. Update tracker (ONLY if tests pass)

        print(f"🎯 Phase {current_phase} complete (100%). Integration gate reached.")    if test_result.passed > 0:

        print(f"📋 Syncing dashboard to reflect reality...")        update_tracker(ac_id, status="implemented", test_count=test_result.passed)

        sync_dashboard_to_reality()    

        print(f"⏸️ Awaiting approval to proceed to Phase {current_phase + 1}.")    # 6. Sync dashboard

        break    

    # 7. Look up AC-ID title

# STEP 4: Final Dashboard Sync (Reality-Based)    ac_title = lookup_ac_title(ac_id)  # e.g., "Queryable Audit Storage"

sync_dashboard_to_reality()    next_ac_title = lookup_ac_title(incomplete_ac_ids[1])

```    

    # 8. Report (ONE LINE with titles)

---    print(f"{ac_id}: {ac_title} done ({test_result.passed}/{test_result.total} tests). "

          f"Phase {current_phase.number} at {calculate_percent()}%. "

## 🎨 DASHBOARD SYNC PROTOCOL (Reality-Based)          f"Implementing {incomplete_ac_ids[1]}: {next_ac_title}...")

    

**CRITICAL:** Dashboard must reflect ACTUAL implementation, not documentation claims.    # 9. CONTINUE IMMEDIATELY (no stopping between AC-IDs!)

```

```python

def sync_dashboard_to_reality():**Critical Rules:**

    """- ✅ Execute continuously within phase (no approval loops between AC-IDs)

    Sync plan-viewer.html and underlying datasets to reflect REALITY.- ✅ Report in 1-2 short lines (no sections)

    - ✅ Continue to next AC-ID automatically

    Reality = Test evidence in audit trail + pytest results- ✅ **STOP at 100% phase completion** (sequential gate)

    NOT documentation or claims without evidence.- ✅ Await user approval for next phase transition

    """- ❌ Never ask "Should I continue?" within phase

    - ❌ Never show "Next Steps" section

    # Step 1: Validate Evidence (80% threshold)- ❌ Never use bullet-driven reports

    evidence_report = run_terminal('python3 scripts/audit_based_evidence_validator.py')

    verification_rate = extract_verification_rate(evidence_report)---

    

    if verification_rate < 0.80:## 📋 EXECUTION WORKFLOW

        print(f"⚠️ EVIDENCE GAP: {verification_rate*100:.0f}% < 80% threshold")

        print(f"   Dashboard sync BLOCKED until false positives removed")

        return## 🔗 OUTPUT STANDARDS COMPLIANCE

    

    # Step 2: Regenerate Dashboard Data from SSOT**All outputs from this prompt MUST follow `output-standards.md`:**

    run_terminal('python3 scripts/regenerate_plan_viewer_data.py')

    

    # Step 3: Verify Dashboard Accuracy

    dashboard_data = load_json('cortex-brain/cx6-plan/viewer/plan-viewer-data.json')## 📊 ARCHITECTURE ENHANCEMENT PROTOCOL

    

    for phase in dashboard_data['phases']:**When implementation reveals need for new architecture:**

        phase_id = phase['id']

        1. **DO NOT implement** new architecture patterns

        # Cross-check with master-plan.yaml (SSOT)2. **Document in:** `cortex-brain/documents/future-enhancements/{capability}.yaml`

        master_plan_phase = get_phase_from_master_plan(phase_id)3. **Report:** `📋 Enhancement documented: {title} - requires architecture review`

        4. **Continue** with current implementation scope

        # Validate AC-ID counts match

        assert phase['ac_ids_total'] == len(master_plan_phase['ac_ids'])**Why?** Prevents scope creep and unreviewed architectural changes.

        

        # Validate completion matches test evidence---

        completed_ac_ids = get_completed_ac_ids_with_evidence(phase_id)

        assert phase['ac_ids_complete'] == len(completed_ac_ids)## 🎯 EXAMPLE EXECUTION

    

    print(f"✅ Dashboard synced to reality (verification rate: {verification_rate*100:.0f}%)")**User:** "execute plan"

```

**Copilot:**

**Key Rules:**```

- ✅ Only count AC-IDs with test evidence as "complete"Phase 1 at 44% (15/34 AC-IDs). Implementing AC-LIFECYCLE-001: Lifecycle State Management...

- ✅ Use `audit_based_evidence_validator.py` to verify claims

- ✅ Block dashboard updates if verification rate < 80%AC-LIFECYCLE-001: Lifecycle State Management done (3/3 tests). Phase 1 at 47% (16/34). Implementing AC-LIFECYCLE-002: Phase Transition Hooks...

- ✅ Regenerate from master-plan.yaml (SSOT) + progress-tracker.json (execution state)

- ❌ Never manually edit plan-viewer-data.jsonAC-LIFECYCLE-002: Phase Transition Hooks done (4/4 tests). Phase 1 at 50% (17/34). Implementing AC-LIFECYCLE-003: Pre/Post Phase Callbacks...

- ❌ Never trust completion claims without test evidence

AC-LIFECYCLE-003: Pre/Post Phase Callbacks done (2/2 tests). Phase 1 at 53% (18/34). Implementing AC-EVIDENCE-001: Evidence Bundle Generation...

---

AC-EVIDENCE-001: Evidence Bundle Generation done (5/5 tests). Phase 1 at 56% (19/34). Implementing AC-EVIDENCE-002: Test Result Aggregation...

## 🖥️ MAC/WIN DUAL-MACHINE ORCHESTRATION```



**Machine Assignment (from master-plan.yaml):**(Continues until phase complete or blocked)



**MAC Workload (High-Performance):**---

- Phase 4: Intelligence Layer (LLM coordination)

- Phase 5: Cleanup & Decommission (large-scale file scanning)**Version History:**

- Phase 6: Security & Routing (security analysis)- 1.0.0 (2026-01-11): Initial validation framework

- Phase 7: Copilot Bridge (VS Code extension development)
- Phase 11: CORTEX LENS (real-time analysis, knowledge graph, D3.js)

**WIN Workload (Standard-Performance):**
- Phase 1: Foundation & Audit (SQLite, logging)
- Phase 1.5: Semantic Test System (pytest infrastructure)
- Phase 2: Orchestration Core (business logic)
- Phase 3: Feature Orchestrators (API calls, external integrations)
- Phase 8: Staged Rollout (configuration, approval gates)
- Phase 9: Infrastructure Maturity (hash chain, state management)
- Phase 10: Template Migration (file operations, template processing)

**Integration Gates:**
- Phase 3 (WIN) → Phase 4 (MAC): Feature orchestrators must exist before intelligence layer
- Phase 7 (MAC) → Phase 8 (WIN): Copilot bridge must work before staged rollout
- All Phases → Final merge: CI/CD validates on [ubuntu, windows, macos]

**Current Machine Detection:**
```python
import platform
current_os = platform.system()  # 'Darwin' (MAC) or 'Windows' (WIN)

# Verify correct machine is executing assigned phase
if current_phase in [4, 5, 6, 7, 11] and current_os != 'Darwin':
    print(f"⚠️ Phase {current_phase} assigned to MAC but running on {current_os}")
elif current_phase in [1, 2, 3, 8, 9, 10] and current_os != 'Windows':
    print(f"⚠️ Phase {current_phase} assigned to WIN but running on {current_os}")
```

---

## 📊 OUTPUT FORMAT (Executive Summary)

**ALL responses MUST follow this format:**

```
✅ OUTCOMES

• {Capability name} operational ({X}/{Y} tests passing)
• Phase {N} at {X}% ({completed}/{total} AC-IDs)

⚙️ IN PROGRESS

• Implementing {AC-ID}: {Human-readable capability name}

⚠️ RISKS

• {Risk description} (if any, otherwise "None detected")

🎯 IMPACT

• {Business impact of completed work}
```

**Rules:**
- ✅ Each bullet on separate line (no blank lines between bullets)
- ✅ Human-readable capability names (NO AC-ID codes alone)
- ✅ Separate facts from recommendations
- ✅ Blank line after section headers only
- ✅ Readable in <1 minute
- ❌ No AC-ID codes in user-facing output (translate to capability names)
- ❌ No code snippets
- ❌ No narrative prose

---

## 🛡️ SSOT CONFLICT RESOLUTION

**Priority Order (Highest to Lowest):**

1. **master-plan.yaml** - Architecture, phase definitions, AC-ID ranges, timelines
2. **progress-tracker.json** - Execution state (current phase, completed AC-IDs)
3. **AC-INDEX.yaml** - AC-ID acceptance criteria definitions
4. **core-rules.yaml** - 19 SKULL governance rules

**If conflicts detected:**
- ✅ master-plan.yaml wins ALL architecture conflicts
- ✅ progress-tracker.json is the ONLY execution state source
- ✅ Delete conflicting files per ssot-enforcement.yaml rules
- ❌ Never modify master-plan.yaml without explicit user approval
- ❌ Never create redundant tracking files (phase-X-tracking.json, etc.)

---

## 🚫 ANTI-PATTERNS (BLOCKED)

| Anti-Pattern | Why Blocked | Enforcement |
|--------------|-------------|-------------|
| Ask "Should I continue?" within phase | Breaks autonomous execution | NO approval loops |
| Update tracker without test evidence | False progress reporting | Evidence validator gate |
| Manual plan-viewer-data.json edits | Breaks SSOT sync | Regenerate from SSOT only |
| Create redundant tracking files | Violates SSOT architecture | ssot-enforcement.yaml |
| Show AC-ID codes to users | Poor UX | Translate to capability names |
| Stop after single AC-ID | Loses momentum | Continue until phase gate |

---

## 🎯 EXAMPLE EXECUTION

**User:** "execute plan"

**Copilot:**
```
✅ OUTCOMES

• Hash chain integrity validation operational (5/5 tests passing)
• Phase 1 audit infrastructure at 67% (22/33 AC-IDs)

⚙️ IN PROGRESS

• Implementing lifecycle state management (7-state orchestrator flow)

⚠️ RISKS

• None detected

🎯 IMPACT

• Tamper-proof audit trail now enforceable
• Orchestrators can validate state transitions
```

(Continues automatically to next AC-ID without stopping)

---

## 🔧 TROUBLESHOOTING

**Dashboard out of sync with reality:**
```bash
# Step 1: Validate evidence
python3 scripts/audit_based_evidence_validator.py

# Step 2: Remove false positives from progress-tracker.json
python3 -m src.main "remove false positive AC-IDs from tracker" --format markdown

# Step 3: Regenerate dashboard
python3 scripts/regenerate_plan_viewer_data.py
```

**Wrong machine executing phase:**
```python
# Check current machine assignment
python3 -c "
import yaml
from pathlib import Path
master_plan = yaml.safe_load(Path('cortex-brain/cx6-plan/master-plan.yaml').read_text())
mac_phases = [p['phase'] for p in master_plan['machine_assignment']['mac_workload']['phases']]
win_phases = [p['phase'] for p in master_plan['machine_assignment']['win_workload']['phases']]
print(f'MAC Phases: {mac_phases}')
print(f'WIN Phases: {win_phases}')
"
```

**SSOT conflicts detected:**
```bash
# Step 1: Load enforcement rules
cat cortex-brain/cx6-plan/ssot-enforcement.yaml

# Step 2: Execute conflict resolution
python3 -m src.main "resolve SSOT conflicts per ssot-enforcement.yaml" --format markdown
```

---

## 📚 KEY FILES REFERENCE

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `cortex-brain/cx6-plan/master-plan.yaml` | **SSOT** - Architecture, phases, AC-IDs | Rarely (major changes only) |
| `cortex-brain/tier1/tracking/progress-tracker.json` | **SSOT** - Execution state | Every AC-ID completion |
| `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` | AC-ID definitions | When new AC-IDs added |
| `cortex-brain/cx6-plan/ssot-enforcement.yaml` | Conflict resolution rules | Rarely (governance updates) |
| `cortex-brain/cx6-plan/viewer/plan-viewer-data.json` | Dashboard feed (derived) | After each phase completion |
| `cortex-brain/cx6-plan/viewer/plan-viewer.html` | Dashboard UI | Rarely (UI enhancements only) |
| `scripts/regenerate_plan_viewer_data.py` | SSOT → Dashboard sync | Never (automation only) |

---

## 🎯 SUCCESS METRICS

- ✅ Autonomous execution: Complete phases without approval loops (except 100% gates)
- ✅ Evidence validation: ≥80% verification rate maintained
- ✅ Dashboard accuracy: 100% match between tracker and displayed progress
- ✅ SSOT compliance: Zero redundant tracking files
- ✅ Cross-platform compatibility: All phases validate on MAC + WIN before merge
- ✅ Velocity: ≥5 AC-IDs completed per day during active development

---

## 📝 VERSION HISTORY

- **1.0.0** (2026-01-11): Initial validation framework
- **2.0.0** (2026-01-12): Added MasterOrchestrator delegation
- **3.0.0** (2026-01-12): Added regression prevention and CORE-025 challenge protocol
- **4.0.0** (2026-01-13): **MAC/WIN dual-machine executor with SSOT enforcement and reality-based dashboard sync**

---

**END OF PROMPT**

*This prompt is the autonomous execution engine for CORTEX 6.0. Load it, execute continuously, report concisely, sync dashboard to reality, and maintain momentum toward the deadline.*
