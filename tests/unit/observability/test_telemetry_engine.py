"""AC-PHASE43-023: Telemetry and Observability Engine

Validates metrics collection, aggregation, and health monitoring.

Target: 6/6 tests passing
AC-ID: AC-PHASE43-023
"""

import pytest
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class TelemetryEngine:
    """Collect and analyze system telemetry (Phase 43: AC-PHASE43-023)."""
    
    def __init__(self):
        """Initialize telemetry engine."""
        self.metrics = []
        self.aggregations = {}
    
    def record_metric(self, metric_name: str, value: float, 
                     tags: Optional[Dict[str, str]] = None) -> None:
        """Record a metric."""
        self.metrics.append({
            "name": metric_name,
            "value": value,
            "timestamp": datetime.now(),
            "tags": tags or {},
        })
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate health report."""
        return {
            "total_metrics": len(self.metrics),
            "health_status": self._compute_health(),
            "metric_summary": self._summarize_metrics(),
            "recent_events": self._extract_recent_events(),
            "system_uptime": self._calculate_uptime(),
        }
    
    def _compute_health(self) -> str:
        """Compute system health status."""
        if not self.metrics:
            return "unknown"
        
        # Calculate average metric values
        recent = self.metrics[-20:] if len(self.metrics) > 20 else self.metrics
        
        # Mock health calculation: based on error rates
        error_metrics = [m for m in recent if "error" in m["name"].lower()]
        error_ratio = len(error_metrics) / len(recent) if recent else 0.0
        
        if error_ratio > 0.3:
            return "critical"
        elif error_ratio > 0.15:
            return "warning"
        else:
            return "healthy"
    
    def _summarize_metrics(self) -> Dict[str, Any]:
        """Summarize metrics by type."""
        summary = {}
        
        for metric in self.metrics:
            name = metric["name"]
            if name not in summary:
                summary[name] = {"count": 0, "sum": 0.0, "min": float("inf"), "max": float("-inf")}
            
            summary[name]["count"] += 1
            summary[name]["sum"] += metric["value"]
            summary[name]["min"] = min(summary[name]["min"], metric["value"])
            summary[name]["max"] = max(summary[name]["max"], metric["value"])
        
        # Compute averages
        for name in summary:
            if summary[name]["count"] > 0:
                summary[name]["average"] = summary[name]["sum"] / summary[name]["count"]
        
        return summary
    
    def _extract_recent_events(self) -> List[Dict[str, Any]]:
        """Extract recent significant events."""
        significant = []
        
        for metric in self.metrics[-10:]:
            if metric["value"] > 10.0 or "error" in metric["name"].lower():
                significant.append({
                    "metric": metric["name"],
                    "value": metric["value"],
                    "timestamp": metric["timestamp"].isoformat(),
                })
        
        return significant
    
    def _calculate_uptime(self) -> Dict[str, Any]:
        """Calculate system uptime."""
        if not self.metrics:
            return {"uptime_minutes": 0, "status": "not_started"}
        
        first_metric = self.metrics[0]
        last_metric = self.metrics[-1]
        
        uptime_delta = last_metric["timestamp"] - first_metric["timestamp"]
        uptime_minutes = uptime_delta.total_seconds() / 60.0
        
        return {
            "uptime_minutes": uptime_minutes,
            "status": "running",
            "metric_density": len(self.metrics) / max(1, uptime_minutes),
        }


class TestTelemetryEngine:
    """Tests for telemetry and observability."""
    
    def test_engine_initializes(self):
        """Validate engine initializes."""
        engine = TelemetryEngine()
        assert engine is not None
        assert engine.metrics == []
    
    def test_engine_records_metrics(self):
        """Validate metric recording."""
        engine = TelemetryEngine()
        
        engine.record_metric("request_latency", 45.2, {"service": "api"})
        engine.record_metric("error_count", 2.0, {"service": "api"})
        
        assert len(engine.metrics) == 2
        assert engine.metrics[0]["name"] == "request_latency"
    
    def test_engine_computes_health(self):
        """Validate health computation."""
        engine = TelemetryEngine()
        
        # Record some healthy metrics
        for i in range(10):
            engine.record_metric("request_latency", 50.0 + i)
        
        report = engine.get_health_report()
        
        assert report["health_status"] in ["healthy", "warning", "critical"]
    
    def test_engine_summarizes_metrics(self):
        """Validate metric summarization."""
        engine = TelemetryEngine()
        
        engine.record_metric("latency", 10.0)
        engine.record_metric("latency", 20.0)
        engine.record_metric("latency", 30.0)
        
        report = engine.get_health_report()
        summary = report["metric_summary"]
        
        assert "latency" in summary
        assert summary["latency"]["count"] == 3
        assert summary["latency"]["average"] == 20.0
    
    def test_engine_detects_errors(self):
        """Validate error detection."""
        engine = TelemetryEngine()
        
        # Record error metrics
        for i in range(15):
            engine.record_metric("error_count", 1.0)
        for i in range(5):
            engine.record_metric("request_latency", 50.0)
        
        report = engine.get_health_report()
        
        assert report["health_status"] in ["warning", "critical"]
    
    def test_engine_calculates_uptime(self):
        """Validate uptime calculation."""
        engine = TelemetryEngine()
        
        engine.record_metric("metric1", 100.0)
        engine.record_metric("metric2", 200.0)
        
        report = engine.get_health_report()
        uptime = report["system_uptime"]
        
        assert uptime["status"] == "running"
        assert uptime["uptime_minutes"] >= 0
