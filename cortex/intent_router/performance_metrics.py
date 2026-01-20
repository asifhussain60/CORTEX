"""Performance Metrics - Tracks performance of intent routing.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceSnapshot:
    """A snapshot of performance metrics at a point in time."""
    
    timestamp: datetime
    avg_response_time_ms: float
    requests_per_second: float
    error_rate: float
    success_rate: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float


class PerformanceMetrics:
    """Tracks and reports performance metrics for intent routing."""
    
    def __init__(self, window_size: int = 1000):
        """Initialize performance metrics.
        
        Args:
            window_size: Number of recent operations to track
        """
        self.window_size = window_size
        self.response_times: List[float] = []
        self.request_timestamps: List[datetime] = []
        self.error_count = 0
        self.success_count = 0
        self.total_requests = 0
        self.snapshots: List[PerformanceSnapshot] = []
    
    def record_request(
        self,
        response_time_ms: float,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """Record a request.
        
        Args:
            response_time_ms: Response time in milliseconds
            success: Whether the request succeeded
            error: Optional error message
        """
        self.response_times.append(response_time_ms)
        self.request_timestamps.append(datetime.now())
        self.total_requests += 1
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
            if error:
                logger.warning(f"Request error: {error}")
        
        # Keep only recent entries
        if len(self.response_times) > self.window_size:
            self.response_times.pop(0)
            self.request_timestamps.pop(0)
    
    def get_average_response_time(self) -> float:
        """Get average response time.
        
        Returns:
            Average response time in milliseconds
        """
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_requests_per_second(self) -> float:
        """Get current requests per second.
        
        Returns:
            Requests per second
        """
        if len(self.request_timestamps) < 2:
            return 0.0
        
        # Calculate based on recent window
        now = datetime.now()
        recent_window = now - timedelta(seconds=1)
        recent_requests = sum(
            1 for ts in self.request_timestamps 
            if ts > recent_window
        )
        
        return float(recent_requests)
    
    def get_error_rate(self) -> float:
        """Get error rate.
        
        Returns:
            Error rate (0-1)
        """
        if self.total_requests == 0:
            return 0.0
        return self.error_count / self.total_requests
    
    def get_success_rate(self) -> float:
        """Get success rate.
        
        Returns:
            Success rate (0-1)
        """
        if self.total_requests == 0:
            return 0.0
        return self.success_count / self.total_requests
    
    def get_percentile(self, percentile: float) -> float:
        """Get response time percentile.
        
        Args:
            percentile: Percentile to calculate (e.g., 0.95 for p95)
            
        Returns:
            Response time at the given percentile
        """
        if not self.response_times:
            return 0.0
        
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * percentile)
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    def take_snapshot(self) -> PerformanceSnapshot:
        """Take a snapshot of current metrics.
        
        Returns:
            PerformanceSnapshot with current metrics
        """
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            avg_response_time_ms=self.get_average_response_time(),
            requests_per_second=self.get_requests_per_second(),
            error_rate=self.get_error_rate(),
            success_rate=self.get_success_rate(),
            p50_latency_ms=self.get_percentile(0.50),
            p95_latency_ms=self.get_percentile(0.95),
            p99_latency_ms=self.get_percentile(0.99)
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics.
        
        Returns:
            Dictionary with performance statistics
        """
        return {
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.get_success_rate(),
            "error_rate": self.get_error_rate(),
            "avg_response_time_ms": self.get_average_response_time(),
            "requests_per_second": self.get_requests_per_second(),
            "p50_latency_ms": self.get_percentile(0.50),
            "p95_latency_ms": self.get_percentile(0.95),
            "p99_latency_ms": self.get_percentile(0.99),
            "recent_window_size": len(self.response_times)
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.response_times.clear()
        self.request_timestamps.clear()
        self.error_count = 0
        self.success_count = 0
        self.total_requests = 0
        logger.info("Performance metrics reset")


__all__ = ["PerformanceMetrics", "PerformanceSnapshot"]
