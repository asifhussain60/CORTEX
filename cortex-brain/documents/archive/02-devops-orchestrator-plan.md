# 🔧 DevOps Orchestrator - Sub-Plan

**Purpose:** Unified git operations, CI/CD, deployments, system maintenance, and cleanup  
**Complexity:** HIGH (8 files consolidated, cross-cutting concerns)  
**LOC:** 1,500 (from 1,779 existing → optimized consolidation)  
**Test Strategy:** SMOKE TEST ONLY (2 tests: initialization + git checkpoint workflow)

---

## 📋 Navigation

- **Master Plan:** [orchestration-master-plan.md](../orchestration-master-plan.md)
- **Previous:** TDD Orchestrator (Phase 2 Complete)
- **Next:** [QA Orchestrator Plan](03-qa-orchestrator-plan.md)
- **Workflow YAML:** `src/orchestration_3_0/workflows/devops_workflow.yaml`

---

## 1️⃣ Existing State (Current Implementation)

### Current Files Being Consolidated

| File | LOC | Purpose | Key Features |
|------|-----|---------|--------------|
| `src/orchestrators/git_checkpoint_orchestrator.py` | 302 | TDD phase checkpoints | Auto-commits at RED/GREEN/REFACTOR boundaries |
| `src/orchestrators/git_sync_and_optimize.py` | 800 | Git sync + optimization | 7-phase workflow: stash → pull → merge → align → optimize → cleanup → push |
| `src/operations/deploy.py` | 120 | Deployment wrapper | 19 validation gates, publish to branch |
| `src/operations/cleanup.py` | 557 | Workspace cleanup | Temp files, cache, logs, build artifacts removal |

**Total LOC:** 1,779 lines across 4 files  
**Target LOC:** 1,500 lines (16% reduction through consolidation + removal of duplicated git operations)

**Note:** Master plan originally listed "8 orchestrators (5,200 LOC)" but actual audit finds 4 files (1,779 LOC). The remaining files (system_maintenance, holistic_cleanup, publish_branch, git_sync variants) appear to have been refactored/removed prior to this audit.

### Current DevOps Workflows

**1. Git Checkpoint Workflow (TDD Integration)**
- **Trigger:** After each TDD phase (RED/GREEN/REFACTOR)
- **Process:** Create lightweight git commit with phase metadata
- **Features:** Rollback capability, audit trail, progress tracking
- **Integration:** Called by TDD Orchestrator

**2. Git Sync & Optimize Workflow**
- **Phases:**
  1. **Stash:** Save local work with timestamp
  2. **Pull:** Fetch and merge from remote
  3. **Merge:** Auto-resolve or prompt for conflicts
  4. **Align:** Run system alignment validation
  5. **Optimize:** Performance improvements
  6. **Cleanup:** Remove obsolete artifacts
  7. **Push:** Sync to remote
- **Safety:** Rollback on failure, conflict detection, validation checkpoints

**3. Deployment Workflow**
- **Gates:** 19 mandatory validation checks
- **Target:** Publish branch (configurable, default: main)
- **Pre-flight:** Optional alignment check
- **Dry Run:** Preview mode for validation

**4. Cleanup Workflow**
- **Categories:** Temp files, cache dirs, old logs, build artifacts
- **Safety:** Never deletes source code, critical files protected
- **Metrics:** Space freed, files removed, errors logged

### Current Issues & Pain Points

**Fragmentation:**
- Git operations scattered across 2 orchestrators + operations files
- Duplicated git command execution (stash, pull, push logic in multiple places)
- No unified state machine for multi-phase workflows
- Cleanup logic embedded in sync orchestrator AND separate operation file

**Reliability:**
- No session persistence (sync orchestrator state lost on crash)
- Manual rollback required on merge conflicts
- Cleanup can't be retried if partial failure
- No dependency injection (hardcoded paths)

**Scalability:**
- Single-project focus (no multi-tenant support)
- No RBAC (anyone can trigger deployment)
- No cross-project deployment coordination

---

## 2️⃣ New Structure

### Target Architecture

```
src/orchestration_3_0/orchestrators/devops/
├── __init__.py
├── devops_orchestrator.py           # Main orchestrator (400 LOC)
├── git_operations.py                # Git commands abstraction (300 LOC)
├── checkpoint_manager.py            # TDD checkpoint creation (200 LOC)
├── deployment_engine.py             # Deployment with 19 gates (250 LOC)
├── cleanup_engine.py                # Workspace cleanup (200 LOC)
└── sync_coordinator.py              # 7-phase sync workflow (150 LOC)
```

