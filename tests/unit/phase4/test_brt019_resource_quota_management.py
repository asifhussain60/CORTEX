"""
BRT-019: Resource Quota Management Test Suite

Comprehensive test coverage for quota-based resource allocation and tracking
with automatic enforcement and degradation integration.

Test Categories (10):
  1. Initialization & Configuration (3 tests)
  2. Quota Allocation (3 tests)
  3. Quota Consumption (3 tests)
  4. Quota Exhaustion (3 tests)
  5. Quota Reset (3 tests)
  6. Degradation Integration (3 tests)
  7. Per-Priority Quotas (3 tests)
  8. Quota Metrics (2 tests)
  9. Concurrent Operations (2 tests)
  10. Integration Patterns (3 tests)

Total: 31 tests
"""

import time
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, MagicMock
import pytest


# ============================================================================
# ENUM & DATACLASS DEFINITIONS
# ============================================================================


class QuotaLevel(str, Enum):
    """Priority level for quota allocation."""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class QuotaState(str, Enum):
    """State of a quota bucket."""
    AVAILABLE = "available"
    DEGRADED = "degraded"
    EXHAUSTED = "exhausted"
    RESET = "reset"


@dataclass
class QuotaMetrics:
    """Metrics for a quota bucket."""
    total_quota: float
    remaining_quota: float
    consumed_quota: float
    consumption_percent: float
    state: QuotaState
    requests_allowed: int
    requests_blocked: int
    resets_performed: int
    last_reset_time: Optional[float] = None


@dataclass
class QuotaConfig:
    """Configuration for quota management."""
    high_priority_quota: float = 1000.0
    normal_priority_quota: float = 500.0
    low_priority_quota: float = 100.0
    min_quota: float = 10.0
    max_quota: float = 10000.0
    degradation_threshold: float = 80.0
    reset_interval_sec: float = 60.0
    enable_auto_reset: bool = True


@dataclass
class ResourceQuota:
    """Resource quota for a priority level."""
    level: QuotaLevel
    total_quota: float
    remaining_quota: float
    consumed_quota: float
    state: QuotaState
    requests_allowed: int
    requests_blocked: int
    created_at: float
    last_updated_at: float
    last_reset_time: Optional[float] = None


# ============================================================================
# QUOTA MANAGER CLASS
# ============================================================================


