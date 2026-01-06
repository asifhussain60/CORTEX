"""
Execution Engine - Lifecycle management and metrics collection.

Manages orchestrator execution lifecycle, error handling, and performance metrics.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout


class ExecutionStatus(str, Enum):
    """Execution status values."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ExecutionContext:
    """Context for execution."""
    execution_id: str
    plan_id: str
    phase_number: int
    started_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "plan_id": self.plan_id,
            "phase_number": self.phase_number,
            "started_at": self.started_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ExecutionResult:
    """Result of execution."""
    execution_id: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: datetime
    output: Any
    error: Optional[str] = None
    task_results: List[Any] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "output": self.output,
            "error": self.error,
            "duration": (self.completed_at - self.started_at).total_seconds()
        }


class ExecutionError(Exception):
    """Raised when execution fails."""
    pass


class ExecutionEngine:
    """
    Manages execution lifecycle and metrics.
    
    Provides:
    - Phase execution management
    - Task execution with timeouts
    - Error handling and recovery
    - Execution metrics collection
    - Active execution tracking
    """
    
    def __init__(self, metrics_dir: Optional[str] = None):
        """
        Initialize ExecutionEngine.
        
        Args:
            metrics_dir: Directory for metrics storage
        """
        self.logger = logging.getLogger("cortex.orchestrators.execution_engine")
        self.metrics_dir = Path(metrics_dir) if metrics_dir else None
        self.active_executions: Dict[str, ExecutionContext] = {}
        self.completed_executions: List[ExecutionResult] = []
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        self.logger.info("ExecutionEngine initialized")
    
    def execute_phase(
        self, 
        context: ExecutionContext, 
        phase_func: Callable
    ) -> ExecutionResult:
        """
        Execute a phase.
        
        Args:
            context: Execution context
            phase_func: Phase function to execute
            
        Returns:
            Execution result
        """
        self.logger.info(f"Executing phase {context.phase_number} for {context.plan_id}")
        
        with self._lock:
            self.active_executions[context.execution_id] = context
        
        started_at = datetime.now()
        
        try:
            # Execute phase function
            output = phase_func()
            
            completed_at = datetime.now()
            result = ExecutionResult(
                execution_id=context.execution_id,
                status=ExecutionStatus.SUCCESS,
                started_at=started_at,
                completed_at=completed_at,
                output=output
            )
            
            self.logger.info(f"Phase {context.phase_number} completed successfully")
            
        except Exception as e:
            completed_at = datetime.now()
            result = ExecutionResult(
                execution_id=context.execution_id,
                status=ExecutionStatus.FAILED,
                started_at=started_at,
                completed_at=completed_at,
                output=None,
                error=str(e)
            )
            
            self.logger.error(f"Phase {context.phase_number} failed: {e}")
        
        finally:
            with self._lock:
                if context.execution_id in self.active_executions:
                    del self.active_executions[context.execution_id]
                self.completed_executions.append(result)
        
        return result
    
    def execute_task(
        self, 
        task_id: str, 
        task_func: Callable,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute a single task.
        
        Args:
            task_id: Task identifier
            task_func: Task function to execute
            timeout: Optional timeout in seconds
            
        Returns:
            Execution result
        """
        self.logger.debug(f"Executing task: {task_id}")
        
        started_at = datetime.now()
        
        try:
            if timeout:
                # Execute with timeout
                future = self._executor.submit(task_func)
                try:
                    output = future.result(timeout=timeout)
                    status = ExecutionStatus.SUCCESS
                    error = None
                except FutureTimeout:
                    future.cancel()
                    output = None
                    status = ExecutionStatus.TIMEOUT
                    error = f"Task timed out after {timeout}s"
            else:
                # Execute without timeout
                output = task_func()
                status = ExecutionStatus.SUCCESS
                error = None
            
        except Exception as e:
            output = None
            status = ExecutionStatus.FAILED
            error = str(e)
            self.logger.error(f"Task {task_id} failed: {e}")
        
        completed_at = datetime.now()
        
        return ExecutionResult(
            execution_id=task_id,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            output=output,
            error=error
        )
    
    def record_metrics(
        self, 
        context: ExecutionContext, 
        result: ExecutionResult
    ) -> bool:
        """
        Record execution metrics.
        
        Args:
            context: Execution context
            result: Execution result
            
        Returns:
            True if metrics recorded successfully
        """
        if not self.metrics_dir:
            return False
        
        try:
            self.metrics_dir.mkdir(parents=True, exist_ok=True)
            
            metrics_file = self.metrics_dir / f"{context.execution_id}.json"
            
            metrics = {
                "context": context.to_dict(),
                "result": result.to_dict()
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            self.logger.debug(f"Recorded metrics for {context.execution_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record metrics: {e}")
            return False
    
    def get_execution_status(self, execution_id: str) -> Optional[ExecutionContext]:
        """
        Get status of active execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Execution context if active, None otherwise
        """
        with self._lock:
            return self.active_executions.get(execution_id)
    
    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel active execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            True if cancelled successfully
        """
        with self._lock:
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
                self.logger.info(f"Cancelled execution: {execution_id}")
                return True
        return False
    
    def list_active_executions(self) -> List[ExecutionContext]:
        """
        List all active executions.
        
        Returns:
            List of active execution contexts
        """
        with self._lock:
            return list(self.active_executions.values())
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get execution metrics.
        
        Returns:
            Dictionary of metrics
        """
        with self._lock:
            return {
                "total_executions": len(self.completed_executions),
                "active_executions": len(self.active_executions),
                "completed_executions": len(self.completed_executions),
                "success_rate": self._calculate_success_rate()
            }
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate of completed executions."""
        if not self.completed_executions:
            return 0.0
        
        successful = sum(
            1 for r in self.completed_executions 
            if r.status == ExecutionStatus.SUCCESS
        )
        return successful / len(self.completed_executions)


class PhaseExecutor:
    """Executes orchestrator phases with task management."""
    
    def __init__(self):
        """Initialize PhaseExecutor."""
        self.logger = logging.getLogger("cortex.orchestrators.phase_executor")
    
    def execute(self, tasks: List[Callable]) -> ExecutionResult:
        """
        Execute phase with multiple tasks.
        
        Args:
            tasks: List of task functions
            
        Returns:
            Execution result
        """
        started_at = datetime.now()
        task_results = []
        
        try:
            for i, task in enumerate(tasks):
                self.logger.debug(f"Executing task {i+1}/{len(tasks)}")
                result = task()
                task_results.append(result)
            
            status = ExecutionStatus.SUCCESS
            error = None
            
        except Exception as e:
            status = ExecutionStatus.FAILED
            error = str(e)
            self.logger.error(f"Phase execution failed: {e}")
        
        completed_at = datetime.now()
        
        return ExecutionResult(
            execution_id="phase",
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            output=task_results,
            error=error,
            task_results=task_results
        )


class TaskExecutor:
    """Executes individual tasks."""
    
    def __init__(self):
        """Initialize TaskExecutor."""
        self.logger = logging.getLogger("cortex.orchestrators.task_executor")
    
    def execute(self, task: Callable) -> ExecutionResult:
        """
        Execute single task.
        
        Args:
            task: Task function
            
        Returns:
            Execution result
        """
        started_at = datetime.now()
        
        try:
            output = task()
            status = ExecutionStatus.SUCCESS
            error = None
            
        except Exception as e:
            output = None
            status = ExecutionStatus.FAILED
            error = str(e)
            self.logger.error(f"Task execution failed: {e}")
        
        completed_at = datetime.now()
        
        return ExecutionResult(
            execution_id="task",
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            output=output,
            error=error
        )
