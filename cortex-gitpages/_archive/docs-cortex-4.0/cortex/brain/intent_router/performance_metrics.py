"""AC-PHX-007-09: Performance Metrics"""
from typing import Dict, Any
from datetime import datetime

class PerformanceMetrics:
    """Tracks performance metrics for intent router."""
    
    def __init__(self) -> None:
        self.metrics: Dict[str, Any] = {
            "classifications": 0,
            "avg_latency_ms": 0.0,
            "cache_hits": 0,
            "routing_success_rate": 1.0,
            "start_time": datetime.now().isoformat(),
        }
    
    def record_classification(self, latency_ms: float) -> None:
        """Record classification metrics."""
        self.metrics["classifications"] += 1
        current_avg = self.metrics.get("avg_latency_ms", 0.0)
        n = self.metrics["classifications"]
        self.metrics["avg_latency_ms"] = (
            (current_avg * (n - 1) + latency_ms) / n
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.metrics.copy()
