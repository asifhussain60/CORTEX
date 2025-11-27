"""Performance Behavior - Request Performance Monitoring"""
from typing import Callable, Awaitable
import logging
import time
from src.application.common.interfaces import IPipelineBehavior, IRequest
from src.application.common.result import Result

logger = logging.getLogger(__name__)


class PerformanceBehavior(IPipelineBehavior):
    """Pipeline behavior for performance monitoring
    
    This behavior wraps request handlers to:
    - Measure execution time
    - Detect slow operations
    - Log performance metrics
    - Track performance trends
    
    Benefits:
    - Identify performance bottlenecks
    - Monitor system health
    - Alert on degradation
    - Support optimization efforts
    """
    
    def __init__(self, slow_threshold_ms: float = 1000.0):
        """Initialize performance behavior
        
        Args:
            slow_threshold_ms: Threshold in milliseconds for slow operation warning
        """
        self.slow_threshold_ms = slow_threshold_ms
        self.performance_metrics = {}  # Track metrics per request type
        
    async def handle(
        self,
        request: IRequest,
        next_handler: Callable[[IRequest], Awaitable[Result]]
    ) -> Result:
        """Monitor request performance
        
        Args:
            request: The request to monitor
            next_handler: Next handler in pipeline
            
        Returns:
            Result from next handler with performance metrics logged
        """
        request_type = request.__class__.__name__
        
        # Start timing
        start_time = time.perf_counter()
        
        try:
            # Execute handler
            result = await next_handler(request)
            
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Record metrics
            self._record_metrics(request_type, duration_ms, result.is_success)
            
            # Log performance
            self._log_performance(request_type, duration_ms, result.is_success)
            
            # Warn if slow
            if duration_ms > self.slow_threshold_ms:
                logger.warning(
                    f"⚠️ Slow operation detected: {request_type} "
                    f"took {duration_ms:.2f}ms (threshold: {self.slow_threshold_ms}ms)"
                )
            
            return result
            
        except Exception as e:
            # Calculate duration even on error
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Record failed metrics
            self._record_metrics(request_type, duration_ms, False)
            
            logger.error(
                f"❌ Request failed: {request_type} "
                f"(duration: {duration_ms:.2f}ms, error: {e})"
            )
            
            # Re-raise to maintain error handling
            raise
    
    def _record_metrics(self, request_type: str, duration_ms: float, success: bool):
        """Record performance metrics
        
        Args:
            request_type: Type of request
            duration_ms: Duration in milliseconds
            success: Whether request succeeded
        """
        if request_type not in self.performance_metrics:
            self.performance_metrics[request_type] = {
                'count': 0,
                'total_duration_ms': 0.0,
                'min_duration_ms': float('inf'),
                'max_duration_ms': 0.0,
                'success_count': 0,
                'failure_count': 0
            }
        
        metrics = self.performance_metrics[request_type]
        metrics['count'] += 1
        metrics['total_duration_ms'] += duration_ms
        metrics['min_duration_ms'] = min(metrics['min_duration_ms'], duration_ms)
        metrics['max_duration_ms'] = max(metrics['max_duration_ms'], duration_ms)
        
        if success:
            metrics['success_count'] += 1
        else:
            metrics['failure_count'] += 1
    
    def _log_performance(self, request_type: str, duration_ms: float, success: bool):
        """Log performance information
        
        Args:
            request_type: Type of request
            duration_ms: Duration in milliseconds
            success: Whether request succeeded
        """
        status = "✅" if success else "❌"
        
        # Get average duration for comparison
        metrics = self.performance_metrics.get(request_type, {})
        avg_duration = (
            metrics['total_duration_ms'] / metrics['count']
            if metrics.get('count', 0) > 0
            else 0.0
        )
        
        logger.info(
            f"⏱️ {status} {request_type}: {duration_ms:.2f}ms "
            f"(avg: {avg_duration:.2f}ms, "
            f"count: {metrics.get('count', 0)})"
        )
    
    def get_metrics_summary(self) -> dict:
        """Get performance metrics summary
        
        Returns:
            Dictionary with performance metrics for all request types
        """
        summary = {}
        
        for request_type, metrics in self.performance_metrics.items():
            avg_duration = (
                metrics['total_duration_ms'] / metrics['count']
                if metrics['count'] > 0
                else 0.0
            )
            
            success_rate = (
                metrics['success_count'] / metrics['count'] * 100
                if metrics['count'] > 0
                else 0.0
            )
            
            summary[request_type] = {
                'count': metrics['count'],
                'avg_duration_ms': round(avg_duration, 2),
                'min_duration_ms': round(metrics['min_duration_ms'], 2),
                'max_duration_ms': round(metrics['max_duration_ms'], 2),
                'success_rate': round(success_rate, 2),
                'success_count': metrics['success_count'],
                'failure_count': metrics['failure_count']
            }
        
        return summary
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        self.performance_metrics.clear()
        logger.info("Performance metrics reset")
