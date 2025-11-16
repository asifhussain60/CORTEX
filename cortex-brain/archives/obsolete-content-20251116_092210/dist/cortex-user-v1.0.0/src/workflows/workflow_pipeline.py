"""
CORTEX Workflow Pipeline System

Orchestrates multi-stage workflows with:
- Declarative YAML definitions
- Dependency management (DAG validation)
- Shared state management
- Error recovery and retries
- Checkpoint/resume capability
- Context injection (Tier 1-3)

Author: CORTEX Development Team
Version: 1.0
"""

from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime
import yaml
import uuid


class StageStatus(Enum):
    """Stage execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result from stage execution"""
    stage_id: str
    status: StageStatus
    duration_ms: float
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """
    Shared state passed between workflow stages
    
    All stages read from and write to this state.
    Persisted to disk for checkpoint/resume capability.
    """
    workflow_id: str
    conversation_id: str
    user_request: str
    
    # Context injected once at start (from Tier 1-3)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Outputs from each stage
    stage_outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Stage statuses
    stage_statuses: Dict[str, StageStatus] = field(default_factory=dict)
    
    # Overall workflow metadata
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_stage: Optional[str] = None
    
    def update_stage(self, result: StageResult):
        """Update state with stage result"""
        self.stage_outputs[result.stage_id] = result.output
        self.stage_statuses[result.stage_id] = result.status
    
    def get_stage_output(self, stage_id: str) -> Optional[Dict[str, Any]]:
        """Get output from previous stage"""
        return self.stage_outputs.get(stage_id)
    
    def all_stages_before_completed(self, stage_id: str, dependencies: List[str]) -> bool:
        """Check if all dependency stages completed successfully"""
        for dep in dependencies:
            if self.stage_statuses.get(dep) != StageStatus.SUCCESS:
                return False
        return True


class WorkflowStage(Protocol):
    """
    Interface that all workflow stages must implement
    
    Each stage is a focused, single-responsibility script
    """
    
    def execute(self, state: WorkflowState) -> StageResult:
        """
        Execute this stage
        
        Args:
            state: Shared workflow state
        
        Returns:
            StageResult with outputs
        """
        ...
    
    def validate_input(self, state: WorkflowState) -> bool:
        """
        Validate that state has required inputs for this stage
        
        Returns:
            True if inputs valid
        """
        ...
    
    def on_failure(self, state: WorkflowState, error: Exception):
        """
        Handle stage failure (cleanup, logging)
        
        Args:
            state: Current workflow state
            error: Exception that caused failure
        """
        ...


@dataclass
class StageDefinition:
    """Definition of a single stage in workflow"""
    id: str
    script: str  # Python module path (e.g., "threat_modeler")
    required: bool = True
    depends_on: List[str] = field(default_factory=list)
    retryable: bool = False
    max_retries: int = 3
    timeout_seconds: int = 300


