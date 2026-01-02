# Cleanup Orchestrator v2 Migration Strategy

**Plan:** cleanup-v2-migration  
**Created:** January 2, 2026  
**Purpose:** Define strategy for migrating cleanup from maintenance Phase 2 to standalone autonomous orchestrator

---

## 🎯 Migration Goals

### Primary Objectives
1. **Standalone Orchestrator:** Usable independently via Master Orchestrator routing
2. **Pure Autonomous:** Python-driven execution, config-only manifests
3. **Selective Modes:** Cache, logs, artifacts, full, git (user choice)
4. **State Persistence:** Track cleanup sessions in PlanningStateDB
5. **Backward Compatible:** Maintenance pipeline continues to work

### Success Criteria
- ✅ BaseOrchestrator v4.1 compliance
- ✅ Master Orchestrator routing operational
- ✅ 95%+ test coverage (40+ tests)
- ✅ Selective mode support (5 modes)
- ✅ State persistence in PlanningStateDB
- ✅ Template-driven reporting
- ✅ Zero breaking changes to maintenance pipeline

---

## 🏗️ Architecture Design

### Component Structure

```
src/orchestrators/cleanup/
├── __init__.py
├── cleanup_orchestrator_v2.py      # Main orchestrator (BaseOrchestrator v4.1)
├── cache_cleaner.py                 # Group 1: Cache cleanup
├── log_manager.py                   # Group 2: Log management
├── artifact_remover.py              # Group 3: Artifact removal
├── git_optimizer.py                 # Group 4: Git optimization
└── cleanup_engine.py                # Shared scanning/deletion logic
```

### Class Hierarchy

```python
BaseOrchestratorV4_1
    ↓
CleanupOrchestratorV2
    ├── CacheCleaner
    ├── LogManager
    ├── ArtifactRemover
    └── GitOptimizer
```

---

## 📋 Phase-by-Phase Migration

### Phase 1: Core Implementation (1.5 days)

#### Task 1.1: CleanupOrchestratorV2 Base (6h)
**File:** `src/orchestrators/cleanup/cleanup_orchestrator_v2.py`

**Implementation:**
```python
from src.orchestrators.base.base_orchestrator_v4_1 import BaseOrchestratorV4_1
from src.database.planning_state_db import PlanningStateDB
from typing import Dict, Any

class CleanupOrchestratorV2(BaseOrchestratorV4_1):
    """
    Autonomous cleanup orchestrator v2.
    
    Modes:
    - cache: Cache directories only (HIGH priority, safe)
    - logs: Log management only (MEDIUM priority, rotation)
    - artifacts: Build artifacts only (MEDIUM priority, backups)
    - full: All cleanup categories (cache + logs + artifacts)
    - git: Git optimization only (LOW priority, slow)
    """
    
    def __init__(self, config_path: str, state_db: PlanningStateDB):
        super().__init__(config_path, state_db)
        
        # Initialize category cleaners
        self.cache_cleaner = CacheCleaner(self.config)
        self.log_manager = LogManager(self.config)
        self.artifact_remover = ArtifactRemover(self.config)
        self.git_optimizer = GitOptimizer(self.config)
    
    def execute(self, mode: str = "full", **kwargs) -> Dict[str, Any]:
        """
        Execute cleanup based on mode.
        
        Args:
            mode: Cleanup mode (cache, logs, artifacts, full, git)
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with cleanup results
        """
        # Validate mode
        valid_modes = ["cache", "logs", "artifacts", "full", "git"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Valid: {valid_modes}")
        
        # Create session
        session_id = self.state_db.create_session(
            orchestrator="cleanup_orchestrator_v2",
            intent=f"cleanup {mode}",
            metadata={"mode": mode}
        )
        
        try:
            # Execute based on mode
            if mode == "cache":
                result = self.cache_cleaner.execute()
            elif mode == "logs":
                result = self.log_manager.execute()
            elif mode == "artifacts":
                result = self.artifact_remover.execute()
            elif mode == "full":
                result = self._execute_full_cleanup()
            elif mode == "git":
                result = self.git_optimizer.execute()
            
            # Save state
            self.state_db.save_session_artifact(
                session_id=session_id,
                artifact_type="cleanup_result",
                artifact_data=result
            )
            
            # Render report
            report = self.render_template(
                template_name="cleanup-report.jinja2",
                context={"result": result, "mode": mode}
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "mode": mode,
                "statistics": result["statistics"],
                "report": report
            }
        
        except Exception as e:
            self.state_db.fail_session(session_id, str(e))
            raise
    
    def _execute_full_cleanup(self) -> Dict[str, Any]:
        """Execute all cleanup categories (cache + logs + artifacts)"""
        results = []
        
        # Execute in priority order
        results.append(self.cache_cleaner.execute())
        results.append(self.log_manager.execute())
        results.append(self.artifact_remover.execute())
        
        # Aggregate statistics
        return self._aggregate_results(results)
```

