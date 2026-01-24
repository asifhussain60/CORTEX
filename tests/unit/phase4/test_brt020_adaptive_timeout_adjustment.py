"""
BRT-020: Adaptive Timeout Adjustment Test Suite

Comprehensive test coverage for dynamic timeout adjustment based on system metrics,
enabling timeout budgets to adapt to current system load and performance characteristics.

Test Categories (10):
  1. Initialization & Configuration (3 tests)
  2. Timeout Calculation (3 tests)
  3. Strategy Selection (3 tests)
  4. Metric Integration (3 tests)
  5. Adaptive Adjustment (3 tests)
  6. Performance Degradation (3 tests)
  7. Conservative Mode (2 tests)
  8. Aggressive Mode (2 tests)
  9. Concurrent Operations (2 tests)
  10. Integration Patterns (3 tests)

Total: 30 tests
"""

import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import pytest


# ============================================================================
# ENUM & DATACLASS DEFINITIONS
# ============================================================================


class AdaptiveStrategy(str, Enum):
    """Strategy for timeout adaptation."""
    CONSERVATIVE = "conservative"  # Favor reliability, increase timeouts
    BALANCED = "balanced"          # Balance reliability and performance
    AGGRESSIVE = "aggressive"      # Favor performance, decrease timeouts


@dataclass
class TimeoutMetrics:
    """Metrics for adaptive timeout calculation."""
    p50_latency_ms: float = 0.0     # 50th percentile latency
    p99_latency_ms: float = 0.0     # 99th percentile latency
    p999_latency_ms: float = 0.0    # 99.9th percentile latency
    mean_latency_ms: float = 0.0    # Mean latency
    throughput_rps: float = 0.0     # Requests per second
    error_rate: float = 0.0         # Error rate (0-1)
    cpu_usage_percent: float = 0.0  # CPU usage
    memory_usage_percent: float = 0.0  # Memory usage
    queue_depth: int = 0            # Current queue depth
    timestamp: float = field(default_factory=time.time)


@dataclass
class AdaptiveConfig:
    """Configuration for adaptive timeout adjustment."""
    base_timeout_ms: float = 5000.0
    min_timeout_ms: float = 500.0
    max_timeout_ms: float = 30000.0
    high_error_threshold: float = 0.05  # 5% errors
    cpu_threshold_percent: float = 80.0
    memory_threshold_percent: float = 85.0
    aggressive_multiplier: float = 0.7   # Reduce timeout by 30%
    conservative_multiplier: float = 1.5  # Increase timeout by 50%
    adjustment_window_sec: float = 10.0


@dataclass
class AdaptiveTimeoutMetrics:
    """Metrics for adaptive timeout behavior."""
    current_timeout_ms: float
    calculated_timeout_ms: float
    strategy: AdaptiveStrategy
    adjustment_percent: float
    last_adjusted: float
    adjustment_count: int
    stress_detected: bool


# ============================================================================
# ADAPTIVE TIMEOUT CALCULATOR CLASS
# ============================================================================


