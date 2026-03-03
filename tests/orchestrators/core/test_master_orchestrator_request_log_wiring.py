"""
Tests for Phase 113 Sub-phase B — Wire RequestLogManager into MasterOrchestrator.

Verifies that:
1. MasterOrchestrator has a `_request_log_manager` attribute after init
2. process_user_request() calls log_request() BEFORE the pipeline executes
3. update_status(PROCESSING) is called after log_request()
4. update_status(COMPLETED) / update_status(FAILED) is called after pipeline completion
5. session_id is consistent within a request lifecycle

TDD sequence (RED → GREEN → REFACTOR):
  RED: all tests written first; run must show ALL FAIL before implementation.
"""

from unittest.mock import MagicMock, patch, call
import pytest


class TestMasterOrchestratorHasRequestLogManager:
    """MasterOrchestrator must expose _request_log_manager after init."""

    def test_has_request_log_manager_attribute(self) -> None:
        """MasterOrchestrator must have a _request_log_manager attribute."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()
        assert hasattr(mo, "_request_log_manager"), (
            "_request_log_manager attribute must be present after __init__"
        )

    def test_request_log_manager_is_not_none(self) -> None:
        """_request_log_manager must not be None after wiring."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()
        assert mo._request_log_manager is not None, (
            "_request_log_manager must be a live RequestLogManager instance"
        )

    def test_request_log_manager_has_log_request_method(self) -> None:
        """_request_log_manager must expose the log_request() method."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()
        assert callable(getattr(mo._request_log_manager, "log_request", None)), (
            "_request_log_manager.log_request must be callable"
        )

    def test_request_log_manager_has_update_status_method(self) -> None:
        """_request_log_manager must expose the update_status() method."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()
        assert callable(getattr(mo._request_log_manager, "update_status", None)), (
            "_request_log_manager.update_status must be callable"
        )


class TestProcessUserRequestLogsBeforePipeline:
    """process_user_request() must call log_request() BEFORE entering the pipeline."""

    def test_log_request_called_on_process_user_request(self) -> None:
        """log_request() must be called when process_user_request() is invoked."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()

        mock_manager = MagicMock()
        mock_manager.log_request.return_value = "test-request-id-001"
        mo._request_log_manager = mock_manager

        with patch.object(mo, "execute_operation", return_value=MagicMock(is_ok=lambda: True)):
            mo.process_user_request("Build a login module")

        mock_manager.log_request.assert_called_once()
        _, kwargs = mock_manager.log_request.call_args
        assert "user_request" in kwargs or len(mock_manager.log_request.call_args.args) >= 1, (
            "log_request must be called with at least user_request"
        )

    def test_log_request_receives_correct_user_request_text(self) -> None:
        """log_request() must receive the full user_request text without truncation."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()

        mock_manager = MagicMock()
        mock_manager.log_request.return_value = "rid-001"
        mo._request_log_manager = mock_manager

        long_request = "A" * 500
        with patch.object(mo, "execute_operation", return_value=MagicMock(is_ok=lambda: True)):
            mo.process_user_request(long_request)

        call_args = mock_manager.log_request.call_args
        all_args = list(call_args.args) + list(call_args.kwargs.values())
        assert long_request in all_args, "Full user_request text must be passed to log_request"

    def test_update_status_processing_called_after_log(self) -> None:
        """update_status(PROCESSING) must be called after log_request()."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()

        mock_manager = MagicMock()
        mock_manager.log_request.return_value = "rid-proc"
        mo._request_log_manager = mock_manager

        with patch.object(mo, "execute_operation", return_value=MagicMock(is_ok=lambda: True)):
            mo.process_user_request("Do something")

        # Verify the call ordering: log_request before update_status(PROCESSING)
        calls = mock_manager.method_calls
        call_names = [c[0] for c in calls]
        assert "log_request" in call_names, "log_request must be called"
        assert "update_status" in call_names, "update_status must be called"

        log_idx = next(i for i, c in enumerate(calls) if c[0] == "log_request")
        upd_idx = next(i for i, c in enumerate(calls) if c[0] == "update_status")
        assert log_idx < upd_idx, "log_request must be called BEFORE update_status"

    def test_update_status_uses_request_id_from_log_request(self) -> None:
        """update_status() must use the request_id returned by log_request()."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()

        expected_rid = "canonical-request-id-xyz"
        mock_manager = MagicMock()
        mock_manager.log_request.return_value = expected_rid
        mo._request_log_manager = mock_manager

        with patch.object(mo, "execute_operation", return_value=MagicMock(is_ok=lambda: True)):
            mo.process_user_request("Fix the bug")

        update_calls = [c for c in mock_manager.method_calls if c[0] == "update_status"]
        assert len(update_calls) >= 1, "update_status must be called at least once"
        first_update_rid = update_calls[0].args[0] if update_calls[0].args else update_calls[0].kwargs.get("request_id")
        assert first_update_rid == expected_rid, (
            f"update_status must use request_id '{expected_rid}', got '{first_update_rid}'"
        )

    def test_update_status_completed_called_on_success(self) -> None:
        """update_status('COMPLETED') must be called when pipeline succeeds."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()

        mock_manager = MagicMock()
        mock_manager.log_request.return_value = "rid-ok"
        mo._request_log_manager = mock_manager

        success_result = MagicMock()
        success_result.is_ok.return_value = True
        with patch.object(mo, "execute_operation", return_value=success_result):
            mo.process_user_request("Implement feature X")

        status_values = []
        for c in mock_manager.method_calls:
            if c[0] == "update_status":
                args = c.args
                if args and len(args) >= 2:
                    status_values.append(args[1])
                elif c.kwargs.get("status"):
                    status_values.append(c.kwargs["status"])

        assert "COMPLETED" in status_values or any(
            "COMPLETED" in str(c) for c in mock_manager.method_calls
        ), f"COMPLETED status must be set. Calls: {mock_manager.method_calls}"
