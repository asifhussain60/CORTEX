"""
Health Metrics Collector for CORTEX

This module implements health metrics tracking for validation and orchestration
performance.

Components:
- HealthMetrics: Singleton for metrics collection
- MetricEntry: Individual metric data point
- MetricSummary: Aggregated metrics with statistics
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from collections import defaultdict
import statistics
import logging


class MetricType(Enum):
    """Types of metrics tracked"""
    VALIDATION_SUCCESS = "validation_success"
    VALIDATION_FAILURE = "validation_failure"
    SEMANTIC_ACCURACY = "semantic_accuracy"
    ORCHESTRATOR_EXECUTION = "orchestrator_execution"
    MCP_TOOL_CALL = "mcp_tool_call"
    RULE_EVALUATION = "rule_evaluation"


@dataclass
class MetricEntry:
    """Individual metric entry"""
    timestamp: datetime
    metric_type: MetricType
    component: str  # e.g., "InputValidator", "RuleEvaluator"
    value: float  # 0.0-1.0 for rates, milliseconds for times
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_type": self.metric_type.value,
            "component": self.component,
            "value": self.value,
            "metadata": self.metadata
        }


@dataclass
class MetricSummary:
    """Summary statistics for a metric"""
    metric_type: MetricType
    component: str
    count: int
    mean: float
    min: float
    max: float
    median: float
    std_dev: float
    period_start: datetime
    period_end: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metric_type": self.metric_type.value,
            "component": self.component,
            "count": self.count,
            "mean": self.mean,
            "min": self.min,
            "max": self.max,
            "median": self.median,
            "std_dev": self.std_dev,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat()
        }


class HealthMetrics:
    """
    Singleton metrics collector.
    
    Implements:
    - AC-METRICS-001: Validation success rate tracking
    - AC-METRICS-002: Semantic accuracy tracking
    """
    
    _instance = None
    _lock = None

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize HealthMetrics"""
        if self._initialized:
            return
        
        self.logger = logging.getLogger(__name__)
        self._metrics: List[MetricEntry] = []
        self._retention_hours = 24
        self._initialized = True

    @classmethod
    def instance(cls) -> "HealthMetrics":
        """Get singleton instance"""
        return cls()

    # AC-METRICS-001: Validation Success Rate Tracking
    
    def record_validation_success(
        self,
        component: str = "InputValidator",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a successful validation.
        
        Args:
            component: Component performing validation
            metadata: Optional metadata about validation
        """
        entry = MetricEntry(
            timestamp=datetime.now(),
            metric_type=MetricType.VALIDATION_SUCCESS,
            component=component,
            value=1.0,
            metadata=metadata or {}
        )
        self._metrics.append(entry)
        self.logger.debug(f"Validation success recorded: {component}")

    def record_validation_failure(
        self,
        component: str = "InputValidator",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a failed validation.
        
        Args:
            component: Component performing validation
            metadata: Optional metadata about validation failure
        """
        entry = MetricEntry(
            timestamp=datetime.now(),
            metric_type=MetricType.VALIDATION_FAILURE,
            component=component,
            value=0.0,
            metadata=metadata or {}
        )
        self._metrics.append(entry)
        self.logger.debug(f"Validation failure recorded: {component}")

    def get_validation_success_rate(
        self,
        component: Optional[str] = None,
        hours: int = 1
    ) -> float:
        """
        Get validation success rate.
        
        AC-METRICS-001: Input validation success rate tracking
        
        Args:
            component: Optional component filter
            hours: Time window in hours
        
        Returns:
            Success rate as percentage (0.0-100.0)
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        validations = [
            m for m in self._metrics
            if m.timestamp >= cutoff_time
            and m.metric_type in [MetricType.VALIDATION_SUCCESS, MetricType.VALIDATION_FAILURE]
        ]
        
        if component:
            validations = [m for m in validations if m.component == component]
        
        if not validations:
            return 0.0
        
        successes = sum(1 for m in validations if m.metric_type == MetricType.VALIDATION_SUCCESS)
        success_rate = (successes / len(validations)) * 100.0
        
        return success_rate

    # AC-METRICS-002: Semantic Accuracy Tracking
    
    def record_semantic_accuracy(
        self,
        accuracy_score: float,
        component: str = "InputValidator",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record semantic validation accuracy.
        
        AC-METRICS-002: Semantic validation accuracy tracking
        
        Args:
            accuracy_score: Accuracy as 0.0-1.0
            component: Component performing validation
            metadata: Optional metadata
        """
        if not (0.0 <= accuracy_score <= 1.0):
            raise ValueError("accuracy_score must be between 0.0 and 1.0")
        
        entry = MetricEntry(
            timestamp=datetime.now(),
            metric_type=MetricType.SEMANTIC_ACCURACY,
            component=component,
            value=accuracy_score,
            metadata=metadata or {}
        )
        self._metrics.append(entry)
        self.logger.debug(
            f"Semantic accuracy recorded: {component} = {accuracy_score:.2%}"
        )

    def get_semantic_accuracy(
        self,
        component: Optional[str] = None,
        hours: int = 1
    ) -> Optional[float]:
        """
        Get semantic validation accuracy.
        
        Returns mean accuracy over time window.
        
        Args:
            component: Optional component filter
            hours: Time window in hours
        
        Returns:
            Mean accuracy as 0.0-1.0, or None if no data
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        accuracies = [
            m.value for m in self._metrics
            if m.timestamp >= cutoff_time
            and m.metric_type == MetricType.SEMANTIC_ACCURACY
        ]
        
        if component:
            accuracies = [
                m.value for m in self._metrics
                if m.timestamp >= cutoff_time
                and m.metric_type == MetricType.SEMANTIC_ACCURACY
                and m.component == component
            ]
        
        if not accuracies:
            return None
        
        return statistics.mean(accuracies)

    # AC-METRICS-003: Cross-reference Success Rate
    
    def record_cross_reference_check(
        self,
        success: bool,
        component: str = "InputValidator",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record cross-reference validation result.
        
        AC-METRICS-003: Cross-reference success rate tracking
        
        Args:
            success: Whether cross-reference was valid
            component: Component performing check
            metadata: Optional metadata
        """
        entry = MetricEntry(
            timestamp=datetime.now(),
            metric_type=MetricType.VALIDATION_SUCCESS if success else MetricType.VALIDATION_FAILURE,
            component=f"{component}_cross_ref",
            value=1.0 if success else 0.0,
            metadata=metadata or {}
        )
        self._metrics.append(entry)

    def get_cross_reference_success_rate(
        self,
        hours: int = 1
    ) -> float:
        """
        Get cross-reference validation success rate.
        
        Args:
            hours: Time window in hours
        
        Returns:
            Success rate as percentage (0.0-100.0)
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        checks = [
            m for m in self._metrics
            if m.timestamp >= cutoff_time
            and "cross_ref" in m.component
        ]
        
        if not checks:
            return 0.0
        
        successes = sum(1 for m in checks if m.value == 1.0)
        success_rate = (successes / len(checks)) * 100.0
        
        return success_rate

    # AC-METRICS-004: Phase Alignment Enforcement Rate
    
    def record_phase_alignment_check(
        self,
        aligned: bool,
        phase: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record phase alignment check result.
        
        AC-METRICS-004: Phase alignment enforcement rate tracking
        
        Args:
            aligned: Whether request aligned with current phase
            phase: Phase being checked
            metadata: Optional metadata
        """
        entry = MetricEntry(
            timestamp=datetime.now(),
            metric_type=MetricType.VALIDATION_SUCCESS if aligned else MetricType.VALIDATION_FAILURE,
            component="PhaseAlignmentValidator",
            value=1.0 if aligned else 0.0,
            metadata={"phase": phase, **(metadata or {})}
        )
        self._metrics.append(entry)

    def get_phase_alignment_rate(
        self,
        hours: int = 1
    ) -> float:
        """
        Get phase alignment enforcement rate.
        
        Args:
            hours: Time window in hours
        
        Returns:
            Alignment rate as percentage (0.0-100.0)
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        checks = [
            m for m in self._metrics
            if m.timestamp >= cutoff_time
            and m.component == "PhaseAlignmentValidator"
        ]
        
        if not checks:
            return 0.0
        
        aligned = sum(1 for m in checks if m.value == 1.0)
        alignment_rate = (aligned / len(checks)) * 100.0
        
        return alignment_rate

    # AC-METRICS-005: Anomaly Detection Alerts
    
    def detect_anomalies(
        self,
        metric_type: Optional[MetricType] = None,
        threshold_std_dev: float = 2.0,
        hours: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in metrics.
        
        AC-METRICS-005: Anomaly detection alerts
        
        Uses standard deviation from mean to identify outliers.
        
        Args:
            metric_type: Optional metric type filter
            threshold_std_dev: Z-score threshold (default 2.0 = ~95% confidence)
            hours: Time window in hours
        
        Returns:
            List of anomalies detected
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter metrics
        metrics_to_check = [
            m for m in self._metrics
            if m.timestamp >= cutoff_time
        ]
        
        if metric_type:
            metrics_to_check = [
                m for m in metrics_to_check
                if m.metric_type == metric_type
            ]
        
        # Group by component and metric type
        grouped: Dict[tuple, List[float]] = defaultdict(list)
        for m in metrics_to_check:
            key = (m.component, m.metric_type)
            grouped[key].append(m.value)
        
        # Find anomalies
        anomalies = []
        for (component, mtype), values in grouped.items():
            if len(values) < 3:
                continue  # Need at least 3 points
            
            try:
                mean = statistics.mean(values)
                std_dev = statistics.stdev(values)
                
                if std_dev == 0:
                    continue  # No variation
                
                # Find outliers
                for i, value in enumerate(values):
                    z_score = abs((value - mean) / std_dev)
                    if z_score > threshold_std_dev:
                        anomalies.append({
                            "component": component,
                            "metric_type": mtype.value,
                            "value": value,
                            "mean": mean,
                            "std_dev": std_dev,
                            "z_score": z_score,
                            "severity": "high" if z_score > 3.0 else "medium"
                        })
            except Exception as e:
                self.logger.warning(f"Error detecting anomalies: {str(e)}")
        
        return anomalies

    def get_metric_summary(
        self,
        metric_type: MetricType,
        component: Optional[str] = None,
        hours: int = 1
    ) -> Optional[MetricSummary]:
        """
        Get summary statistics for a metric.
        
        Args:
            metric_type: Type of metric
            component: Optional component filter
            hours: Time window in hours
        
        Returns:
            MetricSummary or None if no data
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        metrics = [
            m for m in self._metrics
            if m.timestamp >= cutoff_time
            and m.metric_type == metric_type
        ]
        
        if component:
            metrics = [m for m in metrics if m.component == component]
        
        if not metrics:
            return None
        
        values = [m.value for m in metrics]
        
        return MetricSummary(
            metric_type=metric_type,
            component=component or "all",
            count=len(metrics),
            mean=statistics.mean(values),
            min=min(values),
            max=max(values),
            median=statistics.median(values),
            std_dev=statistics.stdev(values) if len(values) > 1 else 0.0,
            period_start=cutoff_time,
            period_end=datetime.now()
        )

    def clear_old_metrics(self, hours: int = None) -> int:
        """
        Clear metrics older than retention period.
        
        Args:
            hours: Optional custom retention hours (default uses _retention_hours)
        
        Returns:
            Number of metrics removed
        """
        if hours is None:
            hours = self._retention_hours
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        original_count = len(self._metrics)
        self._metrics = [m for m in self._metrics if m.timestamp >= cutoff_time]
        removed = original_count - len(self._metrics)
        
        if removed > 0:
            self.logger.info(f"Removed {removed} old metrics")
        
        return removed
        return removed

    def reset_metrics(self) -> None:
        """Clear all metrics"""
        self._metrics.clear()
        self.logger.info("All metrics cleared")

    def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Get all metrics as dictionaries"""
        return [m.to_dict() for m in self._metrics]

    def get_metrics_count(self) -> int:
        """Get total number of metrics stored"""
        return len(self._metrics)
