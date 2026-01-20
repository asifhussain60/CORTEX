# MIGRATION_PLAN.md: From Dual to Unified CORTEX Structure
**Acceptance Criteria**: Folder Structure Planning & Design  
**Document**: Migration Planning & Execution Strategy  
**Status**: MIGRATION PLAN (AC-AR-010-01 Phase 2)  
**Date**: 2026-01-18  
**Target Completion**: 2026-01-23

---

## Executive Summary

This plan details the phased migration from CORTEX's current dual-structure organization (cortex_brain/ + src/) to the unified, tier-based hierarchy defined in FOLDER_STRUCTURE_DESIGN.md.

**Migration Scope**: 
- Consolidate 30+ modules from cortex_brain/ and src/
- Reorganize into 8 top-level modules under unified cortex/ root
- Update 200+ import paths
- Validate on macOS, Linux, Windows (simulated)
- Zero downtime (staging → main in atomic operation)

**Risk Level**: MEDIUM-HIGH (widespread refactoring, many dependencies)

---

## Migration Approach: Four-Phase Strategy

### Phase 1: Preparation & Validation (Day 1-2)
- Analyze current structure in detail
- Create migration script (AC-AR-010-02)
- Test script on staging environment
- Build rollback plan

### Phase 2: Structural Migration (Day 3)
- Execute file movement (automated script)
- Verify file integrity (checksums)
- Generate migration report
- Manual verification of critical paths

### Phase 3: Import Updates (Day 4-5)
- Update all import statements (automated + manual)
- Update __init__.py files
- Resolve circular dependencies
- Test on all platforms

### Phase 4: Verification & Deployment (Day 5-6)
- Full test suite execution (100% pass required)
- Cross-platform validation
- Performance benchmarking
- Deploy to main

---

## Phase 1: Preparation & Validation (Days 1-2)

### 1.1 Current State Inventory

**Files to Migrate** (High-Level Count):

```
cortex_brain/
├── tier0/          ← 12 files (governance, audit, schemas)
├── tier1/          ← 18 files (orchestrators, routing)
├── tier2/          ← 25 files (domains, coherence, security, resilience)
├── tier3/          ← 8 files (knowledge, cache, services)
└── [other]/        ← 7 files (config, registry, state, vacuum)
TOTAL: ~70 files

src/
├── api/            ← 15 files (REST, MCP, CLI)
├── orchestrators/  ← 12 files (domain, planning, master orchestrators)
├── infrastructure/ ← 8 files (deployment, monitoring, logging)
├── knowledge/      ← 10 files (providers, storage, domains)
├── tools/          ← 8 files (testing utilities, validators)
└── [others]/       ← 30+ files (ci_cd, cli, core, dashboard, etc.)
TOTAL: ~100+ files

GRAND TOTAL: ~170 files to reorganize
```

### 1.2 Dependency Analysis

**Critical Dependencies to Track**:
1. **Tier isolation violations** (tier2 importing from tier1, etc.)
2. **Circular imports** (A → B → A)
3. **External package dependencies** (ensure portability)
4. **Platform-specific imports** (Windows/Linux/macOS differences)

**Dependency Map** (Sample):
```
cortex.core (tier0 foundation)
  ← tier1 (orchestrators) imports from tier0
    ← tier2 (domains) imports from tier1 and tier0
      ← tier3 (knowledge) imports from tier2, tier1, tier0
      ← api imports from tier0, tier1, tier2, tier3
```

### 1.3 Pre-Migration Checklist

- [ ] **Code backup**: Full git commit of current state
- [ ] **Test baseline**: Current test suite passes 100%
- [ ] **Import audit**: Document all current imports
- [ ] **Platform check**: Test current code on Windows (via WSL simulation)
- [ ] **Dependencies**: List all external packages used
- [ ] **Documentation**: Document current structure in commit message

**Command**:
```bash
git add -A
git commit -m "MIGRATION-PREP: Baseline before folder structure consolidation

Current structure: cortex_brain/ + src/ (dual)
Target structure: cortex/ (unified)

Baseline tests: ✅ All passing
Current files: ~170 Python modules
Import paths: ~200+ to update

Backup: This commit
Next: Execute migration script (AC-AR-010-02)"
```

---

## Phase 2: Structural Migration (Day 3)

### 2.1 File Movement Strategy

**Order of Operations** (Dependency-aware):

