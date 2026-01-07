# Hardcoded Paths Audit - A19 Cortex5 Snowball Epic

**Date:** January 6, 2026  
**Author:** Asif Hussain  
**Purpose:** Identify all hardcoded `cortex-brain/documents/planning/active/` paths and propose centralized configuration  
**Status:** 🔴 CRITICAL - 60+ hardcoded references found

---

## 🎯 Executive Summary

**Problem:** Planning orchestrator and 10+ other components have hardcoded `cortex-brain/documents/planning/active/` path, violating DRY principle and causing maintenance issues.

**Impact:**
- ❌ 60+ hardcoded references across codebase
- ❌ Path changes require 60+ file edits
- ❌ Inconsistent path construction patterns
- ❌ Cannot easily relocate planning folder
- ❌ Testing requires mock filesystem structure

**Solution:** Centralize path configuration in `CortexConfig` with single source of truth.

---

## 📊 Audit Results

### 🔴 CRITICAL: Core Orchestrators (12 references)

**File:** `src/orchestrators/planning/planning_orchestrator_v5.py`  
**References:** 11 hardcoded paths

| Line | Context | Pattern |
|------|---------|---------|
| 481 | `generate_master_plan` | `Path(f"cortex-brain/documents/planning/active/{folder_name}")` |
| 665 | `_generate_plan_metadata` | `f'cortex-brain/documents/planning/active/{feature_name}'` |
| 854 | `_create_context_folder` | `Path(f"cortex-brain/documents/planning/active/{feature_name}")` |
| 912 | `_create_analysis_folder` | `Path(f"cortex-brain/documents/planning/active/{feature_name}")` |
| 1036 | `_create_reports_folder` | `Path(f"cortex-brain/documents/planning/active/{feature_name}")` |
| 1113 | `_create_tracking_folder` | `Path(f"cortex-brain/documents/planning/active/{folder_name}")` |
| 1187 | `_create_artifacts_folder` | `Path(f"cortex-brain/documents/planning/active/{folder_name}")` |
| 1534 | `_generate_continuation_prompt` | `Path(f"cortex-brain/documents/planning/active/{folder_name}")` |
| 2020 | `_validate_plan_structure` | `Path(f"cortex-brain/documents/planning/active/{expected_folder_name}")` |
| 2025 | `_validate_plan_structure` | `Path(f"cortex-brain/documents/planning/active/{feature_name}")` |
| 2248 | `_load_existing_plan` | `Path(f"cortex-brain/documents/planning/active/{feature_name}")` |

**File:** `src/orchestrators/holistic_review_orchestrator.py`  
**References:** 3 hardcoded paths

| Line | Context |
|------|---------|
| 276 | `f"cortex-brain/documents/planning/active/{parent_plan_id}"` |
| 307 | `Path(f"cortex-brain/documents/planning/active/{sibling_dir}")` |
| 653 | `f"cortex-brain/documents/planning/active/{parent_plan_id}/{document_path}"` |

**File:** `src/orchestrators/base/base_orchestrator_v4_1.py`  
**References:** 1 hardcoded path

| Line | Context |
|------|---------|
| 552 | `Path(f"cortex-brain/documents/planning/active/{self.plan_id}")` |

**File:** `src/orchestrators/master_orchestrator.py`  
**References:** 1 hardcoded path

| Line | Context |
|------|---------|
| 144 | `f"cortex-brain/documents/planning/active/{parent_plan_id}/tracking/progress.json"` |

---

### 🟠 HIGH: Supporting Systems (8 references)

**File:** `src/orchestrators/plan_upgrade/plan_upgrade_orchestrator.py`

| Line | Context |
|------|---------|
| 30 | `"root": "cortex-brain/documents/planning/active/"` |

**File:** `src/orchestrators/autonomous_execution_engine.py`

| Line | Context |
|------|---------|
| 111 | `plan_path="cortex-brain/documents/planning/active/my-plan/00-master-plan.md"` |

**File:** `src/orchestrators/system/system_integrity_orchestrator.py`

