# CORTEX 3.0 → 4.0 Migration Guide

**Version:** 4.0.0 GA  
**Release Date:** December 25, 2025  
**Author:** Asif Hussain  
**Status:** ✅ Production Ready

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Breaking Changes](#breaking-changes)
3. [Migration Prerequisites](#migration-prerequisites)
4. [Step-by-Step Migration](#step-by-step-migration)
5. [Feature Migrations](#feature-migrations)
6. [Port-Ready Indicators](#port-ready-indicators)
7. [Testing & Validation](#testing--validation)
8. [Rollback Procedures](#rollback-procedures)
9. [Common Issues & Solutions](#common-issues--solutions)

---

## 📊 Executive Summary

### What's New in 4.0

**Major Improvements:**
- 🏗️ **Orchestrator Consolidation:** 28 → 13 orchestrators (46% reduction)
- 🧠 **4-Tier Brain Architecture:** Sub-100ms memory access, pattern learning
- 📝 **Manifest Consolidation:** 6,760 → 500 lines (93% reduction)
- 🎯 **Planning System:** Auto-complexity detection, DoR/DoD compliance
- 🔄 **TDD Mastery v4.0:** RED→GREEN→REFACTOR enforcement
- 🚀 **40% Productivity Gain:** From consolidated workflows
- ✅ **98.3% Test Reliability:** From TDD-first approach

### Migration Complexity: MEDIUM

**Estimated Timeline:**
- **Small Projects (<5K LOC):** 2-4 hours
- **Medium Projects (5K-20K LOC):** 4-8 hours  
- **Large Projects (>20K LOC):** 1-2 days

**Required Skills:**
- Python 3.8+ experience
- Understanding of orchestration patterns
- Git workflow knowledge
- YAML configuration experience

---

## ⚠️ Breaking Changes

### 1. Orchestrator Architecture

**REMOVED:**
```python
# CORTEX 3.0 - Direct orchestrator imports
from src.orchestrators.planning_v3 import PlanningOrchestratorV3
from src.orchestrators.execution_v3 import ExecutionOrchestratorV3
from src.orchestrators.maintenance_v2 import MaintenanceOrchestrator
```

**NEW:**
```python
# CORTEX 4.0 - Unified base + specialized orchestrators
from src.orchestrators.base import BaseOrchestrator
from src.orchestrators.planning import PlanningOrchestrator
from src.orchestration_4_0.orchestrators.execution import ExecutionOrchestrator
from src.operations.modules.orchestration import MaintenanceOrchestrator
```

**Impact:** All orchestrators now inherit from `BaseOrchestrator` with standardized lifecycle.

---

### 2. Brain Tier Structure

**REMOVED:**
```python
# CORTEX 3.0 - Flat brain structure
from src.brain import memory, knowledge_base, context_manager

memory.store("key", value)
knowledge_base.query("topic")
```

**NEW:**
```python
# CORTEX 4.0 - 4-tier hierarchy
from src.tier0 import BrainProtector  # Governance (SKULL)
from src.tier1 import WorkingMemory   # 70-conv FIFO, <100ms
from src.tier2 import KnowledgeGraph  # Pattern learning
from src.tier3 import DevContext      # Metrics, hotspots

working_memory = WorkingMemory()
working_memory.store_conversation(conversation_id, data)
```

**Impact:** 
- Memory access now tiered (working → knowledge → context)
- SKULL rules enforced at Tier 0 (TDD, holistic discovery, git isolation)
- Workspace-specific context in Tier 3 (`.cortex/tier3/context.db`)

---

### 3. Manifest Format

**REMOVED:**
```yaml
# CORTEX 3.0 - Multiple YAML files
# cortex-planning.yaml
# cortex-execution.yaml  
# cortex-maintenance.yaml
# (6,760 total lines)
```

**NEW:**
```yaml
# CORTEX 4.0 - Single cortex-operations.yaml (500 lines)
operations:
  planning:
    id: "PLANNING_SYSTEM_2_0"
    name: "Planning System"
    execution_method: "copilot_chat"
    complexity: "high"
    features:
      - auto_complexity_detection
      - dor_dod_compliance
      - tdd_integration
```

**Impact:** 
- Single source of truth for operations
- 93% reduction in configuration size
- Clear execution method classification

---

### 4. Execution Modes

**REMOVED:**
```python
# CORTEX 3.0 - Manual mode only
orchestrator.execute(plan_data)
```

**NEW:**
```python
# CORTEX 4.0 - Adaptive execution modes
from src.operations.modules.orchestration.adaptive_execution import ExecutionMode

orchestrator = ExecutionOrchestrator(config={
    "execution_mode": ExecutionMode.AUTONOMOUS  # or SUPERVISED, MANUAL
})

result = orchestrator.execute(context={"plan": plan_data})
```

**Modes:**
- `AUTONOMOUS`: Full automation with self-healing (3 retries)
- `SUPERVISED`: Human approval at phase gates
- `MANUAL`: Step-by-step execution

---

### 5. Planning System

**REMOVED:**
```python
# CORTEX 3.0 - Manual complexity selection
planning_orchestrator.create_plan(
    feature_name="user-auth",
    complexity="high"  # User must specify
)
```

**NEW:**
```python
# CORTEX 4.0 - Auto-complexity detection
planning_orchestrator.execute(
    feature_name="user-auth"
    # Complexity auto-detected from DoR criteria
    # HIGH: Incremental phasing
    # MEDIUM: Conditional validation
    # LOW: Skeleton only
)
```

**Features:**
- ✅ Auto-complexity detection via DoR criteria
- ✅ TDD automatically included in all plans
- ✅ Phase 10 YAML modularization (>20KB → index + modules)
- ✅ Git checkpoint-based rollback

---

### 6. TDD Workflow

**REMOVED:**
```python
# CORTEX 3.0 - Optional TDD
tdd_orchestrator.run_tests()  # Manual invocation
```

**NEW:**
```python
# CORTEX 4.0 - Mandatory TDD enforcement
# RED phase: Tests MUST fail first
# GREEN phase: Implementation passes tests
# REFACTOR phase: Cleanup without breaking tests

# SKULL rule: TDD_ENFORCEMENT
# ALL code changes require passing test evidence
```

**Impact:** 
- Tests must exist before implementation (RED phase)
- 98.3% test reliability from TDD-first approach
- Per-layer coverage validation

---

## 📋 Migration Prerequisites

### 1. Environment Setup

```bash
# Python 3.8+ required
python --version  # Must be 3.8 or higher

# Install CORTEX 4.0 dependencies
pip install -r requirements.txt

# Verify installation
python -c "from src.orchestrators.base import BaseOrchestrator; print('✅ CORTEX 4.0 ready')"
```

### 2. Backup Current State

```bash
# Create migration branch
git checkout -b cortex-4.0-migration

# Backup CORTEX 3.0 state
git tag cortex-3.0-baseline

# Archive existing configuration
mkdir -p cortex-3.0-backup
cp -r cortex-brain/ cortex-3.0-backup/
cp -r src/ cortex-3.0-backup/
```

### 3. Identify Port-Ready Components

Run the discovery script to identify components ready for migration:

```bash
# Discover 3.0 implementations
python scripts/port_ready_discovery.py

# Output: List of components with:
# - ✅ Tests passing
# - ✅ Clear boundaries  
# - ✅ 4.0-compatible architecture
```

---

## 🚀 Step-by-Step Migration

### Phase 1: Core Infrastructure (2 hours)

#### 1.1 Update Brain Tier References

**Before:**
```python
from src.brain import memory
memory.store("key", value)
```

**After:**
```python
from src.tier1 import WorkingMemory
working_memory = WorkingMemory()
working_memory.store_conversation(conv_id, data)
```

#### 1.2 Migrate Orchestrator Inheritance

**Before:**
```python
class MyOrchestrator:
    def __init__(self):
        self.name = "my-orchestrator"
    
    def execute(self, params):
        # Custom logic
        pass
```

**After:**
```python
from src.orchestrators.base import BaseOrchestrator, OrchestratorResult, OrchestratorStatus

class MyOrchestrator(BaseOrchestrator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Custom initialization
    
    def execute(self) -> OrchestratorResult:
        # Uses self.workspace_info, self.target_directory
        # Custom logic
        
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Operation complete",
            data={"key": "value"}
        )
```

**Benefits:**
- ✅ Standardized lifecycle (setup → execute → teardown)
- ✅ Workspace-aware file operations
- ✅ Built-in error handling
- ✅ Consistent result format

---

### Phase 2: Planning System Migration (1 hour)

#### 2.1 Update Planning Invocation

**Before:**
```python
from src.orchestrators.planning_v3 import PlanningOrchestratorV3

orchestrator = PlanningOrchestratorV3()
result = orchestrator.create_plan(
    feature_name="user-authentication",
    complexity="high"
)
```

**After:**
```python
from src.orchestrators.planning import PlanningOrchestrator

orchestrator = PlanningOrchestrator(config={
    "name": "planning",
    "workspace_root": Path("/path/to/workspace"),
    "autonomous_execution": True  # Enable auto-execution
})

result = orchestrator.execute(
    feature_name="user-authentication"
    # Complexity auto-detected
    # TDD phases auto-included
)
```

#### 2.2 Enable Autonomous Execution

```python
# If autonomous_execution=True and plan_executor enabled:
# - Plan generates phases
# - ExecutionOrchestrator auto-invoked
# - TDD workflow enforced
# - Git checkpoints created

result.data["execution_summary"]
# {
#   "status": "completed",
#   "phases_executed": 8,
#   "execution_time_seconds": 145.2,
#   "checkpoint_created": "checkpoint_abc123",
#   "rollback_available": True
# }
```

---

### Phase 3: TDD Workflow Integration (1 hour)

#### 3.1 Create Test-First

**CORTEX 4.0 enforces RED→GREEN→REFACTOR:**

```python
# Step 1: RED - Write failing test
def test_user_authentication():
    auth = UserAuthenticator()
    assert auth.login("user", "pass") == True  # MUST fail

# Step 2: Run tests (expect failure)
pytest tests/test_auth.py -v
# FAIL: test_user_authentication

# Step 3: GREEN - Implement to pass
class UserAuthenticator:
    def login(self, username, password):
        return username and password  # Simplest implementation

# Step 4: Run tests (expect pass)
pytest tests/test_auth.py -v  
# PASS: test_user_authentication

# Step 5: REFACTOR - Cleanup code
class UserAuthenticator:
    def login(self, username: str, password: str) -> bool:
        """Authenticate user with credentials."""
        if not username or not password:
            return False
        # Add actual auth logic
        return self._verify_credentials(username, password)
```

**SKULL Enforcement:**
```python
# If implementing without RED phase:
# ❌ ERROR: TDD_ENFORCEMENT violation
# Must provide failing test evidence before implementation
```

---

### Phase 4: Execution Mode Configuration (30 min)

Configure execution mode based on use case:

```python
# Development: SUPERVISED mode (human approval at gates)
config = {
    "execution_mode": ExecutionMode.SUPERVISED,
    "enable_rollback": True,
    "max_retries": 3
}

# Production: AUTONOMOUS mode (full automation)
config = {
    "execution_mode": ExecutionMode.AUTONOMOUS,
    "enable_rollback": True,
    "max_retries": 3,
    "auto_checkpoint": True
}

# Manual control: MANUAL mode (step-by-step)
config = {
    "execution_mode": ExecutionMode.MANUAL,
    "enable_rollback": False
}

orchestrator = ExecutionOrchestrator(config=config)
```

---

## 🔧 Feature Migrations

### ADO Operations

**NEW in 4.0:** Azure DevOps integration with orchestrator-level formatting.

```python
# Generate ADO-formatted work items
from src.operations.ado_operations import generate_ado_plan

result = generate_ado_plan(
    feature_name="payment-gateway",
    plan_type="feature"  # or "story"
)

# Output: Manifest with ADO-compatible formatting
# - Inherits Planning System (DoR/DoD/TDD)
# - Adds ADO-specific output format
# - Work item hierarchy (Epic → Feature → Story → Task)
```

**Manifest:** `ado-planning-manifest.yaml`
- Inherits: `planning-system-manifest.yaml`
- Adds: ADO formatting rules

---

### Code Sanitization

**NEW in 4.0:** 5-phase workflow for open-source sharing.

```bash
# Invoke via Copilot Chat
User: "sanitize src/internal/"

# 5-Phase Workflow:
# 1. Analyze: Scan for company-specific data
# 2. Mapping: Create transformation rules
# 3. Transform: Apply generic replacements
# 4. Validate: Ensure functionality preserved
# 5. Report: Generate sanitization summary
```

**Guide:** `cortex-brain/CODE-SANITIZATION-QUICK-REF.md`

---

### System Maintenance v3.0

**Enhanced in 4.0:** 7-phase holistic maintenance with completion detection.

```bash
# Invoke via Copilot Chat
User: "system maintenance"

# 7 Phases:
# 1. Healthcheck: Baseline metrics
# 2. Align: Auto-fix misalignments
# 3. Cleanup: Remove obsolete artifacts
# 4. Optimize: Performance improvements
# 5. Vacuum: Database optimization
# 6. Refresh Prompts: Regenerate docs
# 7. Final Healthcheck: Verify improvements

# Completion Signal:
# "# 🎉 CONGRATULATIONS" when all phases complete with no errors
```

**Engagement Hints:**
- `🎭 Orchestrator engaged: MaintenanceOrchestrator`
- `🎭 Phase transition: HEALTHCHECK → ALIGN`
- `🎭 Orchestrator completing: ✅ ALL WORK COMPLETE`

---

## ✅ Port-Ready Indicators

### When to Port from 3.0 to 4.0

**Port when ALL conditions met:**

1. **✅ Tests Passing**
   ```bash
   pytest tests/path/to/module -v
   # All tests green, no failures
   ```

2. **✅ Clear Boundaries**
   - Single responsibility
   - No cross-orchestrator dependencies
   - Well-defined input/output

3. **✅ 4.0-Compatible Architecture**
   - Can inherit from `BaseOrchestrator`
   - Uses workspace-aware paths
   - Returns `OrchestratorResult`

4. **✅ Documentation Exists**
   - README with usage examples
   - API documentation
   - Integration tests

**DO NOT port if:**
- ❌ Tests failing or missing
- ❌ Tight coupling with 3.0 internals
- ❌ Deprecated dependencies
- ❌ Architectural conflicts

---

## 🧪 Testing & Validation

### Validation Checklist

After migration, verify each component:

```bash
# 1. Run unit tests
pytest tests/orchestrators/your_orchestrator -v
# Expected: 100% pass rate

# 2. Run integration tests  
pytest tests/integration/test_your_orchestrator_integration.py -v
# Expected: All phases execute successfully

# 3. Validate workspace detection
python -c "
from src.orchestrators.your_orchestrator import YourOrchestrator
orch = YourOrchestrator(config={'name': 'test'})
print(f'Workspace: {orch.workspace_name}')
print(f'Target: {orch.target_directory}')
"
# Expected: Correct workspace detected

# 4. Verify SKULL compliance
# - TDD: Tests exist before implementation
# - Holistic Discovery: No duplicate code created
# - Refactor Cleanup: Orphaned code removed
# - Git Isolation: CORTEX code not in user repos

# 5. Run full system maintenance
# Invoke via Copilot: "system maintenance"
# Expected: All phases complete, no errors
```

---

## 🔄 Rollback Procedures

### Automatic Rollback (Execution Orchestrator)

```python
# Enabled with auto_checkpoint=True
orchestrator = ExecutionOrchestrator(config={
    "execution_mode": ExecutionMode.AUTONOMOUS,
    "enable_rollback": True,
    "auto_checkpoint": True
})

result = orchestrator.execute(context={"plan": plan_data})

if not result.success:
    # Automatic rollback to last checkpoint
    print(f"Rolled back to: {result.data['rollback_checkpoint']}")
```

### Manual Rollback (Git-based)

```bash
# List available checkpoints
git tag -l "checkpoint_*"

# Rollback to specific checkpoint
git checkout checkpoint_abc123

# Or rollback to 3.0 baseline
git checkout cortex-3.0-baseline

# Create fix branch
git checkout -b fix-migration-issue
```

### Planning Orchestrator Checkpoints

```python
# Planning orchestrator creates git checkpoints per phase
# If execution fails, rollback available

from src.orchestrators.planning import PlanningOrchestrator

orchestrator = PlanningOrchestrator(config={
    "git_checkpoints_enabled": True
})

result = orchestrator.execute(feature_name="payment")

if not result.success:
    # Check result.data["checkpoint_created"]
    # Use: git checkout <checkpoint_id>
    pass
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Import Errors After Migration

**Problem:**
```python
ImportError: No module named 'src.orchestrators.planning_v3'
```

**Solution:**
```python
# Update imports to 4.0 structure
from src.orchestrators.planning import PlanningOrchestrator  # ✅
```

---

### Issue 2: Workspace Detection Fails

**Problem:**
```
WARNING: Workspace detection failed: No active workspace found
```

**Solution:**
```python
# Explicitly set workspace_root in config
config = {
    "name": "my-orchestrator",
    "workspace_root": Path("/explicit/path/to/workspace")
}
orchestrator = MyOrchestrator(config=config)
```

---

### Issue 3: TDD Enforcement Violations

**Problem:**
```
ERROR: TDD_ENFORCEMENT violation - No failing test evidence
```

**Solution:**
```python
# Step 1: Write failing test FIRST (RED phase)
def test_feature():
    result = my_function()
    assert result == expected  # This MUST fail initially

# Step 2: Run pytest to confirm failure
pytest tests/test_feature.py -v
# FAIL: test_feature ✅ (Expected at RED phase)

# Step 3: Implement to pass (GREEN phase)
def my_function():
    return expected

# Step 4: Run pytest to confirm pass
pytest tests/test_feature.py -v  
# PASS: test_feature ✅
```

---

### Issue 4: Manifest Not Found

**Problem:**
```
FileNotFoundError: cortex-operations.yaml not found
```

**Solution:**
```bash
# Ensure cortex-operations.yaml exists at project root
ls -la cortex-operations.yaml

# If missing, copy from template
cp cortex.config.template.json cortex.config.json
# Edit paths in cortex.config.json
```

---

### Issue 5: Execution Mode Errors

**Problem:**
```
ValueError: Invalid execution mode: 'auto'
```

**Solution:**
```python
# Use correct ExecutionMode enum values
from src.operations.modules.orchestration.adaptive_execution import ExecutionMode

config = {
    "execution_mode": ExecutionMode.AUTONOMOUS  # ✅ Not "auto"
    # Options: AUTONOMOUS, SUPERVISED, MANUAL
}
```

---

## 📚 Additional Resources

### Documentation
- **Quick Start:** `.github/copilot-instructions.md`
- **Complete Guide:** `.github/prompts/CORTEX.prompt.md`
- **Orchestrator Framework:** `src/orchestrators/README.md`
- **Brain Architecture:** `cortex-brain/README-ORGANIZATION.md`

### Migration Reports
- **Phase 11 Completion:** `cortex-brain/documents/reports/phase-11-completion-report.md`
- **Task 8.4 Orchestrator Testing:** `cortex-brain/documents/reports/task-8.4-completion-report.md`
- **CORTEX 4.0 Status:** `cortex-brain/documents/archive/CORTEX4-STATUS.md`

### Developer Guides
- **Base Orchestrator Guide:** `cortex-brain/documents/guides/BASE-ORCHESTRATOR-DEVELOPER-GUIDE.md`
- **Execution Orchestrator Guide:** `cortex-brain/documents/guides/EXECUTION-ORCHESTRATOR-GUIDE.md`
- **Code Sanitization:** `cortex-brain/CODE-SANITIZATION-QUICK-REF.md`

### Support
- **GitHub:** https://github.com/asifhussain60/CORTEX
- **Issues:** Report migration issues with `[migration]` tag
- **Author:** Asif Hussain (asifhussain60@github)

---

## ✅ Migration Checklist

Use this checklist to track migration progress:

- [ ] **Prerequisites Complete**
  - [ ] Python 3.8+ installed
  - [ ] Dependencies installed (`pip install -r requirements.txt`)
  - [ ] Backup created (`git tag cortex-3.0-baseline`)
  - [ ] Migration branch created (`git checkout -b cortex-4.0-migration`)

- [ ] **Core Infrastructure**
  - [ ] Brain tier references updated (Tier 0-3)
  - [ ] Orchestrators inherit from `BaseOrchestrator`
  - [ ] Workspace detection verified
  - [ ] Manifest consolidated to `cortex-operations.yaml`

- [ ] **Feature Migrations**
  - [ ] Planning System integrated
  - [ ] TDD workflow enforced (RED→GREEN→REFACTOR)
  - [ ] Execution modes configured
  - [ ] ADO operations enabled (if applicable)
  - [ ] Code sanitization available (if applicable)

- [ ] **Testing & Validation**
  - [ ] All unit tests passing (100%)
  - [ ] Integration tests passing
  - [ ] Workspace detection correct
  - [ ] SKULL rules enforced
  - [ ] System maintenance runs successfully

- [ ] **Documentation**
  - [ ] Updated import statements
  - [ ] README reflects 4.0 changes
  - [ ] Examples use 4.0 patterns
  - [ ] Migration notes documented

- [ ] **Production Readiness**
  - [ ] Code review complete
  - [ ] Performance validated
  - [ ] Rollback procedures tested
  - [ ] Monitoring configured
  - [ ] Team trained on 4.0 workflows

---

**Migration Status:** ✅ Ready for GA Release  
**Last Updated:** December 25, 2025  
**Version:** 1.0.0
