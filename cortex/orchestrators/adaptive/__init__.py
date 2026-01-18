"""Adaptive Execution Framework

Implements context-aware orchestrator routing and optimization for CORTEX.

Modules:
    execution_context_analyzer: ExecutionContextAnalyzer for task analysis
    routing_engine: OrchestratorRoutingEngine for intelligent orchestrator selection
    execution_modes: ExecutionMode enums and mode handlers
    caching_layer: CachingLayer for result caching with TTL
    performance_profiler: PerformanceProfiler for execution profiling

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

from .execution_context_analyzer import (
    ExecutionContext,
    ExecutionContextAnalyzer,
)
from .routing_engine import (
    RoutingDecision,
    OrchestratorRoutingEngine,
)
from .execution_modes import (
    ExecutionMode,
    ModeConfiguration,
    AdaptiveExecutor,
)
from .caching_layer import (
    CacheEntry,
    CachingLayer,
)
from .performance_profiler import (
    ExecutionMetrics,
    PerformanceProfile,
    PerformanceProfiler,
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
]
