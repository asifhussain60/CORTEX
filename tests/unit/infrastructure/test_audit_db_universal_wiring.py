"""
Tests for universal SQLite activity log wiring in OrchestratorBase.

Verifies that every orchestrator execute()/run() call is automatically
logged to .cortex-runtime/audit.db without opt-in — Phase 15.

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from typing import Dict, Any, Optional

from cortex.core.orchestrator_base import OrchestratorBase, ExecutionResult, LifecycleStage
from cortex.infrastructure.audit_db import CortexAuditDB, AuditEntry, EventType


class _MinimalOrchestrator(OrchestratorBase):
    """Minimal concrete orchestrator for testing."""

    def __init__(self, orch_id: str = "test-orch") -> None:
        """Init with a test orchestrator id."""
        super().__init__(orchestrator_id=orch_id)

    def execute_operation(self) -> Dict[str, Any]:
        """Return a minimal result dict."""
        return {"done": True}


class _FailingOrchestrator(OrchestratorBase):
    """Orchestrator whose execute_operation raises."""

    def execute_operation(self) -> Dict[str, Any]:
        """Raise intentionally."""
        raise ValueError("deliberate failure")


class TestAuditDbUniversalWiring:
    """Universal audit log wiring tests (Phase 15)."""

    def test_execute_logs_orchestrator_start(self, tmp_path: Path) -> None:
        """execute() must emit ORCHESTRATOR_START before any lifecycle step."""
        db_path = tmp_path / "audit.db"
        db = CortexAuditDB(db_path)

        with patch("cortex.infrastructure.audit_db.get_audit_db", return_value=db):
            orch = _MinimalOrchestrator("orch-start-test")
            orch.execute()

        events = db.query_events(orchestrator_id="orch-start-test")
        start_events = [e for e in events if e.event_type == EventType.ORCHESTRATOR_START.value]
        assert len(start_events) >= 1, "ORCHESTRATOR_START not logged by execute()"

    def test_execute_logs_orchestrator_end(self, tmp_path: Path) -> None:
        """execute() must emit ORCHESTRATOR_END via teardown()."""
        db_path = tmp_path / "audit.db"
        db = CortexAuditDB(db_path)

        with patch("cortex.infrastructure.audit_db.get_audit_db", return_value=db):
            orch = _MinimalOrchestrator("orch-end-test")
            orch.execute()

        events = db.query_events(orchestrator_id="orch-end-test")
        end_events = [e for e in events if e.event_type == EventType.ORCHESTRATOR_END.value]
        assert len(end_events) >= 1, "ORCHESTRATOR_END not logged by teardown()"

    def test_run_logs_orchestrator_start(self, tmp_path: Path) -> None:
        """run() must emit ORCHESTRATOR_START."""
        db_path = tmp_path / "audit.db"
        db = CortexAuditDB(db_path)

        with patch("cortex.infrastructure.audit_db.get_audit_db", return_value=db):
            orch = _MinimalOrchestrator("run-start-test")
            orch.run()

        events = db.query_events(orchestrator_id="run-start-test")
        start_events = [e for e in events if e.event_type == EventType.ORCHESTRATOR_START.value]
        assert len(start_events) >= 1, "ORCHESTRATOR_START not logged by run()"

    def test_run_logs_orchestrator_end(self, tmp_path: Path) -> None:
        """run() must emit ORCHESTRATOR_END via teardown()."""
        db_path = tmp_path / "audit.db"
        db = CortexAuditDB(db_path)

        with patch("cortex.infrastructure.audit_db.get_audit_db", return_value=db):
            orch = _MinimalOrchestrator("run-end-test")
            orch.run()

        events = db.query_events(orchestrator_id="run-end-test")
        end_events = [e for e in events if e.event_type == EventType.ORCHESTRATOR_END.value]
        assert len(end_events) >= 1, "ORCHESTRATOR_END not logged by run()/teardown()"

    def test_start_event_contains_class_name(self, tmp_path: Path) -> None:
        """START audit entry metadata must include the orchestrator class name."""
        db_path = tmp_path / "audit.db"
        db = CortexAuditDB(db_path)

        with patch("cortex.infrastructure.audit_db.get_audit_db", return_value=db):
            orch = _MinimalOrchestrator("class-meta-test")
            orch.execute()

        events = db.query_events(orchestrator_id="class-meta-test")
        start_events = [e for e in events if e.event_type == EventType.ORCHESTRATOR_START.value]
        assert start_events, "No START event found"
        meta = start_events[0].metadata
        assert meta.get("class") == "_MinimalOrchestrator"

    def test_end_event_status_success(self, tmp_path: Path) -> None:
        """END audit entry status must be 'success' for passing orchestrators."""
        db_path = tmp_path / "audit.db"
        db = CortexAuditDB(db_path)

        with patch("cortex.infrastructure.audit_db.get_audit_db", return_value=db):
            orch = _MinimalOrchestrator("success-status-test")
            orch.execute()

        events = db.query_events(orchestrator_id="success-status-test")
        end_events = [e for e in events if e.event_type == EventType.ORCHESTRATOR_END.value]
        assert end_events[0].status == "success"

    def test_end_event_status_failed_on_exception(self, tmp_path: Path) -> None:
        """END audit entry status must be 'failed' when execute_operation raises."""
        db_path = tmp_path / "audit.db"
        db = CortexAuditDB(db_path)

        with patch("cortex.infrastructure.audit_db.get_audit_db", return_value=db):
            orch = _FailingOrchestrator("fail-status-test")
            orch.execute()

        events = db.query_events(orchestrator_id="fail-status-test")
        end_events = [e for e in events if e.event_type == EventType.ORCHESTRATOR_END.value]
        assert end_events, "No END event for failing orchestrator"
        assert end_events[0].status == "failed"

    def test_audit_failure_does_not_block_execution(self) -> None:
        """If audit DB is unavailable, execute() must still return a result."""
        with patch("cortex.infrastructure.audit_db.get_audit_db", side_effect=RuntimeError("db down")):
            orch = _MinimalOrchestrator("audit-failure-test")
            result = orch.execute()
        assert isinstance(result, ExecutionResult)
        # execution succeeded despite audit failure
        assert result.success is True

    def test_end_event_contains_duration_ms(self, tmp_path: Path) -> None:
        """END audit entry must record a non-negative duration_ms."""
        db_path = tmp_path / "audit.db"
        db = CortexAuditDB(db_path)

        with patch("cortex.infrastructure.audit_db.get_audit_db", return_value=db):
            orch = _MinimalOrchestrator("duration-test")
            orch.execute()

        events = db.query_events(orchestrator_id="duration-test")
        end_events = [e for e in events if e.event_type == EventType.ORCHESTRATOR_END.value]
        assert end_events[0].duration_ms >= 0

    def test_multiple_executions_all_logged(self, tmp_path: Path) -> None:
        """Every sequential execute() call must produce its own START+END pair."""
        db_path = tmp_path / "audit.db"
        db = CortexAuditDB(db_path)

        with patch("cortex.infrastructure.audit_db.get_audit_db", return_value=db):
            orch = _MinimalOrchestrator("multi-exec-test")
            orch.execute()
            orch.execute()
            orch.execute()

        events = db.query_events(orchestrator_id="multi-exec-test", limit=20)
        start_count = sum(1 for e in events if e.event_type == EventType.ORCHESTRATOR_START.value)
        end_count = sum(1 for e in events if e.event_type == EventType.ORCHESTRATOR_END.value)
        assert start_count == 3, f"Expected 3 START events, got {start_count}"
        assert end_count == 3, f"Expected 3 END events, got {end_count}"
