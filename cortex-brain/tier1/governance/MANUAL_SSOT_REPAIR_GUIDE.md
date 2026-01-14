# 🔨 SSOT Manual Repair Guide – Step-by-Step Fix Instructions

**Purpose:** Complete the remaining 50% of SSOT integrity repair  
**Estimated Time:** 1-2 hours  
**Status:** READY FOR EXECUTION  
**Blocker:** Prevents Phase 2 execution

---

## 📋 Repair Checklist

- [ ] **Step 1** – Analyze master-plan.yaml structure (10 mins)
- [ ] **Step 2** – Fix AC-INDEX schema violations (20 mins)
- [ ] **Step 3** – Rebuild master-plan.yaml phases (30 mins)
- [ ] **Step 4** – Re-run auto-repair (5 mins)
- [ ] **Step 5** – Validate all green (5 mins)
- [ ] **Step 6** – Commit changes (5 mins)

**Total Time:** ~75 minutes

---

## 🔍 Step 1: Analyze master-plan.yaml Structure

### Current State Check

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Check what's currently in master-plan
head -50 cortex-brain/cx6-plan/master-plan.yaml

# Check backup (pre-repair state)
head -50 cortex-brain/backups/ssot-integrity/master-plan.yaml.backup.20260113_182508
```

### Expected Structure

**master-plan.yaml SHOULD look like:**

```yaml
version: "6.0"
metadata:
  name: "CORTEX 6.0 Implementation Plan"
  phases_total: 11
  
phases:
  phase_1:
    name: "Foundation"
    description: "Core infrastructure and governance"
    ac_ids:
      - AC-AUDIT-001
      - AC-AUDIT-002
      - ... (more ACs)
    total_ac_count: 30
    target_completion: "2026-02-01"
    
  phase_2:
    name: "Orchestration Core"
    description: "MasterOrchestrator and TDD infrastructure"
    ac_ids:
      - AC-ORCH-001
      - AC-TDD-001
      - ... (more ACs)
    total_ac_count: 54
    target_completion: "2026-03-01"
    
  # ... phase_3 through phase_11
```

### Check Current Corruption

```bash
# Validate syntax first
python3 -c "
import yaml
try:
    data = yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml'))
    print('✅ YAML syntax valid')
    if data and 'phases' in data:
        print(f'phases type: {type(data[\"phases\"])}')
        if data['phases'] is None:
            print('❌ phases is NULL')
        elif isinstance(data['phases'], list):
            print(f'❌ phases is a LIST with {len(data[\"phases\"])} items (should be DICT)')
        elif isinstance(data['phases'], dict):
            print(f'✅ phases is a DICT with {len(data[\"phases\"])} phases')
    else:
        print('❌ No \"phases\" key found')
except Exception as e:
    print(f'❌ YAML syntax error: {e}')
"
```

---

## 🔧 Step 2: Fix AC-INDEX Schema Violations

### Issue: 5 Corrupted Entries

**Problem:** These top-level keys in AC-INDEX.yaml have non-dictionary values:
- `acceptance_criteria`
- `description`
- `last_updated`
- `schema_version`
- `updated_by`

### Analyze AC-INDEX Current State

```bash
# View first 100 lines to understand structure
head -100 cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml

# Check for problem entries
grep -n "^acceptance_criteria:" cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml
grep -n "^description:" cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml
grep -n "^last_updated:" cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml
grep -n "^schema_version:" cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml
grep -n "^updated_by:" cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml
```

### Expected AC-INDEX Structure

**SHOULD look like:**

```yaml
version: "1.0"
ac_registry:
  AC-AUDIT-001:
    title: "Queryable Audit Storage"
    description: "SQL audit log with query interface"
    phase: "phase_1"
    status: "implemented"
    acceptance_criteria:
      - "Audit log stored in SQLite"
      - "Query interface works"
    test_evidence_id: "test-run-20260113-001"
    last_updated: "2026-01-13"
    updated_by: "cortex-system"
  
  AC-AUDIT-002:
    # ... more entries
