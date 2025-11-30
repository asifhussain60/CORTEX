"""
CORTEX Workflow Engine - DAG-based Workflow Orchestration

This module provides a declarative workflow pipeline system that allows
chaining tasks in any order with dependency management, state sharing,
checkpoint/resume, and context injection optimization.

Author: CORTEX Development Team
Date: 2025-11-08
Version: 2.0.0
"""

import json
import time
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Protocol
from collections import defaultdict, deque


class StageStatus(Enum):
    """Status of a workflow stage"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result from executing a workflow stage"""
    stage_id: str
    status: StageStatus
    duration_ms: int
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WorkflowState:
    """Shared state passed between workflow stages"""
    workflow_id: str
    conversation_id: str
    user_request: str
    
    # Context from Tier 1-3 (injected once at start)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Outputs from completed stages
    stage_outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Status of each stage
    stage_statuses: Dict[str, StageStatus] = field(default_factory=dict)
    
    # Execution metadata
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    current_stage: Optional[str] = None
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    def get_stage_output(self, stage_id: str) -> Optional[Dict[str, Any]]:
        """Get output from a specific stage"""
        return self.stage_outputs.get(stage_id)
    
    def set_stage_output(self, stage_id: str, output: Dict[str, Any]) -> None:
        """Set output for a specific stage"""
        self.stage_outputs[stage_id] = output
    
    def set_stage_status(self, stage_id: str, status: StageStatus) -> None:
        """Set status for a specific stage"""
        self.stage_statuses[stage_id] = status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "workflow_id": self.workflow_id,
            "conversation_id": self.conversation_id,
            "user_request": self.user_request,
            "context": self.context,
            "stage_outputs": self.stage_outputs,
            "stage_statuses": {k: v.value for k, v in self.stage_statuses.items()},
            "start_time": self.start_time,
            "end_time": self.end_time,
            "current_stage": self.current_stage,
            "config": self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Create WorkflowState from dictionary"""
        state = cls(
            workflow_id=data["workflow_id"],
            conversation_id=data["conversation_id"],
            user_request=data["user_request"],
            context=data.get("context", {}),
            stage_outputs=data.get("stage_outputs", {}),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            current_stage=data.get("current_stage"),
            config=data.get("config", {})
        )
        
        # Convert stage statuses back to enum
        for stage_id, status_str in data.get("stage_statuses", {}).items():
            state.stage_statuses[stage_id] = StageStatus(status_str)
        
        return state


class WorkflowStage(Protocol):
    """Protocol for workflow stages - defines the interface"""
    
    def execute(self, state: WorkflowState) -> StageResult:
        """Execute the stage with given state"""
        ...
    
    def validate_input(self, state: WorkflowState) -> bool:
        """Validate inputs before execution"""
        ...
    
    def on_failure(self, state: WorkflowState, error: Exception) -> None:
        """Handle stage failure"""
        ...


@dataclass
class StageDefinition:
    """Definition of a workflow stage"""
    id: str
    script: str
    required: bool = True
    depends_on: List[str] = field(default_factory=list)
    retryable: bool = False
    max_retries: int = 0
    timeout_seconds: int = 300
    description: str = ""


@dataclass
class WorkflowDefinition:
    """Definition of a complete workflow"""
    workflow_id: str
    name: str
    description: str
    stages: List[StageDefinition]
    version: str = "1.0.0"
    
    @classmethod
    def from_yaml(cls, file_path: Path) -> "WorkflowDefinition":
        """Load workflow definition from YAML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        stages = [
            StageDefinition(
                id=s["id"],
                script=s["script"],
                required=s.get("required", True),
                depends_on=s.get("depends_on", []),
                retryable=s.get("retryable", False),
                max_retries=s.get("max_retries", 0),
                timeout_seconds=s.get("timeout_seconds", 300),
                description=s.get("description", "")
            )
            for s in data["stages"]
        ]
        
        return cls(
            workflow_id=data["workflow_id"],
            name=data["name"],
            description=data["description"],
            stages=stages,
            version=data.get("version", "1.0.0")
        )
    
    def validate_dag(self) -> List[str]:
        """Validate workflow is a valid DAG (no cycles, all dependencies exist)"""
        errors = []
        
        # Check all dependencies exist
        stage_ids = {s.id for s in self.stages}
        for stage in self.stages:
            for dep in stage.depends_on:
                if dep not in stage_ids:
                    errors.append(f"Stage '{stage.id}' depends on non-existent stage '{dep}'")
        
        # Check for cycles using topological sort
        if not errors:
            try:
                self._topological_sort()
            except ValueError as e:
                errors.append(str(e))
        
        return errors
    
    def _topological_sort(self) -> List[str]:
        """Topological sort of stages (returns execution order)"""
        # Build adjacency list and in-degree count
        graph = defaultdict(list)
        in_degree = {s.id: 0 for s in self.stages}
        
        for stage in self.stages:
            for dep in stage.depends_on:
                graph[dep].append(stage.id)
                in_degree[stage.id] += 1
        
        # Find all stages with no dependencies
        queue = deque([s_id for s_id, deg in in_degree.items() if deg == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # Reduce in-degree for dependent stages
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If not all stages processed, there's a cycle
        if len(result) != len(self.stages):
            raise ValueError("Workflow contains circular dependencies (cycle detected)")
        
        return result
    
    def get_execution_order(self) -> List[str]:
        """Get the order stages should be executed in"""
        return self._topological_sort()


class WorkflowOrchestrator:
    """Orchestrates workflow execution with DAG validation and state management"""
    
    def __init__(
        self,
        workflow_def: WorkflowDefinition,
        context_injector: Optional[Any] = None,
        checkpoint_dir: Optional[Path] = None
    ):
        self.workflow_def = workflow_def
        self.context_injector = context_injector
        self.checkpoint_dir = checkpoint_dir or Path("./workflow_checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Stage registry: stage_id -> stage instance
        self._stages: Dict[str, WorkflowStage] = {}
        
        # Validate workflow DAG
        errors = workflow_def.validate_dag()
        if errors:
            raise ValueError(f"Invalid workflow DAG: {', '.join(errors)}")
        
        # Get execution order
        self.execution_order = workflow_def.get_execution_order()
    
    def register_stage(self, stage_id: str, stage: WorkflowStage) -> None:
        """Register a stage implementation"""
        self._stages[stage_id] = stage
    
    def execute(
        self,
        user_request: str,
        conversation_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> WorkflowState:
        """Execute the complete workflow"""
        # Create initial state
        workflow_id = f"wf-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        state = WorkflowState(
            workflow_id=workflow_id,
            conversation_id=conversation_id,
            user_request=user_request,
            config=config or {},
            start_time=datetime.now().isoformat()
        )
        
        # Inject context once (optimization)
        if self.context_injector:
            state.context = self.context_injector.inject_context(conversation_id)
        
        # Initialize stage statuses
        for stage_def in self.workflow_def.stages:
            state.set_stage_status(stage_def.id, StageStatus.PENDING)
        
        # Execute stages in order
        for stage_id in self.execution_order:
            stage_def = self._get_stage_def(stage_id)
            
            # Check if stage should be skipped
            if not self._should_execute_stage(stage_def, state):
                state.set_stage_status(stage_id, StageStatus.SKIPPED)
                continue
            
            # Execute stage
            state.current_stage = stage_id
            result = self._execute_stage(stage_def, state)
            
            # Save checkpoint after each stage
            self._save_checkpoint(state)
            
            # Handle stage failure
            if result.status == StageStatus.FAILED:
                if stage_def.required:
                    # Required stage failed - abort workflow
                    state.end_time = datetime.now().isoformat()
                    return state
                else:
                    # Optional stage failed - continue
                    continue
        
        # Workflow complete
        state.end_time = datetime.now().isoformat()
        state.current_stage = None
        
        return state
    
    def resume(self, workflow_id: str) -> WorkflowState:
        """Resume a workflow from checkpoint"""
        state = self._load_checkpoint(workflow_id)
        
        # Find next stage to execute
        current_idx = self.execution_order.index(state.current_stage) if state.current_stage else 0
        
        # Execute remaining stages
        for stage_id in self.execution_order[current_idx:]:
            stage_def = self._get_stage_def(stage_id)
            
            # Skip if already completed
            if state.stage_statuses.get(stage_id) == StageStatus.SUCCESS:
                continue
            
            # Execute stage
            state.current_stage = stage_id
            result = self._execute_stage(stage_def, state)
            
            # Save checkpoint
            self._save_checkpoint(state)
            
            # Handle failure
            if result.status == StageStatus.FAILED and stage_def.required:
                state.end_time = datetime.now().isoformat()
                return state
        
        # Workflow complete
        state.end_time = datetime.now().isoformat()
        state.current_stage = None
        
        return state
    
    def _should_execute_stage(self, stage_def: StageDefinition, state: WorkflowState) -> bool:
        """Check if stage should be executed"""
        # Check all dependencies are satisfied
        for dep_id in stage_def.depends_on:
            dep_status = state.stage_statuses.get(dep_id)
            if dep_status != StageStatus.SUCCESS:
                return False
        
        return True
    
    def _execute_stage(self, stage_def: StageDefinition, state: WorkflowState) -> StageResult:
        """Execute a single stage with retry logic"""
        stage = self._stages.get(stage_def.id)
        if not stage:
            error_msg = f"Stage '{stage_def.id}' not registered"
            state.set_stage_status(stage_def.id, StageStatus.FAILED)
            return StageResult(
                stage_id=stage_def.id,
                status=StageStatus.FAILED,
                duration_ms=0,
                error=error_msg
            )
        
        # Validate input
        if not stage.validate_input(state):
            error_msg = f"Stage '{stage_def.id}' input validation failed"
            state.set_stage_status(stage_def.id, StageStatus.FAILED)
            return StageResult(
                stage_id=stage_def.id,
                status=StageStatus.FAILED,
                duration_ms=0,
                error=error_msg
            )
        
        # Execute with retry logic
        attempts = 0
        max_attempts = stage_def.max_retries + 1 if stage_def.retryable else 1
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                state.set_stage_status(stage_def.id, StageStatus.RUNNING)
                
                start_time = time.time()
                result = stage.execute(state)
                duration_ms = int((time.time() - start_time) * 1000)
                
                result.duration_ms = duration_ms
                
                if result.status == StageStatus.SUCCESS:
                    state.set_stage_status(stage_def.id, StageStatus.SUCCESS)
                    state.set_stage_output(stage_def.id, result.output)
                    return result
                
            except Exception as e:
                error_msg = f"Stage '{stage_def.id}' execution failed: {str(e)}"
                
                if attempts < max_attempts:
                    # Retry
                    time.sleep(1 * attempts)  # Exponential backoff
                    continue
                else:
                    # Max retries exceeded
                    stage.on_failure(state, e)
                    state.set_stage_status(stage_def.id, StageStatus.FAILED)
                    return StageResult(
                        stage_id=stage_def.id,
                        status=StageStatus.FAILED,
                        duration_ms=0,
                        error=error_msg
                    )
        
        # Should not reach here
        return StageResult(
            stage_id=stage_def.id,
            status=StageStatus.FAILED,
            duration_ms=0,
            error="Unexpected execution path"
        )
    
    def _get_stage_def(self, stage_id: str) -> StageDefinition:
        """Get stage definition by ID"""
        for stage_def in self.workflow_def.stages:
            if stage_def.id == stage_id:
                return stage_def
        raise ValueError(f"Stage definition not found: {stage_id}")
    
    def _save_checkpoint(self, state: WorkflowState) -> None:
        """Save workflow state to checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"{state.workflow_id}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, indent=2)
    
    def _load_checkpoint(self, workflow_id: str) -> WorkflowState:
        """Load workflow state from checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"{workflow_id}.json"
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint not found: {workflow_id}")
        
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return WorkflowState.from_dict(data)


class BaseWorkflowStage:
    """Base class for workflow stages with default implementations"""
    
    def __init__(self, stage_id: str):
        self.stage_id = stage_id
    
    def execute(self, state: WorkflowState) -> StageResult:
        """Override this in subclasses"""
        raise NotImplementedError(f"Stage '{self.stage_id}' must implement execute()")
    
    def validate_input(self, state: WorkflowState) -> bool:
        """Default: Always valid. Override if needed."""
        return True
    
    def on_failure(self, state: WorkflowState, error: Exception) -> None:
        """Default: Log error. Override if needed."""
        print(f"[WORKFLOW] Stage '{self.stage_id}' failed: {error}")


# Export public API
__all__ = [
    "StageStatus",
    "StageResult",
    "WorkflowState",
    "WorkflowStage",
    "StageDefinition",
    "WorkflowDefinition",
    "WorkflowOrchestrator",
    "BaseWorkflowStage"
]
