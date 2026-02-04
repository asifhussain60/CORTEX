"""
Instrumentation Orchestrator - Coordinate metrics capture and enhancement triggers.

AC-ID: AC-PHASE-20.9-03 - InstrumentationOrchestrator Implementation
Author: Asif Hussain
Created: 2026-02-04

Provides:
- Centralized metrics recording API
- Threshold-based enhancement recommendations
- Evidence-driven tool improvement suggestions
"""

from datetime import datetime
from threading import Lock
from typing import Any, Optional
from uuid import uuid4

import yaml

from cortex.observability.metrics_collector import MetricsCollector, get_metrics_collector
from cortex.observability.metrics_schema import (
    CodeGenMetric,
    DebugMetric,
    EnhancementRecommendation,
    MetricAggregation,
    OrchestratorMetric,
    RecordResult,
    TDDMetric,
)


# Default thresholds for enhancement triggers
DEFAULT_THRESHOLDS = {
    "tdd_cycle_time_p90": 300,  # 5 minutes in seconds
    "debugger_failure_rate": 0.05,  # 5%
    "codegen_customization_rate": 0.10,  # 10%
    "orchestrator_latency_p95": 2000,  # 2 seconds in ms
}

# Singleton instance
_orchestrator_instance: Optional["InstrumentationOrchestrator"] = None
_orchestrator_lock = Lock()


def get_instrumentation_orchestrator() -> "InstrumentationOrchestrator":
    """Get the singleton InstrumentationOrchestrator instance."""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        with _orchestrator_lock:
            if _orchestrator_instance is None:
                _orchestrator_instance = InstrumentationOrchestrator()
                
    return _orchestrator_instance


