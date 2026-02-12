"""Adaptive Execution Framework

Implements context-aware orchestrator routing and optimization for CORTEX.

Modules:
    execution_context_analyzer: ExecutionContextAnalyzer for task analysis
    routing_engine: OrchestratorRoutingEngine for intelligent orchestrator selection
    execution_modes: ExecutionMode enums and mode handlers
    caching_layer: CachingLayer for result caching with TTL
    performance_profiler: PerformanceProfiler for execution profiling
    unified_adaptive_layer: UnifiedAdaptiveLayer consolidating all adaptive components
"""

from .caching_layer import (
    CacheEntry,
    CachingLayer,
)
from .execution_context_analyzer import (
    ExecutionContext,
    ExecutionContextAnalyzer,
)
from .execution_modes import (
    AdaptiveExecutor,
    ExecutionMode,
    ModeConfiguration,
)
from .performance_profiler import (
    ExecutionMetrics,
    PerformanceProfile,
    PerformanceProfiler,
)
from .routing_engine import (
    OrchestratorRoutingEngine,
    RoutingDecision,
)
from .unified_adaptive_layer import (
    FailoverContext,
    ResourceAllocation,
    StrategyType,
    UnifiedAdaptiveLayer,
)

__all__ = [
    "ExecutionContext",
    "ExecutionContextAnalyzer",
    "RoutingDecision",
    "OrchestratorRoutingEngine",
    "ExecutionMode",
    "ModeConfiguration",
    "AdaptiveExecutor",
    "CacheEntry",
    "CachingLayer",
    "ExecutionMetrics",
    "PerformanceProfile",
    "PerformanceProfiler",
    "UnifiedAdaptiveLayer",
    "FailoverContext",
    "ResourceAllocation",
    "StrategyType",
]
