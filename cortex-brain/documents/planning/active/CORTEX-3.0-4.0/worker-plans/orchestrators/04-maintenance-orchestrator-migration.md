# Maintenance Orchestrator Migration Plan
## CORTEX 3.0 → 4.0 Consolidation

**Target:** Consolidate 7 maintenance operations into unified `MaintenanceOrchestrator`

**Version:** 1.0.0 | **Author:** Asif Hussain | **Date:** December 17, 2025

---

## 📋 Executive Summary

### Current State (CORTEX 3.0)
Seven separate maintenance operations with no unified orchestration:

1. **Healthcheck** (`src/operations/healthcheck.py`)
   - 60 lines of code
   - System health validation
   - Brain database checks

2. **Align** (`src/operations/align.py`)
   - 230 lines of code
   - Feature registration validation
   - Auto-discovery and wiring check
   - Intent router coverage
   - Response template validation
   - Obsolete code detection

3. **Cleanup** (`src/operations/cleanup.py`)
   - 559 lines of code
   - Workspace cleanup (temp files, cache, logs)
   - Safe deletion with protection rules
   - Space recovery tracking

4. **Optimize** (`src/operations/optimize.py`)
   - 202 lines of code
   - Token optimization
   - File system optimization
   - Database consolidation

5. **Vacuum** (`src/operations/modules/vacuum_sqlite_databases_module.py`)
   - 182 lines of code
   - SQLite database optimization
   - Space recovery calculation

6. **Refresh Design Docs** (`src/operations/modules/refresh_design_docs_module.py`)
   - 249 lines of code
   - Documentation updates
   - Index regeneration
   - Timestamp updates

7. **Refresh Prompts** (embedded in align)
   - Prompt file optimization
   - CORTEX.prompt.md validation

**Total:** 1,482 LOC scattered across 7+ files

### Target State (CORTEX 4.0)
Single unified `MaintenanceOrchestrator` with:

- **7-phase workflow**: Healthcheck → Align → Cleanup → Optimize → Vacuum → Refresh → Healthcheck
- **Autonomous execution**: Runs all phases without user confirmation (user approves workflow, not each phase)
- **Progress tracking**: Real-time progress bars and phase status
- **Error recovery**: Continues on non-critical errors, rolls back on critical failures
- **MCP integration**: All operations exposed as MCP tools
- **Event-driven**: Emits maintenance events for monitoring

**Target:** 800 LOC in `cortex_orchestrators/maintenance/`

---

## 🎯 Consolidation Strategy

### Architecture Changes

**Before (CORTEX 3.0):**
```
User: "system maintenance"
    ↓
[Manual execution of each operation]
    ├── python -m src.operations.healthcheck
    ├── python -m src.operations.align
    ├── python -m src.operations.cleanup
    ├── python -m src.operations.optimize
    ├── python -m src.operations.vacuum
    └── python -m src.operations.refresh
```

**After (CORTEX 4.0):**
```
User: "system maintenance"
    ↓
[LLM Intent Router]
    ↓
MaintenanceOrchestrator
    ↓
    ├── Phase 1: Healthcheck (baseline)
    ├── Phase 2: Align (auto-fix issues)
    ├── Phase 3: Cleanup (temp files, cache)
    ├── Phase 4: Optimize (tokens, files, DB)
    ├── Phase 5: Vacuum (SQLite optimization)
    ├── Phase 6: Refresh (docs, prompts)
    └── Phase 7: Healthcheck (verify improvements)
```

### Workflow Design

**7-Phase Autonomous Workflow:**

1. **Phase 1: Baseline Healthcheck** (30 seconds)
   - Validate system health
   - Check brain databases
   - Verify core modules
   - Establish baseline metrics

2. **Phase 2: Align** (2-5 minutes)
   - Feature registration validation
   - Auto-fix wiring issues
   - Intent router coverage check
   - Response template validation
   - Obsolete code detection

3. **Phase 3: Cleanup** (1-3 minutes)
   - Remove temp files (`__pycache__`, `*.pyc`)
   - Clear old logs (>30 days)
   - Clean cache directories
   - Report space recovered

4. **Phase 4: Optimize** (2-5 minutes)
   - Token optimization (governance files)
   - File system optimization
   - Database consolidation
   - Performance tuning

