"""
Comprehensive test suite for BRT-018: Cascading Timeout Management Pattern.

Tests context-based timeout management enabling timeouts to cascade through
nested operation calls, preventing timeout overflow and ensuring parent timeouts
constrain child operations, critical for systems with multi-level call hierarchies.

The cascading timeout pattern provides:
- Context-based timeout tracking with parent-child relationships
- Automatic timeout inheritance from parent to child contexts
- Remaining time calculation accounting for elapsed time
- Timeout expiration detection and enforcement
- Metrics tracking for timeout cascade chains

AC-INFRA-003-12: Cascading timeout management with inheritance
"""

import threading
import time
from typing import List, Generator, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

import pytest


# ============================================================================
# CASCADING TIMEOUT IMPLEMENTATION FOR TESTING
# ============================================================================

class TimeoutState(str, Enum):
    """State of a timeout context."""
    ACTIVE = "active"
    EXPIRED = "expired"
    COMPLETED = "completed"


@dataclass
class TimeoutMetrics:
    """Metrics for timeout tracking."""
    
    total_timeouts_created: int = 0
    cascaded_timeouts: int = 0
    expired_timeouts: int = 0
    completed_timeouts: int = 0
    total_elapsed_ms: float = 0.0


@dataclass
class TimeoutConfig:
    """Configuration for timeout management."""
    
    enable_cascading: bool = True
    warn_threshold_percent: float = 80.0  # Warn at 80% elapsed
    min_timeout_ms: float = 10.0
    max_timeout_ms: float = 300000.0


class TimeoutContext:
    """Represents a timeout scope for an operation."""
    
    def __init__(
        self,
        timeout_ms: float,
        parent_context: Optional["TimeoutContext"] = None,
        context_id: str = "",
    ) -> None:
        """Initialize timeout context."""
        self.context_id = context_id
        self.timeout_ms = timeout_ms
        self.parent_context = parent_context
        self.state = TimeoutState.ACTIVE
        self.start_time = time.time()
        self.child_contexts: List["TimeoutContext"] = []
        self._lock = threading.Lock()
        
        # Calculate actual timeout considering parent
        if parent_context is not None and parent_context.get_remaining_ms() > 0:
            parent_remaining = parent_context.get_remaining_ms()
            self.actual_timeout_ms = min(timeout_ms, parent_remaining)
        else:
            self.actual_timeout_ms = timeout_ms
        
        # Register with parent
        if parent_context is not None:
            with parent_context._lock:
                parent_context.child_contexts.append(self)
    
    def get_elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return (time.time() - self.start_time) * 1000
    
    def get_remaining_ms(self) -> float:
        """Get remaining time in milliseconds."""
        elapsed = self.get_elapsed_ms()
        remaining = self.actual_timeout_ms - elapsed
        return max(0, remaining)
    
    def is_expired(self) -> bool:
        """Check if timeout has expired."""
        if self.state != TimeoutState.ACTIVE:
            return self.state == TimeoutState.EXPIRED
        
        if self.get_remaining_ms() <= 0:
            with self._lock:
                if self.state == TimeoutState.ACTIVE:
                    self.state = TimeoutState.EXPIRED
            return True
        
        return False
    
    def is_warning_threshold(self) -> bool:
        """Check if elapsed time exceeds warning threshold (80%)."""
        elapsed_percent = (self.get_elapsed_ms() / self.actual_timeout_ms) * 100
        return elapsed_percent >= 80.0
    
    def mark_completed(self) -> None:
        """Mark context as completed successfully."""
        with self._lock:
            if self.state == TimeoutState.ACTIVE:
                self.state = TimeoutState.COMPLETED
    
    def get_state(self) -> TimeoutState:
        """Get current state."""
        if self.is_expired():
            return TimeoutState.EXPIRED
        return self.state
    
    def create_child(
        self,
        child_timeout_ms: float,
        child_id: str = "",
    ) -> "TimeoutContext":
        """Create a child timeout context."""
        return TimeoutContext(
            timeout_ms=child_timeout_ms,
            parent_context=self,
            context_id=child_id,
        )
    
    def get_depth(self) -> int:
        """Get nesting depth (0 for root)."""
        depth = 0
        current = self.parent_context
        while current is not None:
            depth += 1
            current = current.parent_context
        return depth
    
    def get_chain(self) -> List["TimeoutContext"]:
        """Get timeout chain from root to this context."""
        chain: List[TimeoutContext] = []
        current: Optional[TimeoutContext] = self
        while current is not None:
            chain.insert(0, current)
            current = current.parent_context
        return chain


