"""
Tests for LifecycleHookSystem (ENH-092 | Phase 53.3)

Tests automatic cleanup triggering on completions.

Author: Asif Hussain
Governance: CORE-008 (TDD), RED → GREEN → REFACTOR
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from typing import List

from cortex.orchestrators.core.lifecycle_hook_system import (
    LifecycleHookSystem,
    CompletionEvent,
    CompletionContext
)


@pytest.fixture
def mock_vacuum_orchestrator():
    """Mock VacuumOrchestrator for testing."""
    mock = Mock()
    mock.execute_vacuum = AsyncMock(return_value={"status": "success", "files_archived": 12})
    mock.archive_session = AsyncMock(return_value={"status": "success", "session_archived": True})
    return mock


@pytest.fixture
def hook_system(mock_vacuum_orchestrator):
    """Create LifecycleHookSystem with mock vacuum orchestrator."""
    return LifecycleHookSystem(vacuum_orchestrator=mock_vacuum_orchestrator)


@pytest.fixture
def hook_system_no_vacuum():
    """Create LifecycleHookSystem without vacuum orchestrator."""
    return LifecycleHookSystem(vacuum_orchestrator=None)


# RED: Test initialization
def test_lifecycle_hook_system_initialization(hook_system):
    """WHEN system initialized THEN hooks registry created for all event types."""
    assert len(hook_system._hooks) == 4
    assert CompletionEvent.WAVE_COMPLETE in hook_system._hooks
    assert CompletionEvent.PHASE_COMPLETE in hook_system._hooks
    assert CompletionEvent.STAGE_COMPLETE in hook_system._hooks
    assert CompletionEvent.SESSION_END in hook_system._hooks


def test_lifecycle_hook_system_default_hooks_registered(hook_system):
    """WHEN vacuum orchestrator provided THEN default hooks auto-registered."""
    # Should have 3 default hooks (wave, phase, session)
    assert len(hook_system._hooks[CompletionEvent.WAVE_COMPLETE]) == 1
    assert len(hook_system._hooks[CompletionEvent.PHASE_COMPLETE]) == 1
    assert len(hook_system._hooks[CompletionEvent.SESSION_END]) == 1
    assert len(hook_system._hooks[CompletionEvent.STAGE_COMPLETE]) == 0  # No default for stage


def test_lifecycle_hook_system_no_vacuum_no_defaults(hook_system_no_vacuum):
    """WHEN no vacuum orchestrator THEN no default hooks registered."""
    for event_type in CompletionEvent:
        assert len(hook_system_no_vacuum._hooks[event_type]) == 0


# RED: Test hook registration
def test_register_hook_adds_to_registry(hook_system_no_vacuum):
    """WHEN hook registered THEN appears in hooks registry."""
    def my_hook(ctx: CompletionContext):
        pass
    
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, my_hook)
    
    assert my_hook in hook_system_no_vacuum._hooks[CompletionEvent.WAVE_COMPLETE]


def test_register_hook_idempotent(hook_system_no_vacuum):
    """WHEN same hook registered twice THEN only added once."""
    def my_hook(ctx: CompletionContext):
        pass
    
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, my_hook)
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, my_hook)
    
    assert hook_system_no_vacuum._hooks[CompletionEvent.WAVE_COMPLETE].count(my_hook) == 1


def test_register_multiple_hooks_same_event(hook_system_no_vacuum):
    """WHEN multiple hooks registered for same event THEN all stored."""
    def hook1(ctx): pass
    def hook2(ctx): pass
    def hook3(ctx): pass
    
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, hook1)
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, hook2)
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, hook3)
    
    assert len(hook_system_no_vacuum._hooks[CompletionEvent.WAVE_COMPLETE]) == 3


# RED: Test hook unregistration
def test_unregister_hook_removes_from_registry(hook_system_no_vacuum):
    """WHEN hook unregistered THEN removed from registry."""
    def my_hook(ctx): pass
    
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, my_hook)
    result = hook_system_no_vacuum.unregister_hook(CompletionEvent.WAVE_COMPLETE, my_hook)
    
    assert result is True
    assert my_hook not in hook_system_no_vacuum._hooks[CompletionEvent.WAVE_COMPLETE]


def test_unregister_hook_not_registered_returns_false(hook_system_no_vacuum):
    """WHEN unregistering non-existent hook THEN returns False."""
    def my_hook(ctx): pass
    
    result = hook_system_no_vacuum.unregister_hook(CompletionEvent.WAVE_COMPLETE, my_hook)
    
    assert result is False


# RED: Test completion triggering
@pytest.mark.asyncio
async def test_trigger_completion_executes_registered_hooks(hook_system_no_vacuum):
    """WHEN completion triggered THEN all registered hooks executed."""
    execution_log: List[str] = []
    
    def hook1(ctx):
        execution_log.append(f"hook1:{ctx.entity_id}")
    
    def hook2(ctx):
        execution_log.append(f"hook2:{ctx.entity_id}")
    
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, hook1)
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, hook2)
    
    result = await hook_system_no_vacuum.trigger_completion(
        CompletionEvent.WAVE_COMPLETE,
        "wave-12"
    )
    
    assert len(execution_log) == 2
    assert "hook1:wave-12" in execution_log
    assert "hook2:wave-12" in execution_log
    assert result["hooks_executed"] == 2
    assert result["hooks_failed"] == 0


@pytest.mark.asyncio
async def test_trigger_completion_handles_async_hooks(hook_system_no_vacuum):
    """WHEN async hook registered THEN executed correctly."""
    execution_log: List[str] = []
    
    async def async_hook(ctx):
        await asyncio.sleep(0.01)  # Simulate async work
        execution_log.append(f"async_hook:{ctx.entity_id}")
    
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, async_hook)
    
    result = await hook_system_no_vacuum.trigger_completion(
        CompletionEvent.WAVE_COMPLETE,
        "wave-12"
    )
    
    assert len(execution_log) == 1
    assert "async_hook:wave-12" in execution_log
    assert result["hooks_executed"] == 1


@pytest.mark.asyncio
async def test_trigger_completion_tracks_failures(hook_system_no_vacuum):
    """WHEN hook raises exception THEN failure tracked but execution continues."""
    execution_log: List[str] = []
    
    def failing_hook(ctx):
        raise ValueError("Hook failed!")
    
    def success_hook(ctx):
        execution_log.append("success")
    
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, failing_hook)
    hook_system_no_vacuum.register_hook(CompletionEvent.WAVE_COMPLETE, success_hook)
    
    result = await hook_system_no_vacuum.trigger_completion(
        CompletionEvent.WAVE_COMPLETE,
        "wave-12"
    )
    
    assert result["hooks_executed"] == 1  # Only success_hook
    assert result["hooks_failed"] == 1
    assert "success" in execution_log


@pytest.mark.asyncio
async def test_trigger_completion_records_history(hook_system_no_vacuum):
    """WHEN completion triggered THEN added to execution history."""
    await hook_system_no_vacuum.trigger_completion(
        CompletionEvent.WAVE_COMPLETE,
        "wave-12",
        metadata={"test": "data"}
    )
    
    history = hook_system_no_vacuum.get_execution_history()
    
    assert len(history) == 1
    assert history[0].event_type == CompletionEvent.WAVE_COMPLETE
    assert history[0].entity_id == "wave-12"
    assert history[0].metadata == {"test": "data"}


# RED: Test execution history
@pytest.mark.asyncio
async def test_get_execution_history_returns_recent_first(hook_system_no_vacuum):
    """WHEN multiple completions triggered THEN history in reverse order."""
    await hook_system_no_vacuum.trigger_completion(CompletionEvent.WAVE_COMPLETE, "wave-1")
    await hook_system_no_vacuum.trigger_completion(CompletionEvent.WAVE_COMPLETE, "wave-2")
    await hook_system_no_vacuum.trigger_completion(CompletionEvent.WAVE_COMPLETE, "wave-3")
    
    history = hook_system_no_vacuum.get_execution_history()
    
    assert len(history) == 3
    assert history[0].entity_id == "wave-3"  # Most recent first
    assert history[1].entity_id == "wave-2"
    assert history[2].entity_id == "wave-1"


@pytest.mark.asyncio
async def test_get_execution_history_filters_by_event_type(hook_system_no_vacuum):
    """WHEN history filtered by event type THEN only matching events returned."""
    await hook_system_no_vacuum.trigger_completion(CompletionEvent.WAVE_COMPLETE, "wave-1")
    await hook_system_no_vacuum.trigger_completion(CompletionEvent.PHASE_COMPLETE, "phase-1")
    await hook_system_no_vacuum.trigger_completion(CompletionEvent.WAVE_COMPLETE, "wave-2")
    
    history = hook_system_no_vacuum.get_execution_history(
        event_type=CompletionEvent.WAVE_COMPLETE
    )
    
    assert len(history) == 2
    assert all(ctx.event_type == CompletionEvent.WAVE_COMPLETE for ctx in history)


@pytest.mark.asyncio
async def test_get_execution_history_respects_limit(hook_system_no_vacuum):
    """WHEN limit specified THEN only that many entries returned."""
    for i in range(10):
        await hook_system_no_vacuum.trigger_completion(
            CompletionEvent.WAVE_COMPLETE,
            f"wave-{i}"
        )
    
    history = hook_system_no_vacuum.get_execution_history(limit=5)
    
    assert len(history) == 5
    assert history[0].entity_id == "wave-9"  # Most recent


# RED: Test default vacuum integration
@pytest.mark.asyncio
async def test_wave_complete_triggers_full_vacuum(hook_system, mock_vacuum_orchestrator):
    """WHEN wave completes THEN full vacuum triggered."""
    result = await hook_system.trigger_completion(
        CompletionEvent.WAVE_COMPLETE,
        "wave-12"
    )
    
    mock_vacuum_orchestrator.execute_vacuum.assert_called_once_with(
        mode="AUTO",
        trigger_source="lifecycle_hook:wave-12"
    )
    assert result["hooks_executed"] == 1


@pytest.mark.asyncio
async def test_phase_complete_triggers_targeted_vacuum(hook_system, mock_vacuum_orchestrator):
    """WHEN phase completes THEN targeted vacuum triggered."""
    result = await hook_system.trigger_completion(
        CompletionEvent.PHASE_COMPLETE,
        "phase-53"
    )
    
    mock_vacuum_orchestrator.execute_vacuum.assert_called_once_with(
        mode="TARGETED",
        scope="phase-53",
        trigger_source="lifecycle_hook:phase-53"
    )
    assert result["hooks_executed"] == 1


@pytest.mark.asyncio
async def test_session_end_triggers_archive(hook_system, mock_vacuum_orchestrator):
    """WHEN session ends THEN session archive triggered."""
    result = await hook_system.trigger_completion(
        CompletionEvent.SESSION_END,
        "session-abc123"
    )
    
    mock_vacuum_orchestrator.archive_session.assert_called_once_with(
        session_id="session-abc123",
        trigger_source="lifecycle_hook:session_end"
    )
    assert result["hooks_executed"] == 1


@pytest.mark.asyncio
async def test_vacuum_failure_does_not_block(hook_system, mock_vacuum_orchestrator):
    """WHEN vacuum fails THEN error logged but execution continues."""
    mock_vacuum_orchestrator.execute_vacuum.side_effect = Exception("Vacuum failed!")
    
    result = await hook_system.trigger_completion(
        CompletionEvent.WAVE_COMPLETE,
        "wave-12"
    )
    
    # Hook executed but failed
    assert result["hooks_failed"] == 1
    assert result["hooks_executed"] == 0
