# 🛡️ Vacuum Orchestrator v2 Migration Plan

**Plan ID:** vacuum-v2-migration  
**Feature:** Vacuum Orchestrator Migration to Pure Autonomous Architecture  
**Created:** January 2, 2026  
**Complexity:** TIER 3 (ORCHESTRATOR MIGRATION)  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.2)  
**Strategy:** Convert prompt-based GUIDED orchestrator to pure autonomous Python implementation  
**Estimated Duration:** 5 days

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Foundation & Analysis | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 1 | Core Filesystem Engine | `░░░░░░░░░░` | 1.5d | ⏸️ Not Started |
| 2 | Cleanup & Safety Logic | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 3 | Config & Templates | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |
| 4 | Testing & Validation | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |
| 5 | Master Orch Activation | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |

---

## 🎯 Executive Summary

### Migration Goals

Transform Vacuum from **prompt-based GUIDED execution** to **pure autonomous filesystem operations**:

**Current State (v1 - GUIDED):**
- ✅ Comprehensive cleanup categories (temp files, build artifacts, IDE metadata, duplicates)
- ✅ Safety-first approach (dry-run default, checkpoints, rollback)
- ✅ Filesystem traversal with exclude patterns
- ❌ GUIDED orchestrator (CORTEX reads cortex-vacuum.prompt.md and executes)
- ❌ No state persistence
- ❌ Limited rollback granularity
- ❌ Not Master Orchestrator integrated

**Target State (v2 - AUTONOMOUS):**
- ✅ Pure Python implementation (zero prompt interpretation)
- ✅ Atomic filesystem operations with transactions
- ✅ State persistence in PlanningStateDB
- ✅ Granular rollback (file-level, not directory-level)
- ✅ Master Orchestrator integrated
- ✅ Template-driven reports
- ✅ BaseOrchestrator v4.1 compliance

### Success Criteria

**Technical:**
- ✅ Vacuum v2 inherits from BaseOrchestrator v4.1
- ✅ All 5 cleanup categories handled algorithmically
- ✅ Filesystem operations transactional (atomic commits/rollbacks)
- ✅ Config-only manifest (cleanup rules, exclusions, safety thresholds)
- ✅ State tracked in database (files scanned, deleted, moved)
- ✅ 100% test coverage (unit + integration)
- ✅ Master Orchestrator routes "vacuum [path]" → Vacuum v2

**Functional:**
- ✅ Dry-run mode generates accurate preview
- ✅ Checkpoint system preserves rollback capability
- ✅ Aggressive mode removes duplicates + orphans
- ✅ Reorganization follows CORTEX governance
- ✅ Safety validation prevents critical file deletion
- ✅ Progress tracking during long operations

---

## 🏗️ Phase 0: Foundation & Analysis (1 day)

**Goal:** Analyze cortex-vacuum.prompt.md, document filesystem patterns, prepare migration

### Task 0.1: Vacuum v1 Prompt Analysis
**Duration:** 4h

**Analyze:**
- `cortex-vacuum.prompt.md` (1053 lines - v1 specification)
- `src/operations/modules/vacuum/vacuum_orchestrator.py` (if exists - v0 implementation)

**Analysis Deliverables:**
- `context/vacuum-v1-architecture.md`
  - 5 cleanup category specifications
  - Filesystem traversal algorithm
  - Safety validation logic
  - Checkpoint/rollback mechanism

- `context/filesystem-operations-patterns.md`
  - Safe deletion patterns
  - Atomic move operations
  - Symlink creation strategies
  - Permission handling

- `context/safe-deletion-strategies.md`
  - Critical file protection (git metadata, config, source code)
  - Exclude pattern enforcement
  - User confirmation workflows

### Task 0.2: Baseline Testing
**Duration:** 2h

**Actions:**
- Create test filesystem structure
- Run manual vacuum workflow (via current GUIDED orchestrator)
- Document expected behavior
- Capture edge cases (symlinks, permissions, locked files)

**Deliverable:** `context/baseline-test-filesystem.md`

### Task 0.3: Migration Strategy
**Duration:** 2h

**File:** `artifacts/migration-strategy.md`

**Content:**
- Transactional filesystem operation design
- Rollback checkpoint architecture
- Duplicate detection algorithm
- Orphan file identification strategy