| Line | Context |
|------|---------|
| 669 | `if "cortex-brain/documents/planning/active" in str(path):` |

**File:** `src/orchestrators/shared/examples.py` (5 references)

| Line | Context |
|------|---------|
| 36 | `Path("cortex-brain/documents/planning/active/test-feature/tracking/progress-tracker.json")` |
| 89 | `Path("cortex-brain/documents/planning/active/CORTEX-5.0/tracking/epic-progress-tracker.json")` |
| 94 | `Path("cortex-brain/documents/planning/active/CORTEX-5.0/00A-epic-structure-cleanup/tracking/progress-tracker.json")` |
| 102 | `Path("cortex-brain/documents/planning/active/CORTEX-5.0/00B-epic-feature-planner/tracking/progress-tracker.json")` |
| 131 | `Path("cortex-brain/documents/planning/active/CORTEX-5.0/CORTEX-5.0-plan-viewer.html")` |

---

### 🟡 MEDIUM: Tooling & Scripts (6 references)

**File:** `scripts/audit_master_orchestrator_architecture.py`

| Line | Context |
|------|---------|
| 148 | `"cortex-brain/documents/planning/active/c150-remediation-plan/00-c150-remediation-plan.yaml"` |
| 263 | `plan_dir = self.workspace_root / "cortex-brain/documents/planning/active"` |
| 435 | `c150_plan = self.workspace_root / "cortex-brain/documents/planning/active/c150-remediation-plan/00-c150-remediation-plan.yaml"` |

**File:** `regenerate_yaml_plan_viewers.py`

| Line | Context |
|------|---------|
| 75 | `base_path = Path("cortex-brain/documents/planning/active")` |

**File:** `src/validation/glassmorphism_validator.py`

| Line | Context |
|------|---------|
| 614 | `"- **Master Plan:** `cortex-brain/documents/planning/active/level-2-glassmorphism-standardization/00-master-plan.md`"` |

---

### 🟢 LOW: Documentation (32+ references)

**Files:**
- `.asif/copilot-chats/fix-wiring.md` (10 references)
- `.github/copilot/copilot-chats/chat01.md` (8 references)
- `.github/copilot/copilot-chats/chat04.md` (3 references)
- `cortex-brain/documents/planning/active/cortex5-remediation/epic-manifest.yaml` (10 references)
- `src/templates/README.md` (1 reference)
- `src/brain/README.md` (1 reference)
- `src/orchestrators/README.md` (1 reference)
- `backups/css-deployment-backup-20260103_165253/glass-design-tokens.css` (1 reference)

**Action:** Update documentation after path centralization.

---

## 🛠️ Proposed Solution

### 1. Centralize Path Configuration in `CortexConfig`

**File:** `src/config/config_manager.py`

**Add to `PathConfig` dataclass:**

```python
@dataclass
class PathConfig:
    """Path configuration with resolution."""
    orchestrators: Path
    brain: Path
    templates: Path
    mcp_gateway: Path
    logs: Path
    cache: Path
    
    # NEW: Planning paths
    planning_active: Path = field(default_factory=lambda: Path("cortex-brain/documents/planning/active"))
    planning_archived: Path = field(default_factory=lambda: Path("cortex-brain/archives/plans"))
    planning_templates: Path = field(default_factory=lambda: Path("cortex-brain/manifests/plan-templates"))
    
    def resolve_all(self, root: Path) -> None:
        """Resolve all paths relative to root if they're not absolute."""
        for key in self.__dataclass_fields__.keys():
            path_value = getattr(self, key)
            if not path_value.is_absolute():
                setattr(self, key, root / path_value)
    
    def get_plan_path(self, plan_name: str, active: bool = True) -> Path:
        """Get path for specific plan folder."""
        base = self.planning_active if active else self.planning_archived
        return base / plan_name
    
    def get_plan_tracking_path(self, plan_name: str) -> Path:
        """Get tracking folder path for plan."""
        return self.get_plan_path(plan_name) / "tracking"
    
    def get_plan_reports_path(self, plan_name: str) -> Path:
        """Get reports folder path for plan."""
        return self.get_plan_path(plan_name) / "reports"
```

