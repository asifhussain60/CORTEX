# Sprint 8 Plan: Low-Hanging Fruit Sweep

**Author:** Asif Hussain  
**Created:** December 2, 2025  
**Sprint Goal:** Migrate 4 small orchestrators (774→541 lines, 30% reduction)  
**Estimated Duration:** 2-3 hours

---

## 🎯 Sprint 8 Objectives

Maintain Sprint 7 momentum by targeting low-complexity orchestrators with clear operation boundaries. Rapid migration to reduce from 14 to 10 orchestrators.

**Lesson from Sprint 7:** Always check for existing utilities first to avoid duplicate work!

---

## 📊 Sprint 8 Targets

### Original Target (Pre-Investigation)

| Orchestrator | Lines | Complexity | Risk | Existing Utility? |
|--------------|-------|------------|------|-------------------|
| setup_orchestrator.py | 249 | LOW | LOW | ❓ |
| deploy_orchestrator.py | 207 | LOW | LOW | ❓ |
| cleanup_strategy.py | 172 | LOW | LOW | ❓ |
| rollback_command_parser.py | 146 | LOW | LOW | ❓ |
| **TOTAL** | **774** | - | - | - |

### After Pre-Investigation

| Orchestrator | Lines | Status | Action | New Utility Lines |
|--------------|-------|--------|--------|-------------------|
| **rollback_command_parser.py** | 146 | ✅ **Already migrated** | Deprecate only | N/A (469-line utility exists) |
| setup_orchestrator.py | 249 | 🔄 **Migrate** | Create utility | ~174 (30% reduction) |
| deploy_orchestrator.py | 207 | 🔄 **Migrate** | Create utility | ~145 (30% reduction) |
| cleanup_strategy.py | 172 | 🔄 **Migrate** | Create utility | ~120 (30% reduction) |
| **ADJUSTED TOTAL** | **628** | - | - | **439** |

**Discovery Bonus:** Rollback utility already exists at 469 lines (comprehensive with checkpoint validation, git reset, safety checks, dry-run, confirmation prompts)

**Adjusted Sprint 8 Impact:**
- **Original:** 774→541 lines (233 removed, 30%)
- **Adjusted:** 628→439 lines (189 removed, 30%) + 146 lines deprecated
- **Total Removed:** **335 lines** (146 rollback deprecation + 189 new migrations)

---

## 🔍 Orchestrator Analysis

### 1. Rollback Command Parser (146 lines) - ✅ ALREADY MIGRATED

**Status:** Utility exists at `src/operations/modules/git/rollback_utility.py` (469 lines)

**Existing Utility Features:**
- ✅ Checkpoint validation before rollback
- ✅ Git reset with safety checks
- ✅ Uncommitted changes detection
- ✅ Dry-run mode for preview
- ✅ User confirmation prompts
- ✅ Force mode (bypass safety)
- ✅ Comprehensive error handling

**Action:** Deprecate `rollback_command_parser.py` immediately (redundant)

**Time Saved:** ~20 minutes (no implementation needed)

---

### 2. Setup Orchestrator (249 lines)

**Purpose:** Shared CORTEX tooling environment management

**Key Operations:**
1. `create_shared_environment()` - Create ~/.cortex/venv/ virtual environment
2. `install_cortex_tooling()` - Install pytest, pyyaml, requests, playwright
3. `link_project_to_shared_environment()` - Update cortex.config.json with venv reference
4. `install_project_dependencies()` - Install project-specific deps separately
5. `get_python_executable()` - Get shared venv Python path
6. `get_environment_variables()` - Get PYTHONPATH with project deps

**Complexity:** LOW
- Clear operation boundaries
- No Tier 0/1/2 dependencies
- Simple file operations + subprocess calls

**Migration Strategy:**
- Create `src/operations/modules/setup/setup_utility.py`
- 6 operations (map 1:1 with orchestrator methods)
- Target: 174 lines (30% reduction from 249)
- Preserve shared venv architecture (10x speedup)