**Key Features:**
- Inherits from BaseOrchestrator v4.1
- Mode-based execution
- State persistence via PlanningStateDB
- Template rendering via Jinja2
- Session tracking

---

#### Task 1.2: Category Implementations (6h)

**1. CacheCleaner** (`cache_cleaner.py`)
```python
class CacheCleaner:
    """Cache cleanup (Group 1) - Python cache, generic cache, temp dirs"""
    
    CATEGORIES = [
        "python_cache",
        "cache",
        "sweeper",
        "temp_directories",
        "empty_directories"
    ]
    
    def execute(self) -> Dict[str, Any]:
        """Execute cache cleanup"""
        # Use CleanupEngine to scan and delete
        result = self.cleanup_engine.process_categories(self.CATEGORIES)
        return result
```

**2. LogManager** (`log_manager.py`)
```python
class LogManager:
    """Log management (Group 2) - Rotation, archiving, old log deletion"""
    
    CATEGORIES = [
        "logs",
        "build_output",
        "session_summaries",
        "system_refactor_reports",
        "duplicate_cleanup_reports"
    ]
    
    def execute(self) -> Dict[str, Any]:
        """Execute log management"""
        result = self.cleanup_engine.process_categories(self.CATEGORIES)
        
        # Apply log rotation
        self._rotate_large_logs(threshold_mb=10)
        
        return result
    
    def _rotate_large_logs(self, threshold_mb: int) -> None:
        """Rotate logs larger than threshold"""
        # Implementation...
```

**3. ArtifactRemover** (`artifact_remover.py`)
```python
class ArtifactRemover:
    """Artifact removal (Group 3) - Backups, reports, build artifacts"""
    
    CATEGORIES = [
        "backup_archive",
        "story_backups",
        "phase_reports",
        # ...(15 categories total)
    ]
    
    def execute(self) -> Dict[str, Any]:
        """Execute artifact removal"""
        result = self.cleanup_engine.process_categories(self.CATEGORIES)
        return result
```

**4. GitOptimizer** (`git_optimizer.py`)
```python
class GitOptimizer:
    """Git optimization (Group 4) - gc, prune, repack"""
    
    def execute(self) -> Dict[str, Any]:
        """Execute git optimization"""
        result = {
            "operations": [],
            "space_freed_mb": 0,
            "duration_seconds": 0
        }
        
        # Execute git operations
        result["operations"].append(self._git_gc())
        result["operations"].append(self._git_prune())
        result["operations"].append(self._git_repack())
        
        return result
```

**5. CleanupEngine** (`cleanup_engine.py`)
```python
class CleanupEngine:
    """Shared scanning and deletion logic (reuse from DynamicCleanupOrchestrator)"""
    
    def process_categories(self, categories: List[str]) -> Dict[str, Any]:
        """Scan and clean specified categories"""
        # Reuse logic from src/plugins/cleanup_orchestrator.py
        # - scan_category()
        # - apply_retention_policy()
        # - _execute_cleanup_actions()
```

