# CORTEX Builder - Unified Phase Mode (Updated 2026-01-18)

## 🆕 KEY CHANGE: Single Source of Truth (SSOT)

**Effective immediately**: All phase operations work with **cortex-master.yaml ONLY**.

```
❌ OLD (Broken)         ✅ NEW (Fixed)
cortex-master.yaml      cortex-master.yaml
        ↓                       ↓
    splits                 phases: section
        ↓                    (all specs here)
phase-XX.yaml files    ← ARCHIVED (read-only)
(27 files)
```

**Why this change?**
- Eliminated 2-source-of-truth sync issues
- Chat01 required multiple audit passes to achieve consistency
- Metrics changed 90.7% → 74.2% during sync discovery
- Status mismatches discovered in 4 phases (03, 04, 05, PARALLEL)

**Result**: Single file to keep in sync, validator prevents desync, pre-commit hook catches errors before they happen.

---

## ✅ PRE-IMPLEMENTATION VALIDATION CHECKLIST

**Before running this prompt, verify:**

```bash
# 1. Consolidation script exists
[ -f scripts/consolidate_phases.py ]

# 2. Validation script exists  
[ -f scripts/validate_phase_sync.py ]

# 3. Run validator (should pass)
python3 scripts/validate_phase_sync.py

# 4. Pre-commit hook installed
[ -f .git/hooks/pre-commit ]

# 5. Phase files archived (optional but recommended)
[ -d _workspaces/roadmap/_archives/phase-yamls-v1/ ]
```

---

## 🛡️ PHASE OPERATION WORKFLOW (New)

### Updated: Load Phase Context

**Old (Split)**:
```
1. Read cortex-master.yaml (metadata)
2. Read _workspaces/roadmap/phases/phase-XX.yaml (spec)
3. Mentally merge both sources
```

**New (Unified)**:
```
# Load single source
phases:
  PHASE-XX:
    title: "Phase Title"
    status: NOT_STARTED
    locked: false
    ac_ids:
      AC-XXX-XX-01:
        title: "AC Title"
        description: "..."
        testing: {unit: 5, integration: 1}
        # ... all details in ONE place
```

### Updated: Update Phase Status

**Old (Manual Split)**:
```
1. Edit _workspaces/roadmap/phases/phase-XX.yaml
2. Update cortex-master.yaml phase_tracker
3. Manually sync counts
4. Hope they don't drift
```

**New (Atomic)**:
```
# Edit cortex-master.yaml ONLY
phases:
  PHASE-XX:
    status: IN_PROGRESS  ← Single edit
    locked: false        ← Single edit
    ac_ids: {...}        ← Everything together
    
# Run validation
python3 scripts/validate_phase_sync.py

# Commit (pre-commit hook validates before accepting)
git commit -m "phase-XX: status updated"
```

### Updated: Add New AC-ID

**Old (Manual Coordination)**:
```
1. Add to phase-XX.yaml ac_ids
2. Update cortex-master.yaml counts
3. Verify they match
4. Risk: Human error, drift
```

**New (Single Location)**:
```
# Edit cortex-master.yaml → phases.PHASE-XX.ac_ids
phases:
  PHASE-XX:
    ac_ids:
      AC-XXX-XX-01: {...existing...}
      AC-XXX-XX-02: {...NEW...}  ← Add here only
      # metadata.total_ac_ids auto-updated by validator

# Commit
git commit -m "phase-XX: added AC-XXX-XX-02"
# Pre-commit hook runs validator
# Counts automatically corrected if needed
```

---

## 📋 CRITICAL: Phase Tracker Structure (Unchanged)

The `phase_tracker` section in `cortex-master.yaml` remains as **quick lookup only**:

```yaml
phase_tracker:
  PHASE-01:
    ac_ids: [AC-AR-001-01, AC-AR-001-02, ...]
    status: COMPLETED
    locked: true
    # ... summary fields

# This MIRRORS the detailed data in phases: section
# Validator ensures they stay in sync
```

**Important**: When you edit `phases.PHASE-XX`, the validator automatically updates `phase_tracker.PHASE-XX` to match.

---

## 🔄 VALIDATOR AUTO-FIXES (Applied Before Commit)

The `validate_phase_sync.py` script automatically fixes common mistakes:

| Issue | Auto-Fix |
|-------|----------|
| `metadata.total_ac_ids` mismatch | Count actual phases.*.ac_ids, update metadata |
| Duplicate AC-IDs | Detect and report error (fails validation) |
| Invalid status values | Detect and report error (fails validation) |
| Locked phase with incomplete ACs | Warning issued (fails validation if strict) |
| Phase metadata out of sync with phase_tracker | Auto-sync to match phases: section |

