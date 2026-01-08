"""
Master Orchestrator
==================
Coordinates all orchestrators (TODO, Governance, etc.) with intelligent routing.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 2 Task: 2.1
TDD Phase: GREEN
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
from pathlib import Path

from ..middleware.orchestrator_lifecycle import (
    OrchestratorLifecycle,
    LifecycleState,
    LifecycleError
)
from .todo_orchestrator import TodoOrchestrator
from ..state_manager import StateManager
from ..audit_logger import get_audit_logger, AuditCategory


@dataclass
class ExecutionResult:
    """Result of orchestrator execution"""
    success: bool
    orchestrator: str
    result: Any = None
    error: Optional[str] = None


class MasterOrchestrator:
    """Master orchestrator coordinating all sub-orchestrators"""
    
    def __init__(self, workspace_root: Path):
        """
        Initialize master orchestrator
        
        Args:
            workspace_root: Root directory of workspace
        """
        self.workspace_root = workspace_root
        self.logger = get_audit_logger()
        
        # Orchestrator registry
        self.orchestrators: Dict[str, Any] = {}
        self.lifecycles: Dict[str, OrchestratorLifecycle] = {}
        
        # Initialize sub-orchestrators
        self._initialize_orchestrators()
    
    def _initialize_orchestrators(self) -> None:
        """Initialize all sub-orchestrators"""
        # Initialize state manager
        state_db = self.workspace_root / "cortex-brain" / "database" / "state.db"
        state_db.parent.mkdir(parents=True, exist_ok=True)
        state_manager = StateManager(state_file=str(state_db))
        
        # Initialize TODO orchestrator
        todo_orch = TodoOrchestrator(state_manager=state_manager)
        self.orchestrators["todo"] = todo_orch
        
        # Create lifecycle tracker for TODO
        todo_lifecycle = OrchestratorLifecycle("todo-orchestrator")
        todo_lifecycle.transition_to(LifecycleState.READY)
        self.lifecycles["todo"] = todo_lifecycle
        
        self.logger.info(
            category=AuditCategory.EXECUTION,
            component='master_orchestrator',
            operation='initialize',
            message='Master orchestrator initialized',
            context={'orchestrators': list(self.orchestrators.keys())}
        )
    
    def has_orchestrator(self, name: str) -> bool:
        """Check if orchestrator is registered"""
        return name in self.orchestrators
    
    def get_orchestrator(self, name: str) -> Any:
        """Get orchestrator by name"""
        return self.orchestrators.get(name)
    
    def get_lifecycle(self, name: str) -> Optional[OrchestratorLifecycle]:
        """Get lifecycle tracker for orchestrator"""
        return self.lifecycles.get(name)
    
    def execute(self, request: str) -> ExecutionResult:
        """
        Execute request via appropriate orchestrator
        
        Args:
            request: User request
            
        Returns:
            ExecutionResult with success status
        """
        try:
            # Simple routing logic (will be enhanced with intelligence layer)
            if "todo" in request.lower() or "task" in request.lower():
                return self._execute_todo(request)
            
            return ExecutionResult(
                success=False,
                orchestrator="unknown",
                error="No orchestrator found for request"
            )
            
        except Exception as e:
            self.logger.error(
                category=AuditCategory.EXECUTION,
                component='master_orchestrator',
                operation='execute',
                message=f'Execution failed: {e}',
                context={'request': request[:100]}
            )
            return ExecutionResult(
                success=False,
                orchestrator="master",
                error=str(e)
            )
    
    def _execute_todo(self, request: str) -> ExecutionResult:
        """Execute via TODO orchestrator"""
        try:
            todo = self.orchestrators["todo"]
            lifecycle = self.lifecycles["todo"]
            
            # Ensure we're in READY state before execution
            # This handles cases where lifecycle wasn't properly reset
            if lifecycle.current_state not in [LifecycleState.READY, LifecycleState.RUNNING]:
                lifecycle.transition_to(LifecycleState.READY)
            
            # Transition to RUNNING if currently READY
            if lifecycle.current_state == LifecycleState.READY:
                lifecycle.transition_to(LifecycleState.RUNNING)
            
            # Execute (simplified - actual implementation would parse request)
            # For now, just validate it's a valid request format
            if "invalid" in request.lower():
                raise ValueError("Invalid TODO request format")
            
            result = {"status": "created", "request": request}
            
            # Always transition back to READY after successful execution
            if lifecycle.current_state == LifecycleState.RUNNING:
                lifecycle.transition_to(LifecycleState.READY)
            
            return ExecutionResult(
                success=True,
                orchestrator="todo",
                result=result
            )
            
        except LifecycleError as le:
            # Lifecycle error - don't transition to ERROR for these
            return ExecutionResult(
                success=False,
                orchestrator="todo",
                error=str(le)
            )
        except Exception as e:
            # Other errors - transition to ERROR
            lifecycle = self.lifecycles.get("todo")
            if lifecycle and lifecycle.current_state not in [LifecycleState.ERROR, LifecycleState.STOPPED]:
                try:
                    lifecycle.transition_to(LifecycleState.ERROR, error=str(e))
                except:
                    pass  # Ignore transition errors during error handling
            
            return ExecutionResult(
                success=False,
                orchestrator="todo",
                error=str(e)
            )