---

### Phase 2: Config & Templates (0.5 days)

#### Task 2.1: Manifest (2h)
**File:** `cortex-brain/manifests/orchestrators/cleanup-orchestrator-v2.yaml`

```yaml
orchestrator: cleanup_orchestrator_v2
version: "2.0.0"
autonomous: true
base_orchestrator: "v4.1"

modes:
  cache:
    description: "Clean cache directories only"
    categories: ["python_cache", "cache", "sweeper", "temp_directories", "empty_directories"]
    priority: "HIGH"
    confirmation_required: false
    estimated_duration_seconds: 10
    expected_space_freed_mb: 1000
  
  logs:
    description: "Manage logs (rotation, archiving, deletion)"
    categories: ["logs", "build_output", "session_summaries", "system_refactor_reports", "duplicate_cleanup_reports"]
    priority: "MEDIUM"
    confirmation_required: true
    log_rotation_threshold_mb: 10
    estimated_duration_seconds: 10
    expected_space_freed_mb: 250
  
  artifacts:
    description: "Remove build artifacts and backups"
    categories: ["backup_archive", "story_backups", "phase_reports", ...]
    priority: "MEDIUM"
    confirmation_required: true
    retention_days: 30
    estimated_duration_seconds: 60
    expected_space_freed_mb: 2500
  
  full:
    description: "Full cleanup (cache + logs + artifacts)"
    includes: ["cache", "logs", "artifacts"]
    priority: "MEDIUM"
    confirmation_required: true
    estimated_duration_seconds: 80
    expected_space_freed_mb: 3750
  
  git:
    description: "Git repository optimization"
    operations: ["gc", "prune", "repack"]
    priority: "LOW"
    confirmation_required: false
    estimated_duration_seconds: 180
    expected_space_freed_mb: 100

# Cleanup rules reference
rules_file: "cortex-brain/cleanup-rules.yaml"

# Protected directories
protected_directories:
  - "cortex-brain/tier1"
  - "cortex-brain/tier2"
  - "cortex-brain/tier3"
  - ".git"
  - "src"
  - "tests"
  - "cortex-brain/documents"

# Safety settings
safety:
  max_recursion_depth: 15
  require_git_clean: false
  create_rollback_manifest: true
```

---

#### Task 2.2: Templates (2h)

**1. Cleanup Report Template** (`cleanup-report.jinja2`)
```jinja2
# 🧹 Cleanup Report - {{ mode|title }} Mode

**Orchestrator:** Cleanup v2  
**Mode:** {{ mode }}  
**Timestamp:** {{ result.timestamp }}  
**Duration:** {{ result.statistics.execution_time_seconds }}s

---

## 📊 Statistics

| Metric | Count |
|--------|-------|
| Files Scanned | {{ result.statistics.files_scanned | format_number }} |
| Files Deleted | {{ result.statistics.files_deleted | format_number }} |
| Files Archived | {{ result.statistics.files_archived | format_number }} |
| Folders Deleted | {{ result.statistics.folders_deleted | format_number }} |
| Space Freed | {{ result.statistics.space_freed_mb | format_number }} MB |

---

## 📂 Categories Processed

{% for category, data in result.categories.items() %}
### {{ category }}
- **Items:** {{ data.count }}
- **Size:** {{ data.size_mb | format_number }} MB

{% endfor %}

---

## ⚠️ Errors & Warnings

{% if result.errors %}
**Errors:**
{% for error in result.errors %}
- {{ error }}
{% endfor %}
{% else %}
✅ No errors
{% endif %}

{% if result.warnings %}
**Warnings:**
{% for warning in result.warnings %}
- {{ warning }}
{% endfor %}
{% endif %}

---

✅ **Cleanup complete!**
```