**Total Target LOC:** 1,500 lines (16% reduction from 1,779)

### Component Responsibilities

**Main Orchestrator (`devops_orchestrator.py` - 400 LOC)**
- Extends `BaseOrchestrator`
- State machine integration (INITIALIZED → GIT_CHECKPOINT → GIT_SYNC → DEPLOY → CLEANUP → COMPLETED)
- DI container registration
- Session manager persistence
- Workflow coordination

**Git Operations (`git_operations.py` - 300 LOC)**
- Unified git command abstraction
- `execute_git()` method with error handling
- Common operations: stash, pull, push, merge, status, log
- Subprocess execution with timeout
- Git repository validation

**Checkpoint Manager (`checkpoint_manager.py` - 200 LOC)**
- TDD phase checkpoint creation
- Auto-commit with metadata (session_id, phase, timestamp)
- Rollback to previous checkpoint
- Audit trail generation
- Integration with TDD Orchestrator

**Deployment Engine (`deployment_engine.py` - 250 LOC)**
- 19 validation gates (alignment, tests, docs, version)
- Publish to target branch (main, staging, dev)
- Dry run mode for validation
- Pre-flight checks (alignment optional)
- Post-deployment verification

**Cleanup Engine (`cleanup_engine.py` - 200 LOC)**
- 4 cleanup categories: temp files, cache, logs, build artifacts
- Safety checks (never delete source code)
- Space freed metrics
- Dry run support
- Error recovery

**Sync Coordinator (`sync_coordinator.py` - 150 LOC)**
- 7-phase workflow: stash → pull → merge → align → optimize → cleanup → push
- Conflict detection and resolution
- Rollback on failure
- Validation checkpoints between phases

---

## 3️⃣ State Machine Design

### DevOps Workflow States

```
INITIALIZED
  ↓
GIT_CHECKPOINT_VALIDATING_DOR
  ↓ (DoR: TDD phase complete)
GIT_CHECKPOINT_EXECUTING
  ↓ (creates commit)
GIT_CHECKPOINT_VALIDATING_DOD
  ↓ (DoD: commit created successfully)
GIT_SYNC_VALIDATING_DOR
  ↓ (DoR: clean working directory OR stash successful)
GIT_SYNC_EXECUTING
  ↓ (7-phase sync)
GIT_SYNC_VALIDATING_DOD
  ↓ (DoD: synced with remote, no conflicts)
DEPLOY_VALIDATING_DOR
  ↓ (DoR: all 19 gates pass)
DEPLOY_EXECUTING
  ↓ (publish to branch)
DEPLOY_VALIDATING_DOD
  ↓ (DoD: published successfully)
CLEANUP_VALIDATING_DOR
  ↓ (DoR: no critical operations running)
CLEANUP_EXECUTING
  ↓ (remove temp files, cache, logs)
CLEANUP_VALIDATING_DOD
  ↓ (DoD: cleanup complete, space freed)
COMPLETED
```

### Transition Guards

- **GIT_CHECKPOINT → GIT_SYNC:** TDD phase committed
- **GIT_SYNC → DEPLOY:** No merge conflicts, alignment passed
- **DEPLOY → CLEANUP:** Deployment successful
- **CLEANUP → COMPLETED:** No errors, space freed

---

## 4️⃣ Integration Points

### TDD Orchestrator Integration

**TDD triggers checkpoint:**
```python
# After RED phase complete
devops_orchestrator.execute_phase("GIT_CHECKPOINT", {
    "session_id": tdd_session_id,
    "checkpoint_type": "RED",
    "message": "RED phase complete - tests failing"
})
```

### Planning Orchestrator Integration

**Planning triggers deployment:**
```python
# After feature planning complete
devops_orchestrator.execute_phase("DEPLOY", {
    "branch": "feature/user-auth",
    "dry_run": False,
    "skip_align": False
})
```

### Execution Orchestrator Integration

