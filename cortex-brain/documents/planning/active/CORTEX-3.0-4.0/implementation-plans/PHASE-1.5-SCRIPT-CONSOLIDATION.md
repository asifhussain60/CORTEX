# Phase 1.5: Script Consolidation into CORTEX Toolkit

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 17, 2025  
**Timeline:** Week 3 (parallel with Phase 1 foundation)  
**Status:** 📋 PLANNED

---

## 🎯 Executive Summary

Consolidate 418 scattered scripts (115 PowerShell + 350 Python, minus 47 already in toolkit) from `scripts/` into well-organized CORTEX Toolkit structure. This phase runs in parallel with Phase 1 foundation work and must complete before Phase 3 orchestrator migration to prevent duplication.

**Current State:**
- ✅ `cortex-toolkit/` structure exists with 47 organized scripts
- ❌ 115 PowerShell scripts scattered in `scripts/` and subdirectories
- ❌ 350 Python scripts in `scripts/` (many duplicates, legacy, or archived)
- ❌ No clear ownership or categorization for 90% of scripts

**Target State:**
- ✅ All production scripts in `cortex-toolkit/` with proper categorization
- ✅ Legacy scripts archived with documentation
- ✅ Duplicate scripts consolidated with migration mapping
- ✅ All scripts have README.md and type hints
- ✅ Test coverage for 85%+ of consolidated scripts

**Risk Level:** 🟡 MEDIUM (high script count, but well-defined process)

---

## 📊 Script Inventory Analysis

### Current Distribution

| Location | PowerShell | Python | Total | Status |
|----------|------------|--------|-------|--------|
| `scripts/` (root) | ~30 | ~150 | 180 | Mixed (prod + legacy) |
| `scripts/cli_wrappers/` | 0 | 8 | 8 | ✅ Production (move to toolkit) |
| `scripts/admin/` | ~5 | ~20 | 25 | ✅ Production (move to toolkit) |
| `scripts/operations/` | 0 | ~30 | 30 | ✅ Production (move to toolkit) |
| `scripts/utilities/` | 0 | ~40 | 40 | Mixed (assess individually) |
| `scripts/_archive/` | ~60 | ~80 | 140 | ❌ Legacy (keep in archive) |
| `scripts/temp/` | ~10 | ~15 | 25 | ❌ Temporary (delete after review) |
| `scripts/completions/` | ~5 | 0 | 5 | ✅ Shell integration (keep) |
| **Subtotal** | **110** | **343** | **453** | |
| `cortex-toolkit/` | 3 | 44 | 47 | ✅ Already organized |
| **TOTAL** | **113** | **387** | **500** | |

**Action Required:** Consolidate ~406 scripts (453 - 47 already in toolkit)

---

## 🗂️ Categorization Strategy

### 1. Production Scripts (Migrate to Toolkit) - ~180 scripts

**Criteria:**
- ✅ Used in CORTEX 3.0 workflows
- ✅ No deprecated dependencies
- ✅ Has clear purpose/documentation
- ✅ Not a duplicate

**Target Categories in Toolkit:**

| Toolkit Category | Script Count | Examples |
|------------------|--------------|----------|
| `core/brain/` | 15 | `align.py`, `cleanup.py`, `healthcheck.py`, `optimize.py` |
| `core/operations/` | 20 | `deploy.py`, `review.py`, `sanitize.py`, `refine.py` |
| `core/planning/` | 12 | `ado_manager.py`, `plan_generator.py`, `planning_file_manager.py` |
| `core/utilities/` | 25 | `version_manager.py`, `measure_prompt_tokens.py`, database utils |
| `analytics/profiling/` | 8 | `profile_performance.py`, `profile_startup.py`, benchmarking |
| `analytics/metrics/` | 10 | `collect_dashboard_data.py`, `monitor_brain_health.py` |
| `analytics/visualization/` | 12 | `dependency_graph_generator.py`, `generate_uml_standalone.py` |
| `documentation/` | 15 | `generate_docs_from_code.py`, `regenerate_prompts.py` |
| `testing/` | 18 | `validate_deployment.py`, `verify_no_mocks.py`, test generators |
| `migration/` | 10 | `schema_migrator.py`, conversation import/export |
| `maintenance/` | 20 | `cleanup_temp_files.py`, `detect_duplicates.py`, `master_cleanup.py` |
| `cli/wrappers/` | 15 | All CLI wrappers for system operations |
| **TOTAL** | **180** | |

