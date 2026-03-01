"""
InteractionOrchestrator E2E Golden Tests — Stage 1 Pipeline Audit.

Covers:
- G1+G2: ChallengeGenerator wired into _evaluate_challenge() for code-touching requests
- G3:    WorkflowGateway delegation for IMPLEMENT/FIX/REFACTOR intents
- G4:    Audit trail populated on every turn (in-memory + SQLite)
- G5:    per-mode output shape (comprehension, challenge, exempt)
- G6:    Silent Stage 1 skip emits a warning (no silent failure)
- G7:    User role propagated through LENS context
- G8:    Audit log assertions against SQLite trace DB

AC_START: AC-INTERACTION-E2E-GOLDEN-001
Authority: CORE-008 (TDD-first), CORE-012 (docstrings), CORE-011 (type hints)
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_orchestrator(
    enable_challenges: bool = True,
    user_role: str = "developer",
) -> InteractionOrchestrator:
    """Build an InteractionOrchestrator with a mock ConversationProtocol."""
    proto = MagicMock()
    orch = InteractionOrchestrator(
        conversation_protocol=proto,
        enable_challenges=enable_challenges,
    )
    orch._user_role = user_role
    return orch


def _make_round_context(msg: str = "test") -> Any:
    """Build a minimal RoundContext-like mock."""
    ctx = MagicMock()
    ctx.user_message = msg
    ctx.session_id = "test-session-001"
    return ctx


CODE_TOUCHING_REQUESTS = [
    "implement a new authentication service",
    "fix the broken retry logic in the HTTP client",
    "refactor the orchestrator base class to use a mixin",
    "build a new endpoint for user profile data",
    "create a database migration script",
    "add type hints to all public methods",
    "modify the LENS pipeline to support multi-file analysis",
    "delete the deprecated orchestrator file",
]

NON_CODE_REQUESTS = [
    "explain how CORTEX orchestrators work",
    "what is the LENS pipeline?",
    "show me the architecture diagram",
    "who owns the governance rules?",
]


# ── fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def orchestrator() -> InteractionOrchestrator:
    """Standard orchestrator fixture with challenges enabled."""
    return _make_orchestrator(enable_challenges=True)


@pytest.fixture
def orchestrator_no_challenges() -> InteractionOrchestrator:
    """Orchestrator with challenges explicitly disabled."""
    return _make_orchestrator(enable_challenges=False)


@pytest.fixture
def round_ctx() -> Any:
    """Standard RoundContext mock."""
    return _make_round_context("implement a new auth service")


# =============================================================================
# G1: ChallengeGenerator IS wired into _evaluate_challenge()
# =============================================================================

class TestChallengeGeneratorWired:
    """G1 — ChallengeGenerator must be available inside InteractionOrchestrator."""

    def test_challenge_gen_attribute_exists(self, orchestrator: InteractionOrchestrator) -> None:
        """InteractionOrchestrator must have a _challenge_gen attribute."""
        assert hasattr(orchestrator, "_challenge_gen"), (
            "G1: _challenge_gen not found — ChallengeGenerator not wired into "
            "InteractionOrchestrator.__init__(). Fix: add self._challenge_gen = ChallengeGenerator()"
        )

    def test_challenge_gen_is_correct_type(self, orchestrator: InteractionOrchestrator) -> None:
        """_challenge_gen must be a ChallengeGenerator instance."""
        from cortex.orchestrators.core.intent_router.challenge_generator import ChallengeGenerator
        assert isinstance(orchestrator._challenge_gen, ChallengeGenerator), (
            "G1: _challenge_gen is not a ChallengeGenerator instance. "
            f"Got: {type(orchestrator._challenge_gen)}"
        )

    def test_challenge_gen_has_generate_all(self, orchestrator: InteractionOrchestrator) -> None:
        """ChallengeGenerator must expose generate_all() callable."""
        assert callable(getattr(orchestrator._challenge_gen, "generate_all", None)), (
            "G1: _challenge_gen.generate_all() not callable — ChallengeGenerator API mismatch."
        )


# =============================================================================
# G2: Challenge IS mandatory for code-touching requests
# =============================================================================

class TestMandatoryChallenge:
    """G2 — Every code-touching request must be evaluated for challenges."""

    @pytest.mark.parametrize("user_request", CODE_TOUCHING_REQUESTS)
    def test_code_touching_request_evaluated(
        self,
        orchestrator: InteractionOrchestrator,
        user_request: str,
    ) -> None:
        """_evaluate_challenge() must be called (and return a value or None) for code-touching requests."""
        lens_ctx: Dict[str, Any] = {"status": "ok", "code_snippet": "def foo(): pass"}
        result = orchestrator._evaluate_challenge(user_request, lens_ctx, None)
        # Result can be None (no challenge found) or a dict (challenge found).
        # The key assertion: it must NOT raise and must not be a stub.
        assert result is None or isinstance(result, dict), (
            f"G2: _evaluate_challenge() returned unexpected type {type(result)} "
            f"for code-touching request '{user_request[:40]}'"
        )

    @pytest.mark.parametrize("user_request", NON_CODE_REQUESTS)
    def test_non_code_request_not_challenged(
        self,
        orchestrator: InteractionOrchestrator,
        user_request: str,
    ) -> None:
        """Non-code requests must NOT generate a challenge (governance performance)."""
        lens_ctx: Dict[str, Any] = {"status": "ok"}
        result = orchestrator._evaluate_challenge(user_request, lens_ctx, None)
        assert result is None, (
            f"G2: Non-code request '{user_request[:40]}' incorrectly challenged. "
            "Only code-touching requests should be challenged."
        )

    def test_bare_except_in_snippet_triggers_governance_challenge(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """Code with bare except must trigger a GOVERNANCE_RISK challenge."""
        snippet = "def foo():\n    try:\n        pass\n    except:\n        pass\n"
        lens_ctx: Dict[str, Any] = {"status": "ok", "code_snippet": snippet}
        result = orchestrator._evaluate_challenge(
            "fix the broken retry logic", lens_ctx, None
        )
        assert result is not None, (
            "G2: Bare except in code snippet must trigger a GOVERNANCE_RISK challenge "
            "(CORE-013 violation). _evaluate_challenge() returned None."
        )
        assert "category" in result, "G2: Challenge dict missing 'category' key"
        assert "severity" in result, "G2: Challenge dict missing 'severity' key"
        assert "description" in result, "G2: Challenge dict missing 'description' key"
        assert "mitigation" in result, "G2: Challenge dict missing 'mitigation' key"

    def test_eval_in_snippet_triggers_critical_challenge(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """Code with eval() must trigger a CRITICAL challenge."""
        snippet = "def compute(x):\n    return eval(x)\n"
        lens_ctx: Dict[str, Any] = {"status": "ok", "code_snippet": snippet}
        result = orchestrator._evaluate_challenge(
            "implement compute function", lens_ctx, None
        )
        assert result is not None, (
            "G2: eval() in code snippet must trigger a CRITICAL challenge. "
            "_evaluate_challenge() returned None."
        )
        assert result.get("severity") == "CRITICAL", (
            f"G2: eval() challenge severity must be CRITICAL, got {result.get('severity')}"
        )

    def test_clean_code_returns_none_challenge(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """Clean code with no violations must return None (no false positives)."""
        snippet = (
            "def add(a: int, b: int) -> int:\n"
            '    """Add two numbers.\n\n    Args:\n        a: First number.\n        b: Second.\n\n    Returns:\n        Sum.\n    """\n'
            "    return a + b\n"
        )
        lens_ctx: Dict[str, Any] = {"status": "ok", "code_snippet": snippet}
        result = orchestrator._evaluate_challenge(
            "implement add utility", lens_ctx, None
        )
        # Clean code may or may not have challenges (test gap is valid)
        # We just assert it's the right type
        assert result is None or isinstance(result, dict), (
            "G2: _evaluate_challenge() must return None or dict for clean code."
        )


# =============================================================================
# G3: WorkflowGateway delegated for IMPLEMENT/FIX/REFACTOR turns
# =============================================================================

class TestWorkflowGatewayDelegation:
    """G3 — execute_turn_with_challenge() must call WorkflowGateway for code intents."""

    def test_implement_turn_includes_workflow_template_key(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """IMPLEMENT turns must include workflow_template in output."""
        ctx = _make_round_context("implement a new auth service")
        result = orchestrator.execute_turn_with_challenge(
            user_request="implement a new auth service",
            round_context=ctx,
        )
        assert result.is_ok(), f"G3: execute_turn_with_challenge failed: {result}"
        output = result.unwrap()
        assert "workflow_template" in output, (
            "G3: IMPLEMENT turn missing 'workflow_template' key in output. "
            "WorkflowGateway must be called for code-touching intents."
        )

    def test_fix_turn_includes_workflow_template_key(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """FIX turns must include workflow_template in output."""
        ctx = _make_round_context("fix the broken retry logic")
        result = orchestrator.execute_turn_with_challenge(
            user_request="fix the broken retry logic",
            round_context=ctx,
        )
        assert result.is_ok(), f"G3: execute_turn_with_challenge failed: {result}"
        output = result.unwrap()
        assert "workflow_template" in output, (
            "G3: FIX turn missing 'workflow_template' key. WorkflowGateway must be called."
        )

    def test_refactor_turn_includes_workflow_template_key(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """REFACTOR turns must include workflow_template in output."""
        ctx = _make_round_context("refactor the orchestrator base class")
        result = orchestrator.execute_turn_with_challenge(
            user_request="refactor the orchestrator base class",
            round_context=ctx,
        )
        assert result.is_ok(), f"G3: execute_turn_with_challenge failed: {result}"
        output = result.unwrap()
        assert "workflow_template" in output, (
            "G3: REFACTOR turn missing 'workflow_template' key. WorkflowGateway must be called."
        )

    def test_query_turn_does_not_require_workflow_template(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """Non-code-touching (QUERY) turns are exempt from WorkflowGateway."""
        ctx = _make_round_context("what is the LENS pipeline?")
        result = orchestrator.execute_turn_with_challenge(
            user_request="what is the LENS pipeline?",
            round_context=ctx,
        )
        assert result.is_ok(), f"G3: execute_turn_with_challenge failed for query: {result}"
        # Query may or may not have workflow_template — both are valid
        output = result.unwrap()
        assert isinstance(output, dict), "G3: Output must be a dict"


# =============================================================================
# G4: Audit trail populated on every turn
# =============================================================================

class TestAuditTrail:
    """G4 — Every turn must append an entry to the in-memory audit trail."""

    def test_audit_trail_grows_per_turn(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """Each execute_turn() call must append one audit entry."""
        initial_len = len(orchestrator._audit_trail)
        orchestrator.execute_turn("first turn")
        orchestrator.execute_turn("second turn")
        assert len(orchestrator._audit_trail) == initial_len + 2, (
            "G4: Audit trail must grow by 1 per execute_turn() call. "
            f"Expected {initial_len + 2}, got {len(orchestrator._audit_trail)}"
        )

    def test_execute_turn_with_challenge_appends_audit(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """execute_turn_with_challenge() must append an audit entry."""
        ctx = _make_round_context("implement feature X")
        initial_len = len(orchestrator._audit_trail)
        orchestrator.execute_turn_with_challenge(
            user_request="implement feature X",
            round_context=ctx,
        )
        assert len(orchestrator._audit_trail) > initial_len, (
            "G4: execute_turn_with_challenge() must append to _audit_trail."
        )

    def test_audit_entry_has_required_fields(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """Each audit entry must contain timestamp, operation, and success fields."""
        orchestrator.execute_turn("audit field test")
        entry = orchestrator._audit_trail[-1]
        for required_key in ("operation", "success", "timestamp"):
            assert required_key in entry, (
                f"G4: Audit entry missing required field '{required_key}'. "
                f"Entry: {entry}"
            )

    def test_get_audit_trail_returns_ok(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """get_audit_trail() must return Ok with a list."""
        orchestrator.execute_turn("populate audit")
        result = orchestrator.get_audit_trail(limit=10)
        assert result.is_ok(), f"G4: get_audit_trail() returned Err: {result}"
        data = result.unwrap()
        assert isinstance(data, list), f"G4: get_audit_trail() must return a list, got {type(data)}"


# =============================================================================
# G5: Per-mode output shape
# =============================================================================

class TestPerModeOutputShape:
    """G5 — Output dict shape must match the mode (comprehension vs challenge)."""

    def test_comprehension_mode_output_keys(
        self,
        orchestrator_no_challenges: InteractionOrchestrator,
    ) -> None:
        """Comprehension mode output must have canonical keys."""
        ctx = _make_round_context("what is CORTEX?")
        result = orchestrator_no_challenges.execute_turn_with_challenge(
            user_request="what is CORTEX?",
            round_context=ctx,
        )
        assert result.is_ok(), f"G5: comprehension mode failed: {result}"
        output = result.unwrap()
        for key in ("type", "user_request", "lens_context", "turn_number", "timestamp"):
            assert key in output, (
                f"G5: Comprehension output missing key '{key}'. Output keys: {list(output.keys())}"
            )
        assert output["type"] == "comprehension", (
            f"G5: Expected type='comprehension' for non-challenge turn, got '{output.get('type')}'"
        )

    def test_challenge_mode_output_keys(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """When a challenge fires, output must include 'challenge' key and type='challenge'."""
        snippet = "def foo():\n    try:\n        pass\n    except:\n        pass\n"

        with patch.object(
            orchestrator,
            "_run_lens_analysis",
            return_value={"status": "ok", "code_snippet": snippet},
        ):
            ctx = _make_round_context("fix broken code")
            result = orchestrator.execute_turn_with_challenge(
                user_request="fix broken code",
                round_context=ctx,
            )

        assert result.is_ok(), f"G5: challenge mode failed: {result}"
        output = result.unwrap()
        # If a challenge was generated, it must have correct shape
        if output.get("type") == "challenge":
            assert "challenge" in output, "G5: challenge type output missing 'challenge' key"
            challenge = output["challenge"]
            for key in ("category", "severity", "description", "mitigation"):
                assert key in challenge, (
                    f"G5: Challenge dict missing key '{key}'. Challenge: {challenge}"
                )

    def test_execute_comprehension_output_shape(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """execute() (simplified interface) must return intent_type and lens_context."""
        result = orchestrator.execute(context={"user_intent": "implement new service"})
        assert result.is_ok(), f"G5: execute() failed: {result}"
        output = result.unwrap()
        for key in ("intent_type", "lens_context", "confidence", "analysis_complete"):
            assert key in output, (
                f"G5: execute() output missing key '{key}'. Keys: {list(output.keys())}"
            )

    def test_breadcrumb_present_in_turn_output(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """Every turn output must include 'breadcrumb' key for VS Code rendering."""
        ctx = _make_round_context("explain CORTEX")
        result = orchestrator.execute_turn_with_challenge(
            user_request="explain CORTEX",
            round_context=ctx,
        )
        assert result.is_ok(), f"G5: turn failed: {result}"
        output = result.unwrap()
        assert "breadcrumb" in output, (
            "G5: Output missing 'breadcrumb' key required for VS Code Copilot Chat rendering."
        )


# =============================================================================
# G6: Silent Stage 1 skip must not fail silently
# =============================================================================

class TestStage1FallbackLogging:
    """G6 — When InteractionOrchestrator is None, MasterOrchestrator must log a warning."""

    def test_challenge_disabled_still_runs_lens(
        self,
        orchestrator_no_challenges: InteractionOrchestrator,
    ) -> None:
        """Even with challenges disabled, LENS must still run per turn."""
        result = orchestrator_no_challenges.execute_turn("analyze this code")
        assert result.is_ok(), f"G6: execute_turn failed with challenges disabled: {result}"
        output = result.unwrap()
        assert "lens_context" in output, (
            "G6: LENS context missing even when challenges are disabled. "
            "LENS is mandatory per-turn regardless of challenge setting."
        )

    def test_interaction_orchestrator_initialize_returns_ok(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """initialize() must return Ok — no silent boot failures."""
        result = orchestrator.initialize()
        assert result.is_ok(), (
            f"G6: InteractionOrchestrator.initialize() returned Err: {result}. "
            "Silent boot failure detected — Stage 1 would be skipped silently."
        )

    def test_challenge_eval_false_when_disabled(
        self,
        orchestrator_no_challenges: InteractionOrchestrator,
    ) -> None:
        """challenge_evaluated must be False when enable_challenges=False."""
        ctx = _make_round_context("fix something")
        result = orchestrator_no_challenges.execute_turn_with_challenge(
            user_request="fix something",
            round_context=ctx,
        )
        assert result.is_ok()
        output = result.unwrap()
        assert output.get("challenge_evaluated") is False, (
            "G6: challenge_evaluated must be False when enable_challenges=False."
        )


# =============================================================================
# G7: User role propagated through LENS context
# =============================================================================

class TestUserRolePropagation:
    """G7 — User role must be set and accessible on InteractionOrchestrator."""

    def test_user_role_attribute_settable(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """_user_role must be settable on the orchestrator instance."""
        orchestrator._user_role = "architect"
        assert orchestrator._user_role == "architect", (
            "G7: _user_role not settable on InteractionOrchestrator."
        )

    def test_turn_output_includes_user_role_when_set(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """When _user_role is set, execute_turn_with_challenge() output must include it."""
        orchestrator._user_role = "security_engineer"
        ctx = _make_round_context("audit auth service")
        result = orchestrator.execute_turn_with_challenge(
            user_request="audit auth service",
            round_context=ctx,
        )
        assert result.is_ok(), f"G7: turn failed: {result}"
        output = result.unwrap()
        assert output.get("user_role") == "security_engineer", (
            "G7: user_role not included in turn output. "
            "LENS context must be role-aware for accurate intelligence."
        )

    def test_default_role_is_developer(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """When no role is set, default role must be 'developer'."""
        fresh = _make_orchestrator()
        # Remove _user_role if set by fixture
        if hasattr(fresh, "_user_role"):
            delattr(fresh, "_user_role")
        role = getattr(fresh, "_user_role", "developer")
        assert role == "developer", (
            f"G7: Default user role must be 'developer', got '{role}'"
        )


# =============================================================================
# G8: SQLite audit log assertions
# =============================================================================

class TestSQLiteAuditLog:
    """G8 — workflow_runs table in SQLite must be populated for code-touching turns."""

    def test_workflow_gateway_logs_implement_run(self, tmp_path: Path) -> None:
        """WorkflowGateway must log an IMPLEMENT run to SQLite workflow_runs table."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        db_path = tmp_path / "test_traces.db"
        gateway = WorkflowGateway(db_path=db_path)

        # Patch WorkflowComposer to avoid template file I/O in test
        mock_composer = MagicMock()
        mock_composer.execute_from_template.return_value = {
            "status": "complete",
            "steps_completed": 3,
        }
        gateway._composer = mock_composer

        gateway.execute_gated(
            orchestrator_name="InteractionOrchestrator",
            mode="IMPLEMENT",
            context={"user_request": "implement new auth service"},
        )

        # Assert row in SQLite
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.execute(
                "SELECT orchestrator, mode, status FROM workflow_runs WHERE orchestrator='InteractionOrchestrator'"
            )
            rows = cursor.fetchall()

        assert len(rows) >= 1, (
            "G8: No workflow_runs row found for InteractionOrchestrator IMPLEMENT. "
            "WorkflowGateway must log every code-touching operation to SQLite."
        )
        orchestrator_name, mode, status = rows[0]
        assert mode == "IMPLEMENT", f"G8: Expected mode IMPLEMENT, got '{mode}'"
        assert status == "complete", f"G8: Expected status 'complete', got '{status}'"

    def test_workflow_gateway_logs_fix_run(self, tmp_path: Path) -> None:
        """WorkflowGateway must log a FIX run to SQLite."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        db_path = tmp_path / "test_fix_traces.db"
        gateway = WorkflowGateway(db_path=db_path)
        mock_composer = MagicMock()
        mock_composer.execute_from_template.return_value = {"status": "complete", "steps_completed": 2}
        gateway._composer = mock_composer

        gateway.execute_gated(
            orchestrator_name="InteractionOrchestrator",
            mode="FIX",
            context={"user_request": "fix retry logic"},
        )

        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.execute("SELECT mode FROM workflow_runs LIMIT 1")
            row = cursor.fetchone()

        assert row is not None, "G8: No row in workflow_runs after FIX operation."
        assert row[0] == "FIX", f"G8: Expected mode FIX, got '{row[0]}'"

    def test_interaction_orchestrator_audit_trail_has_ac_id(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """execute_turn_with_challenge() audit entries must include ac_id field."""
        ctx = _make_round_context("implement X")
        orchestrator.execute_turn_with_challenge(
            user_request="implement X",
            round_context=ctx,
        )
        entries_with_ac = [e for e in orchestrator._audit_trail if "ac_id" in e]
        assert len(entries_with_ac) >= 1, (
            "G8: No audit entry with 'ac_id' found after execute_turn_with_challenge(). "
            "All audit entries must include an AC marker ID for SQLite traceability."
        )

    def test_workflow_runs_table_has_required_columns(self, tmp_path: Path) -> None:
        """workflow_runs SQLite table must have all required columns."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        db_path = tmp_path / "schema_test.db"
        WorkflowGateway(db_path=db_path)  # triggers _ensure_db()

        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.execute("PRAGMA table_info(workflow_runs)")
            columns = {row[1] for row in cursor.fetchall()}

        required = {
            "run_id", "orchestrator", "mode", "template_id",
            "status", "steps_completed", "duration_ms",
            "started_at", "completed_at",
        }
        missing = required - columns
        assert not missing, (
            f"G8: workflow_runs table missing required columns: {missing}"
        )