**Add to `CortexConfig` class:**

```python
@dataclass
class CortexConfig:
    """Main configuration container."""
    environment: Environment
    paths: PathConfig
    brain: BrainConfig
    ide: IDEConfig
    logging: LoggingConfig
    metadata: ConfigMetadata
    
    @property
    def planning_active_path(self) -> Path:
        """Shortcut for active planning folder."""
        return self.paths.planning_active
    
    @property
    def planning_archived_path(self) -> Path:
        """Shortcut for archived planning folder."""
        return self.paths.planning_archived
    
    def get_plan_path(self, plan_name: str, active: bool = True) -> Path:
        """Get path for specific plan folder."""
        return self.paths.get_plan_path(plan_name, active)
```

---

### 2. Update Planning Orchestrator v5

**File:** `src/orchestrators/planning/planning_orchestrator_v5.py`

**Add config import:**

```python
from src.config import config  # Singleton CortexConfig instance
```

**Replace all 11 hardcoded references:**

**BEFORE:**
```python
plan_folder = Path(f"cortex-brain/documents/planning/active/{folder_name}")
```

**AFTER:**
```python
plan_folder = config.get_plan_path(folder_name, active=True)
```

**Pattern replacement table:**

| Current Pattern | New Pattern |
|----------------|-------------|
| `Path(f"cortex-brain/documents/planning/active/{name}")` | `config.get_plan_path(name)` |
| `f'cortex-brain/documents/planning/active/{name}'` | `str(config.get_plan_path(name))` |
| `Path(f"cortex-brain/documents/planning/active/{name}/tracking")` | `config.paths.get_plan_tracking_path(name)` |
| `Path(f"cortex-brain/documents/planning/active/{name}/reports")` | `config.paths.get_plan_reports_path(name)` |

---

### 3. Update Other Orchestrators

**Files to update (priority order):**

1. ✅ **`src/orchestrators/holistic_review_orchestrator.py`** (3 references)
   - Line 276: `config.get_plan_path(parent_plan_id)`
   - Line 307: `config.get_plan_path(sibling_dir)`
   - Line 653: `config.get_plan_path(parent_plan_id) / document_path`

2. ✅ **`src/orchestrators/base/base_orchestrator_v4_1.py`** (1 reference)
   - Line 552: `config.get_plan_path(self.plan_id)`

3. ✅ **`src/orchestrators/master_orchestrator.py`** (1 reference)
   - Line 144: `config.paths.get_plan_tracking_path(parent_plan_id) / "progress.json"`

4. ✅ **`src/orchestrators/plan_upgrade/plan_upgrade_orchestrator.py`** (1 reference)
   - Line 30: `"root": str(config.planning_active_path)`

5. ✅ **`src/orchestrators/autonomous_execution_engine.py`** (1 reference)
   - Line 111: Update example to use `config.get_plan_path("my-plan")`

6. ✅ **`src/orchestrators/system/system_integrity_orchestrator.py`** (1 reference)
   - Line 669: `if str(config.planning_active_path) in str(path):`

7. ✅ **`src/orchestrators/shared/examples.py`** (5 references)
   - Update all examples to use `config.get_plan_path()`

---

### 4. Update Tooling & Scripts

**Files:**

1. ✅ **`scripts/audit_master_orchestrator_architecture.py`** (3 references)
   - Import config singleton
   - Replace all 3 hardcoded paths

2. ✅ **`regenerate_yaml_plan_viewers.py`** (1 reference)
   - Line 75: `base_path = config.planning_active_path`

3. ✅ **`src/validation/glassmorphism_validator.py`** (1 reference)
   - Line 614: Use config for documentation path

---

### 5. Configuration File

**File:** `cortex.config.json`

**Add planning paths section:**

