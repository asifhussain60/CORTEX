"""
OpenTelemetry Metrics Exporter for CORTEX

Implements metrics export functionality for observability.
Supports async export and batching.

AC-NFR-004-01: OpenTelemetry metrics exported
"""

import logging
import json
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
from abc import ABC, abstractmethod
import threading
import queue

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"           # Monotonically increasing
    GAUGE = "gauge"               # Can go up and down
    HISTOGRAM = "histogram"        # Distribution
    SUMMARY = "summary"            # Aggregated statistics


@dataclass
class MetricAttribute:
    """Attribute for a metric."""
    key: str
    value: Any


@dataclass
class MetricData:
    """A single metric data point."""
    name: str
    type: MetricType
    value: Any
    unit: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    attributes: List[MetricAttribute] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "attributes": {attr.key: attr.value for attr in self.attributes}
        }


@dataclass
class MetricBatch:
    """Batch of metrics for export."""
    metrics: List[MetricData] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    batch_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "batch_id": self.batch_id,
            "timestamp": self.timestamp.isoformat(),
            "metrics": [m.to_dict() for m in self.metrics]
        }


class MetricsExporter(ABC):
    """Base class for metrics exporters."""
    
    @abstractmethod
    def export(self, batch: MetricBatch) -> bool:
        """Export a batch of metrics. Returns success."""
        pass
    
    @abstractmethod
    def shutdown(self):
        """Shutdown exporter gracefully."""
        pass


class ConsoleMetricsExporter(MetricsExporter):
    """Exports metrics to console (stdout)."""
    
    def export(self, batch: MetricBatch) -> bool:
        """Export metrics to console."""
        try:
            logger.info(f"Exporting {len(batch.metrics)} metrics to console")
            print(json.dumps(batch.to_dict(), indent=2, default=str))
            return True
        except Exception as e:
            logger.error(f"Failed to export metrics: {str(e)}")
            return False
    
    def shutdown(self):
        """No-op for console exporter."""
        pass


class MemoryMetricsExporter(MetricsExporter):
    """Stores metrics in memory for testing."""
    
    def __init__(self, max_batches: int = 100):
        self.batches: List[MetricBatch] = []
        self.max_batches = max_batches
    
    def export(self, batch: MetricBatch) -> bool:
        """Store batch in memory."""
        try:
            self.batches.append(batch)
            if len(self.batches) > self.max_batches:
                self.batches.pop(0)
            logger.debug(f"Stored batch in memory: {batch.batch_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store metrics: {str(e)}")
            return False
    
    def shutdown(self):
        """Clear memory."""
        self.batches.clear()
    
    def get_batches(self) -> List[MetricBatch]:
        """Get all stored batches."""
        return self.batches.copy()
    
    def get_metrics_count(self) -> int:
        """Get total metrics stored."""
        return sum(len(b.metrics) for b in self.batches)


class TelemetryProvider:
    """
    Manages metric collection and export.
    Supports async batching and multiple exporters.
    """
    
    def __init__(
        self,
        exporters: Optional[List[MetricsExporter]] = None,
        batch_size: int = 10,
        use_async: bool = True
    ):
        self.exporters = exporters or []
        self.batch_size = batch_size
        self.use_async = use_async
        self.metrics_buffer: List[MetricData] = []
        self.metrics_lock = threading.Lock()
        self.batch_queue: queue.Queue = queue.Queue()
        self.running = False
        self.export_thread: Optional[threading.Thread] = None
        
        if use_async:
            self._start_async_export()
    
    def add_exporter(self, exporter: MetricsExporter):
        """Add a metrics exporter."""
        self.exporters.append(exporter)
        logger.info(f"Added exporter: {type(exporter).__name__}")
    
    def record_metric(
        self,
        name: str,
        value: Any,
        metric_type: MetricType = MetricType.GAUGE,
        unit: Optional[str] = None,
        attributes: Optional[List[MetricAttribute]] = None
    ) -> MetricData:
        """Record a metric."""
        metric = MetricData(
            name=name,
            type=metric_type,
            value=value,
            unit=unit,
            attributes=attributes or []
        )
        
        with self.metrics_lock:
            self.metrics_buffer.append(metric)
        
        logger.debug(f"Recorded metric: {name} = {value}")
        
        # Check if batch is ready
        if len(self.metrics_buffer) >= self.batch_size:
            self.flush()
        
        return metric
    
    def flush(self, force: bool = False) -> bool:
        """Flush buffered metrics."""
        with self.metrics_lock:
            if not self.metrics_buffer and not force:
                return True
            
            if not self.metrics_buffer:
                return True
            
            batch = MetricBatch(
                metrics=self.metrics_buffer.copy(),
                batch_id=f"batch-{datetime.utcnow().timestamp()}"
            )
            self.metrics_buffer.clear()
        
        if self.use_async:
            self.batch_queue.put(batch)
        else:
            return self._export_batch(batch)
        
        return True
    
    def _start_async_export(self):
        """Start async export thread."""
        self.running = True
        self.export_thread = threading.Thread(
            target=self._async_export_worker,
            daemon=True
        )
        self.export_thread.start()
        logger.info("Started async metrics exporter")
    
    def _async_export_worker(self):
        """Worker thread for async export."""
        while self.running:
            try:
                batch = self.batch_queue.get(timeout=5.0)
                self._export_batch(batch)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Async export error: {str(e)}")
    
    def _export_batch(self, batch: MetricBatch) -> bool:
        """Export batch to all exporters."""
        success = True
        for exporter in self.exporters:
            try:
                if not exporter.export(batch):
                    success = False
            except Exception as e:
                logger.error(f"Exporter error: {str(e)}")
                success = False
        
        return success
    
    def shutdown(self):
        """Shutdown telemetry provider."""
        # Flush remaining metrics
        self.flush(force=True)
        
        # Stop async export
        if self.use_async:
            self.running = False
            if self.export_thread:
                self.export_thread.join(timeout=5.0)
        
        # Shutdown exporters
        for exporter in self.exporters:
            try:
                exporter.shutdown()
            except Exception as e:
                logger.error(f"Exporter shutdown error: {str(e)}")
        
        logger.info("Telemetry provider shutdown complete")
    
    def get_metrics_count(self) -> int:
        """Get count of buffered metrics."""
        with self.metrics_lock:
            return len(self.metrics_buffer)
    
    def get_exporters(self) -> List[MetricsExporter]:
        """Get list of exporters."""
        return self.exporters.copy()
    
    def is_running(self) -> bool:
        """Check if async export is running."""
        return self.running if self.use_async else True