```
Step 1: Create new cortex/ root directory
Step 2: Move tier0 files → cortex/core/ + cortex/brain/tier0/
Step 3: Move tier1 files → cortex/brain/tier1/
Step 4: Move tier2 files → cortex/brain/tier2/
Step 5: Move tier3 files → cortex/brain/tier3/
Step 6: Move API files → cortex/api/
Step 7: Move orchestrators → cortex/orchestrators/
Step 8: Move knowledge files → cortex/knowledge/
Step 9: Move infrastructure → cortex/infrastructure/
Step 10: Move tools → cortex/tools/
Step 11: Update documentation
Step 12: Remove old directories (cortex_brain/, src/)
Step 13: Update imports
```

**Why This Order?**
- Start with foundation (tier0) - no dependencies on higher tiers
- Move tiers in order (tier1 before tier2, etc.)
- Save API/tools last (depend on everything)
- Update imports at end (after structure stable)

### 2.2 Automated Migration Script Requirements (AC-AR-010-02)

**Script Inputs**:
- Current directory structure (discovered automatically)
- Mapping file (cortex_brain → cortex/brain, src/api → cortex/api, etc.)
- Dry-run flag (--dry-run)
- Verbose flag (--verbose)

**Script Outputs**:
- Migration report (files moved, checksums, errors)
- Rollback script (revert all moves)
- Import update list (files requiring import changes)

**Pseudocode**:
```python
def migrate_structure(dry_run=False, verbose=False):
    """
    Migrate from dual (cortex_brain/ + src/) to unified cortex/ structure.
    """
    # 1. Validate preconditions
    validate_git_clean()
    validate_current_structure()
    
    # 2. Create mapping (source → destination)
    mapping = create_migration_mapping()  # ~40 entries
    
    # 3. For each mapping entry, move files
    for source, dest in mapping:
        if dry_run:
            print(f"Would move: {source} → {dest}")
        else:
            safe_move(source, dest)  # with checksum verification
            
    # 4. Generate reports
    report = MigrationReport(
        files_moved=count,
        errors=[],
        import_changes_needed=import_list
    )
    
    # 5. Generate rollback script
    generate_rollback_script(mapping)
    
    return report
```

### 2.3 File Integrity Verification

**Checksum Strategy**:
```python
# Before move: hash all files
before_hashes = {
    "cortex_brain/tier2/domains/foo.py": "abc123...",
    "cortex_brain/tier2/domains/bar.py": "def456...",
    ...
}

# After move: verify all hashes match new locations
after_hashes = {
    "cortex/brain/tier2/domains/foo.py": "abc123...",  # Must match
    "cortex/brain/tier2/domains/bar.py": "def456...",  # Must match
    ...
}

# Validation: before_hashes == after_hashes
if before_hashes == after_hashes:
    print("✅ All files moved correctly, no data loss")
else:
    print("❌ CHECKSUM MISMATCH - ROLLBACK REQUIRED")
    rollback()
```

### 2.4 Manual Verification Checklist (Post-Move)

After automated migration, verify:

- [ ] **cortex/ root created** and contains 8 top-level folders
- [ ] **All old directories empty** (cortex_brain/, src/ removed or empty)
- [ ] **No orphaned files** (all files accounted for)
- [ ] **__init__.py exists** in all packages
- [ ] **Critical modules present**:
  - [ ] cortex/core/governance/ (tier0 foundation)
  - [ ] cortex/brain/tier1/orchestrators/ (tier1 orchestration)
  - [ ] cortex/orchestrators/ (public API)
  - [ ] cortex/api/ (external interfaces)
- [ ] **File count matches** expected count (~170 files)
- [ ] **Checksums all verify**

---

## Phase 3: Import Updates (Days 4-5)

### 3.1 Import Update Strategy

**Three-Tier Approach**:

1. **Automated Updates** (via AST rewriting)
   - Apply regex patterns to update common imports
   - Update __init__.py files
   - Estimated coverage: 70-80%

2. **Manual Updates** (for complex cases)
   - Circular dependency resolution
   - Conditional imports
   - Dynamic imports (getattr, __import__)
   - Estimated count: 40-60 cases

3. **Validation** (via testing)
   - Test suite catches remaining import errors
   - Cross-platform import resolution
   - IDE import resolution (Pylance validation)

### 3.2 Import Transformation Examples

**Example 1: Tier-based imports**
```python
# OLD
from cortex_brain.tier2.domains.security import SecurityDomain

# NEW
from cortex.brain.tier2.domains.security import SecurityDomain

# Regex pattern:
# from cortex_brain\.tier(\d+)\.(\w+) → from cortex.brain.tier$1.$2
```

**Example 2: Orchestrator imports**
```python
# OLD
from src.orchestrators.planning.orchestrator import PlanningOrchestrator

# NEW (private)
from cortex.brain.tier1.orchestrators.planning import PlanningOrchestrator

# NEW (public, preferred)
from cortex.orchestrators.planning import PlanningOrchestrator

# Choice: Prefer public API when available
```

