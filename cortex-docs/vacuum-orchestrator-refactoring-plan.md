# Vacuum Orchestrator Refactoring Plan

**Authority:** cortex-architect.prompt.md § HOLISTIC WORK PROTOCOL  
**Phase:** AC-VACUUM-REFACTOR-001  
**Author:** CORTEX Architect  
**Date:** 2026-02-15

---

## 🎯 Refactoring Objectives

### Current State Problems
1. **Monolithic script** — 744 lines in `.cortex/run_vacuum.py` with mixed concerns
2. **No separation of concerns** — Cleanup logic mixed with orchestration
3. **Hard to test** — Direct file operations without abstraction layer
4. **No golden tests** — Regressions possible on refactoring
5. **Manual string templates** — Embedded file content in cleanup methods

### Target State Goals
1. **Plugin architecture** — Cleaners as independent, testable plugins
2. **Golden test coverage** — Immutable behavioral contracts for all operations
3. **Safe refactoring** — Tests prevent regressions during restructuring
4. **Orchestration layer** — Clean separation between coordination and execution
5. **Template management** — External templates for file recreation

---

## 📋 Golden Test Results (RED Phase)

### Test Summary
```
✅ 3 PASSING (preservation tests)
❌ 4 FAILING (deletion/relocation tests - expected in RED phase)

Preservation Tests (PASSING):
- test_subdirectory_databases_preserved ✅
- test_config_jsons_preserved ✅
- test_valid_markdown_preserved ✅

Action Tests (FAILING - Need GREEN implementation):
- test_root_databases_deleted ❌
- test_report_jsons_relocated ❌
- test_sprawl_markdown_deleted ❌
- test_complete_vacuum_cycle ❌
```

### Behavioral Contracts Defined

