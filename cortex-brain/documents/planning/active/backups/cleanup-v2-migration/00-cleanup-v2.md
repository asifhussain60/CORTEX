# 🛡️ Cleanup Orchestrator v2 Migration Plan

**Plan ID:** cleanup-v2-migration  
**Feature:** Cleanup Orchestrator Migration to Pure Autonomous Architecture  
**Created:** January 2, 2026  
**Complexity:** TIER 2 (ORCHESTRATOR MIGRATION - SIMPLER)  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.3)  
**Strategy:** Convert maintenance cleanup phase to autonomous orchestrator  
**Estimated Duration:** 4 days

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Foundation & Analysis | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |
| 1 | Core Implementation | `░░░░░░░░░░` | 1.5d | ⏸️ Not Started |
| 2 | Config & Templates | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |
| 3 | Testing & Validation | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 4 | Master Orch Activation | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |

---

## 🎯 Executive Summary

### Migration Goals

Transform Cleanup from **maintenance phase 2** to **standalone autonomous orchestrator**:

**Current State (Maintenance Phase 2):**
- ✅ Cache cleanup (`__pycache__`, `.pytest_cache`, `.mypy_cache`)
- ✅ Log rotation (truncate/archive logs >10MB)
- ✅ Temp file removal (`.tmp`, build artifacts)
- ❌ Part of larger maintenance workflow (not standalone)
- ❌ No state persistence
- ❌ Not Master Orchestrator integrated

**Target State (v2 - AUTONOMOUS):**
- ✅ Standalone orchestrator (usable independently)
- ✅ Pure Python implementation
- ✅ Config-driven cleanup rules
- ✅ State persistence in PlanningStateDB
- ✅ Master Orchestrator integrated
- ✅ Template-driven reports
- ✅ Selective cleanup (cache only, logs only, full cleanup)

### Cleanup Categories

1. **Cache Cleanup** (Priority: HIGH)
   - `__pycache__/`, `*.pyc`, `*.pyo`
   - `.pytest_cache/`, `.mypy_cache/`, `.tox/`
   - `htmlcov/` (coverage reports)
   - `node_modules/.cache/` (if JavaScript)

2. **Log Management** (Priority: MEDIUM)
   - Truncate logs >10MB
   - Archive logs >30 days old
   - Compress archived logs
   - Clean log rotation backups

3. **Build Artifacts** (Priority: MEDIUM)
   - `bin/`, `obj/`, `target/`, `build/`, `dist/`
   - Temp directories

4. **Git Optimization** (Priority: LOW)
   - `git gc` (garbage collection)
   - Prune unreachable objects
   - Optimize pack files

---

## 🏗️ Phase 0: Foundation & Analysis (0.5 days)

### Task 0.1: Current Cleanup Analysis
**Duration:** 2h

Analyze `cortex-maintenance.prompt.md` Phase 2 (Cleanup).

**Deliverables:**
- `context/maintenance-phase-2-analysis.md` - Current cleanup logic
- `context/cleanup-rules.md` - Categorization and rules

### Task 0.2: Migration Strategy
**Duration:** 2h

**File:** `artifacts/migration-strategy.md`

Determine:
- What moves from maintenance to standalone
- Integration points with maintenance workflow
- Backward compatibility approach

---

## 🏛️ Phase 1: Core Implementation (1.5 days)

### Task 1.1: CleanupOrchestratorV2 Base
**Duration:** 6h

**File:** `src/orchestrators/cleanup/cleanup_orchestrator_v2.py`

```python
class CleanupOrchestratorV2(BaseOrchestratorV4_1):
    """
    Cleanup Orchestrator v2 - Autonomous cache/log/artifact cleanup.
    
    Modes:
    - cache: Cache directories only
    - logs: Log management only
    - artifacts: Build artifacts only
    - full: All cleanup categories
    """
    
    def execute(self, **kwargs):
        mode = kwargs.get('mode', 'full')
        target_path = kwargs.get('target_path', '.')
        
        # Execute cleanup based on mode
        if mode == 'cache' or mode == 'full':
            self._cleanup_caches(target_path)
        
        if mode == 'logs' or mode == 'full':
            self._manage_logs(target_path)
        
        if mode == 'artifacts' or mode == 'full':
            self._remove_build_artifacts(target_path)
        
        if mode == 'git':
            self._optimize_git(target_path)
```

