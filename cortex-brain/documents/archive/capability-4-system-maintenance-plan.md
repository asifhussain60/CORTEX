# Phase 13B Capability 4: System Maintenance Validation Plan

**Capability:** System Maintenance - 7-Phase Workflow  
**Status:** ⏳ READY FOR VALIDATION  
**Date:** December 26, 2025  
**Duration:** 5 hours estimated

---

## 🎯 Validation Objective

Validate System Maintenance Orchestrator's ability to comprehensively maintain a codebase through 7 integrated phases:

1. **Pre-Healthcheck:** Establish baseline health score
2. **Align:** Auto-fix SKULL rule violations
3. **Cleanup:** Remove dead code, orphaned files
4. **Optimize:** Token optimization (response templates, manifests)
5. **Vacuum:** SQLite database compression
6. **Refresh Prompts:** Regenerate `.prompt.md` files
7. **Post-Healthcheck:** Measure health improvement

**Target:** STS validation app with 300+ lines dead code, memory leaks, 0 critical issues post-maintenance

---

## 📊 STS Application Current State (Pre-Maintenance)

### Deliberate Flaws (65 total, targeting maintenance-relevant issues)

| Category | Flaw ID | Description | Lines | Target Phase |
|----------|---------|-------------|-------|--------------|
| **Dead Code** | CQ-05 | Unused helper functions | 150 | Cleanup |
| **Dead Code** | CQ-06 | Commented-out code blocks | 80 | Cleanup |
| **Dead Code** | CQ-12 | Orphaned test fixtures | 40 | Cleanup |
| **Dead Code** | CQ-15 | Unused imports across 20 files | 30 | Cleanup |
| **Memory Leaks** | PERF-03 | Cache never cleared | - | Align |
| **Memory Leaks** | PERF-04 | DB connections not closed | - | Align |
| **Complexity** | CQ-01 | OrderProcessor complexity 87 | - | Align |
| **Complexity** | CQ-09 | God object (500+ LOC) | - | Align |
| **SOLID Violations** | SOL-01 | UserManager God class (820+ LOC) | - | Align |
| **SQLite Bloat** | PERF-07 | 50MB database, 10MB wasted | - | Vacuum |
| **Token Waste** | DOC-03 | Verbose response templates | - | Optimize |
| **Outdated Docs** | DOC-01 | Contradictory architecture.md | - | Refresh |
| **Outdated Docs** | DOC-04 | Missing API endpoints | - | Refresh |

**Summary:**
- **Dead Code:** 300+ lines to remove
- **Memory Leaks:** 2 critical issues (cache + connections)
- **Complexity:** 2 god classes (87, 500+ LOC)
- **SQLite Bloat:** 10MB wasted space
- **Token Waste:** 20% reduction potential
- **Outdated Docs:** 8 documentation issues

**Health Baseline:** 35/100 (F grade)

---

## 🎯 Phase-by-Phase Validation Plan

### Phase 1: Pre-Healthcheck (30 minutes)

**Objective:** Establish baseline health score across 7 components

**Components to Scan:**
1. **Tier 0 (SKULL):** Brain protection rules enforcement (20% weight)
2. **Tier 1 (Working Memory):** Conversation history health (15% weight)
3. **Tier 2 (Knowledge Graph):** Graph integrity (15% weight)
4. **Tier 3 (Dev Context):** Dev context freshness (10% weight)
5. **Code Quality:** Complexity, duplication, dead code (20% weight)
6. **Test Coverage:** Test pass rate, coverage % (10% weight)
7. **Documentation:** Doc freshness, completeness (10% weight)

**Expected Baseline:**
```python
{
    "tier0_health": 45,  # SKULL violations: memory leaks, god classes
    "tier1_health": 60,  # Working memory: acceptable
    "tier2_health": 70,  # Knowledge graph: good
    "tier3_health": 50,  # Dev context: some outdated
    "code_quality": 25,  # Dead code, complexity, SOLID violations
    "test_coverage": 15,  # 15% coverage only
    "documentation": 30,  # Outdated, contradictory
    "overall_health": 35  # Weighted average (F grade)
}
```

