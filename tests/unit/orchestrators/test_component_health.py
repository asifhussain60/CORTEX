"""
Tests for component health tracking and initialization status.

AC-REM-004-01: Explicit Initialization Status API (8 tests)
AC-REM-004-02: Component Health Checks (12 tests)
AC-REM-004-03: Degradation Mode Visibility (6 tests)
"""

import pytest

from cortex.orchestrators.core.component_health import (
    ComponentHealthTracker,
    ComponentStatus,
    ComponentType,
)


@pytest.fixture
def health_tracker():
    """Create fresh health tracker."""
    return ComponentHealthTracker()


# AC-REM-004-01: Initialization Status API Tests

def test_register_component(health_tracker):
    """Test registering a component."""
    health_tracker.register_component("TestComponent", ComponentType.OPTIONAL)
    
    status = health_tracker.get_initialization_status("TestComponent")
    assert len(status) == 1
    assert status[0].component_name == "TestComponent"
    assert not status[0].initialized


def test_mark_component_initialized_success(health_tracker):
    """Test marking component as initialized successfully."""
    health_tracker.register_component("TestComponent", ComponentType.OPTIONAL)
    health_tracker.mark_initialized("TestComponent", success=True)
    
    status = health_tracker.get_initialization_status("TestComponent")[0]
    assert status.initialized
    assert not status.degraded


def test_mark_component_initialized_failure(health_tracker):
    """Test marking component as failed."""
    health_tracker.register_component("TestComponent", ComponentType.OPTIONAL)
    health_tracker.mark_initialized(
        "TestComponent",
        success=False,
        error_message="Connection timeout"
    )
    
    status = health_tracker.get_initialization_status("TestComponent")[0]
    assert not status.initialized
    assert status.degraded
    assert status.error_message == "Connection timeout"


def test_get_all_component_statuses(health_tracker):
    """Test getting all component statuses."""
    health_tracker.register_component("Component1", ComponentType.CRITICAL)
    health_tracker.register_component("Component2", ComponentType.OPTIONAL)
    
    statuses = health_tracker.get_initialization_status()
    assert len(statuses) == 2


def test_critical_vs_optional_classification(health_tracker):
    """Test CRITICAL vs OPTIONAL classification."""
    health_tracker.register_component("CriticalComp", ComponentType.CRITICAL)
    health_tracker.register_component("OptionalComp", ComponentType.OPTIONAL)
    
    critical_status = health_tracker.get_initialization_status("CriticalComp")[0]
    optional_status = health_tracker.get_initialization_status("OptionalComp")[0]
    
    assert critical_status.required
    assert not optional_status.required


def test_get_status_nonexistent_component(health_tracker):
    """Test getting status for component that doesn't exist."""
    status = health_tracker.get_initialization_status("NonExistent")
    assert len(status) == 0


def test_mark_initialized_nonexistent_component(health_tracker):
    """Test marking nonexistent component (should handle gracefully)."""
    # Should not raise exception
    health_tracker.mark_initialized("NonExistent", success=True)


def test_component_status_structure(health_tracker):
    """Test ComponentStatus dataclass structure."""
    health_tracker.register_component("TestComp", ComponentType.CRITICAL)
    health_tracker.mark_initialized("TestComp", success=False, error_message="Test error")
    
    status = health_tracker.get_initialization_status("TestComp")[0]
    
    assert status.component_name == "TestComp"
    assert not status.initialized
    assert status.required
    assert status.degraded
    assert status.error_message == "Test error"
    assert status.component_type == ComponentType.CRITICAL


# AC-REM-004-02: Health Check Tests

def test_is_ready_all_critical_initialized(health_tracker):
    """Test is_ready when all CRITICAL components initialized."""
    health_tracker.register_component("Critical1", ComponentType.CRITICAL)
    health_tracker.register_component("Critical2", ComponentType.CRITICAL)
    health_tracker.register_component("Optional1", ComponentType.OPTIONAL)
    
    health_tracker.mark_initialized("Critical1", success=True)
    health_tracker.mark_initialized("Critical2", success=True)
    health_tracker.mark_initialized("Optional1", success=False)  # Optional can fail
    
    assert health_tracker.is_ready()


