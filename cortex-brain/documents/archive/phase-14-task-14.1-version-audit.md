# Phase 14, Task 14.1: Version Consolidation Audit

**Date:** December 23, 2025  
**Author:** Asif Hussain  
**Status:** ✅ COMPLETE

---

## 🎯 Executive Summary

Comprehensive audit of all v2/v3 version artifacts across CORTEX codebase to establish inventory for consolidation to unified v4.0 naming.

**Findings:**
- **Total Files with v2/v3 in Name:** 129 files
- **Active Code Files (src/):** 5 files (CRITICAL - require rename)
- **Active Test Files (tests/):** 2 files (MEDIUM - require rename)
- **Active Scripts (scripts/):** 5 files (LOW - can archive)
- **Historical Reports (cortex-brain/documents/reports/):** 90+ files (ARCHIVE ONLY - no rename needed)
- **Documentation (cortex-brain/documents/):** 15+ files (REVIEW - some may need updates)
- **Manifests/Schemas (cortex-brain/):** 7 files (REVIEW - assess migration vs archive)
- **Hidden Dependencies (.venv/, node_modules/):** 2 files (IGNORE - external libraries)

**Priority:**
1. 🔥 **HIGH:** 5 src files (production code)
2. ⚠️ **MEDIUM:** 2 test files (test coverage)
3. 📋 **LOW:** 5 scripts (utilities)
4. 📚 **INFO:** Documentation & reports (historical context)

---

## 📊 Detailed Inventory

### 1. 🔥 CRITICAL: Production Code Files (src/) - 5 FILES

**Action Required:** Rename to v4.0 convention + update all imports

| Current Path | Proposed New Path | Usage Analysis | Risk Level |
|--------------|-------------------|----------------|------------|
| `src/operations/dashboard_validator_v2.py` | `src/operations/dashboard_validator.py` | Used by onboarding orchestrator | MEDIUM |
| `src/dashboard/collectors/architecture_collector_v2.py` | `src/dashboard/collectors/architecture_collector.py` | Imported by `dashboard/collectors/__init__.py` | MEDIUM |
| `src/dashboard/schema/universal_schema_v2.py` | `src/dashboard/schema/universal_schema.py` | Core schema definition, imported by `__init__.py` | HIGH |
| `src/dashboard/schema/schema_validator_v2.py` | `src/dashboard/schema/schema_validator.py` | Schema validation, imported by `__init__.py` | HIGH |
| `src/orchestrators/sanitization/sanitization_orchestrator_v2_migrated.py` | `src/orchestrators/sanitization/sanitization_orchestrator.py` | Sanitization workflow | LOW |

**Import References Found:**
```python
# src/dashboard/collectors/__init__.py
from .architecture_collector_v2 import (...)

# src/dashboard/schema/__init__.py
from src.dashboard.schema.universal_schema_v2 import UniversalSchemaV2, SCHEMA_VERSION
from src.dashboard.schema.schema_validator_v2 import SchemaValidatorV2, ValidationResult

# src/operations/onboarding_orchestrator.py
from operations.dashboard_validator_v2 import DashboardValidator
```

**Classes/Functions to Track:**
- `UniversalSchemaV2` → `UniversalSchema` (class rename required)
- `SchemaValidatorV2` → `SchemaValidator` (class rename required)
- `DashboardValidator` (class name OK, just file rename)
- `ArchitectureCollectorV2` → `ArchitectureCollector` (class rename required)

---

### 2. ⚠️ MEDIUM: Test Files (tests/) - 2 FILES

**Action Required:** Rename to v4.0 convention

| Current Path | Proposed New Path | Notes |
|--------------|-------------------|-------|
| `tests/operations/test_align_system_v2_refactor.py` | `tests/operations/test_align_system.py` | Tests `align_system_v2()` function - currently SKIPPED |
| `tests/orchestrators/sanitization/test_sanitization_orchestrator_v2_agentic.py` | `tests/orchestrators/sanitization/test_sanitization_orchestrator.py` | Tests sanitization orchestrator v2 |

**Test Status:**
- `test_align_system_v2_refactor.py`: Contains skip marker referencing Phase 7B
- Both tests reference v2 code that will be renamed

---

### 3. 📋 LOW: Utility Scripts (scripts/) - 5 FILES

**Action Required:** Archive to `scripts/archive/v3-migration/` (no longer needed for v4.0)

| Current Path | Purpose | Keep or Archive? |
|--------------|---------|------------------|
| `scripts/fix_test_parameters_v2.py` | One-time migration script | ARCHIVE |
| `scripts/utilities/analyze_duplicates_v2.py` | Analysis utility v2 | ARCHIVE |
| `scripts/extract_evidence_templates_v2.py` | Template extraction v2 | ARCHIVE |
| `scripts/fix_response_format_v3.py` | One-time migration script | ARCHIVE |
| `scripts/migrate_templates_v3.py` | Template migration v2→v3 | ARCHIVE |