### Task 1.2: Cleanup Category Implementations
**Duration:** 6h

**Files:**
- `src/orchestrators/cleanup/cache_cleaner.py`
- `src/orchestrators/cleanup/log_manager.py`
- `src/orchestrators/cleanup/artifact_remover.py`
- `src/orchestrators/cleanup/git_optimizer.py`

---

## 📝 Phase 2: Config & Templates (0.5 days)

### Task 2.1: Manifest
**Duration:** 2h

**File:** `cortex-brain/manifests/orchestrators/cleanup-orchestrator-v2.yaml`

```yaml
cleanup_rules:
  caches:
    patterns: ["__pycache__/", "*.pyc", ".pytest_cache/", ".mypy_cache/"]
    priority: "HIGH"
  
  logs:
    max_size_mb: 10
    archive_after_days: 30
    compress: true
  
  artifacts:
    patterns: ["bin/", "obj/", "target/", "build/", "dist/"]
  
  git:
    enabled: false
    operations: ["gc", "prune"]

modes:
  cache: ["caches"]
  logs: ["logs"]
  artifacts: ["artifacts"]
  full: ["caches", "logs", "artifacts"]
  git: ["git"]
```

### Task 2.2: Templates
**Duration:** 2h

- `cleanup-report.jinja2` - Summary of cleaned items
- `log-rotation-report.jinja2` - Log management details

---

## ✅ Phase 3: Testing & Validation (1 day)

### Task 3.1: Unit Tests
**Duration:** 4h

**Files:**
- `tests/orchestrators/cleanup/test_cleanup_orchestrator_v2.py`
- `tests/orchestrators/cleanup/test_cache_cleaner.py`
- `tests/orchestrators/cleanup/test_log_manager.py`

### Task 3.2: Integration Tests
**Duration:** 4h

**Scenarios:**
1. Cache cleanup: Remove `__pycache__` directories
2. Log rotation: Truncate large logs
3. Selective mode: Cache only (artifacts untouched)
4. Full cleanup: All categories cleaned

---

## 🔴 Phase 4: Master Orchestrator Activation (0.5 days)

### Task 4.1: Master Orchestrator Config
**Duration:** 2h

```yaml
- pattern: "^(cleanup|cleanup cache|cleanup logs|cleanup full).*$"
  orchestrator: "cleanup_orchestrator_v2"
  confidence: 1.0
  match_type: "regex"
  priority: 50
```

### Task 4.2: CORTEX.prompt.md Update
**Duration:** 1h

```markdown
| `cleanup cache` | 🛡️ **Cleanup v2 (AUTONOMOUS)** | Cache cleanup only |
| `cleanup logs` | 🛡️ **Cleanup v2 (AUTONOMOUS)** | Log management only |
| `cleanup full` | 🛡️ **Cleanup v2 (AUTONOMOUS)** | Full cleanup |
```

### Task 4.3: End-to-End Test
**Duration:** 1h

```
User: "cleanup cache"
→ Master Orch routes to cleanup_orchestrator_v2 (mode=cache)
→ Cleanup v2 executes
→ Report: "Removed 45 cache directories (1.2GB freed)"
```

---

## 🎉 Completion Checklist

- [ ] CleanupOrchestratorV2 implemented
- [ ] All 4 categories functional
- [ ] Selective mode operational
- [ ] Config-only manifest
- [ ] 100% test coverage
- [ ] Master Orchestrator routing
- [ ] Integration with maintenance workflow preserved

---

**Status:** ⏸️ NOT STARTED  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.3)  
**Estimated Start:** After Vacuum v2 complete
