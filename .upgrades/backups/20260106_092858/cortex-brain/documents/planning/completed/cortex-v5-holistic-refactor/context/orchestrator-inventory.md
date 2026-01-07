# CORTEX Orchestrator Inventory

**Created:** January 2, 2026  
**Phase:** 0 - Foundation Setup (Task 0.3)  
**Purpose:** Complete catalog of orchestrators with current issues

---

## Orchestrator Classification

**Total:** 12 active orchestrators  
**AUTONOMOUS:** 4 (claim autonomy, actually hybrid)  
**GUIDED:** 8 (intentionally CORTEX-driven)

---

## 🛡️ AUTONOMOUS Orchestrators

### 1. Planning System v4.0

**File:** `src/orchestrators/planning_orchestrator.py`  
**Manifest:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`  
**Status:** 🔴 CRITICAL - Needs complete rewrite

**Current Behavior:**
- Claims to generate plans autonomously
- Actually requires CORTEX to read manifest and execute steps
- Stores state in JSON file without transactions

**Issues:**
1. No automatic recovery from failures
2. Manual context gathering (requires CORTEX tool calls)
3. No validation of generated plans
4. File-based state (no ACID guarantees)
5. Hardcoded folder structure paths

**Configuration Source:** Hybrid (YAML config + natural language instructions)

**Migration Strategy:** 
- Phase 4: Build Planning Orchestrator v5 (pure Python)
- Config-only manifest with Jinja2 templates
- SQLite state tracking

---

### 2. ADO Operations

**File:** `src/cortex_agents/ado_agent.py` (not orchestrator!)  
**Manifest:** `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml`  
**Status:** 🔴 CRITICAL - No dedicated orchestrator exists

**Current Behavior:**
- Logic scattered across `ado_agent.py`
- CORTEX calls agent methods directly
- No orchestrator pattern applied

**Issues:**
1. Not actually an orchestrator - just an agent
2. No workflow management
3. No state tracking
4. Tightly coupled to ADO API

**Configuration Source:** Manifest contains instructions, not data

**Migration Strategy:**
- Phase 6: Build ADO Orchestrator v2 from scratch
- Extract logic from agent into orchestrator
- Config-driven work item generation

---

### 3. Vacuum Orchestrator

**File:** `.github/prompts/cortex-vacuum.prompt.md`  
**Manifest:** None (prompt file serves as manifest)  
**Status:** 🔴 CRITICAL - No Python implementation

**Current Behavior:**
- Defined entirely in prompt file
- CORTEX follows markdown instructions
- No state persistence

**Issues:**
1. No Python code - only natural language instructions
2. No rollback capability for file deletions
3. No dry-run mode
4. No safety checks before destructive operations

**Configuration Source:** Prompt file (entirely natural language)

**Migration Strategy:**
- Phase 6: Build Vacuum Orchestrator v2 (Python)
- Atomic filesystem operations
- Transaction boundaries with rollback
- Safety validations

---

### 4. Cleanup Orchestrator

**File:** Embedded in `cortex-maintenance.prompt.md` (Phase 2)  
**Manifest:** `cortex-brain/cleanup-rules.yaml`  
**Status:** 🟡 HIGH - Part of maintenance, not standalone

**Current Behavior:**
- Runs as Phase 2 of system maintenance
- CORTEX executes cleanup rules
- Some Python utilities exist

**Issues:**
1. Not standalone - tied to maintenance workflow
2. Execution order not deterministic
3. No state tracking
4. Rules need manual interpretation

**Configuration Source:** `cleanup-rules.yaml` (data + some instructions)

**Migration Strategy:**
- Phase 6: Extract into Cleanup Orchestrator v2
- Standalone execution capability
- Deterministic rule application
- State persistence

---

## 📋 GUIDED Orchestrators

### 5. Upgrade Orchestrator v2

**File:** `src/orchestrators/upgrade_orchestrator_v2.py`  
**Base Class:** Extends `BaseOrchestrator`  
**Status:** 🟢 MEDIUM - Works well, needs v4.1 base

**Current Behavior:**
- Manages CORTEX system upgrades
- Uses session state for tracking
- Well-structured Python code

**Strengths:**
- Clear Python implementation
- Extends base class (good pattern)
- Error handling exists

**Issues:**
1. Session-dependent (doesn't work standalone)
2. No checkpoint/rollback capability
3. Hardcoded upgrade paths

**Migration Strategy:**
- Phase 7: Migrate to BaseOrchestrator v4.1
- Add checkpoint creation
- Externalize upgrade paths to config

---

### 6. Git Checkpoint Orchestrator

**File:** `src/orchestrators/git_checkpoint_orchestrator.py`  
**Status:** 🟢 MEDIUM - Simple, effective

**Current Behavior:**
- Creates git tags for checkpoints
- Validates checkpoint names
- Integrates with brain protection rules

**Strengths:**
- Focused, single responsibility
- Uses existing git infrastructure
- Clear error messages

**Issues:**
1. No recovery from failed checkpoints
2. Hardcoded naming conventions
3. No metadata storage beyond git

**Migration Strategy:**
- Phase 7: Migrate to BaseOrchestrator v4.1
- Add metadata to SQLite
- Support checkpoint querying

---

### 7. Git Sync and Optimize

**File:** `src/orchestrators/git_sync_and_optimize.py`  
**Status:** 🟢 MEDIUM - Works, could be cleaner

**Current Behavior:**
- Multi-machine sync verification
- Force-sync with reset --hard
- Follows commit workflow

**Strengths:**
- Solves real multi-machine problem
- Clear 7-phase workflow
- Good error recovery

**Issues:**
1. Tool-call driven (not self-contained)
2. No transaction boundaries
3. Hardcoded git commands

**Migration Strategy:**
- Phase 7: Assess if needs migration (might stay GUIDED)
- Externalize git commands to config
- Add state tracking

---

### 8. Rollback Orchestrator

**File:** `src/orchestrators/rollback_orchestrator.py`  
**Dependencies:** `PhaseCheckpointManager`, `SessionModel`  
**Status:** 🟡 HIGH - Session-dependent, fragile

**Current Behavior:**
- Rolls back to previous phase checkpoints
- Reads session state to determine rollback target
- Restores file system state

**Strengths:**
- Addresses real need (undo operations)
- Integrates with checkpoint system

**Issues:**
1. Tightly coupled to session state (doesn't work without active session)
2. No database state - relies on JSON files
3. Limited to same-session rollback
4. File restoration is not transactional

**Migration Strategy:**
- Phase 7: Major refactor needed
- Use SQLite snapshots instead of JSON
- Support cross-session rollback
- Atomic filesystem operations

---

### 9. Onboarding Acknowledgment Orchestrator

**File:** `src/orchestrators/onboarding_acknowledgment_orchestrator.py`  
**Status:** 🟢 MEDIUM - Interactive, works as intended

**Current Behavior:**
- Guides new users through CORTEX capabilities
- Interactive Q&A format
- Tracks acknowledgment state

**Strengths:**
- Great user experience
- Clear progression
- State tracking via JSON

**Issues:**
1. Hardcoded questions/answers
2. No multi-language support
3. State in JSON (not queryable)

**Migration Strategy:**
- Phase 7: Assess if migration beneficial
- Externalize content to templates
- Consider keeping GUIDED (benefits from CORTEX interaction)

---

### 10. Master Setup Orchestrator

**File:** `src/orchestrators/master_setup_orchestrator.py`  
**Status:** 🟢 MEDIUM - Rarely used, works

**Current Behavior:**
- Initial CORTEX system setup
- Validates configuration files
- Creates directory structure

**Strengths:**
- Comprehensive validation
- Clear error messages
- Only runs once (setup)

**Issues:**
1. Hardcoded validation rules
2. No setup state tracking
3. Can't re-run safely (not idempotent)

**Migration Strategy:**
- Low priority (rarely executed)
- Phase 7: Add idempotency
- Externalize validation rules

---

### 11. Alignment Orchestrator

**File:** `src/orchestrators/alignment_orchestrator.py`  
**Status:** 🟢 MEDIUM - Template utility

**Current Behavior:**
- Aligns response formatting
- Applies templates consistently
- Validates response structure

**Strengths:**
- Ensures consistent output
- Template-driven (good pattern)
- Simple, focused

**Issues:**
1. Template paths hardcoded
2. No template validation
3. Limited template library

**Migration Strategy:**
- Phase 7: Migrate to use Jinja2 templates
- Add template schema validation
- Expand template library

---

### 12. Application Health Orchestrator

**File:** `src/orchestrators/application_health_orchestrator.py`  
**Status:** 🟢 MEDIUM - Diagnostic utility

**Current Behavior:**
- Runs health checks
- Validates configuration files
- Checks dependencies

**Strengths:**
- Comprehensive diagnostics
- Clear health report format
- Catches common issues

**Issues:**
1. Hardcoded check list
2. No historical health tracking
3. Can't trigger auto-remediation

**Migration Strategy:**
- Phase 7: Externalize checks to config
- Add health history to database
- Integrate with incident response

---

## Orchestrator Comparison Matrix

| Orchestrator | Python Code | Config File | State Management | Recovery | Test Coverage | Priority |
|--------------|-------------|-------------|------------------|----------|---------------|----------|
| Planning v4 | Hybrid | Hybrid | JSON | ❌ | Low | 🔴 P0 |
| ADO Ops | Agent only | Hybrid | None | ❌ | None | 🔴 P0 |
| Vacuum | Prompt only | None | None | ❌ | None | 🔴 P0 |
| Cleanup | Scattered | YAML | None | ❌ | Low | 🟡 P1 |
| Upgrade v2 | ✅ | None | Session | ⚠️ | Medium | 🟢 P2 |
| Git Checkpoint | ✅ | Rules | Git | ⚠️ | Medium | 🟢 P2 |
| Git Sync | ✅ | None | None | ⚠️ | Low | 🟢 P3 |
| Rollback | ✅ | None | JSON | ⚠️ | Low | 🟡 P1 |
| Onboarding | ✅ | None | JSON | ⚠️ | Medium | 🟢 P3 |
| Setup | ✅ | Validation | None | ❌ | Low | 🟢 P3 |
| Alignment | ✅ | Templates | None | N/A | Medium | 🟢 P3 |
| Health | ✅ | None | None | N/A | Low | 🟢 P3 |

**Legend:**
- 🔴 P0: Critical - Phase 4-6 (Bootstrap + Early Migration)
- 🟡 P1: High - Phase 6 (Migration batch 1)
- 🟢 P2-P3: Medium/Low - Phase 6 (Later migration)

---

## Common Patterns Analysis

### What's Working

**Good Patterns:**
1. `BaseOrchestrator` extension (Upgrade v2)
2. Single responsibility focus (Git Checkpoint)
3. Clear error messages (most orchestrators)
4. Template usage (Alignment)

### What's Broken

**Anti-Patterns:**
1. Natural language in manifests (Planning, ADO, Vacuum)
2. Session dependency (Upgrade, Rollback)
3. JSON file state (multiple orchestrators)
4. Hardcoded paths/rules (most orchestrators)
5. No base class (many orchestrators)

---

## Migration Decision Tree

```
For each orchestrator:
  ├─ Is logic in Python? 
  │   ├─ Yes: Can we improve with v4.1 base?
  │   │   ├─ Yes → Migrate to BaseOrchestrator v4.1 (Phase 7)
  │   │   └─ No → Keep as-is (document why)
  │   └─ No: MUST rewrite in Python (Phase 4-6)
  │
  ├─ Does it need state persistence?
  │   ├─ Yes → Add SQLite integration (Phase 2 schema)
  │   └─ No → Document stateless design
  │
  ├─ Does it have config file?
  │   ├─ Yes: Is it data-only or hybrid?
  │   │   ├─ Hybrid → Separate config from instructions
  │   │   └─ Data-only → Validate against schema
  │   └─ No → Consider if config would help
  │
  └─ Should it be AUTONOMOUS or GUIDED?
      ├─ Complex multi-phase workflow → AUTONOMOUS
      ├─ Requires user interaction → GUIDED
      └─ Simple tool integration → GUIDED
```

---

**Status:** ✅ Orchestrator Inventory Complete  
**Next:** Create agent inventory document
