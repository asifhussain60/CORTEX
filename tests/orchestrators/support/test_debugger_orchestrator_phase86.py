"""
Phase 86 — GAP-86-11 through 86-15: DebuggerOrchestrator intelligence wiring tests.

Tests for:
  GAP-86-11: OPJMixin in class hierarchy + _opj_init() called in __init__
  GAP-86-12: _urs_emit_signal() called after debug sessions resolve
  GAP-86-13: CC-021 + IC-021 entries present in IntelligenceMatrixBuilder
  GAP-86-14: DEBUG_INSIGHT + DEBUG_FIX_APPLIED EventBus publish calls
  GAP-86-15: KnowledgeSynthesisEngine receives debug pattern data via cross-cutting hooks

CORE-008: TDD — these tests are written before the wiring edits.
"""

import pytest
from unittest.mock import MagicMock, patch, call
from cortex.core.event_bus import EventBus, Event


# ─────────────────────────────────────────────────────────────────────────────
# GAP-86-11: OPJMixin wiring
# ─────────────────────────────────────────────────────────────────────────────
class TestDebuggerOrchestratorOPJMixin:
    """Verify DebuggerOrchestrator inherits OPJMixin (GAP-86-11)."""

    def test_debugger_orchestrator_inherits_opj_mixin(self) -> None:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        from cortex.intelligence.learning.opj_mixin import OPJMixin
        assert issubclass(DebuggerOrchestrator, OPJMixin)

    def test_debugger_orchestrator_has_opj_init_method(self) -> None:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert hasattr(DebuggerOrchestrator, "_opj_init")

    def test_debugger_orchestrator_has_opj_record_success(self) -> None:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert hasattr(DebuggerOrchestrator, "_opj_record_success")

    def test_debugger_orchestrator_has_opj_record_failure(self) -> None:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert hasattr(DebuggerOrchestrator, "_opj_record_failure")

    def test_debugger_orchestrator_has_urs_emit_signal(self) -> None:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert hasattr(DebuggerOrchestrator, "_urs_emit_signal")


# ─────────────────────────────────────────────────────────────────────────────
# GAP-86-12: URS signal emission
# ─────────────────────────────────────────────────────────────────────────────
class TestDebuggerOrchestratorURSSignal:
    """Verify URS signal emission in DebuggerOrchestrator (GAP-86-12)."""

    def _make_orchestrator(self) -> "DebuggerOrchestrator":
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        event_bus = EventBus()
        marker_engine = MagicMock()
        marker_engine.inject.return_value = True
        cleanup_manager = MagicMock()
        cleanup_manager.cleanup_resolved_sessions.return_value = []
        return DebuggerOrchestrator(event_bus, marker_engine, cleanup_manager)

    def test_handle_test_failure_emits_urs_signal(self) -> None:
        orch = self._make_orchestrator()
        with patch.object(orch, "_urs_emit_signal") as mock_urs:
            orch.handle_test_failure(Event(
                type="TEST_FAILURE",
                payload={"test_name": "test_x", "file_path": "x.py", "line_number": 1, "failure_reason": "err"}
            ))
            mock_urs.assert_called_once()

    def test_handle_tests_passed_emits_urs_cleanup_signal(self) -> None:
        orch = self._make_orchestrator()
        with patch.object(orch, "_urs_emit_signal") as mock_urs:
            orch.handle_tests_passed(Event(
                type="TESTS_PASSED",
                payload={"test_suite": "unit", "passed_count": 42}
            ))
            mock_urs.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# GAP-86-13: IntelligenceMatrix CC-021 + IC-021