**Risk:** LOW (straightforward utility conversion)

---

### 3. Deploy Orchestrator (207 lines)

**Purpose:** Production deployment with architecture sync

**Key Operations:**
1. `execute()` - Main deployment workflow orchestration
2. `_validate_pre_deployment()` - Run tests, lint, coverage checks
3. `_sync_architecture_docs()` - Update ARCHITECTURE.md (DocSyncHook)
4. `_bump_version()` - Increment version in VERSION file
5. `_deploy_to_production()` - Deploy to production branch

**Complexity:** LOW
- Simple workflow orchestration
- Calls other utilities (DocSyncHook)
- Minimal business logic

**Migration Strategy:**
- Create `src/operations/modules/deploy/deploy_utility.py`
- 5 operations (map 1:1 with orchestrator methods)
- Target: 145 lines (30% reduction from 207)
- Preserve DocSyncHook integration

**Risk:** LOW (utility wraps existing hooks)

---

### 4. Cleanup Strategy (172 lines)

**Purpose:** Phase 8 cleanup with profile-based strategies

**Key Components:**
1. `CleanupStrategy` (base class) - Abstract strategy pattern
2. `QuickCleanupStrategy` - Temp/cache only
3. `StandardCleanupStrategy` - Temp/cache/old backups (>30 days)
4. `ComprehensiveCleanupStrategy` - Deep cleanup (all obsolete files)
5. `get_cleanup_strategy()` - Factory function

**Complexity:** LOW
- Clean strategy pattern implementation
- No external dependencies
- File detection logic only

**Migration Strategy:**
- Create `src/operations/modules/cleanup/cleanup_utility.py`
- 5 operations:
  1. `get_cleanup_strategy()` - Factory (keep name)
  2. `detect_quick_cleanup_files()` - Quick strategy logic
  3. `detect_standard_cleanup_files()` - Standard strategy logic
  4. `detect_comprehensive_cleanup_files()` - Comprehensive strategy logic
  5. `execute_cleanup()` - Remove files safely
- Target: 120 lines (30% reduction from 172)
- Flatten strategy classes into functions

**Risk:** LOW (strategy pattern → functional approach)

---

## 📋 Sprint 8 Implementation Plan

### Phase 1: Immediate Deprecation (5 minutes)

**Task:** Deprecate rollback_command_parser.py (already migrated)

```bash
cd src/orchestrators
mv rollback_command_parser.py rollback_command_parser.py.bak
git add rollback_command_parser.py.bak
git commit -m "chore: deprecate rollback_command_parser (utility exists at 469 lines)"
git push
```

**Impact:** 146 lines removed, 13 orchestrators remaining

---

### Phase 2: Setup Orchestrator Migration (45 minutes)

**Task:** Create `src/operations/modules/setup/setup_utility.py`

**Operations:**
1. `create_shared_venv(home_dir: Path) -> Dict[str, Any]`
2. `install_cortex_tooling(venv_path: Path) -> Dict[str, Any]`
3. `link_project(project_dir: Path, venv_path: Path) -> Dict[str, Any]`
4. `install_project_deps(project_dir: Path, python_path: Path) -> Dict[str, Any]`
5. `get_python_path(venv_path: Path) -> Path`
6. `get_project_env_vars(project_dir: Path) -> Dict[str, str]`

**Target:** 174 lines (vs 249 original = 75 lines removed, 30% reduction)

**Testing:**
```bash
python3 -m src.operations.modules.setup.setup_utility
# Expected: ✅ All 6 operations tested, <0.01s execution
```

---

### Phase 3: Deploy Orchestrator Migration (40 minutes)

**Task:** Create `src/operations/modules/deploy/deploy_utility.py`