```

### Fix Strategy

**If the 5 corrupted entries are ORPHANED (not inside ac_registry):**

```yaml
# ❌ WRONG (these are orphaned top-level keys)
version: "1.0"
ac_registry: {...}
acceptance_criteria: [...]  # ❌ This is the problem
description: "..."           # ❌ This is the problem
last_updated: "..."          # ❌ This is the problem
schema_version: "..."        # ❌ This is the problem
updated_by: "..."            # ❌ This is the problem

# ✅ CORRECT (move inside ac_registry or remove if metadata)
version: "1.0"
metadata:
  description: "AC Index"
  schema_version: "1.0"
  last_updated: "2026-01-13"
  updated_by: "cortex-system"
ac_registry:
  AC-AUDIT-001: {...}
  # ... all ACs
```

### Repair Steps

**Option A: Remove orphaned entries (if not needed)**
```bash
# Edit AC-INDEX.yaml and delete the 5 orphaned lines
# These should NOT be at the root level
```

**Option B: Move to metadata section (if metadata is needed)**
```yaml
metadata:
  schema_version: "1.0"
  last_updated: "2026-01-13"
  updated_by: "cortex-system"
  description: "CORTEX 6.0 AC Registry"
  acceptance_criteria: []  # Move any orphaned array here

ac_registry:
  # All ACs here
```

### Validate Fix

```bash
# Syntax check
python3 -c "import yaml; yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml')); print('✅ YAML valid')"

# Check structure
python3 -c "
import yaml
data = yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))
print(f'Keys: {list(data.keys())}')
if 'ac_registry' in data:
    print(f'AC count: {len(data[\"ac_registry\"])}')
"
```

---

## 📐 Step 3: Rebuild master-plan.yaml Phases

### Source of Truth: AC-INDEX.yaml

**All ACs in AC-INDEX already have a `phase` field!**

```bash
# Extract phase distribution from AC-INDEX
python3 << 'EOF'
import yaml

data = yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))

# Count ACs per phase
phase_map = {}
for ac_id, ac_data in data.get('ac_registry', {}).items():
    phase = ac_data.get('phase', 'unknown')
    if phase not in phase_map:
        phase_map[phase] = []
    phase_map[phase].append(ac_id)

# Report
print("ACs per phase:")
for phase in sorted(phase_map.keys()):
    ac_list = phase_map[phase]
    print(f"  {phase}: {len(ac_list)} ACs")
    print(f"    {', '.join(ac_list[:5])}{' ...' if len(ac_list) > 5 else ''}")
EOF
```

### Rebuild Process

**Generate complete master-plan.yaml from AC-INDEX:**

```bash
python3 << 'EOF'
import yaml
import json

# Load AC-INDEX (authority)
ac_index = yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))

# Build phase structure from AC-INDEX
phase_map = {}
for ac_id, ac_data in ac_index.get('ac_registry', {}).items():
    phase = ac_data.get('phase', 'phase_unknown')
    if phase not in phase_map:
        phase_map[phase] = {
            'name': phase.replace('_', ' ').title(),
            'ac_ids': [],
            'description': f'Phase: {phase}'
        }
    phase_map[phase]['ac_ids'].append(ac_id)

# Create master-plan structure
master_plan = {
    'version': '6.0',
    'metadata': {
        'name': 'CORTEX 6.0 Implementation Plan',
        'description': 'Sequential phase-based execution (11 phases, 115 ACs)',
        'created': '2026-01-13',
        'last_updated': '2026-01-13'
    },
    'phases': {}
}

# Sort phases naturally (phase_1, phase_2, ..., phase_11)
for phase_key in sorted(phase_map.keys(), key=lambda x: (
    int(x.split('_')[1]) if '_' in x and x.split('_')[1].isdigit() else 999
)):
    phase_data = phase_map[phase_key]
    master_plan['phases'][phase_key] = {
        'name': phase_data['name'],
        'description': phase_data['description'],
        'ac_ids': phase_data['ac_ids'],
        'total_ac_count': len(phase_data['ac_ids']),
        'completed_ac_count': 0,  # Will be updated by validator
        'target_completion': '2026-02-01'  # Update per phase
    }

