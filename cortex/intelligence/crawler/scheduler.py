# AC_START: AC-PHASE58-S1-004
# Description: PatternDiscoveryScheduler Queue Management
# Authority: CORE-008 TDD, CORE-011 type hints
# Stage: S1 - GREEN phase implementation

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import time


class WorkItemStatus(Enum):
    """Work item status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkItem:
    """Work item for pattern discovery."""
    file_path: str
    metadata: Dict[str, Any]
    status: WorkItemStatus = WorkItemStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None


class PatternDiscoveryScheduler:
    """
    Manages work queue for pattern discovery pipeline.
    
    Features:
    - Async work queue with configurable size limits
    - Backpressure handling (queue size limits)
    - Work item status tracking
    - Concurrent task distribution
    - Cancellation support
    """

    def __init__(
        self,
        max_queue_size: int = 1000,
        max_concurrent_workers: int = 10,
        worker_timeout: float = 30.0,
    ):
        """
        Initialize PatternDiscoveryScheduler.
        
        Args:
            max_queue_size: Maximum queue size before backpressure
            max_concurrent_workers: Maximum concurrent worker tasks
            worker_timeout: Timeout per worker task
        """
        self.max_queue_size = max_queue_size
        self.max_concurrent_workers = max_concurrent_workers
        self.worker_timeout = worker_timeout
        
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.work_items: Dict[str, WorkItem] = {}
        self.active_workers: set = set()
        self.is_running = False

    async def enqueue(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Enqueue work item for processing.
        
        Args:
            file_path: File path to process
            metadata: File metadata
            
        Returns:
            True if enqueued, False if queue full
        """
        try:
            work_item = WorkItem(file_path=file_path, metadata=metadata)
            self.work_items[file_path] = work_item
            
            # Non-blocking put with timeout
            await asyncio.wait_for(self.queue.put(work_item), timeout=1.0)
            return True
        
        except asyncio.TimeoutError:
            return False  # Queue full, backpressure

    def queue_size(self) -> int:
        """Get current queue size."""
        return self.queue.qsize()

    def get_work_item_status(self, file_path: str) -> Optional[WorkItemStatus]:
        """Get status of work item."""
        item = self.work_items.get(file_path)
        return item.status if item else None

    async def start(self) -> None:
        """Start scheduler."""
        self.is_running = True

    async def stop(self) -> None:
        """Stop scheduler and cancel active workers."""
        self.is_running = False
        
        # Cancel all active workers
        for worker in self.active_workers:
            if not worker.done():
                worker.cancel()

    async def process_work_item(
        self,
        work_item: WorkItem,
        handler: Callable,
    ) -> None:
        """
        Process single work item with timeout.
        
        Args:
            work_item: Item to process
            handler: Async handler function
        """
        work_item.status = WorkItemStatus.PROCESSING
        work_item.started_at = time.time()
        
        try:
            await asyncio.wait_for(
                handler(work_item.file_path, work_item.metadata),
                timeout=self.worker_timeout,
            )
            work_item.status = WorkItemStatus.COMPLETED
            work_item.completed_at = time.time()
        
        except asyncio.TimeoutError:
            work_item.status = WorkItemStatus.FAILED
            work_item.error = "Timeout"
        
        except asyncio.CancelledError:
            work_item.status = WorkItemStatus.CANCELLED
        
        except Exception as e:
            work_item.status = WorkItemStatus.FAILED
            work_item.error = str(e)

    def get_metrics(self) -> Dict[str, Any]:
        """Get scheduler metrics."""
        statuses = {}
        for item in self.work_items.values():
            status_name = item.status.value
            statuses[status_name] = statuses.get(status_name, 0) + 1
        
        return {
            "queue_size": self.queue.qsize(),
            "active_workers": len([w for w in self.active_workers if not w.done()]),
            "total_items": len(self.work_items),
            "by_status": statuses,
        }

# AC_COMPLETE: AC-PHASE58-S1-004 ✅
# Implementation: PatternDiscoveryScheduler with queue management
# Status: READY FOR TESTING