### 2. Legacy Scripts (Archive) - ~140 scripts

**Criteria:**
- ❌ Not used in CORTEX 3.0
- ❌ Has deprecated dependencies
- ❌ Superseded by newer implementation
- ❌ Part of old KDS/Brain architecture

**Action:** Move to `archive/scripts-v3.9.0/` with migration notes

**Categories:**
- `kds-legacy/` - Old KDS brain scripts (~80 scripts)
- `brain-v2/` - Old tier architecture (~30 scripts)
- `dashboard-v1/` - Old dashboard generation (~20 scripts)
- `misc/` - Unclassified legacy (~10 scripts)

### 3. Temporary Scripts (Delete) - ~25 scripts

**Criteria:**
- ❌ In `scripts/temp/` directory
- ❌ No production usage
- ❌ Experimental/one-off scripts

**Action:** Review individually, keep documentation if valuable, delete scripts

### 4. Duplicate Scripts (Consolidate) - ~61 scripts

**Criteria:**
- ❌ Multiple versions of same functionality
- ❌ Different names, same logic

**Examples:**
- `optimize.py`, `optimize_cortex_orchestrator.py`, `run_optimize.py` → `cortex-toolkit/core/brain/optimize.py`
- `cleanup*.py` (5 variants) → `cortex-toolkit/core/brain/cleanup.py`
- `align.py`, `run_alignment.py` → `cortex-toolkit/core/brain/align.py`

**Action:** Create consolidated version, document migration mapping

---

## 🚀 Implementation Phases

### Sub-Phase 1: Assessment & Planning (Days 1-2)

**Goal:** Classify all 453 scripts into categories

**Tasks:**
1. **Automated Analysis:**
   ```python
   # Script: scripts/analyze_script_inventory.py
   # Output: cortex-brain/documents/planning/active/CORTEX-3.0-4.0/SCRIPT-INVENTORY-REPORT.md
   
   - Scan all scripts in scripts/ recursively
   - Detect imports, dependencies, last modified date
   - Classify by: production/legacy/temp/duplicate
   - Generate migration matrix
   ```

2. **Manual Review:**
   - Review top 50 most-used scripts (by git history)
   - Flag critical infrastructure scripts
   - Document business logic for complex scripts

3. **Create Migration Mapping:**
   ```yaml
   # cortex-toolkit/migration-mapping.yaml
   migrations:
     - source: scripts/align.py
       target: cortex-toolkit/core/brain/align.py
       status: already_migrated
       notes: "CLI wrapper exists"
     
     - source: scripts/admin/deploy_cortex.py
       target: cortex-toolkit/core/operations/deploy.py
       status: needs_consolidation
       duplicates:
         - scripts/deploy_cortex_simple.py
         - scripts/operations/deploy_orchestrator.py
       notes: "Merge 3 variants into single deploy.py"
   ```

**Deliverables:**
- ✅ `SCRIPT-INVENTORY-REPORT.md` (automated analysis)
- ✅ `migration-mapping.yaml` (consolidation plan)
- ✅ `high-priority-scripts.txt` (critical path items)

---

### Sub-Phase 2: Production Script Migration (Days 3-7)

**Goal:** Migrate 180 production scripts to toolkit with tests

**Priority Order:**
1. **Tier 1 - Critical Infrastructure (Days 3-4):** 40 scripts
   - CLI wrappers (already done, validate)
   - Brain operations (align, cleanup, healthcheck, optimize)
   - Core utilities (version manager, config, logging)
   - System operations (deploy, review, sanitize)

