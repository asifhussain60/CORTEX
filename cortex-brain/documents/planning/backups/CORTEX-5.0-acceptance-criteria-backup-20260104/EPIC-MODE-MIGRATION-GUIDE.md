# 🎭 EPIC Mode Migration Guide for plan_orchestrator.py

**Version:** 5.0.1  
**Created:** January 4, 2026  
**Author:** Asif Hussain

---

## 📋 Overview

The `plan_orchestrator.py` script now supports **EPIC Mode** - a manifest-driven approach to managing hierarchical multi-plan execution. This migration guide explains how the EPIC mode works and how to use it.

---

## 🔀 What Changed?

### Before (v5.0.0)
- Child plan metadata stored in `tracking/epic-progress-tracker.json`
- Dependencies defined inline in JSON tracker
- No formal validation rules or gate enforcement
- Manual updates required for new child plans

### After (v5.0.1 - EPIC Mode)
- **Manifest file:** `cortex-5.0-epic-manifest.yaml` (source of truth)
- **Automatic detection:** Script detects manifest and enters EPIC mode
- **Gate enforcement:** Progress-based gates block dependent plans
- **Validation rules:** Formal dependency checking with rationale
- **Critical path tracking:** 11-week strategic timeline
- **Backward compatible:** Falls back to JSON-only if manifest missing

---

## 🎯 EPIC Mode Detection

The orchestrator automatically detects EPIC mode by checking for the manifest file:

```bash
CORTEX-5.0/
├── cortex-5.0-epic-manifest.yaml  # ← Triggers EPIC mode
├── tracking/
│   ├── epic-progress-tracker.json
│   ├── child-plan-registry.json
│   └── dependency-graph.json
└── plan_orchestrator.py
```

When you run the script, you'll see:

```
🎭 EPIC Mode Detected
   Manifest: cortex-5.0-epic-manifest.yaml
   ✅ Loaded 18 child plans
   ✅ Validation rules: 2 gates
   ✅ Critical path: 11 weeks
```

---

## 📄 Manifest Structure

### High-Level Organization

```yaml
epic_metadata:
  epic_id: cortex-v5-gap-remediation
  planner_mode: epic  # ← Triggers EPIC detection
  total_child_plans: 18
  
child_plans:
  - id: epic-structure-cleanup
    order: "00A"
    name: "Epic Structure Cleanup"
    dependencies: []  # No dependencies
    
  - id: epic-feature-planner
    order: "00B"
    name: "Epic & Feature Planner"
    dependencies:
      - "00A"  # Depends on 00A completing
    dependency_rules:
      - condition: "Sub-Plan 00A must be 100% complete"
        rationale: "Clean structure required before planner"
    
  - id: test-coverage-sprint
    order: "00C"
    dependencies:
      - "00B"
    dependency_rules:
      - condition: "Sub-Plan 00B must be 100% complete"
        gate: "GATE-1"  # ← Gate enforcement

validation_rules:
  dependency_enforcement:
    enabled: true
    strict_mode: true
  
  gate_enforcement:
    enabled: true
    gates:
      - gate_id: "GATE-1"
        name: "50% Test Coverage"
        condition: "Sub-Plan 00C progress ≥50%"
        blocks: ["01", "02", "05"]

critical_path:
  total_weeks: 11
  path:
    - "00A"
    - "00B"
    - "00C"
    - "01"
    - "08"
    - "12"
    - "09"
```

---

## 🚀 Using EPIC Mode

### 1. Running the Orchestrator

**Check Status:**
```bash
python plan_orchestrator.py status
```

**Output:**
```
🎭 EPIC Mode Detected
   Manifest: cortex-5.0-epic-manifest.yaml
   ✅ Loaded 18 child plans
   ✅ Validation rules: 2 gates
   ✅ Critical path: 11 weeks

📋 Sub-Plans:
00A  Epic Structure Cleanup           ✅ complete     100%         2h
00B  Epic & Feature Planner           🔄 in_progress   15%       2-3w
00C  Test Coverage Sprint             ⏸️ blocked      0.0%       2-3w
```

**Start a Sub-Plan:**
```bash
python plan_orchestrator.py start 00C
```

The orchestrator will:
1. Check manifest for dependencies (00B must be complete)
2. Check gate conditions (if any)
3. Block execution if dependencies not met
4. Start if all conditions satisfied

**Update Progress:**
```bash
python plan_orchestrator.py update 00C 50
```

This triggers:
- Progress update in tracker JSON
- Gate condition evaluation (GATE-1: 50% coverage)
- Automatic unblocking of dependent plans (01, 02, 05)

---

## 🔧 Dependency Management

### Simple Dependencies

```yaml
- id: refinement-orchestrator
  order: "01"
  dependencies:
    - "00C"  # Must complete 00C first
```

**Behavior:** Plan 01 is blocked until Sub-Plan 00C status = "complete"