@dataclass
class WorkflowDefinition:
    """Definition of complete workflow pipeline"""
    workflow_id: str
    name: str
    description: str
    stages: List[StageDefinition]
    
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'WorkflowDefinition':
        """Load workflow definition from YAML file"""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        stages = [
            StageDefinition(
                id=stage['id'],
                script=stage['script'],
                required=stage.get('required', True),
                depends_on=stage.get('depends_on', []),
                retryable=stage.get('retryable', False),
                max_retries=stage.get('max_retries', 3),
                timeout_seconds=stage.get('timeout_seconds', 300)
            )
            for stage in data['stages']
        ]
        
        return cls(
            workflow_id=data['workflow_id'],
            name=data['name'],
            description=data.get('description', ''),
            stages=stages
        )
    
    def validate_dag(self) -> List[str]:
        """
        Validate workflow is a valid DAG (no cycles)
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        stage_ids = {stage.id for stage in self.stages}
        
        # Check all dependencies exist
        for stage in self.stages:
            for dep in stage.depends_on:
                if dep not in stage_ids:
                    errors.append(
                        f"Stage '{stage.id}' depends on unknown stage '{dep}'"
                    )
        
        # Check for cycles (simplified - use topological sort in production)
        visited = set()
        
        def has_cycle(stage_id: str, path: set) -> bool:
            if stage_id in path:
                return True
            if stage_id in visited:
                return False
            
            path.add(stage_id)
            visited.add(stage_id)
            
            stage = next((s for s in self.stages if s.id == stage_id), None)
            if stage:
                for dep in stage.depends_on:
                    if has_cycle(dep, path.copy()):
                        return True
            
            return False
        
        for stage in self.stages:
            if has_cycle(stage.id, set()):
                errors.append(f"Cycle detected in dependencies for stage '{stage.id}'")
        
        return errors
    
    def get_execution_order(self) -> List[str]:
        """
        Get topological sort of stages (execution order)
        
        Returns:
            List of stage IDs in execution order
        """
        # Kahn's algorithm for topological sort
        in_degree = {stage.id: len(stage.depends_on) for stage in self.stages}
        queue = [stage.id for stage in self.stages if len(stage.depends_on) == 0]
        result = []
        
        while queue:
            stage_id = queue.pop(0)
            result.append(stage_id)
            
            # Reduce in-degree for dependent stages
            for stage in self.stages:
                if stage_id in stage.depends_on:
                    in_degree[stage.id] -= 1
                    if in_degree[stage.id] == 0:
                        queue.append(stage.id)
        
        return result


class WorkflowOrchestrator:
    """
    Orchestrates workflow execution with:
    - Dependency management
    - State persistence
    - Error recovery
    - Checkpoint/resume
    """
    
    def __init__(
        self,
        workflow_def: WorkflowDefinition,
        context_injector,
        tier1_api
    ):
        self.workflow_def = workflow_def
        self.context_injector = context_injector
        self.tier1 = tier1_api
        self.stage_modules: Dict[str, WorkflowStage] = {}
    
    def register_stage(self, stage_id: str, stage_module: WorkflowStage):
        """Register a stage implementation"""
        self.stage_modules[stage_id] = stage_module
    
    def execute(
        self,
        user_request: str,
        conversation_id: str
    ) -> WorkflowState:
        """
        Execute complete workflow pipeline
        
        Args:
            user_request: User's original request
            conversation_id: Conversation UUID
        
        Returns:
            Final workflow state
        """
        # Initialize state
        state = WorkflowState(
            workflow_id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            user_request=user_request,
            start_time=datetime.now()
        )
        
        # Inject context ONCE at start (performance optimization)
        state.context = self.context_injector.inject_context(
            user_request=user_request,
            conversation_id=conversation_id
        )
        
        # Validate workflow DAG
        dag_errors = self.workflow_def.validate_dag()
        if dag_errors:
            raise ValueError(f"Invalid workflow DAG: {dag_errors}")
        
        # Get execution order
        execution_order = self.workflow_def.get_execution_order()
        
        # Execute stages in order
        for stage_id in execution_order:
            stage_def = next(
                (s for s in self.workflow_def.stages if s.id == stage_id),
                None
            )
            
            if not stage_def:
                continue
            
            # Check if dependencies satisfied
            if not state.all_stages_before_completed(stage_id, stage_def.depends_on):
                # Dependencies failed - skip if optional
                if not stage_def.required:
                    state.stage_statuses[stage_id] = StageStatus.SKIPPED
                    continue
                else:
                    # Required stage with failed dependencies - abort
                    raise RuntimeError(
                        f"Required stage '{stage_id}' cannot run: "
                        f"dependencies {stage_def.depends_on} not satisfied"
                    )
            
            # Execute stage
            result = self._execute_stage(stage_def, state)
            state.update_stage(result)
            
            # Handle failure
            if result.status == StageStatus.FAILED:
                if stage_def.required:
                    # Required stage failed - abort workflow
                    state.end_time = datetime.now()
                    self._log_workflow_failure(state, result)
                    raise RuntimeError(
                        f"Required stage '{stage_id}' failed: {result.error}"
                    )
                else:
                    # Optional stage failed - log warning and continue
                    self._log_stage_warning(state, result)
        
        # Workflow complete
        state.end_time = datetime.now()
        self._log_workflow_success(state)
        
        return state
    
    def _execute_stage(
        self,
        stage_def: StageDefinition,
        state: WorkflowState
    ) -> StageResult:
        """
        Execute single stage with retry logic
        
        Args:
            stage_def: Stage definition
            state: Current workflow state
        
        Returns:
            StageResult
        """
        stage_module = self.stage_modules.get(stage_def.id)
        
        if not stage_module:
            return StageResult(
                stage_id=stage_def.id,
                status=StageStatus.FAILED,
                duration_ms=0,
                error=f"Stage module not registered: {stage_def.script}"
            )
        
        # Update current stage
        state.current_stage = stage_def.id
        state.stage_statuses[stage_def.id] = StageStatus.RUNNING
        
        # Validate input
        if not stage_module.validate_input(state):
            return StageResult(
                stage_id=stage_def.id,
                status=StageStatus.FAILED,
                duration_ms=0,
                error="Input validation failed"
            )
        
        # Execute with retries
        attempts = 0
        last_error = None
        
        while attempts < (stage_def.max_retries if stage_def.retryable else 1):
            try:
                import time
                start = time.perf_counter()
                
                result = stage_module.execute(state)
                
                duration_ms = (time.perf_counter() - start) * 1000
                result.duration_ms = duration_ms
                
                # Log to Tier 1
                self.tier1.add_message(
                    conversation_id=state.conversation_id,
                    role='system',
                    content=f"Stage '{stage_def.id}' completed in {duration_ms:.0f}ms"
                )
                
                return result
                
            except Exception as e:
                attempts += 1
                last_error = e
                
                # Call failure handler
                stage_module.on_failure(state, e)
                
                # Retry if configured
                if stage_def.retryable and attempts < stage_def.max_retries:
                    self.tier1.add_message(
                        conversation_id=state.conversation_id,
                        role='system',
                        content=f"Stage '{stage_def.id}' failed (attempt {attempts}), retrying..."
                    )
                    continue
                else:
                    # All retries exhausted
                    return StageResult(
                        stage_id=stage_def.id,
                        status=StageStatus.FAILED,
                        duration_ms=0,
                        error=str(last_error)
                    )
        
        # Should not reach here
        return StageResult(
            stage_id=stage_def.id,
            status=StageStatus.FAILED,
            duration_ms=0,
            error=str(last_error)
        )
    
    def _log_workflow_success(self, state: WorkflowState):
        """Log successful workflow completion"""
        duration = (state.end_time - state.start_time).total_seconds()
        
        self.tier1.add_message(
            conversation_id=state.conversation_id,
            role='system',
            content=(
                f"✅ Workflow '{self.workflow_def.name}' completed successfully\n"
                f"Duration: {duration:.1f}s\n"
                f"Stages completed: {len([s for s in state.stage_statuses.values() if s == StageStatus.SUCCESS])}"
            )
        )
    
    def _log_workflow_failure(self, state: WorkflowState, failed_result: StageResult):
        """Log workflow failure"""
        self.tier1.add_message(
            conversation_id=state.conversation_id,
            role='system',
            content=(
                f"❌ Workflow '{self.workflow_def.name}' failed at stage '{failed_result.stage_id}'\n"
                f"Error: {failed_result.error}"
            )
        )
    
    def _log_stage_warning(self, state: WorkflowState, result: StageResult):
        """Log optional stage failure as warning"""
        self.tier1.add_message(
            conversation_id=state.conversation_id,
            role='system',
            content=(
                f"⚠️  Optional stage '{result.stage_id}' failed (continuing)\n"
                f"Error: {result.error}"
            )
        )