**2. Log Rotation Template** (`log-rotation-report.jinja2`)
```jinja2
# 📋 Log Rotation Report

**Rotated:** {{ rotated_count }} logs  
**Archived:** {{ archived_count }} logs  
**Deleted:** {{ deleted_count }} old logs

---

## Rotated Logs

{% for log in rotated_logs %}
- `{{ log.path }}` ({{ log.size_mb }} MB → {{ log.new_size_mb }} MB)
{% endfor %}

---

✅ **Log rotation complete!**
```

---

### Phase 3: Testing & Validation (1 day)

#### Task 3.1: Unit Tests (4h)

**File:** `tests/orchestrators/cleanup/test_cleanup_orchestrator_v2.py`

**Test Categories:**
1. **Mode Detection** (8 tests)
   - Valid modes accepted
   - Invalid modes rejected
   - Default mode (full) applied

2. **Cache Cleanup** (10 tests)
   - Python cache removal
   - Generic cache removal
   - Temp directory cleanup
   - Empty directory removal
   - Protected paths skipped

3. **Log Management** (10 tests)
   - Log rotation (>10MB)
   - Old log deletion (>30 days)
   - Log archiving
   - Report cleanup (keep 5 recent)

4. **Artifact Removal** (10 tests)
   - Backup cleanup (keep 5 recent)
   - Root clutter removal
   - Legacy file deletion
   - Protected paths skipped

5. **Git Optimization** (4 tests)
   - Git gc execution
   - Git prune execution
   - Git repack execution
   - Error handling

6. **State Persistence** (4 tests)
   - Session creation
   - Artifact saving
   - Session completion
   - Session failure

7. **Template Rendering** (2 tests)
   - Report generation
   - Log rotation report

**Target:** 48 tests, 95%+ coverage

---

#### Task 3.2: Integration Tests (4h)

**File:** `tests/orchestrators/cleanup/test_cleanup_integration.py`

**Test Scenarios:**
1. **End-to-End Cleanup** (6 tests)
   - Cache mode E2E
   - Logs mode E2E
   - Artifacts mode E2E
   - Full mode E2E
   - Git mode E2E
   - Error recovery E2E

2. **Master Orchestrator Integration** (4 tests)
   - Pattern matching (`cleanup cache`)
   - Mode extraction from user input
   - Orchestrator invocation
   - Result propagation

3. **Maintenance Pipeline Integration** (2 tests)
   - Phase 0 invocation (maintenance)
   - Backward compatibility (CLI)

**Target:** 12 tests, 90%+ coverage

---

### Phase 4: Master Orchestrator Activation (0.5 days)

#### Task 4.1: Routing Configuration (2h)

**File:** `cortex-brain/config/master-orchestrator.yaml`

**Add routing patterns:**
```yaml
cleanup_v2:
  patterns:
    - "^cleanup\\s+cache.*$"
    - "^cleanup\\s+logs.*$"
    - "^cleanup\\s+artifacts.*$"
    - "^cleanup\\s+full.*$"
    - "^cleanup\\s+git.*$"
    - "^cleanup$"  # Default to full
  orchestrator: "cleanup_orchestrator_v2"
  confidence: 1.0
  match_type: "regex"
  priority: 50
  mode_extraction:
    pattern: "^cleanup\\s+(cache|logs|artifacts|full|git).*$"
    default: "full"
```

---

#### Task 4.2: CORTEX.prompt.md Update (1h)

**File:** `.github/prompts/CORTEX.prompt.md`

**Add to Intent Router:**
```markdown
| `cleanup cache`, `cleanup logs`, `cleanup artifacts`, `cleanup full`, `cleanup git` | 🛡️ **Cleanup v2 (AUTONOMOUS)** | `cleanup-orchestrator-v2.yaml` | Selective cleanup modes |
```

---

#### Task 4.3: End-to-End Validation (1h)

