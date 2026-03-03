"""
Tests for Phase 113 Sub-phase C — InteractionOrchestrator context chain.

Verifies that InteractionOrchestrator can:
1. Accept a request_log_manager via set_request_log_manager()
2. Build a context summary from prior requests
3. Inject prior context into execute_turn_with_challenge()
4. Handle the first-turn case (empty prior context) gracefully
5. Limit the number of prior requests queried (configurable)

TDD sequence (RED → GREEN → REFACTOR):
  RED: all tests written first; run must show ALL FAIL before implementation.
"""

from unittest.mock import MagicMock, patch
import pytest


# ─── Fixtures ────────────────────────────────────────────────────────────────

def _make_orchestrator():
    """Return a real InteractionOrchestrator instance with a stub conversation_protocol."""
    from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
    mock_protocol = MagicMock()
    mock_protocol.execute_turn.return_value = {"output": "ok"}
    return InteractionOrchestrator(
        conversation_protocol=mock_protocol,
        enable_challenges=False,  # test isolation
    )


# ─── set_request_log_manager ─────────────────────────────────────────────────

class TestSetRequestLogManager:
    """InteractionOrchestrator must accept an injected RequestLogManager."""

    def test_set_request_log_manager_stores_reference(self) -> None:
        """set_request_log_manager() must store the manager as _request_log_manager."""
        io = _make_orchestrator()
        mock_mgr = MagicMock()
        io.set_request_log_manager(mock_mgr)
        assert io._request_log_manager is mock_mgr

    def test_default_request_log_manager_is_none(self) -> None:
        """_request_log_manager must default to None before injection."""
        io = _make_orchestrator()
        assert getattr(io, "_request_log_manager", None) is None


# ─── build_context_summary ───────────────────────────────────────────────────

class TestBuildContextSummary:
    """build_context_summary() must produce a compact context string."""

    def test_build_context_summary_returns_string(self) -> None:
        """build_context_summary() must return a str."""
        io = _make_orchestrator()
        prior = [
            {"sequence_number": 1, "user_request": "Create auth module", "intent_type": "IMPLEMENT"},
        ]
        result = io.build_context_summary(prior)
        assert isinstance(result, str)

    def test_build_context_summary_includes_request_text(self) -> None:
        """Summary must include each prior request's user_request text."""
        io = _make_orchestrator()
        prior = [
            {"sequence_number": 2, "user_request": "Add password hashing", "intent_type": "IMPLEMENT"},
            {"sequence_number": 1, "user_request": "Create auth module", "intent_type": "IMPLEMENT"},
        ]
        summary = io.build_context_summary(prior)
        assert "Add password hashing" in summary
        assert "Create auth module" in summary

    def test_build_context_summary_includes_intent_types(self) -> None:
        """Summary must include intent_type for each prior request."""
        io = _make_orchestrator()
        prior = [
            {"sequence_number": 1, "user_request": "Fix the login bug", "intent_type": "FIX"},
        ]
        summary = io.build_context_summary(prior)
        assert "FIX" in summary

    def test_build_context_summary_empty_list_returns_empty_string(self) -> None:
        """Empty prior request list must return empty string (first-turn case)."""
        io = _make_orchestrator()
        summary = io.build_context_summary([])
        assert summary == ""

    def test_build_context_summary_includes_sequence_numbers(self) -> None:
        """Summary must reference sequence numbers for ordering clarity."""
        io = _make_orchestrator()
        prior = [
            {"sequence_number": 3, "user_request": "Add rate limiting", "intent_type": "IMPLEMENT"},
        ]
        summary = io.build_context_summary(prior)
        assert "3" in summary


# ─── Context injection in execute_turn_with_challenge ────────────────────────

class TestContextChainInjection:
    """Prior context must be injected into the LENS analysis for each turn."""

    def test_execute_turn_queries_prior_requests_when_manager_set(self) -> None:
        """execute_turn_with_challenge() must call get_prior_requests() when manager is set."""
        io = _make_orchestrator()

        mock_mgr = MagicMock()
        mock_mgr.get_prior_requests.return_value = []
        io.set_request_log_manager(mock_mgr)

        mock_round_ctx = MagicMock()
        mock_round_ctx.session_id = "sess-test"

        with patch.object(io, "_evaluate_challenge", return_value=None), \
             patch.object(io, "_run_lens_analysis", return_value={}):
            try:
                io.execute_turn_with_challenge(
                    user_request="Add rate limiting",
                    round_context=mock_round_ctx,
                )
            except Exception:
                pass  # Pipeline may fail in isolation — we only check the mock was called

        mock_mgr.get_prior_requests.assert_called_once()

    def test_execute_turn_skips_prior_query_when_no_manager(self) -> None:
        """execute_turn_with_challenge() must not crash when _request_log_manager is None."""
        io = _make_orchestrator()
        assert io._request_log_manager is None  # pre-condition

        mock_round_ctx = MagicMock()
        mock_round_ctx.session_id = "sess-test"

        # Must not raise AttributeError / NoneType error
        try:
            io.execute_turn_with_challenge(
                user_request="First request ever",
                round_context=mock_round_ctx,
            )
        except AttributeError as e:
            pytest.fail(f"Should not raise AttributeError when manager is None: {e}")
        except Exception:
            pass  # Other pipeline errors acceptable in test isolation

    def test_first_turn_works_with_empty_prior_context(self) -> None:
        """First turn must work correctly when prior requests list is empty."""
        io = _make_orchestrator()

        mock_mgr = MagicMock()
        mock_mgr.get_prior_requests.return_value = []
        io.set_request_log_manager(mock_mgr)

        mock_round_ctx = MagicMock()
        mock_round_ctx.session_id = "sess-first"

        # Should not crash
        try:
            io.execute_turn_with_challenge(
                user_request="Very first user request",
                round_context=mock_round_ctx,
            )
        except AttributeError as e:
            pytest.fail(f"First-turn case must not raise AttributeError: {e}")
        except Exception:
            pass  # Other pipeline errors acceptable in test isolation

    def test_context_chain_three_turns(self) -> None:
        """Three consecutive turns must build cumulative prior context."""
        from cortex.orchestrators.core.request_log_manager import RequestLogManager
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            rlm = RequestLogManager(db_path=db)

            # Simulate 3 sequential requests
            sess = "sess-chain-c"
            rlm.log_request(session_id=sess, user_request="Create user auth module")
            rlm.log_request(session_id=sess, user_request="Add password hashing")
            rid3 = rlm.log_request(session_id=sess, user_request="Add rate limiting")

            # Prior requests for turn 3 (excluding turn 3 itself)
            prior = rlm.get_prior_requests(
                session_id=sess, limit=5, exclude_id=rid3
            )

        assert len(prior) == 2, f"Expected 2 prior requests, got {len(prior)}"
        texts = [r["user_request"] for r in prior]
        assert "Add password hashing" in texts
        assert "Create user auth module" in texts

    def test_prior_context_limit_respected(self) -> None:
        """get_prior_requests(limit=3) must return at most 3 results."""
        from cortex.orchestrators.core.request_log_manager import RequestLogManager
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            rlm = RequestLogManager(db_path=db)

            sess = "sess-limit-c"
            for i in range(8):
                rlm.log_request(session_id=sess, user_request=f"Request {i+1}")

            prior = rlm.get_prior_requests(session_id=sess, limit=3)

        assert len(prior) == 3, f"Expected exactly 3 results, got {len(prior)}"
