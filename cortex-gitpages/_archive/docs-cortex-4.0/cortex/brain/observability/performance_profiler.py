"""
Performance Profiling and Optimization Module

Identifies bottlenecks and generates optimization recommendations.

AC-OB-002-02: Performance Profiling & Optimization
- Real-time performance profiling
- Bottleneck identification
- Optimization recommendations
- Before/after performance comparison
"""

import logging
import time
import json
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Performance level classification."""
    EXCELLENT = "excellent"  # <50ms
    GOOD = "good"  # 50-100ms
    FAIR = "fair"  # 100-500ms
    POOR = "poor"  # 500-2000ms
    CRITICAL = "critical"  # >2000ms


@dataclass
class PerformanceMetric:
    """Single performance measurement."""
    name: str
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_level(self) -> PerformanceLevel:
        """Classify performance level."""
        if self.duration_ms < 50:
            return PerformanceLevel.EXCELLENT
        elif self.duration_ms < 100:
            return PerformanceLevel.GOOD
        elif self.duration_ms < 500:
            return PerformanceLevel.FAIR
        elif self.duration_ms < 2000:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL


@dataclass
class PerformanceStats:
    """Statistics for a performance metric."""
    name: str
    count: int
    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float
    stddev_ms: float
    p95_ms: float
    p99_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "count": self.count,
            "min_ms": round(self.min_ms, 2),
            "max_ms": round(self.max_ms, 2),
            "mean_ms": round(self.mean_ms, 2),
            "median_ms": round(self.median_ms, 2),
            "stddev_ms": round(self.stddev_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            "p99_ms": round(self.p99_ms, 2)
        }


@dataclass
class Bottleneck:
    """Identified performance bottleneck."""
    operation: str
    avg_duration_ms: float
    occurrences: int
    impact_score: float  # 0-100
    root_cause: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation": self.operation,
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "occurrences": self.occurrences,
            "impact_score": round(self.impact_score, 1),
            "root_cause": self.root_cause
        }


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation."""
    bottleneck: str
    recommendation: str
    expected_improvement_percent: float
    implementation_effort: str  # "low", "medium", "high"
    priority: str  # "critical", "high", "medium", "low"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bottleneck": self.bottleneck,
            "recommendation": self.recommendation,
            "expected_improvement_percent": round(
                self.expected_improvement_percent,
                1
            ),
            "implementation_effort": self.implementation_effort,
            "priority": self.priority
        }


