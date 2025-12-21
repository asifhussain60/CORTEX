"""
Test suite for ExecutionModeManager

Author: Asif Hussain
Version: 1.0
Created: December 21, 2025

RED Phase: These tests are expected to PASS with the minimal implementation
"""

import pytest
from datetime import datetime, timedelta

from src.orchestration_4_0.execution.execution_mode import ExecutionMode
from src.orchestration_4_0.execution.execution_mode_manager import (
    ExecutionModeManager,
    ModeSelector,
    ModeEscalator,
    UserProfile,
    User,
    Operation,
    Execution,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def new_user():
    """Create a new user with no experience"""
    return User(
        user_id="new_user_123",
        completed_operations=0,
        successful_operations=0,
        days_since_first_use=0,
        first_used_at=datetime.now()
    )


@pytest.fixture
def intermediate_user():
    """Create an intermediate user"""
    return User(
        user_id="intermediate_user_456",
        completed_operations=50,
        successful_operations=45,
        days_since_first_use=15,
        first_used_at=datetime.now() - timedelta(days=15)
    )


@pytest.fixture
def expert_user():
    """Create an expert user"""
    return User(
        user_id="expert_user_789",
        completed_operations=200,
        successful_operations=190,
        days_since_first_use=60,
        first_used_at=datetime.now() - timedelta(days=60)
    )


@pytest.fixture
def low_risk_operation():
    """Create a low-risk operation (cleanup)"""
    return Operation(
        name="cleanup_workspace",
        category="maintenance",
        estimated_duration=60,
        requires_validation=True
    )


@pytest.fixture
def high_risk_operation():
    """Create a high-risk operation (deploy to production)"""
    return Operation(
        name="deploy_production",
        category="deployment",
        estimated_duration=300,
        requires_validation=True
    )


@pytest.fixture
def mode_selector():
    """Create ModeSelector instance"""
    return ModeSelector()


@pytest.fixture
def mode_escalator():
    """Create ModeEscalator instance"""
    return ModeEscalator()


# ============================================================================
# Core Tests (RED Phase)
# ============================================================================

def test_mode_selector_calculates_risk_score(mode_selector, low_risk_operation, high_risk_operation):
    """
    Test risk scoring for different operation types
    
    Expected:
    - cleanup operations: low risk (0.1)
    - deploy_production operations: high risk (0.9)
    """
    low_risk_score = mode_selector.calculate_risk_score(low_risk_operation)
    high_risk_score = mode_selector.calculate_risk_score(high_risk_operation)
    
    assert low_risk_score == 0.1, "Cleanup should have low risk score"
    assert high_risk_score == 0.9, "Deploy production should have high risk score"
    assert low_risk_score < high_risk_score, "Low risk should be less than high risk"


def test_mode_selector_gets_user_experience(mode_selector, new_user, expert_user):
    """
    Test user experience level calculation
    
    Expected:
    - new users: 0.0 experience
    - expert users: ~1.0 experience
    """
    new_user_experience = mode_selector.get_user_experience_level(new_user)
    expert_user_experience = mode_selector.get_user_experience_level(expert_user)
    
    assert new_user_experience == 0.0, "New user should have 0.0 experience"
    assert expert_user_experience >= 0.9, "Expert user should have high experience"
    assert new_user_experience < expert_user_experience, "New user experience < expert"


def test_mode_selection_for_new_user(mode_selector, new_user, low_risk_operation, high_risk_operation):
    """
    Test mode selection for new users
    
    Expected:
    - New users ALWAYS get HUMAN_IN_LOOP regardless of operation risk
    """
    mode_low_risk = mode_selector.select_mode(low_risk_operation, new_user)
    mode_high_risk = mode_selector.select_mode(high_risk_operation, new_user)
    
    assert mode_low_risk == ExecutionMode.HUMAN_IN_LOOP, "New user + low risk = human-in-loop"
    assert mode_high_risk == ExecutionMode.HUMAN_IN_LOOP, "New user + high risk = human-in-loop"


def test_mode_selection_for_high_risk_operation(mode_selector, expert_user, high_risk_operation):
    """
    Test mode selection for high-risk operations
    
    Expected:
    - High-risk operations ALWAYS use SUPERVISED mode, even for experts
    """
    mode = mode_selector.select_mode(high_risk_operation, expert_user)
    
    assert mode == ExecutionMode.SUPERVISED, "High-risk operation should be supervised even for experts"


def test_mode_selection_for_experienced_user_low_risk(mode_selector, expert_user, low_risk_operation):
    """
    Test mode selection for experienced user + low-risk operation
    
    Expected:
    - Experienced users + low risk = AUTONOMOUS mode
    """
    mode = mode_selector.select_mode(low_risk_operation, expert_user)
    
    assert mode == ExecutionMode.AUTONOMOUS, "Expert + low risk = autonomous"


def test_escalation_after_3_failures(mode_escalator):
    """
    Test escalation trigger after 3 consecutive failures
    
    Expected:
    - should_escalate returns True after failure_count >= 3
    """
    execution_0_failures = Execution(
        operation=Operation("test", "test", 60),
        mode=ExecutionMode.AUTONOMOUS,
        failure_count=0
    )
    execution_3_failures = Execution(
        operation=Operation("test", "test", 60),
        mode=ExecutionMode.AUTONOMOUS,
        failure_count=3
    )
    
    assert not mode_escalator.should_escalate(execution_0_failures), "Should not escalate with 0 failures"
    assert mode_escalator.should_escalate(execution_3_failures), "Should escalate after 3 failures"


def test_escalation_path(mode_escalator):
    """
    Test escalation path through modes
    
    Expected escalation path:
    AUTONOMOUS → SUPERVISED → HUMAN_IN_LOOP → HUMAN_IN_LOOP (can't escalate further)
    """
    escalated_from_autonomous = mode_escalator.escalate_mode(ExecutionMode.AUTONOMOUS)
    escalated_from_supervised = mode_escalator.escalate_mode(ExecutionMode.SUPERVISED)
    escalated_from_human = mode_escalator.escalate_mode(ExecutionMode.HUMAN_IN_LOOP)
    
    assert escalated_from_autonomous == ExecutionMode.SUPERVISED, "AUTONOMOUS should escalate to SUPERVISED"
    assert escalated_from_supervised == ExecutionMode.HUMAN_IN_LOOP, "SUPERVISED should escalate to HUMAN_IN_LOOP"
    assert escalated_from_human == ExecutionMode.HUMAN_IN_LOOP, "HUMAN_IN_LOOP can't escalate further"


def test_execution_mode_manager_integration():
    """
    End-to-end test with ExecutionModeManager
    
    Expected:
    - Manager successfully selects mode
    - Mode can be overridden via config
    - User profile tracking works
    """
    config = {}
    user_profile = UserProfile("test_user")
    manager = ExecutionModeManager(config, user_profile)
    
    operation = Operation("cleanup", "maintenance", 60)
    
    # Get recommended mode
    mode = manager.get_mode_for_operation(operation)
    assert mode in [ExecutionMode.HUMAN_IN_LOOP, ExecutionMode.SUPERVISED, ExecutionMode.AUTONOMOUS]
    
    # Test config override
    config["force_mode"] = "autonomous"
    forced_mode = manager.get_mode_for_operation(operation)
    assert forced_mode == ExecutionMode.AUTONOMOUS, "Config should override mode selection"


# ============================================================================
# Edge Case Tests
# ============================================================================

def test_mode_selector_with_unknown_operation(mode_selector, expert_user):
    """
    Test mode selection with unknown operation type
    
    Expected:
    - Unknown operations should default to medium risk (0.5)
    - Should return SUPERVISED mode for safety
    """
    unknown_op = Operation("mystery_operation", "unknown", 100)
    risk = mode_selector.calculate_risk_score(unknown_op)
    mode = mode_selector.select_mode(unknown_op, expert_user)
    
    assert risk == 0.5, "Unknown operation should have medium risk"
    assert mode == ExecutionMode.SUPERVISED, "Unknown operation should use supervised mode"


def test_user_profile_creates_new_user():
    """
    Test UserProfile creates new user if not found
    
    Expected:
    - New user has 0 operations, 0 days active
    - Success rate defaults to 1.0
    """
    user_profile = UserProfile("brand_new_user")
    user = user_profile.get_user()
    
    assert user.completed_operations == 0
    assert user.successful_operations == 0
    assert user.days_since_first_use == 0
    assert user.success_rate == 1.0


def test_user_profile_updates_stats():
    """
    Test UserProfile updates operation statistics
    
    Expected:
    - completed_operations increments
    - successful_operations increments on success only
    """
    user_profile = UserProfile("test_user_stats")
    
    # Initial state: new user
    user = user_profile.get_user()
    assert user.completed_operations == 0
    assert user.successful_operations == 0
    
    # Simulate successful operation
    user_profile.update_operation_stats("test_op", success=True)
    user_after_success = user_profile.get_user()
    
    assert user_after_success.completed_operations == 1
    assert user_after_success.successful_operations == 1
    
    # Simulate failed operation
    user_profile.update_operation_stats("test_op_fail", success=False)
    user_after_failure = user_profile.get_user()
    
    assert user_after_failure.completed_operations == 2
    assert user_after_failure.successful_operations == 1  # No increment


def test_escalation_message_format(mode_escalator):
    """
    Test escalation message format
    
    Expected:
    - Message contains both old and new modes
    - Message is user-friendly
    """
    message = mode_escalator.get_escalation_message(
        ExecutionMode.AUTONOMOUS,
        ExecutionMode.SUPERVISED
    )
    
    assert "autonomous" in message.lower()
    assert "supervised" in message.lower()
    assert "⚠️" in message  # Warning emoji
    assert str(mode_escalator.MAX_RETRIES) in message


# ============================================================================
# Performance Tests
# ============================================================================

def test_mode_selection_performance(mode_selector, expert_user, low_risk_operation):
    """
    Test mode selection performance
    
    Expected:
    - Mode selection should complete in <10ms
    """
    import time
    
    start = time.perf_counter()
    result = mode_selector.select_mode(low_risk_operation, expert_user)
    duration_ms = (time.perf_counter() - start) * 1000
    
    assert result in [ExecutionMode.HUMAN_IN_LOOP, ExecutionMode.SUPERVISED, ExecutionMode.AUTONOMOUS]
    assert duration_ms < 10, f"Mode selection took {duration_ms:.2f}ms, expected <10ms"


def test_risk_calculation_performance(mode_selector, high_risk_operation):
    """
    Test risk calculation performance
    
    Expected:
    - Risk calculation should complete in <5ms
    """
    import time
    
    start = time.perf_counter()
    result = mode_selector.calculate_risk_score(high_risk_operation)
    duration_ms = (time.perf_counter() - start) * 1000
    
    assert 0.0 <= result <= 1.0
    assert duration_ms < 5, f"Risk calculation took {duration_ms:.2f}ms, expected <5ms"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