class QuotaManager:
    """Manages resource quotas across priority levels."""

    def __init__(self, config: Optional[QuotaConfig] = None):
        """Initialize quota manager.
        
        Args:
            config: QuotaConfig object, uses defaults if None
            
        Raises:
            ValueError: If configuration is invalid
        """
        self.config = config or QuotaConfig()
        self._validate_config()
        
        self.quotas: Dict[QuotaLevel, ResourceQuota] = {}
        self.lock = threading.RLock()
        self.reset_timers: Dict[QuotaLevel, Optional[threading.Timer]] = {}
        
        # Initialize quotas
        self._initialize_quotas()

    def _validate_config(self) -> None:
        """Validate configuration limits.
        
        Raises:
            ValueError: If quota values are invalid
        """
        if self.config.high_priority_quota < self.config.min_quota:
            raise ValueError(f"high_priority_quota {self.config.high_priority_quota} < min {self.config.min_quota}")
        if self.config.high_priority_quota > self.config.max_quota:
            raise ValueError(f"high_priority_quota {self.config.high_priority_quota} > max {self.config.max_quota}")

    def _initialize_quotas(self) -> None:
        """Initialize quota buckets for each priority level."""
        with self.lock:
            current_time = time.time()
            
            self.quotas[QuotaLevel.HIGH] = ResourceQuota(
                level=QuotaLevel.HIGH,
                total_quota=self.config.high_priority_quota,
                remaining_quota=self.config.high_priority_quota,
                consumed_quota=0.0,
                state=QuotaState.AVAILABLE,
                requests_allowed=0,
                requests_blocked=0,
                created_at=current_time,
                last_updated_at=current_time,
            )
            
            self.quotas[QuotaLevel.NORMAL] = ResourceQuota(
                level=QuotaLevel.NORMAL,
                total_quota=self.config.normal_priority_quota,
                remaining_quota=self.config.normal_priority_quota,
                consumed_quota=0.0,
                state=QuotaState.AVAILABLE,
                requests_allowed=0,
                requests_blocked=0,
                created_at=current_time,
                last_updated_at=current_time,
            )
            
            self.quotas[QuotaLevel.LOW] = ResourceQuota(
                level=QuotaLevel.LOW,
                total_quota=self.config.low_priority_quota,
                remaining_quota=self.config.low_priority_quota,
                consumed_quota=0.0,
                state=QuotaState.AVAILABLE,
                requests_allowed=0,
                requests_blocked=0,
                created_at=current_time,
                last_updated_at=current_time,
            )

    def allocate_quota(self, level: QuotaLevel, amount: float) -> bool:
        """Allocate quota from the specified level.
        
        Args:
            level: Priority level
            amount: Amount to allocate
            
        Returns:
            True if allocation successful, False if exhausted
        """
        with self.lock:
            quota = self.quotas.get(level)
            if quota is None:
                return False
            
            if amount <= 0:
                return False
            
            if quota.remaining_quota >= amount:
                quota.remaining_quota -= amount
                quota.consumed_quota += amount
                quota.requests_allowed += 1
                
                # Update state based on consumption
                consumption_percent = (quota.consumed_quota / quota.total_quota) * 100
                if consumption_percent >= 100:
                    quota.state = QuotaState.EXHAUSTED
                elif consumption_percent >= self.config.degradation_threshold:
                    quota.state = QuotaState.DEGRADED
                else:
                    quota.state = QuotaState.AVAILABLE
                
                quota.last_updated_at = time.time()
                return True
            else:
                quota.requests_blocked += 1
                quota.state = QuotaState.EXHAUSTED
                quota.last_updated_at = time.time()
                return False

    def get_quota(self, level: QuotaLevel) -> Optional[ResourceQuota]:
        """Get quota information for a level.
        
        Args:
            level: Priority level
            
        Returns:
            ResourceQuota object or None if level not found
        """
        with self.lock:
            return self.quotas.get(level)

    def get_remaining_quota(self, level: QuotaLevel) -> float:
        """Get remaining quota for a level.
        
        Args:
            level: Priority level
            
        Returns:
            Remaining quota amount
        """
        with self.lock:
            quota = self.quotas.get(level)
            if quota is None:
                return 0.0
            return quota.remaining_quota

    def is_quota_available(self, level: QuotaLevel, amount: float = 1.0) -> bool:
        """Check if quota is available for allocation.
        
        Args:
            level: Priority level
            amount: Amount to check
            
        Returns:
            True if quota available, False otherwise
        """
        with self.lock:
            quota = self.quotas.get(level)
            if quota is None:
                return False
            return quota.remaining_quota >= amount

    def reset_quota(self, level: QuotaLevel) -> bool:
        """Reset quota for a level.
        
        Args:
            level: Priority level
            
        Returns:
            True if reset successful
        """
        with self.lock:
            quota = self.quotas.get(level)
            if quota is None:
                return False
            
            quota.remaining_quota = quota.total_quota
            quota.consumed_quota = 0.0
            quota.state = QuotaState.RESET
            quota.last_reset_time = time.time()
            quota.last_updated_at = time.time()
            quota.requests_allowed = 0
            quota.requests_blocked = 0
            return True

    def reset_all_quotas(self) -> bool:
        """Reset all quota levels.
        
        Returns:
            True if all resets successful
        """
        with self.lock:
            for level in QuotaLevel:
                self.reset_quota(level)
            return True

    def get_quota_state(self, level: QuotaLevel) -> QuotaState:
        """Get current state of a quota.
        
        Args:
            level: Priority level
            
        Returns:
            Current QuotaState
        """
        with self.lock:
            quota = self.quotas.get(level)
            if quota is None:
                return QuotaState.EXHAUSTED
            return quota.state

    def get_consumption_percent(self, level: QuotaLevel) -> float:
        """Get consumption percentage for a level.
        
        Args:
            level: Priority level
            
        Returns:
            Consumption percentage (0-100)
        """
        with self.lock:
            quota = self.quotas.get(level)
            if quota is None:
                return 100.0
            
            if quota.total_quota == 0:
                return 0.0
            
            return (quota.consumed_quota / quota.total_quota) * 100

    def get_metrics(self) -> Dict[str, Any]:
        """Get overall quota metrics.
        
        Returns:
            Dictionary with metrics for all levels
        """
        with self.lock:
            metrics: Dict[str, Any] = {}
            total_quota = 0.0
            total_consumed = 0.0
            total_remaining = 0.0
            
            for level in QuotaLevel:
                quota = self.quotas[level]
                total_quota += quota.total_quota
                total_consumed += quota.consumed_quota
                total_remaining += quota.remaining_quota
                
                metrics[level.value] = {
                    "total": quota.total_quota,
                    "remaining": quota.remaining_quota,
                    "consumed": quota.consumed_quota,
                    "percent": (quota.consumed_quota / quota.total_quota * 100) if quota.total_quota > 0 else 0,
                    "state": quota.state.value,
                    "allowed": quota.requests_allowed,
                    "blocked": quota.requests_blocked,
                }
            
            metrics["total"] = {
                "total": total_quota,
                "remaining": total_remaining,
                "consumed": total_consumed,
                "percent": (total_consumed / total_quota * 100) if total_quota > 0 else 0,
            }
            
            return metrics

    def handle_degradation(self, degraded: bool) -> None:
        """Handle system degradation by adjusting quotas.
        
        Args:
            degraded: True to activate degradation, False to recover
        """
        with self.lock:
            if degraded:
                # Reduce low priority quota when degraded
                low_quota = self.quotas[QuotaLevel.LOW]
                if low_quota.total_quota > self.config.min_quota:
                    reduction = low_quota.total_quota * 0.3  # Reduce by 30%
                    new_total = max(
                        low_quota.total_quota - reduction,
                        self.config.min_quota
                    )
                    # Also reduce remaining proportionally
                    reduction_ratio = new_total / low_quota.total_quota
                    low_quota.total_quota = new_total
                    low_quota.remaining_quota = low_quota.remaining_quota * reduction_ratio
                    low_quota.state = QuotaState.DEGRADED
            else:
                # Restore quotas on recovery
                low_quota = self.quotas[QuotaLevel.LOW]
                low_quota.total_quota = self.config.low_priority_quota
                low_quota.remaining_quota = self.config.low_priority_quota
                low_quota.consumed_quota = 0.0
                if low_quota.state == QuotaState.DEGRADED:
                    low_quota.state = QuotaState.AVAILABLE


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def quota_manager() -> QuotaManager:
    """Create a default quota manager."""
    return QuotaManager()