5. **Phase 5: Vacuum** (30 seconds - 2 minutes)
   - Vacuum SQLite databases
   - Recover fragmented space
   - Optimize query performance

6. **Phase 6: Refresh** (1-2 minutes)
   - Update design documentation
   - Refresh prompt files
   - Regenerate indexes
   - Update timestamps

7. **Phase 7: Final Healthcheck** (30 seconds)
   - Validate improvements
   - Compare with baseline
   - Generate report
   - Show metrics delta

**Total Duration:** 7-18 minutes

### Component Mapping

| **CORTEX 3.0 Component** | **CORTEX 4.0 Location** | **Changes** |
|---------------------------|-------------------------|-------------|
| `healthcheck.py` | `cortex_orchestrators/maintenance/phases/healthcheck.py` | Extract as phase module |
| `align.py` | `cortex_orchestrators/maintenance/phases/align.py` | Extract as phase module |
| `cleanup.py` | `cortex_orchestrators/maintenance/phases/cleanup.py` | Extract as phase module |
| `optimize.py` | `cortex_orchestrators/maintenance/phases/optimize.py` | Extract as phase module |
| `vacuum_sqlite_databases_module.py` | `cortex_orchestrators/maintenance/phases/vacuum.py` | Extract as phase module |
| `refresh_design_docs_module.py` | `cortex_orchestrators/maintenance/phases/refresh.py` | Extract as phase module |

---

## 🗓️ Migration Timeline

### Day 1: Foundation & Phase Interfaces (8 hours)

**Goal:** Create directory structure and phase interface

**Tasks:**

1. **Create directory structure** (1 hour)
   ```
   cortex_orchestrators/
   └── maintenance/
       ├── __init__.py
       ├── orchestrator.py          # Main orchestrator
       ├── models.py                 # Data models
       ├── phases/
       │   ├── __init__.py
       │   ├── base.py               # Base phase interface
       │   ├── healthcheck.py        # Phase 1 & 7
       │   ├── align.py              # Phase 2
       │   ├── cleanup.py            # Phase 3
       │   ├── optimize.py           # Phase 4
       │   ├── vacuum.py             # Phase 5
       │   └── refresh.py            # Phase 6
       └── tests/
           ├── __init__.py
           ├── test_orchestrator.py
           └── test_phases.py
   ```

2. **Define phase interface** (2 hours)
   
   **File:** `cortex_orchestrators/maintenance/phases/base.py`
   ```python
   from abc import ABC, abstractmethod
   from dataclasses import dataclass
   from typing import Dict, Any, List
   from datetime import datetime
   
   @dataclass
   class PhaseResult:
       """Result of a maintenance phase."""
       phase_name: str
       success: bool
       duration_seconds: float
       metrics: Dict[str, Any]
       warnings: List[str]
       errors: List[str]
       skipped: bool = False
       
   class MaintenancePhase(ABC):
       """Base interface for maintenance phases."""
       
       @abstractmethod
       def get_phase_name(self) -> str:
           """Return phase name."""
           pass
       
       @abstractmethod
       def get_estimated_duration_seconds(self) -> int:
           """Return estimated duration in seconds."""
           pass
       
       @abstractmethod
       async def execute(self, context: Dict[str, Any]) -> PhaseResult:
           """
           Execute maintenance phase.
           
           Args:
               context: Shared context from orchestrator
               
           Returns:
               PhaseResult with execution status
           """
           pass
       
       @abstractmethod
       def is_critical(self) -> bool:
           """
           Whether phase failure should stop entire workflow.
           
           Returns:
               True if critical (stop on failure), False otherwise
           """
           pass
   ```