2. **Tier 2 - High-Use Utilities (Days 5-6):** 60 scripts
   - Analytics & metrics collectors
   - Documentation generators
   - Testing & validation scripts
   - Migration tools

3. **Tier 3 - Specialized Tools (Day 7):** 80 scripts
   - Visualization generators
   - Profiling & benchmarking
   - Maintenance scripts
   - Admin utilities

**Migration Process (Per Script):**

```python
# Template: scripts/migrate_script_to_toolkit.py

def migrate_script(source_path: Path, target_category: str) -> MigrationResult:
    """
    Migrate a single script to CORTEX Toolkit
    
    Steps:
    1. Copy source to target location in toolkit
    2. Add type hints if missing
    3. Add/update docstrings
    4. Create README.md if first in category
    5. Add tests in tests/ subfolder
    6. Update toolkit-manifest.yaml
    7. Run validation (imports, type hints, tests)
    8. Archive original with forwarding stub
    """
    
    # Step 1: Copy with enhancements
    enhanced_code = enhance_script(source_path)
    target_path = TOOLKIT_ROOT / target_category / source_path.name
    target_path.write_text(enhanced_code)
    
    # Step 2: Generate tests
    test_code = generate_tests(enhanced_code, source_path.name)
    test_path = target_path.parent / "tests" / f"test_{source_path.stem}.py"
    test_path.write_text(test_code)
    
    # Step 3: Update manifest
    update_manifest(target_path, metadata={
        "category": target_category,
        "migrated_from": str(source_path),
        "migration_date": datetime.now().isoformat(),
        "status": "production"
    })
    
    # Step 4: Validate
    validation = validate_migration(target_path, test_path)
    
    # Step 5: Archive original
    if validation.passed:
        archive_with_forwarding_stub(source_path, target_path)
    
    return validation
```

**Quality Gates (Per Script):**
- ✅ Type hints on all public functions
- ✅ Docstrings with Args/Returns/Raises
- ✅ README.md in category folder
- ✅ Unit tests with 70%+ coverage
- ✅ Passes `ruff check` and `mypy`
- ✅ Manifest entry created

**Automation:**
```bash
# Migrate all scripts in a category
python scripts/batch_migrate_scripts.py \
  --category core/brain \
  --source-dir scripts/admin \
  --dry-run

# Review migration plan
cat cortex-toolkit/migration-report.yaml

# Execute migration
python scripts/batch_migrate_scripts.py \
  --category core/brain \
  --source-dir scripts/admin \
  --execute
```

---

### Sub-Phase 3: Duplicate Consolidation (Days 8-10)

**Goal:** Consolidate 61 duplicate scripts into single canonical versions

**Process:**

1. **Identify Duplicates:**
   ```python
   # Script: scripts/detect_duplicate_functionality.py
   
   # Strategies:
   - AST similarity analysis (>80% code similarity)
   - Function signature matching
   - Import pattern matching
   - Git history analysis (common ancestor)
   ```

2. **Create Consolidated Version:**
   ```python
   # For each duplicate set:
   # 1. Compare all versions
   # 2. Select "best" version (most features, cleanest code)
   # 3. Merge unique features from others
   # 4. Add feature flags if needed for backward compatibility
   # 5. Document consolidated functionality
   ```

3. **Create Forwarding Stubs:**
   ```python
   # scripts/align.py (archived)
   """
   DEPRECATED: This script has been migrated to CORTEX Toolkit.
   
   Forwarding stub - DO NOT USE directly.
   
   New location: cortex-toolkit/core/brain/align.py
   Migration date: 2025-12-17
   
   This file will be removed in CORTEX 4.0.
   """
   import sys
   from pathlib import Path
   
   # Forward to toolkit version
   toolkit_path = Path(__file__).parent.parent / "cortex-toolkit"
   sys.path.insert(0, str(toolkit_path))
   
   from core.brain.align import main as toolkit_main
   
   if __name__ == "__main__":
       print("⚠️  WARNING: Using deprecated script location")
       print("   Migrate to: python cortex-toolkit/core/brain/align.py")
       toolkit_main()
   ```