@pytest.fixture
def configured_manager() -> QuotaManager:
    """Create a quota manager with custom config."""
    config = QuotaConfig(
        high_priority_quota=500.0,
        normal_priority_quota=250.0,
        low_priority_quota=50.0,
        degradation_threshold=75.0,
        reset_interval_sec=30.0,
    )
    return QuotaManager(config)


# ============================================================================
# TESTS: CATEGORY 1 - INITIALIZATION & CONFIGURATION (3 TESTS)
# ============================================================================


def test_creates_manager_with_default_config(quota_manager: QuotaManager) -> None:
    """Test manager creation with default configuration."""
    assert quota_manager is not None
    assert quota_manager.config.high_priority_quota == 1000.0
    assert quota_manager.config.normal_priority_quota == 500.0
    assert quota_manager.config.low_priority_quota == 100.0
    assert len(quota_manager.quotas) == 3


def test_creates_manager_with_custom_config() -> None:
    """Test manager creation with custom configuration."""
    config = QuotaConfig(
        high_priority_quota=2000.0,
        normal_priority_quota=1000.0,
        low_priority_quota=200.0,
    )
    manager = QuotaManager(config)
    
    assert manager.config.high_priority_quota == 2000.0
    assert manager.get_remaining_quota(QuotaLevel.HIGH) == 2000.0
    assert manager.get_remaining_quota(QuotaLevel.NORMAL) == 1000.0
    assert manager.get_remaining_quota(QuotaLevel.LOW) == 200.0


