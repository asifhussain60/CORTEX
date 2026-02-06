"""
Context Metrics Collector - Prometheus metrics for context optimization.

Authority: ENH-046 (Context Synthesis Gateway)
Version: 1.0
Date: 2026-02-06

Tracks context consumption efficiency to prevent GitHub Copilot token exhaustion.
Critical governance metric for AUDIT mode P1 checks.

CORE Governance:
- CORE-008: TDD (tests before implementation)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)


# =============================================================================
# Prometheus Metrics
# =============================================================================

# Context size tracking
context_size_before = Histogram(
    'cortex_context_size_before_bytes',
    'Context size before synthesis (bytes)',
    buckets=[1000, 5000, 10000, 20000, 50000, 100000, 200000, 500000]
)

context_size_after = Histogram(
    'cortex_context_size_after_bytes',
    'Context size after synthesis (bytes)',
    buckets=[1000, 5000, 10000, 20000, 50000, 100000]
)

# Compression metrics
compression_ratio = Gauge(
    'cortex_context_compression_ratio',
    'Context compression ratio (0.0-1.0, higher is better)'
)

synthesis_time_ms = Histogram(
    'cortex_context_synthesis_time_ms',
    'Time to synthesize context (milliseconds)',
    buckets=[10, 25, 50, 100, 250, 500, 1000]
)

# Cache metrics
cache_hit_rate = Gauge(
    'cortex_context_cache_hit_rate',
    'Context cache hit rate (percentage)'
)

# Copilot interaction tracking
copilot_summarization_count = Counter(
    'cortex_copilot_summarization_total',
    'Total number of "Summarized conversation history" events',
    ['session_id']
)

copilot_reference_count = Counter(
    'cortex_copilot_reference_total',
    'Total number of file references loaded',
    ['session_id', 'reference_type']
)

# Token budget compliance
token_budget_violations = Counter(
    'cortex_token_budget_violations_total',
    'Total token budget violations',
    ['session_id']
)

token_budget_usage = Histogram(
    'cortex_token_budget_usage_tokens',
    'Token usage per turn',
    buckets=[1000, 5000, 10000, 15000, 20000, 30000, 50000]
)


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class ContextMetrics:
    """Context optimization metrics for a single operation."""
    
    session_id: str
    timestamp: float
    size_before: int  # bytes
    size_after: int  # bytes
    compression_ratio: float  # 0.0-1.0
    synthesis_time_ms: float
    cache_hits: int
    cache_misses: int
    token_budget: int
    tokens_used: int
    references_loaded: int
    reference_types: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Context Metrics Collector
# =============================================================================

class ContextMetricsCollector:
    """
    Collects and publishes context optimization metrics.
    
    Tracks:
    - Context size before/after synthesis
    - Compression ratios
    - Synthesis latency
    - Cache efficiency
    - Copilot summarization frequency
    - Token budget compliance
    
    Integration:
    - Called by ContextSynthesisGateway
    - Metrics exported to Prometheus
    - Dashboard visualization via Grafana
    
    Example:
        >>> collector = ContextMetricsCollector()
        >>> collector.start_synthesis("session-123")
        >>> # ... synthesis happens ...
        >>> collector.end_synthesis(
        ...     session_id="session-123",
        ...     size_before=50000,
        ...     size_after=8000,
        ...     cache_hits=5,
        ...     cache_misses=2
        ... )
    """
    
    def __init__(self):
        """Initialize context metrics collector."""
        self._active_syntheses: Dict[str, float] = {}
        self._session_metrics: Dict[str, List[ContextMetrics]] = {}
    
    def start_synthesis(self, session_id: str) -> None:
        """
        Start tracking a synthesis operation.
        
        Args:
            session_id: Unique session identifier
        """
        self._active_syntheses[session_id] = time.time()
    
    def end_synthesis(
        self,
        session_id: str,
        size_before: int,
        size_after: int,
        cache_hits: int = 0,
        cache_misses: int = 0,
        token_budget: int = 20000,
        tokens_used: int = 0,
        references_loaded: int = 0,
        reference_types: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContextMetrics:
        """
        Complete synthesis tracking and publish metrics.
        
        Args:
            session_id: Unique session identifier
            size_before: Context size before synthesis (bytes)
            size_after: Context size after synthesis (bytes)
            cache_hits: Number of cache hits
            cache_misses: Number of cache misses
            token_budget: Token budget for this turn
            tokens_used: Actual tokens used
            references_loaded: Number of file references loaded
            reference_types: Breakdown by reference type
            metadata: Additional metadata
            
        Returns:
            ContextMetrics object with all tracked metrics
        """
        # Calculate metrics
        start_time = self._active_syntheses.pop(session_id, time.time())
        synthesis_time = (time.time() - start_time) * 1000  # ms
        
        ratio = 0.0
        if size_before > 0:
            ratio = 1.0 - (size_after / size_before)
        
        cache_total = cache_hits + cache_misses
        hit_rate = 0.0
        if cache_total > 0:
            hit_rate = (cache_hits / cache_total) * 100.0
        
        # Create metrics object
        metrics = ContextMetrics(
            session_id=session_id,
            timestamp=time.time(),
            size_before=size_before,
            size_after=size_after,
            compression_ratio=ratio,
            synthesis_time_ms=synthesis_time,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            token_budget=token_budget,
            tokens_used=tokens_used,
            references_loaded=references_loaded,
            reference_types=reference_types or {},
            metadata=metadata or {}
        )
        
        # Store metrics
        if session_id not in self._session_metrics:
            self._session_metrics[session_id] = []
        self._session_metrics[session_id].append(metrics)
        
        # Publish to Prometheus
        context_size_before.observe(size_before)
        context_size_after.observe(size_after)
        compression_ratio.set(ratio)
        synthesis_time_ms.observe(synthesis_time)
        cache_hit_rate.set(hit_rate)
        token_budget_usage.observe(tokens_used)
        
        if tokens_used > token_budget:
            token_budget_violations.labels(session_id=session_id).inc()
        
        # Log for debugging
        logger.info(
            f"Context synthesis complete: {session_id} | "
            f"Before: {size_before}B | After: {size_after}B | "
            f"Compression: {ratio:.1%} | Time: {synthesis_time:.1f}ms | "
            f"Cache: {cache_hits}/{cache_total} ({hit_rate:.1f}%)"
        )
        
        return metrics
    
    def record_copilot_summarization(self, session_id: str) -> None:
        """
        Record a Copilot "Summarized conversation history" event.
        
        This is a critical governance metric - high frequency indicates
        token overconsumption.
        
        Args:
            session_id: Unique session identifier
        """
        copilot_summarization_count.labels(session_id=session_id).inc()
        logger.warning(
            f"Copilot summarization detected in session {session_id} - "
            f"indicates context exhaustion"
        )
    
    def record_reference(
        self,
        session_id: str,
        reference_type: str
    ) -> None:
        """
        Record a file reference loaded.
        
        Args:
            session_id: Unique session identifier
            reference_type: Type of reference (agent, yaml, source, etc.)
        """
        copilot_reference_count.labels(
            session_id=session_id,
            reference_type=reference_type
        ).inc()
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary metrics for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Summary metrics dictionary
        """
        metrics_list = self._session_metrics.get(session_id, [])
        
        if not metrics_list:
            return {
                "session_id": session_id,
                "total_syntheses": 0,
                "error": "No metrics recorded"
            }
        
        # Calculate aggregates
        total_syntheses = len(metrics_list)
        avg_compression = sum(m.compression_ratio for m in metrics_list) / total_syntheses
        avg_time_ms = sum(m.synthesis_time_ms for m in metrics_list) / total_syntheses
        total_cache_hits = sum(m.cache_hits for m in metrics_list)
        total_cache_misses = sum(m.cache_misses for m in metrics_list)
        
        cache_total = total_cache_hits + total_cache_misses
        cache_hit_rate_pct = 0.0
        if cache_total > 0:
            cache_hit_rate_pct = (total_cache_hits / cache_total) * 100.0
        
        return {
            "session_id": session_id,
            "total_syntheses": total_syntheses,
            "avg_compression_ratio": avg_compression,
            "avg_synthesis_time_ms": avg_time_ms,
            "cache_hit_rate": cache_hit_rate_pct,
            "total_references": sum(m.references_loaded for m in metrics_list)
        }


# =============================================================================
# Singleton Instance
# =============================================================================

_collector_instance: Optional[ContextMetricsCollector] = None


def get_context_metrics_collector() -> ContextMetricsCollector:
    """
    Get singleton ContextMetricsCollector instance.
    
    Returns:
        ContextMetricsCollector singleton
    """
    global _collector_instance
    
    if _collector_instance is None:
        _collector_instance = ContextMetricsCollector()
    
    return _collector_instance