3. **Define data models** (2 hours)
   
   **File:** `cortex_orchestrators/maintenance/models.py`
   ```python
   from dataclasses import dataclass, field
   from datetime import datetime
   from typing import List, Dict, Any
   from enum import Enum
   
   class MaintenanceStatus(Enum):
       NOT_STARTED = "not_started"
       IN_PROGRESS = "in_progress"
       COMPLETED = "completed"
       FAILED = "failed"
       CANCELLED = "cancelled"
   
   @dataclass
   class MaintenanceMetrics:
       """Metrics from maintenance workflow."""
       baseline_health_score: float = 0.0
       final_health_score: float = 0.0
       health_improvement: float = 0.0
       
       issues_fixed: int = 0
       space_recovered_mb: float = 0.0
       files_removed: int = 0
       
       databases_vacuumed: int = 0
       db_space_recovered_mb: float = 0.0
       
       docs_refreshed: int = 0
       prompts_optimized: int = 0
       
       total_duration_seconds: float = 0.0
       
   @dataclass
   class MaintenanceReport:
       """Complete maintenance report."""
       started_at: datetime
       completed_at: datetime
       status: MaintenanceStatus
       metrics: MaintenanceMetrics
       phase_results: List[Any]  # List[PhaseResult]
       warnings: List[str] = field(default_factory=list)
       errors: List[str] = field(default_factory=list)
       
       @property
       def duration_minutes(self) -> float:
           delta = self.completed_at - self.started_at
           return delta.total_seconds() / 60
   ```

4. **Create test scaffolding** (3 hours)
   
   **File:** `cortex_orchestrators/maintenance/tests/test_orchestrator.py`
   ```python
   import pytest
   from unittest.mock import Mock, AsyncMock
   from cortex_orchestrators.maintenance.orchestrator import MaintenanceOrchestrator
   from cortex_orchestrators.maintenance.models import MaintenanceStatus
   
   @pytest.fixture
   def mock_event_bus():
       return Mock()
   
   @pytest.fixture
   def mock_brain_engine():
       return Mock()
   
   @pytest.fixture
   def orchestrator(mock_event_bus, mock_brain_engine):
       return MaintenanceOrchestrator(
           event_bus=mock_event_bus,
           brain_engine=mock_brain_engine
       )
   
   @pytest.mark.asyncio
   async def test_full_maintenance_workflow(orchestrator):
       """Test complete 7-phase maintenance workflow."""
       report = await orchestrator.run_maintenance()
       
       assert report.status == MaintenanceStatus.COMPLETED
       assert len(report.phase_results) == 7
       assert report.metrics.final_health_score > report.metrics.baseline_health_score
   
   @pytest.mark.asyncio
   async def test_phase_failure_recovery(orchestrator):
       """Test non-critical phase failure doesn't stop workflow."""
       # Mock phase 3 (cleanup) to fail
       orchestrator.phases[2].execute = AsyncMock(side_effect=Exception("Mock failure"))
       
       report = await orchestrator.run_maintenance()
       
       # Workflow should continue despite cleanup failure
       assert report.status == MaintenanceStatus.COMPLETED
       assert len(report.errors) > 0
   ```

**Deliverables (Day 1):**
- ✅ Directory structure created
- ✅ Phase interface defined (`MaintenancePhase`)
- ✅ Data models defined (`MaintenanceMetrics`, `MaintenanceReport`)
- ✅ Test scaffolding ready

---

### Day 2: Core Orchestrator & Phase Migration (8 hours)

**Goal:** Implement MaintenanceOrchestrator and migrate 3 phases

**Tasks:**