**Test Flow:**
```
User: "cleanup cache"
  ↓
Master Orchestrator.route_request()
  ↓
Pattern Match: "^cleanup\s+cache.*$"
  ↓
Mode Extraction: "cache"
  ↓
CleanupOrchestratorV2.execute(mode="cache")
  ↓
CacheCleaner.execute()
  ↓
Report: "Deleted 120 cache files, freed 800MB"
```

**Validation Checks:**
- ✅ Pattern matching works
- ✅ Mode extraction correct
- ✅ Orchestrator executes
- ✅ Report generated
- ✅ State persisted

---

## 🔄 Backward Compatibility

### Maintenance Pipeline Integration

**No Breaking Changes:**
- ✅ Maintenance Phase 0 continues to work
- ✅ CLI invocation preserved: `python src/plugins/cleanup_orchestrator.py`
- ✅ Report format unchanged (JSON structure)
- ✅ Protected directories unchanged

**Migration Path:**
1. **Phase 1:** CleanupOrchestratorV2 created (new entry point)
2. **Phase 2:** Maintenance Phase 0 updated to use v2 (optional)
3. **Phase 3:** CLI wrapper updated to use v2 (optional)
4. **Phase 4:** Old orchestrator deprecated (optional, keep for CLI)

**Recommendation:** Keep both orchestrators for 1-2 release cycles.

---

## 📊 Success Metrics

### Implementation Quality
| Metric | Target | Actual |
|--------|--------|--------|
| Lines of Code | ~1500 | TBD |
| Test Coverage | 95%+ | TBD |
| Test Count | 60+ | TBD |
| BaseOrchestrator Compliance | 100% | TBD |

### Performance Benchmarks
| Mode | Duration Target | Space Freed Target |
|------|----------------|-------------------|
| cache | <10s | 1000MB+ |
| logs | <10s | 250MB+ |
| artifacts | <60s | 2500MB+ |
| full | <80s | 3750MB+ |
| git | <180s | 100MB+ |

### User Experience
- ✅ Selective mode support (5 modes)
- ✅ Confirmation prompts (medium risk)
- ✅ Clear progress reporting
- ✅ Detailed error messages
- ✅ Template-driven reports

---

## 🎯 Rollout Plan

### Week 1: Implementation
- Day 1-2: Phase 1 (Core Implementation)
- Day 2.5: Phase 2 (Config & Templates)

### Week 2: Testing & Activation
- Day 3-4: Phase 3 (Testing & Validation)
- Day 4.5: Phase 4 (Master Orch Activation)

### Post-Launch
- Week 3: Monitor usage metrics
- Week 4: Gather user feedback
- Week 5: Iterate based on feedback

---

## ⚠️ Risks & Mitigations

### Risk 1: Data Loss
**Mitigation:**
- Protected directories hardcoded
- Rollback manifests created
- Confirmation prompts for medium risk
- Extensive testing before launch

### Risk 2: Performance Degradation
**Mitigation:**
- Recursion limits (max depth: 15)
- Async scanning (future enhancement)
- Selective modes (avoid full cleanup overhead)

### Risk 3: Maintenance Pipeline Breakage
**Mitigation:**
- Keep old orchestrator operational
- Gradual migration (Phase 0 updated last)
- Backward compatibility testing

---

## ✅ Phase 0 Completion Criteria

- ✅ Current cleanup analysis complete (`maintenance-phase-2-analysis.md`)
- ✅ Cleanup rules categorized (`cleanup-rules.md`)
- ✅ Migration strategy documented (this file)
- ✅ Architecture designed
- ✅ Implementation plan defined
- ✅ Testing strategy defined
- ✅ Rollout plan created

---

**Strategy Complete:** January 2, 2026  
**Created By:** CORTEX Planning System v5  
**Next:** Phase 1 (Core Implementation - CleanupOrchestratorV2)