@dataclass
class CascadeMetrics:
    """Metrics for cascade operation."""
    
    chain_depth: int = 0
    max_child_timeout_ms: float = 0.0
    inherited_timeout_ms: float = 0.0
    safety_margin_ms: float = 0.0


class CascadingTimeoutManager:
    """Manages cascading timeout contexts."""
    
    def __init__(self, config: Optional[TimeoutConfig] = None) -> None:
        """Initialize timeout manager."""
        self.config = config or TimeoutConfig()
        self.metrics = TimeoutMetrics()
        self.lock = threading.Lock()
        self._active_contexts: List[TimeoutContext] = []
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration."""
        if self.config.min_timeout_ms <= 0:
            raise ValueError("min_timeout_ms must be > 0")
        if self.config.max_timeout_ms <= 0:
            raise ValueError("max_timeout_ms must be > 0")
        if self.config.max_timeout_ms < self.config.min_timeout_ms:
            raise ValueError("max_timeout_ms must be >= min_timeout_ms")
        if not (0 < self.config.warn_threshold_percent <= 100):
            raise ValueError("warn_threshold_percent must be between 0 and 100")
    
    def create_timeout(
        self,
        timeout_ms: float,
        context_id: str = "",
    ) -> TimeoutContext:
        """Create a new timeout context."""
        with self.lock:
            # Clamp timeout to configured limits
            clamped_timeout = max(
                self.config.min_timeout_ms,
                min(timeout_ms, self.config.max_timeout_ms),
            )
            
            context = TimeoutContext(
                timeout_ms=clamped_timeout,
                parent_context=None,
                context_id=context_id,
            )
            
            self._active_contexts.append(context)
            self.metrics.total_timeouts_created += 1
            
            return context
    
    def cascade_timeout(
        self,
        parent_context: TimeoutContext,
        child_timeout_ms: float,
        child_id: str = "",
    ) -> TimeoutContext:
        """Create a cascaded child timeout from parent context."""
        with self.lock:
            # Clamp child timeout
            clamped_timeout = max(
                self.config.min_timeout_ms,
                min(child_timeout_ms, self.config.max_timeout_ms),
            )
            
            # Create child context (will inherit parent's remaining time if less)
            child_context = parent_context.create_child(
                child_timeout_ms=clamped_timeout,
                child_id=child_id,
            )
            
            self._active_contexts.append(child_context)
            self.metrics.cascaded_timeouts += 1
            
            return child_context
    
    def check_timeout(self, context: TimeoutContext) -> bool:
        """Check if timeout has expired."""
        if context.is_expired():
            with self.lock:
                self.metrics.expired_timeouts += 1
            return True
        return False
    
    def complete_timeout(self, context: TimeoutContext) -> None:
        """Mark timeout context as completed successfully."""
        context.mark_completed()
        with self.lock:
            self.metrics.completed_timeouts += 1
    
    def get_cascade_metrics(self, context: TimeoutContext) -> CascadeMetrics:
        """Get metrics for a cascaded timeout."""
        chain = context.get_chain()
        
        # Find max child timeout in chain
        max_child_timeout = 0.0
        for ctx in chain:
            if ctx.actual_timeout_ms > max_child_timeout:
                max_child_timeout = ctx.actual_timeout_ms
        
        # Calculate inherited timeout (minimum in chain)
        inherited_timeout = min((ctx.actual_timeout_ms for ctx in chain), default=0.0)
        
        # Safety margin (how much less than parent)
        safety_margin = 0.0
        if context.parent_context is not None:
            safety_margin = context.parent_context.actual_timeout_ms - context.actual_timeout_ms
        
        return CascadeMetrics(
            chain_depth=len(chain),
            max_child_timeout_ms=max_child_timeout,
            inherited_timeout_ms=inherited_timeout,
            safety_margin_ms=safety_margin,
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get timeout management metrics."""
        with self.lock:
            return {
                "total_timeouts_created": self.metrics.total_timeouts_created,
                "cascaded_timeouts": self.metrics.cascaded_timeouts,
                "expired_timeouts": self.metrics.expired_timeouts,
                "completed_timeouts": self.metrics.completed_timeouts,
                "active_contexts": len(self._active_contexts),
            }
    
    def cleanup_context(self, context: TimeoutContext) -> None:
        """Remove context from tracking."""
        with self.lock:
            if context in self._active_contexts:
                self._active_contexts.remove(context)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def timeout_manager() -> Generator[CascadingTimeoutManager, None, None]:
    """Create a CascadingTimeoutManager for testing."""
    manager = CascadingTimeoutManager()
    yield manager


