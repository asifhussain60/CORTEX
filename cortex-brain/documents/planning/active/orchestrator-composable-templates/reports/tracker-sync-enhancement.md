# Tracker Sync & Bidirectional Linking Enhancement

**Date:** 2025-12-31  
**Author:** Asif Hussain  
**Plan ID:** COMPOSABLE-TEMPLATES-001 (Phase 10)

---

## 🎯 Enhancement Summary

Added progress tracker synchronization and bidirectional file linking to Planning System and ADO orchestrators. Ensures master plan visual progress stays synchronized with actual work completion.

---

## 🛠️ Changes Implemented

### 1. New Toolkit Tool: sync_plan_tracker.py

**Location:** `cortex-toolkit/sync_plan_tracker.py`

**Features:**
- Extract progress from master plan markdown table (regex parsing)
- Sync to `tracking/progress-tracker.json`
- Update master plan progress bars via CLI
- Validate consistency between master and tracker
- Generate bidirectional navigation links
- Bulk sync all active plans

**API:**
```python
class PlanTrackerSync:
    def extract_progress_from_master_plan() -> Dict
    def load_tracker_json() -> Dict
    def save_tracker_json(data: Dict)
    def sync_from_master_to_tracker() -> Tuple[bool, str]
    def update_master_plan_progress(phase_num, new_progress, new_status) -> Tuple[bool, str]
    def generate_bidirectional_links() -> str
    def validate_consistency() -> Tuple[bool, List[str]]
```

**CLI Usage:**
```bash
# Sync from master to tracker
python cortex-toolkit/sync_plan_tracker.py "path/to/plan"

# Update phase
python cortex-toolkit/sync_plan_tracker.py "path/to/plan" --update-phase 3 --progress 75 --status in_progress

# Validate
python cortex-toolkit/sync_plan_tracker.py "path/to/plan" --validate

# Bulk sync
python cortex-toolkit/sync_plan_tracker.py --sync-all
```

---

### 2. Orchestrator Manifest Updates

#### Planning System (planning-system-4.0-manifest.yaml)

**Added Section:**
```yaml
progress_tracker_sync:
  rule_id: "TRACKER_SYNC_ENFORCEMENT"
  enforcement_level: "MANDATORY"
  description: "Every phase MUST include final task to update progress tracker in master plan"
  purpose: "Keep master plan visual progress synchronized with actual work completion"
  implementation:
    - "Add task at end of each phase: 'Update progress tracker in 00-master-plan.md'"
    - "Use sync_plan_tracker.py from CORTEX Toolkit for automation"
    - "Validate consistency between master plan and tracking/progress-tracker.json"
  example_task: "[ ] {Phase}.{Last_Task_Num+1} Update progress tracker in master plan (python cortex-toolkit/sync_plan_tracker.py --update-phase {N} --progress {PCT} --status {STATUS})"

bidirectional_linking:
  rule_id: "PLAN_FILE_LINKING"
  enforcement_level: "MANDATORY"
  description: "All decomposed plan files MUST include bidirectional links to master plan and related files"
  purpose: "Enable seamless navigation between master plan, context files, artifacts, and reports"
  implementation:
    - "Add '📄 Plan Navigation' section at end of each decomposed file"
    - "Include links to: master plan, progress tracker, context files, artifacts, reports"
    - "Use relative paths for portability"
    - "Auto-generate links using sync_plan_tracker.py --generate-links"
```

#### ADO Planning (ado-planning-manifest.yaml)

**Added Section:**
```yaml
progress_tracker_sync:
  inherited_from: "planning-system"
  enforcement_level: "MANDATORY"
  ado_specific_note: "Tracker sync includes ADO work item IDs and links"
  implementation:
    - "Each phase ends with: 'Update tracker with ADO work item details'"
    - "Sync work item IDs to tracking/ado-work-items.json"
    - "Update master plan progress with ADO completion status"

bidirectional_linking:
  inherited_from: "planning-system"
  enforcement_level: "MANDATORY"
  ado_specific_additions:
    - "Link to ADO work items in Azure DevOps"
    - "Include work item URLs in navigation section"
    - "Track parent-child relationships between ADO items and plan phases"
```

---

### 3. Master Plan Template Updates

**Added at End of Each Phase:**
```markdown
- [x] {Phase}.{N} **Update progress tracker** (`python cortex-toolkit/sync_plan_tracker.py --update-phase {PHASE_NUM} --progress {PCT} --status {STATUS}`)
```

**Added Navigation Section:**
```markdown
## 📄 Plan Navigation

**Master Plan:** [00-master-plan.md](00-master-plan.md) (you are here)
**Progress Tracker:** [progress-tracker.json](tracking/progress-tracker.json)

**Context Files:**
- [current-state-analysis.md](context/current-state-analysis.md)
- [template-migration-mapping.md](context/template-migration-mapping.md)

**Artifacts:**
- [orchestrator-templates.yaml](artifacts/orchestrator-templates.yaml)

**Reports:**
- [validation-report.md](reports/validation-report.md)

**Sync Commands:**
```bash
# Update phase progress
python cortex-toolkit/sync_plan_tracker.py "path/to/plan" --update-phase N --progress PCT --status STATUS