**Example 3: API imports**
```python
# OLD
from src.api.rest import create_app
from src.api.mcp import serve

# NEW
from cortex.api.rest import create_app
from cortex.api.mcp import serve

# Regex pattern:
# from src\.(\w+) → from cortex.$1
```

### 3.3 Circular Dependency Resolution

**Strategy**: Use import at function level if necessary

```python
# Before: Circular dependency
# domains.py imports from resilience.py
# resilience.py imports from domains.py

# Problem: Can't resolve at module level
# Solution 1: Move shared code to separate module
# Solution 2: Import at function level

# Option 2 example:
# domains.py
def get_resilient_domain(domain_id):
    from cortex.brain.tier2.resilience import apply_resilience
    # Import inside function - OK
    resilient = apply_resilience(self.domain)
    return resilient
```

### 3.4 Import Validation Tests (New)

**Created in AC-AR-010-03**:
```python
def test_no_broken_imports():
    """Verify all imports can be resolved"""
    import ast
    for py_file in find_all_py_files():
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Try importing the module
                try:
                    __import__(node.module)
                except ImportError as e:
                    fail(f"Broken import in {py_file}: {node.module}")

def test_no_tier_isolation_violations():
    """Verify tier isolation rules"""
    # tier0 imports: only from tier0
    # tier1 imports: only from tier0, tier1
    # tier2 imports: only from tier0, tier1, tier2
    # tier3 imports: any lower tier
    # Validate via AST analysis
    pass

def test_no_circular_dependencies():
    """Verify no circular imports"""
    # Build dependency graph
    # Check for cycles using DFS
    pass
```

---

## Phase 4: Verification & Deployment (Days 5-6)

### 4.1 Test Suite Validation

**Required Pass Rates**:

| Test Category | Required | Acceptable | Failure Threshold |
|--------------|----------|------------|-------------------|
| Unit Tests | 100% | N/A | 0 failures |
| Integration Tests | 100% | N/A | 0 failures |
| Import Resolution | 100% | N/A | 0 broken imports |
| Tier Isolation | 100% | N/A | 0 violations |
| Cross-Platform Paths | 100% | N/A | 0 platform errors |
| **Overall** | **100%** | **N/A** | **0 failures** |

**Command**:
```bash
# Run all tests
python -m pytest tests/ -v --tb=short

# Expected output:
# ================ 200 passed in 12.34s ================
```

### 4.2 Cross-Platform Validation

**Platforms to Test**:

1. **macOS** (primary development)
   ```bash
   python -m pytest tests/ -k "not windows"
   ```

2. **Linux** (CI/CD environment)
   ```bash
   # Via Docker or GitHub Actions
   docker run -v $(pwd):/cortex python:3.9 bash -c \
     "cd /cortex && python -m pytest tests/"
   ```

3. **Windows** (via WSL simulation)
   ```bash
   # Test path handling with Windows paths
   pytest tests/test_import_paths.py -k "windows"
   ```

**Path Resolution Tests** (ensure cross-platform):
```python
def test_import_resolution_posix():
    """Verify imports work on POSIX (macOS/Linux)"""
    from cortex.brain.tier2.domains.security import SecurityDomain
    assert SecurityDomain is not None

def test_import_resolution_windows_paths():
    """Verify pathlib handles Windows paths correctly"""
    from pathlib import Path
    # Use PureWindowsPath to simulate Windows without actual system
    win_path = PureWindowsPath("cortex\\brain\\tier2\\domains")
    posix_path = Path("cortex/brain/tier2/domains")
    assert win_path.as_posix() == str(posix_path)
```

### 4.3 Performance Benchmarking

**Baseline Metrics**:
```python
import time

# Import time
start = time.time()
from cortex.brain.tier1 import *  # Import tier1
import_time = time.time() - start

# Must be < 100ms (currently ~50ms before migration)
assert import_time < 0.1, f"Import time degraded: {import_time}"

# Module discovery time
start = time.time()
import cortex
discover_time = time.time() - start

# Must be < 200ms
assert discover_time < 0.2, f"Discovery time: {discover_time}"
```

### 4.4 Deployment Plan

**Deployment Sequence**:

1. **Backup Current Main** (just in case)
   ```bash
   git tag pre-migration-backup
   ```

2. **Merge Migration Branch**
   ```bash
   git merge feature/unified-structure
   ```

3. **Deploy to Staging**
   ```bash
   ./deploy.sh staging
   ```