@pytest.fixture
def configured_manager() -> Generator[CascadingTimeoutManager, None, None]:
    """Create manager with custom configuration."""
    config = TimeoutConfig(
        enable_cascading=True,
        warn_threshold_percent=75.0,
        min_timeout_ms=50.0,
        max_timeout_ms=10000.0,
    )
    manager = CascadingTimeoutManager(config=config)
    yield manager


# ============================================================================
# CATEGORY 1: INITIALIZATION & CONFIGURATION (3/3)
# ============================================================================

class TestInitialization:
    """Test timeout manager initialization."""
    
    def test_creates_manager_with_default_config(
        self,
        timeout_manager: CascadingTimeoutManager,
    ) -> None:
        """Should create manager with default configuration."""
        assert timeout_manager is not None
        assert timeout_manager.config.enable_cascading is True
        assert timeout_manager.config.warn_threshold_percent == 80.0
    
    def test_creates_manager_with_custom_config(self) -> None:
        """Should create manager with custom configuration."""
        config = TimeoutConfig(
            enable_cascading=False,
            warn_threshold_percent=90.0,
        )
        manager = CascadingTimeoutManager(config=config)
        
        assert manager.config.enable_cascading is False
        assert manager.config.warn_threshold_percent == 90.0
    
    def test_rejects_invalid_timeout_limits(self) -> None:
        """Should reject invalid timeout limits."""
        with pytest.raises(ValueError):
            config = TimeoutConfig(min_timeout_ms=-1.0)
            CascadingTimeoutManager(config=config)


# ============================================================================
# CATEGORY 2: TIMEOUT CONTEXT CREATION (3/3)
# ============================================================================