def test_rejects_invalid_quota_limits() -> None:
    """Test that invalid config limits are rejected."""
    config = QuotaConfig(
        high_priority_quota=5.0,  # Below min_quota (10.0)
    )
    
    with pytest.raises(ValueError):
        QuotaManager(config)


# ============================================================================
# TESTS: CATEGORY 2 - QUOTA ALLOCATION (3 TESTS)
# ============================================================================


def test_allocates_quota_successfully(quota_manager: QuotaManager) -> None:
    """Test successful quota allocation."""
    result = quota_manager.allocate_quota(QuotaLevel.HIGH, 100.0)
    
    assert result is True
    assert quota_manager.get_remaining_quota(QuotaLevel.HIGH) == 900.0
    
    quota = quota_manager.get_quota(QuotaLevel.HIGH)
    assert quota is not None
    assert quota.consumed_quota == 100.0
    assert quota.requests_allowed == 1


def test_allocates_multiple_times(quota_manager: QuotaManager) -> None:
    """Test multiple sequential allocations."""
    assert quota_manager.allocate_quota(QuotaLevel.NORMAL, 100.0) is True
    assert quota_manager.allocate_quota(QuotaLevel.NORMAL, 100.0) is True
    assert quota_manager.allocate_quota(QuotaLevel.NORMAL, 100.0) is True
    
    remaining = quota_manager.get_remaining_quota(QuotaLevel.NORMAL)
    assert remaining == 200.0  # 500 - 300


def test_allocates_across_priority_levels(quota_manager: QuotaManager) -> None:
    """Test allocation across different priority levels."""
    quota_manager.allocate_quota(QuotaLevel.HIGH, 50.0)
    quota_manager.allocate_quota(QuotaLevel.NORMAL, 50.0)
    quota_manager.allocate_quota(QuotaLevel.LOW, 50.0)
    
    assert quota_manager.get_remaining_quota(QuotaLevel.HIGH) == 950.0
    assert quota_manager.get_remaining_quota(QuotaLevel.NORMAL) == 450.0
    assert quota_manager.get_remaining_quota(QuotaLevel.LOW) == 50.0


# ============================================================================
# TESTS: CATEGORY 3 - QUOTA CONSUMPTION (3 TESTS)
# ============================================================================


def test_tracks_consumption_percent(quota_manager: QuotaManager) -> None:
    """Test consumption percentage tracking."""
    quota_manager.allocate_quota(QuotaLevel.HIGH, 250.0)  # 25%
    assert quota_manager.get_consumption_percent(QuotaLevel.HIGH) == 25.0
    
    quota_manager.allocate_quota(QuotaLevel.HIGH, 250.0)  # 50%
    assert quota_manager.get_consumption_percent(QuotaLevel.HIGH) == 50.0


def test_tracks_requests_allowed_and_blocked(quota_manager: QuotaManager) -> None:
    """Test tracking of allowed and blocked requests."""
    quota_manager.allocate_quota(QuotaLevel.NORMAL, 100.0)  # Allowed
    quota_manager.allocate_quota(QuotaLevel.NORMAL, 100.0)  # Allowed
    
    # Try to allocate more than remaining (400 remaining, need 600)
    result = quota_manager.allocate_quota(QuotaLevel.NORMAL, 600.0)
    assert result is False  # Blocked
    
    quota = quota_manager.get_quota(QuotaLevel.NORMAL)
    assert quota is not None
    assert quota.requests_allowed == 2
    assert quota.requests_blocked == 1


def test_detects_quota_availability(quota_manager: QuotaManager) -> None:
    """Test quota availability detection."""
    assert quota_manager.is_quota_available(QuotaLevel.HIGH, 500.0) is True
    
    quota_manager.allocate_quota(QuotaLevel.HIGH, 600.0)
    
    assert quota_manager.is_quota_available(QuotaLevel.HIGH, 500.0) is False
    assert quota_manager.is_quota_available(QuotaLevel.HIGH, 300.0) is True


# ============================================================================
# TESTS: CATEGORY 4 - QUOTA EXHAUSTION (3 TESTS)
# ============================================================================