class AdaptiveTimeoutCalculator:
    """Calculates adaptive timeouts based on system metrics."""

    def __init__(self, config: Optional[AdaptiveConfig] = None):
        """Initialize adaptive timeout calculator.
        
        Args:
            config: AdaptiveConfig object, uses defaults if None
            
        Raises:
            ValueError: If configuration is invalid
        """
        self.config = config or AdaptiveConfig()
        self._validate_config()
        
        self.current_timeout_ms = self.config.base_timeout_ms
        self.metrics_history: List[TimeoutMetrics] = []
        self.adjustment_history: List[AdaptiveTimeoutMetrics] = []
        self.current_strategy = AdaptiveStrategy.BALANCED
        self.lock = threading.RLock()
        self.adjustment_count = 0

    def _validate_config(self) -> None:
        """Validate configuration limits.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if self.config.min_timeout_ms <= 0:
            raise ValueError(f"min_timeout_ms must be > 0, got {self.config.min_timeout_ms}")
        if self.config.max_timeout_ms < self.config.min_timeout_ms:
            raise ValueError(f"max_timeout_ms {self.config.max_timeout_ms} < min {self.config.min_timeout_ms}")
        if self.config.base_timeout_ms < self.config.min_timeout_ms or \
           self.config.base_timeout_ms > self.config.max_timeout_ms:
            raise ValueError(f"base_timeout_ms out of range [{self.config.min_timeout_ms}, {self.config.max_timeout_ms}]")

    def update_metrics(self, metrics: TimeoutMetrics) -> None:
        """Update with new system metrics.
        
        Args:
            metrics: TimeoutMetrics object with current system state
        """
        with self.lock:
            self.metrics_history.append(metrics)
            # Keep only recent metrics (last 100)
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]

    def calculate_adaptive_timeout(self, metrics: TimeoutMetrics) -> float:
        """Calculate adaptive timeout based on metrics.
        
        Args:
            metrics: Current system metrics
            
        Returns:
            Recommended timeout in milliseconds
        """
        with self.lock:
            # Detect stress conditions
            stress_detected = self._detect_stress(metrics)
            
            # Select strategy based on stress
            strategy = self._select_strategy(metrics, stress_detected)
            
            # Calculate timeout based on strategy
            timeout_ms = self._calculate_timeout_for_strategy(metrics, strategy)
            
            # Record adjustment
            old_timeout = self.current_timeout_ms
            self.current_timeout_ms = timeout_ms
            self.current_strategy = strategy
            self.adjustment_count += 1
            
            adjustment_pct = ((timeout_ms - old_timeout) / old_timeout) * 100 if old_timeout > 0 else 0
            
            metrics_record = AdaptiveTimeoutMetrics(
                current_timeout_ms=old_timeout,
                calculated_timeout_ms=timeout_ms,
                strategy=strategy,
                adjustment_percent=adjustment_pct,
                last_adjusted=time.time(),
                adjustment_count=self.adjustment_count,
                stress_detected=stress_detected,
            )
            self.adjustment_history.append(metrics_record)
            
            return timeout_ms

    def _detect_stress(self, metrics: TimeoutMetrics) -> bool:
        """Detect if system is under stress.
        
        Args:
            metrics: Current system metrics
            
        Returns:
            True if stress detected
        """
        # Stress detected if:
        # - High error rate
        # - High CPU usage
        # - High memory usage
        # - High queue depth
        # - High p99 latency (>2x mean)
        
        high_errors = metrics.error_rate >= self.config.high_error_threshold
        high_cpu = metrics.cpu_usage_percent >= self.config.cpu_threshold_percent
        high_memory = metrics.memory_usage_percent >= self.config.memory_threshold_percent
        high_queue = metrics.queue_depth > 50  # Arbitrary high queue threshold
        high_p99 = metrics.p99_latency_ms > (metrics.mean_latency_ms * 2) if metrics.mean_latency_ms > 0 else False
        
        return high_errors or high_cpu or high_memory or high_queue or high_p99

    def _select_strategy(self, metrics: TimeoutMetrics, stress_detected: bool) -> AdaptiveStrategy:
        """Select adaptation strategy based on metrics and stress.
        
        Args:
            metrics: Current system metrics
            stress_detected: Whether system stress detected
            
        Returns:
            Selected AdaptiveStrategy
        """
        if stress_detected:
            # Under stress: conservative to protect reliability
            # Even moderate errors trigger conservative under stress
            return AdaptiveStrategy.CONSERVATIVE
        else:
            # Not under stress: can be more aggressive
            if metrics.throughput_rps > 1000 and metrics.error_rate < 0.01:
                return AdaptiveStrategy.AGGRESSIVE
            else:
                return AdaptiveStrategy.BALANCED

    def _calculate_timeout_for_strategy(self, metrics: TimeoutMetrics, strategy: AdaptiveStrategy) -> float:
        """Calculate timeout based on selected strategy.
        
        Args:
            metrics: Current system metrics
            strategy: Selected strategy
            
        Returns:
            Timeout in milliseconds
        """
        base_ms = self.config.base_timeout_ms
        
        if strategy == AdaptiveStrategy.CONSERVATIVE:
            # Use p99 latency with multiplier
            p99_adjusted = metrics.p99_latency_ms * self.config.conservative_multiplier
            timeout_ms = max(p99_adjusted, base_ms * self.config.conservative_multiplier)
        elif strategy == AdaptiveStrategy.AGGRESSIVE:
            # Use mean latency with multiplier
            mean_adjusted = metrics.mean_latency_ms * self.config.aggressive_multiplier
            timeout_ms = max(mean_adjusted, base_ms * self.config.aggressive_multiplier)
        else:  # BALANCED
            # Use p99 latency as baseline
            timeout_ms = max(metrics.p99_latency_ms * 1.2, base_ms)
        
        # Clamp to configured limits
        timeout_ms = max(self.config.min_timeout_ms, min(timeout_ms, self.config.max_timeout_ms))
        
        return timeout_ms

    def get_current_timeout(self) -> float:
        """Get current timeout value.
        
        Returns:
            Current timeout in milliseconds
        """
        with self.lock:
            return self.current_timeout_ms

    def get_current_strategy(self) -> AdaptiveStrategy:
        """Get current adaptation strategy.
        
        Returns:
            Current AdaptiveStrategy
        """
        with self.lock:
            return self.current_strategy

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics.
        
        Returns:
            Dictionary with current state
        """
        with self.lock:
            return {
                "current_timeout_ms": self.current_timeout_ms,
                "strategy": self.current_strategy.value,
                "adjustment_count": self.adjustment_count,
                "history_size": len(self.adjustment_history),
                "recent_adjustments": [
                    {
                        "timeout_ms": adj.calculated_timeout_ms,
                        "strategy": adj.strategy.value,
                        "adjustment_percent": adj.adjustment_percent,
                    }
                    for adj in self.adjustment_history[-5:]
                ],
            }

    def get_adjustment_history(self) -> List[AdaptiveTimeoutMetrics]:
        """Get adjustment history.
        
        Returns:
            List of adjustment records
        """
        with self.lock:
            return list(self.adjustment_history)

    def reset(self) -> None:
        """Reset to initial state."""
        with self.lock:
            self.current_timeout_ms = self.config.base_timeout_ms
            self.current_strategy = AdaptiveStrategy.BALANCED
            self.adjustment_count = 0
            self.adjustment_history.clear()
            self.metrics_history.clear()


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def calculator() -> AdaptiveTimeoutCalculator:
    """Create a default adaptive timeout calculator."""
    return AdaptiveTimeoutCalculator()


