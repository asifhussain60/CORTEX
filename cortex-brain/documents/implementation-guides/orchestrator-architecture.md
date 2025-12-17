# Orchestrator Architecture Implementation Guide

**Author:** Asif Hussain  
**Version:** 2.0 (Planning System 3.0)  
**Last Updated:** December 16, 2025

---

## Purpose

This guide explains the CORTEX orchestrator architecture, helping developers understand when to create user-facing orchestrators vs internal helper orchestrators, and how to properly implement each pattern.

---

## Table of Contents

1. [Orchestrator Types](#orchestrator-types)
2. [Architecture Patterns](#architecture-patterns)
3. [When to Use Each Pattern](#when-to-use-each-pattern)
4. [Implementation Guide](#implementation-guide)
5. [Integration Features](#integration-features)
6. [Testing Requirements](#testing-requirements)
7. [Best Practices](#best-practices)

---

## Orchestrator Types

### 1. User-Facing Orchestrators

**Purpose:** Direct user invocation via Copilot Chat or CLI wrappers

**Characteristics:**
- Inherit from `BaseOperationModule`
- Registered in `cortex-operations.yaml`
- Use `@with_orchestration_metrics` decorator
- Return `OperationResult`
- Provide visual progress tracking (`yield_progress`)
- Emit engagement hints (🎭 pattern)

**Examples:**
- `MaintenanceOrchestratorV3` - System maintenance workflow
- `PlanningOrchestrator` - Feature planning with TDD
- `ADOPlanningOrchestrator` - Azure DevOps work item generation
- `TDDOrchestrator` - Test-Driven Development workflow
- `CleanupOrchestrator` - File organization and cleanup

### 2. Internal Helper Orchestrators

**Purpose:** Called by other orchestrators for specialized tasks

**Characteristics:**
- Inherit from `BaseOperationModule` (as of v2.0)
- NOT registered in `cortex-operations.yaml`
- Use `@with_orchestration_metrics` decorator (as of v2.0)
- Return `OperationResult` (as of v2.0)
- Emit engagement hints (🎭 pattern)
- NOT directly invoked by users

**Examples:**
- `VacuumOrchestrator` - Deep cleanup (duplicates, dead code)
- `RefactorCycleOrchestrator` - Automatic code refactoring
- `DocumentHygieneOrchestrator` - Markdown maintenance

---

## Architecture Patterns

### Pattern A: User-Facing Orchestrator (Full Integration)

```python
"""
MyFeature Orchestrator v3.0 for CORTEX

Integrated with Planning System 3.0:
- Uses PlanningSession for state management
- Inherits visual progress tracking
- Phase-based git checkpoints
- Tiered routing for operation classification
- Success template integration

Author: Your Name
Version: 3.0.0
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule, OperationResult, OperationStatus,
    OperationPhase, OperationModuleMetadata
)
from src.operations.modules.orchestration.planning_orchestrator import (
    PlanningOrchestrator
)
from src.orchestrators.session_model import PlanningSession, SessionStatus
from src.operations.modules.routing.tiered_router import TieredRouter
from src.operations.modules.routing.complexity_analyzer import ComplexityAnalyzer
from src.operations.modules.version.version_manager import get_version_manager
from src.utils.progress_decorator import with_progress, yield_progress
from src.operations.utilities.orchestration_metrics_collector import (
    with_orchestration_metrics
)

class MyFeatureOrchestrator(BaseOperationModule):
    """
    User-facing orchestrator with full Planning System 3.0 integration.
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize orchestrator v3.0."""
        super().__init__()
        self.project_root = project_root or Path.cwd()
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("my_feature", "3.0")
        self.version = self.version_manager.get_orchestrator_version("my_feature")
        
        # Planning System 3.0 integration
        self.planning_orchestrator = PlanningOrchestrator(project_root=project_root)
        self.tiered_router = TieredRouter()
        self.complexity_analyzer = ComplexityAnalyzer()
        
        # State management
        self.current_session: Optional[PlanningSession] = None
        
        # Metrics
        self.metrics = {
            'operations_processed': 0,
            'phases_completed': 0,
            'errors': []
        }
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="my_feature",
            name="MyFeature Orchestrator 3.0",
            description="Description of what this orchestrator does",
            phase=OperationPhase.PROCESSING,
            priority=80,
            version="3.0.0",
            author="Your Name",
            tags=["orchestration", "feature-name", "planning-system-3.0"]
        )
    
    @with_progress(operation_name="MyFeature", threshold_seconds=3.0)
    @with_orchestration_metrics("MyFeatureOrchestrator")
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute orchestration workflow.
        
        Args:
            context: Operation context with parameters
        
        Returns:
            OperationResult with metrics and outcomes
        """
        start_time = datetime.now()
        operation = context.get('operation', 'default')
        
        logger.info(f"🎭 Orchestrator engaged: MyFeatureOrchestrator v{self.version}")
        
        try:
            # Phase execution with progress tracking
            yield_progress(1, 3, "Phase 1: Setup")
            logger.info("🎭 Phase transition: START → PHASE_1")
            # ... phase 1 logic ...
            
            yield_progress(2, 3, "Phase 2: Processing")
            logger.info("🎭 Phase transition: PHASE_1 → PHASE_2")
            # ... phase 2 logic ...
            
            yield_progress(3, 3, "Phase 3: Completion")
            logger.info("🎭 Phase transition: PHASE_2 → COMPLETE")
            # ... phase 3 logic ...
            
            success = True
            is_complete = success and len(self.metrics['errors']) == 0
            
            logger.info(
                f"🎭 Orchestrator completing: "
                f"{'✅ ALL WORK COMPLETE' if is_complete else '⏳ PHASES DONE'}"
            )
            
            return OperationResult(
                success=success,
                status=OperationStatus.SUCCESS,
                message=f"MyFeature completed: {self.metrics['phases_completed']} phases",
                data={
                    'metrics': self.metrics,
                    'is_complete': is_complete
                },
                errors=self.metrics['errors'],
                warnings=[],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
                formatted_header="🚀 MyFeature",
                formatted_footer="Operation complete"
            )
            
        except Exception as e:
            logger.error(f"MyFeature failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"MyFeature failed: {e}",
                data={'metrics': self.metrics},
                errors=[str(e)],
                warnings=[],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now()
            )
```

### Pattern B: Internal Helper Orchestrator (Standardized)

```python
"""
Helper Tool Orchestrator v2.0 - Specialized internal utility

Integrated with Planning System 3.0 for standardized operation handling:
- Inherits BaseOperationModule for consistent interface
- Uses orchestration metrics for engagement tracking
- Returns standardized OperationResult
- Provides visual progress tracking with 🎭 hints

Called by other orchestrators, not directly by users.

Author: Your Name
Version: 2.0.0
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule, OperationResult, OperationStatus,
    OperationPhase, OperationModuleMetadata
)
from src.operations.modules.version.version_manager import get_version_manager
from src.operations.utilities.orchestration_metrics_collector import (
    with_orchestration_metrics
)
from src.utils.progress_decorator import with_progress, yield_progress

class HelperToolOrchestrator(BaseOperationModule):
    """
    Internal helper orchestrator for specialized tasks.
    
    Called by: MaintenanceOrchestrator, PlanningOrchestrator
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize helper orchestrator v2.0."""
        super().__init__()
        self.project_root = project_root or Path.cwd()
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("helper_tool", "2.0")
        self.version = self.version_manager.get_orchestrator_version("helper_tool")
        
        self.metrics = {
            'items_processed': 0,
            'errors': []
        }
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="helper_tool_orchestrator",
            name="Helper Tool Orchestrator 2.0",
            description="Specialized utility for internal operations",
            phase=OperationPhase.PROCESSING,
            priority=60,
            version="2.0.0",
            author="Your Name",
            tags=["orchestration", "helper", "internal", "planning-system-3.0"]
        )
    
    @with_progress(operation_name="Helper Tool", threshold_seconds=3.0)
    @with_orchestration_metrics("HelperToolOrchestrator")
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute helper operation.
        
        Args:
            context: Operation context with parameters
        
        Returns:
            OperationResult with processing metrics
        """
        start_time = datetime.now()
        
        logger.info(f"🎭 Orchestrator engaged: HelperToolOrchestrator v{self.version}")
        
        try:
            # Simplified phase execution
            yield_progress(1, 2, "Phase 1: Processing")
            logger.info("🎭 Phase transition: START → PROCESSING")
            # ... processing logic ...
            
            yield_progress(2, 2, "Phase 2: Completion")
            logger.info("🎭 Phase transition: PROCESSING → COMPLETE")
            # ... completion logic ...
            
            success = len(self.metrics['errors']) == 0
            
            logger.info(f"🎭 Orchestrator completing: {'✅' if success else '⚠️'}")
            
            return OperationResult(
                success=success,
                status=OperationStatus.SUCCESS if success else OperationStatus.WARNING,
                message=f"Helper tool completed: {self.metrics['items_processed']} items",
                data={'metrics': self.metrics},
                errors=self.metrics['errors'],
                warnings=[],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Helper tool failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Helper tool failed: {e}",
                data={'metrics': self.metrics},
                errors=[str(e)],
                warnings=[],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now()
            )
```

---

## When to Use Each Pattern

### Use Pattern A (User-Facing) When:

✅ Users directly invoke the operation  
✅ Operation appears in `cortex-operations.yaml`  
✅ Multi-phase workflow with user feedback needed  
✅ Requires Planning System 3.0 state management  
✅ Needs tiered routing (Tier 1-4 classification)  
✅ Operation creates planning documents  
✅ Git checkpoints between phases required

**Examples:** Feature planning, system maintenance, ADO work items, TDD workflows

### Use Pattern B (Internal Helper) When:

✅ Only called by other orchestrators  
✅ NOT in `cortex-operations.yaml`  
✅ Specialized utility task (cleanup, vacuum, refactor)  
✅ No direct user interaction needed  
✅ Simpler workflow (2-4 phases)  
✅ No planning documents generated  
✅ Used as building block in larger workflows

**Examples:** Duplicate detection, code refactoring, document consolidation

---

## Implementation Guide

### Step 1: Choose Your Pattern

Decision tree:
```
Will users invoke this directly?
├─ YES → Pattern A (User-Facing)
└─ NO → Pattern B (Internal Helper)
```

### Step 2: Set Up Base Structure

**For Both Patterns:**

1. Inherit from `BaseOperationModule`
2. Implement `get_metadata()` returning `OperationModuleMetadata`
3. Implement `execute(context: Dict[str, Any]) -> OperationResult`
4. Add `@with_orchestration_metrics("OrchestratorName")` decorator
5. Add `@with_progress(operation_name="Name", threshold_seconds=3.0)` decorator
6. Register version with `version_manager`

### Step 3: Add Pattern-Specific Features

**Pattern A (User-Facing) Additional:**

1. Initialize `PlanningOrchestrator` instance
2. Add `TieredRouter` and `ComplexityAnalyzer`
3. Create `PlanningSession` for state management
4. Implement tier-based routing logic
5. Register in `cortex-operations.yaml`:
   ```yaml
   my_feature:
     name: MyFeature
     description: Description
     deployment_tier: user
     execution_method: copilot_chat
     natural_language:
       - trigger phrases
     category: feature-category
     modules:
       - my_feature_orchestrator
   ```

**Pattern B (Internal Helper):**

1. Keep implementation lightweight
2. Focus on single specialized task
3. Provide clear API for parent orchestrators
4. NO `cortex-operations.yaml` registration

### Step 4: Implement Phase Workflow

**Standard Phase Pattern:**

```python
try:
    # Phase 1
    yield_progress(1, total_phases, "Phase 1: Description")
    logger.info("🎭 Phase transition: START → PHASE_1")
    result_1 = self._execute_phase_1(context)
    
    # Phase 2
    yield_progress(2, total_phases, "Phase 2: Description")
    logger.info("🎭 Phase transition: PHASE_1 → PHASE_2")
    result_2 = self._execute_phase_2(context)
    
    # Final phase
    yield_progress(total_phases, total_phases, f"Phase {total_phases}: Completion")
    logger.info("🎭 Phase transition: PHASE_N → COMPLETE")
    self._finalize(results)
    
    # Completion signaling
    success = len(self.metrics['errors']) == 0
    is_complete = success and all_phases_done
    
    logger.info(
        f"🎭 Orchestrator completing: "
        f"{'✅ ALL WORK COMPLETE' if is_complete else '⏳ PHASES DONE'}"
    )
    
    return OperationResult(...)
    
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    return OperationResult(success=False, ...)
```

### Step 5: Add Orchestration Metrics

Metrics are automatically collected via `@with_orchestration_metrics` decorator:

- **Engagement start:** Logged when `execute()` begins
- **Engagement complete:** Logged when `execute()` returns
- **Duration:** Auto-calculated
- **Outcome:** success/failure from `OperationResult.success`

**Storage:** `logs/orchestration-metrics/{YYYY-MM-DD}/events.jsonl`

**Retention:** 30 days auto-archival

### Step 6: Implement Progress Tracking

Use `yield_progress()` for visual feedback:

```python
@with_progress(operation_name="MyOperation", threshold_seconds=3.0)
def execute(self, context: Dict[str, Any]) -> OperationResult:
    # Progress updates
    yield_progress(1, 5, "Phase 1: Setup")
    yield_progress(2, 5, "Phase 2: Processing")
    yield_progress(3, 5, "Phase 3: Validation")
    yield_progress(4, 5, "Phase 4: Cleanup")
    yield_progress(5, 5, "Phase 5: Complete")
```

### Step 7: Add Engagement Hints (🎭 Pattern)

Emit hints for orchestrator activity:

```python
logger.info(f"🎭 Orchestrator engaged: MyOrchestrator v{self.version}")
logger.info("🎭 Phase transition: SETUP → PROCESSING")
logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
```

### Step 8: Return OperationResult

Always return standardized `OperationResult`:

```python
return OperationResult(
    success=True,
    status=OperationStatus.SUCCESS,
    message="Operation completed successfully",
    data={
        'metrics': self.metrics,
        'is_complete': True,
        'custom_data': custom_results
    },
    errors=[],
    warnings=[],
    duration_seconds=elapsed_time,
    timestamp=datetime.now(),
    formatted_header="🚀 Operation Name",
    formatted_footer="Summary text"
)
```

---

## Integration Features

### Planning System 3.0 Integration (User-Facing Only)

**PlanningSession State Management:**

```python
# Initialize session
self.session = PlanningSession(
    session_id=f"mysession_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    operation_type="my_feature",
    status=SessionStatus.IN_PROGRESS,
    complexity_tier=complexity_score.tier,
    phases_total=len(phases),
    phases_completed=0
)

# Update session progress
self.session.phases_completed += 1
self.session.update_progress(phase_idx, len(phases))

# Complete session
self.session.status = SessionStatus.COMPLETE
```

**Tiered Routing:**

```python
# Classify operation tier
complexity_score = self.complexity_analyzer.analyze(operation)
routing_decision = self.tiered_router.route(operation)

# Route to execution path
if routing_decision.tier == 1:
    # Instant execution
elif routing_decision.tier == 2:
    # Lightweight planning
elif routing_decision.tier == 3:
    # Documented feature planning
elif routing_decision.tier == 4:
    # Complex architecture planning
```

**Git Checkpoints:**

```python
if self.checkpoint_orchestrator:
    checkpoint_id = self.checkpoint_orchestrator.create_checkpoint(
        message=f"Checkpoint: {phase_name}",
        metadata={'phase': phase_name, 'session_id': session_id}
    )
```

### Orchestration Metrics (All Orchestrators)

Automatic tracking via decorator:

- Entry timestamp
- Exit timestamp
- Duration
- Success/failure status
- Orchestrator name
- Event ID (UUID)

**Query metrics:**

```python
from src.operations.utilities.orchestration_metrics_collector import (
    OrchestrationMetricsCollector
)

collector = OrchestrationMetricsCollector()
report = collector.generate_report(days=7)
```

### Visual Progress (All Orchestrators)

```python
@with_progress(operation_name="MyOp", threshold_seconds=3.0)
def execute(self, context):
    # Shows progress bar if operation > 3 seconds
    yield_progress(current, total, "Status message")
```

---

## Testing Requirements

### Unit Tests

**Test Structure:**

```python
import pytest
from src.operations.modules.orchestration.my_orchestrator import MyOrchestrator

def test_orchestrator_initialization():
    """Test orchestrator initializes correctly."""
    orchestrator = MyOrchestrator()
    assert orchestrator.version == "3.0"
    assert orchestrator.metrics is not None

def test_execute_success():
    """Test successful execution."""
    orchestrator = MyOrchestrator()
    context = {'operation': 'test'}
    result = orchestrator.execute(context)
    
    assert result.success is True
    assert result.status == OperationStatus.SUCCESS
    assert 'metrics' in result.data

def test_execute_failure():
    """Test failure handling."""
    orchestrator = MyOrchestrator()
    context = {'operation': 'invalid'}
    result = orchestrator.execute(context)
    
    assert result.success is False
    assert result.status == OperationStatus.FAILED
    assert len(result.errors) > 0

def test_metadata():
    """Test metadata structure."""
    orchestrator = MyOrchestrator()
    metadata = orchestrator.get_metadata()
    
    assert metadata.module_id == "my_orchestrator"
    assert metadata.version == "3.0.0"
    assert "planning-system-3.0" in metadata.tags
```

### Integration Tests

```python
def test_orchestrator_with_planning_system():
    """Test integration with Planning System 3.0."""
    orchestrator = MyOrchestrator()
    # Test PlanningSession creation
    # Test tiered routing
    # Test git checkpoints

def test_orchestrator_metrics_collection():
    """Test metrics are collected properly."""
    orchestrator = MyOrchestrator()
    context = {'operation': 'test'}
    result = orchestrator.execute(context)
    
    # Verify metrics file created
    # Verify event structure
```

---

## Best Practices

### DO ✅

1. **Always inherit from BaseOperationModule**
2. **Use `@with_orchestration_metrics` decorator**
3. **Return `OperationResult` from `execute()`**
4. **Emit 🎭 engagement hints for visibility**
5. **Use `yield_progress()` for long operations**
6. **Register version with version_manager**
7. **Implement `get_metadata()` with complete info**
8. **Log errors with `exc_info=True`**
9. **Set `is_complete` flag in result data**
10. **Document which orchestrators call internal helpers**

### DON'T ❌

1. **Don't skip BaseOperationModule inheritance**
2. **Don't return Dict instead of OperationResult**
3. **Don't hardcode version strings (use version_manager)**
4. **Don't forget error handling in execute()**
5. **Don't mix user-facing and internal patterns**
6. **Don't register internal helpers in cortex-operations.yaml**
7. **Don't skip progress tracking for >3 second operations**
8. **Don't omit 🎭 phase transition hints**
9. **Don't forget to increment version on breaking changes**
10. **Don't bypass orchestration metrics decorator**

### Code Quality

**Naming Conventions:**
- Orchestrator classes: `*Orchestrator` (e.g., `MaintenanceOrchestrator`)
- File names: `*_orchestrator.py` (e.g., `maintenance_orchestrator.py`)
- Module IDs: `*_orchestrator` (e.g., `maintenance_orchestrator_v3`)

**Version Numbering:**
- v1.0: Initial implementation
- v2.0: BaseOperationModule standardization
- v3.0: Full Planning System 3.0 integration

**Error Handling:**
```python
try:
    # Operation logic
except SpecificException as e:
    logger.error(f"Specific error: {e}", exc_info=True)
    return OperationResult(success=False, ...)
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return OperationResult(success=False, ...)
```

---

## Migration Guide

### Upgrading v1.0 → v2.0 (Internal Helpers)

**Changes:**
1. Add `BaseOperationModule` inheritance
2. Add `get_metadata()` method
3. Change `execute()` to return `OperationResult`
4. Add `@with_orchestration_metrics` decorator
5. Add `@with_progress` decorator
6. Convert async to sync (use `asyncio.run()` internally)
7. Update version to 2.0

### Upgrading v2.0 → v3.0 (User-Facing)

**Changes:**
1. Add `PlanningOrchestrator` integration
2. Add `PlanningSession` state management
3. Add `TieredRouter` and `ComplexityAnalyzer`
4. Implement tiered routing logic
5. Add git checkpoint support
6. Update version to 3.0

---

## Examples

### Example 1: Simple Internal Helper

See: `src/operations/modules/orchestration/vacuum_orchestrator.py`

### Example 2: Complex User-Facing Orchestrator

See: `src/operations/modules/orchestration/maintenance_orchestrator_v3.py`

### Example 3: Planning-Integrated Orchestrator

See: `src/operations/modules/orchestration/planning_orchestrator.py`

---

## Related Documentation

- **BaseOperationModule:** `src/operations/base_operation_module.py`
- **Orchestration Metrics:** `src/operations/utilities/orchestration_metrics_collector.py`
- **Progress Decorator:** `src/utils/progress_decorator.py`
- **Planning System 3.0:** `cortex-brain/manifests/orchestrators/planning-system-2.0-manifest.yaml`
- **Version Management:** `src/operations/modules/version/version_manager.py`

---

## Support

**Questions?** Review the orchestrator review report:  
`cortex-brain/documents/reports/orchestrator-review-2025-12-16.md`

**Need Help?** Check existing orchestrators for reference implementations.

**Found a Bug?** Create an issue with `[ORCHESTRATOR]` prefix.

---

**Last Updated:** December 16, 2025  
**Maintained By:** CORTEX Development Team