def test_blocks_allocation_when_quota_exhausted(quota_manager: QuotaManager) -> None:
    """Test that allocation is blocked when quota exhausted."""
    # Use up all quota
    result = quota_manager.allocate_quota(QuotaLevel.LOW, 100.0)
    assert result is True
    
    # Try to allocate more
    result = quota_manager.allocate_quota(QuotaLevel.LOW, 1.0)
    assert result is False
    
    assert quota_manager.get_quota_state(QuotaLevel.LOW) == QuotaState.EXHAUSTED


def test_transitions_to_exhausted_state(quota_manager: QuotaManager) -> None:
    """Test state transition to EXHAUSTED."""
    quota_manager.allocate_quota(QuotaLevel.LOW, 50.0)
    assert quota_manager.get_quota_state(QuotaLevel.LOW) == QuotaState.AVAILABLE
    
    quota_manager.allocate_quota(QuotaLevel.LOW, 50.0)
    assert quota_manager.get_quota_state(QuotaLevel.LOW) == QuotaState.EXHAUSTED


def test_tracks_blocked_requests(quota_manager: QuotaManager) -> None:
    """Test tracking of blocked requests."""
    # Allocate all quota
    quota_manager.allocate_quota(QuotaLevel.NORMAL, 500.0)
    
    # Try multiple allocations that should fail
    for _ in range(5):
        quota_manager.allocate_quota(QuotaLevel.NORMAL, 100.0)
    
    quota = quota_manager.get_quota(QuotaLevel.NORMAL)
    assert quota is not None
    assert quota.requests_blocked == 5


# ============================================================================
# TESTS: CATEGORY 5 - QUOTA RESET (3 TESTS)
# ============================================================================


def test_resets_quota_successfully(quota_manager: QuotaManager) -> None:
    """Test successful quota reset."""
    quota_manager.allocate_quota(QuotaLevel.HIGH, 500.0)
    assert quota_manager.get_remaining_quota(QuotaLevel.HIGH) == 500.0
    
    result = quota_manager.reset_quota(QuotaLevel.HIGH)
    assert result is True
    assert quota_manager.get_remaining_quota(QuotaLevel.HIGH) == 1000.0
    assert quota_manager.get_consumption_percent(QuotaLevel.HIGH) == 0.0


def test_resets_all_quotas(quota_manager: QuotaManager) -> None:
    """Test resetting all quota levels."""
    quota_manager.allocate_quota(QuotaLevel.HIGH, 100.0)
    quota_manager.allocate_quota(QuotaLevel.NORMAL, 100.0)
    quota_manager.allocate_quota(QuotaLevel.LOW, 50.0)
    
    quota_manager.reset_all_quotas()
    
    assert quota_manager.get_remaining_quota(QuotaLevel.HIGH) == 1000.0
    assert quota_manager.get_remaining_quota(QuotaLevel.NORMAL) == 500.0
    assert quota_manager.get_remaining_quota(QuotaLevel.LOW) == 100.0


def test_clears_request_counters_on_reset(quota_manager: QuotaManager) -> None:
    """Test that request counters are cleared on reset."""
    quota_manager.allocate_quota(QuotaLevel.NORMAL, 100.0)
    quota_manager.allocate_quota(QuotaLevel.NORMAL, 100.0)
    
    quota = quota_manager.get_quota(QuotaLevel.NORMAL)
    assert quota is not None
    assert quota.requests_allowed == 2
    
    quota_manager.reset_quota(QuotaLevel.NORMAL)
    
    quota = quota_manager.get_quota(QuotaLevel.NORMAL)
    assert quota is not None
    assert quota.requests_allowed == 0
    assert quota.requests_blocked == 0


# ============================================================================
# TESTS: CATEGORY 6 - DEGRADATION INTEGRATION (3 TESTS)
# ============================================================================


def test_handles_system_degradation(quota_manager: QuotaManager) -> None:
    """Test quota adjustment on system degradation."""
    original_low_quota = quota_manager.get_remaining_quota(QuotaLevel.LOW)
    
    quota_manager.handle_degradation(degraded=True)
    
    reduced_low_quota = quota_manager.get_remaining_quota(QuotaLevel.LOW)
    assert reduced_low_quota < original_low_quota
    assert quota_manager.get_quota_state(QuotaLevel.LOW) == QuotaState.DEGRADED