| Contract | Files | Operation | Status |
|----------|-------|-----------|--------|
| Root databases deleted | 4 (.db files) | DELETE | ❌ RED |
| Subdirectory databases preserved | 2 (.db files) | PRESERVE | ✅ PASS |
| Report JSONs relocated | 3 (report/*.json) | RELOCATE | ❌ RED |
| Config JSONs preserved | 2 (package.json, tsconfig.json) | PRESERVE | ✅ PASS |
| Sprawl markdown deleted | 4 (*-summary.md, etc.) | DELETE | ❌ RED |
| Valid markdown preserved | 3 (README.md, cortex-docs/, .github/) | PRESERVE | ✅ PASS |

---

## 🏗️ Refactoring Architecture

### New Structure

```
cortex_brain/tier1/orchestrators/
├── vacuum/
│   ├── __init__.py                  # Public API
│   ├── orchestrator.py              # VacuumOrchestrator (coordinator)
│   ├── state.py                     # OrchestratorState, Report models
│   └── config.yaml                  # Configuration
│
└── cleaners/
    ├── __init__.py                  # Cleaner registry
    ├── base.py                      # CleanerInterface (ABC)
    ├── registry.py                  # CleanerRegistry
    ├── database_migration.py        # DatabaseMigrationCleaner
    ├── root_artifacts.py            # RootArtifactsCleaner
    ├── markdown_sprawl.py           # MarkdownSprawlCleaner
    └── cache_artifacts.py           # CacheArtifactsCleaner

.cortex/
├── run_vacuum.py                    # CLI wrapper (thin layer)
└── templates/
    └── auto_cleanup_manager.py.j2   # Jinja2 template for file recreation
```

### Plugin Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class Analysis:
    """Analysis result from cleaner scan."""
    cleaner_id: str
    timestamp: str
    files_scanned: int
    issues_found: int
    plan: Dict[str, Any]  # Execution plan
    logs: list[str]

@dataclass
class Report:
    """Execution report from cleaner."""
    cleaner_id: str
    timestamp: str
    status: str  # SUCCESS, FAILED, PARTIAL
    actions_taken: int
    changes: Dict[str, int]  # deleted: N, relocated: M
    errors: list[str]
    logs: list[str]

class CleanerInterface(ABC):
    """Base interface for all vacuum cleaners."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return cleaner name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Return cleaner version."""
        pass
    
    @abstractmethod
    def analyze(self) -> Analysis:
        """Scan repository and generate execution plan."""
        pass
    
    @abstractmethod
    def execute(self, plan: Dict[str, Any]) -> Report:
        """Execute cleanup plan."""
        pass
    
    @abstractmethod
    def rollback(self) -> RollbackResult:
        """Rollback changes if needed."""
        pass
```

---

## 🔄 Refactoring Strategy

### Phase 1: Extract Cleaner Plugins (Current)
**Status:** In Progress  
**Golden Tests:** ✅ Defined (7 scenarios)

**Steps:**
1. ✅ Define golden test scenarios with immutable expectations
2. ✅ Create CleanerInterface base class
3. ⚪ Extract DatabaseMigrationCleaner from run_vacuum.py
4. ⚪ Extract RootArtifactsCleaner (JSON cleanup)
5. ⚪ Extract MarkdownSprawlCleaner
6. ⚪ Create VacuumOrchestrator coordinator
7. ⚪ Update .cortex/run_vacuum.py to use orchestrator
8. ⚪ Run golden tests → GREEN phase

### Phase 2: Add Template Management
**Steps:**
1. ⚪ Create .cortex/templates/ directory
2. ⚪ Extract auto_cleanup_manager.py to Jinja2 template
3. ⚪ Add TemplateRecreationCleaner plugin
4. ⚪ Update golden tests for template recreation

### Phase 3: Enhance Observability
**Steps:**
1. ⚪ Add structured logging to all cleaners
2. ⚪ Generate JSON reports for dashboard integration
3. ⚪ Add dry-run mode for all cleaners
4. ⚪ Add rollback capability tests

---

## 📊 Golden Test Coverage

### Scenarios Defined

| Scenario | Files | Operations | Assertions |
|----------|-------|------------|------------|
| database_cleanup | 7 | 4 DELETE, 2 PRESERVE, 1 WARN | 3 |
| json_cleanup | 6 | 3 RELOCATE, 2 PRESERVE, 1 WARN | 3 |
| markdown_sprawl_cleanup | 7 | 4 DELETE, 3 PRESERVE | 2 |
| **Total** | **20** | **17** | **8** |

### Coverage Matrix

```
Operation Type    | Tests | Status
------------------|-------|--------
DELETE            | 12    | ❌ RED
RELOCATE          | 3     | ❌ RED
PRESERVE          | 7     | ✅ PASS
WARN              | 2     | ⚪ TODO
ROLLBACK          | 0     | ⚪ TODO
```

---

## ✅ Success Criteria

### Green Phase Checklist
- [ ] All 7 golden tests passing
- [ ] 4 cleaner plugins extracted
- [ ] VacuumOrchestrator coordinating cleaners
- [ ] Original .cortex/run_vacuum.py still functional (backward compat)
- [ ] No regression in existing vacuum behavior

### Refactor Phase Checklist
- [ ] Plugin architecture fully implemented
- [ ] Template management working
- [ ] JSON reports generated
- [ ] Dry-run mode functional
- [ ] Rollback capability tested
- [ ] Documentation updated

---

## 🔍 Next Actions

### Immediate (GREEN Phase)
1. **Create cleaner base classes** (`cortex_brain/tier1/orchestrators/cleaners/base.py`)
2. **Extract DatabaseMigrationCleaner** (root *.db deletion)
3. **Extract RootArtifactsCleaner** (JSON relocation)
4. **Extract MarkdownSprawlCleaner** (markdown cleanup)
5. **Create VacuumOrchestrator** (coordinator)
6. **Run golden tests** → Achieve GREEN

### Follow-up (REFACTOR Phase)
1. Add template management for file recreation
2. Enhance observability with structured logging
3. Implement rollback capability
4. Add dashboard integration (JSON reports)
5. Document plugin development guide

---

## 📝 Commit Strategy

### Commits Plan
```
1. test(vacuum): Add golden test patterns for vacuum refactoring
   - 7 golden scenarios defined
   - 20 test files with immutable expectations
   - RED phase: 4 failing, 3 passing

2. refactor(vacuum): Extract cleaner plugin architecture
   - CleanerInterface base class
   - DatabaseMigrationCleaner
   - RootArtifactsCleaner
   - MarkdownSprawlCleaner
   
3. refactor(vacuum): Create VacuumOrchestrator coordinator
   - Orchestrator manages cleaner lifecycle
   - Analysis → Execute → Report pattern
   - GREEN phase: All golden tests passing

4. refactor(vacuum): Add template management
   - Jinja2 templates for file recreation
   - TemplateRecreationCleaner plugin

5. feat(vacuum): Enhance observability
   - Structured logging
   - JSON report generation
   - Dashboard integration
```

---

**Status:** ✅ RED Phase Complete — Golden tests defined, 4 failing as expected  
**Next:** GREEN Phase — Implement cleaner plugins to pass golden tests

---

## Appendix: Test File
**Location:** `tests/unit/tier1/orchestrators/test_vacuum_golden_patterns.py`  
**Lines:** 815  
**Scenarios:** 7  
**Test Classes:** 4  
**Fixtures:** 7
