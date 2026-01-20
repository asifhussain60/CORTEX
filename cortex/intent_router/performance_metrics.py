"""Performance Metrics - Tracking intent router performance.

Tracks classification latency and throughput metrics.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import time
from typing import Dict, Any, List


class PerformanceMetrics:
    """Track performance metrics.
    
    Records classification latency and computes statistics.
    
    Attributes:
        classifications: Total number of classifications
        latencies: List of classification latencies (ms)
        start_time: Timestamp when metrics tracking started
    """
    
    def __init__(self):
        """Initialize metrics."""
        self.classifications: int = 0
        self.latencies: List[float] = []
        self.start_time: float = time.time()
    
    def record_classification(self, latency_ms: float) -> None:
        """Record a classification.
        
        Args:
            latency_ms: Classification latency in milliseconds
        """
        self.classifications += 1
        self.latencies.append(latency_ms)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics.
        
        Returns:
            Dictionary with classifications, avg_latency_ms, min_latency_ms, max_latency_ms, start_time
        """
        if not self.latencies:
            return {
                "classifications": 0,
                "avg_latency_ms": 0.0,
                "min_latency_ms": 0.0,
                "max_latency_ms": 0.0,
                "start_time": self.start_time,
            }
        
        return {
            "classifications": self.classifications,
            "avg_latency_ms": sum(self.latencies) / len(self.latencies),
            "min_latency_ms": min(self.latencies),
            "max_latency_ms": max(self.latencies),
            "start_time": self.start_time,
        }


__all__ = ["PerformanceMetrics"]