**Validation Criteria:**
- ✅ Baseline calculated (0-100 scale)
- ✅ All 7 components scanned
- ✅ Results logged with breakdown
- ✅ Baseline stored for delta calculation

---

### Phase 2: Align (60 minutes)

**Objective:** Auto-fix SKULL rule violations

**Target Violations:**
1. **TDD_ENFORCEMENT:** No tests for OrderProcessor
2. **HOLISTIC_CODE_DISCOVERY_ENFORCEMENT:** Duplicate payment processors (3×)
3. **REFACTOR_CODE_CLEANUP_ENFORCEMENT:** God classes (UserManager 820 LOC, helpers.py 500 LOC)
4. **GIT_ISOLATION_ENFORCEMENT:** Tests mixed with src code

**Auto-Fix Strategy:**
```python
# 1. TDD Enforcement
- Detect untested modules: order_processor.py (0% coverage)
- Create test stubs: test_order_processor.py (15 placeholder tests)
- Log recommendation: "Run TDD Mastery to implement tests"

# 2. Holistic Discovery
- Detect duplicates: payment_stripe.py, payment_paypal.py, payment_square.py
- Extract interface: IPaymentProcessor
- Log recommendation: "Consolidate payment processors using Strategy pattern"

# 3. Refactor Cleanup
- Detect god classes: UserManager (820 LOC), helpers.py (500 LOC)
- Log recommendation: "Run Planning System to refactor god classes"

# 4. Git Isolation
- Detect mixed code: tests/ has src files, src/ has test files
- Auto-fix: Move files to correct directories
- Update imports automatically
```

**Expected Fixes:**
- **Auto-Fixed:** Git isolation (10 files moved), test stub creation (3 files)
- **Logged Recommendations:** Refactoring (2 god classes), consolidation (3 payment processors)

**Validation Criteria:**
- ✅ SKULL violations detected (4/4 categories)
- ✅ Auto-fixes applied (git isolation, test stubs)
- ✅ Recommendations logged for manual fixes
- ✅ No false positives (no incorrect "violations")

---

### Phase 3: Cleanup (45 minutes)

**Objective:** Remove dead code, orphaned files, unused imports

**Cleanup Rules (from `cortex-brain/cleanup-rules.yaml`):**

1. **Dead Code Detection:**
```python
# Rule: Unused functions (no callers in codebase)
def obsolete_helper():  # CQ-05: No callers
    """This function is never called."""
    pass

# Rule: Commented-out code blocks
# def old_payment_logic():  # CQ-06: Commented out
#     # This is old code, should be removed
#     pass

# Rule: Unreachable code (after return)
def process_order(order):
    return order.total
    print("This never executes")  # Unreachable
```

2. **Orphaned Files:**
```python
# Rule: Test files with no src equivalent
tests/test_deprecated_api.py  # CQ-12: API removed, test orphaned

# Rule: Backup files (.bak, .old)
src/api/users.py.bak  # Backup file, should be removed
```

3. **Unused Imports:**
```python
# Rule: Imports not referenced in file
from datetime import datetime  # CQ-15: Never used
from typing import Dict, List, Optional  # Only Dict used
import json  # Never used
```

**Target Cleanup:**
- **Dead Functions:** 8 unused helpers (150 LOC)
- **Commented Code:** 12 blocks (80 LOC)
- **Unreachable Code:** 5 instances (20 LOC)
- **Orphaned Files:** 6 files (40 LOC)
- **Unused Imports:** 30 imports across 20 files (30 LOC)

**Total Cleanup:** 320 lines removed

**Validation Criteria:**
- ✅ Dead code detected (100% accuracy, 0 false positives)
- ✅ Orphaned files identified (6/6)
- ✅ Unused imports removed (30/30)
- ✅ Code still passes tests after cleanup
- ✅ No regressions (existing tests still pass)

---

### Phase 4: Optimize (45 minutes)

**Objective:** Token optimization for large files

**Target Files:**