**Additional:** 5 files in `scripts/cortex_lens_v3/` directory (utilities for v3 lens extraction)

**Recommendation:** Archive entire `scripts/cortex_lens_v3/` directory to `scripts/archive/cortex-lens-v3/`

---

### 4. 📚 INFORMATIONAL: Documentation & Reports - 105+ FILES

#### 4.1 Historical Reports (90+ files)

**Location:** `cortex-brain/documents/reports/`

**Pattern:** `system-alignment-v2-YYYYMMDD_HHMMSS.md` (90+ timestamped reports)

**Action Required:** **NONE** - These are historical execution logs from CORTEX Align v2.0 runs (December 3-9, 2025). Keep for audit trail.

**Notable Reports:**
- `admin-governor-v2-governance-cycle-01.md`
- `admin-governor-v2-upgrade-report.md`
- `cortex-align-v2-all-phases-complete.md`
- `planning-orchestrator-v2-consolidation.md`
- `DEPLOYMENT-READY-v3.1.0.md`
- `v3.7.1-deployment-validation.md`
- `dashboard-v3-overview-tab-*.md` (3 files)
- `enhanced-cleanup-v3-live-execution-report.md`
- `legacy-spec-generator-v3-completion.md`

#### 4.2 Implementation Guides (3 files)

**Location:** `cortex-brain/documents/implementation-guides/`

| File | Action | Rationale |
|------|--------|-----------|
| `dashboard-v3-handoff-instructions.md` | KEEP | May contain relevant v3→v4 migration context |
| `enhanced-cleanup-orchestrator-v3-summary.md` | KEEP | Documents v3 cleanup orchestrator (historical) |
| `planning-orchestrator-v3.1-enhancement-summary.md` | KEEP | Documents v3.1 planning system (historical) |

#### 4.3 Analysis Documents (2 files)

**Location:** `cortex-brain/documents/analysis/`

| File | Action | Rationale |
|------|--------|-----------|
| `dashboard-v3-data-feasibility-analysis.md` | KEEP | v3 dashboard analysis (historical context) |
| `duplicate-functionality-analysis-v2.json` | KEEP | v2 analysis results (historical context) |

#### 4.4 Planning Documents (3 files)

**Location:** `cortex-brain/documents/planning/`

| File | Action | Rationale |
|------|--------|-----------|
| `archived/CORTEX-PROMPT-UPDATE-v3.md` | KEEP | Already archived, no action needed |
| `archived/sessions/cortex-lens-plan-v3.md` | KEEP | Already archived, no action needed |
| `features/active/comprehensive-dashboard-code-intelligence-plan-v3.9.yaml` | REVIEW | Active plan - may need version update |

---

### 5. 🔧 TECHNICAL: Manifests & Schemas - 7 FILES

**Location:** `cortex-brain/manifests/` and `cortex-brain/response-templates/`

| File | Type | Action Required |
|------|------|----------------|
| `cortex-brain/manifests/orchestrators/cortex-lens-v3-manifest.yaml` | Orchestrator | REVIEW - assess if active or historical |
| `cortex-brain/manifests/schemas/config-manifest-schema-v2.json` | Schema | **CRITICAL** - Phase 7A output, should be v4.0 |
| `cortex-brain/manifests/schemas/core-manifest-schema-v2.json` | Schema | **CRITICAL** - Phase 7A output, should be v4.0 |
| `cortex-brain/manifests/schemas/integration-manifest-schema-v2.json` | Schema | **CRITICAL** - Phase 7A output, should be v4.0 |
| `cortex-brain/response-templates/mixins-v2.yaml` | Template | REVIEW - assess migration status |
| `cortex-brain/response-templates/templates-v3-intelligent.yaml` | Template | REVIEW - assess if superseded by v4.0 templates |
| `cortex-brain/dashboards/ui/components/overview-tab-v3.js` | Dashboard UI | REVIEW - assess if active |

**⚠️ CRITICAL FINDING:** 3 schema files from Phase 7A have v2 suffix but are production artifacts. These should be:
- Renamed to remove version suffix (canonical schemas)
- OR confirmed as intentional v2 designation

---

### 6. 🔍 CODE REFERENCES: Function/Variable Names with v2/v3

**In-Code Version References (not file names):**