**Execution coordinates multi-orchestrator workflows:**
```python
# Execute TDD → DevOps checkpoint → TDD → DevOps deploy
execution_orchestrator.execute_plan({
    "phases": [
        {"orchestrator": "tdd", "phase": "RED"},
        {"orchestrator": "devops", "phase": "GIT_CHECKPOINT"},
        {"orchestrator": "tdd", "phase": "GREEN"},
        {"orchestrator": "devops", "phase": "GIT_CHECKPOINT"},
        {"orchestrator": "tdd", "phase": "REFACTOR"},
        {"orchestrator": "devops", "phase": "GIT_CHECKPOINT"},
        {"orchestrator": "devops", "phase": "DEPLOY"}
    ]
})
```

---

## 5️⃣ Implementation Details

### Git Operations Component

**Purpose:** Unified git command execution

**Key Methods:**
```python
class GitOperations:
    def execute_git(self, args: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Execute git command with error handling."""
        
    def stash_save(self, message: str) -> bool:
        """Stash current work."""
        
    def pull_remote(self, remote: str = "origin", branch: str = "main") -> bool:
        """Pull from remote branch."""
        
    def push_remote(self, remote: str = "origin", branch: str = "main", force: bool = False) -> bool:
        """Push to remote branch."""
        
    def get_status(self) -> Dict[str, Any]:
        """Get current git status."""
        
    def create_commit(self, message: str, files: List[str] = None) -> str:
        """Create commit with message."""
```

### Checkpoint Manager Component

**Purpose:** TDD phase checkpoints

**Key Methods:**
```python
class CheckpointManager:
    def create_checkpoint(
        self,
        session_id: str,
        checkpoint_type: str,  # RED, GREEN, REFACTOR
        message: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create TDD phase checkpoint."""
        
    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """Rollback to previous checkpoint."""
        
    def list_checkpoints(self, session_id: str) -> List[Dict[str, Any]]:
        """List all checkpoints for session."""
        
    def get_audit_trail(self, session_id: str) -> Dict[str, Any]:
        """Generate audit trail for TDD session."""
```

### Deployment Engine Component

**Purpose:** Production deployment with validation gates

**19 Validation Gates:**
1. Alignment check (0 issues)
2. All tests passing
3. Documentation up-to-date
4. Version bumped correctly
5. Changelog updated
6. No hardcoded secrets
7. No debug code
8. Code coverage ≥ 80%
9. No TODOs in production code
10. Dependencies up-to-date
11. Security scan clean
12. Performance benchmarks passing
13. Database migrations tested
14. API contracts validated
15. Configuration validated
16. Build successful
17. Smoke tests passing
18. Rollback plan documented
19. Stakeholder approval (manual gate)

**Key Methods:**
```python
class DeploymentEngine:
    def validate_gates(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run all 19 validation gates."""
        
    def publish_to_branch(self, branch: str, dry_run: bool = False) -> bool:
        """Publish to target branch."""
        
    def verify_deployment(self, branch: str) -> bool:
        """Post-deployment verification."""
        
    def rollback_deployment(self, checkpoint_id: str) -> bool:
        """Rollback to previous deployment."""
```

### Cleanup Engine Component

**Purpose:** Workspace cleanup

**Cleanup Categories:**
- **Temp Files:** `*.tmp`, `*.temp`, `*.bak`
- **Cache Dirs:** `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- **Old Logs:** Logs older than 30 days
- **Build Artifacts:** `dist/`, `build/`, `*.pyc`, `*.pyo`

**Safety Checks:**
- Never delete `.py`, `.md`, `.yaml`, `.json` source files
- Protected directories: `src/`, `tests/`, `cortex-brain/`, `.git/`
- Dry run mode for validation

**Key Methods:**
```python
class CleanupEngine:
    def cleanup_workspace(
        self,
        categories: List[str],  # temp_files, cache_dirs, old_logs, build_artifacts
        dry_run: bool = False,
        max_age_days: int = 30
    ) -> Dict[str, Any]:
        """Clean workspace by category."""
        
    def calculate_space_to_free(self) -> int:
        """Estimate space that can be freed."""
        
    def is_safe_to_delete(self, path: Path) -> bool:
        """Check if file/dir is safe to delete."""