1. **Response Templates (Token Waste: DOC-03):**
```yaml
# BEFORE (verbose, 15KB)
system_maintenance_complete:
  header: "🎉 System Maintenance Complete..."
  sections:
    - title: "Understanding & Scope"
      content: "Long verbose explanation of what was done..."
    - title: "Approach & Considerations"
      content: "Detailed breakdown of every step..."
    # ... 8 more verbose sections

# AFTER (token-optimized, 8KB, 47% reduction)
system_maintenance_complete:
  header: "🎉 System Maintenance Complete..."
  sections:
    - title: "Understanding"
      content: "Concise summary..."
    - title: "Approach"
      content: "Brief breakdown..."
    # ... condensed to 4 sections
```

2. **Manifest Files (Token Waste: >20KB):**
```yaml
# BEFORE (monolithic, 25KB)
planning-system-manifest.yaml:
  phases: [10 phases with full details inline...]
  tdd_integration: [6 cycles with full details...]
  dor_gates: [40+ gates with full details...]

# AFTER (modular hierarchy, 8KB index + 3 modules)
planning-system-manifest.yaml:  # 8KB index
  metadata: ...
  includes:
    - phases/phase-details.yaml  # 6KB
    - tdd/tdd-cycles.yaml  # 5KB
    - dor-dod/gates.yaml  # 6KB
```

**Expected Optimization:**
- **Response Templates:** 15KB → 8KB (47% reduction)
- **Manifests:** 25KB → 8KB index + 3×6KB modules (68% reduction for loading)
- **Total Tokens Saved:** ~35% across optimized files

**Validation Criteria:**
- ✅ Large files identified (>10KB)
- ✅ Token reduction achieved (30%+ target)
- ✅ Content integrity preserved (no meaning lost)
- ✅ Performance improved (faster loading)

---

### Phase 5: Vacuum (30 minutes)

**Objective:** SQLite database compression + AST/bytecode cleanup

**Target Databases:**

1. **cortex_alerts.db (PERF-07):**
   - Size: 12MB
   - Wasted space: 3MB (deleted records, fragmentation)
   - Expected after vacuum: 9MB (25% reduction)

2. **cortex_metrics.db:**
   - Size: 18MB
   - Wasted space: 4MB
   - Expected after vacuum: 14MB (22% reduction)

3. **cortex-brain.db:**
   - Size: 25MB
   - Wasted space: 5MB
   - Expected after vacuum: 20MB (20% reduction)

**Vacuum Strategy:**
```python
# 1. Identify SQLite databases
databases = [
    "cortex_alerts.db",
    "cortex_metrics.db",
    "cortex-brain.db"
]

# 2. For each database:
for db_path in databases:
    # Measure size before
    size_before = get_file_size(db_path)
    
    # Run VACUUM command
    conn = sqlite3.connect(db_path)
    conn.execute("VACUUM")
    conn.close()
    
    # Measure size after
    size_after = get_file_size(db_path)
    
    # Calculate savings
    space_saved = size_before - size_after
    reduction_pct = (space_saved / size_before) * 100

# 3. AST/Bytecode cleanup (.pyc files)
find_and_remove_pyc_files()
```

**Expected Results:**
- **Databases Vacuumed:** 3/3
- **Space Saved:** 12MB total (22% average reduction)
- **AST Cleanup:** ~200 `.pyc` files removed

**Validation Criteria:**
- ✅ All SQLite databases identified (3/3)
- ✅ VACUUM command executed successfully
- ✅ Space saved (>10% reduction target)
- ✅ Data integrity verified (no corruption)
- ✅ AST cleanup completed

---

### Phase 6: Refresh Prompts (30 minutes)

**Objective:** Regenerate `.prompt.md` files from YAML manifests

**Target Prompts (Outdated: DOC-01, DOC-04):**

1. **planning-system.prompt.md (Outdated):**
```markdown
# BEFORE (contradicts code)
## Planning System 2.0
- 3-tier complexity routing (LIGHTWEIGHT, DOCUMENTED, COMPLEX)
- No TDD integration
- Manual DoR/DoD gates

# AFTER (regenerated from manifest)
## Planning System 4.0
- 4-tier complexity routing (INSTANT, LIGHTWEIGHT, DOCUMENTED, COMPLEX)
- Automatic TDD integration (6 cycles)
- Automated DoR/DoD gates (40+)
```