**Operations:**
1. `execute_deployment(cortex_root: Path, dry_run: bool) -> Dict[str, Any]`
2. `validate_pre_deployment(cortex_root: Path) -> Dict[str, Any]`
3. `sync_architecture_docs(cortex_root: Path, dry_run: bool) -> Dict[str, Any]`
4. `bump_version(cortex_root: Path, dry_run: bool) -> Dict[str, Any]`
5. `deploy_to_production(cortex_root: Path, dry_run: bool) -> Dict[str, Any]`

**Target:** 145 lines (vs 207 original = 62 lines removed, 30% reduction)

**Testing:**
```bash
python3 -m src.operations.modules.deploy.deploy_utility
# Expected: ✅ All 5 operations tested (dry-run mode), <0.01s execution
```

---

### Phase 4: Cleanup Strategy Migration (35 minutes)

**Task:** Create `src/operations/modules/cleanup/cleanup_utility.py`

**Operations:**
1. `get_cleanup_strategy(profile: str, brain_path: Path) -> str`
2. `detect_quick_files(brain_path: Path) -> List[Path]`
3. `detect_standard_files(brain_path: Path, cutoff_days: int) -> List[Path]`
4. `detect_comprehensive_files(brain_path: Path, cutoff_days: int) -> List[Path]`
5. `execute_cleanup(files: List[Path], dry_run: bool) -> Dict[str, Any]`

**Target:** 120 lines (vs 172 original = 52 lines removed, 30% reduction)

**Testing:**
```bash
python3 -m src.operations.modules.cleanup.cleanup_utility
# Expected: ✅ All 5 operations tested (dry-run mode), <0.01s execution
```

---

### Phase 5: Commit & Validate (15 minutes)

**Tasks:**
1. Deprecate 3 orchestrators (setup, deploy, cleanup_strategy)
2. Git commit + push
3. Verify 10 orchestrators remaining
4. Run system alignment (expect 8/8 HEALTHY)

**Commands:**
```bash
cd src/orchestrators
mv setup_orchestrator.py setup_orchestrator.py.bak
mv deploy_orchestrator.py deploy_orchestrator.py.bak
mv cleanup_strategy.py cleanup_strategy.py.bak

git add src/operations/modules/{setup,deploy,cleanup}/*.py
git add src/orchestrators/*.bak
git commit -m "feat: Sprint 8 - Setup, Deploy, Cleanup migrations (335 lines removed)"
git push

ls src/orchestrators/*.py | wc -l  # Expect: 10
python3 -m src.operations.align  # Expect: 8/8 HEALTHY
```

---

### Phase 6: Sprint 8 Completion Report (10 minutes)

**Task:** Create `cortex-brain/documents/reports/sprint-8-completion-report.md`

**Content:**
- Sprint 8 summary: 4 orchestrators, 335 lines removed (146 rollback + 189 migrations)
- Discovery bonus: Rollback utility already existed (469 lines)
- Cumulative progress: 22 migrations, ~6,245 lines removed (Sprints 1-8)
- 10 orchestrators remaining (67% reduction from baseline 30)
- Sprint 9 recommendations

---

## 📊 Sprint 8 Success Metrics

### Target Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Lines Removed** | 335 | 146 deprecation + 189 new migrations |
| **Reduction %** | 43% | (774 original → 439 new) |
| **Orchestrators** | 14 → 10 | 4 migrated (29% sprint reduction) |
| **Duration** | 2-3 hours | ~140 minutes estimated |
| **System Health** | 8/8 HEALTHY | Post-migration alignment |
| **Performance** | <0.01s | All new utilities sub-millisecond |

### Cumulative Metrics (Post-Sprint 8)

| Metric | Sprint 1 Baseline | Post-Sprint 8 | Change |
|--------|-------------------|---------------|--------|
| **Orchestrators** | 30 | 10 | -20 (67% reduction) |
| **Lines Removed** | 0 | ~6,245 | +6,245 |
| **Migrations** | 0 | 22 | +22 |
| **Sprints** | 0 | 8 | +8 |