#### Production Code:
```python
# src/operations/modules/realignment/realignment_utility.py
def align_system_v2(...)  # Function name

# src/operations/modules/upgrade/upgrade_utility.py
def compare_versions(v1: str, v2: str) -> int:  # Variable names (OK - not version)

# src/epmo/brain/brain_config.py
def _vector_similarity(self, v1: List[float], v2: List[float]) -> float:  # Variable names (OK)

# src/dashboard/schema/schema_validator_v2.py
def _validate_v2_schema(...)  # Method name
def _validate_metadata_v2(...)  # Method name

# src/dashboard/schema/schema_migrator.py
def migrate_v1_to_v2(...)  # Method name (migration utility)

# src/operations/align.py
from src.operations.modules.realignment.realignment_utility import align_system_v2  # Import
```

**Action Required:**
- Rename `align_system_v2()` → `align_system()` (primary function)
- Rename `_validate_v2_schema()` → `_validate_schema()` (internal method)
- Rename `_validate_metadata_v2()` → `_validate_metadata()` (internal method)
- KEEP `migrate_v1_to_v2()` (explicit migration utility - version in name is intentional)
- KEEP `compare_versions(v1, v2)` (variable names, not versions)
- KEEP `_vector_similarity(v1, v2)` (variable names, not versions)

#### Documentation References:
```markdown
# Multiple references to "CORTEX Align v2.0", "Planning System v3.1", etc.
# These are acceptable as historical context in documentation
```

---

## 🎯 Consolidation Strategy

### Phase 1: High-Priority Renames (Task 14.2)

**Target:** 5 src files, 2 test files (CRITICAL path)

**Steps:**
1. Create backup branch: `git checkout -b phase-14-backup`
2. Rename files (git mv):
   ```bash
   git mv src/operations/dashboard_validator_v2.py src/operations/dashboard_validator.py
   git mv src/dashboard/collectors/architecture_collector_v2.py src/dashboard/collectors/architecture_collector.py
   git mv src/dashboard/schema/universal_schema_v2.py src/dashboard/schema/universal_schema.py
   git mv src/dashboard/schema/schema_validator_v2.py src/dashboard/schema/schema_validator.py
   git mv src/orchestrators/sanitization/sanitization_orchestrator_v2_migrated.py src/orchestrators/sanitization/sanitization_orchestrator.py
   ```
3. Rename classes (AST-based refactoring):
   - `UniversalSchemaV2` → `UniversalSchema`
   - `SchemaValidatorV2` → `SchemaValidator`
   - `ArchitectureCollectorV2` → `ArchitectureCollector`
4. Update imports (semantic search + replace):
   - `from .architecture_collector_v2 import` → `from .architecture_collector import`
   - `from src.dashboard.schema.universal_schema_v2 import UniversalSchemaV2` → `from src.dashboard.schema.universal_schema import UniversalSchema`
   - `from src.dashboard.schema.schema_validator_v2 import SchemaValidatorV2` → `from src.dashboard.schema.schema_validator import SchemaValidator`
5. Rename test files:
   ```bash
   git mv tests/operations/test_align_system_v2_refactor.py tests/operations/test_align_system.py
   git mv tests/orchestrators/sanitization/test_sanitization_orchestrator_v2_agentic.py tests/orchestrators/sanitization/test_sanitization_orchestrator.py
   ```
6. Run tests: `pytest tests/ -v`

**Estimated Duration:** 2 days

---

### Phase 2: Function/Method Renames (Task 14.2 continued)

**Target:** 3 function names in code

**Steps:**
1. Rename `align_system_v2()` → `align_system()`:
   - Update definition in `src/operations/modules/realignment/realignment_utility.py`
   - Update import in `src/operations/align.py`
   - Update import in `scripts/cli_wrappers/align_wrapper.py`
   - Update import in `tests/operations/test_align_system.py` (already renamed)
2. Rename schema validation methods:
   - `_validate_v2_schema()` → `_validate_schema()`
   - `_validate_metadata_v2()` → `_validate_metadata()`
3. Update all references

**Estimated Duration:** 1 day (included in Task 14.2)

---

### Phase 3: Schema File Review (Task 14.2 or separate)

**Target:** 3 schema JSON files from Phase 7A

**Decision Point:**
- **Option A:** Remove version suffix (canonical naming)
  - `config-manifest-schema-v2.json` → `config-manifest-schema.json`
  - `core-manifest-schema-v2.json` → `core-manifest-schema.json`
  - `integration-manifest-schema-v2.json` → `integration-manifest-schema.json`
- **Option B:** Keep v2 suffix (intentional versioning for future schema evolution)

**Recommendation:** **Option A** - Remove suffix, these are the current production schemas

**Steps:**
1. Verify no other schema files exist with same names
2. Rename files
3. Update references in manifest loaders
4. Run manifest tests

**Estimated Duration:** 0.5 days

---

### Phase 4: Script Archival (Task 14.2 - LOW priority)