2. **tdd-mastery.prompt.md (Missing endpoints: DOC-04):**
```markdown
# BEFORE (incomplete)
## TDD Orchestrator
- RED phase: Write failing tests
- GREEN phase: Make tests pass

# AFTER (regenerated from manifest)
## TDD Orchestrator
- RED phase: Write failing tests (pytest)
- GREEN phase: Minimal implementation
- REFACTOR phase: Clean code (complexity <15, coverage 90%+)
- Git checkpoint safety (3 per cycle)
```

**Regeneration Strategy:**
```python
# 1. Find all YAML manifests
manifests = [
    "planning-system-manifest.yaml",
    "tdd-mastery-manifest.yaml",
    "maintenance-manifest.yaml",
    # ...
]

# 2. For each manifest:
for manifest_path in manifests:
    # Parse YAML
    manifest = yaml.safe_load(open(manifest_path))
    
    # Extract key sections
    metadata = manifest["metadata"]
    phases = manifest.get("phases", [])
    examples = manifest.get("examples", [])
    
    # Generate .prompt.md
    prompt_content = generate_prompt_from_manifest(
        metadata, phases, examples
    )
    
    # Write to file
    prompt_path = manifest_path.replace(".yaml", ".prompt.md")
    with open(prompt_path, "w") as f:
        f.write(prompt_content)

# 3. Validate regenerated prompts
- Check no sections missing
- Verify examples included
- Confirm metadata correct
```

**Expected Results:**
- **Prompts Regenerated:** 8 files
- **Contradictions Resolved:** 3 outdated descriptions fixed
- **Missing Content Added:** 5 missing endpoint descriptions

**Validation Criteria:**
- ✅ All prompts regenerated (8/8)
- ✅ Content accurate (matches manifests 100%)
- ✅ No contradictions (code vs docs alignment)
- ✅ Examples included (all examples from YAML)

---

### Phase 7: Post-Healthcheck (30 minutes)

**Objective:** Measure health improvement (delta calculation)

**Expected Health Improvement:**

| Component | Baseline | Post-Maintenance | Delta | Improvement |
|-----------|----------|------------------|-------|-------------|
| **Tier 0 (SKULL)** | 45 | 75 | +30 | Auto-fixes applied |
| **Tier 1 (Memory)** | 60 | 65 | +5 | Minor improvements |
| **Tier 2 (Knowledge)** | 70 | 75 | +5 | Graph cleanup |
| **Tier 3 (Dev Context)** | 50 | 70 | +20 | Docs refreshed |
| **Code Quality** | 25 | 60 | +35 | Dead code removed |
| **Test Coverage** | 15 | 25 | +10 | Test stubs created |
| **Documentation** | 30 | 80 | +50 | Prompts regenerated |
| **Overall** | **35** | **65** | **+30** | **F → D grade** |

**Health Delta Interpretation:**
- **0-10 points:** Minimal improvement (maintenance unnecessary)
- **10-20 points:** Moderate improvement (regular maintenance recommended)
- **20-40 points:** Significant improvement (maintenance critical)
- **40+ points:** Transformational improvement (system was unhealthy)

**Expected:** +30 points (Significant improvement, F → D grade)

**Validation Criteria:**
- ✅ Final health calculated (0-100 scale)
- ✅ Delta calculated (baseline vs final)
- ✅ All 7 components rescanned
- ✅ Improvement logged with breakdown
- ✅ Health trend positive (+30 target)

---

## 📊 Success Criteria Matrix

| Phase | Criteria | Target | Validation Method |
|-------|----------|--------|-------------------|
| **Pre-Healthcheck** | Baseline calculated | 35/100 | Health scan output |
| | Components scanned | 7/7 | Scan results log |
| **Align** | SKULL violations detected | 4/4 | Violation report |
| | Auto-fixes applied | 2/4 | Git diff (10 files moved, 3 test stubs) |
| | Recommendations logged | 2/4 | Recommendation report |
| **Cleanup** | Dead code removed | 320 LOC | Git diff line count |
| | Accuracy | 100% | Manual review (0 false positives) |
| | No regressions | 100% | Test pass rate maintained |
| **Optimize** | Token reduction | 35%+ | File size comparison |
| | Content integrity | 100% | Semantic comparison |
| **Vacuum** | Databases vacuumed | 3/3 | Vacuum log |
| | Space saved | 12MB | File size comparison |
| **Refresh** | Prompts regenerated | 8/8 | File modification times |
| | Accuracy | 100% | Manifest-prompt comparison |
| **Post-Healthcheck** | Final health | 65/100 | Health scan output |
| | Delta | +30 | Baseline vs final |
| **Overall** | Critical issues | 0 | Final health report |
| | Grade improvement | F → D | Score interpretation |