def test_is_ready_critical_component_failed(health_tracker):
    """Test is_ready when CRITICAL component failed."""
    health_tracker.register_component("Critical1", ComponentType.CRITICAL)
    health_tracker.mark_initialized("Critical1", success=False)
    
    assert not health_tracker.is_ready()


def test_is_live_always_true(health_tracker):
    """Test is_live always returns True."""
    assert health_tracker.is_live()


def test_health_summary_all_healthy(health_tracker):
    """Test health summary when all components healthy."""
    health_tracker.register_component("Comp1", ComponentType.CRITICAL)
    health_tracker.register_component("Comp2", ComponentType.OPTIONAL)
    
    health_tracker.mark_initialized("Comp1", success=True)
    health_tracker.mark_initialized("Comp2", success=True)
    
    summary = health_tracker.get_health_summary()
    
    assert summary["ready"]
    assert summary["live"]
    assert summary["total_components"] == 2
    assert summary["initialized"] == 2
    assert summary["degraded"] == 0
    assert summary["critical_failed"] == 0
    assert summary["health_percentage"] == 100.0


def test_health_summary_with_degradation(health_tracker):
    """Test health summary with degraded components."""
    health_tracker.register_component("Critical1", ComponentType.CRITICAL)
    health_tracker.register_component("Optional1", ComponentType.OPTIONAL)
    health_tracker.register_component("Optional2", ComponentType.OPTIONAL)
    
    health_tracker.mark_initialized("Critical1", success=True)
    health_tracker.mark_initialized("Optional1", success=False)
    health_tracker.mark_initialized("Optional2", success=True)
    
    summary = health_tracker.get_health_summary()
    
    assert summary["ready"]  # Still ready (critical OK)
    assert summary["live"]
    assert summary["total_components"] == 3
    assert summary["initialized"] == 2
    assert summary["degraded"] == 1
    assert summary["critical_failed"] == 0
    assert summary["health_percentage"] == pytest.approx(66.67, 0.1)


def test_health_summary_critical_failure(health_tracker):
    """Test health summary with critical failure."""
    health_tracker.register_component("Critical1", ComponentType.CRITICAL)
    health_tracker.mark_initialized("Critical1", success=False)
    
    summary = health_tracker.get_health_summary()
    
    assert not summary["ready"]
    assert summary["critical_failed"] == 1


def test_health_percentage_calculation(health_tracker):
    """Test health percentage calculation."""
    for i in range(10):
        health_tracker.register_component(f"Comp{i}", ComponentType.OPTIONAL)
    
    # Initialize 7 out of 10
    for i in range(7):
        health_tracker.mark_initialized(f"Comp{i}", success=True)
    
    summary = health_tracker.get_health_summary()
    assert summary["health_percentage"] == 70.0


def test_health_summary_empty_tracker(health_tracker):
    """Test health summary with no components."""
    summary = health_tracker.get_health_summary()
    
    assert summary["ready"]  # No critical components to fail
    assert summary["live"]
    assert summary["total_components"] == 0
    assert summary["health_percentage"] == 0


def test_multiple_critical_components(health_tracker):
    """Test readiness with multiple critical components."""
    for i in range(5):
        health_tracker.register_component(f"Critical{i}", ComponentType.CRITICAL)
    
    # Initialize all but one
    for i in range(4):
        health_tracker.mark_initialized(f"Critical{i}", success=True)
    
    assert not health_tracker.is_ready()
    
    # Initialize last one
    health_tracker.mark_initialized("Critical4", success=True)
    assert health_tracker.is_ready()