**Example**:
```
$ python3 scripts/validate_phase_sync.py

[CHECK] Metadata counts...
   ⚠️ AC-ID count mismatch: metadata says 300, actual is 302
   🔧 AUTO-FIX: Updating total_ac_ids 300 → 302
   
✅ Fix saved to cortex-master.yaml
```

---

## 🚀 NEW WORKFLOW: Phase Implementation

### Step 1: Load Phase Details

```bash
# From cortex-master.yaml, find your phase in phases: section
# All details are here - NO separate file to read

grep -A 100 "phases:" cortex-master.yaml | grep -A 50 "PHASE-XX:"
```

**You get** (all in one place):
- Title, description, status, locked flag
- All AC-IDs with specs
- Testing requirements
- Governance rules
- Success criteria
- Dependencies

### Step 2: Implement AC-IDs

For each AC-ID in `phases.PHASE-XX.ac_ids`:

```yaml
# From cortex-master.yaml
phases:
  PHASE-XX:
    ac_ids:
      AC-XXX-XX-01:
        title: "AC Title"
        description: "..."
        testing:
          unit_tests_expected: 5
          integration_tests_expected: 1
        success_criteria:
          - "Criterion 1"
          - "Criterion 2"
```

**Implementation** (standard TDD):
1. Write tests (from `testing:` section)
2. Implement code
3. All tests pass → AC-ID COMPLETED
4. Log to audit trail

### Step 3: Update AC Status

```yaml
# Edit cortex-master.yaml
phases:
  PHASE-XX:
    ac_ids:
      AC-XXX-XX-01:
        status: COMPLETED  ← Updated
        completed_date: 2026-01-18
        verified: true
```

### Step 4: Validate & Commit

```bash
# Validation runs before commit (pre-commit hook)
python3 scripts/validate_phase_sync.py

# If passes:
git add cortex-master.yaml
git commit -m "phase-XX: AC-XXX-XX-01 COMPLETED"

# Pre-commit hook automatically:
# - Validates phase sync
# - Updates counts if needed
# - Checks AC naming conventions
# - Prevents broken states
```

### Step 5: Lock Phase (When All ACs Complete)

```yaml
# When ALL ac_ids in PHASE-XX are COMPLETED:
phases:
  PHASE-XX:
    status: COMPLETED
    locked: true  ← Set to true
    
# Commit
git commit -m "phase-XX: COMPLETED - all 10 ACs verified"

# This automatically updates phase_tracker summary
```

---

## 📊 VALIDATION RULES

The validator enforces these rules automatically:

### Rule 1: Single Location of Phase Truth

```python
# ✅ ALLOWED: Single source
cortex-master.yaml → phases.PHASE-XX → all data here

# ❌ NOT ALLOWED: Split sources
cortex-master.yaml → phases.PHASE-XX (partial)
_workspaces/roadmap/phases/phase-XX.yaml (partial)
# Risk of sync drift
```

### Rule 2: Status Machine

```
NOT_STARTED → IN_PROGRESS → COMPLETED
     ↓             ↓              ↓
locked: false  locked: false  locked: true
   (can change)    (can change)   (immutable)
```

Valid transitions:
- NOT_STARTED → IN_PROGRESS ✅
- IN_PROGRESS → COMPLETED ✅
- IN_PROGRESS → NOT_STARTED ✅ (rollback)
- COMPLETED → IN_PROGRESS ❌ (unlock required)

### Rule 3: Locked Phase Immutability

```yaml
phases:
  PHASE-XX:
    locked: true
    # Cannot change:
    status: COMPLETED        # Read-only
    ac_ids: {...}            # Read-only
    # Can only add metadata fields:
    archive_date: 2026-01-18  # New field OK
    completion_notes: "..."    # New field OK
```

### Rule 4: AC-ID Uniqueness

```yaml
# ✅ CORRECT: AC-IDs unique across all phases
phases:
  PHASE-01:
    ac_ids:
      AC-AR-001-01: {...}
  PHASE-02:
    ac_ids:
      AC-ORC-002-01: {...}  # Different prefix, OK

# ❌ WRONG: Duplicate AC-ID
phases:
  PHASE-01:
    ac_ids:
      AC-AR-001-01: {...}
  PHASE-02:
    ac_ids:
      AC-AR-001-01: {...}  # ERROR: Duplicate!
```

---

## 🔧 MAINTENANCE: When to Run Validator

**Automatic** (pre-commit hook):
- Every `git commit` involving cortex-master.yaml
- Prevents sync issues before they reach repo