---

## 🔄 Execution Timeline

### Day 1 (5 hours total)

**Hour 1: Pre-Healthcheck + Setup**
- Run baseline health scan (30 min)
- Document baseline metrics (30 min)

**Hour 2: Align Phase**
- Detect SKULL violations (20 min)
- Apply auto-fixes (30 min)
- Log recommendations (10 min)

**Hour 3: Cleanup Phase**
- Detect dead code (15 min)
- Remove dead code (20 min)
- Verify no regressions (10 min)

**Hour 4: Optimize + Vacuum**
- Token optimization (25 min)
- SQLite vacuum (20 min)
- Verify space saved (15 min)

**Hour 5: Refresh + Post-Healthcheck**
- Regenerate prompts (20 min)
- Run final health scan (20 min)
- Calculate delta (10 min)
- Generate report (10 min)

---

## 📝 Validation Report Template

```markdown
# System Maintenance Validation Report

## Executive Summary
- **Overall Result:** ✅ PASS / ❌ FAIL
- **Health Improvement:** 35 → 65 (+30 points, F → D grade)
- **Critical Issues:** 0 remaining
- **Duration:** 5 hours

## Phase Results

### Phase 1: Pre-Healthcheck ✅
- **Baseline Health:** 35/100
- **Components Scanned:** 7/7
- **Criteria Met:** 4/4

### Phase 2: Align ✅
- **Violations Detected:** 4/4 (TDD, Discovery, Refactor, Git Isolation)
- **Auto-Fixes:** 2/4 (Git isolation, test stubs)
- **Recommendations:** 2/4 (god classes, payment processors)
- **Criteria Met:** 4/4

### Phase 3: Cleanup ✅
- **Dead Code Removed:** 320 LOC
- **Accuracy:** 100% (0 false positives)
- **No Regressions:** 100% tests still passing
- **Criteria Met:** 5/5

### Phase 4: Optimize ✅
- **Token Reduction:** 38% (15KB → 8KB templates)
- **Content Integrity:** 100%
- **Criteria Met:** 4/4

### Phase 5: Vacuum ✅
- **Databases Vacuumed:** 3/3
- **Space Saved:** 12MB (22%)
- **Data Integrity:** 100%
- **Criteria Met:** 5/5

### Phase 6: Refresh Prompts ✅
- **Prompts Regenerated:** 8/8
- **Accuracy:** 100%
- **Contradictions Resolved:** 3/3
- **Criteria Met:** 4/4

### Phase 7: Post-Healthcheck ✅
- **Final Health:** 65/100
- **Delta:** +30 points (Significant improvement)
- **Grade:** F → D
- **Criteria Met:** 5/5

## Overall Validation

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Health Improvement | +20 | +30 | ✅ PASS |
| Critical Issues | 0 | 0 | ✅ PASS |
| Phase Completion | 7/7 | 7/7 | ✅ PASS |
| Accuracy | 100% | 100% | ✅ PASS |
| No Regressions | 100% | 100% | ✅ PASS |

**Verdict:** ✅ **SYSTEM MAINTENANCE VALIDATED**
```

---

## 🎯 Next Steps After Validation

1. **Capability 5: System Refinement** - Resolve remaining SOLID violations (35 → 0)
2. **Return to TDD Mastery:** Complete Cycles 2-8 (90%+ coverage target)
3. **Capability 6: Architectural Review** - Score improvement (25 → 90)

---

**Plan Created:** December 26, 2025  
**Status:** ⏳ READY FOR VALIDATION  
**Duration:** 5 hours estimated  
**Target:** 0 critical issues, +30 health improvement, F → D grade

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
