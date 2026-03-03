"""
resilience — Graceful degradation, retry, circuit breaker, and monitoring.

AC_START: AC-RESILIENCE-001
Phase 103-f: decomposed from resilience.py (1,876L) god-object.
Backwards-compatible re-export of all public symbols.
AC_COMPLETE: AC-RESILIENCE-001 ✅
"""
# --- models ---
from cortex.intelligence.memory.tier2_adaptive.resilience.models import (
    ComponentFailure,
    DegradedResponse,
    FallbackStrategy,
    PartialFunctionalityMode,
    StrategyExecutionException,
)

# --- degradation ---
from cortex.intelligence.memory.tier2_adaptive.resilience.degradation import (
    GracefulDegradationFramework,
)

# --- retry ---
from cortex.intelligence.memory.tier2_adaptive.resilience.retry import (
    ExponentialBackoffRetry,
    RetryPolicy,
    RetryPolicyBuilder,
    RetryResult,
)

# --- circuit_breaker ---
from cortex.intelligence.memory.tier2_adaptive.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerMetrics,
    CircuitBreakerOpen,
)

# --- canonical enums (re-exported for backwards compat with tier2_adaptive/__init__.py) ---
from cortex.models.canonical_enums import AlertSeverity, CircuitBreakerState

# --- monitoring ---
from cortex.intelligence.memory.tier2_adaptive.resilience.monitoring import (
    Alert,
    AlertManager,
    DashboardMetrics,
    DashboardUpdate,
    DashboardUpdateType,
    InstrumentationSpan,
    MetricExportConfig,
    MetricUnit,
    MetricValue,
    MetricsCollector,
    NotificationChannel,
    RealTimeProgressDashboard,
    Threshold,
    ThresholdOperator,
)

__all__ = [
    # models
    "ComponentFailure",
    "DegradedResponse",
    "FallbackStrategy",
    "PartialFunctionalityMode",
    "StrategyExecutionException",
    # degradation
    "GracefulDegradationFramework",
    # retry
    "ExponentialBackoffRetry",
    "RetryPolicy",
    "RetryPolicyBuilder",
    "RetryResult",
    # circuit_breaker
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerMetrics",
    "CircuitBreakerOpen",
    # canonical enums (backwards compat)
    "AlertSeverity",
    "CircuitBreakerState",
    # monitoring
    "Alert",
    "AlertManager",
    "DashboardMetrics",
    "DashboardUpdate",
    "DashboardUpdateType",
    "InstrumentationSpan",
    "MetricExportConfig",
    "MetricUnit",
    "MetricValue",
    "MetricsCollector",
    "NotificationChannel",
    "RealTimeProgressDashboard",
    "Threshold",
    "ThresholdOperator",
]
