"""Batch processing — unified pipeline with adapters, filters, transformers.

Components:
    BatchProcessor:     Size + timeout-based batching (canonical, CORE-035)
    BatchTrigger:       Enum for trigger reasons (SIZE, TIMEOUT, NONE)
    BatchResult:        Dataclass for batch processing results
    Pipeline:           Adapter → Filter → Transform → Sink pattern
    Streaming:          Yield-based streaming for large datasets
    ProgressTracker:    ASCII progress bars for batch operations

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
CORE-035: Canonical batch implementation (consolidates 4 duplicates)
"""

from cortex.toolkit.batch.batch_processor import (
    BatchProcessor,
    BatchTrigger,
    BatchResult,
)

__all__ = [
    "BatchProcessor",
    "BatchTrigger",
    "BatchResult",
]
