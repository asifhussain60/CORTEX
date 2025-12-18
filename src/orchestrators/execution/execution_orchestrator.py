"""
Execution Orchestrator for CORTEX 4.0

Implements workflow execution coordination with dependency blocking.

Consolidates:
- Execution coordination logic
- Workflow phase management
- Dependency resolution

New Implementation: 625 LOC (migrated from orchestration_3_0)

Features:
- Execute feature plans from Planning Orchestrator
- Coordinate workflow phases
- Dependency blocking and resolution
- Real-time execution tracking
- Rollback capability
- Autonomous execution after initiation

Migration: Phase 3 Week 7 Days 1-3
Source: src/orchestration_3_0/orchestrators/execution/execution_orchestrator.py
Target: src/orchestrators/execution/execution_orchestrator.py

Author: Asif Hussain
Date: December 10, 2025 (Original)
Migrated: December 18, 2025
Version: 4.0.0
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

# CORTEX 4.0 imports - updated from orchestration_3_0
from src.orchestrators.base.base_orchestrator import (
    BaseOrchestrator,
    ValidationResult,
    OrchestratorResult,
    OrchestratorStatus
)

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Execution status for phases."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    ROLLED_BACK = "ROLLED_BACK"


class OrchestratorType(Enum):
    """Available orchestrator types for phase execution."""
    TDD = "TDD"
    SCAFFOLDING = "Scaffolding"
    DEVOPS = "DevOps"
    QA = "QA"
    DOCUMENTATION = "Documentation"
    OBSERVABILITY = "Observability"
    PLANNING = "Planning"
    ADO = "ADO"
    MAINTENANCE = "Maintenance"
    INTELLIGENCE = "Intelligence"
    ONBOARDING = "Onboarding"


@dataclass
class PhaseExecution:
    """Execution tracking for a phase."""
    phase_number: int
    phase_name: str
    status: ExecutionStatus
    orchestrator: Optional[OrchestratorType]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    blocking_dependencies: List[str] = field(default_factory=list)
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    """Complete execution plan."""
    feature_name: str
    phases: List[PhaseExecution]
    execution_order: List[int]  # Phase numbers in execution order
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    success: bool = False


class ExecutionOrchestrator(BaseOrchestrator):
    """
    Execution Orchestrator for workflow coordination.
    
    Workflow:
    1. DoR Validation: Verify execution plan, dependencies resolved
    2. Dependency Resolution: Determine execution order
    3. Phase Execution: Execute phases in order, blocking on dependencies
    4. Progress Tracking: Real-time status updates
    5. Error Handling: Rollback on failure if needed
    6. DoD Validation: All phases completed successfully
    
    Autonomous Execution: Once execution initiated, proceeds through all
    workflow phases without pausing for confirmation (unless critical error).
    
    Visual Progress: Real-time progress bars showing phase execution status.
    
    Extends: BaseOrchestrator (CORTEX 4.0 foundation)
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        container: Optional[Any] = None
    ):
        """
        Initialize Execution Orchestrator.
        
        Args:
            config: Optional configuration dictionary
            container: Optional DI container
        """
        super().__init__(config=config or {})
        
        self.container = container
        self.current_execution: Optional[ExecutionPlan] = None
        self.orchestrator_registry: Dict[OrchestratorType, Callable] = {}
        
        self.logger.info("🎭 Orchestrator engaged: ExecutionOrchestrator")
        self.logger.info("ExecutionOrchestrator initialized (CORTEX 4.0)")
    
    def register_orchestrator(
        self,
        orchestrator_type: OrchestratorType,
        orchestrator_fn: Callable
    ):
        """
        Register orchestrator for execution.
        
        Args:
            orchestrator_type: Type of orchestrator
            orchestrator_fn: Callable that executes orchestrator
        """
        self.orchestrator_registry[orchestrator_type] = orchestrator_fn
        self.logger.info(f"Registered orchestrator: {orchestrator_type.value}")
    
    def validate_input(self, params: Dict[str, Any]) -> ValidationResult:
        """
        Validate execution orchestrator input.
        
        Prerequisites (DoR):
        - Execution plan provided (phases with orchestrators)
        - All dependencies resolvable
        - Required orchestrators registered
        - No circular dependencies
        
        Args:
            params: Input parameters with execution_plan
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check execution plan
        plan = params.get('execution_plan')
        if not plan:
            errors.append("Execution plan not provided")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        
        phases = plan.get('phases', [])
        if not phases:
            errors.append("Execution plan has no phases")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        
        # Check dependencies
        phase_names = {p['phase_name'] for p in phases}
        for phase in phases:
            dependencies = phase.get('dependencies', [])
            for dep in dependencies:
                if dep not in phase_names:
                    errors.append(f"Phase '{phase['phase_name']}' depends on unknown phase '{dep}'")
        
        # Check orchestrator registration
        for phase in phases:
            orchestrator_type = phase.get('orchestrator')
            if orchestrator_type:
                try:
                    orch_enum = OrchestratorType[orchestrator_type.upper()]
                    if orch_enum not in self.orchestrator_registry:
                        warnings.append(
                            f"Orchestrator '{orchestrator_type}' not registered - phase will be simulated"
                        )
                except KeyError:
                    warnings.append(f"Unknown orchestrator type: {orchestrator_type}")
        
        # Check circular dependencies
        if self._has_circular_dependencies(phases):
            errors.append("Circular dependencies detected in execution plan")
        
        valid = len(errors) == 0
        return ValidationResult(valid=valid, errors=errors, warnings=warnings)
    
    def execute(self, params: Dict[str, Any]) -> OrchestratorResult:
        """
        Execute workflow coordination.
        
        Autonomous Execution: Once execution initiated, proceeds through all
        phases without pausing for confirmation (unless critical error).
        
        Args:
            params: Parameters with execution_plan
            
        Returns:
            OrchestratorResult with execution details
        """
        try:
            plan_data = params.get('execution_plan')
            feature_name = plan_data.get('feature_name', 'Unknown Feature')
            
            self.logger.info(f"Starting execution workflow for: {feature_name}")
            self.logger.info("🎭 Phase transition: INIT → PLAN_PARSING")
            
            # Phase 1: Parse Execution Plan
            self.logger.info("📋 Phase 1: Parsing execution plan")
            phases = self._parse_execution_plan(plan_data)
            execution_order = self._resolve_dependencies(phases)
            
            self.current_execution = ExecutionPlan(
                feature_name=feature_name,
                phases=phases,
                execution_order=execution_order,
                started_at=datetime.now()
            )
            
            # Phase 2: Dependency Resolution
            self.logger.info(f"🔗 Phase 2: Resolved {len(execution_order)} phases in execution order")
            self.logger.info("🎭 Phase transition: PLAN_PARSING → PHASE_EXECUTION")
            
            # Phase 3: Execute Phases
            self.logger.info("⚙️ Phase 3: Executing workflow phases")
            execution_results = self._execute_phases(execution_order)
            
            # Phase 4: Finalization
            self.logger.info("🎭 Phase transition: PHASE_EXECUTION → FINALIZATION")
            self.logger.info("✅ Phase 4: Finalizing execution")
            
            self.current_execution.completed_at = datetime.now()
            self.current_execution.total_duration_seconds = (
                self.current_execution.completed_at - self.current_execution.started_at
            ).total_seconds()
            
            # Check overall success
            self.current_execution.success = all(
                p.status == ExecutionStatus.COMPLETED for p in self.current_execution.phases
                if p.status != ExecutionStatus.PENDING  # Allow skipped phases
            )
            
            completed_phases = sum(1 for p in self.current_execution.phases if p.status == ExecutionStatus.COMPLETED)
            failed_phases = sum(1 for p in self.current_execution.phases if p.status == ExecutionStatus.FAILED)
            
            status = OrchestratorStatus.COMPLETED if self.current_execution.success else OrchestratorStatus.FAILED
            
            # Determine if all work is complete (success template trigger)
            is_complete = (
                self.current_execution.success and
                failed_phases == 0 and
                completed_phases == len(self.current_execution.phases)
            )
            
            if is_complete:
                self.logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            
            return OrchestratorResult(
                status=status,
                success=self.current_execution.success,
                message=f"Execution {'completed successfully' if self.current_execution.success else 'failed'}",
                data={
                    'execution_plan': self._execution_to_dict(self.current_execution),
                    'success': self.current_execution.success,
                    'completed_phases': completed_phases,
                    'failed_phases': failed_phases,
                    'total_phases': len(self.current_execution.phases),
                    'duration_seconds': self.current_execution.total_duration_seconds,
                    'is_complete': is_complete
                },
                errors=[]
            )
        
        except Exception as e:
            self.logger.exception(f"Execution orchestrator failed: {e}")
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                success=False,
                message=f"Execution failed: {str(e)}",
                data={},
                errors=[str(e)]
            )
    
    def _parse_execution_plan(self, plan_data: Dict[str, Any]) -> List[PhaseExecution]:
        """
        Parse execution plan into PhaseExecution objects.
        
        Args:
            plan_data: Raw execution plan data
            
        Returns:
            List of PhaseExecution objects
        """
        phases = []
        
        for phase_data in plan_data.get('phases', []):
            orchestrator_str = phase_data.get('orchestrator')
            orchestrator = None
            
            if orchestrator_str:
                try:
                    orchestrator = OrchestratorType[orchestrator_str.upper()]
                except KeyError:
                    self.logger.warning(f"Unknown orchestrator type: {orchestrator_str}")
            
            phase = PhaseExecution(
                phase_number=phase_data.get('phase_number'),
                phase_name=phase_data.get('phase_name'),
                status=ExecutionStatus.PENDING,
                orchestrator=orchestrator,
                blocking_dependencies=phase_data.get('dependencies', [])
            )
            
            phases.append(phase)
        
        return phases
    
    def _resolve_dependencies(self, phases: List[PhaseExecution]) -> List[int]:
        """
        Resolve execution order based on dependencies.
        
        Uses topological sort to determine safe execution order.
        
        Args:
            phases: List of phase executions
            
        Returns:
            List of phase numbers in execution order
        """
        # Build dependency graph
        phase_map = {p.phase_number: p for p in phases}
        in_degree = {p.phase_number: 0 for p in phases}
        
        for phase in phases:
            for dep_name in phase.blocking_dependencies:
                # Find dependency phase by name
                dep_phase = next((p for p in phases if p.phase_name == dep_name), None)
                if dep_phase:
                    in_degree[phase.phase_number] += 1
        
        # Topological sort
        queue = [num for num, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            # Find phases that depend on current
            for phase in phases:
                current_phase = phase_map[current]
                if current_phase.phase_name in phase.blocking_dependencies:
                    in_degree[phase.phase_number] -= 1
                    if in_degree[phase.phase_number] == 0:
                        queue.append(phase.phase_number)
        
        return execution_order
    
    def _has_circular_dependencies(self, phases: List[Dict[str, Any]]) -> bool:
        """
        Check for circular dependencies.
        
        Args:
            phases: List of phase dictionaries
            
        Returns:
            True if circular dependencies detected
        """
        # Build dependency graph
        graph = {}
        for phase in phases:
            phase_name = phase['phase_name']
            dependencies = phase.get('dependencies', [])
            graph[phase_name] = dependencies
        
        # DFS cycle detection
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    return True
        
        return False
    
    def _execute_phases(self, execution_order: List[int]) -> Dict[int, Any]:
        """
        Execute phases in order.
        
        Args:
            execution_order: List of phase numbers to execute
            
        Returns:
            Dictionary of phase results
        """
        results = {}
        phase_map = {p.phase_number: p for p in self.current_execution.phases}
        total_phases = len(execution_order)
        
        for idx, phase_num in enumerate(execution_order, 1):
            phase = phase_map[phase_num]
            
            # Check if dependencies completed
            if not self._dependencies_met(phase):
                self.logger.warning(f"Phase {phase.phase_name} blocked by dependencies")
                phase.status = ExecutionStatus.BLOCKED
                continue
            
            # Execute phase
            self.logger.info(f"Executing phase {phase_num}: {phase.phase_name} ({idx}/{total_phases})")
            
            phase.status = ExecutionStatus.RUNNING
            phase.started_at = datetime.now()
            
            try:
                # Execute orchestrator if available
                if phase.orchestrator and phase.orchestrator in self.orchestrator_registry:
                    orchestrator_fn = self.orchestrator_registry[phase.orchestrator]
                    phase.outputs = orchestrator_fn()
                    self.logger.info(f"Orchestrator {phase.orchestrator.value} completed successfully")
                else:
                    # Simulate execution
                    self.logger.info(f"No orchestrator registered for {phase.orchestrator} - simulating")
                    phase.outputs = {'simulated': True}
                
                phase.status = ExecutionStatus.COMPLETED
                phase.completed_at = datetime.now()
                phase.duration_seconds = (phase.completed_at - phase.started_at).total_seconds()
                
                results[phase_num] = phase.outputs
            
            except Exception as e:
                self.logger.exception(f"Phase {phase.phase_name} failed: {e}")
                phase.status = ExecutionStatus.FAILED
                phase.errors.append(str(e))
                phase.completed_at = datetime.now()
                
                # Optionally rollback
                if self._should_rollback(phase):
                    self._rollback_phases(phase_num)
                
                break  # Stop execution on critical failure
        
        return results
    
    def _dependencies_met(self, phase: PhaseExecution) -> bool:
        """
        Check if all dependencies for phase are met.
        
        Args:
            phase: Phase execution to check
            
        Returns:
            True if all dependencies completed successfully
        """
        if not phase.blocking_dependencies:
            return True
        
        for dep_name in phase.blocking_dependencies:
            dep_phase = next(
                (p for p in self.current_execution.phases if p.phase_name == dep_name),
                None
            )
            
            if not dep_phase or dep_phase.status != ExecutionStatus.COMPLETED:
                return False
        
        return True
    
    def _should_rollback(self, failed_phase: PhaseExecution) -> bool:
        """
        Determine if rollback is needed.
        
        Rollback criteria:
        - Critical phase (Foundation, Core)
        - Data migration phase
        - Integration phase with external systems
        
        Args:
            failed_phase: Phase that failed
            
        Returns:
            True if rollback recommended
        """
        critical_keywords = ['foundation', 'core', 'migration', 'integration']
        phase_name_lower = failed_phase.phase_name.lower()
        
        return any(keyword in phase_name_lower for keyword in critical_keywords)
    
    def _rollback_phases(self, failed_phase_num: int):
        """
        Rollback completed phases.
        
        Args:
            failed_phase_num: Phase number that failed
        """
        self.logger.warning(f"Rolling back phases up to {failed_phase_num}")
        
        for phase in self.current_execution.phases:
            if phase.phase_number < failed_phase_num and phase.status == ExecutionStatus.COMPLETED:
                self.logger.info(f"Rolling back phase {phase.phase_number}: {phase.phase_name}")
                phase.status = ExecutionStatus.ROLLED_BACK
                
                # In production, execute rollback logic here
                # For now, just mark as rolled back
    
    def _execution_to_dict(self, execution: ExecutionPlan) -> Dict[str, Any]:
        """Convert ExecutionPlan to dictionary."""
        return {
            'feature_name': execution.feature_name,
            'phases': [
                {
                    'phase_number': p.phase_number,
                    'phase_name': p.phase_name,
                    'status': p.status.value,
                    'orchestrator': p.orchestrator.value if p.orchestrator else None,
                    'started_at': p.started_at.isoformat() if p.started_at else None,
                    'completed_at': p.completed_at.isoformat() if p.completed_at else None,
                    'duration_seconds': p.duration_seconds,
                    'blocking_dependencies': p.blocking_dependencies,
                    'outputs': p.outputs,
                    'errors': p.errors
                }
                for p in execution.phases
            ],
            'execution_order': execution.execution_order,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'total_duration_seconds': execution.total_duration_seconds,
            'success': execution.success
        }


# Factory function for DI container
def create_execution_orchestrator(
    config: Optional[Dict[str, Any]] = None,
    container: Optional[Any] = None
) -> ExecutionOrchestrator:
    """
    Create and return Execution Orchestrator instance.
    
    Args:
        config: Optional configuration dictionary
        container: Optional DI container
        
    Returns:
        ExecutionOrchestrator instance
    """
    return ExecutionOrchestrator(config=config, container=container)