**Duplicate Consolidation Matrix:**

| Functionality | Duplicates Found | Consolidated To | Features Merged |
|---------------|------------------|-----------------|-----------------|
| **Align** | 3 | `core/brain/align.py` | Check-only mode, verbose logging, dry-run |
| **Cleanup** | 5 | `core/brain/cleanup.py` | Holistic mode, user mode, temp files, selective |
| **Optimize** | 4 | `core/brain/optimize.py` | CORTEX mode, system mode, vacuum, cache clear |
| **Deploy** | 3 | `core/operations/deploy.py` | Simple mode, full mode, publish integration |
| **Healthcheck** | 2 | `core/brain/healthcheck.py` | Quick mode, full diagnostics |
| **Documentation** | 6 | `documentation/regenerate_prompts.py` | All prompts, specific, architecture, enhanced |
| **Validation** | 4 | `testing/validate_deployment.py` | Pre-deploy, post-deploy, gates, direct |
| **Metrics** | 5 | `analytics/metrics/collect_dashboard_data.py` | Multiple collector variants |
| **Import** | 4 | `migration/import_conversation.py` | Copilot, plan, generic conversation import |
| **Profiling** | 3 | `analytics/profiling/profile_performance.py` | Runtime, startup, memory |
| **Others** | 22 | Various | Miscellaneous duplicates |
| **TOTAL** | **61** | | |

---

### Sub-Phase 4: Legacy Archival (Days 11-12)

**Goal:** Archive 140 legacy scripts with proper documentation

**Process:**

1. **Create Archive Structure:**
   ```
   archive/scripts-v3.9.0/
   ├── README.md                    # Migration guide
   ├── ARCHIVED-SCRIPTS-INDEX.md    # Complete inventory
   ├── kds-legacy/                  # KDS brain era scripts
   │   ├── README.md
   │   └── *.ps1, *.py (80 scripts)
   ├── brain-v2/                    # Old tier architecture
   │   ├── README.md
   │   └── *.py (30 scripts)
   ├── dashboard-v1/                # Old dashboard generation
   │   ├── README.md
   │   └── *.py (20 scripts)
   └── misc/                        # Unclassified legacy
       ├── README.md
       └── *.py (10 scripts)
   ```

2. **Document Each Script:**
   ```markdown
   # archive/scripts-v3.9.0/ARCHIVED-SCRIPTS-INDEX.md
   
   ## kds-legacy/verify-system-health.ps1
   
   **Original Purpose:** System health validation for KDS Brain architecture
   
   **Deprecated Reason:** KDS Brain architecture replaced by CORTEX 4-tier brain
   
   **Replacement:** `cortex-toolkit/core/brain/healthcheck.py`
   
   **Migration Notes:**
   - Old: PowerShell-based, KDS-specific checks
   - New: Python-based, CORTEX 4-tier brain checks
   - Key differences: New version checks all 4 tiers, SQLite schema validation
   
   **Last Used:** CORTEX 3.8.1 (November 2025)
   
   **Preserved Features:**
   - System health scoring (preserved)
   - Tier integrity checks (adapted for new brain)
   - Quick check mode (preserved)
   ```

3. **Create Migration Guide:**
   ```markdown
   # archive/scripts-v3.9.0/README.md
   
   # CORTEX 3.9.0 Script Archive
   
   This directory contains scripts from CORTEX 3.0-3.9.0 that are no longer
   used in CORTEX 4.0 but preserved for historical reference.
   
   ## Quick Reference
   
   | Old Script | New Location | Notes |
   |------------|--------------|-------|
   | `verify-system-health.ps1` | `cortex-toolkit/core/brain/healthcheck.py` | Rewritten for 4-tier brain |
   | `optimize_cortex_orchestrator.py` | `cortex-toolkit/core/brain/optimize.py` | Consolidated |
   | ... | ... | ... |
   
   ## Why These Scripts Were Archived
   
   - **KDS Legacy (80 scripts):** KDS Brain architecture deprecated
   - **Brain v2 (30 scripts):** Old tier architecture replaced
   - **Dashboard v1 (20 scripts):** New dashboard system with MCP
   - **Misc (10 scripts):** Superseded or experimental
   ```

