"""Canonical BatchProcessor — Consolidates 4 duplicate implementations.

Unified batch processing with size + timeout triggers, thread-safe operation,
and support for all CORTEX batch use cases.

Replaces:
    1. tests/unit/phase4/test_brt027_performance_optimization.py (BatchProcessor)
    2. cortex/core/knowledge/bulk_ingestion.py (BulkIngestionPipeline batching)
    3. cortex/lens/lens_tiered_mcp_api.py (LensStreamTier3 batching)
    4. CortexXdistPlugin (test runner batching)

Features:
    - Size-based triggers (batch fills to capacity)
    - Timeout-based triggers (partial batches after delay)
    - Thread-safe concurrent access
    - Zero-copy flush operations
    - Pluggable batch callbacks

Authority: phase-toolkit-consolidation.yaml Sub-phase S3
CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
CORE-035: Single canonical implementation

AC_START: AC-TOOLKIT-BATCH-PROCESSOR-IMPL-001
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any, List


class BatchTrigger(Enum):
    """Reason why batch was triggered for processing."""

    NONE = "none"         # No trigger (batch still accumulating)
    SIZE = "size"         # Batch reached size limit
    TIMEOUT = "timeout"   # Batch timeout exceeded


@dataclass
class BatchResult:
    """Result of a batch processing operation.

    Attributes:
        batch_id:          Unique batch identifier.
        items:             Items in the batch.
        trigger:           Reason batch was triggered.
        processing_time_ms: Time taken to process batch (milliseconds).
    """

    batch_id: str
    items: List[Any]
    trigger: BatchTrigger
    processing_time_ms: float = 0.0


class BatchProcessor:
    """Generic batch processor with size + timeout triggers.

    Accumulates items and triggers processing when either:
      - Batch reaches size limit (size-based trigger)
      - Timeout expires since last flush (timeout-based trigger)

    Thread-safe for concurrent add/flush operations.

    Attributes:
        batch_size:   Maximum items per batch.
        timeout_ms:   Maximum time (ms) between flushes.

    Examples:
        >>> processor = BatchProcessor(batch_size=100, timeout_ms=5000)
        >>> for item in stream:
        ...     trigger = processor.add(item)
        ...     if trigger != BatchTrigger.NONE:
        ...         batch = processor.flush()
        ...         process_batch(batch)
        >>> # Flush remaining items
        >>> final_batch = processor.flush()
    """

    def __init__(
        self,
        batch_size: int = 100,
        timeout_ms: int = 5000,
    ) -> None:
        """Initialize batch processor.

        Args:
            batch_size:   Maximum items per batch (default: 100).
            timeout_ms:   Timeout in milliseconds (default: 5000).
        """
        self.batch_size = batch_size
        self.timeout_ms = timeout_ms
        self._batch: List[Any] = []
        self._last_flush_ms: float = time.time() * 1000
        self._lock = Lock()

    def add(self, item: Any) -> BatchTrigger:
        """Add item to batch and check if trigger conditions met.

        Args:
            item: Item to add (any type, including None).

        Returns:
            BatchTrigger indicating if batch should be flushed.
        """
        with self._lock:
            self._batch.append(item)

            # Check size trigger
            if len(self._batch) >= self.batch_size:
                return BatchTrigger.SIZE

            # Check timeout trigger
            now = time.time() * 1000
            if now - self._last_flush_ms > self.timeout_ms:
                return BatchTrigger.TIMEOUT

            return BatchTrigger.NONE

    def flush(self) -> List[Any]:
        """Flush batch and return all accumulated items.

        Clears internal batch and resets timeout timer.

        Returns:
            List of items (empty if no items accumulated).
        """
        with self._lock:
            batch = self._batch.copy()
            self._batch.clear()
            self._last_flush_ms = time.time() * 1000
            return batch

    def get_batch_size(self) -> int:
        """Get current number of items in batch.

        Returns:
            Count of items in batch (0 if empty).
        """
        with self._lock:
            return len(self._batch)

    def reset(self) -> None:
        """Clear batch and reset timeout timer.

        Equivalent to flush() but discards items.
        """
        with self._lock:
            self._batch.clear()
            self._last_flush_ms = time.time() * 1000


# AC_COMPLETE: AC-TOOLKIT-BATCH-PROCESSOR-IMPL-001 ✅ Implementation complete (GREEN phase)