1. **Implement MaintenanceOrchestrator** (4 hours)
   
   **File:** `cortex_orchestrators/maintenance/orchestrator.py`
   ```python
   from typing import Optional, List
   import logging
   from datetime import datetime
   
   from cortex_core.event_bus import EventBus
   from cortex_core.brain_engine import BrainEngine
   from cortex_mcp.server import MCPServer
   
   from .phases.base import MaintenancePhase, PhaseResult
   from .phases.healthcheck import HealthcheckPhase
   from .phases.align import AlignPhase
   from .phases.cleanup import CleanupPhase
   from .phases.optimize import OptimizePhase
   from .phases.vacuum import VacuumPhase
   from .phases.refresh import RefreshPhase
   from .models import MaintenanceReport, MaintenanceStatus, MaintenanceMetrics
   
   logger = logging.getLogger(__name__)
   
   class MaintenanceOrchestrator:
       """
       System maintenance orchestrator with 7-phase workflow.
       
       Phases:
       1. Baseline Healthcheck (establish metrics)
       2. Align (auto-fix system issues)
       3. Cleanup (remove temp files, logs)
       4. Optimize (tokens, files, databases)
       5. Vacuum (SQLite optimization)
       6. Refresh (docs, prompts)
       7. Final Healthcheck (verify improvements)
       
       Features:
       - Autonomous execution (no user prompts per phase)
       - Real-time progress tracking
       - Error recovery (non-critical phases)
       - MCP integration
       """
       
       def __init__(
           self,
           event_bus: EventBus,
           brain_engine: BrainEngine,
           mcp_server: Optional[MCPServer] = None
       ):
           self.event_bus = event_bus
           self.brain_engine = brain_engine
           self.mcp_server = mcp_server
           
           # Initialize phases
           self.phases: List[MaintenancePhase] = [
               HealthcheckPhase(is_baseline=True),    # Phase 1
               AlignPhase(),                           # Phase 2
               CleanupPhase(),                         # Phase 3
               OptimizePhase(),                        # Phase 4
               VacuumPhase(),                          # Phase 5
               RefreshPhase(),                         # Phase 6
               HealthcheckPhase(is_baseline=False)    # Phase 7
           ]
           
           # Register MCP tools
           if self.mcp_server:
               self._register_mcp_tools()
           
           logger.info("🎭 MaintenanceOrchestrator initialized")
           logger.info(f"   ✅ 7 phases loaded")
       
       async def run_maintenance(
           self,
           skip_phases: Optional[List[str]] = None
       ) -> MaintenanceReport:
           """
           Run complete maintenance workflow.
           
           Args:
               skip_phases: Optional list of phase names to skip
               
           Returns:
               MaintenanceReport with results
           """
           logger.info("🚀 Starting system maintenance workflow")
           
           started_at = datetime.now()
           phase_results: List[PhaseResult] = []
           metrics = MaintenanceMetrics()
           warnings: List[str] = []
           errors: List[str] = []
           
           # Emit start event
           self.event_bus.emit("maintenance.started", {
               "total_phases": len(self.phases)
           })
           
           # Execute phases
           for idx, phase in enumerate(self.phases, 1):
               phase_name = phase.get_phase_name()
               
               # Check skip list
               if skip_phases and phase_name in skip_phases:
                   logger.info(f"⏭️  Skipping phase {idx}: {phase_name}")
                   phase_results.append(PhaseResult(
                       phase_name=phase_name,
                       success=True,
                       duration_seconds=0,
                       metrics={},
                       warnings=[],
                       errors=[],
                       skipped=True
                   ))
                   continue
               
               logger.info(f"🔄 Phase {idx}/7: {phase_name}")
               
               # Emit phase start event
               self.event_bus.emit("maintenance.phase_started", {
                   "phase_number": idx,
                   "phase_name": phase_name,
                   "estimated_duration": phase.get_estimated_duration_seconds()
               })
               
               try:
                   # Execute phase
                   context = {
                       "brain_engine": self.brain_engine,
                       "event_bus": self.event_bus,
                       "phase_number": idx,
                       "baseline_metrics": metrics if idx == 1 else None
                   }
                   
                   result = await phase.execute(context)
                   phase_results.append(result)
                   
                   # Update metrics
                   self._update_metrics(metrics, result)
                   
                   # Collect warnings/errors
                   warnings.extend(result.warnings)
                   errors.extend(result.errors)
                   
                   if result.success:
                       logger.info(f"✅ Phase {idx} complete: {phase_name}")
                   else:
                       logger.warning(f"⚠️  Phase {idx} failed: {phase_name}")
                       
                       # Critical phase failure stops workflow
                       if phase.is_critical():
                           logger.error("🛑 Critical phase failed, stopping workflow")
                           break
                   
                   # Emit phase complete event
                   self.event_bus.emit("maintenance.phase_completed", {
                       "phase_number": idx,
                       "phase_name": phase_name,
                       "success": result.success,
                       "duration": result.duration_seconds
                   })
                   
               except Exception as e:
                   logger.error(f"❌ Phase {idx} error: {e}")
                   errors.append(f"Phase {idx} ({phase_name}): {str(e)}")
                   
                   # Critical phase exception stops workflow
                   if phase.is_critical():
                       logger.error("🛑 Critical phase exception, stopping workflow")
                       break
           
           # Calculate final metrics
           completed_at = datetime.now()
           metrics.total_duration_seconds = (completed_at - started_at).total_seconds()
           
           # Determine status
           if len(phase_results) < len(self.phases):
               status = MaintenanceStatus.FAILED
           elif errors:
               status = MaintenanceStatus.COMPLETED  # Completed with warnings
           else:
               status = MaintenanceStatus.COMPLETED
           
           # Create report
           report = MaintenanceReport(
               started_at=started_at,
               completed_at=completed_at,
               status=status,
               metrics=metrics,
               phase_results=phase_results,
               warnings=warnings,
               errors=errors
           )
           
           # Emit completion event
           self.event_bus.emit("maintenance.completed", {
               "status": status.value,
               "duration_minutes": report.duration_minutes,
               "health_improvement": metrics.health_improvement,
               "space_recovered_mb": metrics.space_recovered_mb
           })
           
           # Store report in brain
           await self.brain_engine.store_maintenance_report(report)
           
           logger.info(f"✅ Maintenance workflow complete: {status.value}")
           logger.info(f"   Duration: {report.duration_minutes:.1f} minutes")
           logger.info(f"   Health improvement: {metrics.health_improvement:.1f}%")
           logger.info(f"   Space recovered: {metrics.space_recovered_mb:.1f} MB")
           
           return report
       
       def _update_metrics(self, metrics: MaintenanceMetrics, 
                          result: PhaseResult) -> None:
           """Update metrics from phase result."""
           phase_metrics = result.metrics
           
           # Healthcheck metrics
           if "health_score" in phase_metrics:
               if metrics.baseline_health_score == 0:
                   metrics.baseline_health_score = phase_metrics["health_score"]
               else:
                   metrics.final_health_score = phase_metrics["health_score"]
                   metrics.health_improvement = (
                       metrics.final_health_score - metrics.baseline_health_score
                   )
           
           # Align metrics
           if "issues_fixed" in phase_metrics:
               metrics.issues_fixed += phase_metrics["issues_fixed"]
           
           # Cleanup metrics
           if "space_recovered_mb" in phase_metrics:
               metrics.space_recovered_mb += phase_metrics["space_recovered_mb"]
           if "files_removed" in phase_metrics:
               metrics.files_removed += phase_metrics["files_removed"]
           
           # Vacuum metrics
           if "databases_vacuumed" in phase_metrics:
               metrics.databases_vacuumed = phase_metrics["databases_vacuumed"]
           if "db_space_recovered_mb" in phase_metrics:
               metrics.db_space_recovered_mb = phase_metrics["db_space_recovered_mb"]
           
           # Refresh metrics
           if "docs_refreshed" in phase_metrics:
               metrics.docs_refreshed = phase_metrics["docs_refreshed"]
           if "prompts_optimized" in phase_metrics:
               metrics.prompts_optimized = phase_metrics["prompts_optimized"]
       
       def _register_mcp_tools(self):
           """Register MCP tools for maintenance operations."""
           
           @self.mcp_server.tool("cortex_maintenance")
           async def maintenance_tool(
               skip_phases: list[str] = None
           ):
               """
               Run complete system maintenance workflow.
               
               Executes 7 phases: healthcheck, align, cleanup, 
               optimize, vacuum, refresh, healthcheck.
               """
               report = await self.run_maintenance(skip_phases=skip_phases)
               
               return {
                   "status": report.status.value,
                   "duration_minutes": report.duration_minutes,
                   "health_improvement": report.metrics.health_improvement,
                   "space_recovered_mb": report.metrics.space_recovered_mb,
                   "errors": len(report.errors)
               }
           
           logger.info("🔧 MCP tools registered: cortex_maintenance")
   ```