### Completion Criteria
- ✅ Vacuum v1 fully documented
- ✅ Filesystem patterns cataloged
- ✅ Test baseline established
- ✅ Migration strategy approved

---

## 🏛️ Phase 1: Core Filesystem Engine (1.5 days)

**Goal:** Implement pure autonomous filesystem operations with transactional safety

### Task 1.1: VacuumOrchestratorV2 Base Class
**Duration:** 4h

**File:** `src/orchestrators/vacuum/vacuum_orchestrator_v2.py`

**Implementation:**
```python
"""
Vacuum Orchestrator v2 - Pure Autonomous Filesystem Cleanup.

Transactional filesystem operations with granular rollback capability.
All logic in Python, manifest contains only cleanup rules and exclusions.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from src.orchestrators.base.base_orchestrator_v4_1 import BaseOrchestratorV4_1
from src.database.planning_state_db import PlanningStateDB
from typing import Dict, Any, List
from pathlib import Path

class VacuumOrchestratorV2(BaseOrchestratorV4_1):
    """
    Vacuum Orchestrator v2 - Pure autonomous filesystem cleanup.
    
    Workflow:
    1. DISCOVERY: Filesystem traversal + categorization
    2. ANALYSIS: Duplicate detection + orphan identification
    3. PLANNING: Generate cleanup plan with safety validation
    4. APPROVAL: User preview (if not auto-approved)
    5. EXECUTION: Atomic filesystem operations
    6. COMPLETION: Report generation + checkpoint verification
    """
    
    def __init__(self, config_path: str, state_db: PlanningStateDB):
        super().__init__(config_path, state_db)
        
        # Load cleanup rules
        self.cleanup_rules = self.config['cleanup_categories']
        self.safety_rules = self.config['safety']
        self.exclude_patterns = self.config['exclusions']
        
        # Initialize filesystem engine
        from src.orchestrators.vacuum.filesystem_engine import FilesystemEngine
        self.fs_engine = FilesystemEngine(
            state_db=state_db,
            safety_rules=self.safety_rules
        )
    
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute vacuum workflow.
        
        Args:
            target_path: Absolute path to vacuum
            dry_run: Preview only (default: True)
            aggressive: Enable duplicate/orphan removal
            reorganize: Move misplaced files
            checkpoint: Create rollback checkpoint
        """
        target_path = Path(kwargs['target_path'])
        dry_run = kwargs.get('dry_run', True)
        
        # Validate target path
        if not target_path.exists():
            return {'status': 'error', 'message': f'Path not found: {target_path}'}
        
        # Create vacuum plan in database
        plan_id = self.state_db.create_plan(
            feature_name=f"Vacuum {target_path}",
            metadata={
                'orchestrator': 'vacuum_v2',
                'target_path': str(target_path),
                'dry_run': dry_run,
                'params': kwargs
            }
        )
        
        try:
            # Phase 1: DISCOVERY
            phase_id = self.state_db.start_phase(plan_id, 1, {'name': 'DISCOVERY'})
            inventory = self._phase_discovery(target_path)
            self.state_db.complete_phase(phase_id)
            
            # Phase 2: ANALYSIS
            phase_id = self.state_db.start_phase(plan_id, 2, {'name': 'ANALYSIS'})
            cleanup_plan = self._phase_analysis(inventory, kwargs)
            self.state_db.complete_phase(phase_id)
            
            # Phase 3: PLANNING (safety validation)
            phase_id = self.state_db.start_phase(plan_id, 3, {'name': 'PLANNING'})
            validated_plan = self._phase_planning(cleanup_plan)
            self.state_db.complete_phase(phase_id)
            
            # Phase 4: APPROVAL (if not auto-approved)
            if not kwargs.get('auto_approve', False) and not dry_run:
                phase_id = self.state_db.start_phase(plan_id, 4, {'name': 'APPROVAL'})
                approved = self._phase_approval(validated_plan)
                self.state_db.complete_phase(phase_id)
                
                if not approved:
                    return {'status': 'cancelled', 'message': 'User rejected'}
            
            # Phase 5: EXECUTION (or dry-run report)
            if dry_run:
                return self._generate_dry_run_report(validated_plan)
            else:
                phase_id = self.state_db.start_phase(plan_id, 5, {'name': 'EXECUTION'})
                execution_result = self._phase_execution(validated_plan, kwargs)
                self.state_db.complete_phase(phase_id)
                
                # Phase 6: COMPLETION
                return self._phase_completion(execution_result)
        
        except Exception as e:
            self.state_db.fail_phase(phase_id, str(e))
            raise
    
    def _phase_discovery(self, target_path: Path) -> Dict[str, Any]:
        """
        Phase 1: DISCOVERY - Filesystem traversal and categorization.
        
        Returns:
            Inventory dict with categorized files:
            {
                'temp_files': [Path(...)],
                'build_artifacts': [Path(...)],
                'ide_metadata': [Path(...)],
                'duplicates': [{hash: ..., paths: [...]}],
                'orphans': [Path(...)]
            }
        """
        return self.fs_engine.scan_directory(
            target_path,
            cleanup_rules=self.cleanup_rules,
            exclude_patterns=self.exclude_patterns
        )
    
    # ... (implement remaining phases)
```