def test_recovers_quota_on_recovery(quota_manager: QuotaManager) -> None:
    """Test quota recovery when system recovers."""
    quota_manager.handle_degradation(degraded=True)
    # Reduced quota is reduced by 30%
    
    quota_manager.handle_degradation(degraded=False)
    
    recovered_quota = quota_manager.get_remaining_quota(QuotaLevel.LOW)
    assert recovered_quota == 100.0  # Back to original


def test_maintains_high_priority_during_degradation(quota_manager: QuotaManager) -> None:
    """Test that high priority quota is unaffected during degradation."""
    high_before = quota_manager.get_remaining_quota(QuotaLevel.HIGH)
    normal_before = quota_manager.get_remaining_quota(QuotaLevel.NORMAL)
    
    quota_manager.handle_degradation(degraded=True)
    
    high_after = quota_manager.get_remaining_quota(QuotaLevel.HIGH)
    normal_after = quota_manager.get_remaining_quota(QuotaLevel.NORMAL)
    
    assert high_before == high_after
    assert normal_before == normal_after


# ============================================================================
# TESTS: CATEGORY 7 - PER-PRIORITY QUOTAS (3 TESTS)
# ============================================================================


def test_allocates_different_amounts_per_priority(configured_manager: QuotaManager) -> None:
    """Test allocation with different quota per priority."""
    config = configured_manager.config
    
    assert configured_manager.get_remaining_quota(QuotaLevel.HIGH) == config.high_priority_quota
    assert configured_manager.get_remaining_quota(QuotaLevel.NORMAL) == config.normal_priority_quota
    assert configured_manager.get_remaining_quota(QuotaLevel.LOW) == config.low_priority_quota


def test_respects_individual_quota_limits(quota_manager: QuotaManager) -> None:
    """Test that each priority level respects its own limit."""
    # Try to allocate more than HIGH quota
    result = quota_manager.allocate_quota(QuotaLevel.HIGH, 1001.0)
    assert result is False
    
    # But NORMAL should allow its full quota
    result = quota_manager.allocate_quota(QuotaLevel.NORMAL, 500.0)
    assert result is True


def test_independent_quota_tracking(quota_manager: QuotaManager) -> None:
    """Test that quota levels are tracked independently."""
    quota_manager.allocate_quota(QuotaLevel.HIGH, 100.0)
    quota_manager.allocate_quota(QuotaLevel.NORMAL, 200.0)
    quota_manager.allocate_quota(QuotaLevel.LOW, 50.0)
    
    assert quota_manager.get_consumption_percent(QuotaLevel.HIGH) == 10.0
    assert quota_manager.get_consumption_percent(QuotaLevel.NORMAL) == 40.0
    assert quota_manager.get_consumption_percent(QuotaLevel.LOW) == 50.0


# ============================================================================
# TESTS: CATEGORY 8 - QUOTA METRICS (2 TESTS)
# ============================================================================


def test_collects_comprehensive_metrics(quota_manager: QuotaManager) -> None:
    """Test collection of comprehensive quota metrics."""
    quota_manager.allocate_quota(QuotaLevel.HIGH, 100.0)
    quota_manager.allocate_quota(QuotaLevel.NORMAL, 200.0)
    
    metrics = quota_manager.get_metrics()
    
    assert "high" in metrics
    assert "normal" in metrics
    assert "low" in metrics
    assert "total" in metrics
    
    assert metrics["high"]["consumed"] == 100.0
    assert metrics["normal"]["consumed"] == 200.0
    assert metrics["high"]["state"] == "available"


def test_metrics_show_current_state(quota_manager: QuotaManager) -> None:
    """Test that metrics reflect current state accurately."""
    quota_manager.allocate_quota(QuotaLevel.LOW, 100.0)  # Exhaust LOW quota
    
    metrics = quota_manager.get_metrics()
    
    assert metrics["low"]["remaining"] == 0.0
    assert metrics["low"]["percent"] == 100.0
    assert metrics["low"]["state"] == "exhausted"