```json
{
  "environment": "development",
  "paths": {
    "orchestrators": "src/orchestrators",
    "brain": "cortex-brain",
    "templates": "templates",
    "mcp_gateway": "src/mcp",
    "logs": "logs",
    "cache": "cortex-brain/cache",
    "planning_active": "cortex-brain/documents/planning/active",
    "planning_archived": "cortex-brain/archives/plans",
    "planning_templates": "cortex-brain/manifests/plan-templates"
  },
  "brain": {
    "tier1_db": "{repo}/cortex-brain/tier1/working_memory.db",
    "tier2_db": "{repo}/cortex-brain/tier2/knowledge-graph.db",
    "tier3_db": "{repo}/cortex-brain/tier3/dev-context.db",
    "tier0_rules": "{repo}/cortex-brain/tier0/brain-protection-rules.yaml",
    "max_conversations": 70,
    "pattern_confidence_threshold": 0.5,
    "enable_cross_repo_learning": true
  }
}
```

---

## 📋 Implementation Plan

### Phase 1: Configuration Infrastructure (1 hour)

**Tasks:**
1. ✅ Update `PathConfig` dataclass with planning paths (3 new fields + 3 helper methods)
2. ✅ Add `CortexConfig` convenience properties (`planning_active_path`, `get_plan_path()`)
3. ✅ Update `cortex.config.json` with planning path defaults
4. ✅ Write unit tests for path resolution logic
5. ✅ Validate backward compatibility (old code still works during migration)

**Deliverables:**
- `src/config/config_manager.py` (updated)
- `cortex.config.json` (updated)
- `tests/config/test_planning_paths.py` (new)

**Success Criteria:**
- `config.planning_active_path` returns correct Path object
- `config.get_plan_path("test-plan")` returns `cortex-brain/documents/planning/active/test-plan`
- Tests pass (100% coverage)

---

### Phase 2: Core Orchestrators Migration (2 hours)

**Tasks:**
1. ✅ Update `planning_orchestrator_v5.py` (11 references)
2. ✅ Update `holistic_review_orchestrator.py` (3 references)
3. ✅ Update `base_orchestrator_v4_1.py` (1 reference)
4. ✅ Update `master_orchestrator.py` (1 reference)
5. ✅ Run integration tests for planning orchestrator
6. ✅ Test plan creation with new config-based paths

**Deliverables:**
- Updated orchestrator files (4 files)
- Integration test results

**Success Criteria:**
- All 16 core references converted to config-based paths
- Planning orchestrator creates plans in correct location
- Holistic review orchestrator finds sibling plans correctly
- Zero path-related errors in tests

---

### Phase 3: Supporting Systems Migration (1 hour)

**Tasks:**
1. ✅ Update `plan_upgrade_orchestrator.py` (1 reference)
2. ✅ Update `autonomous_execution_engine.py` (1 reference)
3. ✅ Update `system_integrity_orchestrator.py` (1 reference)
4. ✅ Update `shared/examples.py` (5 references)
5. ✅ Run unit tests for affected modules

**Deliverables:**
- Updated supporting files (4 files)
- Unit test results

**Success Criteria:**
- All 8 supporting references converted
- Examples code works with config-based paths
- Plan upgrade uses config paths
- System integrity checks use config paths

---

### Phase 4: Tooling & Scripts Migration (30 minutes)

**Tasks:**
1. ✅ Update `scripts/audit_master_orchestrator_architecture.py` (3 references)
2. ✅ Update `regenerate_yaml_plan_viewers.py` (1 reference)
3. ✅ Update `src/validation/glassmorphism_validator.py` (1 reference)
4. ✅ Test script execution with new config

**Deliverables:**
- Updated script files (3 files)
- Script execution validation

**Success Criteria:**
- Scripts use config paths correctly
- Plan viewer regeneration works
- Architecture audit uses config paths

---

### Phase 5: Documentation Updates (30 minutes)

**Tasks:**
1. ✅ Update `src/templates/README.md` (1 reference)
2. ✅ Update `src/brain/README.md` (1 reference)
3. ✅ Update `src/orchestrators/README.md` (1 reference)
4. ✅ Add migration guide to `cortex-brain/documents/planning/active/cortex5-snowball/`
5. ✅ Update architecture diagrams if needed

