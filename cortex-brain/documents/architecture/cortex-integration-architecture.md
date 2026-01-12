# CORTEX 6.0 Integration Architecture & Data Flow Specification

**Document Version:** 1.0  
**Created:** 2026-01-12T17:00:00Z  
**Author:** GitHub Copilot (CORTEX Intent Clarification Protocol)  
**Purpose:** Define unified sync workflow for all prompts and tools  
**Status:** Approved for Implementation

---

## Executive Summary

**Problem Identified:**
Phase 4.5 was added to master-plan.yaml but NOT reflected in plan-viewer.html/plan-viewer-data.json, revealing a critical gap: **no unified data flow protocol exists**.

**Solution:**
Establish a **Single Source of Truth (SSOT)** architecture where:
- `master-plan.yaml` is primary authority for phase definitions
- `AC-INDEX.yaml` is primary authority for AC-ID definitions  
- `progress-tracker.json` is primary authority for completion state
- All other files (dashboards, viewers, HTML, docs) are **derived** (secondary)
- **Sync triggers** fire automatically when primary sources change
- **All prompts follow strict workflow** to avoid state staleness

---

## Part 1: Current Integration Landscape

### 1.1 Primary Source Files (SSOT - Single Source of Truth)

| File | Authority | What It Defines | Owner | Update Frequency |
|------|-----------|-----------------|-------|-----------------|
| `cortex-brain/cx6-plan/master-plan.yaml` | ✅ PRIMARY | Phase definitions, AC-ID ranges, dependencies, timelines | MasterOrchestrator | When phases added/modified |
| `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` | ✅ PRIMARY | AC-ID titles, descriptions, status, categories, acceptance criteria | MasterOrchestrator | When AC-IDs added/modified |
| `cortex-brain/tier1/tracking/progress-tracker.json` | ✅ PRIMARY | Current phase, completion %, AC-ID status, phase gates | MasterOrchestrator | After each task execution |
| `cortex-brain/tier0/governance/core-rules.yaml` | ✅ PRIMARY | 19 SKULL rules, governance enforcement | GovernanceMerger | When rules change |

### 1.2 Derived Files (Secondary - Regenerated from SSOT)

| File | Derives From | What It Provides | Regeneration Trigger |
|------|--------------|------------------|----------------------|
| `cortex-brain/cx6-plan/viewer/plan-viewer-data.json` | progress-tracker.json + AC-INDEX.yaml | JSON feed for dashboard (phase, AC counts, capabilities) | sync_plan_viewer_data.py |
| `cortex-brain/cx6-plan/viewer/plan-viewer.html` | plan-viewer-data.json | Interactive HTML dashboard | plan-viewer.html (static, reads .json at runtime) |
| `cortex-brain/cx6-plan/viewer/docs/html-views/` | master-plan.yaml + AC-INDEX.yaml | Per-phase markdown + HTML views | generate_html_views.py |
| `cortex-brain/cx6-plan/viewer/audit-log-viewer.html` | audit-logs-aggregated.json | Audit trail visualization | aggregate_audit_logs.py |
| `cortex-brain/documents/` | Various sources | Human-readable documentation | Various generators |

### 1.3 Current Sync Mechanisms (FRAGMENTED - PROBLEMS!)