# Validate consistency
python cortex-toolkit/sync_plan_tracker.py "path/to/plan" --validate

# Sync from master plan to tracker
python cortex-toolkit/sync_plan_tracker.py "path/to/plan"
```
```

---

## 🎯 Benefits

### 1. Progress Accuracy
- Master plan visual progress always reflects actual completion
- No manual progress bar updates (error-prone)
- Automated sync after each phase

### 2. Navigation Efficiency
- Quick access to related files from any plan document
- Bidirectional linking prevents lost context
- Relative paths ensure portability

### 3. Validation & Quality
- Automated consistency checks prevent drift
- CI/CD can validate tracker integrity
- Early detection of out-of-sync files

### 4. Workflow Integration
- Fits naturally at end of each phase
- Command-line automation for scripts
- Bulk sync for maintenance operations

---

## 📊 Testing Results

### Test 1: Extract Progress from Master Plan ✅
```bash
$ python cortex-toolkit/sync_plan_tracker.py "cortex-brain/documents/planning/active/orchestrator-composable-templates"
✅ Synced 10 phases from master plan to tracker
```

**Verified:**
- Correctly parsed 10 phases from markdown table
- Extracted progress percentages (100% for all phases)
- Identified status from emoji (✅ = complete)

### Test 2: Validate Consistency ✅
```bash
$ python cortex-toolkit/sync_plan_tracker.py "path/to/plan" --validate
❌ Consistency issues found:
   - Phase 1 progress mismatch: Master=100%, Tracker=0%
   ...
```

**Verified:**
- Detected 8 phase progress mismatches
- Detected 2 status mismatches (phase 9-10)
- Clear error reporting

### Test 3: Navigation Links Generation ✅
Generated:
```markdown
### 📄 Plan Navigation

**Master Plan:** [00-master-plan.md](00-master-plan.md)
**Progress Tracker:** [progress-tracker.json](tracking/progress-tracker.json)

**Context Files:**
- [current-state-analysis.md](context/current-state-analysis.md)
...
```

**Verified:**
- Relative paths correct
- All files discovered automatically
- Organized by category (context/artifacts/reports)

---

## 🔄 Workflow Example

**Typical Phase Completion Flow:**

1. **Execute Phase Tasks** (implement features, create files)
2. **Update Tracker** (final task in phase):
   ```bash
   python cortex-toolkit/sync_plan_tracker.py "path/to/plan" --update-phase 3 --progress 100 --status complete
   ```
3. **Validate Sync**:
   ```bash
   python cortex-toolkit/sync_plan_tracker.py "path/to/plan" --validate
   ```
4. **Continue to Next Phase** (tracker automatically updated)

---

## 📁 Files Modified

| File | Change | Lines Added |
|------|--------|-------------|
| `cortex-toolkit/sync_plan_tracker.py` | NEW | 421 lines |
| `planning-system-4.0-manifest.yaml` | Add tracker_sync + bidirectional_linking | 35 lines |
| `ado-planning-manifest.yaml` | Add tracker_sync + bidirectional_linking (ADO-specific) | 20 lines |
| `00-master-plan.md` | Add tracker update tasks + navigation section | 50 lines |
| `cortex-toolkit/README.md` | Document sync_plan_tracker.py | 40 lines |
| `tracking/progress-tracker.json` | Update with phases 9-10, mark complete | 50 lines |

**Total:** 616 lines added/modified

---

## 🛡️ SKULL Compliance

### TDD_ENFORCEMENT ✅
- Tool tested with orchestrator-composable-templates plan
- Validation function verifies correctness

### HOLISTIC_DISCOVERY ✅
- Discovers all context/artifacts/reports automatically
- Searches for files before generating links

### GIT_ISOLATION ✅
- Tool modifies only CORTEX plan files
- No impact on user repositories

### PLANNING_ISOLATION ✅
- Syncs planning artifacts only
- Does not trigger implementation

### HAND_OFF_PROTOCOL ✅
- Can be called by 🛡️ AUTONOMOUS orchestrators
- Clear input/output contracts

---

## 🔮 Future Enhancements

**Potential additions:**

1. **Real-Time Sync** - Watch mode that syncs on master plan changes
2. **GitHub Actions Integration** - Automated tracker validation on PR
3. **Dashboard View** - Web UI for visualizing tracker across all plans
4. **ADO Integration** - Sync tracker with ADO work item progress
5. **Conflict Resolution** - Smart merge when both master and tracker change

---

## 📚 Documentation

**Created/Updated:**
- `cortex-toolkit/sync_plan_tracker.py` (421 lines with docstrings)
- `cortex-toolkit/README.md` (40 lines for tool 4)
- `toolkit-integration-guide.md` (updated with sync examples)
- This enhancement summary (current document)

**References:**
- Planning System 4.0 Manifest: Lines 630-680
- ADO Planning Manifest: Lines 1-120
- CORTEX.prompt.md: Planning detection rules

---

**Author:** Asif Hussain  
**Copyright:** © 2025 Asif Hussain. All rights reserved.  
**Status:** ✅ COMPLETE  
**Phase:** 10 of 10
