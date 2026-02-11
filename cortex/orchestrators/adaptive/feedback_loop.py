"""Performance Feedback Loop for continuous optimization.

This module implements a feedback loop that collects execution metrics,
analyzes performance trends, identifies bottlenecks, and generates
optimization recommendations.

AC-PHX-010-04: Feedback mechanisms for:
- Execution metrics collection
- Performance analysis
- Strategy optimization
- Adjustment recommendations

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ExecutionRecord:
    """Record of a single execution."""
    timestamp: datetime
    strategy: str
    duration: float
    success: bool
    resource_usage: Dict[str, float] = field(default_factory=dict)
    phase: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class FeedbackLoop:
    """Collects and analyzes execution metrics for optimization.

    Maintains a feedback loop that:
    - Collects execution metrics
    - Analyzes performance trends
    - Identifies bottlenecks
    - Generates optimization recommendations

    Example:
        >>> loop = FeedbackLoop()
        >>> loop.record_execution({
        ...     "strategy": "FAST",
        ...     "duration": 1.0,
        ...     "success": True
        ... })
        >>> recommendations = loop.get_recommendations()
    """

    def __init__(self, history_window: int = 100) -> None:
        """Initialize feedback loop.

        Args:
            history_window: Number of recent executions to keep
        """
        self._history: List[ExecutionRecord] = []
        self._history_window = history_window
        self._aggregated_metrics: Dict[str, Any] = {}

    def record_execution(self, execution_result: Dict[str, Any]) -> None:
        """Record execution result.

        Args:
            execution_result: Dictionary with execution details
        """
        record = ExecutionRecord(
            timestamp=datetime.now(),
            strategy=execution_result.get("strategy", "UNKNOWN"),
            duration=execution_result.get("duration", 0.0),
            success=execution_result.get("success", True),
            resource_usage=execution_result.get("resource_usage", {}),
            phase=execution_result.get("phase", ""),
            metadata=execution_result.get("metadata", {})
        )

        self._history.append(record)

        # Maintain window size
        if len(self._history) > self._history_window:
            self._history.pop(0)

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics from execution history.

        Returns:
            Metrics dictionary
        """
        if not self._history:
            return {}

        successful = [r for r in self._history if r.success]
        failed = [r for r in self._history if not r.success]

        durations = [r.duration for r in self._history]

        return {
            "total_executions": len(self._history),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(self._history) if self._history else 0,
            "avg_duration": statistics.mean(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "std_duration": statistics.stdev(durations) if len(durations) > 1 else 0,
        }

    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over recent history.

        Returns:
            Trends analysis dictionary
        """
        if len(self._history) < 2:
            return {"trend": "insufficient_data"}

        # Split history into two halves
        mid = len(self._history) // 2
        first_half = self._history[:mid]
        second_half = self._history[mid:]

        # Calculate metrics for each half
        first_avg = statistics.mean([r.duration for r in first_half])
        second_avg = statistics.mean([r.duration for r in second_half])

        # Determine trend
        improvement_pct = ((first_avg - second_avg) / first_avg * 100) if first_avg > 0 else 0

        return {
            "first_half_avg_duration": first_avg,
            "second_half_avg_duration": second_avg,
            "improvement_percent": improvement_pct,
            "trend": "improving" if improvement_pct > 5 else (
                "declining" if improvement_pct < -5 else "stable"
            ),
        }

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations.

        Returns:
            List of recommendation dictionaries
        """
        recommendations: List[Dict[str, Any]] = []

        if not self._history:
            return recommendations

        metrics = self.get_metrics()
        trends = self.analyze_trends()

        # Low success rate
        if metrics.get("success_rate", 0) < 0.95:
            recommendations.append({
                "type": "reliability",
                "priority": "HIGH",
                "description": "Success rate below 95%, consider using THOROUGH strategy",
                "action": "Increase validation level or retry count"
            })

        # High execution time
        if metrics.get("avg_duration", 0) > 5.0:
            recommendations.append({
                "type": "performance",
                "priority": "MEDIUM",
                "description": "Average execution time exceeds 5 seconds",
                "action": "Consider using FAST or BALANCED strategy for non-critical tasks"
            })

        # Declining performance
        if trends.get("trend") == "declining":
            recommendations.append({
                "type": "trend",
                "priority": "MEDIUM",
                "description": "Performance is declining over time",
                "action": "Investigate system bottlenecks or resource constraints"
            })

        # High variance
        if metrics.get("std_duration", 0) > metrics.get("avg_duration", 1) * 0.5:
            recommendations.append({
                "type": "stability",
                "priority": "MEDIUM",
                "description": "High variance in execution times",
                "action": "Stabilize resource allocation or improve strategy selection"
            })

        return recommendations

    def identify_bottlenecks(self) -> Dict[str, Any]:
        """Identify performance bottlenecks.

        Returns:
            Bottleneck analysis dictionary
        """
        if not self._history:
            return {}

        # Group by phase if available
        by_phase: Dict[str, List[ExecutionRecord]] = {}
        for record in self._history:
            if record.phase:
                if record.phase not in by_phase:
                    by_phase[record.phase] = []
                by_phase[record.phase].append(record)

        bottlenecks = {}
        for phase, records in by_phase.items():
            if records:
                durations = [r.duration for r in records]
                avg_duration = statistics.mean(durations)
                if avg_duration > 2.0:  # Threshold
                    bottlenecks[phase] = {
                        "avg_duration": avg_duration,
                        "count": len(records),
                        "severity": "HIGH" if avg_duration > 5 else "MEDIUM"
                    }

        # Check resource usage
        high_cpu = []
        high_memory = []
        for record in self._history:
            if record.resource_usage.get("cpu", 0) > 0.8:
                high_cpu.append(record)
            if record.resource_usage.get("memory", 0) > 0.8:
                high_memory.append(record)

        if high_cpu:
            bottlenecks["cpu_constraint"] = {
                "count": len(high_cpu),
                "percentage": len(high_cpu) / len(self._history) * 100
            }

        if high_memory:
            bottlenecks["memory_constraint"] = {
                "count": len(high_memory),
                "percentage": len(high_memory) / len(self._history) * 100
            }

        return bottlenecks

    def get_strategy_effectiveness(self) -> Dict[str, Any]:
        """Get effectiveness comparison of strategies.

        Returns:
            Strategy effectiveness dictionary
        """
        strategies: Dict[str, List[ExecutionRecord]] = {}

        for record in self._history:
            if record.strategy not in strategies:
                strategies[record.strategy] = []
            strategies[record.strategy].append(record)

        effectiveness = {}
        for strategy, records in strategies.items():
            if records:
                successful = sum(1 for r in records if r.success)
                durations = [r.duration for r in records]

                effectiveness[strategy] = {
                    "count": len(records),
                    "success_rate": successful / len(records),
                    "avg_duration": statistics.mean(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                }

        return effectiveness

    def clear_history(self) -> None:
        """Clear execution history."""
        self._history.clear()