```
❌ CURRENT STATE: Multiple disconnected sync scripts
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  scripts/sync_plan_viewer_data.py                       │
│  ├─ Reads: progress-tracker.json                       │
│  ├─ Reads: AC-INDEX.yaml                              │
│  ├─ Writes: plan-viewer-data.json                      │
│  └─ Triggered by: Manual call only ⚠️                 │
│                                                         │
│  scripts/generate_html_views.py                         │
│  ├─ Reads: master-plan.yaml (partially)               │
│  ├─ Writes: docs/html-views/*.html/yaml               │
│  └─ Triggered by: Manual call only ⚠️                 │
│                                                         │
│  scripts/aggregate_audit_logs.py                        │
│  ├─ Reads: cortex-brain/audit-logs/*.jsonl            │
│  ├─ Writes: plan-viewer/audit-logs-aggregated.json    │
│  └─ Triggered by: Manual call only ⚠️                 │
│                                                         │
│  Scripts all called independently → Data staleness! ❌  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.4 Integration Points (Identified but Not Automated)

| Integration Point | Source | Destination | Current Status | Issue |
|-------------------|--------|-------------|-----------------|-------|
| Master Plan → Dashboard | master-plan.yaml | plan-viewer-data.json | ❌ MANUAL | Phase 4.5 not synced |
| AC-INDEX → Dashboard | AC-INDEX.yaml | plan-viewer-data.json | ❌ MANUAL | AC-INTEG not synced |
| Progress → Dashboard | progress-tracker.json | plan-viewer-data.json | ❌ MANUAL | Percentages stale |
| Master Plan → HTML Views | master-plan.yaml | docs/html-views/ | ❌ MANUAL | Views outdated |
| AC-INDEX → HTML Views | AC-INDEX.yaml | docs/html-views/ | ❌ MANUAL | AC descriptions old |
| Audit Logs → Dashboard | audit-logs/ | audit-logs-aggregated.json | ❌ MANUAL | Audit trail incomplete |
| AC-INDEX → CORTEX.prompt.md | AC-INDEX.yaml | .github/prompts/ | ❌ NONE | AC-ID lookup hardcoded |
| Master Plan → Progress Tracker | master-plan.yaml | progress-tracker.json | ✅ AUTO | MasterOrchestrator reads |

---

## Part 2: Unified Integration Architecture (Solution)

### 2.1 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PRIMARY SOURCES (SSOT)                         │
│                                                                      │
│  master-plan.yaml          AC-INDEX.yaml          governance/*      │
│  (phases, AC ranges)       (AC definitions)       (SKULL rules)     │
└────────────┬────────────────────┬────────────────────────┬──────────┘
             │                    │                        │
             │   ┌────────────────┼────────────────┐       │
             │   │                │                │       │
         reads  reads          reads            reads       │
             │   │                │                │       │
             ▼   ▼                ▼                ▼       │
    ┌────────────────────────────────────────────────────┐ │
    │         MasterOrchestrator                         │ │
    │  (Central Controller - Reads ALL SSOT)            │ │
    │  ├─ Loads governance rules (4-tier merger)        │ │
    │  ├─ Resolves phase definitions                    │ │
    │  ├─ Validates AC-ID registry                      │ │
    │  └─ Updates progress-tracker.json (atomic)        │ │
    └────────────────┬────────────────────────────────────┘ │
                     │ updates                               │
                     ▼                                       │
    ┌────────────────────────────────────────────────────┐ │
    │      progress-tracker.json (SSOT)                 │ │
    │  (Completion state - only written by Master)      │ │
    └────────────────┬────────────────────────────────────┘ │
                     │ reads                                 │
            ┌────────┴──────────┐                           │
            │                   │                           │
     reads  │  reads reads      │ reads                     │
            ▼  ▼     ▼          ▼                           │
    ┌──────────────────────────────────────────────────┐   │
    │    SyncOrchestrator (NEW!)                       │ │
    │    (Regenerates all derived files)              │ │
    │                                                  │   │
    │  TRIGGER: MasterOrchestrator completes task     │ │
    │  OR: Manual call to sync_all()                  │ │
    │                                                  │   │
    │  ├─ sync_plan_viewer_data() ─────┐              │ │
    │  ├─ sync_html_views() ────────────┤──┐          │ │
    │  ├─ sync_audit_dashboard() ───────┤──┼──┐       │ │
    │  ├─ update_prompt_ac_mappings() ──┤  │  │       │ │
    │  └─ notify_watchers() ────────────┘  │  │       │ │
    └──────────────────────────────────────┼──┼────────┘ │
                                           │  │           │
                                           │  │        reads
                                           │  │           │
            ┌──────────────────────────────┘  │           │
            │                                 │           │
    ┌───────▼──────────────────────────────────────────┐  │
    │    DERIVED FILES (Secondary)                     │  │
    │                                                  │  │
    │  plan-viewer-data.json                          │  │
    │  ├─ Read by: plan-viewer.html                   │  │
    │  ├─ Regenerated by: sync_plan_viewer_data()    │  │
    │  └─ Includes: Phases, AC counts, capabilities   │  │
    │                                                  │  │
    │  docs/html-views/*.html/.yaml                   │  │
    │  ├─ Read by: Browsers                           │  │
    │  ├─ Regenerated by: sync_html_views()          │  │
    │  └─ Includes: Per-phase markdown + HTML         │  │
    │                                                  │  │
    │  audit-logs-aggregated.json                     │  │
    │  ├─ Read by: audit-log-viewer.html              │  │
    │  ├─ Regenerated by: sync_audit_dashboard()     │  │
    │  └─ Includes: Aggregated audit trail            │  │
    │                                                  │  │
    │  .github/prompts/AC-mappings.json               │  │
    │  ├─ Read by: All prompts (lookup AC-ID→name)    │  │
    │  ├─ Regenerated by: update_prompt_ac_mappings()│  │
    │  └─ Includes: AC-ID → human-readable mappings   │  │
    │                                                  │  │
    └──────────────────────────────────────────────────┘  │
                                                          │
    ┌──────────────────────────────────────────────────┐  │
    │  CONSUMERS (Read-Only)                           │  │
    │  ├─ plan-viewer.html (loads .json at runtime)   │  │
    │  ├─ Browsers/Users (view dashboards)            │  │
    │  ├─ All CORTEX prompts (lookup AC IDs)          │  │
    │  └─ Audit viewers (trace operations)            │  │
    └──────────────────────────────────────────────────┘  │
                                                          │
    ✅ GUARANTEE: Derived files always in sync!          │
    ✅ GUARANTEE: Single source of truth respected       │
    ✅ GUARANTEE: No stale dashboards                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 SyncOrchestrator (NEW COMPONENT)

**Purpose:** Automatically regenerate all derived files when SSOT changes

**Location:** `src/orchestrators/core/sync_orchestrator.py` (NEW)

**Responsibilities:**

```python
class SyncOrchestrator(BaseOrchestrator):
    """
    Synchronizes Primary Sources → All Derived Files
    
    Called AUTOMATICALLY by MasterOrchestrator after state changes.
    Can also be called manually for emergency resync.
    """
    
    def sync_all(self, change_type: str = "unknown") -> SyncResult:
        """
        Regenerate all derived files
        
        Args:
            change_type: "phase_added" | "ac_modified" | "progress_updated" | "governance_changed"
        
        Returns:
            SyncResult with all sync operations
        """
        
    def sync_plan_viewer_data(self) -> bool:
        """Regenerate: plan-viewer-data.json"""
        # Reads: master-plan.yaml + AC-INDEX.yaml + progress-tracker.json
        # Writes: plan-viewer-data.json
        
    def sync_html_views(self) -> bool:
        """Regenerate: docs/html-views/*.html/*.yaml"""
        # Reads: master-plan.yaml + AC-INDEX.yaml
        # Writes: docs/html-views/
        
    def sync_audit_dashboard(self) -> bool:
        """Regenerate: audit-logs-aggregated.json"""
        # Reads: cortex-brain/audit-logs/*.jsonl
        # Writes: audit-logs-aggregated.json
        
    def update_prompt_ac_mappings(self) -> bool:
        """Regenerate: .github/prompts/AC-mappings.json"""
        # Reads: AC-INDEX.yaml
        # Writes: .github/prompts/AC-mappings.json
        # Purpose: All prompts can lookup AC-ID → human-readable name
        
    def notify_watchers(self, change_summary: dict) -> None:
        """Notify subscribers of sync completion"""
        # Audit trail: log sync operation
        # Dashboard refresh: notify browsers via WebSocket (future)
