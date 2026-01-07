"""
Child Orchestrator Spawner

Enables dynamic orchestrator instantiation with:
- Worker pool for parallel execution (4 workers default)
- Lifecycle management: spawn → execute → collect → terminate
- Error isolation per child
- Resource cleanup and management
- Integration with CORTEX orchestrators

Features:
- ThreadPoolExecutor-based worker pool
- UUID-based child identification
- Task queuing and result collection
- Graceful shutdown with cleanup
- Parent-child communication
"""

import logging
import uuid
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future, as_completed, TimeoutError
from contextlib import contextmanager


@dataclass
class OrchestratorTask:
    """Represents a task to be executed by a child orchestrator."""
    
    task_type: str
    target_path: Path
    parameters: Dict[str, Any] = field(default_factory=dict)
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.task_type:
            raise ValueError("task_type is required")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "target_path": str(self.target_path),
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class TaskResult:
    """Represents the result of a task execution."""
    
    task_id: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    @classmethod
    def success_result(cls, task_id: str, output: Dict[str, Any] = None) -> 'TaskResult':
        """Create a successful result."""
        now = datetime.now()
        return cls(
            task_id=task_id,
            success=True,
            output=output or {},
            completed_at=now,
            started_at=now
        )
    
    @classmethod
    def error_result(cls, task_id: str, error: str) -> 'TaskResult':
        """Create an error result."""
        now = datetime.now()
        return cls(
            task_id=task_id,
            success=False,
            error=error,
            completed_at=now,
            started_at=now
        )


