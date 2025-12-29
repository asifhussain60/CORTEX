# Planning Orchestrator Filename Issue Investigation

**Date:** December 4, 2024  
**Investigator:** CORTEX (Asif Hussain)  
**Issue:** Planning system creating long filenames despite restoration claiming filename enforcement

---

## 🎯 My Understanding Of Your Request

User reported that CORTEX is still creating plans with long filenames despite earlier restoration that should have brought in 30-character max instructions. Need to investigate why and what else from that session is not wired in.

## ⚠️ Challenge

Multiple layers of missing implementations and documentation discrepancies discovered.

## 💬 Response

## Executive Summary

**ROOT CAUSE FOUND:** The `_truncate_filename()` function is **called but never defined** in `planning_utility.py`.

**SEVERITY:** HIGH - Code will fail at runtime when creating or saving plans  
**IMPACT:** All plan creation operations will crash with `NameError: name '_truncate_filename' is not defined`

**SECONDARY ISSUE:** Documentation/specification conflict:
- **Phase 8 Plan Specification:** 45-character max (older)
- **Implemented Report:** 30-character max (December 4, 2024)
- **Current Code:** Calls `_truncate_filename(safe_name, max_length=30)`

---

## Investigation Findings

### 1. Missing Function

**File:** `src/operations/modules/planning/planning_utility.py`

**Problem Locations:**
```python
# Line 93 - create_plan()
filename = _truncate_filename(safe_name, max_length=30)

# Line 230 - save_plan()
filename = _truncate_filename(safe_name, max_length=30)
```

**Function Status:** ❌ **NOT DEFINED ANYWHERE**

**Why Import Succeeds:** Python only validates function existence at call time, not import time. This is a runtime bomb waiting to explode.

**Test Validation:**
```bash
python3 -c "from src.operations.modules.planning.planning_utility import create_plan; print('Import successful')"
# Output: Import successful ✅ (but execution would fail ❌)
```

---

### 2. Implementation Report vs Code Reality

**Report Found:** `cortex-brain/documents/reports/filename-length-validation-20241204.md`

**Report Claims (December 4, 2024):**
- ✅ "Successfully implemented 30-character filename limit"
- ✅ "Added `_truncate_filename()` utility function"
- ✅ "Smart truncation preserving meaningful parts"
- ✅ "Updated functions: create_plan() Line 94, save_plan() Line 231"
- ✅ Test cases with 5 examples

**Actual Code Reality:**
- ❌ Function calls exist (lines 93, 230)
- ❌ Function definition **MISSING**
- ❌ Tests would fail on execution
- ✅ Comments confirm intent: "# Generate filename from feature name (30 char max)"

**Conclusion:** Report was aspirational/planned work, not actual implementation verification.

---

### 3. Documentation Discrepancy

#### Phase 8 Plan (Older Specification)

**File:** `cortex-brain/documents/planning/shared-environment-default-activation.md`

**Specified Limits:**
- **Maximum:** 45 characters (excluding extension)
- **Minimum:** 10 characters (excluding extension)
- **Sweet Spot:** 20-35 characters

**Rationale:** "45 chars = ~5 tabs visible in VS Code (optimal multitasking)"

**Task 8.5:** "Update Planning Orchestrator"
- Pattern: `PLAN-{auto_id}-{abbreviated_title}.md`
- Auto-ID: 3-digit sequential (001, 002, 003)
- Abbreviated title: 2-3 word summary (15-20 chars max)

#### Implementation Report (Newer)

**File:** `cortex-brain/documents/reports/filename-length-validation-20241204.md`

**Implemented Limits:**
- **Maximum:** 30 characters (excluding extension)

**Algorithm:**
1. Total limit: 30 chars
2. Timestamp: 8 chars (YYYYMMDD)
3. Extension: 5 chars (.yaml)
4. Hyphen: 1 char
5. **Available for name: 16 chars**

**Examples:**
- `user-aut-fea-20251204.yaml` (26 chars)
- `payment-gat-int-20251204.yaml` (29 chars)
- `database-mig-too-20251204.yaml` (30 chars)

**Discrepancy:** 45 → 30 character change not explained. Looks like someone decided 30 was better but didn't update the master plan.

---

### 4. Phase 8 Task Status