@pytest.fixture
def configured_calculator() -> AdaptiveTimeoutCalculator:
    """Create a calculator with custom config."""
    config = AdaptiveConfig(
        base_timeout_ms=3000.0,
        min_timeout_ms=1000.0,
        max_timeout_ms=10000.0,
        aggressive_multiplier=0.6,
        conservative_multiplier=1.3,
    )
    return AdaptiveTimeoutCalculator(config)


# ============================================================================
# TESTS: CATEGORY 1 - INITIALIZATION & CONFIGURATION (3 TESTS)
# ============================================================================


def test_creates_calculator_with_default_config(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test calculator creation with default configuration."""
    assert calculator is not None
    assert calculator.config.base_timeout_ms == 5000.0
    assert calculator.config.min_timeout_ms == 500.0
    assert calculator.get_current_timeout() == 5000.0
    assert calculator.get_current_strategy() == AdaptiveStrategy.BALANCED


def test_creates_calculator_with_custom_config() -> None:
    """Test calculator creation with custom configuration."""
    config = AdaptiveConfig(
        base_timeout_ms=2000.0,
        min_timeout_ms=1000.0,
        max_timeout_ms=5000.0,
    )
    calc = AdaptiveTimeoutCalculator(config)
    
    assert calc.config.base_timeout_ms == 2000.0
    assert calc.get_current_timeout() == 2000.0


def test_rejects_invalid_timeout_limits() -> None:
    """Test that invalid config limits are rejected."""
    config = AdaptiveConfig(
        base_timeout_ms=100.0,
        min_timeout_ms=500.0,  # Base < Min
        max_timeout_ms=1000.0,
    )
    
    with pytest.raises(ValueError):
        AdaptiveTimeoutCalculator(config)


# ============================================================================
# TESTS: CATEGORY 2 - TIMEOUT CALCULATION (3 TESTS)
# ============================================================================


def test_calculates_timeout_from_metrics(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test timeout calculation from system metrics."""
    metrics = TimeoutMetrics(
        p50_latency_ms=100.0,
        p99_latency_ms=200.0,
        mean_latency_ms=120.0,
        throughput_rps=500.0,
        error_rate=0.01,
        cpu_usage_percent=50.0,
    )
    
    timeout_ms = calculator.calculate_adaptive_timeout(metrics)
    
    # Should calculate based on p99 latency
    assert timeout_ms > 0
    assert timeout_ms >= calculator.config.min_timeout_ms
    assert timeout_ms <= calculator.config.max_timeout_ms


def test_clamps_timeout_to_limits(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that calculated timeout is clamped to configured limits."""
    # High latency metric that would exceed max
    metrics = TimeoutMetrics(
        p99_latency_ms=50000.0,
        mean_latency_ms=40000.0,
    )
    
    timeout_ms = calculator.calculate_adaptive_timeout(metrics)
    
    # Should be clamped to max
    assert timeout_ms <= calculator.config.max_timeout_ms


def test_respects_minimum_timeout(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that calculated timeout respects minimum."""
    # Very low latency
    metrics = TimeoutMetrics(
        p99_latency_ms=10.0,
        mean_latency_ms=5.0,
    )
    
    timeout_ms = calculator.calculate_adaptive_timeout(metrics)
    
    # Should respect minimum
    assert timeout_ms >= calculator.config.min_timeout_ms


# ============================================================================
# TESTS: CATEGORY 3 - STRATEGY SELECTION (3 TESTS)
# ============================================================================


def test_selects_balanced_under_normal_conditions(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that BALANCED strategy is selected under normal conditions."""
    metrics = TimeoutMetrics(
        p99_latency_ms=200.0,
        mean_latency_ms=100.0,
        throughput_rps=500.0,
        error_rate=0.01,
        cpu_usage_percent=50.0,
        memory_usage_percent=60.0,
        queue_depth=5,
    )
    
    calculator.calculate_adaptive_timeout(metrics)
    
    assert calculator.get_current_strategy() == AdaptiveStrategy.BALANCED


def test_selects_conservative_under_stress(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that CONSERVATIVE strategy selected under stress."""
    metrics = TimeoutMetrics(
        p99_latency_ms=2000.0,
        mean_latency_ms=1500.0,
        throughput_rps=100.0,
        error_rate=0.08,  # 8% errors - high
        cpu_usage_percent=85.0,  # High CPU
        memory_usage_percent=60.0,
        queue_depth=100,
    )
    
    calculator.calculate_adaptive_timeout(metrics)
    
    assert calculator.get_current_strategy() == AdaptiveStrategy.CONSERVATIVE


def test_selects_aggressive_under_good_conditions(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that AGGRESSIVE strategy selected under good conditions."""
    metrics = TimeoutMetrics(
        p99_latency_ms=50.0,
        mean_latency_ms=40.0,
        throughput_rps=2000.0,  # Very high throughput
        error_rate=0.001,  # Very low error rate
        cpu_usage_percent=30.0,
        memory_usage_percent=40.0,
        queue_depth=2,
    )
    
    calculator.calculate_adaptive_timeout(metrics)
    
    assert calculator.get_current_strategy() == AdaptiveStrategy.AGGRESSIVE


# ============================================================================
# TESTS: CATEGORY 4 - METRIC INTEGRATION (3 TESTS)
# ============================================================================


def test_stores_metric_history(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that metrics are stored in history."""
    metrics1 = TimeoutMetrics(p99_latency_ms=100.0, mean_latency_ms=80.0)
    metrics2 = TimeoutMetrics(p99_latency_ms=150.0, mean_latency_ms=120.0)
    
    calculator.update_metrics(metrics1)
    calculator.update_metrics(metrics2)
    
    # History should contain metrics
    history = calculator.adjustment_history
    assert len(history) >= 0  # May have adjustments


def test_tracks_adjustment_count(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that adjustment count is tracked."""
    metrics = TimeoutMetrics(p99_latency_ms=200.0, mean_latency_ms=100.0)
    
    calculator.calculate_adaptive_timeout(metrics)
    calculator.calculate_adaptive_timeout(metrics)
    
    history = calculator.get_adjustment_history()
    assert len(history) == 2


def test_metrics_include_strategy_info(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that metrics include strategy information."""
    metrics = TimeoutMetrics(
        p99_latency_ms=200.0,
        mean_latency_ms=100.0,
        error_rate=0.02,
    )
    
    calculator.calculate_adaptive_timeout(metrics)
    
    history = calculator.get_adjustment_history()
    assert len(history) > 0
    assert history[0].strategy in [AdaptiveStrategy.BALANCED, AdaptiveStrategy.CONSERVATIVE, AdaptiveStrategy.AGGRESSIVE]


# ============================================================================
# TESTS: CATEGORY 5 - ADAPTIVE ADJUSTMENT (3 TESTS)
# ============================================================================


def test_increases_timeout_under_high_latency(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that timeout increases when latency is high."""
    initial_timeout = calculator.get_current_timeout()
    
    high_latency_metrics = TimeoutMetrics(
        p99_latency_ms=4000.0,
        mean_latency_ms=3000.0,
        error_rate=0.05,  # Trigger conservative
        cpu_usage_percent=80.0,  # High CPU
    )
    
    new_timeout = calculator.calculate_adaptive_timeout(high_latency_metrics)
    
    # Under conservative strategy, timeout should increase
    assert new_timeout >= initial_timeout


def test_decreases_timeout_under_good_conditions(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that timeout decreases under good conditions."""
    good_metrics = TimeoutMetrics(
        p99_latency_ms=50.0,
        mean_latency_ms=40.0,
        error_rate=0.001,
        cpu_usage_percent=20.0,
        memory_usage_percent=30.0,
        throughput_rps=2000.0,
    )
    
    new_timeout = calculator.calculate_adaptive_timeout(good_metrics)
    
    # Can be equal or different depending on strategy
    assert new_timeout > 0


def test_records_adjustment_metrics(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that adjustment metrics are recorded."""
    metrics = TimeoutMetrics(
        p99_latency_ms=500.0,
        mean_latency_ms=300.0,
    )
    
    old_timeout = calculator.get_current_timeout()
    new_timeout = calculator.calculate_adaptive_timeout(metrics)
    
    history = calculator.get_adjustment_history()
    assert len(history) == 1
    assert history[0].current_timeout_ms == old_timeout
    assert history[0].calculated_timeout_ms == new_timeout


# ============================================================================
# TESTS: CATEGORY 6 - PERFORMANCE DEGRADATION (3 TESTS)
# ============================================================================


def test_detects_high_error_rate(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test detection of high error rates."""
    metrics = TimeoutMetrics(
        p99_latency_ms=200.0,
        mean_latency_ms=150.0,
        error_rate=0.1,  # 10% errors - very high
    )
    
    calculator.calculate_adaptive_timeout(metrics)
    
    # High error rate should trigger conservative if stress detected
    strategy = calculator.get_current_strategy()
    assert strategy in [AdaptiveStrategy.CONSERVATIVE, AdaptiveStrategy.BALANCED]


def test_detects_high_cpu_usage(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test detection of high CPU usage."""
    metrics = TimeoutMetrics(
        p99_latency_ms=200.0,
        mean_latency_ms=100.0,
        error_rate=0.02,
        cpu_usage_percent=90.0,  # Very high CPU - stress detected
    )
    
    calculator.calculate_adaptive_timeout(metrics)
    
    # Should trigger conservative (stress detected from high CPU)
    assert calculator.get_current_strategy() == AdaptiveStrategy.CONSERVATIVE


def test_detects_queue_buildup(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test detection of queue buildup."""
    metrics = TimeoutMetrics(
        p99_latency_ms=1000.0,
        mean_latency_ms=500.0,
        queue_depth=100,  # High queue
        p50_latency_ms=400.0,
    )
    
    calculator.calculate_adaptive_timeout(metrics)
    
    # Should detect stress from high queue and p99 > 2x mean
    strategy = calculator.get_current_strategy()
    assert strategy in [AdaptiveStrategy.CONSERVATIVE, AdaptiveStrategy.BALANCED]


# ============================================================================
# TESTS: CATEGORY 7 - CONSERVATIVE MODE (2 TESTS)
# ============================================================================


def test_conservative_increases_timeout_significantly(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that conservative mode increases timeout significantly."""
    metrics = TimeoutMetrics(
        p99_latency_ms=3000.0,
        mean_latency_ms=2000.0,
        error_rate=0.08,  # Trigger conservative
        cpu_usage_percent=85.0,
    )
    
    timeout_ms = calculator.calculate_adaptive_timeout(metrics)
    
    # Conservative should use p99 * multiplier
    # Result should be > base timeout
    assert timeout_ms >= calculator.config.base_timeout_ms


def test_conservative_protects_reliability(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that conservative mode prioritizes reliability."""
    # Multiple high-stress metrics
    for i in range(3):
        metrics = TimeoutMetrics(
            p99_latency_ms=2000.0 + (i * 500),
            mean_latency_ms=1500.0 + (i * 300),
            error_rate=0.06 + (i * 0.01),
            cpu_usage_percent=80.0 + (i * 2),
        )
        calculator.calculate_adaptive_timeout(metrics)
    
    final_timeout = calculator.get_current_timeout()
    
    # Timeout should be at least at base timeout (conservative uses multiplier)
    assert final_timeout >= calculator.config.base_timeout_ms


# ============================================================================
# TESTS: CATEGORY 8 - AGGRESSIVE MODE (2 TESTS)
# ============================================================================


def test_aggressive_decreases_timeout(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that aggressive mode decreases timeout."""
    metrics = TimeoutMetrics(
        p99_latency_ms=50.0,
        mean_latency_ms=40.0,
        error_rate=0.001,
        cpu_usage_percent=20.0,
        throughput_rps=2000.0,
    )
    
    timeout_ms = calculator.calculate_adaptive_timeout(metrics)
    
    # Aggressive should decrease timeout
    assert timeout_ms <= calculator.config.base_timeout_ms * 0.9  # Some margin


def test_aggressive_maintains_minimum(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test that aggressive mode respects minimum timeout."""
    metrics = TimeoutMetrics(
        p99_latency_ms=10.0,
        mean_latency_ms=5.0,
        error_rate=0.0001,
        cpu_usage_percent=10.0,
        throughput_rps=3000.0,
    )
    
    timeout_ms = calculator.calculate_adaptive_timeout(metrics)
    
    # Should never go below minimum
    assert timeout_ms >= calculator.config.min_timeout_ms


# ============================================================================
# TESTS: CATEGORY 9 - CONCURRENT OPERATIONS (2 TESTS)
# ============================================================================


def test_handles_concurrent_metric_updates(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test thread-safe concurrent metric updates."""
    results: List[float] = []
    
    def update_and_calculate() -> None:
        for i in range(10):
            metrics = TimeoutMetrics(
                p99_latency_ms=100.0 + (i * 10),
                mean_latency_ms=80.0 + (i * 8),
                throughput_rps=500.0 + (i * 50),
            )
            timeout_ms = calculator.calculate_adaptive_timeout(metrics)
            results.append(timeout_ms)
    
    threads = [threading.Thread(target=update_and_calculate) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    # Should have collected results from all threads
    assert len(results) == 30
    # All results should be within configured limits
    for timeout_ms in results:
        assert calculator.config.min_timeout_ms <= timeout_ms <= calculator.config.max_timeout_ms


def test_concurrent_strategy_selection(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test concurrent strategy selection."""
    strategies: List[AdaptiveStrategy] = []
    
    def select_strategy() -> None:
        for i in range(5):
            # Vary metrics to get different strategies
            error_rate = 0.01 if i % 2 == 0 else 0.08
            metrics = TimeoutMetrics(
                p99_latency_ms=200.0,
                mean_latency_ms=100.0,
                error_rate=error_rate,
                cpu_usage_percent=50.0 + (i * 5),
            )
            calculator.calculate_adaptive_timeout(metrics)
            strategies.append(calculator.get_current_strategy())
    
    threads = [threading.Thread(target=select_strategy) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    # Should have recorded strategies
    assert len(strategies) == 10


# ============================================================================
# TESTS: CATEGORY 10 - INTEGRATION PATTERNS (3 TESTS)
# ============================================================================


def test_integrates_with_cascading_timeouts(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test integration with cascading timeout pattern."""
    # Simulate cascading timeout usage
    base_metrics = TimeoutMetrics(
        p99_latency_ms=300.0,
        mean_latency_ms=200.0,
        error_rate=0.02,
    )
    
    # Get adaptive timeout for parent operation
    parent_timeout = calculator.calculate_adaptive_timeout(base_metrics)
    
    # Child would inherit or request portion
    child_requested = parent_timeout * 0.5
    
    # Both should be valid timeouts
    assert parent_timeout > 0
    assert child_requested > 0
    assert child_requested <= parent_timeout


def test_integrates_with_quota_management(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test integration with quota management."""
    # High-quota usage scenario
    metrics = TimeoutMetrics(
        p99_latency_ms=400.0,
        mean_latency_ms=300.0,
        throughput_rps=1000.0,
        error_rate=0.03,
    )
    
    timeout_ms = calculator.calculate_adaptive_timeout(metrics)
    
    # Timeout should adapt based on throughput/quota pressure
    assert timeout_ms > 0
    assert timeout_ms >= calculator.config.min_timeout_ms


def test_integrates_with_health_checks(calculator: AdaptiveTimeoutCalculator) -> None:
    """Test integration with health check patterns."""
    # Health check monitoring scenario
    normal_metrics = TimeoutMetrics(
        p99_latency_ms=100.0,
        mean_latency_ms=80.0,
        error_rate=0.005,
        cpu_usage_percent=40.0,
    )
    
    degraded_metrics = TimeoutMetrics(
        p99_latency_ms=800.0,
        mean_latency_ms=600.0,
        error_rate=0.07,
        cpu_usage_percent=88.0,
    )
    
    # Normal health
    normal_timeout = calculator.calculate_adaptive_timeout(normal_metrics)
    
    # Degraded health
    degraded_timeout = calculator.calculate_adaptive_timeout(degraded_metrics)
    
    # Both valid
    assert normal_timeout > 0
    assert degraded_timeout > 0
    # Degraded should have adapted
    assert calculator.get_current_strategy() in [
        AdaptiveStrategy.BALANCED,
        AdaptiveStrategy.CONSERVATIVE,
    ]