class TestTimeoutContextCreation:
    """Test timeout context creation."""
    
    def test_creates_timeout_context(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should create timeout context."""
        context = timeout_manager.create_timeout(1000.0, context_id="op1")
        
        assert context is not None
        assert context.context_id == "op1"
        assert context.actual_timeout_ms == 1000.0
    
    def test_clamps_timeout_to_max_limit(
        self,
        configured_manager: CascadingTimeoutManager,
    ) -> None:
        """Should clamp timeout to configured maximum."""
        context = configured_manager.create_timeout(50000.0)
        
        # Should be clamped to max_timeout_ms (10000.0)
        assert context.actual_timeout_ms == 10000.0
    
    def test_tracks_created_timeouts(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should track created timeouts."""
        timeout_manager.create_timeout(1000.0)
        timeout_manager.create_timeout(2000.0)
        
        metrics = timeout_manager.get_metrics()
        assert metrics["total_timeouts_created"] == 2


# ============================================================================
# CATEGORY 3: CASCADING TIMEOUTS (4/4)
# ============================================================================

class TestCascadingTimeouts:
    """Test cascading timeout functionality."""
    
    def test_cascades_child_timeout_from_parent(
        self,
        timeout_manager: CascadingTimeoutManager,
    ) -> None:
        """Should cascade child timeout from parent context."""
        parent = timeout_manager.create_timeout(5000.0, context_id="parent")
        child = timeout_manager.cascade_timeout(parent, 2000.0, child_id="child")
        
        assert child.parent_context is parent
        assert child.get_depth() == 1
    
    def test_child_inherits_less_timeout_than_parent(
        self,
        timeout_manager: CascadingTimeoutManager,
    ) -> None:
        """Should limit child timeout to parent's remaining time."""
        parent = timeout_manager.create_timeout(1000.0)
        
        # Request 2000ms child timeout, but parent only has 1000ms
        child = timeout_manager.cascade_timeout(parent, 2000.0)
        
        # Child should inherit parent's remaining time (or less)
        assert child.actual_timeout_ms <= parent.actual_timeout_ms
    
    def test_tracks_cascaded_timeouts(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should track cascaded timeouts."""
        parent = timeout_manager.create_timeout(5000.0)
        
        timeout_manager.cascade_timeout(parent, 2000.0)
        timeout_manager.cascade_timeout(parent, 1500.0)
        
        metrics = timeout_manager.get_metrics()
        assert metrics["cascaded_timeouts"] == 2
    
    def test_creates_timeout_chain(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should create chain of cascaded timeouts."""
        level1 = timeout_manager.create_timeout(5000.0)
        level2 = timeout_manager.cascade_timeout(level1, 4000.0)
        level3 = timeout_manager.cascade_timeout(level2, 3000.0)
        
        chain = level3.get_chain()
        assert len(chain) == 3
        assert chain[0] is level1
        assert chain[1] is level2
        assert chain[2] is level3


# ============================================================================
# CATEGORY 4: TIMEOUT EXPIRATION (4/4)
# ============================================================================

class TestTimeoutExpiration:
    """Test timeout expiration detection."""
    
    def test_detects_expired_timeout(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should detect expired timeout."""
        context = timeout_manager.create_timeout(10.0)  # 10ms timeout
        
        # Wait for timeout to expire
        time.sleep(0.05)  # 50ms
        
        assert context.is_expired() is True
    
    def test_detects_active_timeout(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should detect active (non-expired) timeout."""
        context = timeout_manager.create_timeout(5000.0)  # 5 second timeout
        
        # Should not be expired immediately
        assert context.is_expired() is False
    
    def test_cascaded_child_expires_with_parent(
        self,
        timeout_manager: CascadingTimeoutManager,
    ) -> None:
        """Should cascade expiration from parent to child."""
        parent = timeout_manager.create_timeout(10.0)  # 10ms
        child = timeout_manager.cascade_timeout(parent, 1000.0)
        
        # Wait for parent timeout
        time.sleep(0.05)
        
        # Both should be expired
        assert parent.is_expired() is True
        assert child.is_expired() is True  # Child inherits parent's timeout
    
    def test_tracks_expired_timeouts(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should track expired timeouts."""
        context = timeout_manager.create_timeout(10.0)
        
        time.sleep(0.05)
        timeout_manager.check_timeout(context)
        
        metrics = timeout_manager.get_metrics()
        assert metrics["expired_timeouts"] >= 1


# ============================================================================
# CATEGORY 5: REMAINING TIME CALCULATION (3/3)
# ============================================================================

class TestRemainingTimeCalculation:
    """Test remaining time calculation."""
    
    def test_calculates_remaining_time(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should calculate remaining time."""
        context = timeout_manager.create_timeout(100.0)
        
        remaining = context.get_remaining_ms()
        assert 0 < remaining <= 100.0
    
    def test_remaining_time_decreases_over_time(
        self,
        timeout_manager: CascadingTimeoutManager,
    ) -> None:
        """Should decrease remaining time as time passes."""
        context = timeout_manager.create_timeout(1000.0)
        
        remaining1 = context.get_remaining_ms()
        time.sleep(0.05)
        remaining2 = context.get_remaining_ms()
        
        assert remaining2 < remaining1
    
    def test_remaining_time_never_negative(
        self,
        timeout_manager: CascadingTimeoutManager,
    ) -> None:
        """Should never return negative remaining time."""
        context = timeout_manager.create_timeout(10.0)
        
        time.sleep(0.05)
        remaining = context.get_remaining_ms()
        
        assert remaining >= 0


# ============================================================================
# CATEGORY 6: TIMEOUT STATE MANAGEMENT (3/3)
# ============================================================================

class TestTimeoutStateManagement:
    """Test timeout state transitions."""
    
    def test_starts_in_active_state(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should start in ACTIVE state."""
        context = timeout_manager.create_timeout(5000.0)
        
        assert context.get_state() == TimeoutState.ACTIVE
    
    def test_transitions_to_completed(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should transition to COMPLETED state."""
        context = timeout_manager.create_timeout(5000.0)
        
        context.mark_completed()
        assert context.get_state() == TimeoutState.COMPLETED
    
    def test_transitions_to_expired(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should transition to EXPIRED state."""
        context = timeout_manager.create_timeout(10.0)
        
        time.sleep(0.05)
        assert context.get_state() == TimeoutState.EXPIRED


# ============================================================================
# CATEGORY 7: WARNING THRESHOLD (2/2)
# ============================================================================

class TestWarningThreshold:
    """Test warning threshold detection."""
    
    def test_detects_warning_threshold(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should detect when elapsed time exceeds warning threshold."""
        # 10ms timeout, 80% warning threshold = 8ms
        context = timeout_manager.create_timeout(10.0)
        
        time.sleep(0.009)  # Wait 9ms (exceeds 8ms threshold)
        
        assert context.is_warning_threshold() is True
    
    def test_does_not_warn_below_threshold(
        self,
        timeout_manager: CascadingTimeoutManager,
    ) -> None:
        """Should not warn below threshold."""
        # 5000ms timeout, 80% warning = 4000ms
        context = timeout_manager.create_timeout(5000.0)
        
        # Check immediately (way below threshold)
        assert context.is_warning_threshold() is False


# ============================================================================
# CATEGORY 8: CASCADE METRICS (2/2)
# ============================================================================

class TestCascadeMetrics:
    """Test cascade metrics collection."""
    
    def test_calculates_chain_depth(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should calculate timeout chain depth."""
        level1 = timeout_manager.create_timeout(5000.0)
        level2 = timeout_manager.cascade_timeout(level1, 4000.0)
        level3 = timeout_manager.cascade_timeout(level2, 3000.0)
        
        metrics = timeout_manager.get_cascade_metrics(level3)
        assert metrics.chain_depth == 3
    
    def test_calculates_safety_margin(self, timeout_manager: CascadingTimeoutManager) -> None:
        """Should calculate safety margin between parent and child."""
        parent = timeout_manager.create_timeout(5000.0)
        child = timeout_manager.cascade_timeout(parent, 3000.0)
        
        metrics = timeout_manager.get_cascade_metrics(child)
        # Safety margin should be positive (parent > child)
        assert metrics.safety_margin_ms >= 0


# ============================================================================
# CATEGORY 9: CONCURRENT TIMEOUT OPERATIONS (2/2)
# ============================================================================

class TestConcurrentTimeoutOperations:
    """Test concurrent timeout operations."""
    
    def test_handles_concurrent_timeout_creation(
        self,
        configured_manager: CascadingTimeoutManager,
    ) -> None:
        """Should handle concurrent timeout creation."""
        contexts: List[TimeoutContext] = []
        lock = threading.Lock()
        
        def worker(timeout_ms: float) -> None:
            context = configured_manager.create_timeout(timeout_ms)
            with lock:
                contexts.append(context)
        
        threads = [
            threading.Thread(target=worker, args=(1000 + i * 100,))
            for i in range(10)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(contexts) == 10
    
    def test_thread_safe_cascading(self, configured_manager: CascadingTimeoutManager) -> None:
        """Should safely cascade timeouts from multiple threads."""
        parent = configured_manager.create_timeout(5000.0)
        children: List[TimeoutContext] = []
        lock = threading.Lock()
        
        def worker(child_id: int) -> None:
            child = configured_manager.cascade_timeout(
                parent,
                2000.0,
                child_id=f"child{child_id}",
            )
            with lock:
                children.append(child)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(children) == 5


# ============================================================================
# CATEGORY 10: INTEGRATION PATTERNS (3/3)
# ============================================================================

class TestIntegrationPatterns:
    """Test integration with other resilience patterns."""
    
    def test_integrates_with_request_priority(
        self,
        timeout_manager: CascadingTimeoutManager,
    ) -> None:
        """Should integrate with request prioritization."""
        # High priority: shorter timeout
        high_priority_timeout = timeout_manager.create_timeout(5000.0, context_id="high")
        
        # Low priority: longer timeout but cascaded from high
        low_priority_timeout = timeout_manager.cascade_timeout(
            high_priority_timeout,
            10000.0,
            child_id="low",
        )
        
        # Low priority should inherit high priority timeout
        assert low_priority_timeout.actual_timeout_ms <= high_priority_timeout.actual_timeout_ms
    
    def test_handles_retry_within_timeout_budget(
        self,
        timeout_manager: CascadingTimeoutManager,
    ) -> None:
        """Should enable retry strategy within timeout budget."""
        total_timeout = timeout_manager.create_timeout(1000.0)
        
        # First attempt gets half the budget
        attempt1 = timeout_manager.cascade_timeout(total_timeout, 400.0)
        
        # Second attempt gets remaining budget
        attempt2 = timeout_manager.cascade_timeout(total_timeout, 400.0)
        
        # Both should respect total timeout
        assert attempt1.actual_timeout_ms <= 1000.0
        assert attempt2.actual_timeout_ms <= 1000.0
    
    def test_coordinates_cascading_with_health_checks(
        self,
        timeout_manager: CascadingTimeoutManager,
    ) -> None:
        """Should coordinate cascading timeouts with health checks."""
        # Operation timeout
        operation_timeout = timeout_manager.create_timeout(5000.0)
        
        # Health check within operation
        health_check_timeout = timeout_manager.cascade_timeout(
            operation_timeout,
            100.0,
            child_id="health_check",
        )
        
        # Health check should complete quickly
        assert health_check_timeout.actual_timeout_ms <= 100.0
        
        # Main operation should have remaining time
        assert operation_timeout.get_remaining_ms() > 0
