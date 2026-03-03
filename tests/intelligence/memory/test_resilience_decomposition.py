"""TDD RED — Phase 103-f: resilience.py decomposition.

GAP-103-06: resilience.py (1,876L) → sub-package with 5 modules.
CORE-008: tests written before implementation.
"""
# ruff: noqa: S101
from __future__ import annotations

import pathlib
import pytest

RESILIENCE_PKG = pathlib.Path("cortex/intelligence/memory/tier2_adaptive/resilience")
RESILIENCE_FLAT = pathlib.Path("cortex/intelligence/memory/tier2_adaptive/resilience.py")


class TestResiliencePackageStructure:
    """Verify the sub-package exists with expected modules."""

    def test_resilience_is_package_not_flat_file(self) -> None:
        """resilience/ directory must exist; flat .py must not."""
        assert RESILIENCE_PKG.is_dir(), "resilience/ sub-package directory not found"
        assert not RESILIENCE_FLAT.exists(), "flat resilience.py must be removed after extraction"

    @pytest.mark.parametrize("module", [
        "__init__.py",
        "models.py",
        "degradation.py",
        "retry.py",
        "circuit_breaker.py",
        "monitoring.py",
    ])
    def test_expected_module_exists(self, module: str) -> None:
        assert (RESILIENCE_PKG / module).exists(), f"resilience/{module} not found"

    def test_coordinator_under_1000_lines(self) -> None:
        """orchestrator.py or __init__.py must be < 1000 lines."""
        target = RESILIENCE_PKG / "__init__.py"
        lines = len(target.read_text().splitlines())
        assert lines < 1000, f"resilience/__init__.py is {lines}L — must be < 1000L"


class TestResilienceImports:
    """All public symbols importable from top-level package path."""

    def test_models_importable(self) -> None:
        from cortex.intelligence.memory.tier2_adaptive.resilience import (
            ComponentFailure,
            DegradedResponse,
            FallbackStrategy,
            StrategyExecutionException,
            PartialFunctionalityMode,
        )
        assert ComponentFailure is not None
        assert DegradedResponse is not None
        assert FallbackStrategy is not None
        assert StrategyExecutionException is not None
        assert PartialFunctionalityMode is not None

    def test_degradation_importable(self) -> None:
        from cortex.intelligence.memory.tier2_adaptive.resilience import (
            GracefulDegradationFramework,
        )
        assert GracefulDegradationFramework is not None

    def test_retry_importable(self) -> None:
        from cortex.intelligence.memory.tier2_adaptive.resilience import (
            RetryPolicy,
            RetryPolicyBuilder,
            RetryResult,
            ExponentialBackoffRetry,
        )
        assert RetryPolicy is not None
        assert RetryPolicyBuilder is not None
        assert RetryResult is not None
        assert ExponentialBackoffRetry is not None

    def test_circuit_breaker_importable(self) -> None:
        from cortex.intelligence.memory.tier2_adaptive.resilience import (
            CircuitBreakerOpen,
            CircuitBreakerMetrics,
            CircuitBreakerConfig,
            CircuitBreaker,
        )
        assert CircuitBreakerOpen is not None
        assert CircuitBreakerMetrics is not None
        assert CircuitBreakerConfig is not None
        assert CircuitBreaker is not None

    def test_monitoring_importable(self) -> None:
        from cortex.intelligence.memory.tier2_adaptive.resilience import (
            DashboardUpdateType,
            DashboardUpdate,
            DashboardMetrics,
            RealTimeProgressDashboard,
            ThresholdOperator,
            Threshold,
            Alert,
            NotificationChannel,
            AlertManager,
        )
        assert RealTimeProgressDashboard is not None
        assert AlertManager is not None

    def test_backwards_compat_all_symbols(self) -> None:
        """All symbols that existed in flat file are re-exported from package."""
        import cortex.intelligence.memory.tier2_adaptive.resilience as pkg
        expected = [
            "ComponentFailure", "DegradedResponse", "FallbackStrategy",
            "StrategyExecutionException", "PartialFunctionalityMode",
            "GracefulDegradationFramework", "RetryPolicy", "RetryPolicyBuilder",
            "RetryResult", "ExponentialBackoffRetry", "CircuitBreakerOpen",
            "CircuitBreakerMetrics", "CircuitBreakerConfig", "CircuitBreaker",
            "DashboardUpdateType", "DashboardUpdate", "DashboardMetrics",
            "RealTimeProgressDashboard", "ThresholdOperator", "Threshold",
            "Alert", "NotificationChannel", "AlertManager",
        ]
        for sym in expected:
            assert hasattr(pkg, sym), f"resilience package missing re-export: {sym}"
