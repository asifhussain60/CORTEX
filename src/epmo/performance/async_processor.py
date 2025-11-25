"""
CORTEX 3.0 Async Document Processor
====================================

High-performance asynchronous processing for large-scale documentation generation
with queue management, worker pools, and progress tracking.
"""

import asyncio
import time
import threading
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging
from pathlib import Path
import json


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingMode(Enum):
    """Processing execution modes."""
    THREAD = "thread"
    PROCESS = "process"
    ASYNC = "async"
    HYBRID = "hybrid"


@dataclass
class ProcessingTask:
    """Represents a single processing task."""
    task_id: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: int = 0  # Higher = more important
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress: float = 0.0
    metadata: dict = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate task execution duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def is_finished(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]


@dataclass
class ProcessingStats:
    """Processing performance statistics."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    avg_execution_time: float = 0.0
    max_execution_time: float = 0.0
    min_execution_time: float = 0.0
    throughput_per_second: float = 0.0
    queue_size: int = 0
    active_workers: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate task success rate."""
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks
    
    @property
    def pending_tasks(self) -> int:
        """Calculate pending tasks."""
        return self.total_tasks - self.completed_tasks - self.failed_tasks - self.cancelled_tasks


class AsyncDocumentProcessor:
    """
    High-performance async processor for documentation generation with
    intelligent queue management, worker scaling, and progress tracking.
    """
    
    def __init__(
        self,
        max_workers: int = 8,
        max_queue_size: int = 1000,
        processing_mode: ProcessingMode = ProcessingMode.HYBRID,
        enable_progress_tracking: bool = True,
        stats_update_interval: float = 5.0
    ):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.processing_mode = processing_mode
        self.enable_progress_tracking = enable_progress_tracking
        self.stats_update_interval = stats_update_interval
        
        # Task management
        self._task_queue: asyncio.Queue = None
        self._tasks: Dict[str, ProcessingTask] = {}
        self._task_lock = threading.RLock()
        
        # Worker management
        self._workers: List[asyncio.Task] = []
        self._thread_executor: Optional[ThreadPoolExecutor] = None
        self._process_executor: Optional[ProcessPoolExecutor] = None
        
        # Performance tracking
        self._stats = ProcessingStats()
        self._stats_task: Optional[asyncio.Task] = None
        self._execution_times: List[float] = []
        
        # Event loop management
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._running = False
        
        # Progress callbacks
        self._progress_callbacks: List[Callable] = []
    
    async def start(self) -> None:
        """Start the async processor."""
        if self._running:
            return
        
        self._loop = asyncio.get_event_loop()
        self._task_queue = asyncio.Queue(maxsize=self.max_queue_size)
        
        # Initialize executors based on processing mode
        if self.processing_mode in [ProcessingMode.THREAD, ProcessingMode.HYBRID]:
            self._thread_executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        if self.processing_mode in [ProcessingMode.PROCESS, ProcessingMode.HYBRID]:
            self._process_executor = ProcessPoolExecutor(max_workers=max(2, self.max_workers // 2))
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker_task = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker_task)
        
        # Start statistics tracking
        if self.enable_progress_tracking:
            self._stats_task = asyncio.create_task(self._update_stats())
        
        self._running = True
        logger.info(f"AsyncDocumentProcessor started with {self.max_workers} workers")
    
    async def stop(self) -> None:
        """Stop the async processor gracefully."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel all workers
        for worker in self._workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        
        # Stop stats tracking
        if self._stats_task:
            self._stats_task.cancel()
        
        # Shutdown executors
        if self._thread_executor:
            self._thread_executor.shutdown(wait=True)
        if self._process_executor:
            self._process_executor.shutdown(wait=True)
        
        logger.info("AsyncDocumentProcessor stopped")
    
    async def submit_task(
        self,
        func: Callable,
        *args,
        task_id: Optional[str] = None,
        priority: int = 0,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        metadata: Optional[dict] = None,
        **kwargs
    ) -> str:
        """
        Submit a task for async processing.
        
        Args:
            func: Function to execute
            *args: Function arguments
            task_id: Optional custom task ID
            priority: Task priority (higher = more important)
            timeout: Task timeout in seconds
            max_retries: Maximum retry attempts
            metadata: Additional task metadata
            **kwargs: Function keyword arguments
            
        Returns:
            Task ID for tracking
        """
        if not self._running:
            await self.start()
        
        if task_id is None:
            task_id = f"task-{int(time.time() * 1000000)}"
        
        task = ProcessingTask(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
            metadata=metadata or {}
        )
        
        with self._task_lock:
            self._tasks[task_id] = task
            self._stats.total_tasks += 1
        
        # Add to priority queue
        await self._task_queue.put(task)
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[ProcessingTask]:
        """Get current status of a task."""
        with self._task_lock:
            return self._tasks.get(task_id)
    
    async def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        Wait for task completion and return result.
        
        Args:
            task_id: Task identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            Task result
            
        Raises:
            asyncio.TimeoutError: If timeout exceeded
            RuntimeError: If task failed
        """
        start_time = time.time()
        
        while True:
            task = await self.get_task_status(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            if task.status == TaskStatus.COMPLETED:
                return task.result
            elif task.status == TaskStatus.FAILED:
                raise RuntimeError(f"Task {task_id} failed: {task.error}")
            elif task.status == TaskStatus.CANCELLED:
                raise RuntimeError(f"Task {task_id} was cancelled")
            
            # Check timeout
            if timeout and time.time() - start_time > timeout:
                raise asyncio.TimeoutError(f"Task {task_id} timeout after {timeout}s")
            
            await asyncio.sleep(0.1)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        with self._task_lock:
            task = self._tasks.get(task_id)
            if task and not task.is_finished:
                task.status = TaskStatus.CANCELLED
                task.completed_at = time.time()
                self._stats.cancelled_tasks += 1
                return True
            return False
    
    def get_stats(self) -> ProcessingStats:
        """Get current processing statistics."""
        with self._task_lock:
            self._stats.queue_size = self._task_queue.qsize() if self._task_queue else 0
            self._stats.active_workers = len([w for w in self._workers if not w.done()])
            
            # Calculate execution time statistics
            if self._execution_times:
                self._stats.avg_execution_time = sum(self._execution_times) / len(self._execution_times)
                self._stats.max_execution_time = max(self._execution_times)
                self._stats.min_execution_time = min(self._execution_times)
            
            return self._stats
    
    def add_progress_callback(self, callback: Callable[[ProcessingStats], None]) -> None:
        """Add progress tracking callback."""
        self._progress_callbacks.append(callback)
    
    def remove_progress_callback(self, callback: Callable) -> None:
        """Remove progress tracking callback."""
        if callback in self._progress_callbacks:
            self._progress_callbacks.remove(callback)
    
    async def process_batch(
        self,
        functions: List[Callable],
        batch_size: int = 10,
        timeout: Optional[float] = None
    ) -> List[Any]:
        """
        Process a batch of functions concurrently.
        
        Args:
            functions: List of functions to execute
            batch_size: Number of concurrent tasks
            timeout: Batch timeout in seconds
            
        Returns:
            List of results in original order
        """
        if not functions:
            return []
        
        # Submit all tasks
        task_ids = []
        for i, func in enumerate(functions):
            if callable(func):
                task_id = await self.submit_task(func, task_id=f"batch-{i}")
                task_ids.append(task_id)
            else:
                # Handle (func, args, kwargs) tuples
                if isinstance(func, (tuple, list)) and len(func) >= 1:
                    f = func[0]
                    args = func[1] if len(func) > 1 else ()
                    kwargs = func[2] if len(func) > 2 else {}
                    task_id = await self.submit_task(f, *args, task_id=f"batch-{i}", **kwargs)
                    task_ids.append(task_id)
        
        # Wait for all results
        results = []
        for task_id in task_ids:
            try:
                result = await self.get_task_result(task_id, timeout)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch task {task_id} failed: {e}")
                results.append(None)
        
        return results
    
    async def _worker(self, worker_name: str) -> None:
        """Worker coroutine for processing tasks."""
        logger.info(f"Worker {worker_name} started")
        
        while self._running:
            try:
                # Get next task with timeout
                task = await asyncio.wait_for(
                    self._task_queue.get(),
                    timeout=1.0
                )
                
                await self._execute_task(task)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
        
        logger.info(f"Worker {worker_name} stopped")
    
    async def _execute_task(self, task: ProcessingTask) -> None:
        """Execute a single task with error handling and retries."""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        try:
            # Choose execution method based on processing mode
            if self.processing_mode == ProcessingMode.ASYNC:
                if asyncio.iscoroutinefunction(task.func):
                    result = await task.func(*task.args, **task.kwargs)
                else:
                    result = task.func(*task.args, **task.kwargs)
            
            elif self.processing_mode == ProcessingMode.THREAD:
                result = await self._loop.run_in_executor(
                    self._thread_executor,
                    task.func,
                    *task.args
                )
            
            elif self.processing_mode == ProcessingMode.PROCESS:
                result = await self._loop.run_in_executor(
                    self._process_executor,
                    task.func,
                    *task.args
                )
            
            else:  # HYBRID mode
                # Use async for I/O bound, thread for CPU bound
                if asyncio.iscoroutinefunction(task.func):
                    result = await task.func(*task.args, **task.kwargs)
                else:
                    executor = self._thread_executor
                    result = await self._loop.run_in_executor(
                        executor,
                        task.func,
                        *task.args
                    )
            
            # Task completed successfully
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            with self._task_lock:
                self._stats.completed_tasks += 1
                if task.duration:
                    self._execution_times.append(task.duration)
                    # Keep only recent execution times
                    if len(self._execution_times) > 1000:
                        self._execution_times = self._execution_times[-500:]
        
        except Exception as e:
            # Handle task failure with retry logic
            task.error = str(e)
            
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.started_at = None
                # Re-queue for retry
                await self._task_queue.put(task)
                logger.warning(f"Task {task.task_id} failed, retrying ({task.retry_count}/{task.max_retries})")
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = time.time()
                with self._task_lock:
                    self._stats.failed_tasks += 1
                logger.error(f"Task {task.task_id} failed permanently: {e}")
    
    async def _update_stats(self) -> None:
        """Periodic statistics update and progress callbacks."""
        while self._running:
            try:
                # Calculate throughput
                completed_tasks = self._stats.completed_tasks
                await asyncio.sleep(self.stats_update_interval)
                
                new_completed = self._stats.completed_tasks - completed_tasks
                self._stats.throughput_per_second = new_completed / self.stats_update_interval
                
                # Notify progress callbacks
                current_stats = self.get_stats()
                for callback in self._progress_callbacks:
                    try:
                        callback(current_stats)
                    except Exception as e:
                        logger.warning(f"Progress callback error: {e}")
            
            except Exception as e:
                logger.error(f"Stats update error: {e}")


# Global processor instance
default_processor = AsyncDocumentProcessor()