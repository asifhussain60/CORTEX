# CORTEX 6.0 - Single Source of Truth (SSOT) Architecture

**Version:** 1.6.0  
**Updated:** 2026-01-13  
**Status:** PRODUCTION  
**Author:** Asif Hussain  

---

## 🎯 EXECUTIVE SUMMARY

CORTEX 6.0 uses a **unified SSOT architecture** where data flows from authoritative sources through a single sync mechanism to derived files. This eliminates data drift, stale state, and dashboard confusion.

**Key Changes in v1.6.0:**
- ✅ Clarified SSOT hierarchy (4 primary sources)
- ✅ Archived 4 redundant `phase-X-tracking.json` files
- ✅ Archived 3 redundant sync scripts (kept 1 canonical script)
- ✅ Updated all prompts to reference unified architecture
- ✅ `plan-viewer.html` now guaranteed to show current state

---

## 📊 SSOT HIERARCHY (4 PRIMARY SOURCES)

### 1. **master-plan.yaml** - Architecture SSOT

**Location:** `cortex-brain/cx6-plan/master-plan.yaml`

**Contains:**
- Phase definitions (1, 1.5, 2, 3, 4, 4.5, 5, 10)
- AC-ID ranges per phase component
- Timelines and duration estimates
- Dependencies and exit criteria
- Snowball strategy and philosophy

**Updated By:** Humans (architects)  
**Updated When:** Phase design changes, architecture refinements  
**Reader:** MasterOrchestrator, regenerate_plan_viewer_data.py  
**Writer:** Humans only (manual YAML edits)

**Purpose:** Defines WHAT the plan is (architecture), not WHERE we are in execution.

---

### 2. **progress-tracker.json** - Execution SSOT

**Location:** `cortex-brain/tier1/tracking/progress-tracker.json`

**Contains:**
- Current phase number and status
- Implemented AC-IDs (with timestamps)
- Planned AC-IDs not yet implemented
- Execution history and audit trail
- Phase gate status

**Updated By:** MasterOrchestrator ONLY  
**Updated When:** After every AC-ID implementation, test pass, phase completion  
**Reader:** All orchestrators, regenerate_plan_viewer_data.py  
**Writer:** MasterOrchestrator (atomic SQLite writes)

**Purpose:** Tracks WHERE we are in execution (current state).

---

### 3. **AC-INDEX.yaml** - Definition SSOT

**Location:** `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`

**Contains:**
- AC-ID names and descriptions
- Acceptance criteria per AC-ID
- Test requirements
- Evidence bundle structure

**Updated By:** Humans (architects)  
**Updated When:** New AC-IDs defined, criteria refined  
**Reader:** All orchestrators, regenerate_plan_viewer_data.py  
**Writer:** Humans only (manual YAML edits)

**Purpose:** Defines WHAT each AC-ID means (specifications).

---

### 4. **core-rules.yaml** - Governance SSOT

**Location:** `cortex-brain/tier0/governance/core-rules.yaml`

**Contains:**
- 19 SKULL rules (immutable)
- Governance enforcement policies
- TDD requirements (CORE-008, CORE-019)
- File organization rules (CORE-002, CORE-009)

**Updated By:** Humans (governance team)  
**Updated When:** Rare governance policy changes  
**Reader:** GovernanceMerger, all orchestrators  
**Writer:** Humans only (manual YAML edits)

**Purpose:** Enforces HOW work is done (governance).

---

## 🔄 DATA FLOW (SIMPLIFIED)

