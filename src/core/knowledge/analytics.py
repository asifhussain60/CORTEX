"""Knowledge analytics and reporting."""
from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

@dataclass
class MetricSnapshot:
    """Metrics snapshot."""
    timestamp: datetime
    query_count: int
    avg_response_time: float
    cache_hit_rate: float
    optimization_efficiency: float

class AnalyticsService:
    """Provides analytics and reporting."""

    def __init__(self, backends: Dict[str, Any]):
        """Initialize AnalyticsService."""
        self.backends = backends
        self.metrics: Dict[str, List[MetricSnapshot]] = {b: [] for b in backends}
        self.usage_stats = defaultdict(int)
        self.performance_data: Dict[str, List[float]] = defaultdict(list)

    def record_query(self, backend: str, query_type: str, response_time: float) -> None:
        """Record query execution."""
        self.usage_stats[f"{backend}_{query_type}"] += 1
        self.performance_data[backend].append(response_time)

    def get_usage_metrics(self, backend: str) -> Dict[str, Any]:
        """Get usage metrics for backend."""
        prefix = f"{backend}_"
        total = sum(v for k, v in self.usage_stats.items() if k.startswith(prefix))
        
        return {
            "total_queries": total,
            "query_types": {k.replace(prefix, ""): v for k, v in self.usage_stats.items() if k.startswith(prefix)},
            "timestamp": datetime.now()
        }

    def get_effectiveness_report(self, backend: str) -> Dict[str, Any]:
        """Get effectiveness metrics."""
        times = self.performance_data.get(backend, [])
        if not times:
            return {"avg_response_time": 0, "min_time": 0, "max_time": 0}
        
        return {
            "avg_response_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "query_count": len(times),
            "timestamp": datetime.now()
        }

    def get_optimization_insights(self) -> Dict[str, Any]:
        """Get optimization insights."""
        insights = {}
        
        for backend, times in self.performance_data.items():
            if times:
                avg_time = sum(times) / len(times)
                # Identify slow backends
                if avg_time > 100:
                    insights[f"{backend}_slow"] = f"Avg response: {avg_time:.1f}ms"
                # Identify optimization opportunities
                if len(times) > 100 and avg_time > 50:
                    insights[f"{backend}_opportunity"] = "Consider indexing"
        
        return insights

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report."""
        report = {
            "timestamp": datetime.now(),
            "backends": {}
        }
        
        for backend in self.backends:
            report["backends"][backend] = {
                "usage": self.get_usage_metrics(backend),
                "effectiveness": self.get_effectiveness_report(backend)
            }
        
        report["insights"] = self.get_optimization_insights()
        return report