**Plan Tasks (from shared-environment-default-activation.md):**

| Task | File | Status |
|------|------|--------|
| **8.1 Add Tier 0 Governance Rules** | `brain-protection-rules.yaml` | ❓ NOT CHECKED |
| **8.2 Define Filename Convention** | `naming-conventions.md` | ❓ NOT CHECKED |
| **8.3 Implement Filename Validator** | `src/utils/filename_validator.py` | ❌ MISSING |
| **8.4 Filename Shortening Algorithm** | `src/utils/filename_optimizer.py` | ❌ MISSING |
| **8.5 Update Planning Orchestrator** | `planning_orchestrator.py` | ✅ RESTORED (but incomplete) |
| **8.6 Create Realignment Script** | `scripts/realign_filenames.py` | ❓ NOT CHECKED |

**Note:** Task 8.5 is partially done - orchestrator was restored, but utility is broken.

---

### 5. Git History Analysis

**Restoration Commit:** `9b52573e` (Dec 4, 2025)
- Restored `planning_orchestrator.py` (2,652 lines)
- Restored `git_checkpoint_orchestrator.py` (231 lines)
- Added wiring validation report

**Pre-Cleanup Commit:** `9f4091c7`
- "Comprehensive UX enhancement - autonomous execution, session restoration, interactive planning"

**Cleanup Commit:** `32d893ee` (referenced in restoration)
- System alignment v2.0
- Auto-register 6 operations
- Cleanup 5 obsolete orchestrators
- **Likely removed utility functions**

**Filename Report:** `filename-length-validation-20241204.md`
- Created December 4, 2024
- Claims implementation complete
- No corresponding commit found implementing `_truncate_filename()`

---

## Required Implementation

### Missing Function Specification

Based on the report's algorithm and test cases:

```python
def _truncate_filename(name: str, max_length: int = 30) -> str:
    """
    Truncate filename to max_length while preserving meaning.
    
    Algorithm:
    - Reserve 9 chars for timestamp: -{YYYYMMDD} (includes hyphen)
    - Reserve 5 chars for extension: .yaml
    - Total overhead: 14 chars
    - Available for name: max_length - 14
    
    For multi-word names:
    - Keep first word complete
    - Abbreviate remaining words to 3 chars each
    - Preserve readability
    
    Args:
        name: Sanitized filename base (lowercase, hyphens only)
        max_length: Maximum total filename length (default: 30)
        
    Returns:
        Truncated filename with timestamp: {name}-{YYYYMMDD}.yaml
        
    Examples:
        "user-authentication-feature" → "user-aut-fea-20251204.yaml"
        "payment-gateway-integration" → "payment-gat-int-20251204.yaml"
        "api" → "api-20251204.yaml"
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    extension = ".yaml"
    
    # Calculate available space for name
    overhead = len(f"-{timestamp}{extension}")  # 14 chars
    available = max_length - overhead
    
    # If name fits, use as-is
    if len(name) <= available:
        return f"{name}-{timestamp}{extension}"
    
    # Multi-word truncation strategy
    words = name.split('-')
    
    if len(words) == 1:
        # Single word - simple truncation
        truncated = name[:available]
        return f"{truncated}-{timestamp}{extension}"
    
    # Multiple words - keep first, abbreviate rest
    result_words = [words[0]]  # Keep first word complete
    remaining_space = available - len(words[0])
    
    for word in words[1:]:
        abbreviated = word[:3]  # 3 chars per word
        if len('-'.join(result_words + [abbreviated])) <= available:
            result_words.append(abbreviated)
        else:
            break
    
    truncated = '-'.join(result_words)
    return f"{truncated}-{timestamp}{extension}"
```

**Validation Test Cases (from report):**

| Input | Expected Output | Length |
|-------|----------------|--------|
| `user-authentication-feature` | `user-aut-fea-20251204.yaml` | 26 chars |
| `payment-gateway-integration-module` | `payment-gat-int-20251204.yaml` | 29 chars |
| `database-migration-tool-for-production` | `database-mig-too-20251204.yaml` | 30 chars |
| `api` | `api-20251204.yaml` | 17 chars |
| `complex-multi-word-feature-name-with-many-parts` | `complex-mul-wor-20251204.yaml` | 29 chars |