```
┌─────────────────────────────────────────────────────────┐
│         PRIMARY SOURCES (SSOT - 4 FILES)                │
├─────────────────────────────────────────────────────────┤
│ 1. master-plan.yaml       (architecture)                │
│ 2. progress-tracker.json  (execution state)             │
│ 3. AC-INDEX.yaml          (AC-ID definitions)           │
│ 4. core-rules.yaml        (governance rules)            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓ (reads)
┌─────────────────────────────────────────────────────────┐
│    SYNC SCRIPT (SINGLE CANONICAL SCRIPT)                │
├─────────────────────────────────────────────────────────┤
│ scripts/regenerate_plan_viewer_data.py                  │
│                                                          │
│ Reads:                                                   │
│ • master-plan.yaml (phase structure)                    │
│ • progress-tracker.json (completion status)             │
│ • AC-INDEX.yaml (AC-ID names)                           │
│                                                          │
│ Writes:                                                  │
│ • plan-viewer-data.json (atomic write)                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓ (writes)
┌─────────────────────────────────────────────────────────┐
│        DERIVED FILES (AUTO-GENERATED)                   │
├─────────────────────────────────────────────────────────┤
│ • plan-viewer-data.json    (dashboard feed)             │
│ • plan-viewer-metrics.json (metrics feed)               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓ (fetch)
┌─────────────────────────────────────────────────────────┐
│          BROWSERS / DASHBOARDS                          │
├─────────────────────────────────────────────────────────┤
│ • plan-viewer.html (main dashboard)                     │
│ • audit-log-viewer.html (audit dashboard)               │
│ • core-rules-viewer.html (governance dashboard)         │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ CLEANUP COMPLETED (v1.6.0)

### **Archived Files:**

#### 1. Duplicate Phase Tracking (DELETED)
```
cortex-brain/cx6-plan/phases/phase-1/phase-1-tracking.json  ❌
cortex-brain/cx6-plan/phases/phase-2/phase-2-tracking.json  ❌
cortex-brain/cx6-plan/phases/phase-3/phase-3-tracking.json  ❌
cortex-brain/cx6-plan/phases/phase-4/phase-4-tracking.json  ❌
```
**Reason:** Duplicated `progress-tracker.json`, became stale, caused confusion.  
**Archive Location:** `cortex-brain/cx6-plan/archive/phase-tracking-deprecated-20260113/`

#### 2. Redundant Sync Scripts (ARCHIVED)
```
scripts/sync_plan_viewer_data.py           ❌
scripts/sync_plan_viewer_holistic.py       ❌
scripts/view_sync_regenerator.py           ❌
```
**Reason:** Multiple sync scripts competed, caused inconsistent outputs.  
**Archive Location:** `scripts/archive/sync-scripts-deprecated-20260113/`

### **Canonical Script (KEPT):**
```
scripts/regenerate_plan_viewer_data.py     ✅
```
**Reason:** Most comprehensive, reads all 3 SSOT sources, atomic writes.

---

## 🛡️ ENFORCEMENT MECHANISMS

### **1. MasterOrchestrator Integration**

```python
# src/orchestrators/core/master_orchestrator.py

def _update_state(self, ac_id: str, status: str):
    """Update progress-tracker.json (SSOT)"""
    # Atomic write to progress-tracker.json
    self.state_manager.update(ac_id, status)
    
    # Auto-trigger dashboard sync
    self._sync_dashboard()

def _sync_dashboard(self):
    """Regenerate plan-viewer-data.json from SSOT"""
    subprocess.run([
        'python3', 
        'scripts/regenerate_plan_viewer_data.py'
    ], check=True)