---

### Sub-Phase 5: PowerShell Script Modernization (Days 13-14)

**Goal:** Modernize 115 PowerShell scripts with consistent patterns

**Challenges:**
- PowerShell scripts scattered across multiple subdirectories
- Inconsistent error handling
- No unified logging
- Mixed coding styles

**Modernization Strategy:**

1. **Create PowerShell Toolkit Module:**
   ```powershell
   # cortex-toolkit/shared/CortexToolkit.psm1
   
   function Invoke-CortexOperation {
       [CmdletBinding()]
       param(
           [Parameter(Mandatory)]
           [string]$Operation,
           
           [hashtable]$Parameters = @{},
           
           [switch]$DryRun,
           [switch]$Verbose
       )
       
       # Unified error handling
       $ErrorActionPreference = 'Stop'
       
       try {
           # Call Python backend via toolkit registry
           $result = python cortex-toolkit/shared/toolkit_registry.py invoke $Operation @Parameters
           
           if ($LASTEXITCODE -ne 0) {
               throw "Operation failed: $Operation"
           }
           
           return $result
       }
       catch {
           Write-Error "CORTEX Operation Error: $_"
           throw
       }
   }
   
   # Export functions
   Export-ModuleMember -Function Invoke-CortexOperation
   ```

2. **Migrate PowerShell Scripts:**
   - Convert to Python where possible (data processing, orchestration)
   - Keep PowerShell for Windows-specific tasks (registry, WMI)
   - Use PowerShell as thin wrapper over Python toolkit

3. **PowerShell Script Categories:**
   
   | Keep as PowerShell | Convert to Python | Rationale |
   |--------------------|-------------------|-----------|
   | `setup_git_exclude.ps1` | - | Git hooks, shell integration |
   | `launch_dashboard.ps1` | - | Windows service, browser launch |
   | `set-utf8-env.ps1` | - | Environment setup |
   | Shell completions | - | Shell integration |
   | - | Most admin scripts | Cross-platform, testability |
   | - | Data processing | Better libraries in Python |
   | - | Orchestration | Integration with Python orchestrators |

**Target Distribution:**
- **Keep PowerShell:** 25 scripts (shell integration, Windows-specific)
- **Convert to Python:** 90 scripts (cross-platform logic)

---

### Sub-Phase 6: Testing & Validation (Days 15-17)

**Goal:** Ensure 85%+ test coverage for all consolidated scripts

**Testing Strategy:**

1. **Unit Tests (Per Script):**
   ```python
   # cortex-toolkit/core/brain/tests/test_align.py
   
   import pytest
   from cortex_toolkit.core.brain.align import AlignmentChecker
   
   def test_alignment_check_basic():
       checker = AlignmentChecker(repo_path="/test/repo")
       result = checker.check()
       assert result.is_valid
   
   def test_alignment_check_with_errors():
       checker = AlignmentChecker(repo_path="/test/repo")
       result = checker.check()
       assert len(result.errors) > 0
   
   def test_alignment_auto_fix():
       checker = AlignmentChecker(repo_path="/test/repo")
       result = checker.fix()
       assert result.fixed_count > 0
   ```

2. **Integration Tests:**
   ```python
   # cortex-toolkit/tests/integration/test_toolkit_workflows.py
   
   def test_full_maintenance_workflow():
       """Test: align → cleanup → optimize → healthcheck"""
       # Simulate full workflow
       results = []
       results.append(run_toolkit_operation("align"))
       results.append(run_toolkit_operation("cleanup"))
       results.append(run_toolkit_operation("optimize"))
       results.append(run_toolkit_operation("healthcheck"))
       
       # All operations should succeed
       assert all(r.success for r in results)
   ```

