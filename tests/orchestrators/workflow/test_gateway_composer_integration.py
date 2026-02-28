"""
Phase 99 — Gateway→Composer Integration: End-to-End Chain Verification.

These tests verify that the REAL gateway→composer chain works without mocks.
Prior to Phase 99, the chain had 5 fatal breaks that caused TypeError/
AttributeError when any orchestrator with PHASE90_GATEWAY_ENABLED=True
attempted to execute.

CORE-008: TDD mandatory
AC-ID: AC-P99-GCI-001
"""
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent.parent


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 1: WorkflowComposer accepts no template_path (gateway mode)
# ════════════════════════════════════════════════════════════════════════════

class TestComposerGatewayMode:
    """WorkflowComposer must be instantiable without template_path for gateway use."""

    def test_composer_instantiates_without_template_path(self) -> None:
        """WorkflowComposer() with no args must not raise TypeError."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        composer = WorkflowComposer()
        assert composer is not None

    def test_composer_with_template_path_still_works(self, tmp_path: Path) -> None:
        """Existing callers that pass template_path must still work."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer

        template = tmp_path / "test.yaml"
        template.write_text(
            "workflow:\n"
            "  name: 'Test Workflow'\n"
            "  steps:\n"
            "    - step_id: s1\n"
            "      orchestrator: TestOrch\n"
            "      parameters: {}\n"
        )
        composer = WorkflowComposer(template_path=template)
        assert composer.workflow_name == "Test Workflow"

    def test_composer_gateway_mode_has_empty_steps(self) -> None:
        """Gateway-mode composer starts with no steps (loaded on-demand)."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        composer = WorkflowComposer()
        assert composer.compose() == []


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 2: execute_from_template accepts string template_id
# ════════════════════════════════════════════════════════════════════════════

class TestComposerExecuteFromTemplateString:
    """execute_from_template must accept a string template_id and load YAML from disk."""

    def test_execute_from_template_with_string_loads_yaml(self) -> None:
        """Passing a template_id string must load the YAML from cortex-registry."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer

        composer = WorkflowComposer()
        # Use a real template that exists in the registry
        result = composer.execute_from_template("sdlc/implement-workflow")
        assert result is not None
        assert result.success is True
        assert result.steps_completed >= 0
        assert result.total_steps > 0

    def test_execute_from_template_with_dict_still_works(self) -> None:
        """Passing a dict must still work (backwards compatibility)."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer

        composer = WorkflowComposer()
        template = {
            "id": "test/inline",
            "name": "Inline Test",
            "steps": [
                {"id": "s1", "action": "noop", "parameters": {}},
                {"id": "s2", "action": "noop", "parameters": {}},
            ],
        }
        result = composer.execute_from_template(template)
        assert result.success is True
        assert result.steps_completed == 2
        assert result.total_steps == 2

    def test_execute_from_template_with_convergence_mode(self) -> None:
        """convergence_mode=True must not crash (Phase 99 fix)."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer

        composer = WorkflowComposer()
        template = {
            "id": "test/convergence",
            "name": "Convergence Test",
            "steps": [{"id": "s1", "action": "noop"}],
        }
        # This would crash pre-Phase 99 (dead imports)
        result = composer.execute_from_template(
            template, convergence_mode=True
        )
        assert result is not None

    def test_execute_from_template_nonexistent_raises(self) -> None:
        """Passing a nonexistent template_id must raise FileNotFoundError."""
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer

        composer = WorkflowComposer()
        with pytest.raises(FileNotFoundError):
            composer.execute_from_template("nonexistent/template-that-does-not-exist")


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 3: Full gateway→composer chain (no mocks)
# ════════════════════════════════════════════════════════════════════════════

