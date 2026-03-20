"""Unit tests for Phase M21 bridge components.

CORE-008: tests first for new runtime bridge surfaces.
"""

from __future__ import annotations

import pytest

from cortex.core.registry.ac_marker_bridge import ACMarkerBridge
from cortex.core.registry.skill_bridge import SkillBridge
from cortex.core.registry.skill_executor import SkillExecutor
from cortex.core.session_bridge import SessionBridge


def test_skill_executor_register_and_execute() -> None:
    """SkillExecutor executes a registered skill."""
    executor = SkillExecutor()
    executor.register_skill("echo", lambda payload: {"payload": payload})

    result = executor.execute_skill("echo", {"x": 1})

    assert result == {"payload": {"x": 1}}


def test_skill_bridge_delegates_to_executor() -> None:
    """SkillBridge delegates invocation through SkillExecutor."""
    executor = SkillExecutor()
    bridge = SkillBridge(executor=executor)
    executor.register_skill("sum", lambda payload: payload["a"] + payload["b"])

    assert bridge.invoke("sum", {"a": 2, "b": 3}) == 5


def test_ac_marker_bridge_emits_paired_markers() -> None:
    """ACMarkerBridge emits AC_START and AC_COMPLETE with canonical IDs."""
    bridge = ACMarkerBridge(domain="M21")

    start_marker = bridge.emit_start(sequence="001")
    complete_marker = bridge.emit_complete(sequence="001")

    assert start_marker.startswith("AC_START: AC-M21-001")
    assert complete_marker.startswith("AC_COMPLETE: AC-M21-001")


def test_session_bridge_store_and_retrieve() -> None:
    """SessionBridge stores and retrieves values by session key."""
    bridge = SessionBridge()
    bridge.set_value("session-1", "last_audit", "ok")

    assert bridge.get_value("session-1", "last_audit") == "ok"
    assert bridge.get_value("session-1", "missing") is None


def test_skill_executor_raises_for_unknown_skill() -> None:
    """Unknown skills raise KeyError."""
    executor = SkillExecutor()

    with pytest.raises(KeyError):
        executor.execute_skill("does-not-exist", {})