### Gate-Based Dependencies

```yaml
- id: refinement-orchestrator
  order: "01"
  dependencies:
    - "00C"
  dependency_rules:
    - condition: "Test coverage ≥50%"
      gate: "GATE-1"
      rationale: "Quality baseline required"
```

**Behavior:** Plan 01 blocked until:
1. Sub-Plan 00C complete **AND**
2. Gate condition met (progress ≥50%)

### Multi-Dependency Plans

```yaml
- id: orchestrator-migrations
  order: "08"
  dependencies:
    - "01"  # Refinement orchestrator
    - "02"  # Debug orchestrator
    - "05"  # Context middleware
```

**Behavior:** Plan 08 blocked until **all three** dependencies complete

---

## 📊 Gate Enforcement

### How Gates Work

Gates are **progress-based blocking conditions** that prevent plans from starting until quality thresholds are met.

**Example: Test Coverage Gate**

```yaml
gate_enforcement:
  gates:
    - gate_id: "GATE-1"
      name: "50% Test Coverage"
      condition: "Sub-Plan 00C progress ≥50%"
      blocks: ["01", "02", "05"]
```

**Timeline:**

```
Progress: 00C at 0%  → Plans 01, 02, 05 = BLOCKED
Progress: 00C at 49% → Plans 01, 02, 05 = BLOCKED
Progress: 00C at 50% → Plans 01, 02, 05 = UNBLOCKED ✅
```

### Checking Gate Status

The orchestrator automatically checks gates when:
- Starting a sub-plan
- Updating progress
- Showing status

You'll see gate status in dependency checking:

```
⏸️ Sub-Plan 01 is blocked by dependencies:
   - Sub-Plan 00C: Test Coverage Sprint (in_progress)
   - GATE-1: 50% Test Coverage (NOT MET - current: 35%)
```

---

## ✏️ Adding New Child Plans

### Step 1: Edit the Manifest

Open `cortex-5.0-epic-manifest.yaml` and add a new child plan:

```yaml
child_plans:
  # ... existing plans ...
  
  - id: my-new-feature
    order: "19"
    name: "My New Feature"
    type: feature
    priority: medium
    blocking: false
    
    folder: "19-my-new-feature/"
    master_plan: "19-my-new-feature/00-my-new-feature.md"
    tracking_file: "19-my-new-feature/tracking/progress-tracker.json"
    
    estimated_hours: 40
    duration_estimate: "1w"
    complexity: moderate
    
    dependencies:
      - "12"  # Depends on production validation
    
    dependency_rules:
      - condition: "Production validation pipeline passed"
        rationale: "New feature requires stable production"
    
    description: "Implements my new feature with comprehensive testing."
    
    exit_criteria:
      - "Feature implemented with ≥95% test coverage"
      - "Integration tests passing"
      - "Documentation complete"
```

### Step 2: Create Folder Structure

```bash
mkdir -p 19-my-new-feature/{context,artifacts,reports,tracking}
touch 19-my-new-feature/00-my-new-feature.md
```

### Step 3: Update Epic Metadata

```yaml
epic_metadata:
  total_child_plans: 19  # ← Increment count
```

### Step 4: Test Detection

```bash
python plan_orchestrator.py status
```

You should see:

```
✅ Loaded 19 child plans  # ← New plan detected
```

---

## 🔄 Backward Compatibility

### JSON-Only Mode (Fallback)

If the manifest file is missing or invalid, the orchestrator automatically falls back to **JSON-only mode**:

```
⚠️  EPIC manifest validation failed
   Falling back to JSON-only mode
```

In this mode:
- Dependencies read from `epic-progress-tracker.json`
- No gate enforcement
- Manual dependency management
- Original v5.0.0 behavior

### Migration Path

**Option 1: Use EPIC Mode (Recommended)**
1. Keep `cortex-5.0-epic-manifest.yaml` in place
2. Script automatically detects and uses it
3. All validation rules enforced

**Option 2: Remove EPIC Mode**
1. Delete or rename `cortex-5.0-epic-manifest.yaml`
2. Script reverts to JSON-only mode
3. Manual dependency management

---

## 🧪 Validation Rules

### Manifest Validation on Load

The orchestrator validates the manifest when loading:

```python
✅ Required keys present: epic_metadata, child_plans, validation_rules
✅ Child plans format: list with 18 entries
✅ Required plan fields: id, order, name, folder, dependencies
✅ Dependency references: all dependencies valid (00A-18)
```

### Dependency Validation on Execution

When starting a sub-plan:

```python
✅ Simple dependency check: Sub-Plan 00B = complete
✅ Gate condition check: GATE-1 condition met (50% progress)
✅ Multi-dependency check: All 3 dependencies complete
```

### Exit Criteria Tracking

The manifest defines exit criteria for each plan:

```yaml
exit_criteria:
  - "All 18 child plan folders properly named"
  - "No duplicate or orphaned files"
  - "Tracking infrastructure validated"
```

These appear in:
- Pre-execution analysis reports
- Completion checklists
- DoD validation

---

## 📈 Critical Path Tracking

The manifest defines the **critical path** - the longest dependency chain determining minimum completion time:

```yaml
critical_path:
  total_weeks: 11
  path:
    - "00A"  # Epic Structure Cleanup (2h)
    - "00B"  # Epic & Feature Planner (2-3w)
    - "00C"  # Test Coverage Sprint (2-3w)
    - "01"   # Refinement Orchestrator (1w)
    - "08"   # Orchestrator Migrations (1-2w)
    - "12"   # Production Validation (1w)
    - "09"   # Final Validation (3-4d)
```

**Why It Matters:**
- **Parallel execution:** Non-critical plans can run simultaneously
- **Timeline estimates:** 11 weeks = minimum completion time
- **Priority guidance:** Critical path plans get highest priority

---

## 🎯 Best Practices

### 1. Always Define Dependencies

```yaml
# ❌ Bad - No dependencies defined
dependencies: []

# ✅ Good - Clear dependency chain
dependencies:
  - "00B"
dependency_rules:
  - condition: "Planning v5 functional"
    rationale: "Requires stable planning system"
```

### 2. Use Gates for Quality Thresholds

```yaml
# ✅ Good - Enforces quality baseline
dependency_rules:
  - condition: "Test coverage ≥50%"
    gate: "GATE-1"
    rationale: "Quality baseline before new features"
```

### 3. Document Rationale

```yaml
# ✅ Good - Clear reasoning
dependency_rules:
  - condition: "Sub-Plan 00A must be 100% complete"
    rationale: "Clean structure required before planner implementation"
```

### 4. Update Total Count

```yaml
epic_metadata:
  total_child_plans: 18  # ← Keep in sync with child_plans list
```

### 5. Validate Before Committing

```bash
python plan_orchestrator.py status

# Look for validation success:
# ✅ Loaded 18 child plans
# ✅ Validation rules: 2 gates
```

---

## 🐛 Troubleshooting

### Issue: "Cannot detect planner mode"

**Cause:** Manifest file missing or misnamed

**Solution:**
```bash
ls cortex-5.0-epic-manifest.yaml  # Check file exists
```

### Issue: "EPIC manifest validation failed"

**Cause:** Missing required fields in YAML

**Solution:** Check for:
- `epic_metadata` key
- `child_plans` key (must be a list)
- `validation_rules` key
- Required fields in each child plan: `id`, `order`, `name`, `folder`, `dependencies`

### Issue: "Invalid dependency 'XYZ' in plan ABC"

**Cause:** Dependency references non-existent sub-plan

**Solution:**
```yaml
# Check that dependency order exists
dependencies:
  - "00B"  # ✅ Valid (00B exists)
  - "99Z"  # ❌ Invalid (99Z doesn't exist)
```

### Issue: Gate condition never met

**Cause:** Progress not reaching threshold or condition syntax error

**Solution:** Check gate definition:
```yaml
condition: "Sub-Plan 00C progress ≥50%"
# Must match format: "Sub-Plan {ORDER} progress ≥{PERCENT}%"
```

---

## 📚 Reference

### Manifest File Location
```
/CORTEX-5.0/cortex-5.0-epic-manifest.yaml
```

### Orchestrator Script
```
/CORTEX-5.0/plan_orchestrator.py
```

### Tracking Files
```
/CORTEX-5.0/tracking/
├── epic-progress-tracker.json      # Progress state
├── child-plan-registry.json        # Child metadata (synced with manifest)
└── dependency-graph.json           # Dependency visualization
```

### Key Methods (Internal)

| Method | Purpose |
|--------|---------|
| `_load_epic_manifest()` | Load and validate YAML manifest |
| `_validate_epic_manifest()` | Check manifest structure |
| `_get_manifest_plan(order)` | Get child plan from manifest by order |
| `_check_gate_condition(gate_id)` | Evaluate gate condition |
| `_dependencies_met(sub_plan)` | Check if dependencies satisfied (uses manifest in EPIC mode) |

---

## 🎉 Conclusion

EPIC Mode transforms `plan_orchestrator.py` from a simple JSON tracker into a sophisticated manifest-driven execution engine with:

- ✅ Automatic mode detection
- ✅ Formal dependency validation
- ✅ Progress-based gate enforcement
- ✅ Critical path tracking
- ✅ Backward compatibility

**Next Steps:**
1. Run `python plan_orchestrator.py status` to verify EPIC mode
2. Review the manifest: `cortex-5.0-epic-manifest.yaml`
3. Start executing sub-plans with confidence in dependency management

---

**Questions?** Review the manifest YAML for examples of all child plan configurations.

**Copyright © 2026 Asif Hussain. All rights reserved.**