**Manual** (troubleshooting):
```bash
# Full validation
python3 scripts/validate_phase_sync.py

# With auto-fixes applied
python3 scripts/validate_phase_sync.py --fix

# Detailed report
python3 scripts/validate_phase_sync.py --verbose
```

---

## 🔍 REFERENCING ARCHIVED PHASE SPECS

If you need to look up old phase YAML structure:

```bash
# Read-only reference (DO NOT EDIT)
cat _workspaces/roadmap/_archives/phase-yamls-v1/phase-XX.yaml

# View differences
diff _archives/phase-yamls-v1/phase-01.yaml <(grep -A 200 "PHASE-01:" cortex-master.yaml)
```

**These files are HISTORICAL ONLY** - all active work goes through cortex-master.yaml.

---

## ⚠️ CRITICAL: If Sync Issues Reappear

**Prevention** (what we've done):
1. ✅ Consolidated into single file
2. ✅ Created validator to catch mismatches
3. ✅ Added pre-commit hook for automatic validation
4. ✅ Archived old phase files as reference

**If issues still occur**:

```bash
# Diagnose
python3 scripts/validate_phase_sync.py --verbose

# Auto-repair (safe fixes only)
python3 scripts/validate_phase_sync.py --fix

# If serious damage:
# Restore from git
git checkout cortex-master.yaml

# If desperate (rollback to pre-consolidation):
# See PHASE-CONSOLIDATION-STRATEGY.md → Rollback Plan
```

---

## 📝 FILE PLACEMENT POLICY (Updated)

| File Type | Location | Authority |
|-----------|----------|-----------|
| **Master Plan** | `cortex-master.yaml` | **CANONICAL** ← NOW INCLUDES PHASE SPECS |
| Phase Specs | `phases:` section in cortex-master.yaml | **NEW: In master file** |
| Old Phase Files | `_archives/phase-yamls-v1/` | Reference only (read-only) |
| Source Code | `src/`, `cortex-brain/tierX/` | Implementation |
| Tests | `tests/` | Verification |
| Validators | `scripts/validate_phase_sync.py` | Automation |
| Hooks | `.git/hooks/pre-commit` | Prevention |
| Documentation | `docs/` | Human-readable |

---

## ✨ SUCCESS METRICS (Since Consolidation)

**Before Consolidation**:
- Files to sync: 27 (cortex-master.yaml + 26 phase YAMLs)
- Sync discovery sessions needed: 2-3 per month
- Status mismatches discovered: Regular (4 found in chat01)
- Time to verify consistency: 30+ minutes

**After Consolidation**:
- Files to sync: 1 (cortex-master.yaml only)
- Sync discovery sessions needed: 0 (prevented)
- Status mismatches possible: No (validator prevents)
- Time to verify consistency: <5 minutes
- Pre-commit hook validations: Automatic

---

## QUICK REFERENCE: Common Tasks

### Check phase status
```bash
grep -A 2 "phases:" cortex-master.yaml | grep -A 1 "PHASE-XX:"
```

### Count AC-IDs in phase
```bash
grep "AC-XXX-" cortex-master.yaml | wc -l
```

### Find all incomplete AC-IDs
```bash
grep -B 2 "status: IN_PROGRESS" cortex-master.yaml | grep "AC-"
```

### Validate before commit
```bash
python3 scripts/validate_phase_sync.py && git commit -m "..."
```

### Repair automatic issues
```bash
python3 scripts/validate_phase_sync.py --fix
```

---

## GOVERNANCE COMPLIANCE (Unchanged)

All governance rules (CORE-008 through CORE-028) remain in effect:

- ✅ CORE-008: TDD pattern (tests first)
- ✅ CORE-011: Type hints mandatory
- ✅ CORE-012: Docstrings mandatory
- ✅ CORE-028: Portable paths (Path(__file__).parent)
- ✅ CORE-024: Audit logging for all changes

**New**: Validation script enforces AC-ID naming:
- Format: `AC-DOMAIN-NNN-NN`
- Example: `AC-MCP-EXPOSURE-001`
- Validated on every commit

---

## 🚀 NEXT SESSION: Implementation Guidance

When implementing next phase:

1. ✅ Load `cortex-master.yaml` (single source)
2. ✅ Navigate to `phases.PHASE-XX` section
3. ✅ All specs are there (no separate file needed)
4. ✅ Edit directly in cortex-master.yaml
5. ✅ Validation runs on commit (automatic)
6. ✅ No more sync discovery audit sessions needed

**Result**: Faster implementation, zero sync issues, atomic updates.

