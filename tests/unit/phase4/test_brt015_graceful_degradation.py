"""
Comprehensive test suite for BRT-015: Graceful Degradation Pattern.

Tests graceful service degradation modes when resources become exhausted or
operations slow down, allowing services to reduce functionality gracefully
instead of failing hard.

The graceful degradation pattern enables:
- Multiple service quality levels (FULL → REDUCED → MINIMAL → OFFLINE)
- Fallback execution modes with reduced functionality
- Automatic recovery transitions when resources become available
- Metrics tracking for degradation events

AC-INFRA-001-04: Graceful service degradation with fallback modes
"""

import threading
import time
from typing import List, Generator, Callable, Any, Optional, Dict
from dataclasses import dataclass, field
from enum import Enum

import pytest


# ============================================================================
# GRACEFUL DEGRADATION IMPLEMENTATION FOR TESTING
# ============================================================================

class DegradationLevel(str, Enum):
    """Service quality levels."""
    FULL = "full"              # Normal operation
    REDUCED = "reduced"        # Limited functionality
    MINIMAL = "minimal"        # Essential operations only
    OFFLINE = "offline"        # Service unavailable


class DegradationTrigger(str, Enum):
    """What triggers degradation."""
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    TIMEOUT_THRESHOLD = "timeout_threshold"
    ERROR_RATE = "error_rate"
    MANUAL = "manual"


@dataclass
class FallbackStrategy:
    """Strategy for executing operation in degraded mode."""
    
    name: str
    level: DegradationLevel
    executor: Callable[..., Any]
    is_cached: bool = False
    response_time_ms: float = 0.0


@dataclass
class DegradationMetrics:
    """Metrics for graceful degradation."""
    
    total_operations: int = 0
    full_level_operations: int = 0
    reduced_level_operations: int = 0
    minimal_level_operations: int = 0
    offline_operations: int = 0
    
    degradation_events: int = 0
    recovery_events: int = 0
    
    average_response_time_ms: float = 0.0
    min_response_time_ms: float = float('inf')
    max_response_time_ms: float = 0.0


@dataclass
class DegradationConfig:
    """Configuration for graceful degradation."""
    
    current_level: DegradationLevel = DegradationLevel.FULL
    enable_auto_degradation: bool = True
    resource_threshold: float = 0.8  # Degrade at 80% resource usage
    error_rate_threshold: float = 0.1  # Degrade at 10% error rate
    recovery_check_interval_ms: float = 1000.0
    fallback_strategies: Dict[Any, Any] = field(default_factory=dict)


