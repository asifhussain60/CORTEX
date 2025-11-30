"""
CORTEX 3.0 - Base Data Collector
===============================

Foundation class for all CORTEX data collectors.
Provides common interface for real-time metrics collection.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #3 (Week 1)
Effort: 4 hours (collector framework)
Target: Real-time collection with minimal overhead
"""

from typing import Dict, Any, Optional, List, Protocol
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from abc import ABC, abstractmethod
import json
import logging
from pathlib import Path
from enum import Enum


class CollectorStatus(Enum):
    """Collector operational status"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"


class CollectorPriority(Enum):
    """Data collection priority levels"""
    CRITICAL = "critical"      # Essential for operation (response templates, errors)
    HIGH = "high"             # Important for optimization (token usage, performance)
    MEDIUM = "medium"         # Useful for insights (workspace health, trends)
    LOW = "low"               # Nice to have (historical patterns, analytics)


@dataclass
class CollectorMetric:
    """Individual metric collected by a collector"""
    name: str
    value: Any
    timestamp: datetime
    tags: Dict[str, str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass 
class CollectorHealth:
    """Health status of a collector"""
    status: CollectorStatus
    last_collection: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    metrics_collected: int = 0
    collection_rate_per_minute: float = 0.0


class ICollector(Protocol):
    """Protocol defining collector interface"""
    
    def start(self) -> bool:
        """Start data collection"""
        ...
    
    def stop(self) -> bool:
        """Stop data collection"""
        ...
    
    def collect(self) -> List[CollectorMetric]:
        """Collect current metrics"""
        ...
    
    def get_health(self) -> CollectorHealth:
        """Get collector health status"""
        ...


class BaseCollector(ABC):
    """
    Base class for all CORTEX data collectors.
    
    Provides common functionality:
    - Health monitoring
    - Error handling
    - Metric storage
    - Collection timing
    - Status management
    """
    
    def __init__(self, 
                 collector_id: str,
                 name: str,
                 priority: CollectorPriority = CollectorPriority.MEDIUM,
                 collection_interval_seconds: float = 60.0,
                 brain_path: Optional[str] = None):
        self.collector_id = collector_id
        self.name = name
        self.priority = priority
        self.collection_interval = collection_interval_seconds
        self.brain_path = Path(brain_path) if brain_path else None
        
        # State management
        self.status = CollectorStatus.INITIALIZING
        self.last_collection = None
        self.error_count = 0
        self.last_error = None
        self.metrics_collected = 0
        
        # Configuration
        self.enabled = True
        self.auto_start = True
        
        # Setup logging
        self.logger = logging.getLogger(f"cortex.collector.{collector_id}")
        
        # Storage for recent metrics (in-memory cache)
        self._recent_metrics: List[CollectorMetric] = []
        self._max_recent_metrics = 1000
    
    def start(self) -> bool:
        """
        Start the collector.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            if not self.enabled:
                self.logger.info(f"Collector {self.name} is disabled, not starting")
                return False
            
            if self.status == CollectorStatus.ACTIVE:
                self.logger.warning(f"Collector {self.name} is already active")
                return True
            
            # Initialize collector-specific resources
            if not self._initialize():
                self.status = CollectorStatus.ERROR
                return False
            
            self.status = CollectorStatus.ACTIVE
            self.logger.info(f"Collector {self.name} started successfully")
            return True
            
        except Exception as e:
            self._handle_error(f"Failed to start collector: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the collector.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            if self.status == CollectorStatus.STOPPED:
                self.logger.info(f"Collector {self.name} is already stopped")
                return True
            
            # Cleanup collector-specific resources
            self._cleanup()
            
            self.status = CollectorStatus.STOPPED
            self.logger.info(f"Collector {self.name} stopped successfully")
            return True
            
        except Exception as e:
            self._handle_error(f"Failed to stop collector: {e}")
            return False
    
    def collect(self) -> List[CollectorMetric]:
        """
        Collect metrics from the collector.
        
        Returns:
            List[CollectorMetric]: List of collected metrics
        """
        if self.status != CollectorStatus.ACTIVE:
            self.logger.warning(f"Collector {self.name} is not active, skipping collection")
            return []
        
        try:
            # Delegate to collector-specific implementation
            metrics = self._collect_metrics()
            
            # Update collector state
            self.last_collection = datetime.now(timezone.utc)
            self.metrics_collected += len(metrics)
            
            # Store recent metrics
            self._store_recent_metrics(metrics)
            
            # Optionally persist to brain
            if self.brain_path and metrics:
                self._persist_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            self._handle_error(f"Failed to collect metrics: {e}")
            return []
    
    def get_health(self) -> CollectorHealth:
        """Get current health status of the collector"""
        # Calculate collection rate
        collection_rate = 0.0
        if self.last_collection and self.metrics_collected > 0:
            time_running = (datetime.now(timezone.utc) - self.last_collection).total_seconds()
            if time_running > 0:
                collection_rate = (self.metrics_collected / time_running) * 60  # per minute
        
        return CollectorHealth(
            status=self.status,
            last_collection=self.last_collection,
            error_count=self.error_count,
            last_error=self.last_error,
            metrics_collected=self.metrics_collected,
            collection_rate_per_minute=collection_rate
        )
    
    def get_recent_metrics(self, count: int = 100) -> List[CollectorMetric]:
        """Get recent metrics from in-memory cache"""
        return self._recent_metrics[-count:] if self._recent_metrics else []
    
    # Abstract methods that subclasses must implement
    
    @abstractmethod
    def _collect_metrics(self) -> List[CollectorMetric]:
        """
        Collect metrics specific to this collector.
        
        Returns:
            List[CollectorMetric]: Metrics collected
        """
        pass
    
    def _initialize(self) -> bool:
        """
        Initialize collector-specific resources.
        Override in subclasses if needed.
        
        Returns:
            bool: True if initialization successful
        """
        return True
    
    def _cleanup(self) -> None:
        """
        Cleanup collector-specific resources.
        Override in subclasses if needed.
        """
        pass
    
    # Private helper methods
    
    def _handle_error(self, error_message: str) -> None:
        """Handle and log collector errors"""
        self.error_count += 1
        self.last_error = error_message
        self.status = CollectorStatus.ERROR
        self.logger.error(error_message)
    
    def _store_recent_metrics(self, metrics: List[CollectorMetric]) -> None:
        """Store metrics in recent metrics cache"""
        self._recent_metrics.extend(metrics)
        
        # Trim if exceeding max size
        if len(self._recent_metrics) > self._max_recent_metrics:
            excess = len(self._recent_metrics) - self._max_recent_metrics
            self._recent_metrics = self._recent_metrics[excess:]
    
    def _persist_metrics(self, metrics: List[CollectorMetric]) -> None:
        """Persist metrics to CORTEX brain storage"""
        try:
            if not self.brain_path:
                return
            
            # Create metrics directory if it doesn't exist
            metrics_dir = self.brain_path / "metrics-history"
            metrics_dir.mkdir(exist_ok=True)
            
            # Create daily metrics file
            today = datetime.now().strftime("%Y-%m-%d")
            metrics_file = metrics_dir / f"{self.collector_id}-{today}.jsonl"
            
            # Append metrics to file (JSONL format)
            with open(metrics_file, "a") as f:
                for metric in metrics:
                    metric_data = metric.to_dict()
                    f.write(json.dumps(metric_data) + "\n")
                    
        except Exception as e:
            self.logger.warning(f"Failed to persist metrics to brain: {e}")


class CollectorRegistry:
    """Registry for managing multiple collectors"""
    
    def __init__(self):
        self.collectors: Dict[str, BaseCollector] = {}
        self.logger = logging.getLogger("cortex.collector.registry")
    
    def register(self, collector: BaseCollector) -> bool:
        """Register a collector"""
        if collector.collector_id in self.collectors:
            self.logger.warning(f"Collector {collector.collector_id} already registered, overwriting")
        
        self.collectors[collector.collector_id] = collector
        self.logger.info(f"Registered collector: {collector.name}")
        return True
    
    def unregister(self, collector_id: str) -> bool:
        """Unregister a collector"""
        if collector_id not in self.collectors:
            return False
        
        # Stop the collector before removing
        collector = self.collectors[collector_id]
        collector.stop()
        
        del self.collectors[collector_id]
        self.logger.info(f"Unregistered collector: {collector_id}")
        return True
    
    def start_all(self) -> Dict[str, bool]:
        """Start all registered collectors"""
        results = {}
        for collector_id, collector in self.collectors.items():
            results[collector_id] = collector.start()
        return results
    
    def stop_all(self) -> Dict[str, bool]:
        """Stop all registered collectors"""
        results = {}
        for collector_id, collector in self.collectors.items():
            results[collector_id] = collector.stop()
        return results
    
    def collect_all(self) -> Dict[str, List[CollectorMetric]]:
        """Collect metrics from all active collectors"""
        results = {}
        for collector_id, collector in self.collectors.items():
            results[collector_id] = collector.collect()
        return results
    
    def get_health_summary(self) -> Dict[str, CollectorHealth]:
        """Get health status of all collectors"""
        return {
            collector_id: collector.get_health() 
            for collector_id, collector in self.collectors.items()
        }


# Global collector registry instance
collector_registry = CollectorRegistry()