### Task 1.2: Filesystem Engine Implementation
**Duration:** 6h

**File:** `src/orchestrators/vacuum/filesystem_engine.py`

**Key Classes:**
- `FilesystemEngine` - Core scanning and operation engine
- `FilesystemTransaction` - Atomic operation wrapper
- `CheckpointManager` - Rollback checkpoint handling
- `DuplicateDetector` - Hash-based duplicate identification
- `OrphanDetector` - Unused file detection via AST analysis

**Features:**
- Transactional delete (checkpoint before delete, rollback on error)
- Transactional move (atomic rename with rollback)
- Symlink creation (safe linking with validation)
- Permission handling (skip locked/system files)

### Task 1.3: Safety Validation System
**Duration:** 2h

**File:** `src/orchestrators/vacuum/safety_validator.py`

**Validations:**
- Critical file protection (never delete `.git`, source code, config)
- Size threshold enforcement (warn if >1GB deletion)
- Exclusion pattern matching
- User confirmation for aggressive actions

### Completion Criteria
- ✅ VacuumOrchestratorV2 implemented (6 phases)
- ✅ FilesystemEngine operational (scan + execute)
- ✅ Transactional operations with rollback
- ✅ Safety validation prevents critical deletions

---

## 🧹 Phase 2: Cleanup & Safety Logic (1 day)

**Goal:** Implement all 5 cleanup categories with safety guardrails

### Task 2.1: Cleanup Category Implementations
**Duration:** 6h

**Files to Create:**
- `src/orchestrators/vacuum/cleanup/temp_files.py`
- `src/orchestrators/vacuum/cleanup/build_artifacts.py`
- `src/orchestrators/vacuum/cleanup/ide_metadata.py`
- `src/orchestrators/vacuum/cleanup/duplicates.py`
- `src/orchestrators/vacuum/cleanup/orphans.py`