4. **Verify on Staging** (15 minutes)
   - Run full test suite ✅
   - Spot-check critical paths ✅
   - Monitor for errors ✅

5. **Deploy to Production**
   ```bash
   ./deploy.sh production
   ```

6. **Verification** (ongoing)
   - Monitor error logs ✅
   - Check import errors ✅
   - Verify performance ✅

---

## Risk Mitigation Strategies

### Risk 1: Import Resolution Failures (LIKELIHOOD: MEDIUM)

**Mitigation**:
- Pre-migration import audit (catalog all imports)
- Automated import update script with validation
- Test-driven: each failing import triggers test failure
- Rollback plan: automated reversion to old structure

**Contingency**: If > 10 import errors detected, rollback to backup

### Risk 2: Circular Dependency Deadlock (LIKELIHOOD: LOW)

**Mitigation**:
- Pre-migration cycle detection (using DFS on import graph)
- Import at function level if cycles exist
- Test: test_no_circular_dependencies validates resolution

**Contingency**: If circular dependencies found, delay migration 1 day for resolution

### Risk 3: Cross-Platform Path Issues (LIKELIHOOD: MEDIUM)

**Mitigation**:
- Enforce pathlib.Path usage (no os.path)
- Test on Windows (via WSL)
- Validate UNC paths, drive letters, long paths
- Platform-specific test suite

**Contingency**: If Windows path tests fail, delay migration, fix root cause

### Risk 4: Performance Degradation (LIKELIHOOD: LOW)

**Mitigation**:
- Benchmark before/after import times
- Verify module discovery time < 200ms
- Profile package initialization
- Cache __init__.py optimization

**Contingency**: If import time > 150ms (was 50ms), profile and optimize

### Risk 5: File Loss or Corruption (LIKELIHOOD: VERY LOW)

**Mitigation**:
- Pre-move checksum hashing of all files
- Post-move verification (must match checksums)
- Atomic operations (all-or-nothing semantics)
- Automatic rollback if any checksum fails

**Contingency**: If checksum fails, auto-rollback, investigate cause

---

## Rollback Plan (If Needed)

**Rollback Trigger** (automatic):
- Any checksum verification fails → Automatic rollback
- > 10 import errors detected → Manual review, then rollback if needed
- Cross-platform tests fail → Delay migration, investigate

**Manual Rollback Command**:
```bash
# Generated automatically during migration
./scripts/rollback_migration.sh

# Manually revert to backup
git checkout pre-migration-backup
```

**Rollback Verification**:
```bash
# After rollback, verify old structure intact
pytest tests/test_current_structure.py

# Verify imports work with old paths
pytest tests/test_imports_old_paths.py
```

**Estimated Rollback Time**: < 10 minutes

---

## Success Criteria (Post-Migration Verification)

### Structural Success
- [ ] cortex/ root created with 8 top-level modules
- [ ] All ~170 files migrated successfully
- [ ] Old directories (cortex_brain/, src/) removed
- [ ] All checksums verified

### Import Success
- [ ] All imports updated successfully
- [ ] 0 broken imports detected
- [ ] 0 tier isolation violations
- [ ] 0 circular dependencies

### Testing Success
- [ ] All 200+ tests pass (100% pass rate)
- [ ] Import resolution tests pass on all platforms
- [ ] Cross-platform path tests pass
- [ ] Performance benchmarks within limits

### Documentation Success
- [ ] FOLDER_STRUCTURE_DESIGN.md updated
- [ ] Import patterns documented
- [ ] Platform considerations documented
- [ ] Getting started guide updated

---

## Timeline & Milestones

| Date | Milestone | Status |
|------|-----------|--------|
| Day 1-2 | Phase 1: Prep & Analysis | PLANNED |
| Day 3 | Phase 2: Structural Migration | PLANNED |
| Day 4-5 | Phase 3: Import Updates | PLANNED |
| Day 5-6 | Phase 4: Verification & Deploy | PLANNED |
| Day 6 | **PHASE-02-CODEBASE-COHERENCE LOCKED** | PLANNED |

---

## Related Documents

- **FOLDER_STRUCTURE_DESIGN.md**: Target structure & rationale
- **AC-AR-010-02**: Automated migration script implementation
- **AC-AR-010-03**: Import path updates & validation
- **tests/test_ac_ar_010_01_design.py**: Design validation tests

---

**Status**: MIGRATION PLAN COMPLETE (AC-AR-010-01 Phase 2)  
**Next**: Implement AC-AR-010-02 (migration script)  
**Then**: Implement AC-AR-010-03 (import updates)  
**Finally**: Execute migration (all 3 ACs complete)