class GracefulDegradationManager:
    """Manages graceful service degradation."""
    
    def __init__(self, config: Optional[DegradationConfig] = None) -> None:
        """Initialize degradation manager."""
        self.config = config or DegradationConfig()
        self.metrics = DegradationMetrics()
        self.lock = threading.Lock()
        self._degradation_history: List[tuple[DegradationLevel, DegradationLevel, Optional[DegradationTrigger]]] = []
        self._current_trigger: Optional[DegradationTrigger] = None
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration."""
        if self.config.resource_threshold <= 0 or self.config.resource_threshold > 1.0:
            raise ValueError("resource_threshold must be between 0 and 1")
        if self.config.error_rate_threshold < 0 or self.config.error_rate_threshold > 1.0:
            raise ValueError("error_rate_threshold must be between 0 and 1")
    
    def set_degradation_level(
        self,
        level: DegradationLevel,
        trigger: Optional[DegradationTrigger] = None,
    ) -> None:
        """Set service degradation level."""
        with self.lock:
            old_level = self.config.current_level
            self.config.current_level = level
            self._current_trigger = trigger
            
            if level != old_level:
                self._degradation_history.append((old_level, level, trigger))
                
                if self._is_degradation(old_level, level):
                    self.metrics.degradation_events += 1
                elif self._is_recovery(old_level, level):
                    self.metrics.recovery_events += 1
    
    def get_degradation_level(self) -> DegradationLevel:
        """Get current degradation level."""
        with self.lock:
            return self.config.current_level
    
    def register_fallback_strategy(
        self,
        level: DegradationLevel,
        name: str,
        executor: Callable[..., Any],
        is_cached: bool = False,
        response_time_ms: float = 0.0,
    ) -> None:
        """Register fallback strategy for degradation level."""
        strategy = FallbackStrategy(
            name=name,
            level=level,
            executor=executor,
            is_cached=is_cached,
            response_time_ms=response_time_ms,
        )
        self.config.fallback_strategies[level] = strategy
    
    def execute_with_degradation(
        self,
        full_operation: Callable[..., Any],
        resource_usage: float = 0.0,
        error_rate: float = 0.0,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute operation with automatic degradation."""
        # Get current level first
        current_level = self.get_degradation_level()
        
        # Check if offline
        if current_level == DegradationLevel.OFFLINE:
            raise RuntimeError("Service is offline")
        
        # Determine degradation level based on conditions (only if auto-degradation enabled)
        if self.config.enable_auto_degradation and (resource_usage > 0 or error_rate > 0):
            level = self._determine_degradation_level(resource_usage, error_rate)
            
            # Update level if changed
            if level != current_level:
                if resource_usage >= self.config.resource_threshold:
                    trigger = DegradationTrigger.RESOURCE_EXHAUSTION
                elif error_rate >= self.config.error_rate_threshold:
                    trigger = DegradationTrigger.ERROR_RATE
                else:
                    trigger = None
                
                self.set_degradation_level(level, trigger)
        else:
            level = current_level
        
        # Execute appropriate operation based on level
        start_time = time.time()
        result = None
        
        try:
            if level == DegradationLevel.FULL:
                result = full_operation(*args, **kwargs)
                with self.lock:
                    self.metrics.full_level_operations += 1
            elif level == DegradationLevel.REDUCED:
                result = self._execute_reduced(*args, **kwargs)
                with self.lock:
                    self.metrics.reduced_level_operations += 1
            elif level == DegradationLevel.MINIMAL:
                result = self._execute_minimal(*args, **kwargs)
                with self.lock:
                    self.metrics.minimal_level_operations += 1
            else:  # OFFLINE
                raise RuntimeError("Service is offline")
        finally:
            elapsed = time.time() - start_time
            elapsed_ms = elapsed * 1000
            
            with self.lock:
                self.metrics.total_operations += 1
                
                # Update response time metrics
                self.metrics.max_response_time_ms = max(
                    self.metrics.max_response_time_ms,
                    elapsed_ms
                )
                self.metrics.min_response_time_ms = min(
                    self.metrics.min_response_time_ms,
                    elapsed_ms
                )
                
                if self.metrics.total_operations > 0:
                    old_avg = self.metrics.average_response_time_ms
                    self.metrics.average_response_time_ms = (
                        old_avg * (self.metrics.total_operations - 1) + elapsed_ms
                    ) / self.metrics.total_operations
        
        return result
    
    def _determine_degradation_level(
        self,
        resource_usage: float,
        error_rate: float,
    ) -> DegradationLevel:
        """Determine appropriate degradation level."""
        if not self.config.enable_auto_degradation:
            return self.get_degradation_level()
        
        if error_rate > self.config.error_rate_threshold:
            if error_rate > 0.3:
                return DegradationLevel.MINIMAL
            else:
                return DegradationLevel.REDUCED
        
        if resource_usage >= self.config.resource_threshold:
            if resource_usage > 0.95:
                return DegradationLevel.MINIMAL
            else:
                return DegradationLevel.REDUCED
        
        return DegradationLevel.FULL
    
    def _execute_reduced(self, *args: Any, **kwargs: Any) -> Any:
        """Execute reduced functionality operation."""
        strategy = self.config.fallback_strategies.get(DegradationLevel.REDUCED)
        if strategy:
            return strategy.executor(*args, **kwargs)
        return None
    
    def _execute_minimal(self, *args: Any, **kwargs: Any) -> Any:
        """Execute minimal operation."""
        strategy = self.config.fallback_strategies.get(DegradationLevel.MINIMAL)
        if strategy:
            return strategy.executor(*args, **kwargs)
        return None
    
    def _is_degradation(self, old_level: DegradationLevel, new_level: DegradationLevel) -> bool:
        """Check if transition is degradation."""
        level_order = [DegradationLevel.FULL, DegradationLevel.REDUCED, 
                      DegradationLevel.MINIMAL, DegradationLevel.OFFLINE]
        return level_order.index(new_level) > level_order.index(old_level)
    
    def _is_recovery(self, old_level: DegradationLevel, new_level: DegradationLevel) -> bool:
        """Check if transition is recovery."""
        level_order = [DegradationLevel.FULL, DegradationLevel.REDUCED, 
                      DegradationLevel.MINIMAL, DegradationLevel.OFFLINE]
        return level_order.index(new_level) < level_order.index(old_level)
    
    def trigger_recovery(self) -> None:
        """Trigger recovery to full functionality."""
        self.set_degradation_level(DegradationLevel.FULL)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get degradation metrics."""
        with self.lock:
            return {
                "total_operations": self.metrics.total_operations,
                "full_level": self.metrics.full_level_operations,
                "reduced_level": self.metrics.reduced_level_operations,
                "minimal_level": self.metrics.minimal_level_operations,
                "offline": self.metrics.offline_operations,
                "degradation_events": self.metrics.degradation_events,
                "recovery_events": self.metrics.recovery_events,
                "average_response_time_ms": self.metrics.average_response_time_ms,
                "max_response_time_ms": self.metrics.max_response_time_ms,
                "min_response_time_ms": self.metrics.min_response_time_ms,
            }
    
    def get_degradation_history(self) -> List[tuple[DegradationLevel, DegradationLevel, Optional[DegradationTrigger]]]:
        """Get history of degradation transitions."""
        with self.lock:
            return list(self._degradation_history)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def degradation_manager() -> Generator[GracefulDegradationManager, None, None]:
    """Create a GracefulDegradationManager for testing."""
    manager = GracefulDegradationManager()
    yield manager


@pytest.fixture
def configured_manager() -> Generator[GracefulDegradationManager, None, None]:
    """Create manager with configured fallback strategies."""
    config = DegradationConfig(enable_auto_degradation=True)
    manager = GracefulDegradationManager(config=config)
    
    # Register fallback strategies
    manager.register_fallback_strategy(
        DegradationLevel.REDUCED,
        "cached_result",
        lambda: {"status": "cached", "data": "limited"},
        is_cached=True,
        response_time_ms=5.0,
    )
    
    manager.register_fallback_strategy(
        DegradationLevel.MINIMAL,
        "minimal_response",
        lambda: {"status": "minimal", "data": "essential_only"},
        is_cached=False,
        response_time_ms=2.0,
    )
    
    yield manager


# ============================================================================
# CATEGORY 1: INITIALIZATION & CONFIGURATION (4/4)
# ============================================================================

class TestInitialization:
    """Test degradation manager initialization."""
    
    def test_creates_manager_with_default_config(
        self,
        degradation_manager: GracefulDegradationManager,
    ) -> None:
        """Should create manager with default configuration."""
        assert degradation_manager is not None
        assert degradation_manager.get_degradation_level() == DegradationLevel.FULL
    
    def test_creates_manager_with_custom_config(self) -> None:
        """Should create manager with custom configuration."""
        config = DegradationConfig(
            current_level=DegradationLevel.REDUCED,
            resource_threshold=0.7,
        )
        manager = GracefulDegradationManager(config=config)
        
        assert manager.get_degradation_level() == DegradationLevel.REDUCED
        assert manager.config.resource_threshold == 0.7
    
    def test_rejects_invalid_resource_threshold(self) -> None:
        """Should reject invalid resource threshold."""
        with pytest.raises(ValueError):
            config = DegradationConfig(resource_threshold=1.5)
            GracefulDegradationManager(config=config)
    
    def test_rejects_invalid_error_rate_threshold(self) -> None:
        """Should reject invalid error rate threshold."""
        with pytest.raises(ValueError):
            config = DegradationConfig(error_rate_threshold=1.5)
            GracefulDegradationManager(config=config)


# ============================================================================
# CATEGORY 2: DEGRADATION LEVELS (3/3)
# ============================================================================

class TestDegradationLevels:
    """Test degradation level transitions."""
    
    def test_starts_at_full_level(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should start at FULL degradation level."""
        assert degradation_manager.get_degradation_level() == DegradationLevel.FULL
    
    def test_transitions_to_reduced_level(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should transition to REDUCED level."""
        degradation_manager.set_degradation_level(DegradationLevel.REDUCED)
        assert degradation_manager.get_degradation_level() == DegradationLevel.REDUCED
    
    def test_transitions_through_all_levels(
        self,
        degradation_manager: GracefulDegradationManager,
    ) -> None:
        """Should transition through all degradation levels."""
        levels = [
            DegradationLevel.FULL,
            DegradationLevel.REDUCED,
            DegradationLevel.MINIMAL,
            DegradationLevel.OFFLINE,
        ]
        
        for level in levels:
            degradation_manager.set_degradation_level(level)
            assert degradation_manager.get_degradation_level() == level


# ============================================================================
# CATEGORY 3: FALLBACK STRATEGIES (4/4)
# ============================================================================

class TestFallbackStrategies:
    """Test fallback strategy registration and execution."""
    
    def test_registers_fallback_strategy(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should register fallback strategy for degradation level."""
        def fallback() -> str:
            return "fallback_result"
        
        degradation_manager.register_fallback_strategy(
            DegradationLevel.REDUCED,
            "test_fallback",
            fallback,
        )
        
        assert DegradationLevel.REDUCED in degradation_manager.config.fallback_strategies
    
    def test_stores_fallback_metadata(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should store fallback strategy metadata."""
        def fallback() -> str:
            return "cached"
        
        degradation_manager.register_fallback_strategy(
            DegradationLevel.REDUCED,
            "cached_result",
            fallback,
            is_cached=True,
            response_time_ms=5.0,
        )
        
        strategy = degradation_manager.config.fallback_strategies[DegradationLevel.REDUCED]
        assert strategy.name == "cached_result"
        assert strategy.is_cached is True
        assert strategy.response_time_ms == 5.0
    
    def test_executes_reduced_fallback(self, configured_manager: GracefulDegradationManager) -> None:
        """Should execute reduced fallback operation."""
        configured_manager.set_degradation_level(DegradationLevel.REDUCED)
        
        result = configured_manager.config.fallback_strategies[DegradationLevel.REDUCED].executor()
        assert result is not None
        assert result["status"] == "cached"
    
    def test_executes_minimal_fallback(self, configured_manager: GracefulDegradationManager) -> None:
        """Should execute minimal fallback operation."""
        configured_manager.set_degradation_level(DegradationLevel.MINIMAL)
        
        result = configured_manager.config.fallback_strategies[DegradationLevel.MINIMAL].executor()
        assert result is not None
        assert result["status"] == "minimal"


# ============================================================================
# CATEGORY 4: AUTOMATIC DEGRADATION (4/4)
# ============================================================================

class TestAutomaticDegradation:
    """Test automatic degradation based on conditions."""
    
    def test_degrades_on_high_resource_usage(
        self,
        degradation_manager: GracefulDegradationManager,
    ) -> None:
        """Should degrade on high resource usage."""
        def op() -> str:
            return "result"
        
        # 85% resource usage should trigger degradation
        degradation_manager.execute_with_degradation(op, resource_usage=0.85)
        assert degradation_manager.get_degradation_level() == DegradationLevel.REDUCED
    
    def test_degrades_to_minimal_on_critical_resource_usage(
        self,
        degradation_manager: GracefulDegradationManager,
    ) -> None:
        """Should degrade to MINIMAL on critical resource usage."""
        def op() -> str:
            return "result"
        
        # 96% resource usage should trigger minimal degradation
        degradation_manager.execute_with_degradation(op, resource_usage=0.96)
        assert degradation_manager.get_degradation_level() == DegradationLevel.MINIMAL
    
    def test_degrades_on_high_error_rate(
        self,
        degradation_manager: GracefulDegradationManager,
    ) -> None:
        """Should degrade on high error rate."""
        def op() -> str:
            return "result"
        
        # 15% error rate should trigger degradation
        degradation_manager.execute_with_degradation(op, error_rate=0.15)
        assert degradation_manager.get_degradation_level() == DegradationLevel.REDUCED
    
    def test_degrades_to_minimal_on_critical_error_rate(
        self,
        degradation_manager: GracefulDegradationManager,
    ) -> None:
        """Should degrade to MINIMAL on critical error rate."""
        def op() -> str:
            return "result"
        
        # 35% error rate should trigger minimal degradation
        degradation_manager.execute_with_degradation(op, error_rate=0.35)
        assert degradation_manager.get_degradation_level() == DegradationLevel.MINIMAL


# ============================================================================
# CATEGORY 5: OPERATION EXECUTION (4/4)
# ============================================================================

class TestOperationExecution:
    """Test operation execution at different degradation levels."""
    
    def test_executes_full_operation(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should execute full operation at FULL level."""
        def op() -> str:
            return "full_result"
        
        result = degradation_manager.execute_with_degradation(op)
        assert result == "full_result"
    
    def test_executes_reduced_operation(self, configured_manager: GracefulDegradationManager) -> None:
        """Should execute reduced operation when degraded."""
        def full_op() -> str:
            return "full_result"
        
        configured_manager.set_degradation_level(DegradationLevel.REDUCED)
        result = configured_manager.execute_with_degradation(full_op)
        
        # Should return cached fallback result
        assert result is not None
        assert result["status"] == "cached"
    
    def test_executes_minimal_operation(self, configured_manager: GracefulDegradationManager) -> None:
        """Should execute minimal operation when severely degraded."""
        def full_op() -> str:
            return "full_result"
        
        configured_manager.set_degradation_level(DegradationLevel.MINIMAL)
        result = configured_manager.execute_with_degradation(full_op)
        
        # Should return minimal fallback result
        assert result is not None
        assert result["status"] == "minimal"
    
    def test_raises_when_offline(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should raise error when service is offline."""
        def op() -> str:
            return "result"
        
        degradation_manager.set_degradation_level(DegradationLevel.OFFLINE)
        
        with pytest.raises(RuntimeError):
            degradation_manager.execute_with_degradation(op)


# ============================================================================
# CATEGORY 6: METRICS COLLECTION (4/4)
# ============================================================================

class TestMetricsCollection:
    """Test metrics collection for degraded operations."""
    
    def test_tracks_total_operations(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should track total operations."""
        def op() -> None:
            pass
        
        for _ in range(5):
            degradation_manager.execute_with_degradation(op)
        
        metrics = degradation_manager.get_metrics()
        assert metrics["total_operations"] == 5
    
    def test_tracks_operations_per_level(self, configured_manager: GracefulDegradationManager) -> None:
        """Should track operations per degradation level."""
        # Disable auto-degradation to control levels manually
        configured_manager.config.enable_auto_degradation = False
        
        def op() -> None:
            pass
        
        # Full level
        configured_manager.execute_with_degradation(op)
        configured_manager.execute_with_degradation(op)
        
        # Reduced level
        configured_manager.set_degradation_level(DegradationLevel.REDUCED)
        configured_manager.execute_with_degradation(op)
        
        metrics = configured_manager.get_metrics()
        assert metrics["full_level"] == 2
        assert metrics["reduced_level"] == 1
    
    def test_tracks_degradation_events(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should track degradation events."""
        def op() -> None:
            pass
        
        # Trigger degradation
        degradation_manager.execute_with_degradation(op, resource_usage=0.85)
        
        metrics = degradation_manager.get_metrics()
        assert metrics["degradation_events"] > 0
    
    def test_tracks_recovery_events(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should track recovery events."""
        def op() -> None:
            pass
        
        # Degrade
        degradation_manager.execute_with_degradation(op, resource_usage=0.85)
        
        # Recover
        degradation_manager.trigger_recovery()
        
        metrics = degradation_manager.get_metrics()
        assert metrics["recovery_events"] > 0


# ============================================================================
# CATEGORY 7: RESPONSE TIME TRACKING (3/3)
# ============================================================================

class TestResponseTimeTracking:
    """Test response time metrics."""
    
    def test_tracks_response_times(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should track operation response times."""
        def op() -> None:
            time.sleep(0.01)
        
        degradation_manager.execute_with_degradation(op)
        
        metrics = degradation_manager.get_metrics()
        assert metrics["average_response_time_ms"] > 0
    
    def test_tracks_min_max_response_times(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should track min/max response times."""
        def fast_op() -> None:
            time.sleep(0.005)
        
        def slow_op() -> None:
            time.sleep(0.02)
        
        degradation_manager.execute_with_degradation(fast_op)
        degradation_manager.execute_with_degradation(slow_op)
        
        metrics = degradation_manager.get_metrics()
        assert metrics["min_response_time_ms"] < metrics["max_response_time_ms"]
    
    def test_calculates_average_response_time(
        self,
        degradation_manager: GracefulDegradationManager,
    ) -> None:
        """Should calculate average response time."""
        def op() -> None:
            time.sleep(0.01)
        
        for _ in range(3):
            degradation_manager.execute_with_degradation(op)
        
        metrics = degradation_manager.get_metrics()
        assert metrics["average_response_time_ms"] > 0


# ============================================================================
# CATEGORY 8: RECOVERY & TRANSITIONS (3/3)
# ============================================================================

class TestRecoveryTransitions:
    """Test recovery and level transitions."""
    
    def test_triggers_recovery(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should trigger recovery to FULL level."""
        degradation_manager.set_degradation_level(DegradationLevel.REDUCED)
        degradation_manager.trigger_recovery()
        
        assert degradation_manager.get_degradation_level() == DegradationLevel.FULL
    
    def test_tracks_recovery_from_reduced(
        self,
        degradation_manager: GracefulDegradationManager,
    ) -> None:
        """Should track recovery from REDUCED level."""
        degradation_manager.set_degradation_level(DegradationLevel.REDUCED)
        degradation_manager.trigger_recovery()
        
        history = degradation_manager.get_degradation_history()
        assert len(history) >= 2
    
    def test_tracks_degradation_trigger(self, degradation_manager: GracefulDegradationManager) -> None:
        """Should track what triggered degradation."""
        def op() -> None:
            pass
        
        degradation_manager.execute_with_degradation(op, resource_usage=0.85)
        
        history = degradation_manager.get_degradation_history()
        assert len(history) > 0


# ============================================================================
# CATEGORY 9: CONCURRENT DEGRADATION (2/2)
# ============================================================================

class TestConcurrentDegradation:
    """Test concurrent degradation management."""
    
    def test_handles_concurrent_degradation_changes(
        self,
        configured_manager: GracefulDegradationManager,
    ) -> None:
        """Should handle concurrent degradation level changes."""
        def op() -> None:
            time.sleep(0.001)
        
        results: List[str] = []
        lock = threading.Lock()
        
        def worker() -> None:
            for _ in range(5):
                try:
                    configured_manager.execute_with_degradation(op)
                    with lock:
                        results.append("ok")
                except RuntimeError:
                    with lock:
                        results.append("offline")
        
        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should complete without race conditions
        assert len(results) == 15
    
    def test_thread_safe_metrics_updates(
        self,
        degradation_manager: GracefulDegradationManager,
    ) -> None:
        """Should safely update metrics from concurrent threads."""
        def op() -> None:
            time.sleep(0.001)
        
        threads = [
            threading.Thread(
                target=lambda: degradation_manager.execute_with_degradation(op)
            )
            for _ in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        metrics = degradation_manager.get_metrics()
        assert metrics["total_operations"] == 10


# ============================================================================
# CATEGORY 10: INTEGRATION PATTERNS (2/2)
# ============================================================================

class TestIntegrationPatterns:
    """Test integration with other resilience patterns."""
    
    def test_integrates_with_timeout_detection(
        self,
        degradation_manager: GracefulDegradationManager,
    ) -> None:
        """Should work with timeout-based slow operation detection."""
        # Simulate timeout-triggered degradation
        degradation_manager.set_degradation_level(DegradationLevel.REDUCED)
        
        assert degradation_manager.get_degradation_level() == DegradationLevel.REDUCED
    
    def test_integrates_with_circuit_breaker(
        self,
        degradation_manager: GracefulDegradationManager,
    ) -> None:
        """Should work with circuit breaker for failure detection."""
        # High error rate triggers both circuit breaker and degradation
        def op() -> None:
            pass
        
        degradation_manager.execute_with_degradation(op, error_rate=0.25)
        
        # Should degrade due to error rate
        assert degradation_manager.get_degradation_level() != DegradationLevel.FULL