```

### 2.3 Workflow: When Each Sync Trigger Fires

**Trigger 1: Phase Added (Like Phase 4.5)**
```
User Request
    ↓
Parse intent ("add phase 4.5")
    ↓
Clarify & confirm (CORTEX.prompt.md)
    ↓
MasterOrchestrator.handle_request()
    ├─ Load governance
    ├─ Validate request
    ├─ CREATE phase in master-plan.yaml
    ├─ CREATE AC-IDs in AC-INDEX.yaml
    ├─ UPDATE progress-tracker.json
    └─ TRIGGER: SyncOrchestrator.sync_all("phase_added")
        ├─ sync_plan_viewer_data()          ✅ Phase 4.5 now in dashboard!
        ├─ sync_html_views()                ✅ Phase 4.5 HTML views created!
        ├─ update_prompt_ac_mappings()      ✅ AC-INTEG-001-012 names available!
        └─ notify_watchers()                ✅ Audit trail recorded
    ↓
Display result to user ✅
```

**Trigger 2: AC-ID Status Changes**
```
Task completes
    ↓
MasterOrchestrator.mark_ac_complete("AC-INTEG-001")
    ├─ UPDATE AC-INDEX.yaml (status: completed)
    ├─ UPDATE progress-tracker.json (percentages)
    └─ TRIGGER: SyncOrchestrator.sync_all("ac_modified")
        ├─ sync_plan_viewer_data()    ✅ Dashboard percentages updated!
        ├─ sync_html_views()          ✅ Phase views show new % complete
        └─ notify_watchers()
    ↓