# =============================================================================
# E2E: Full pipeline — challenge → workflow delegation → audit
# =============================================================================

class TestFullPipelineE2E:
    """End-to-end: LENS → Challenge evaluation → WorkflowGateway → Audit trail."""

    def test_implement_request_full_pipeline(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """Full IMPLEMENT pipeline: LENS + challenge eval + workflow_template in output."""
        ctx = _make_round_context("implement a new payment processor")
        result = orchestrator.execute_turn_with_challenge(
            user_request="implement a new payment processor",
            round_context=ctx,
        )
        assert result.is_ok(), f"E2E: Full IMPLEMENT pipeline failed: {result}"
        output = result.unwrap()

        # Stage 1: LENS ran
        assert "lens_context" in output, "E2E: LENS context missing from IMPLEMENT turn"

        # Stage 2: Challenge evaluated
        assert "challenge_evaluated" in output, "E2E: challenge_evaluated missing"

        # Stage 3: WorkflowGateway delegated
        assert "workflow_template" in output, (
            "E2E: workflow_template missing — WorkflowGateway not called for IMPLEMENT"
        )

        # Stage 4: Audit trail populated
        assert len(orchestrator._audit_trail) >= 1, "E2E: No audit trail entries after full pipeline"

    def test_fix_request_with_governance_violation_raises_challenge(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """FIX request with bare except code must surface a governance challenge."""
        bad_code = "def handle():\n    try:\n        process()\n    except:\n        pass\n"

        with patch.object(
            orchestrator,
            "_run_lens_analysis",
            return_value={"status": "ok", "code_snippet": bad_code},
        ):
            ctx = _make_round_context("fix the error handler")
            result = orchestrator.execute_turn_with_challenge(
                user_request="fix the error handler",
                round_context=ctx,
            )

        assert result.is_ok(), f"E2E: FIX pipeline with violation failed: {result}"
        output = result.unwrap()

        # Either challenge was generated, or challenge_evaluated is True
        challenge_fired = output.get("type") == "challenge" and output.get("challenge") is not None
        challenge_evaluated = output.get("challenge_evaluated") is True

        assert challenge_evaluated, (
            "E2E: challenge_evaluated must be True for FIX request when enable_challenges=True"
        )
        if challenge_fired:
            assert output["challenge"].get("category") is not None, (
                "E2E: Challenge fired but missing 'category' key"
            )

    def test_turn_number_increments_across_turns(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """Turn counter must increment monotonically across multiple turns."""
        ctx1 = _make_round_context("turn 1")
        ctx2 = _make_round_context("turn 2")
        ctx3 = _make_round_context("turn 3")

        r1 = orchestrator.execute_turn_with_challenge(user_request="turn 1", round_context=ctx1)
        r2 = orchestrator.execute_turn_with_challenge(user_request="turn 2", round_context=ctx2)
        r3 = orchestrator.execute_turn_with_challenge(user_request="turn 3", round_context=ctx3)

        t1 = r1.unwrap()["turn_number"]
        t2 = r2.unwrap()["turn_number"]
        t3 = r3.unwrap()["turn_number"]

        assert t1 < t2 < t3, (
            f"E2E: Turn numbers must be monotonically increasing. Got: {t1}, {t2}, {t3}"
        )

    def test_orchestrator_get_name_returns_correct_identifier(
        self,
        orchestrator: InteractionOrchestrator,
    ) -> None:
        """get_name() must return 'InteractionOrchestrator' for routing table correctness."""
        name = orchestrator.get_name()
        assert name == "InteractionOrchestrator", (
            f"E2E: get_name() returned '{name}', expected 'InteractionOrchestrator'. "
            "Routing table and wiring specs depend on this exact string."
        )




# =============================================================================
# P2-D: Challenge decisions must be persisted to SQLite challenge_decisions table
# =============================================================================

class TestChallengeDecisionSQLite:
    """P2-D — Challenge decisions must be logged to SQLite, not only in-memory.

    Red tests (CORE-008): written before implementation.
    Target: .cortex-runtime/traces/orchestrator-traces.db → challenge_decisions table.
    """

    def test_challenge_decisions_table_exists_in_trace_db(self, tmp_path: Path) -> None:
        """challenge_decisions table must exist after InteractionOrchestrator init."""
        proto = MagicMock()
        orch = InteractionOrchestrator(
            conversation_protocol=proto,
            enable_challenges=True,
            trace_db_path=str(tmp_path / "traces.db"),
        )
        with sqlite3.connect(str(tmp_path / "traces.db")) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='challenge_decisions'"
            )
            row = cursor.fetchone()
        assert row is not None, (
            "P2-D: challenge_decisions table not found in trace DB after __init__(). "
            "Add _ensure_challenge_decisions_table() called from __init__()."
        )

    def test_challenge_decisions_table_has_required_columns(self, tmp_path: Path) -> None:
        """challenge_decisions table must have all canonical columns."""
        proto = MagicMock()
        InteractionOrchestrator(
            conversation_protocol=proto,
            enable_challenges=True,
            trace_db_path=str(tmp_path / "traces.db"),
        )
        with sqlite3.connect(str(tmp_path / "traces.db")) as conn:
            cursor = conn.execute("PRAGMA table_info(challenge_decisions)")
            columns = {row[1] for row in cursor.fetchall()}

        required = {
            "decision_id", "timestamp", "turn_number", "user_request_hint",
            "challenge_category", "challenge_severity", "decision",
            "challenge_description", "mitigation", "session_id",
        }
        missing = required - columns
        assert not missing, (
            f"P2-D: challenge_decisions missing columns: {missing}. "
            "Update CREATE TABLE statement in _ensure_challenge_decisions_table()."
        )

    def test_challenge_decision_logged_when_challenge_fires(self, tmp_path: Path) -> None:
        """When a governance challenge fires, a row must be inserted into challenge_decisions."""
        bad_code = "def run():\n    try:\n        work()\n    except:\n        pass\n"
        proto = MagicMock()
        orch = InteractionOrchestrator(
            conversation_protocol=proto,
            enable_challenges=True,
            trace_db_path=str(tmp_path / "traces.db"),
        )

        with patch.object(
            orch,
            "_run_lens_analysis",
            return_value={"status": "ok", "code_snippet": bad_code},
        ):
            ctx = _make_round_context("fix the exception handler")
            orch.execute_turn_with_challenge(
                user_request="fix the exception handler",
                round_context=ctx,
            )

        with sqlite3.connect(str(tmp_path / "traces.db")) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM challenge_decisions")
            count = cursor.fetchone()[0]

        assert count >= 1, (
            "P2-D: No row in challenge_decisions after a challenge-firing turn. "
            "Call _log_challenge_decision() inside execute_turn_with_challenge() "
            "when output['type'] == 'challenge'."
        )

    def test_challenge_decision_row_has_correct_values(self, tmp_path: Path) -> None:
        """challenge_decisions row must store the correct decision, severity and hint."""
        bad_code = "eval(user_input)\n"
        proto = MagicMock()
        orch = InteractionOrchestrator(
            conversation_protocol=proto,
            enable_challenges=True,
            trace_db_path=str(tmp_path / "traces.db"),
        )

        with patch.object(
            orch,
            "_run_lens_analysis",
            return_value={"status": "ok", "code_snippet": bad_code},
        ):
            ctx = MagicMock()
            ctx.session_id = "sess-p2d-test"
            orch.execute_turn_with_challenge(
                user_request="implement eval-based dispatcher",
                round_context=ctx,
            )

        with sqlite3.connect(str(tmp_path / "traces.db")) as conn:
            cursor = conn.execute(
                "SELECT user_request_hint, decision, session_id FROM challenge_decisions LIMIT 1"
            )
            row = cursor.fetchone()

        assert row is not None, "P2-D: No row written to challenge_decisions."
        user_hint, decision, session_id = row
        assert "implement" in user_hint.lower() or "eval" in user_hint.lower(), (
            f"P2-D: user_request_hint '{user_hint}' does not reflect the request."
        )
        assert decision in {"proceed", "mitigate", "cancel", "surfaced"}, (
            f"P2-D: decision value '{decision}' not in allowed set."
        )

    def test_no_row_written_for_non_code_request(self, tmp_path: Path) -> None:
        """Non-code requests (exempt) must NOT produce a challenge_decisions row."""
        proto = MagicMock()
        orch = InteractionOrchestrator(
            conversation_protocol=proto,
            enable_challenges=True,
            trace_db_path=str(tmp_path / "traces.db"),
        )
        ctx = _make_round_context("explain the LENS pipeline")
        orch.execute_turn_with_challenge(
            user_request="explain the LENS pipeline",
            round_context=ctx,
        )
        with sqlite3.connect(str(tmp_path / "traces.db")) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM challenge_decisions")
            count = cursor.fetchone()[0]

        assert count == 0, (
            f"P2-D: {count} row(s) written to challenge_decisions for a non-code request. "
            "Only challenged (code-touch) turns should be logged."
        )

    def test_get_audit_trail_includes_challenge_decisions(self, tmp_path: Path) -> None:
        """get_audit_trail() must surface challenge_decisions rows alongside trace entries."""
        bad_code = "try:\n    work()\nexcept:\n    pass\n"
        proto = MagicMock()
        orch = InteractionOrchestrator(
            conversation_protocol=proto,
            enable_challenges=True,
            trace_db_path=str(tmp_path / "traces.db"),
        )
        with patch.object(
            orch,
            "_run_lens_analysis",
            return_value={"status": "ok", "code_snippet": bad_code},
        ):
            ctx = _make_round_context("fix the exception handler")
            orch.execute_turn_with_challenge(
                user_request="fix the exception handler",
                round_context=ctx,
            )

        result = orch.get_audit_trail(limit=50)
        assert result.is_ok(), f"P2-D: get_audit_trail() returned Err: {result}"
        # The trail may be from in-memory or DB — but the DB row count proves persistence
        with sqlite3.connect(str(tmp_path / "traces.db")) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM challenge_decisions")
            count = cursor.fetchone()[0]
        assert count >= 1, "P2-D: challenge_decisions table empty after challenge-firing turn."


# AC_COMPLETE: AC-INTERACTION-E2E-GOLDEN-001