2. **Migrate Healthcheck phase** (2 hours)
   
   **File:** `cortex_orchestrators/maintenance/phases/healthcheck.py`
   ```python
   from typing import Dict, Any
   from datetime import datetime
   import logging
   
   from .base import MaintenancePhase, PhaseResult
   
   logger = logging.getLogger(__name__)
   
   class HealthcheckPhase(MaintenancePhase):
       """
       Healthcheck maintenance phase.
       
       Validates:
       - Brain databases accessible
       - Core modules importable
       - Critical files present
       - Configuration valid
       """
       
       def __init__(self, is_baseline: bool = True):
           self.is_baseline = is_baseline
       
       def get_phase_name(self) -> str:
           return "Baseline Healthcheck" if self.is_baseline else "Final Healthcheck"
       
       def get_estimated_duration_seconds(self) -> int:
           return 30
       
       def is_critical(self) -> bool:
           return self.is_baseline  # Baseline is critical
       
       async def execute(self, context: Dict[str, Any]) -> PhaseResult:
           """Execute healthcheck."""
           start_time = datetime.now()
           
           logger.info(f"🏥 Running {self.get_phase_name()}")
           
           # Import healthcheck utility
           from src.operations.modules.admin.healthcheck_utility import (
               run_healthcheck_utility
           )
           
           # Run healthcheck
           result = run_healthcheck_utility()
           
           # Calculate health score
           health_score = self._calculate_health_score(result)
           
           duration = (datetime.now() - start_time).total_seconds()
           
           return PhaseResult(
               phase_name=self.get_phase_name(),
               success=result["success"],
               duration_seconds=duration,
               metrics={"health_score": health_score},
               warnings=result.get("warnings", []),
               errors=result.get("errors", [])
           )
       
       def _calculate_health_score(self, result: Dict[str, Any]) -> float:
           """Calculate 0-100 health score."""
           # Simple scoring: 100 if success, 50 if warnings, 0 if errors
           if not result["success"]:
               return 0.0
           
           warnings = len(result.get("warnings", []))
           if warnings == 0:
               return 100.0
           elif warnings < 3:
               return 80.0
           elif warnings < 5:
               return 60.0
           else:
               return 40.0
   ```