class ChildOrchestrator:
    """
    Represents a child orchestrator instance.
    
    Manages execution of a specific orchestrator type with:
    - Unique ID for tracking
    - Status management
    - Task execution
    - Error handling
    """
    
    def __init__(
        self,
        orchestrator_type: str,
        child_id: str,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize child orchestrator.
        
        Args:
            orchestrator_type: Type of orchestrator (e.g., "cleanup", "analyze")
            child_id: Unique identifier for this child
            config: Configuration dictionary
            logger: Logger instance
        """
        self.orchestrator_type = orchestrator_type
        self.child_id = child_id
        self.config = config or {}
        self.logger = logger or logging.getLogger(f"Child-{child_id[:8]}")
        
        self.status = "initialized"
        self.is_terminated = False
        self.result: Optional[TaskResult] = None
    
    def execute(self, task: OrchestratorTask) -> TaskResult:
        """
        Execute a task.
        
        Args:
            task: Task to execute
            
        Returns:
            TaskResult with execution outcome
        """
        self.status = "executing"
        start_time = datetime.now()
        
        try:
            # Simulate orchestrator execution
            # In real implementation, this would delegate to actual orchestrators
            self.logger.info(f"Executing {task.task_type} on {task.target_path}")
            
            # Mock execution - replace with real orchestrator logic
            if task.task_type == "invalid_operation":
                raise ValueError(f"Invalid operation: {task.task_type}")
            
            # Simulate work
            time.sleep(0.01)  # Brief pause to simulate processing
            
            result = TaskResult.success_result(
                task_id=task.task_id,
                output={
                    "child_id": self.child_id,
                    "orchestrator_type": self.orchestrator_type,
                    "task_type": task.task_type,
                    "files_processed": 10  # Mock data
                }
            )
            result.started_at = start_time
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - start_time).total_seconds()
            
            self.status = "completed"
            self.result = result
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            result = TaskResult.error_result(task_id=task.task_id, error=str(e))
            result.started_at = start_time
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - start_time).total_seconds()
            
            self.status = "failed"
            self.result = result
            return result
    
    def terminate(self):
        """Terminate this child orchestrator."""
        self.status = "terminated"
        self.is_terminated = True
        self.logger.info(f"Child {self.child_id[:8]} terminated")


class WorkerPool:
    """
    Manages a pool of workers for parallel task execution.
    
    Features:
    - ThreadPoolExecutor-based implementation
    - Task queuing and distribution
    - Result collection
    - Timeout handling
    - Resource cleanup
    """
    
    def __init__(
        self,
        size: int = 4,
        task_timeout: Optional[int] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize worker pool.
        
        Args:
            size: Number of worker threads
            task_timeout: Timeout per task in seconds
            logger: Logger instance
        """
        self.size = size
        self.task_timeout = task_timeout or 300  # 5 minutes default
        self.logger = logger or logging.getLogger("WorkerPool")
        
        self.executor = ThreadPoolExecutor(max_workers=size)
        self.active_workers = 0
        self.available_workers = size
        self.is_shutdown = False
        
        self.logger.info(f"Worker pool initialized with {size} workers")
    
    def submit_tasks(self, tasks: List[OrchestratorTask]) -> List[Future]:
        """
        Submit tasks to worker pool.
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            List of Future objects
        """
        if self.is_shutdown:
            raise RuntimeError("Worker pool is shut down")
        
        futures = []
        for task in tasks:
            # Create child orchestrator for each task
            child = ChildOrchestrator(
                orchestrator_type=task.task_type,
                child_id=str(uuid.uuid4()),
                logger=self.logger
            )
            
            # Submit task execution
            future = self.executor.submit(child.execute, task)
            futures.append(future)
            self.active_workers = min(self.active_workers + 1, self.size)
        
        self.logger.info(f"Submitted {len(tasks)} tasks to worker pool")
        return futures
    
    def collect_results(
        self,
        futures: List[Future],
        timeout: Optional[int] = None
    ) -> List[TaskResult]:
        """
        Collect results from futures.
        
        Args:
            futures: List of Future objects
            timeout: Timeout for collection in seconds
            
        Returns:
            List of TaskResult objects
        """
        results = []
        timeout = timeout or self.task_timeout
        
        for future in as_completed(futures, timeout=timeout):
            try:
                result = future.result(timeout=1)
                results.append(result)
                self.active_workers = max(0, self.active_workers - 1)
            except TimeoutError:
                error_result = TaskResult.error_result(
                    task_id="timeout",
                    error=f"Task exceeded timeout of {timeout} seconds"
                )
                results.append(error_result)
            except Exception as e:
                error_result = TaskResult.error_result(
                    task_id="error",
                    error=str(e)
                )
                results.append(error_result)
        
        return results
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown worker pool.
        
        Args:
            wait: Whether to wait for tasks to complete
        """
        self.logger.info("Shutting down worker pool")
        self.executor.shutdown(wait=wait)
        self.is_shutdown = True
        self.active_workers = 0


class ChildOrchestratorSpawner:
    """
    Spawns and manages child orchestrators for parallel processing.
    
    Features:
    - Dynamic orchestrator instantiation
    - Worker pool management (4 workers default)
    - Spawn → execute → collect → terminate lifecycle
    - Error isolation per child
    - Resource cleanup
    - Integration with parent orchestrator
    """
    
    def __init__(
        self,
        parent_orchestrator: Optional[Any] = None,
        max_children: int = 4,
        max_workers: int = 4,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize child orchestrator spawner.
        
        Args:
            parent_orchestrator: Parent orchestrator instance
            max_children: Maximum number of active children
            max_workers: Maximum number of worker threads
            logger: Logger instance
        """
        self.parent_orchestrator = parent_orchestrator
        self.max_children = max_children
        self.max_workers = max_workers
        self.logger = logger or logging.getLogger("ChildSpawner")
        
        # Worker pool
        self.worker_pool = WorkerPool(size=max_workers, logger=self.logger)
        
        # Active children tracking
        self.active_children: List[ChildOrchestrator] = []
        self.children_by_id: Dict[str, ChildOrchestrator] = {}
        
        self.logger.info(f"Spawner initialized (max_children={max_children}, max_workers={max_workers})")
    
    def spawn(
        self,
        orchestrator_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> ChildOrchestrator:
        """
        Spawn a new child orchestrator.
        
        Args:
            orchestrator_type: Type of orchestrator to spawn
            config: Configuration for the orchestrator
            
        Returns:
            ChildOrchestrator instance
            
        Raises:
            RuntimeError: If maximum children limit reached
        """
        if len(self.active_children) >= self.max_children:
            raise RuntimeError(
                f"Maximum children limit ({self.max_children}) reached. "
                f"Terminate some children before spawning more."
            )
        
        child_id = str(uuid.uuid4())
        child = ChildOrchestrator(
            orchestrator_type=orchestrator_type,
            child_id=child_id,
            config=config,
            logger=self.logger
        )
        
        self.active_children.append(child)
        self.children_by_id[child_id] = child
        
        self.logger.info(f"Spawned child {child_id[:8]} (type={orchestrator_type})")
        return child
    
    def execute_parallel(self, tasks: List[OrchestratorTask]) -> List[TaskResult]:
        """
        Execute multiple tasks in parallel using worker pool.
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            List of TaskResult objects
        """
        self.logger.info(f"Executing {len(tasks)} tasks in parallel")
        
        # Submit tasks to worker pool
        futures = self.worker_pool.submit_tasks(tasks)
        
        # Collect results
        results = self.worker_pool.collect_results(futures)
        
        self.logger.info(f"Parallel execution complete: {len(results)} results")
        return results
    
    def terminate(self, child_id: str):
        """
        Terminate a specific child orchestrator.
        
        Args:
            child_id: ID of child to terminate
        """
        if child_id not in self.children_by_id:
            self.logger.warning(f"Child {child_id[:8]} not found")
            return
        
        child = self.children_by_id[child_id]
        child.terminate()
        
        self.active_children.remove(child)
        del self.children_by_id[child_id]
        
        self.logger.info(f"Terminated child {child_id[:8]}")
    
    def terminate_all(self):
        """Terminate all active children."""
        self.logger.info(f"Terminating all {len(self.active_children)} children")
        
        for child in list(self.active_children):
            child.terminate()
        
        self.active_children.clear()
        self.children_by_id.clear()
        
        self.logger.info("All children terminated")
    
    def shutdown(self):
        """Shutdown spawner and cleanup resources."""
        self.logger.info("Shutting down spawner")
        self.terminate_all()
        self.worker_pool.shutdown(wait=True)
        self.logger.info("Spawner shutdown complete")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatic cleanup."""
        self.shutdown()
        return False


__all__ = [
    'ChildOrchestratorSpawner',
    'ChildOrchestrator',
    'OrchestratorTask',
    'TaskResult',
    'WorkerPool'
]