3. **End-to-End Tests:**
   ```python
   # cortex-toolkit/tests/e2e/test_toolkit_registry.py
   
   def test_registry_list_all_tools():
       result = subprocess.run([
           "python", "cortex-toolkit/shared/toolkit_registry.py", "list"
       ], capture_output=True)
       
       assert result.returncode == 0
       assert "align" in result.stdout.decode()
       assert "cleanup" in result.stdout.decode()
   ```

4. **Coverage Report:**
   ```bash
   # Generate coverage report
   pytest cortex-toolkit/tests/ \
     --cov=cortex-toolkit \
     --cov-report=html \
     --cov-report=term-missing
   
   # Target: 85%+ coverage across all modules
   ```

**Quality Gates:**
- ✅ 85%+ test coverage across toolkit
- ✅ All CLI wrappers have integration tests
- ✅ All core operations have unit tests
- ✅ No failing tests
- ✅ Performance benchmarks pass (no >20% regression)

---

### Sub-Phase 7: Documentation & Finalization (Days 18-19)

**Goal:** Complete documentation for CORTEX Toolkit

**Deliverables:**

1. **Update README.md:**
   ```markdown
   # CORTEX Toolkit v2.0
   
   **Consolidated from 418 scripts** into 180 production tools + 47 existing
   
   ## What's New in v2.0
   
   - ✅ 180 production scripts migrated and tested
   - ✅ 61 duplicates consolidated
   - ✅ 140 legacy scripts archived
   - ✅ 85%+ test coverage
   - ✅ Unified CLI interface
   - ✅ PowerShell module for Windows integration
   ```

2. **Create Category README.md:**
   - One README per toolkit category
   - Document all tools in category
   - Usage examples
   - Configuration options

3. **Migration Guide:**
   ```markdown
   # cortex-toolkit/MIGRATION-GUIDE-v3-to-v4.md
   
   ## Script Location Changes
   
   | Old Path | New Path | Breaking Changes |
   |----------|----------|------------------|
   | `scripts/align.py` | `cortex-toolkit/core/brain/align.py` | CLI flags unchanged |
   | ... | ... | ... |
   ```

4. **Update Toolkit Manifest:**
   ```yaml
   # cortex-toolkit/toolkit-manifest.yaml
   
   version: "2.0.0"
   consolidated_from: "v3.9.0"
   migration_date: "2025-12-17"
   
   statistics:
     scripts_migrated: 180
     duplicates_consolidated: 61
     legacy_archived: 140
     test_coverage: 87%
     categories: 12
   ```

---

## 📊 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| **Scripts Migrated** | 180 | Count in toolkit-manifest.yaml |
| **Duplicates Consolidated** | 61 | Review migration-mapping.yaml |
| **Legacy Archived** | 140 | Count in archive/scripts-v3.9.0/ |
| **Test Coverage** | 85%+ | `pytest --cov` report |
| **No Regressions** | 100% | All existing workflows still work |
| **Documentation Complete** | 100% | All categories have README.md |
| **Manifest Updated** | 100% | toolkit-manifest.yaml reflects all tools |

---

## 🚨 Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Breaking Changes** | 🟡 MEDIUM | 🔴 HIGH | Forwarding stubs in old locations for 1 release |
| **Missed Dependencies** | 🟢 LOW | 🟡 MEDIUM | Automated import analysis before migration |
| **Test Coverage Gaps** | 🟡 MEDIUM | 🟡 MEDIUM | Prioritize critical path scripts for testing |
| **PowerShell Conversion Errors** | 🟡 MEDIUM | 🟡 MEDIUM | Keep PowerShell for Windows-specific tasks |
| **Performance Regression** | 🟢 LOW | 🟡 MEDIUM | Benchmark before/after migration |