**Target:** 5 script files + cortex_lens_v3 directory

**Steps:**
1. Create archive directory: `scripts/archive/v3-migration/`
2. Move files:
   ```bash
   mkdir -p scripts/archive/v3-migration
   git mv scripts/fix_test_parameters_v2.py scripts/archive/v3-migration/
   git mv scripts/utilities/analyze_duplicates_v2.py scripts/archive/v3-migration/
   git mv scripts/extract_evidence_templates_v2.py scripts/archive/v3-migration/
   git mv scripts/fix_response_format_v3.py scripts/archive/v3-migration/
   git mv scripts/migrate_templates_v3.py scripts/archive/v3-migration/
   git mv scripts/cortex_lens_v3 scripts/archive/cortex-lens-v3
   ```
3. Add README explaining archive purpose

**Estimated Duration:** 0.5 days

---

### Phase 5: Documentation Audit (Task 14.5)

**Target:** Active documentation with v3/v2 references

**Steps:**
1. Review `comprehensive-dashboard-code-intelligence-plan-v3.9.yaml` - update version references
2. Review `dashboard-v3-handoff-instructions.md` - add "HISTORICAL" marker
3. Review `cortex-lens-v3-manifest.yaml` - determine if active or historical
4. Update `.github/prompts/modules/response-format-v3.md` to `response-format-v4.md` if needed
5. Search all .md files for "v2.0" and "v3.0" references - update where appropriate

**Estimated Duration:** 3 days (Task 14.5)

---

## 📋 Task Dependencies

**Task 14.2 (Rename/Archive) depends on:**
- ✅ Task 14.1 complete (this audit)
- Decisions on schema naming (Option A vs B)

**Task 14.6 (Test Validation) depends on:**
- ✅ Task 14.2 complete (all renames done)

---

## 🎯 Success Criteria

**Task 14.1 (this audit) is COMPLETE when:**
- ✅ All v2/v3 files inventoried
- ✅ Consolidation strategy documented
- ✅ Import dependencies mapped
- ✅ Risk assessment complete
- ✅ Phase 2-5 plans outlined

**Overall Phase 14 is COMPLETE when:**
- ☐ All production code files use v4.0 naming (no v2/v3 suffixes)
- ☐ All test files updated to match renamed code
- ☐ All imports/references updated
- ☐ 100% test pass rate maintained
- ☐ Historical scripts archived with context
- ☐ Documentation reviewed and updated
- ☐ Zero broken references

---

## 🚨 Risk Mitigation

**Risks Identified:**
1. **Breaking imports:** Renaming files breaks existing imports
   - **Mitigation:** Use semantic search to find ALL import references before rename
2. **Test failures:** Tests reference old names
   - **Mitigation:** Update tests in same commit as code rename
3. **External dependencies:** Other repos/tools reference v2/v3 names
   - **Mitigation:** CORTEX is isolated (no external dependencies confirmed)
4. **Lost git history:** File renames lose git blame history
   - **Mitigation:** Use `git mv` (preserves history), document in commit message

**Rollback Plan:**
- Backup branch created before any changes
- All changes in single atomic commit per file group
- Can revert with `git reset --hard phase-14-backup`

---

## 📊 Summary Statistics

| Category | Count | Action |
|----------|-------|--------|
| **Production Code Files** | 5 | RENAME (CRITICAL) |
| **Test Files** | 2 | RENAME (MEDIUM) |
| **Utility Scripts** | 10 | ARCHIVE (LOW) |
| **Historical Reports** | 90+ | KEEP (no action) |
| **Documentation** | 15+ | REVIEW (selective update) |
| **Manifests/Schemas** | 7 | REVIEW (3 critical) |
| **Hidden/External** | 2 | IGNORE |
| **TOTAL FILES** | 129 | - |

**Priority Breakdown:**
- 🔥 **CRITICAL (10 files):** 5 src + 2 tests + 3 schemas
- ⚠️ **MEDIUM (5 files):** Active documentation
- 📋 **LOW (10 files):** Utility scripts
- 📚 **INFO (100+ files):** Historical reports & archived docs

---

## ✅ Task 14.1 Status: COMPLETE

**Completion Criteria Met:**
- ✅ Comprehensive file search executed
- ✅ All v2/v3 artifacts inventoried and categorized
- ✅ Import dependencies mapped
- ✅ Consolidation strategy documented with 5 phases
- ✅ Risk assessment and mitigation plan included
- ✅ Success criteria defined for Task 14.2+

**Next Action:** Begin Task 14.2 (High-Priority Renames - 5 src files, 2 test files)

**Estimated Task 14.2 Duration:** 2 days  
**Task 14.2 ETA:** December 25, 2025