class InstrumentationOrchestrator:
    """
    Orchestrates metrics capture and generates enhancement recommendations.
    
    Features:
    - Unified API for recording all metric types
    - Threshold-based breach detection
    - Evidence-driven recommendations
    - YAML export for reports
    """
    
    def __init__(
        self,
        collector: Optional[MetricsCollector] = None,
        thresholds: Optional[dict[str, float]] = None,
    ) -> None:
        """
        Initialize InstrumentationOrchestrator.
        
        Args:
            collector: MetricsCollector instance (uses singleton if not provided)
            thresholds: Custom thresholds (merges with defaults)
        """
        self._collector = collector or get_metrics_collector()
        self.thresholds = {**DEFAULT_THRESHOLDS}
        
        if thresholds:
            self.thresholds.update(thresholds)
            
    # -------------------------------------------------------------------------
    # Recording Methods
    # -------------------------------------------------------------------------
    
    def record_tdd_cycle(
        self,
        phase: str,
        orchestrator: str,
        test_file: str,
        duration_ms: int,
        success: bool,
        failure_reason: Optional[str] = None,
        retry_count: int = 0,
    ) -> RecordResult:
        """
        Record a TDD cycle metric.
        
        Args:
            phase: TDD phase (RED, GREEN, REFACTOR)
            orchestrator: Orchestrator name
            test_file: Test file path
            duration_ms: Duration in milliseconds
            success: Whether cycle succeeded
            failure_reason: Optional failure reason
            retry_count: Number of retries
            
        Returns:
            RecordResult with success status
        """
        metric_id = str(uuid4())
        
        try:
            metric = TDDMetric(
                cycle_id=metric_id,
                phase=phase,
                orchestrator=orchestrator,
                test_file=test_file,
                duration_ms=duration_ms,
                success=success,
                failure_reason=failure_reason,
                retry_count=retry_count,
            )
            
            self._collector.record(metric)
            
            return RecordResult(success=True, metric_id=metric_id)
            
        except Exception as e:
            return RecordResult(success=False, message=str(e))
    
    def record_debug_session(
        self,
        orchestrator: str,
        target_file: str,
        duration_ms: int,
        resolved: bool,
        resolution_method: Optional[str] = None,
        steps_taken: int = 0,
    ) -> RecordResult:
        """
        Record a debug session metric.
        
        Args:
            orchestrator: Orchestrator name
            target_file: File being debugged
            duration_ms: Duration in milliseconds
            resolved: Whether issue was resolved
            resolution_method: How it was resolved
            steps_taken: Number of debug steps
            
        Returns:
            RecordResult with success status
        """
        metric_id = str(uuid4())
        
        try:
            metric = DebugMetric(
                session_id=metric_id,
                orchestrator=orchestrator,
                target_file=target_file,
                duration_ms=duration_ms,
                resolved=resolved,
                resolution_method=resolution_method,
                steps_taken=steps_taken,
            )
            
            self._collector.record(metric)
            
            return RecordResult(success=True, metric_id=metric_id)
            
        except Exception as e:
            return RecordResult(success=False, message=str(e))
    
    def record_codegen(
        self,
        template_name: str,
        target_type: str,
        duration_ms: int,
        success: bool,
        customizations_applied: int = 0,
        manual_edits_needed: bool = False,
    ) -> RecordResult:
        """
        Record a code generation metric.
        
        Args:
            template_name: Template used
            target_type: Type of code generated
            duration_ms: Duration in milliseconds
            success: Whether generation succeeded
            customizations_applied: Number of customizations
            manual_edits_needed: Whether manual edits were needed
            
        Returns:
            RecordResult with success status
        """
        metric_id = str(uuid4())
        
        try:
            metric = CodeGenMetric(
                generation_id=metric_id,
                template_name=template_name,
                target_type=target_type,
                duration_ms=duration_ms,
                success=success,
                customizations_applied=customizations_applied,
                manual_edits_needed=manual_edits_needed,
            )
            
            self._collector.record(metric)
            
            return RecordResult(success=True, metric_id=metric_id)
            
        except Exception as e:
            return RecordResult(success=False, message=str(e))
    
    def record_orchestrator_invocation(
        self,
        orchestrator_name: str,
        operation: str,
        duration_ms: int,
        success: bool,
        error_type: Optional[str] = None,
    ) -> RecordResult:
        """
        Record an orchestrator invocation metric.
        
        Args:
            orchestrator_name: Orchestrator name
            operation: Operation performed
            duration_ms: Duration in milliseconds
            success: Whether operation succeeded
            error_type: Error type if failed
            
        Returns:
            RecordResult with success status
        """
        metric_id = str(uuid4())
        
        try:
            metric = OrchestratorMetric(
                invocation_id=metric_id,
                orchestrator_name=orchestrator_name,
                operation=operation,
                duration_ms=duration_ms,
                success=success,
                error_type=error_type,
            )
            
            self._collector.record(metric)
            
            return RecordResult(success=True, metric_id=metric_id)
            
        except Exception as e:
            return RecordResult(success=False, message=str(e))
    
    # -------------------------------------------------------------------------
    # Async Recording Methods
    # -------------------------------------------------------------------------
    
    async def async_record_tdd_cycle(
        self,
        phase: str,
        orchestrator: str,
        test_file: str,
        duration_ms: int,
        success: bool,
        **kwargs: Any,
    ) -> RecordResult:
        """Async version of record_tdd_cycle."""
        return self.record_tdd_cycle(
            phase=phase,
            orchestrator=orchestrator,
            test_file=test_file,
            duration_ms=duration_ms,
            success=success,
            **kwargs,
        )
    
    async def async_check_thresholds(self) -> list[EnhancementRecommendation]:
        """Async version of check_thresholds."""
        return self.check_thresholds()
    
    # -------------------------------------------------------------------------
    # Threshold & Recommendation Methods
    # -------------------------------------------------------------------------
    
    def check_thresholds(self) -> list[EnhancementRecommendation]:
        """
        Check metrics against thresholds and generate recommendations.
        
        Returns:
            List of enhancement recommendations for breached thresholds
        """
        recommendations: list[EnhancementRecommendation] = []
        
        # Check TDD cycle time
        tdd_agg = self._collector.aggregate("tdd")
        if tdd_agg.count >= 10:  # Minimum sample size
            p90_seconds = tdd_agg.p90_duration_ms / 1000
            threshold = self.thresholds["tdd_cycle_time_p90"]
            
            if p90_seconds > threshold:
                recommendations.append(
                    EnhancementRecommendation(
                        priority="P0",
                        enhancement="TDD Orchestrator Acceleration",
                        evidence={
                            "p90_cycle_time": p90_seconds,
                            "threshold": threshold,
                            "sample_size": tdd_agg.count,
                        },
                        effort="M",
                        expected_impact="60% cycle time reduction",
                    )
                )
        
        # Check debugger failure rate
        debug_agg = self._collector.aggregate("debug")
        if debug_agg.count >= 20:  # Minimum sample size
            failure_rate = 1 - debug_agg.success_rate
            threshold = self.thresholds["debugger_failure_rate"]
            
            if failure_rate > threshold:
                recommendations.append(
                    EnhancementRecommendation(
                        priority="P0",
                        enhancement="Debugger Reliability Improvement",
                        evidence={
                            "failure_rate": failure_rate,
                            "threshold": threshold,
                            "sample_size": debug_agg.count,
                        },
                        effort="S",
                        expected_impact="<2% failure rate",
                    )
                )
        
        # Check code gen customization rate
        codegen_metrics = self._collector.get_metrics("codegen", limit=1000)
        if len(codegen_metrics) >= 50:
            customizations = sum(1 for m in codegen_metrics if m.customizations_applied > 0)
            customization_rate = customizations / len(codegen_metrics)
            threshold = self.thresholds["codegen_customization_rate"]
            
            if customization_rate > threshold:
                recommendations.append(
                    EnhancementRecommendation(
                        priority="P1",
                        enhancement="Code Generator Template Expansion",
                        evidence={
                            "customization_rate": customization_rate,
                            "threshold": threshold,
                            "sample_size": len(codegen_metrics),
                        },
                        effort="M",
                        expected_impact="<5% customization rate",
                    )
                )
        
        # Check orchestrator latency
        orch_agg = self._collector.aggregate("orchestrator")
        if orch_agg.count >= 100:
            p95_ms = orch_agg.p90_duration_ms  # Using P90 as proxy for P95
            threshold = self.thresholds["orchestrator_latency_p95"]
            
            if p95_ms > threshold:
                recommendations.append(
                    EnhancementRecommendation(
                        priority="P1",
                        enhancement="Orchestrator Performance Optimization",
                        evidence={
                            "p95_latency_ms": p95_ms,
                            "threshold": threshold,
                            "sample_size": orch_agg.count,
                        },
                        effort="M",
                        expected_impact="<500ms P95 latency",
                    )
                )
        
        return recommendations
    
    def get_enhancement_recommendations(self) -> list[EnhancementRecommendation]:
        """Alias for check_thresholds for API consistency."""
        return self.check_thresholds()
    
    def update_threshold(self, name: str, value: float) -> None:
        """
        Update a threshold value.
        
        Args:
            name: Threshold name
            value: New threshold value
            
        Raises:
            KeyError: If threshold name is invalid
        """
        if name not in self.thresholds:
            raise KeyError(f"Unknown threshold: {name}")
            
        self.thresholds[name] = value
    
    # -------------------------------------------------------------------------
    # Summary & Export Methods
    # -------------------------------------------------------------------------
    
    def get_metrics_summary(self) -> dict[str, dict[str, Any]]:
        """
        Get summary of all metrics.
        
        Returns:
            Dictionary with metric summaries by type
        """
        summary = {}
        
        for metric_type in ["tdd", "debug", "codegen", "orchestrator"]:
            agg = self._collector.aggregate(metric_type)
            summary[metric_type] = {
                "count": agg.count,
                "avg_duration_ms": agg.avg_duration_ms,
                "p90_duration_ms": agg.p90_duration_ms,
                "success_rate": agg.success_rate,
            }
            
        return summary
    
    def export_metrics_report(self, format: str = "yaml") -> str:
        """
        Export metrics report in specified format.
        
        Args:
            format: Output format ("yaml" or "json")
            
        Returns:
            Formatted metrics report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.get_metrics_summary(),
            "thresholds": self.thresholds,
            "recommendations": [
                r.model_dump() for r in self.check_thresholds()
            ],
        }
        
        if format == "yaml":
            return yaml.dump(report, default_flow_style=False)
        else:
            import json
            return json.dumps(report, indent=2, default=str)
    
    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        self._collector.clear()