```

### Sync Coordinator Component

**Purpose:** 7-phase sync workflow

**Phase Details:**
1. **Stash:** Save local work with timestamp message
2. **Pull:** Fetch and merge from remote (fast-forward preferred)
3. **Merge:** Auto-resolve conflicts OR prompt user
4. **Align:** Run system alignment to validate integration
5. **Optimize:** Performance improvements (optional)
6. **Cleanup:** Remove obsolete artifacts (optional)
7. **Push:** Sync merged changes to remote

**Conflict Resolution Strategies:**
- **Auto-merge:** Ours (keep local), Theirs (keep remote), Both (manual merge)
- **Rollback:** Restore stashed work, abort merge
- **Manual:** Pause workflow, wait for user resolution

**Key Methods:**
```python
class SyncCoordinator:
    def execute_sync_workflow(
        self,
        remote: str = "origin",
        branch: str = "main",
        auto_merge_strategy: str = "prompt"  # ours, theirs, both, prompt
    ) -> Dict[str, Any]:
        """Execute 7-phase sync workflow."""
        
    def detect_conflicts(self) -> List[str]:
        """Detect merge conflicts."""
        
    def resolve_conflicts(self, strategy: str) -> bool:
        """Resolve conflicts using strategy."""
        
    def rollback_sync(self, stash_id: str) -> bool:
        """Rollback sync, restore stashed work."""
```

---

## 6️⃣ Configuration

### DevOps Workflow YAML

**File:** `src/orchestration_3_0/workflows/devops_workflow.yaml`

```yaml
name: devops_workflow
version: 1.0.0
orchestrator: devops

phases:
  - name: GIT_CHECKPOINT
    description: Create TDD phase checkpoint
    dor:
      - tdd_phase_complete
      - working_directory_clean_or_changes_staged
    dod:
      - commit_created
      - checkpoint_id_generated
    timeout: 60  # 1 minute
    
  - name: GIT_SYNC
    description: Sync with remote (7-phase workflow)
    dor:
      - working_directory_clean_or_stashed
      - remote_accessible
    dod:
      - synced_with_remote
      - no_merge_conflicts
      - alignment_passed
    timeout: 600  # 10 minutes
    
  - name: DEPLOY
    description: Deploy to target branch (19 gates)
    dor:
      - all_19_gates_passed
      - target_branch_specified
    dod:
      - published_to_branch
      - deployment_verified
    timeout: 900  # 15 minutes
    
  - name: CLEANUP
    description: Clean workspace
    dor:
      - no_critical_operations_running
    dod:
      - cleanup_complete
      - space_freed_measured
    timeout: 300  # 5 minutes

metrics:
  - checkpoint_count
  - sync_duration
  - deployment_success_rate
  - space_freed_mb

validation:
  git_available: true
  min_disk_space_mb: 100
  max_deployment_time_minutes: 15
```

---

## 7️⃣ Testing Strategy

### Smoke Tests (2 tests)

**Test 1: Initialization**
```python
def test_devops_orchestrator_initialization():
    """Verify DevOps orchestrator initializes correctly."""
    state_machine = StateMachine()
    container = DependencyContainer()
    orchestrator = DevOpsOrchestrator(state_machine, container)
    
    assert orchestrator is not None
    assert orchestrator.git_operations is not None
    assert orchestrator.checkpoint_manager is not None
    assert orchestrator.deployment_engine is not None
    assert orchestrator.cleanup_engine is not None
    assert orchestrator.sync_coordinator is not None
```

**Test 2: Git Checkpoint Workflow**
```python
def test_git_checkpoint_workflow():
    """Verify git checkpoint creation workflow."""
    orchestrator = DevOpsOrchestrator(state_machine, container)
    
    # Mock git operations
    orchestrator.git_operations.execute_git = Mock(return_value={"success": True})
    
    # Execute checkpoint phase
    result = await orchestrator.execute_phase("GIT_CHECKPOINT", {
        "session_id": "test-session",
        "checkpoint_type": "RED",
        "message": "RED phase complete"
    })
    
    assert result.success
    assert state_machine.current_state == "GIT_CHECKPOINT_VALIDATING_DOD"
    assert "commit_id" in result.metadata