class PerformanceProfiler:
    """Main performance profiling service."""
    
    def __init__(self, retention_hours: float = 24.0):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, List[PerformanceMetric]] = {}
        self.baselines: Dict[str, float] = {}
    
    def record_metric(
        self,
        name: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a performance metric."""
        metric = PerformanceMetric(
            name=name,
            duration_ms=duration_ms,
            metadata=metadata or {}
        )
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(metric)
        
        # Clean old metrics
        self._cleanup_old_metrics(name)
    
    def _cleanup_old_metrics(self, name: str) -> None:
        """Remove metrics older than retention period."""
        cutoff_time = datetime.utcnow() - timedelta(
            hours=self.retention_hours
        )
        self.metrics[name] = [
            m for m in self.metrics[name]
            if m.timestamp > cutoff_time
        ]
    
    def get_stats(self, name: str) -> Optional[PerformanceStats]:
        """Get statistics for a metric."""
        if name not in self.metrics or not self.metrics[name]:
            return None
        
        durations = [m.duration_ms for m in self.metrics[name]]
        durations.sort()
        
        return PerformanceStats(
            name=name,
            count=len(durations),
            min_ms=min(durations),
            max_ms=max(durations),
            mean_ms=statistics.mean(durations),
            median_ms=statistics.median(durations),
            stddev_ms=statistics.stdev(durations) if len(durations) > 1 else 0,
            p95_ms=self._percentile(durations, 95),
            p99_ms=self._percentile(durations, 99)
        )
    
    @staticmethod
    def _percentile(data: List[float], p: float) -> float:
        """Calculate percentile."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (p / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = lower + 1
        
        if upper >= len(sorted_data):
            return sorted_data[lower]
        
        factor = index - lower
        return sorted_data[lower] * (1 - factor) + sorted_data[upper] * factor
    
    def set_baseline(self, name: str, baseline_ms: float) -> None:
        """Set performance baseline for comparison."""
        self.baselines[name] = baseline_ms
        logger.info(f"Baseline set for '{name}': {baseline_ms}ms")
    
    def get_baseline(self, name: str) -> Optional[float]:
        """Get baseline for a metric."""
        return self.baselines.get(name)
    
    def identify_bottlenecks(
        self,
        threshold_ms: Optional[float] = None
    ) -> List[Bottleneck]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        for name, metrics_list in self.metrics.items():
            if not metrics_list:
                continue
            
            durations = [m.duration_ms for m in metrics_list]
            avg_duration = statistics.mean(durations)
            
            # Use provided threshold or auto-detect
            if threshold_ms is None:
                # Bottleneck if > 200ms average
                threshold_ms = 200
            
            if avg_duration > threshold_ms:
                # Calculate impact score (0-100)
                impact_score = min(
                    100,
                    (avg_duration / 5000) * 100  # Normalize to 5000ms
                )
                
                # Determine root cause based on characteristics
                root_cause = self._determine_root_cause(
                    name,
                    avg_duration,
                    durations
                )
                
                bottleneck = Bottleneck(
                    operation=name,
                    avg_duration_ms=avg_duration,
                    occurrences=len(metrics_list),
                    impact_score=impact_score,
                    root_cause=root_cause
                )
                bottlenecks.append(bottleneck)
        
        # Sort by impact score
        bottlenecks.sort(
            key=lambda x: x.impact_score,
            reverse=True
        )
        
        return bottlenecks
    
    @staticmethod
    def _determine_root_cause(
        name: str,
        avg_duration: float,
        durations: List[float]
    ) -> str:
        """Determine likely root cause of performance issue."""
        # High variance suggests intermittent issues
        if len(durations) > 1:
            stddev = statistics.stdev(durations)
            if stddev > avg_duration * 0.5:
                return "High variance - possible resource contention or I/O"
        
        # Consistently high suggests inherent slowness
        if avg_duration > 1000:
            return "Operation inherently slow - requires optimization"
        
        # Check if database-related
        if "query" in name.lower() or "db" in name.lower():
            return "Database operation - consider indexing or query optimization"
        
        # Check if network-related
        if "http" in name.lower() or "api" in name.lower() or \
           "request" in name.lower():
            return "Network operation - consider caching or connection pooling"
        
        return "Requires investigation - monitor trends"
    
    def generate_recommendations(
        self,
        bottlenecks: Optional[List[Bottleneck]] = None
    ) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations."""
        if bottlenecks is None:
            bottlenecks = self.identify_bottlenecks()
        
        recommendations = []
        
        for bottleneck in bottlenecks:
            # Generate recommendations based on operation type and root cause
            recs = self._get_recommendations_for_bottleneck(bottleneck)
            recommendations.extend(recs)
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(
            key=lambda x: (priority_order.get(x.priority, 4), -x.expected_improvement_percent)
        )
        
        return recommendations
    
    @staticmethod
    def _get_recommendations_for_bottleneck(
        bottleneck: Bottleneck
    ) -> List[OptimizationRecommendation]:
        """Get specific recommendations for a bottleneck."""
        recommendations = []
        
        # Database-related
        if "query" in bottleneck.operation.lower():
            recommendations.append(
                OptimizationRecommendation(
                    bottleneck=bottleneck.operation,
                    recommendation="Add database indexes for frequently queried columns",
                    expected_improvement_percent=60,
                    implementation_effort="low",
                    priority="high" if bottleneck.avg_duration_ms > 500 else "medium"
                )
            )
            recommendations.append(
                OptimizationRecommendation(
                    bottleneck=bottleneck.operation,
                    recommendation="Implement query result caching",
                    expected_improvement_percent=75,
                    implementation_effort="medium",
                    priority="high"
                )
            )
        
        # Network-related
        if "http" in bottleneck.operation.lower() or "api" in bottleneck.operation.lower():
            recommendations.append(
                OptimizationRecommendation(
                    bottleneck=bottleneck.operation,
                    recommendation="Implement HTTP connection pooling",
                    expected_improvement_percent=40,
                    implementation_effort="low",
                    priority="medium"
                )
            )
            recommendations.append(
                OptimizationRecommendation(
                    bottleneck=bottleneck.operation,
                    recommendation="Enable response caching with appropriate TTL",
                    expected_improvement_percent=50,
                    implementation_effort="low",
                    priority="high"
                )
            )
        
        # General recommendations
        if bottleneck.avg_duration_ms > 1000:
            recommendations.append(
                OptimizationRecommendation(
                    bottleneck=bottleneck.operation,
                    recommendation="Profile with detailed instrumentation to identify exact bottleneck",
                    expected_improvement_percent=30,
                    implementation_effort="medium",
                    priority="high"
                )
            )
        
        return recommendations
    
    def get_performance_comparison(
        self,
        metric_name: str
    ) -> Optional[Dict[str, Any]]:
        """Compare current performance to baseline."""
        stats = self.get_stats(metric_name)
        if not stats:
            return None
        
        baseline = self.get_baseline(metric_name)
        if baseline is None:
            return None
        
        improvement_percent = (
            (baseline - stats.mean_ms) / baseline
        ) * 100 if baseline > 0 else 0
        
        return {
            "metric": metric_name,
            "baseline_ms": baseline,
            "current_ms": round(stats.mean_ms, 2),
            "improvement_percent": round(improvement_percent, 1),
            "status": "improved" if improvement_percent > 0 else "degraded",
            "stats": stats.to_dict()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get profiling summary."""
        stats_list = []
        for name in self.metrics:
            stats = self.get_stats(name)
            if stats:
                stats_list.append(stats.to_dict())
        
        bottlenecks = self.identify_bottlenecks()
        recommendations = self.generate_recommendations(bottlenecks)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_tracked": len(self.metrics),
            "total_measurements": sum(len(m) for m in self.metrics.values()),
            "stats": stats_list,
            "bottlenecks": [b.to_dict() for b in bottlenecks],
            "recommendations": [r.to_dict() for r in recommendations[:5]]  # Top 5
        }


# Global profiler instance
_profiler = None


def get_performance_profiler() -> PerformanceProfiler:
    """Get or create global performance profiler."""
    global _profiler
    if _profiler is None:
        _profiler = PerformanceProfiler()
    return _profiler