3. **Migrate Align phase** (1 hour)
4. **Migrate Cleanup phase** (1 hour)

**Deliverables (Day 2):**
- ✅ `MaintenanceOrchestrator` implemented
- ✅ 3 phases migrated (Healthcheck, Align, Cleanup)
- ✅ MCP tools registered

---

### Day 3: Remaining Phases & Testing (8 hours)

**Goal:** Migrate 4 remaining phases and comprehensive testing

**Tasks:**

1. **Migrate Optimize phase** (1 hour)
2. **Migrate Vacuum phase** (1 hour)
3. **Migrate Refresh phase** (1 hour)
4. **Unit tests** (2 hours) - 30 tests
5. **Integration tests** (2 hours) - 10 tests
6. **E2E test** (1 hour) - Full workflow test

**Deliverables (Day 3):**
- ✅ All 7 phases migrated
- ✅ 40 unit tests passing
- ✅ 95%+ code coverage
- ✅ Full workflow E2E test passing

---

## 🧪 Testing Strategy

### Unit Tests (30 tests)

1. **Orchestrator** (10 tests)
   - Full workflow execution
   - Phase skipping
   - Error recovery (non-critical)
   - Critical phase failure stops workflow
   - Metrics aggregation

2. **Phases** (20 tests)
   - Each phase executes successfully
   - Each phase handles errors gracefully
   - Phase metrics correctly reported
   - Critical vs non-critical behavior

### Integration Tests (10 tests)

1. **End-to-End** (5 tests)
   - Complete workflow with all phases
   - Workflow with skipped phases
   - Baseline vs final healthcheck comparison

2. **MCP Tools** (3 tests)
   - `cortex_maintenance` tool invocation
   - Progress event emission
   - Error handling

3. **Event Bus** (2 tests)
   - Phase start/complete events
   - Workflow completion events

---

## 📊 Success Metrics

- ✅ 7 operations consolidated into 1 orchestrator
- ✅ Autonomous execution (no per-phase prompts)
- ✅ 40 tests passing (95%+ coverage)
- ✅ 7-18 minute execution time
- ✅ Health improvement tracked

---

**Approval Checklist:**

- [ ] Architecture approved (7-phase workflow)
- [ ] Timeline realistic (3 days = 24 hours)
- [ ] Test coverage sufficient (40 tests)
- [ ] Autonomous execution designed
- [ ] Progress tracking implemented

**Sign-off:** _________________________________  Date: ___________