```

### **2. Prompt Enforcement**

All `.prompt.md` files updated to reference SSOT architecture:
- ✅ `CORTEX.prompt.md` (main gateway)
- ✅ `cortex-plan-viewer-sync.prompt.md` (dashboard sync)
- ✅ `cortex-evidence-validator.prompt.md` (validation)
- ✅ `cortex-git-commit.prompt.md` (commit messages)

### **3. .gitignore Rules**

```gitignore
# Derived files (regenerated from SSOT)
cortex-brain/cx6-plan/viewer/plan-viewer-data.json
cortex-brain/cx6-plan/viewer/plan-viewer-metrics.json
```

**Rationale:** Derived files should be generated, not committed.

---

## 📋 VALIDATION CHECKLIST

**After SSOT refactoring, verify:**

- [x] Only 4 SSOT files exist (master-plan.yaml, progress-tracker.json, AC-INDEX.yaml, core-rules.yaml)
- [x] Only 1 sync script exists (regenerate_plan_viewer_data.py)
- [x] No `phase-X-tracking.json` files in phases/ directory
- [x] All prompts reference unified SSOT architecture
- [x] `plan-viewer.html` fetches `plan-viewer-data.json` (single source)
- [x] MasterOrchestrator auto-syncs dashboard after state changes
- [x] Archive directory contains deprecated files (audit trail)

---

## 🎯 BENEFITS OF SSOT ARCHITECTURE

| Benefit | Before (v1.5.0) | After (v1.6.0) |
|---------|-----------------|----------------|
| **Data consistency** | 3 conflicting sources | 1 unified SSOT |
| **Dashboard accuracy** | Showed stale data (Phase 1: 0%) | Always current state |
| **Sync scripts** | 4 competing scripts | 1 canonical script |
| **Prompt clarity** | Ambiguous data sources | Clear SSOT hierarchy |
| **Maintenance** | Manual sync required | Auto-sync on state change |
| **Audit trail** | Lost in duplicates | Single truth preserved |

---

## 🔍 TROUBLESHOOTING

### **Problem: Dashboard shows wrong completion percentage**

**Diagnosis:**
```bash
# Check SSOT
cat cortex-brain/tier1/tracking/progress-tracker.json | jq '.current_phase'

# Check derived file
cat cortex-brain/cx6-plan/viewer/plan-viewer-data.json | jq '.phases[] | select(.id == 1)'
```

**Fix:**
```bash
# Regenerate from SSOT
python3 scripts/regenerate_plan_viewer_data.py

# Verify
open cortex-brain/cx6-plan/viewer/plan-viewer.html
```

### **Problem: Old phase-tracking files exist**

**Diagnosis:**
```bash
find cortex-brain/cx6-plan/phases -name "*-tracking.json"
```

**Fix:**
```bash
# Archive them
mv cortex-brain/cx6-plan/phases/phase-*/phase-*-tracking.json \
   cortex-brain/cx6-plan/archive/phase-tracking-deprecated-20260113/
```

### **Problem: Multiple sync scripts found**

**Diagnosis:**
```bash
ls -la scripts/*sync*.py
```

**Fix:**
```bash
# Keep only regenerate_plan_viewer_data.py
mv scripts/sync_plan_viewer_*.py scripts/archive/sync-scripts-deprecated-20260113/
```

---

## 📚 REFERENCES

| Document | Purpose |
|----------|---------|
| `master-plan.yaml → ssot_declaration` | Complete SSOT spec |
| `.github/prompts/CORTEX.prompt.md` | Prompt SSOT integration |
| `scripts/regenerate_plan_viewer_data.py` | Canonical sync script |
| `cortex-brain/tier1/tracking/progress-tracker.json` | Execution state |

---

## 🚀 NEXT STEPS

**For new phases/AC-IDs:**
1. Update `master-plan.yaml` (architecture)
2. Update `AC-INDEX.yaml` (definitions)
3. Implement via MasterOrchestrator (auto-updates progress-tracker.json)
4. Dashboard auto-syncs (no manual intervention)

**For dashboard issues:**
1. Check SSOT sources (progress-tracker.json)
2. Run: `python3 scripts/regenerate_plan_viewer_data.py`
3. Refresh browser

**For prompt updates:**
1. Always reference SSOT hierarchy
2. Never read/modify SSOT files directly in prompts
3. Delegate to MasterOrchestrator via: `python3 -m src.main "{intent}"`

---

**END OF SSOT ARCHITECTURE SPECIFICATION**

_CORTEX 6.0.0 | Production-Grade AI Orchestration_  
_Copyright © 2025-2026 Asif Hussain. All rights reserved._