def test_degradation_tracking(health_tracker):
    """Test tracking degraded components."""
    health_tracker.register_component("Comp1", ComponentType.OPTIONAL)
    health_tracker.register_component("Comp2", ComponentType.OPTIONAL)
    health_tracker.register_component("Comp3", ComponentType.OPTIONAL)
    
    health_tracker.mark_initialized("Comp1", success=True)
    health_tracker.mark_initialized("Comp2", success=False, error_message="Error 1")
    health_tracker.mark_initialized("Comp3", success=False, error_message="Error 2")
    
    summary = health_tracker.get_health_summary()
    assert summary["degraded"] == 2


def test_reinitialize_component(health_tracker):
    """Test reinitializing a component (recovery scenario)."""
    health_tracker.register_component("Comp1", ComponentType.CRITICAL)
    
    # First attempt fails
    health_tracker.mark_initialized("Comp1", success=False, error_message="Timeout")
    assert not health_tracker.is_ready()
    
    # Second attempt succeeds (recovery)
    health_tracker.mark_initialized("Comp1", success=True)
    assert health_tracker.is_ready()


# AC-REM-004-03: Degradation Visibility Tests

def test_degraded_flag_on_failure(health_tracker):
    """Test degraded flag is set on failure."""
    health_tracker.register_component("Comp1", ComponentType.OPTIONAL)
    health_tracker.mark_initialized("Comp1", success=False)
    
    status = health_tracker.get_initialization_status("Comp1")[0]
    assert status.degraded


def test_degraded_flag_clear_on_success(health_tracker):
    """Test degraded flag is clear on success."""
    health_tracker.register_component("Comp1", ComponentType.OPTIONAL)
    health_tracker.mark_initialized("Comp1", success=True)
    
    status = health_tracker.get_initialization_status("Comp1")[0]
    assert not status.degraded


def test_error_message_captured(health_tracker):
    """Test error message is captured."""
    health_tracker.register_component("Comp1", ComponentType.OPTIONAL)
    health_tracker.mark_initialized(
        "Comp1",
        success=False,
        error_message="Database connection refused"
    )
    
    status = health_tracker.get_initialization_status("Comp1")[0]
    assert status.error_message == "Database connection refused"


def test_degradation_summary_in_health(health_tracker):
    """Test degradation is included in health summary."""
    health_tracker.register_component("Comp1", ComponentType.OPTIONAL)
    health_tracker.register_component("Comp2", ComponentType.OPTIONAL)
    
    health_tracker.mark_initialized("Comp1", success=False)
    health_tracker.mark_initialized("Comp2", success=False)
    
    summary = health_tracker.get_health_summary()
    assert summary["degraded"] == 2


def test_optional_degradation_not_blocking(health_tracker):
    """Test that optional component degradation doesn't block readiness."""
    health_tracker.register_component("Critical1", ComponentType.CRITICAL)
    health_tracker.register_component("Optional1", ComponentType.OPTIONAL)
    
    health_tracker.mark_initialized("Critical1", success=True)
    health_tracker.mark_initialized("Optional1", success=False, error_message="Degraded")
    
    # System should be ready despite optional degradation
    assert health_tracker.is_ready()
    
    # But degradation should be visible
    status = health_tracker.get_initialization_status("Optional1")[0]
    assert status.degraded


def test_mixed_health_visibility(health_tracker):
    """Test visibility of mixed health states."""
    health_tracker.register_component("Critical1", ComponentType.CRITICAL)
    health_tracker.register_component("Critical2", ComponentType.CRITICAL)
    health_tracker.register_component("Optional1", ComponentType.OPTIONAL)
    health_tracker.register_component("Optional2", ComponentType.OPTIONAL)
    
    health_tracker.mark_initialized("Critical1", success=True)
    health_tracker.mark_initialized("Critical2", success=True)
    health_tracker.mark_initialized("Optional1", success=True)
    health_tracker.mark_initialized("Optional2", success=False, error_message="Minor issue")
    
    summary = health_tracker.get_health_summary()
    
    assert summary["ready"]  # All critical OK
    assert summary["initialized"] == 3
    assert summary["degraded"] == 1
    assert summary["critical_failed"] == 0