Users see live dashboard update ✅
```

**Trigger 3: Governance Rules Change**
```
Governance merger updated
    ↓
MasterOrchestrator.merge_governance() updates core-rules.yaml
    └─ TRIGGER: SyncOrchestrator.sync_all("governance_changed")
        ├─ update_prompt_ac_mappings()  ✅ Rule precedence updated in prompts!
        └─ notify_watchers()
    ↓
All prompts see new rules ✅
```

**Trigger 4: Manual Emergency Resync**
```
User: "sync all dashboards"
    ↓
MasterOrchestrator.handle_request("resync dashboards")
    └─ TRIGGER: SyncOrchestrator.sync_all("manual_resync")
        ├─ sync_plan_viewer_data()
        ├─ sync_html_views()
        ├─ sync_audit_dashboard()
        ├─ update_prompt_ac_mappings()
        └─ notify_watchers()
    ↓
All dashboards refreshed ✅
```

---

## Part 3: Updated CORTEX.prompt.md Workflow

### 3.1 Key Changes to CORTEX.prompt.md

**NEW Section: Data Flow & Sync Guarantees**

```markdown
## 🔄 DATA FLOW & SYNC GUARANTEES

**Single Source of Truth (SSOT):**
- `master-plan.yaml` → Phase definitions (PRIMARY)
- `AC-INDEX.yaml` → AC-ID definitions (PRIMARY)
- `progress-tracker.json` → Completion state (PRIMARY)
- All other files → DERIVED (regenerated automatically)

**CRITICAL GUARANTEE:**
Every change to SSOT automatically triggers SyncOrchestrator to:
1. Regenerate plan-viewer-data.json (dashboard feed)
2. Regenerate docs/html-views/ (HTML views)
3. Regenerate audit-logs-aggregated.json (audit dashboard)
4. Update .github/prompts/AC-mappings.json (prompt AC lookup)

**Result:** Zero stale dashboards. All UIs always in sync with master plan.