class TestGatewayComposerChain:
    """The real gateway→composer chain must work end-to-end without mocks."""

    @pytest.fixture
    def gateway(self, tmp_path: Path) -> Any:
        """Create a gateway with a temp SQLite DB (avoid polluting real DB)."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway
        db_path = tmp_path / "test-traces.db"
        return WorkflowGateway(db_path=db_path)

    def test_gateway_execute_gated_implement_succeeds(self, gateway: Any) -> None:
        """execute_gated('IMPLEMENT') must complete without crash."""
        result = gateway.execute_gated(
            orchestrator_name="TDDOrchestrator",
            mode="IMPLEMENT",
            context={"request_summary": "add new feature"},
        )
        assert result is not None
        assert "template_id" in result
        assert result["template_id"] == "sdlc/implement-workflow"
        assert "status" in result
        assert "run_id" in result

    def test_gateway_execute_gated_fix_succeeds(self, gateway: Any) -> None:
        """execute_gated('FIX') must complete without crash."""
        result = gateway.execute_gated(
            orchestrator_name="RefactoringOrchestrator",
            mode="FIX",
            context={},
        )
        assert result["template_id"] == "sdlc/fix-workflow"

    def test_gateway_execute_gated_refactor_succeeds(self, gateway: Any) -> None:
        """execute_gated('REFACTOR') must complete without crash."""
        result = gateway.execute_gated(
            orchestrator_name="RefactoringOrchestrator",
            mode="REFACTOR",
            context={},
        )
        assert result["template_id"] == "quality/refactor-workflow"

    def test_gateway_execute_gated_debug_succeeds(self, gateway: Any) -> None:
        """execute_gated('DEBUG') must complete without crash."""
        result = gateway.execute_gated(
            orchestrator_name="DebuggerOrchestrator",
            mode="DEBUG",
            context={},
        )
        assert result["template_id"] == "debugging/multi-stack-debug-pipeline"

    def test_gateway_execute_gated_audit_succeeds(self, gateway: Any) -> None:
        """execute_gated('AUDIT') must complete without crash."""
        result = gateway.execute_gated(
            orchestrator_name="AuditOrchestrator",
            mode="AUDIT",
            context={},
        )
        assert result["template_id"] == "audit/audit-fix-pipeline"

    def test_gateway_exempt_mode_bypasses(self, gateway: Any) -> None:
        """Exempt modes (QUERY, DESIGN, PLAN) bypass template routing."""
        result = gateway.execute_gated(
            orchestrator_name="AnyOrchestrator",
            mode="QUERY",
            context={},
        )
        assert result["status"] == "exempt"
        assert result["template_id"] is None


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 4: SQLite trace logging works with correct schema
# ════════════════════════════════════════════════════════════════════════════

class TestGatewaySQLiteTracing:
    """Gateway must write trace rows to SQLite with the correct schema."""

    def test_sqlite_trace_written_on_success(self, tmp_path: Path) -> None:
        """execute_gated must write a row to workflow_runs with correct columns."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        db_path = tmp_path / "test-traces.db"
        gateway = WorkflowGateway(db_path=db_path)

        result = gateway.execute_gated(
            orchestrator_name="TDDOrchestrator",
            mode="IMPLEMENT",
            context={},
        )

        # Verify the trace was written
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute("SELECT * FROM workflow_runs").fetchall()
        conn.close()

        assert len(rows) == 1
        # Verify columns are correct (run_id, orchestrator, mode, template_id, ...)
        row = rows[0]
        assert row[0] == result["run_id"]  # run_id
        assert row[1] == "TDDOrchestrator"  # orchestrator
        assert row[2] == "IMPLEMENT"  # mode
        assert row[3] == "sdlc/implement-workflow"  # template_id

    def test_sqlite_schema_has_correct_columns(self, tmp_path: Path) -> None:
        """workflow_runs table must have the gateway-expected columns."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        db_path = tmp_path / "test-traces.db"
        WorkflowGateway(db_path=db_path)

        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("PRAGMA table_info(workflow_runs)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        expected = {
            "run_id", "orchestrator", "mode", "template_id", "status",
            "steps_completed", "duration_ms", "started_at", "completed_at", "error",
        }
        assert columns == expected, f"Schema mismatch: got {columns}, expected {expected}"

    def test_sqlite_migration_from_old_schema(self, tmp_path: Path) -> None:
        """Gateway must migrate the old (Phase 98) schema to the new one."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        db_path = tmp_path / "test-migration.db"
        # Create old schema
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE workflow_runs (
                id INTEGER PRIMARY KEY,
                session_id TEXT NOT NULL,
                loop_name TEXT,
                invoked_at REAL DEFAULT (unixepoch()),
                result TEXT
            )
        """)
        conn.execute(
            "INSERT INTO workflow_runs (session_id, loop_name, result) VALUES (?, ?, ?)",
            ("old-session", "old-loop", "old-result"),
        )
        conn.commit()
        conn.close()

        # Instantiate gateway — should detect and migrate
        gateway = WorkflowGateway(db_path=db_path)

        # Verify new schema
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("PRAGMA table_info(workflow_runs)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        assert "run_id" in columns, "Migration must create 'run_id' column"
        assert "session_id" not in columns, "Migration must remove old 'session_id' column"


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 5: enforce_gateway decorator end-to-end
# ════════════════════════════════════════════════════════════════════════════

class TestEnforceGatewayEndToEnd:
    """@enforce_gateway must route through real gateway when enabled."""

    def test_enforce_gateway_routes_through_real_gateway(self, tmp_path: Path) -> None:
        """When PHASE90_GATEWAY_ENABLED=True, decorator must use real gateway."""
        from cortex.core.workflow_enforcement_mixin import (
            WorkflowEnforcementMixin,
            enforce_gateway,
        )
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        class TestOrchestrator(WorkflowEnforcementMixin):
            PHASE90_GATEWAY_ENABLED = True

            @enforce_gateway
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Any:
                return {"result": "direct_bypass_should_not_happen"}

        orch = TestOrchestrator()
        # Inject a real gateway with temp DB
        orch._gateway = WorkflowGateway(db_path=tmp_path / "test.db")

        result = orch.execute_operation("IMPLEMENT", {"summary": "test"})

        # Should get gateway result, not direct bypass
        assert isinstance(result, dict)
        assert result.get("template_id") == "sdlc/implement-workflow"
        assert result.get("result") != "direct_bypass_should_not_happen"

    def test_enforce_gateway_disabled_falls_through(self) -> None:
        """When PHASE90_GATEWAY_ENABLED=False, decorator is transparent."""
        from cortex.core.workflow_enforcement_mixin import (
            WorkflowEnforcementMixin,
            enforce_gateway,
        )

        class TestOrchestrator(WorkflowEnforcementMixin):
            PHASE90_GATEWAY_ENABLED = False

            @enforce_gateway
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Any:
                return {"result": "direct_execution"}

        orch = TestOrchestrator()
        result = orch.execute_operation("IMPLEMENT", {})
        assert result == {"result": "direct_execution"}


# AC_COMPLETE: AC-P99-GCI-001 ✅ Gateway→Composer integration tests
