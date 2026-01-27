"""Knowledge analytics service for tracking and analyzing query performance."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from statistics import mean, stdev


@dataclass
class MetricSnapshot:
    """Captures point-in-time metrics snapshot.
    
    Attributes:
        backend: Backend identifier.
        query_type: Type of query (select, insert, update, delete, etc.).
        response_time_ms: Response time in milliseconds.
        timestamp: When metric was recorded.
    """
    backend: str = ""
    query_type: str = ""
    response_time_ms: float = 0.0
    timestamp: Optional[str] = None


class AnalyticsService:
    """Service for tracking and analyzing knowledge backend performance.
    
    Maintains statistics on query performance across multiple backends.
    """

    def __init__(self, backends: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """Initialize analytics service with configured backends.
        
        Args:
            backends: Dictionary mapping backend names to backend configurations.
        
        Raises:
            TypeError: If backends is not a dict or None.
        """
        if backends is None:
            backends = {}
        if not isinstance(backends, dict):
            raise TypeError(f"backends must be dict, got {type(backends)}")
        
        self.backends = backends
        self.usage_stats: Dict[str, int] = {}  # backend_querytype -> count
        self.response_times: Dict[str, List[float]] = {}  # backend_querytype -> list of times
        self.performance_data: Dict[str, List[float]] = {}  # backend -> list of times

    def record_query(
        self,
        backend: str,
        query_type: str,
        response_time_ms: float
    ) -> None:
        """Record a query execution metric.
        
        Args:
            backend: Backend name where query executed.
            query_type: Type of query (select, insert, update, delete).
            response_time_ms: Query response time in milliseconds.
        """
        key = f"{backend}_{query_type}"
        
        # Track count
        if key not in self.usage_stats:
            self.usage_stats[key] = 0
        self.usage_stats[key] += 1
        
        # Track response times by query type
        if key not in self.response_times:
            self.response_times[key] = []
        self.response_times[key].append(response_time_ms)
        
        # Track performance data by backend
        if backend not in self.performance_data:
            self.performance_data[backend] = []
        self.performance_data[backend].append(response_time_ms)

    def get_usage_metrics(self, backend: str) -> Dict[str, Any]:
        """Get usage metrics for a backend.
        
        Args:
            backend: Backend name to get metrics for.
        
        Returns:
            Dictionary with:
                - total_queries: Total number of queries
                - query_types: Dictionary of query_type -> count
                - backends_covered: List of backends in results
        """
        total_queries = 0
        query_types: Dict[str, int] = {}
        
        for key, count in self.usage_stats.items():
            if key.startswith(f"{backend}_"):
                query_type = key.replace(f"{backend}_", "", 1)
                query_types[query_type] = count
                total_queries += count
        
        return {
            "total_queries": total_queries,
            "query_types": query_types,
            "backends_covered": [backend]
        }

    def get_effectiveness_report(self, backend: str) -> Dict[str, Any]:
        """Generate effectiveness report for backend performance.
        
        Args:
            backend: Backend name to analyze.
        
        Returns:
            Dictionary with:
                - avg_response_time: Average response time across all queries
                - min_time: Minimum response time
                - max_time: Maximum response time
                - query_count: Total number of queries
                - query_type_stats: Per-query-type statistics
                - recommendation: Performance recommendation
        """
        all_times: List[float] = []
        query_type_stats: Dict[str, Dict[str, float]] = {}
        
        for key, times in self.response_times.items():
            if key.startswith(f"{backend}_"):
                query_type = key.replace(f"{backend}_", "", 1)
                all_times.extend(times)
                query_type_stats[query_type] = {
                    "avg": mean(times),
                    "min": min(times),
                    "max": max(times),
                    "count": len(times)
                }
        
        if not all_times:
            return {
                "avg_response_time": 0.0,
                "min_time": 0.0,
                "max_time": 0.0,
                "query_count": 0,
                "query_type_stats": {},
                "recommendation": "No queries recorded"
            }
        
        avg_time = mean(all_times)
        
        # Determine recommendation based on performance
        if avg_time < 50:
            recommendation = "Excellent performance"
        elif avg_time < 100:
            recommendation = "Good performance"
        elif avg_time < 200:
            recommendation = "Acceptable performance, consider optimization"
        else:
            recommendation = "Poor performance, optimization needed"
        
        return {
            "avg_response_time": avg_time,
            "min_time": min(all_times),
            "max_time": max(all_times),
            "query_count": len(all_times),
            "query_type_stats": query_type_stats,
            "recommendation": recommendation
        }

    def get_optimization_insights(self, backend: Optional[str] = None) -> Dict[str, Any]:
        """Generate optimization insights based on query patterns.
        
        Args:
            backend: Backend name to analyze. If None, analyzes all backends.
        
        Returns:
            Dictionary with:
                - slowest_query_type: Query type with highest avg response time
                - fastest_query_type: Query type with lowest avg response time
                - bottleneck_analysis: Analysis of performance bottlenecks
                - recommendations: List of optimization recommendations
                - opportunity_identified: Whether optimization opportunity exists
        """
        query_stats: Dict[str, Dict[str, float]] = {}
        
        for key, times in self.response_times.items():
            if backend is None or key.startswith(f"{backend}_"):
                query_type = key.split("_", 1)[1] if "_" in key else key
                query_stats[query_type] = {
                    "avg": mean(times),
                    "total": sum(times),
                    "count": len(times)
                }
        
        if not query_stats:
            return {
                "slowest_query_type": None,
                "fastest_query_type": None,
                "bottleneck_analysis": "Insufficient data",
                "recommendations": [],
                "opportunity_identified": False
            }
        
        sorted_stats = sorted(query_stats.items(), key=lambda x: x[1]["avg"])
        fastest_type = sorted_stats[0][0]
        slowest_type = sorted_stats[-1][0]
        slowest_avg = sorted_stats[-1][1]["avg"]
        fastest_avg = sorted_stats[0][1]["avg"]
        
        recommendations = []
        opportunity_identified = False
        
        if slowest_avg > 2 * fastest_avg:
            recommendations.append(
                f"Optimize {slowest_type} queries ({slowest_avg:.1f}ms avg)"
            )
            opportunity_identified = True
        
        # Check for high variance
        for query_type, stats in query_stats.items():
            key = f"{backend}_{query_type}" if backend else query_type
            times = self.response_times.get(key, [])
            if len(times) > 1:
                variance = stdev(times) if len(times) > 1 else 0
                if variance > mean(times) * 0.5:
                    recommendations.append(
                        f"High variance in {query_type} queries: {variance:.1f}ms"
                    )
                    opportunity_identified = True
        
        if not recommendations:
            recommendations.append("Performance is consistent and optimized")
        
        return {
            "slowest_query_type": slowest_type,
            "fastest_query_type": fastest_type,
            "bottleneck_analysis": f"{slowest_type} is {slowest_avg/fastest_avg:.1f}x slower than {fastest_type}" if fastest_avg > 0 else "N/A",
            "recommendations": recommendations,
            "opportunity_identified": opportunity_identified
        }

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report for all backends.
        
        Returns:
            Dictionary with:
                - timestamp: Report generation timestamp
                - backends: Per-backend analysis
                - insights: Overall insights
        """
        import datetime
        
        backends_report = {}
        for backend in self.backends.keys():
            backends_report[backend] = {
                "usage": self.get_usage_metrics(backend),
                "effectiveness": self.get_effectiveness_report(backend),
                "optimization": self.get_optimization_insights(backend)
            }
        
        overall_insights = self.get_optimization_insights()
        
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "backends": backends_report,
            "insights": overall_insights
        }


class KnowledgeAnalytics:
    """High-level knowledge analytics engine with advanced analysis capabilities.
    
    Builds on AnalyticsService to provide domain-specific analytics and insights.
    """

    def __init__(self, backends: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """Initialize knowledge analytics.
        
        Args:
            backends: Dictionary mapping backend names to backend configurations.
        """
        self.analytics_service = AnalyticsService(backends or {})

    def analyze(
        self,
        backend: str,
        analysis_type: str = "effectiveness"
    ) -> Dict[str, Any]:
        """Execute analysis of specified type.
        
        Args:
            backend: Backend to analyze.
            analysis_type: Type of analysis ("usage", "effectiveness", "optimization").
        
        Returns:
            Analysis results dictionary.
        
        Raises:
            ValueError: If analysis_type is not recognized.
        """
        if analysis_type == "usage":
            return self.analytics_service.get_usage_metrics(backend)
        elif analysis_type == "effectiveness":
            return self.analytics_service.get_effectiveness_report(backend)
        elif analysis_type == "optimization":
            return self.analytics_service.get_optimization_insights(backend)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")


__all__ = [
    "MetricSnapshot",
    "AnalyticsService",
    "KnowledgeAnalytics",
]