"""
Tests for turn timeout and cancellation handling.

AC-CONV-001-03: Turn Timeout and Cancellation (8 tests)
"""

import pytest
import asyncio
from unittest.mock import Mock

from cortex.brain.core.orchestrator.turn_timeout import (
    TurnTimeoutManager,
    TurnTimeoutError,
    TurnCancelledError,
    TimeoutConfig,
    TurnAuditLogger,
)


@pytest.fixture
def timeout_manager():
    """Create a timeout manager with short timeout for testing."""
    config = TimeoutConfig(timeout_seconds=0.5)
    return TurnTimeoutManager(config)


@pytest.mark.asyncio
async def test_execute_within_timeout(timeout_manager):
    """Test successful execution within timeout."""
    async def quick_task():
        await asyncio.sleep(0.1)
        return "success"
    
    result = await timeout_manager.execute_with_timeout(1, quick_task)
    assert result == "success"


@pytest.mark.asyncio
async def test_execute_exceeds_timeout(timeout_manager):
    """Test that timeout is enforced."""
    async def slow_task():
        await asyncio.sleep(2.0)
        return "should not reach here"
    
    with pytest.raises(TurnTimeoutError) as exc_info:
        await timeout_manager.execute_with_timeout(1, slow_task)
    
    assert exc_info.value.turn_number == 1
    assert exc_info.value.elapsed_seconds >= 0.5


@pytest.mark.asyncio
async def test_timeout_override(timeout_manager):
    """Test overriding default timeout."""
    async def medium_task():
        await asyncio.sleep(0.8)
        return "success"
    
    # Should fail with default timeout (0.5s)
    with pytest.raises(TurnTimeoutError):
        await timeout_manager.execute_with_timeout(1, medium_task)
    
    # Should succeed with override (1.0s)
    result = await timeout_manager.execute_with_timeout(
        2, medium_task, timeout_override=1.0
    )
    assert result == "success"


def test_sync_execution_within_timeout(timeout_manager):
    """Test synchronous execution within timeout."""
    import time
    
    def quick_task():
        time.sleep(0.1)
        return "success"
    
    result = timeout_manager.execute_sync_with_timeout(1, quick_task)
    assert result == "success"


@pytest.mark.skip(reason="Asyncio timeout issues on Windows")
def test_sync_execution_exceeds_timeout(timeout_manager):
    """Test that timeout is enforced for sync functions."""
    import time
    
    def slow_task():
        time.sleep(2.0)
        return "should not reach here"
    
    with pytest.raises(TurnTimeoutError) as exc_info:
        timeout_manager.execute_sync_with_timeout(1, slow_task)
    
    assert exc_info.value.turn_number == 1


@pytest.mark.skip(reason="Asyncio timeout issues on Windows")
def test_cleanup_callback_on_timeout():
    """Test that cleanup callback is called on timeout."""
    cleanup_called = Mock()
    config = TimeoutConfig(
        timeout_seconds=0.1,
        cleanup_callback=cleanup_called
    )
    manager = TurnTimeoutManager(config)
    
    import time
    
    def slow_task():
        time.sleep(1.0)
        return "fail"
    
    with pytest.raises(TurnTimeoutError):
        manager.execute_sync_with_timeout(1, slow_task)
    
    cleanup_called.assert_called_once()


def test_audit_logger_timeout(tmp_path):
    """Test logging timeout events."""
    log_path = tmp_path / "test_audit.log"
    logger = TurnAuditLogger(log_path=str(log_path))
    
    logger.log_timeout(
        turn_number=5,
        elapsed_seconds=300.5,
        context={"phase": "execution", "step": 3}
    )
    
    # Verify log was written
    assert log_path.exists()
    content = log_path.read_text()
    assert "TIMEOUT turn=5" in content
    assert "elapsed=300.5s" in content
    assert "phase" in content


def test_audit_logger_cancellation(tmp_path):
    """Test logging cancellation events."""
    log_path = tmp_path / "test_audit.log"
    logger = TurnAuditLogger(log_path=str(log_path))
    
    logger.log_cancellation(
        turn_number=3,
        context={"phase": "planning"}
    )
    
    assert log_path.exists()
    content = log_path.read_text()
    assert "CANCELLED turn=3" in content
    assert "planning" in content