# Write rebuilt master-plan
with open('cortex-brain/cx6-plan/master-plan.yaml', 'w') as f:
    yaml.dump(master_plan, f, default_flow_style=False, sort_keys=False)

print("✅ master-plan.yaml rebuilt successfully")
print(f"Phases: {len(master_plan['phases'])}")
print(f"Total ACs: {sum(len(p['ac_ids']) for p in master_plan['phases'].values())}")

# Show summary
for phase_key, phase_data in master_plan['phases'].items():
    print(f"  {phase_key}: {len(phase_data['ac_ids'])} ACs")
EOF
```

### Verify Rebuild

```bash
# Check syntax
python3 -c "import yaml; yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml')); print('✅ Valid YAML')"

# Check structure
python3 -c "
import yaml
data = yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml'))
print(f'Phases: {len(data[\"phases\"])}')
total_acs = sum(len(p.get('ac_ids', [])) for p in data['phases'].values())
print(f'Total ACs: {total_acs}')
"
```

---

## ⚙️ Step 4: Re-run Auto-Repair

### Run Repair Command

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 src/tools/ssot_integrity_validator.py repair
```

### Expected Output (Post-Fixes)

```
✅ All SSOT files loaded successfully
  AC-INDEX has 115 entries
  master-plan has 11 phases
  progress-tracker has 7 phases

🔧 Running auto-repairs...

✅ Fixed: Phases with NULL AC counts: 7
✅ Fixed: Hardcoded 100% but incomplete ACs: 2
✅ Fixed: 115 ACs in AC-INDEX now mapped to master-plan.yaml

🔍 Re-validating...
✅ No issues found

✅ REPAIR COMPLETE: 10 issues fixed
```

---

## ✓ Step 5: Validate All Green

### Full Validation

```bash
python3 src/tools/ssot_integrity_validator.py validate
```

### Expected Output

```
✅ All SSOT files loaded successfully
  AC-INDEX has 115 entries
  master-plan has 11 phases
  progress-tracker has 7 phases

📋 VALIDATION ISSUES REPORT

CRITICAL (0 issues):
HIGH (0 issues):
MEDIUM (0 issues):
LOW (0 issues):

✅ NO ISSUES FOUND
```

### Deep Validation

```bash
# Count ACs per phase
python3 << 'EOF'
import yaml
import json

master_plan = yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml'))
tracker = json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))

print("Master Plan AC Counts:")
total_planned = 0
for phase_key, phase_data in master_plan['phases'].items():
    ac_count = len(phase_data.get('ac_ids', []))
    total_planned += ac_count
    tracker_phase = tracker.get('phases', {}).get(phase_key, {})
    tracker_count = tracker_phase.get('total_ac_count', 0)
    match = "✅" if ac_count == tracker_count else "❌"
    print(f"  {phase_key}: {ac_count} (tracker: {tracker_count}) {match}")

print(f"\nTotal: {total_planned} ACs planned")
print(f"Tracker shows: {sum(p.get('total_ac_count', 0) for p in tracker.get('phases', {}).values())} ACs")
EOF
```

---

## 🔐 Step 6: Commit Changes

### Git Status Check

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
git status
```

### Stage Changes

```bash
git add cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml
git add cortex-brain/cx6-plan/master-plan.yaml
git add cortex-brain/tier1/tracking/progress-tracker.json
```

### Pre-commit Hook Verification

```bash
# The pre-commit hook should run automatically
# If it blocks, fix the issues it reports
```

### Commit

```bash
git commit -m "fix(SSOT): Repair master-plan and AC-INDEX corruption

- Rebuild master-plan.yaml phases from AC-INDEX authority
- Fix AC-INDEX schema violations (moved orphaned keys)
- Reconcile progress-tracker AC counts from master-plan
- All 115 ACs now properly mapped to phases
- Validation: 0 issues remaining