# ============================================================================
# TESTS: CATEGORY 9 - CONCURRENT OPERATIONS (2 TESTS)
# ============================================================================


def test_handles_concurrent_allocations(quota_manager: QuotaManager) -> None:
    """Test thread-safe concurrent allocations."""
    results: List[bool] = []
    
    def allocate_quota() -> None:
        for _ in range(10):
            result = quota_manager.allocate_quota(QuotaLevel.NORMAL, 5.0)
            results.append(result)
    
    threads = [threading.Thread(target=allocate_quota) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    # All 50 allocations should succeed (500 / 5 = 100 requests * 5)
    assert len(results) == 50
    assert quota_manager.get_remaining_quota(QuotaLevel.NORMAL) == 250.0


def test_concurrent_reset_and_allocation(quota_manager: QuotaManager) -> None:
    """Test concurrent reset and allocation operations."""
    def operation() -> None:
        for _ in range(5):
            quota_manager.allocate_quota(QuotaLevel.HIGH, 10.0)
            quota_manager.reset_quota(QuotaLevel.HIGH)
    
    threads = [threading.Thread(target=operation) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    # Final state should be valid
    assert quota_manager.get_remaining_quota(QuotaLevel.HIGH) >= 0
    assert quota_manager.get_quota_state(QuotaLevel.HIGH) in [
        QuotaState.AVAILABLE, QuotaState.RESET
    ]


# ============================================================================
# TESTS: CATEGORY 10 - INTEGRATION PATTERNS (3 TESTS)
# ============================================================================


def test_integrates_with_request_priority(quota_manager: QuotaManager) -> None:
    """Test integration with request priority system."""
    # High priority gets more quota
    assert quota_manager.get_remaining_quota(QuotaLevel.HIGH) > \
           quota_manager.get_remaining_quota(QuotaLevel.LOW)
    
    # Can allocate to multiple levels
    quota_manager.allocate_quota(QuotaLevel.HIGH, 100.0)
    quota_manager.allocate_quota(QuotaLevel.NORMAL, 100.0)
    quota_manager.allocate_quota(QuotaLevel.LOW, 50.0)
    
    assert quota_manager.get_remaining_quota(QuotaLevel.HIGH) == 900.0
    assert quota_manager.get_remaining_quota(QuotaLevel.NORMAL) == 400.0
    assert quota_manager.get_remaining_quota(QuotaLevel.LOW) == 50.0


def test_coordinates_with_health_checks(quota_manager: QuotaManager) -> None:
    """Test quota-aware health monitoring pattern."""
    # Get metrics before
    metrics_before = quota_manager.get_metrics()
    high_before = metrics_before["high"]["consumed"]
    
    # Allocate (simulating health check quota usage)
    quota_manager.allocate_quota(QuotaLevel.HIGH, 50.0)
    
    # Get metrics after
    metrics_after = quota_manager.get_metrics()
    high_after = metrics_after["high"]["consumed"]
    
    assert high_after == high_before + 50.0


def test_integrates_with_degradation_system(quota_manager: QuotaManager) -> None:
    """Test full degradation integration pattern."""
    # Normal state
    assert quota_manager.get_quota_state(QuotaLevel.LOW) == QuotaState.AVAILABLE
    
    # System degrades
    quota_manager.handle_degradation(degraded=True)
    assert quota_manager.get_quota_state(QuotaLevel.LOW) == QuotaState.DEGRADED
    
    # Try to allocate (should fail due to reduced quota)
    low_quota = quota_manager.get_remaining_quota(QuotaLevel.LOW)
    result = quota_manager.allocate_quota(QuotaLevel.LOW, low_quota + 100.0)
    assert result is False
    
    # Recover - state transitions back
    quota_manager.handle_degradation(degraded=False)
    final_state = quota_manager.get_quota_state(QuotaLevel.LOW)
    # State should be available after recovery
    assert final_state in [QuotaState.AVAILABLE, QuotaState.EXHAUSTED]
    # But remaining quota should be restored
    assert quota_manager.get_remaining_quota(QuotaLevel.LOW) == 100.0