**Each Module:**
- Pattern matching (e.g., `*.tmp`, `__pycache__/`)
- Safety checks (e.g., don't delete if modified <24h)
- Categorization logic (HIGH/MEDIUM/LOW priority)

### Task 2.2: Duplicate Detection
**Duration:** 2h

**Algorithm:**
- Hash all files (SHA256)
- Group by hash (exact duplicates)
- Compare similar files (Levenshtein distance for near-duplicates)
- Keep newest or "correct location" per governance

**Optimizations:**
- Skip files >100MB (slow to hash)
- Cache hashes (don't rehash on subsequent runs)
- Parallel hashing (thread pool)

### Completion Criteria
- ✅ All 5 categories implemented
- ✅ Duplicate detection functional
- ✅ Safety checks prevent critical deletions

---

## 📝 Phase 3: Config & Templates (0.5 days)

**Goal:** Create config-only manifest and report templates

### Task 3.1: Manifest Creation
**Duration:** 2h

**File:** `cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml`

**Structure:**
```yaml
schema_version: "5.0"
orchestrator:
  name: "vacuum_orchestrator"
  version: "2.0"
  type: "autonomous"

cleanup_categories:
  temp_files:
    priority: "HIGH"
    patterns: ["*.tmp", "*.temp", "*.cache", "~*", "*.bak"]
    max_age_days: 7
  
  build_artifacts:
    priority: "HIGH"
    patterns: ["bin/", "obj/", "target/", "build/", "dist/", "__pycache__/"]
    
  ide_metadata:
    priority: "MEDIUM"
    patterns: [".vs/", ".vscode/settings.json", ".idea/"]
    exclusions: [".vscode/launch.json", ".vscode/tasks.json"]
  
  duplicates:
    priority: "MEDIUM"
    algorithm: "hash_based"
    similarity_threshold: 0.95
  
  orphans:
    priority: "LOW"
    detection: "ast_analysis"

safety:
  critical_patterns: [".git/", "*.py", "*.md", "*.yaml", "*.json"]
  size_threshold_mb: 1000
  require_confirmation:
    - duplicates
    - orphans

exclusions:
  - ".git"
  - ".github"
  - "node_modules"
  - "venv"

output_templates:
  dry_run_report: "templates/vacuum/dry-run-report.jinja2"
  completion_report: "templates/vacuum/completion-report.jinja2"
```

### Task 3.2: Template Creation
**Duration:** 2h

**Templates:**
1. `dry-run-report.jinja2` - Preview of planned changes
2. `completion-report.jinja2` - Summary of executed changes
3. `checkpoint-manifest.jinja2` - Rollback instructions

### Completion Criteria
- ✅ Config manifest complete
- ✅ Templates render correctly
- ✅ Manifest validates

---

## ✅ Phase 4: Testing & Validation (0.5 days)

**Goal:** Comprehensive testing with real filesystem scenarios

### Task 4.1: Unit Tests
**Duration:** 2h

**Files:**
- `tests/orchestrators/vacuum/test_vacuum_orchestrator_v2.py`
- `tests/orchestrators/vacuum/test_filesystem_engine.py`
- `tests/orchestrators/vacuum/test_duplicate_detector.py`

**Coverage:** 100%

### Task 4.2: Integration Tests
**Duration:** 2h

**Scenarios:**
1. Dry-run: Scan directory → Generate report (no changes)
2. Temp file cleanup: Delete `.tmp`, `.cache` files
3. Duplicate removal: Keep newest, delete older
4. Rollback: Delete files → Error → Restore from checkpoint
5. Aggressive mode: Duplicates + orphans removed

### Completion Criteria
- ✅ 100% test coverage
- ✅ All integration scenarios pass
- ✅ No regression from v1

---

## 🔴 Phase 5: Master Orchestrator Activation (0.5 days)

**Goal:** Activate Vacuum v2 routing via Master Orchestrator

### Task 5.1: Master Orchestrator Configuration
**Duration:** 2h

**Update:** `cortex-brain/config/master-orchestrator.yaml`

```yaml
- pattern: "^(vacuum|deep clean|organize files).*$"
  orchestrator: "vacuum_orchestrator_v2"
  confidence: 1.0
  match_type: "regex"
  priority: 40
```

### Task 5.2: CORTEX.prompt.md Update
**Duration:** 1h

**Update Intent Router:**
```markdown
| `vacuum [path]` | 🛡️ **Vacuum v2 (AUTONOMOUS)** | `vacuum-orchestrator-v2.yaml` | **HAND-OFF** → Filesystem cleanup |
```

### Task 5.3: End-to-End Test
**Duration:** 1h

**Test:**
```
User: "vacuum /path/to/directory"
→ Master Orch routes to vacuum_orchestrator_v2
→ Vacuum v2 executes (dry-run by default)
→ Report generated
```

### Completion Criteria
- ✅ Master Orchestrator routes vacuum commands
- ✅ End-to-end test passes
- ✅ Vacuum v2 LIVE

---

## 🎉 Migration Completion Checklist

### Technical
- [ ] VacuumOrchestratorV2 implemented
- [ ] Transactional filesystem operations
- [ ] All 5 cleanup categories functional
- [ ] Safety validation prevents critical deletions
- [ ] Config-only manifest
- [ ] 100% test coverage
- [ ] Master Orchestrator routing

### Functional
- [ ] Dry-run generates accurate preview
- [ ] Checkpoint/rollback operational
- [ ] Duplicate detection accurate
- [ ] Orphan detection functional
- [ ] Progress tracking during execution

### Documentation
- [ ] v1 analysis complete
- [ ] v2 architecture documented
- [ ] User guide updated

---

**Status:** ⏸️ NOT STARTED  
**Parent Plan:** cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/00-MASTER-PLAN-V5.md  
**Estimated Start:** After ADO v2 migration complete (Phase 6.1)