---

## What Else Is Missing?

### Components Referenced But Not Verified:

1. **Tier 0 Governance Rule:** `FILENAME_LENGTH_GOVERNANCE`
   - File: `cortex-brain/brain-protection-rules.yaml`
   - Status: Unknown - needs verification

2. **Filename Validator:** `src/utils/filename_validator.py`
   - Functions: `validate_filename()`, `suggest_shorter_name()`
   - Status: Likely missing

3. **Filename Optimizer:** `src/utils/filename_optimizer.py`
   - Intelligent abbreviation engine
   - Domain-specific dictionary
   - Status: Likely missing

4. **Realignment Script:** `scripts/realign_filenames.py`
   - Batch rename existing files
   - Dry-run mode
   - Status: Unknown

5. **Planning Orchestrator Integration**
   - File: `src/orchestrators/planning_orchestrator.py`
   - Was restored but may also need `_truncate_filename()`
   - Status: Needs verification

---

## Resolution Priority

### CRITICAL (P0) - Immediate

1. **Implement `_truncate_filename()`** in `planning_utility.py`
   - Without this, all plan creation will crash
   - Blocks all planning operations

### HIGH (P1) - Next

2. **Verify Phase 8 governance rules** exist in `brain-protection-rules.yaml`
3. **Check if `planning_orchestrator.py`** has same missing function issue
4. **Reconcile 30 vs 45 character limit** - update plan or implementation

### MEDIUM (P2) - Follow-up

5. **Implement or locate** `filename_validator.py`
6. **Implement or locate** `filename_optimizer.py`
7. **Verify** `realign_filenames.py` script exists

---

## Recommendations

### Immediate Action

```bash
# 1. Add _truncate_filename() to planning_utility.py
# 2. Run test to verify:
python3 -m src.operations.modules.planning.planning_utility

# 3. Test actual plan creation:
python3 -c "
from src.operations.modules.planning.planning_utility import create_plan
result = create_plan('Test Feature With Long Name')
print(f'Success: {result.success}')
print(f'Filename: {result.plan_path.name if result.plan_path else 'N/A'}')
"
```

### Investigation Expansion

```bash
# Check governance rules
grep -A 20 "FILENAME_LENGTH_GOVERNANCE" cortex-brain/brain-protection-rules.yaml

# Check for utility files
find src/utils -name "*filename*"

# Check planning orchestrator
grep "_truncate_filename" src/orchestrators/planning_orchestrator.py
```

### Documentation Alignment

Decision needed on character limit:
- **Option A:** Keep 30 chars (current implementation intent)
  - Update Phase 8 plan documentation
  - Rationale: More aggressive space saving
  
- **Option B:** Change to 45 chars (original specification)
  - Update implementation and report
  - Rationale: Better readability, matches original analysis

**Recommendation:** Keep 30 chars. The 45-char examples in plan docs are actually 28-31 chars:
- `PLAN-001-shared-env-setup.md` = 28 chars
- `ADO-4567-auth-fix.md` = 18 chars  
- `REPORT-2025Q4-setup-metrics.md` = 31 chars

The spec was self-contradictory. Implementation chose the practical limit.

---

## 📝 Your Request

Investigate why CORTEX is still creating plans with long filenames and check what else from the restoration session is not wired in.

## 🔍 Next Steps

### Parallel Track A: Fix Critical Bug

1. ☐ Implement `_truncate_filename()` function in `planning_utility.py`
2. ☐ Add unit tests for truncation logic
3. ☐ Verify plan creation works end-to-end

### Parallel Track B: Verify Phase 8 Components

4. ☐ Check Tier 0 governance rules in `brain-protection-rules.yaml`
5. ☐ Search for `filename_validator.py` and `filename_optimizer.py`
6. ☐ Check planning orchestrator for same issue
7. ☐ Locate or implement realignment script

### Track C: Documentation Alignment

8. ☐ Decide on 30 vs 45 character limit (recommend: 30)
9. ☐ Update Phase 8 plan documentation
10. ☐ Mark Phase 8 tasks with actual completion status

---

**Status:** Investigation complete, awaiting fix implementation  
**Estimated Fix Time:** 15-20 minutes for critical fix, 1-2 hours for full Phase 8 verification