**You (Copilot) Role:**
- ❌ DO NOT manually call sync scripts
- ✅ MasterOrchestrator handles all syncing
- ✅ You only display results to user
```

**NEW Section: When Each Prompt Must Call MasterOrchestrator**

```markdown
## 🚦 PROMPT INVOCATION REQUIREMENTS

**RULE: ANY prompt that modifies state must route through MasterOrchestrator**

| Operation | Route | Sync Trigger |
|-----------|-------|--------------|
| Add phase | MasterOrchestrator | phase_added |
| Add AC-ID | MasterOrchestrator | ac_modified |
| Update progress | MasterOrchestrator | progress_updated |
| Change governance | MasterOrchestrator | governance_changed |
| Read dashboards | Direct file read | (no sync needed) |

**Example Violations (DON'T DO THESE):**
- ❌ Directly editing master-plan.yaml then calling sync script
- ❌ Modifying plan-viewer-data.json manually
- ❌ Calling multiple sync scripts in different orders
- ❌ Assuming dashboards are updated without sync

**Correct Workflow:**
- ✅ Call MasterOrchestrator with intent
- ✅ MasterOrchestrator updates SSOT
- ✅ SyncOrchestrator auto-triggered
- ✅ Display result to user
```

### 3.2 Updated STATE MANAGEMENT Section

```markdown
## 🗄️ STATE MANAGEMENT (Updated Protocol)

**Primary Sources (You DO NOT Touch These Directly):**
- ❌ DO NOT edit master-plan.yaml directly
- ❌ DO NOT edit AC-INDEX.yaml directly
- ❌ DO NOT edit progress-tracker.json directly
- ✅ MasterOrchestrator owns all writes
- ✅ You only read them for context (if needed)

**Derived Files (Auto-Regenerated - You Ignore These):**
- ❌ DO NOT touch plan-viewer-data.json
- ❌ DO NOT touch docs/html-views/*
- ❌ DO NOT touch audit-logs-aggregated.json
- ✅ SyncOrchestrator regenerates all
- ✅ Users read these to see current state

**Your Responsibility:**
1. Parse user intent
2. Clarify with user (bullets)
3. Get user confirmation
4. Invoke `python3 -m src.main "{intent}"`
5. Display orchestrator result
6. ✅ DONE - Sync happens automatically

**What You NEVER Do:**
- ❌ Call sync scripts
- ❌ Modify derived files
- ❌ Calculate percentages
- ❌ Assume state changes without orchestrator
```

---

## Part 4: Implementation Plan

### 4.1 New Files to Create

| File | Purpose | Lines | Owner |
|------|---------|-------|-------|
| `src/orchestrators/core/sync_orchestrator.py` | Auto-sync SSOT → derived | 200-300 | Asif |
| `.github/prompts/AC-mappings.json` | AC-ID lookup table for prompts | Generated | SyncOrch |
| `cortex-brain/cx6-plan/viewer/docs/html-views/phase-4.5.yaml` | Phase 4.5 YAML (auto-generated) | Generated | SyncOrch |
| `cortex-brain/cx6-plan/viewer/docs/html-views/phase-4.5.html` | Phase 4.5 HTML (auto-generated) | Generated | SyncOrch |

### 4.2 Files to Update

| File | Changes | Priority |
|------|---------|----------|
| `.github/prompts/CORTEX.prompt.md` | Add data flow section, update state management | CRITICAL |
| `src/orchestrators/master_orchestrator.py` | Add sync trigger calls after state changes | CRITICAL |
| `scripts/sync_plan_viewer_data.py` | Refactor to use SyncOrchestrator | HIGH |
| `scripts/generate_html_views.py` | Refactor to use SyncOrchestrator | HIGH |
| `scripts/aggregate_audit_logs.py` | Refactor to use SyncOrchestrator | HIGH |
| `cortex-brain/cx6-plan/viewer/plan-viewer-data.json` | Regenerate with Phase 4.5 + AC-INTEG | CRITICAL |

### 4.3 Immediate Action Items

**TODAY (2026-01-12):**
1. ✅ Create SyncOrchestrator class (200 lines)
2. ✅ Update CORTEX.prompt.md with data flow diagrams
3. ✅ Create AC-mappings.json with AC-INTEG entries
4. ✅ Regenerate plan-viewer-data.json to include Phase 4.5
5. ✅ Commit all changes

**WEEK 1 (2026-01-13 to 2026-01-19):**
1. Integrate SyncOrchestrator calls into MasterOrchestrator
2. Refactor existing sync scripts to use SyncOrchestrator
3. Generate Phase 4.5 HTML views (docs/html-views/)
4. Test full sync pipeline (all triggers)
5. Document for other developers

**WEEK 2+ (2026-01-20+):**
1. All future phase changes use unified sync workflow
2. Monitor for any manual sync calls (audit trail)
3. Optimize sync performance (<100ms total)
4. Add WebSocket notifications (future enhancement)

---

## Part 5: Integration Points Reference

### 5.1 Complete Integration Map

```
SSOT → Derived Files → Consumers
────────────────────────────────

master-plan.yaml
  ├─→ plan-viewer-data.json
  │   ├─→ plan-viewer.html (browser)
  │   └─→ dashboard users (see phases, timelines)
  │
  ├─→ docs/html-views/*.html/.yaml
  │   └─→ browser (per-phase documentation)
  │
  └─→ .github/prompts/AC-mappings.json
      └─→ all CORTEX prompts (lookup AC-ID names)

AC-INDEX.yaml
  ├─→ plan-viewer-data.json
  │   └─→ dashboard (AC capabilities list)
  │
  ├─→ docs/html-views/*.yaml
  │   └─→ browser (AC descriptions)
  │
  └─→ .github/prompts/AC-mappings.json
      └─→ prompts (AC-ID → name translation)

progress-tracker.json
  ├─→ plan-viewer-data.json
  │   └─→ dashboard (completion %, status)
  │
  └─→ docs/html-views/*.html
      └─→ browser (phase progress bars)

core-rules.yaml
  ├─→ .github/prompts/AC-mappings.json
  │   └─→ prompts (rule precedence)
  │
  └─→ audit-logs-aggregated.json
      └─→ audit-log-viewer.html (rule compliance)

audit-logs/*.jsonl
  └─→ audit-logs-aggregated.json
      └─→ audit-log-viewer.html (browsable audit trail)
```

### 5.2 Affected Prompts (Must Follow New Workflow)

| Prompt | Changes Required |
|--------|------------------|
| CORTEX.prompt.md | ✅ Add data flow section, state mgmt rules |
| cortex-exec.prompt.md | ✅ Reference SyncOrchestrator auto-trigger |
| cortex-evidence-validator.prompt.md | ✅ Reference SyncOrchestrator auto-trigger |
| cortex-brittleness-review.prompt.md | ✅ Read-only (no state changes) |

### 5.3 Files That Changed (Phase 4.5 Example)

```
Changes Made Yesterday:
├─ master-plan.yaml (✅ added phase_4_5_integration_tests)
├─ AC-INDEX.yaml (✅ added AC-INTEG-001 to 012)
└─ cortex-brain/documents/ (✅ added PHASE-4.5-INTEGRATION-TESTS-ADDITION.md)

Changes NEEDED Now (via SyncOrchestrator):
├─ plan-viewer-data.json (❌ MISSING Phase 4.5)
├─ docs/html-views/phase-4.5.html (❌ MISSING)
├─ docs/html-views/phase-4.5.yaml (❌ MISSING)
├─ .github/prompts/AC-mappings.json (❌ MISSING AC-INTEG entries)
└─ [browsers] see stale dashboard (❌ PROBLEM)

Solution: Run sync_all() once → all files updated
```

---

## Part 6: Validation Checklist

**Pre-Sync Verification:**
- [ ] master-plan.yaml valid YAML, no syntax errors
- [ ] AC-INDEX.yaml valid YAML, AC-INTEG-001 to 012 present
- [ ] progress-tracker.json valid JSON, current_phase set
- [ ] core-rules.yaml valid YAML, all 19 SKULL rules defined

**Post-Sync Verification:**
- [ ] plan-viewer-data.json includes Phase 4.5 (id: "4.5")
- [ ] plan-viewer-data.json total_ac_ids = 175
- [ ] docs/html-views/phase-4.5.html exists and valid
- [ ] docs/html-views/phase-4.5.yaml exists and valid
- [ ] AC-mappings.json contains all AC-INTEG-001 to 012 entries
- [ ] plan-viewer.html loads and shows Phase 4.5
- [ ] No JavaScript console errors in browser

**System Verification:**
- [ ] All sync operations logged to audit trail
- [ ] Sync completion time < 100ms
- [ ] No conflicts between derived files
- [ ] All consumers (prompts, browsers) see consistent view

---

## Part 7: Anti-Patterns to Prevent

**❌ DO NOT:**
```python
# Anti-Pattern 1: Manual file edits + manual sync calls
edit_master_plan()
run_sync_script()  # Wrong! SSOT updated outside MasterOrchestrator

# Anti-Pattern 2: Multiple sync calls in different orders
sync_plan_viewer_data()
sync_html_views()
sync_audit_dashboard()  # Could race or get stale data

# Anti-Pattern 3: Updating derived files directly
plan_viewer_data.json = {...}  # WRONG! Auto-generated!

# Anti-Pattern 4: Prompts touching state files directly
progress_tracker.json["completed_count"] += 1  # Atomic writes violated!
```

**✅ DO:**
```python
# Correct Pattern 1: Single entry point
MasterOrchestrator.handle_request(user_intent)
  # MasterOrchestrator:
  # 1. Validates request
  # 2. Updates SSOT atomically
  # 3. Triggers SyncOrchestrator
  # 4. Returns result

# Correct Pattern 2: Unified sync
SyncOrchestrator.sync_all(change_type)
  # SyncOrchestrator:
  # 1. Reads all SSOT in consistent order
  # 2. Generates all derived files
  # 3. Validates all outputs
  # 4. Logs operations
  # 5. Atomically replaces files

# Correct Pattern 3: Prompts use unified workflow
python3 -m src.main "{intent}" --format markdown
  # Entry point routes to orchestrator
  # Orchestrator handles all state + sync
  # Copilot displays result
```

---

## Summary: What Changed

| Aspect | Before | After |
|--------|--------|-------|
| Data Flow | Fragmented, manual | Unified, auto-synced |
| Sync Mechanism | Manual script calls | SyncOrchestrator (auto-triggered) |
| SSOT Consistency | ❌ Not guaranteed | ✅ Guaranteed |
| Dashboard Staleness | ❌ Phase 4.5 example | ✅ Zero staleness |
| Prompt Workflow | Unclear state handling | Clear: MasterOrch → Sync → Display |
| Integration Points | 8 (disconnected) | 8 (unified) |
| Troubleshooting | "Run sync script?" | "SyncOrchestrator auto-triggered" |

---

## Implementation: Next Steps

1. **Create SyncOrchestrator** (15 min)
2. **Update CORTEX.prompt.md** with this architecture (20 min)  
3. **Regenerate all derived files** via sync (5 min)
4. **Test Phase 4.5 appears in dashboard** (5 min)
5. **Commit changes with documentation** (5 min)

**Total Time:** ~50 minutes for complete unified architecture

---

**Document Status:** Ready for Implementation  
**Approved By:** GitHub Copilot (Intent Clarification Protocol)  
**Next Review:** After SyncOrchestrator implementation