```

**Why only 2 tests?**
- DevOps Orchestrator is infrastructure-critical but has simple workflows
- Smoke tests validate initialization and core git checkpoint workflow
- Comprehensive tests would be 50+ tests (excessive for Phase 1 validation)
- Real-world testing via TDD integration will provide additional validation

---

## 8️⃣ Migration Strategy

### Phase 1: Create New DevOps Orchestrator (Week 1)
- Implement `DevOpsOrchestrator` extending `BaseOrchestrator`
- Create 5 component files (git_operations, checkpoint_manager, deployment_engine, cleanup_engine, sync_coordinator)
- Write 2 smoke tests
- Integrate with State Machine, DI Container, Session Manager

### Phase 2: TDD Integration (Week 1)
- Update TDD Orchestrator to call DevOps checkpoint after each phase
- Test RED → checkpoint → GREEN → checkpoint → REFACTOR → checkpoint workflow
- Verify rollback capability

### Phase 3: Legacy Orchestrator Deprecation (Week 2)
- Mark old files as deprecated: `git_checkpoint_orchestrator.py`, `git_sync_and_optimize.py`
- Add deprecation warnings when old orchestrators called
- Update all references to use new DevOps Orchestrator

### Phase 4: Legacy Removal (Week 3)
- Delete old orchestrators:
  - `src/orchestrators/git_checkpoint_orchestrator.py` (302 LOC)
  - `src/orchestrators/git_sync_and_optimize.py` (800 LOC)
  - `src/operations/deploy.py` (120 LOC)
  - `src/operations/cleanup.py` (557 LOC)
- Remove old tests, documentation
- Update all integration points

---

## 9️⃣ Extensibility Analysis

**Extensibility Rating: ⭐⭐⭐⭐ (4/5) - Highly extensible**

### Why Highly Extensible?

**1. Git Operations Abstraction**
- `GitOperations` class can be extended with new git commands
- Easy to add: rebase, cherry-pick, tag, submodule operations

**2. Deployment Gates Registry**
- 19 gates can be extended to 50+ gates
- Custom gates for organization-specific validation

**3. Cleanup Categories**
- 4 categories can be extended to include: node_modules, vendor, Docker images
- Custom cleanup rules per project type

**4. Sync Workflow Phases**
- 7-phase workflow can be extended with custom phases
- Example: add "notify stakeholders" phase after deploy

### Extension Example: Custom Deployment Gate

```python
# Add new gate to deployment engine
class CustomSecurityGate(DeploymentGate):
    def validate(self) -> bool:
        """Check for XSS vulnerabilities."""
        # Custom security scan logic
        return scan_result.is_clean
        
# Register in DeploymentEngine
deployment_engine.register_gate("xss_scan", CustomSecurityGate())
```

---

## 🔟 Success Criteria

**Completion Checklist:**
- [ ] DevOps Orchestrator initialized successfully
- [ ] Git checkpoint workflow creates commits
- [ ] 7-phase sync workflow executes without errors
- [ ] 19 deployment gates validate correctly
- [ ] Cleanup engine frees disk space
- [ ] Smoke tests passing (2/2 - 100% success rate)
- [ ] TDD integration working (checkpoint after each phase)
- [ ] Session persistence survives crashes
- [ ] State machine validates all transitions
- [ ] Legacy orchestrators deprecated and removed

**Metrics:**
- Checkpoint creation time: < 5 seconds
- Sync workflow duration: < 10 minutes (typical case)
- Deployment success rate: > 95%
- Space freed by cleanup: 100-500 MB (typical)
- Zero skipped phases (state machine enforcement)

---

## 1️⃣1️⃣ Risk Assessment

### High Risk: Git Merge Conflicts
- **Mitigation:** Auto-detect conflicts, prompt user, rollback capability
- **Recovery:** Stash backup always available, can restore and retry

### Medium Risk: Deployment Gate Failures
- **Mitigation:** Dry run mode, incremental gate validation, detailed error messages
- **Recovery:** Fix issues, re-run deployment with --skip-gates (admin override)

### Low Risk: Cleanup Deletes Important Files
- **Mitigation:** Safety checks, protected directories, dry run mode
- **Recovery:** Git history preserves source code, only temp files at risk

---

## 1️⃣2️⃣ Related Documents

- [Orchestration Master Plan](../orchestration-master-plan.md)
- [Phase 1 Core Infrastructure Complete](../../reports/phase-1-core-infrastructure-complete.md)
- [TDD Orchestrator](src/orchestration_3_0/orchestrators/tdd/) - Phase 2 Complete
- [Planning Orchestrator](src/orchestration_3_0/orchestrators/planning/) - Phase 2 Complete

---

**Next Steps:** Proceed to QA Orchestrator sub-plan (Phase 1: 2 files, 1,580 → 800 LOC consolidation)