---

## 🎯 Sprint 8 Risk Assessment

### Overall Risk: LOW

**Low-Risk Factors:**
- ✅ All 4 targets are low-complexity orchestrators
- ✅ Clear operation boundaries (no tangled dependencies)
- ✅ Rollback utility already exists (1/4 done instantly)
- ✅ Simple file operations + subprocess calls
- ✅ No Tier 0/1/2/3 database modifications
- ✅ Straightforward testing (dry-run modes available)

**Mitigation Strategies:**
- Sprint 7 lesson applied: Check for existing utilities first
- Incremental commits (rollback deprecation → setup → deploy → cleanup)
- Comprehensive testing before deprecation
- System alignment validation between phases

---

## 🚀 Sprint 9 Preview (Post-Sprint 8)

### Remaining 10 Orchestrators

| Orchestrator | Lines | Complexity | Migration Risk |
|--------------|-------|------------|----------------|
| swagger_entry_point_orchestrator.py | 1,572 | VERY HIGH | HIGH |
| setup_epm_orchestrator.py | 1,123 | HIGH | MEDIUM |
| upgrade_orchestrator.py | 1,115 | HIGH | HIGH |
| ux_enhancement_orchestrator.py | 681 | MEDIUM | MEDIUM |
| master_setup_orchestrator.py | 666 | MEDIUM | MEDIUM |
| brain_init_orchestrator.py | 559 | MEDIUM | HIGH |
| unified_entry_point_orchestrator.py | 544 | HIGH | HIGH |
| realignment_orchestrator.py | 401 | MEDIUM | MEDIUM |
| base_incremental_orchestrator.py | 421 | LOW | LOW |
| __init__.py | 14 | N/A | N/A |

**Sprint 9 Option A (RECOMMENDED): UX + Realignment Duo**
- ux_enhancement_orchestrator.py (681 lines)
- realignment_orchestrator.py (401 lines)
- Total: 1,082→757 lines (325 removed, 30%)
- Risk: MEDIUM
- Duration: 3-4 hours

**Sprint 9 Option B: Base Incremental Solo**
- base_incremental_orchestrator.py (421 lines)
- Total: 421→295 lines (126 removed, 30%)
- Risk: LOW
- Duration: 1.5-2 hours

---

## 📝 Sprint 8 Execution Checklist

**Pre-Migration:**
- [x] Check for existing utilities (found rollback_utility.py at 469 lines)
- [x] Analyze all 4 orchestrators (setup, deploy, cleanup, rollback)
- [x] Create Sprint 8 plan with adjusted targets

**Phase 1: Rollback Deprecation**
- [ ] Deprecate rollback_command_parser.py (.bak)
- [ ] Commit + push
- [ ] Verify 13 orchestrators remaining

**Phase 2: Setup Migration**
- [ ] Create setup_utility.py (174 lines target)
- [ ] Test all 6 operations
- [ ] Verify <0.01s performance

**Phase 3: Deploy Migration**
- [ ] Create deploy_utility.py (145 lines target)
- [ ] Test all 5 operations (dry-run)
- [ ] Verify <0.01s performance

**Phase 4: Cleanup Migration**
- [ ] Create cleanup_utility.py (120 lines target)
- [ ] Test all 5 operations (dry-run)
- [ ] Verify <0.01s performance

**Phase 5: Final Deprecation**
- [ ] Deprecate setup, deploy, cleanup_strategy (.bak)
- [ ] Commit + push
- [ ] Verify 10 orchestrators remaining
- [ ] Run system alignment (8/8 HEALTHY)

**Phase 6: Reporting**
- [ ] Create sprint-8-completion-report.md
- [ ] Document discovery bonus (rollback utility)
- [ ] Provide Sprint 9 recommendations

---

**Plan Created:** December 2, 2025 19:30 UTC  
**Ready to Execute:** YES  
**Estimated Completion:** 2-3 hours from start