---

## 🔗 Integration with Master Plan

**Dependencies:**
- **Phase 1 (Weeks 1-3):** Foundation with testing infrastructure MUST be ready
- Depends on: pytest setup, conftest.py, configuration system

**Enables:**
- **Phase 3 (Weeks 7-11):** Orchestrator migration uses consolidated utilities
- **Phase 4 (Weeks 12-14):** DI container wiring uses toolkit registry

**Parallel Execution:**
- ✅ Can run in parallel with Phase 1 (foundation work)
- ✅ Can run in parallel with Phase 2 (brain enhancement)
- ❌ MUST complete before Phase 3 (orchestrator migration)

**Validation:**
```bash
# Phase 1.5 completion checklist
python scripts/validate_toolkit_consolidation.py

# Expected output:
# ✅ 180 scripts migrated to toolkit
# ✅ 61 duplicates consolidated
# ✅ 140 legacy scripts archived
# ✅ 85%+ test coverage
# ✅ All CLI wrappers operational
# ✅ Manifest updated
# ✅ Documentation complete
# ✅ No regression in existing workflows
```

---

## 📋 Phase 1.5 Checklist

### Sub-Phase 1: Assessment (Days 1-2)
- [ ] Run automated script inventory analysis
- [ ] Create migration-mapping.yaml
- [ ] Document high-priority scripts
- [ ] Review top 50 most-used scripts

### Sub-Phase 2: Production Migration (Days 3-7)
- [ ] Migrate Tier 1 scripts (40 scripts)
- [ ] Migrate Tier 2 scripts (60 scripts)
- [ ] Migrate Tier 3 scripts (80 scripts)
- [ ] All scripts have tests (70%+ coverage each)
- [ ] Update toolkit-manifest.yaml

### Sub-Phase 3: Duplicate Consolidation (Days 8-10)
- [ ] Identify all duplicates (61 scripts)
- [ ] Create consolidated versions
- [ ] Add feature flags for backward compatibility
- [ ] Create forwarding stubs

### Sub-Phase 4: Legacy Archival (Days 11-12)
- [ ] Create archive structure
- [ ] Document all legacy scripts
- [ ] Create migration guide
- [ ] Archive 140 legacy scripts

### Sub-Phase 5: PowerShell Modernization (Days 13-14)
- [ ] Create PowerShell toolkit module
- [ ] Convert 90 PowerShell scripts to Python
- [ ] Keep 25 PowerShell scripts for shell integration
- [ ] Test all PowerShell wrappers

### Sub-Phase 6: Testing (Days 15-17)
- [ ] Unit tests for all migrated scripts
- [ ] Integration tests for workflows
- [ ] End-to-end registry tests
- [ ] Achieve 85%+ test coverage
- [ ] Performance benchmarks pass

### Sub-Phase 7: Documentation (Days 18-19)
- [ ] Update main README.md
- [ ] Create category README.md files (12 categories)
- [ ] Create migration guide
- [ ] Update toolkit manifest
- [ ] Generate consolidated script inventory

---

## 🎉 Expected Outcomes

**Before Phase 1.5:**
- 418 scattered scripts across 10+ directories
- Duplicates causing confusion
- No test coverage
- Inconsistent documentation

**After Phase 1.5:**
- ✅ 227 organized scripts in toolkit (180 new + 47 existing)
- ✅ Zero duplicates
- ✅ 85%+ test coverage
- ✅ Complete documentation
- ✅ Unified CLI interface
- ✅ 140 legacy scripts properly archived
- ✅ Migration guide for all changes

**Benefits:**
- 🎯 Single source of truth for all CORTEX utilities
- 🎯 Easy discovery via toolkit registry
- 🎯 Consistent patterns and error handling
- 🎯 Cross-platform support (Windows/Linux/macOS)
- 🎯 Testable and maintainable
- 🎯 Ready for Phase 3 orchestrator migration
