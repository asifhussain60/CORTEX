"""
tier2: Advanced Framework Components

Implements production-grade reliability, observability, and resilience patterns.

Modules:
- resilience: Graceful degradation, retry logic, circuit breaker patterns
- metrics: OpenTelemetry metrics collection and export
- dashboard: Real-time progress monitoring
- alerts: Threshold-based alerting system

All components follow CORTEX governance standards:
✓ CORE-008: TDD Pattern
✓ CORE-011: 100% Type Hints  
✓ CORE-012: 100% Docstrings
✓ CORE-024: Audit Logging
"""

from .resilience import (
    GracefulDegradationFramework,
    FallbackStrategy,
    PartialFunctionalityMode,
    ComponentFailure,
    DegradedResponse,
    StrategyExecutionException,
    ExponentialBackoffRetry,
    RetryPolicy,
    RetryPolicyBuilder,
    RetryResult,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerMetrics,
    CircuitBreakerState,
    CircuitBreakerOpen,
)

__all__ = [
    "GracefulDegradationFramework",
    "FallbackStrategy",
    "PartialFunctionalityMode",
    "ComponentFailure",
    "DegradedResponse",
    "StrategyExecutionException",
    "ExponentialBackoffRetry",
    "RetryPolicy",
    "RetryPolicyBuilder",
    "RetryResult",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerMetrics",
    "CircuitBreakerState",
    "CircuitBreakerOpen",
]