**Deliverables:**
- Updated README files (3 files)
- Migration guide document

**Success Criteria:**
- All documentation references use config-based paths
- Migration guide explains old vs new patterns
- Architecture diagrams reflect centralized config

---

### Phase 6: Validation & Testing (1 hour)

**Tasks:**
1. ✅ Run full test suite (pytest)
2. ✅ Test plan creation end-to-end (Planning v5)
3. ✅ Test plan upgrade workflow
4. ✅ Test holistic review orchestrator
5. ✅ Test plan viewer regeneration
6. ✅ Verify no hardcoded paths remain (`grep` audit)
7. ✅ Performance benchmark (ensure no regression)

**Deliverables:**
- Test results (100% pass rate)
- Performance benchmark report
- Zero hardcoded paths confirmation

**Success Criteria:**
- All tests pass
- Plan creation works correctly
- No performance regression (<5% overhead)
- Zero hardcoded `cortex-brain/documents/planning/active` references in code

---

## 📈 Benefits

### Immediate Benefits

1. **Single Source of Truth** - One place to change planning folder location
2. **Testability** - Mock config for testing without filesystem
3. **Flexibility** - Easy to relocate planning folder (e.g., for multi-workspace support)
4. **Consistency** - All components use same path construction logic
5. **Maintainability** - 60+ hardcoded strings → 1 config property

### Long-Term Benefits

1. **Multi-Workspace Support** - Different workspaces can have different planning paths
2. **Cloud Integration** - Planning folders can be in cloud storage (S3, Azure Blob)
3. **Testing Isolation** - Tests can use temporary directories via config override
4. **Performance** - Path construction optimized in one place
5. **Documentation** - Config file documents all paths in one place

---

## 🎯 Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| **Hardcoded References** | 60+ | 0 | 0 |
| **Files to Edit (Path Change)** | 60+ | 1 (config.json) | 1 |
| **Test Coverage** | N/A | 100% | 100% |
| **Performance Overhead** | N/A | <5% | <5% |
| **Migration Time** | N/A | 6 hours | 1 day |

---

## 🚨 Risks & Mitigation

### Risk 1: Breaking Changes

**Risk:** Existing code breaks during migration  
**Probability:** Medium  
**Impact:** High  
**Mitigation:**
- Phased migration (update config first, then components)
- Backward compatibility layer during transition
- Comprehensive testing before merge
- Rollback plan (Git revert)

### Risk 2: Performance Regression

**Risk:** Config lookup adds overhead  
**Probability:** Low  
**Impact:** Low  
**Mitigation:**
- Config properties cached at startup
- Benchmark before/after
- Profile path construction performance

### Risk 3: Missing References

**Risk:** Some hardcoded paths not found in audit  
**Probability:** Low  
**Impact:** Medium  
**Mitigation:**
- Re-run grep audit after migration
- Integration tests catch path errors
- Manual code review of all orchestrators

---

## 📚 Related Documentation

- **Architecture Contract:** `cortex-brain/documents/cortex-architecture-quick-ref.md`
- **Config Manager:** `src/config/config_manager.py`
- **Planning System Manifest:** `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml` (DRY principle)

---

## 🎯 Next Steps

1. ✅ **Phase 1:** Update config infrastructure (this sprint)
2. ✅ **Phase 2:** Migrate core orchestrators (this sprint)
3. ✅ **Phase 3:** Migrate supporting systems (this sprint)
4. ⏸️ **Phase 4:** Migrate tooling & scripts (next sprint)
5. ⏸️ **Phase 5:** Update documentation (next sprint)
6. ⏸️ **Phase 6:** Full validation & testing (next sprint)

**Total Effort:** 6 hours (spread across 2 sprints)  
**Priority:** HIGH (blocks multi-workspace support)  
**Owner:** Planning Orchestrator v5 team

---

**Generated By:** CORTEX Audit System  
**Audit Date:** January 6, 2026  
**Report Version:** 1.0.0  
**Status:** ✅ READY FOR IMPLEMENTATION