Evidence:
- Repair timestamp: 2026-01-13T18:25:08
- Backups: cortex-brain/backups/ssot-integrity/
- Report: cortex-brain/backups/REPAIR_REPORT_20260113.md

Closes: Phase 2 blocker"
```

### Push

```bash
git push origin main
# Or your feature branch
```

---

## 🎯 After All Steps Complete

### Final Validation

```bash
# Should show ALL GREEN
python3 src/tools/ssot_integrity_validator.py validate

# Should show 0% → 100% for each phase
python3 -c "
import json
tracker = json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))
for phase_key, phase in sorted(tracker.get('phases', {}).items()):
    total = phase.get('total_ac_count', 0)
    completed = phase.get('completed_ac_count', 0)
    pct = (completed/total*100) if total > 0 else 0
    print(f'{phase_key}: {completed}/{total} ({pct:.0f}%)')
"
```

### Proceed to Phase 2

```bash
# SSOT is now healthy, can proceed with Phase 2 execution
python3 -m src.main "execute phase 2"
```

---

## ⚠️ Troubleshooting

### Issue: "YAML syntax error" after edits

**Solution:**
```bash
# Check for common YAML errors
python3 -c "import yaml; yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))"

# Look for:
# - Inconsistent indentation (use 2 spaces)
# - Unclosed quotes
# - Missing colons
```

### Issue: "115 ACs still orphaned" after rebuild

**Cause:** Some ACs don't have `phase` field in AC-INDEX  
**Solution:**
```bash
# Find ACs without phase field
python3 << 'EOF'
import yaml
data = yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))
for ac_id, ac_data in data.get('ac_registry', {}).items():
    if 'phase' not in ac_data:
        print(f"{ac_id}: missing phase field")
EOF

# Add missing phase field to AC-INDEX manually
```

### Issue: Repair still says "error fixing orphaned_ac"

**Cause:** master-plan.yaml structure still invalid  
**Solution:**
```bash
# Verify it's a dict, not a list
python3 -c "
import yaml
data = yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml'))
print(f'Type of phases: {type(data[\"phases\"])}')
if not isinstance(data['phases'], dict):
    print('❌ phases must be DICT, not', type(data['phases']).__name__)
"

# Use rebuild script above to fix
```

---

## 🎓 Learning: Why This Happened

1. **master-plan.yaml emptied:** Likely during earlier phases, phases dict became NULL
2. **AC-INDEX corrupted:** Orphaned keys at root level instead of inside ac_registry
3. **No atomic writes:** Changes weren't validated before persisting
4. **No pre-commit guards:** Invalid states committed to git

**Prevention:** Now active with 2 git hooks + 4 CORE rules ✅

---

## ✨ Success Criteria

After completing all 6 steps, you should have:

✅ **master-plan.yaml**
- 11 phases defined
- 115 ACs mapped (distributed across phases)
- Valid YAML syntax
- All AC IDs reference existing entries in AC-INDEX

✅ **AC-INDEX.yaml**
- All 115 ACs in ac_registry
- No orphaned top-level keys
- Each AC has `phase` field
- Valid YAML syntax

✅ **progress-tracker.json**
- All 7 phases have calculated AC counts (not NULL)
- All phases have calculated percentages (not hardcoded)
- Matches master-plan AC counts
- Valid JSON syntax

✅ **Validator Output**
```
✅ NO ISSUES FOUND
```

✅ **Phase 2 Unblocked**
```
python3 -m src.main "execute phase 2"
# Should proceed without SSOT errors
```

---

## 🚀 Estimated Timeline

| Step | Time | Complexity |
|------|------|------------|
| Analyze structure | 10 min | Easy |
| Fix AC-INDEX schema | 20 min | Easy |
| Rebuild master-plan | 30 min | Medium |
| Re-run repair | 5 min | Easy |
| Validate | 5 min | Easy |
| Commit | 5 min | Easy |
| **TOTAL** | **~75 min** | **Medium** |

**Can start immediately and complete within 2 hours** ✓

---

**Ready to proceed? Execute steps 1-6 in order, run validation, then unblock Phase 2!** 🚀