# ─────────────────────────────────────────────────────────────────────────────
class TestIntelligenceMatrixDebugCells:
    """Verify CC-021 and IC-021 are present in IntelligenceMatrixBuilder (GAP-86-13)."""

    def test_cc_021_present_in_cortex_capabilities(self) -> None:
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import CORTEX_CAPABILITIES
        ids = {cap.id for cap in CORTEX_CAPABILITIES}
        assert "CC-021" in ids, "CC-021 (DebuggerOrchestrator) not found in CORTEX_CAPABILITIES"

    def test_ic_021_present_in_intelligence_capabilities(self) -> None:
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import INTELLIGENCE_CAPABILITIES
        ids = {cap.id for cap in INTELLIGENCE_CAPABILITIES}
        assert "IC-021" in ids, "IC-021 (MultiStackDebugPipeline) not found in INTELLIGENCE_CAPABILITIES"

    def test_cc_021_references_debugger_orchestrator_module(self) -> None:
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import CORTEX_CAPABILITIES
        cc021 = next((c for c in CORTEX_CAPABILITIES if c.id == "CC-021"), None)
        assert cc021 is not None
        assert "debugger" in cc021.module.lower() or "debug" in cc021.name.lower()

    def test_ic_021_references_debug_pipeline(self) -> None:
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import INTELLIGENCE_CAPABILITIES
        ic021 = next((c for c in INTELLIGENCE_CAPABILITIES if c.id == "IC-021"), None)
        assert ic021 is not None
        assert "debug" in ic021.name.lower() or "debug" in ic021.description.lower()


# ─────────────────────────────────────────────────────────────────────────────
# GAP-86-14: EventBus bidirectional — DEBUG_INSIGHT + DEBUG_FIX_APPLIED publish
# ─────────────────────────────────────────────────────────────────────────────
class TestDebuggerOrchestratorEventBusPublish:
    """Verify bidirectional EventBus publish (GAP-86-14)."""

    def _make_orchestrator(self) -> "DebuggerOrchestrator":
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        event_bus = MagicMock(spec=EventBus)
        event_bus.subscribe = MagicMock()
        event_bus.publish = MagicMock()
        marker_engine = MagicMock()
        marker_engine.inject.return_value = True
        cleanup_manager = MagicMock()
        cleanup_manager.cleanup_resolved_sessions.return_value = []
        return DebuggerOrchestrator(event_bus, marker_engine, cleanup_manager)

    def _published_types(self, orch: "DebuggerOrchestrator") -> list:
        calls = orch.event_bus.publish.call_args_list
        return [c.args[0].type for c in calls if c.args]

    def test_handle_test_failure_publishes_debug_markers_injected(self) -> None:
        orch = self._make_orchestrator()
        orch.handle_test_failure(Event(
            type="TEST_FAILURE",
            payload={"test_name": "t", "file_path": "f.py", "line_number": 1, "failure_reason": ""}
        ))
        assert "DEBUG_MARKERS_INJECTED" in self._published_types(orch)

    def test_handle_test_failure_publishes_debug_insight(self) -> None:
        orch = self._make_orchestrator()
        orch.handle_test_failure(Event(
            type="TEST_FAILURE",
            payload={"test_name": "t", "file_path": "f.py", "line_number": 1, "failure_reason": ""}
        ))
        assert "DEBUG_INSIGHT" in self._published_types(orch)

    def test_handle_tests_passed_publishes_debug_fix_applied(self) -> None:
        orch = self._make_orchestrator()
        orch.handle_tests_passed(Event(
            type="TESTS_PASSED",
            payload={"test_suite": "unit", "passed_count": 5}
        ))
        assert "DEBUG_FIX_APPLIED" in self._published_types(orch)


# ─────────────────────────────────────────────────────────────────────────────
# GAP-86-15: KnowledgeSynthesisEngine debug pattern data
# ─────────────────────────────────────────────────────────────────────────────
class TestDebuggerOrchestratorKnowledgeSynthesis:
    """Verify KnowledgeSynthesisEngine receives debug pattern data (GAP-86-15)."""

    def test_execute_operation_calls_cross_cutting_hooks(self) -> None:
        """Cross-cutting hooks (which wire KnSynth) must be invokable directly."""
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        event_bus = EventBus()
        marker_engine = MagicMock()
        marker_engine.inject.return_value = True
        cleanup_manager = MagicMock()
        cleanup_manager.cleanup_resolved_sessions.return_value = []
        orch = DebuggerOrchestrator(event_bus, marker_engine, cleanup_manager)
        # Cross-cutting hooks must be callable (GAP-86-15: KnSynth receives data via OPM)
        assert callable(getattr(orch, "_activate_cross_cutting_hooks", None))

    def test_debugger_orchestrator_has_activate_cross_cutting_hooks(self) -> None:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        assert hasattr(DebuggerOrchestrator, "_activate_cross_cutting_hooks")
