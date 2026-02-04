"""
Metrics Collector - Low-level metrics capture with sampling support.

AC-ID: AC-PHASE-20.9-02 - Metrics Collector Implementation
Author: Asif Hussain
Created: 2026-02-04

Provides:
- Time-series storage (in-memory + periodic flush)
- Configurable sampling rate
- Context-aware metrics (operation, orchestrator, phase)
"""

import random
from collections import defaultdict
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Callable, Optional, Protocol, Union

from cortex.observability.metrics_schema import (
    CodeGenMetric,
    DebugMetric,
    MetricAggregation,
    OrchestratorMetric,
    TDDMetric,
)


# Type alias for all metric types
MetricType = Union[TDDMetric, DebugMetric, CodeGenMetric, OrchestratorMetric]


class StorageBackend(Protocol):
    """Protocol for storage backends."""
    
    def write(self, metrics: list[dict[str, Any]]) -> None:
        """Write metrics to storage."""
        ...
    
    def read(self, metric_type: str, limit: int) -> list[dict[str, Any]]:
        """Read metrics from storage."""
        ...


class InMemoryStorage:
    """Simple in-memory storage backend."""
    
    def __init__(self) -> None:
        self._data: list[dict[str, Any]] = []
        
    def write(self, metrics: list[dict[str, Any]]) -> None:
        """Write metrics to memory."""
        self._data.extend(metrics)
        
    def read(self, metric_type: str, limit: int) -> list[dict[str, Any]]:
        """Read metrics from memory."""
        filtered = [m for m in self._data if m.get("_type") == metric_type]
        return filtered[:limit]


# Singleton instance
_collector_instance: Optional["MetricsCollector"] = None
_collector_lock = Lock()


def get_metrics_collector() -> "MetricsCollector":
    """Get the singleton MetricsCollector instance."""
    global _collector_instance
    
    if _collector_instance is None:
        with _collector_lock:
            if _collector_instance is None:
                _collector_instance = MetricsCollector()
                
    return _collector_instance


class MetricsCollector:
    """
    Collects and manages development metrics with sampling support.
    
    Features:
    - Configurable sampling rate (default 1.0 = record all)
    - In-memory storage with periodic flush
    - Time-based queries and aggregations
    - Thread-safe operations
    """
    
    def __init__(
        self,
        sampling_rate: float = 1.0,
        retention_hours: int = 168,  # 7 days
        storage_backend: Optional[StorageBackend] = None,
    ) -> None:
        """
        Initialize MetricsCollector.
        
        Args:
            sampling_rate: Rate of metrics to record (0.0-1.0)
            retention_hours: Hours to retain metrics
            storage_backend: Optional external storage backend
        """
        self.sampling_rate = min(1.0, max(0.0, sampling_rate))
        self.retention_hours = retention_hours
        self._storage = storage_backend or InMemoryStorage()
        
        # In-memory buffers by metric type
        self._buffers: dict[str, list[MetricType]] = defaultdict(list)
        self._lock = Lock()
        
    def record(self, metric: MetricType) -> bool:
        """
        Record a metric with sampling.
        
        Args:
            metric: Metric to record
            
        Returns:
            True if recorded, False if sampled out
        """
        # Apply sampling
        if random.random() > self.sampling_rate:
            return False
            
        metric_type = self._get_metric_type(metric)
        
        with self._lock:
            self._buffers[metric_type].append(metric)
            
        return True
    
    def get_metrics(
        self,
        metric_type: str,
        limit: int = 100,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        orchestrator: Optional[str] = None,
    ) -> list[MetricType]:
        """
        Get metrics by type with optional filtering.
        
        Args:
            metric_type: Type of metrics to retrieve
            limit: Maximum number of metrics
            since: Start of time range
            until: End of time range
            orchestrator: Filter by orchestrator name
            
        Returns:
            List of metrics matching criteria
        """
        with self._lock:
            metrics = list(self._buffers.get(metric_type, []))
            
        # Apply time filter
        if since:
            metrics = [m for m in metrics if m.timestamp >= since]
        if until:
            metrics = [m for m in metrics if m.timestamp <= until]
            
        # Apply orchestrator filter
        if orchestrator:
            metrics = [
                m for m in metrics
                if hasattr(m, "orchestrator") and m.orchestrator == orchestrator
            ]
            
        return metrics[:limit]
    
    def aggregate(self, metric_type: str) -> MetricAggregation:
        """
        Aggregate metrics by type.
        
        Args:
            metric_type: Type of metrics to aggregate
            
        Returns:
            Aggregated metrics
        """
        metrics = self.get_metrics(metric_type, limit=10000)
        
        if metric_type == "tdd":
            return MetricAggregation.from_tdd_metrics(metrics)  # type: ignore
        elif metric_type == "debug":
            return MetricAggregation.from_debug_metrics(metrics)  # type: ignore
        else:
            # Generic aggregation
            return MetricAggregation(
                metric_type=metric_type,
                count=len(metrics),
            )
    
    def set_storage_backend(self, backend: StorageBackend) -> None:
        """Set external storage backend."""
        self._storage = backend
        
    def flush(self) -> int:
        """
        Flush buffered metrics to storage.
        
        Returns:
            Number of metrics flushed
        """
        total_flushed = 0
        
        with self._lock:
            for metric_type, metrics in self._buffers.items():
                if metrics:
                    metric_dicts = [
                        {**m.model_dump(), "_type": metric_type}
                        for m in metrics
                    ]
                    self._storage.write(metric_dicts)
                    total_flushed += len(metrics)
                    
        return total_flushed
    
    def cleanup_old_metrics(self) -> int:
        """
        Remove metrics older than retention period.
        
        Returns:
            Number of metrics removed
        """
        cutoff = self._get_retention_cutoff()
        total_removed = 0
        
        with self._lock:
            for metric_type in self._buffers:
                original_count = len(self._buffers[metric_type])
                self._buffers[metric_type] = [
                    m for m in self._buffers[metric_type]
                    if m.timestamp >= cutoff
                ]
                total_removed += original_count - len(self._buffers[metric_type])
                
        return total_removed
    
    def clear(self) -> None:
        """Clear all metrics from buffers."""
        with self._lock:
            self._buffers.clear()
            
    def _get_metric_type(self, metric: MetricType) -> str:
        """Get metric type string from metric object."""
        if isinstance(metric, TDDMetric):
            return "tdd"
        elif isinstance(metric, DebugMetric):
            return "debug"
        elif isinstance(metric, CodeGenMetric):
            return "codegen"
        elif isinstance(metric, OrchestratorMetric):
            return "orchestrator"
        else:
            return "unknown"
            
    def _get_retention_cutoff(self) -> datetime:
        """Get retention cutoff timestamp."""
        return datetime.now() - timedelta(hours=self.retention_hours)
