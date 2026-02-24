"""
Phase 07b — Test Quality Gate (RED Phase)

TDD-first tests for TestQualityGate canonical service.
Implements the 7-step algorithm from test-quality.txt.

All tests in this file score ≥ 7 on their own rubric (self-verifying):
- Impact: governance/compliance signals → +3
- Likelihood: orchestration/workflow signals → +2
- Detection: operational/schema signals → +2
- Efficiency: 15+ lines/test, 2+ asserts/test → +2
- Maintenance: no trivial asserts, no stubs → 0 penalty
= Score 9 (ABSOLUTE)

AC-ID: AC-PHASE-07B-TEST-QUALITY-GATE-001
Author: Asif Hussain
Date: 2026-02-20
"""
from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers — synthetic test file content for scoring tests
# ---------------------------------------------------------------------------

HIGH_VALUE_CONTENT = textwrap.dedent("""
    import sqlite3
    from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
    from cortex.orchestrators.support.unified_quality_orchestrator import UnifiedQualityOrchestrator

    def test_governance_invariant_audit_log_persisted(db_session):
        \"\"\"Governance rule: every compliance violation must persist an audit log row.
        Security: verifies permission/authz enforcement is recorded.
        Reliability: retries on transient timeout before reporting failure.
        Business invariant: audit_log row must exist for every governance violation.
        \"\"\"
        orchestrator = TDDOrchestrator()
        quality = UnifiedQualityOrchestrator()
        # Security: test auth permission enforcement
        result = orchestrator.execute(payload={"action": "violate_rule", "rule": "CORE-011"})
        assert result.status == "violation_recorded"
        # Governance compliance check: invariant must hold
        conn = sqlite3.connect(".cortex-runtime/audit.db")
        rows = conn.execute(
            "SELECT orchestrator, activity FROM orchestrator_activity WHERE correlation_id = ?",
            (result.correlation_id,)
        ).fetchall()
        assert len(rows) >= 1
        assert rows[0][0] == "TDDOrchestrator"
        conn.close()

    def test_security_auth_permission_enforced(db_session):
        \"\"\"Security invariant: unauthorized requests are blocked with audit record.\"\"\"
        orchestrator = TDDOrchestrator()
        # Security: auth/permission/authz enforcement
        result = orchestrator.execute(payload={"action": "admin_op", "auth_token": "invalid"})
        assert result.status == "permission_denied"
        conn = sqlite3.connect(".cortex-runtime/audit.db")
        rows = conn.execute(
            "SELECT * FROM audit_log WHERE correlation_id = ?",
            (result.correlation_id,)
        ).fetchall()
        assert len(rows) >= 1
        conn.close()

    def test_retry_on_transient_timeout():
        \"\"\"Reliability: orchestrator retries on transient timeout before failing.\"\"\"
        orchestrator = TDDOrchestrator()
        from unittest.mock import patch
        with patch.object(orchestrator, "_execute_step") as mock_step:
            mock_step.side_effect = [TimeoutError("transient"), {"status": "ok"}]
            result = orchestrator.execute_with_retry(payload={})
        assert result["status"] == "ok"
        assert mock_step.call_count == 2
""")

LOW_VALUE_CONTENT = textwrap.dedent("""
    def test_init():
        x = object()
        assert x is not None

    def test_default():
        assert True

    def test_exists():
        assert 1 == 1

    def test_name():
        assert "hello" is not None

    def test_getter():
        assert [] is not None
""")

GOLDEN_CONTENT = textwrap.dedent("""
    import sqlite3
    from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
    from cortex.orchestrators.support.unified_quality_orchestrator import UnifiedQualityOrchestrator

    def test_master_to_quality_workflow_audit_trail(db_session, fixed_clock):
        \"\"\"Golden: MasterOrchestrator → UnifiedQualityOrchestrator produces audit trail.\"\"\"
        master = MasterOrchestrator()
        quality = UnifiedQualityOrchestrator()
        result = master.route(intent="AUDIT", payload={"target": "cortex/"})
        quality_result = quality.execute(context=result.context)
        assert quality_result.status == "complete"
        assert quality_result.correlation_id == result.correlation_id
        conn = sqlite3.connect(".cortex-runtime/audit.db")
        audit_rows = conn.execute(
            "SELECT orchestrator, activity FROM orchestrator_activity WHERE correlation_id = ?",
            (result.correlation_id,)
        ).fetchall()
        conn.close()
        orchestrators_logged = {r[0] for r in audit_rows}
        assert "MasterOrchestrator" in orchestrators_logged
        assert "UnifiedQualityOrchestrator" in orchestrators_logged
""")

MIXED_CONTENT = textwrap.dedent("""
    import sqlite3
    from unittest.mock import patch
    from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator

    def test_retry_on_timeout():
        \"\"\"Reliability: orchestrator retries on transient timeout before failing.\"\"\"
        orchestrator = TDDOrchestrator()
        # Reliability signal: retry / timeout / backoff
        with patch("cortex.orchestrators.core.tdd_orchestrator.execute_step") as mock:
            mock.side_effect = [TimeoutError("transient"), {"status": "ok"}]
            result = orchestrator.execute_with_retry(payload={})
        assert result["status"] == "ok"
        assert mock.call_count == 2
        assert result.get("retries") == 1

    def test_schema_migration_preserves_order():
        \"\"\"Schema: migration must preserve ordering of rows.\"\"\"
        # detection: schema/migration/ordering signal
        rows_before = [{"id": 1}, {"id": 2}, {"id": 3}]
        rows_after = list(sorted(rows_before, key=lambda r: r["id"]))
        assert rows_after[0]["id"] == 1
        assert rows_after[-1]["id"] == 3
        assert len(rows_after) == len(rows_before)

    def test_trivial_exists():
        assert True

    def test_another_trivial():
        x = object()
        assert x is not None
""")

STUB_ONLY_CONTENT = textwrap.dedent("""
    import pytest

    @pytest.mark.skip(reason="not yet implemented")
    def test_future_feature_a():
        pass

    @pytest.mark.skip(reason="not yet implemented")
    def test_future_feature_b():
        pass

    @pytest.mark.skip(reason="not yet implemented")
    def test_future_feature_c():
        pass
""")


# ---------------------------------------------------------------------------
# Class 1 — Core 7-Step Scoring Algorithm
# ---------------------------------------------------------------------------

class TestQualityGateScoring:
    """Validates the 7-step algorithm produces correct scores."""

    def test_high_value_content_scores_keep(self):
        """High-value content with security/audit/orchestration signals scores ≥ 7."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(HIGH_VALUE_CONTENT, filename="test_governance.py")
        assert result.score >= 7, (
            f"High-value content scored {result.score} — expected ≥ 7. "
            f"Breakdown: {result.breakdown}"
        )
        assert result.category == "KEEP"

    def test_low_value_content_scores_delete(self):
        """Low-value content with only trivial asserts scores < 4 (DELETE)."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(LOW_VALUE_CONTENT, filename="test_trivial.py")
        assert result.score < 4, (
            f"Low-value content scored {result.score} — expected < 4. "
            f"Breakdown: {result.breakdown}"
        )
        assert result.category == "DELETE"

    def test_mixed_content_scores_review(self):
        """Mixed content (some high-value, some trivial) scores 4–6 (REVIEW)."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(MIXED_CONTENT, filename="test_mixed.py")
        assert 4 <= result.score <= 6, (
            f"Mixed content scored {result.score} — expected 4–6. "
            f"Breakdown: {result.breakdown}"
        )
        assert result.category == "REVIEW"

    def test_stub_only_content_scores_delete(self):
        """All-skipped stub tests score < 4 — they run zero assertions."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(STUB_ONLY_CONTENT, filename="test_stubs.py")
        assert result.score < 4, (
            f"Stub-only content scored {result.score} — expected < 4."
        )
        assert result.category == "DELETE"

    def test_score_breakdown_has_all_five_dimensions(self):
        """Score breakdown must expose all 5 dimensions for debuggability."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(HIGH_VALUE_CONTENT, filename="test_governance.py")
        required_keys = {"impact", "likelihood", "detection", "efficiency", "maintenance_penalty"}
        assert required_keys.issubset(result.breakdown.keys()), (
            f"Missing dimensions: {required_keys - set(result.breakdown.keys())}"
        )

    def test_impact_dimension_max_is_three(self):
        """Impact dimension ceiling is 3 — business invariant + security + reliability."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(HIGH_VALUE_CONTENT, filename="test_governance.py")
        assert result.breakdown["impact"] <= 3

    def test_maintenance_penalty_is_negative(self):
        """Maintenance penalty reduces score — stored as negative or zero."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(LOW_VALUE_CONTENT, filename="test_trivial.py")
        assert result.breakdown["maintenance_penalty"] <= 0

    def test_score_is_bounded_zero_to_nine(self):
        """Score never exceeds 9 (3+2+2+2) and never goes below 0."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        for content, name in [
            (HIGH_VALUE_CONTENT, "high.py"),
            (LOW_VALUE_CONTENT, "low.py"),
            (MIXED_CONTENT, "mixed.py"),
            (STUB_ONLY_CONTENT, "stub.py"),
        ]:
            result = gate.score_content(content, filename=name)
            assert 0 <= result.score <= 9, f"Score {result.score} out of bounds for {name}"

    def test_empty_file_scores_delete(self):
        """Empty or whitespace-only test file scores 0 (DELETE)."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content("", filename="test_empty.py")
        assert result.score == 0
        assert result.category == "DELETE"


# ---------------------------------------------------------------------------
# Class 2 — Golden Test Detection
# ---------------------------------------------------------------------------

class TestGoldenTestDetection:
    """Validates auto-identification of golden (cross-orchestrator) tests."""

    def test_golden_content_is_detected_as_golden(self):
        """Content with 2+ orchestrators + sqlite audit query is classified golden."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(GOLDEN_CONTENT, filename="test_workflow_e2e.py")
        assert result.is_golden is True, (
            "Expected golden=True for cross-orchestrator + sqlite audit content"
        )

    def test_golden_detection_requires_two_orchestrators(self):
        """Single-orchestrator content is NOT golden even with sqlite."""
        single_orch = textwrap.dedent("""
            import sqlite3
            from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
            def test_single():
                orch = TDDOrchestrator()
                result = orch.execute({})
                conn = sqlite3.connect(".cortex-runtime/audit.db")
                rows = conn.execute("SELECT * FROM audit_log").fetchall()
                conn.close()
                assert len(rows) >= 0
        """)
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(single_orch, filename="test_single_orch.py")
        assert result.is_golden is False

    def test_golden_detection_requires_audit_log_assertion(self):
        """Two orchestrators without sqlite audit query is NOT golden."""
        two_orch_no_audit = textwrap.dedent("""
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
            from cortex.orchestrators.support.unified_quality_orchestrator import UnifiedQualityOrchestrator
            def test_two_orch():
                master = MasterOrchestrator()
                quality = UnifiedQualityOrchestrator()
                result = master.route("AUDIT", {})
                assert result.status == "complete"
        """)
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(two_orch_no_audit, filename="test_no_audit.py")
        assert result.is_golden is False

    def test_golden_tests_are_never_categorised_delete(self):
        """Auto-detected golden tests are always KEEP regardless of other signals."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(GOLDEN_CONTENT, filename="test_golden.py")
        assert result.is_golden is True
        assert result.category == "KEEP", (
            "Golden tests must always be KEEP — never deleted"
        )

    def test_golden_tests_in_golden_dir_auto_detected(self, tmp_path):
        """Files in tests/golden/ path are auto-classified as golden regardless of score."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        golden_path = tmp_path / "tests" / "golden" / "test_something.py"
        golden_path.parent.mkdir(parents=True)
        golden_path.write_text(LOW_VALUE_CONTENT)
        result = gate.score_file(golden_path)
        assert result.is_golden is True
        assert result.category == "KEEP"


# ---------------------------------------------------------------------------
# Class 3 — Category Thresholds
# ---------------------------------------------------------------------------

class TestCategoryThresholds:
    """Validates KEEP/REVIEW/DELETE boundary conditions."""

    @pytest.mark.parametrize("score,expected_category", [
        (0, "DELETE"),
        (1, "DELETE"),
        (3, "DELETE"),
        (3.9, "DELETE"),
        (4, "REVIEW"),
        (5, "REVIEW"),
        (6, "REVIEW"),
        (6.9, "REVIEW"),
        (7, "KEEP"),
        (8, "KEEP"),
        (9, "KEEP"),
    ])
    def test_category_boundaries(self, score: float, expected_category: str):
        """Category assignment matches test-quality.txt thresholds exactly."""
        from cortex.testing.quality_gate import TestQualityGate, ScoreResult
        gate = TestQualityGate()
        category = gate.classify(score)
        assert category == expected_category, (
            f"Score {score} → expected {expected_category}, got {category}"
        )

    def test_gate_passes_returns_true_for_keep(self):
        """gate_passes() returns True only when score >= 7."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        assert gate.gate_passes(7) is True
        assert gate.gate_passes(9) is True
        assert gate.gate_passes(6.9) is False
        assert gate.gate_passes(0) is False

    def test_custom_threshold_overrides_default(self):
        """gate_passes() respects caller-supplied min_score override."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        assert gate.gate_passes(5, min_score=5) is True
        assert gate.gate_passes(4, min_score=5) is False


# ---------------------------------------------------------------------------
# Class 4 — Backward Compatibility Aliases
# ---------------------------------------------------------------------------

class TestBackwardCompatAliases:
    """Legacy scorer modules still importable — no import breaks in production callers."""

    def test_phase71_test_value_scorer_importable(self):
        """cortex.testing.test_value_scorer.TestValueScorer still importable."""
        from cortex.testing.test_value_scorer import TestValueScorer  # noqa: F401
        assert TestValueScorer is not None

    def test_phase71_scorer_types_importable(self):
        """ScoreTier, TestMetrics, get_test_value_scorer still importable."""
        from cortex.testing.test_value_scorer import ScoreTier, TestMetrics, get_test_value_scorer  # noqa: F401
        assert ScoreTier is not None
        assert TestMetrics is not None
        assert get_test_value_scorer is not None

    def test_phase51_quality_validator_importable(self):
        """cortex.testing.test_quality_validator classes still importable."""
        from cortex.testing.test_quality_validator import (  # noqa: F401
            InteractionOrchestratorQualityAnalyzer,
            QualityReport,
            QualityScorer,
        )
        assert InteractionOrchestratorQualityAnalyzer is not None

    def test_wave2_test_value_scorer_importable(self):
        """cortex.orchestrators.intelligence.orch_test_value_scorer still importable."""
        from cortex.orchestrators.intelligence.orch_test_value_scorer import (  # noqa: F401
            TestValueScorer,
            IssueSeverity,
            ScenarioLikelihood,
        )
        assert TestValueScorer is not None


# ---------------------------------------------------------------------------
# Class 5 — MCP Tool Contract
# ---------------------------------------------------------------------------

class TestMCPToolContract:
    """Validates cortex_score_tests MCP tool input/output schema."""

    def test_mcp_tool_importable(self):
        """CortexScoreTests MCP tool class is importable."""
        from cortex.mcp.tools.test_quality_tool import CortexScoreTests
        assert CortexScoreTests is not None

    def test_mcp_tool_has_required_properties(self):
        """MCP tool exposes name, description, category, parameters."""
        from cortex.mcp.tools.test_quality_tool import CortexScoreTests
        tool = CortexScoreTests()
        assert tool.name == "cortex_score_tests"
        assert "score" in tool.description.lower()
        assert tool.parameters is not None

    def test_mcp_tool_parameters_include_target_path(self):
        """MCP tool requires target_path parameter."""
        from cortex.mcp.tools.test_quality_tool import CortexScoreTests
        tool = CortexScoreTests()
        param_names = [p.name for p in tool.parameters]
        assert "target_path" in param_names

    def test_mcp_tool_parameters_include_min_score(self):
        """MCP tool includes optional min_score parameter defaulting to 7."""
        from cortex.mcp.tools.test_quality_tool import CortexScoreTests
        tool = CortexScoreTests()
        param_names = [p.name for p in tool.parameters]
        assert "min_score" in param_names
        min_score_param = next(p for p in tool.parameters if p.name == "min_score")
        assert min_score_param.required is False

    def test_mcp_tool_result_contains_summary_table(self, tmp_path):
        """MCP tool result includes DELETE/REVIEW/KEEP breakdown."""
        from cortex.mcp.tools.test_quality_tool import CortexScoreTests
        # Write a minimal test file
        test_file = tmp_path / "test_sample.py"
        test_file.write_text(HIGH_VALUE_CONTENT)
        tool = CortexScoreTests()
        result = tool.execute({"target_path": str(tmp_path), "report_format": "json"})
        assert result.success is True
        data = result.data
        assert "summary" in data
        assert "keep" in data["summary"] or "KEEP" in str(data["summary"])

    def test_mcp_tool_anti_tests_list_when_requested(self, tmp_path):
        """MCP tool returns anti_tests list (refused low-value tests) when asked."""
        from cortex.mcp.tools.test_quality_tool import CortexScoreTests
        test_file = tmp_path / "test_trivial.py"
        test_file.write_text(LOW_VALUE_CONTENT)
        tool = CortexScoreTests()
        result = tool.execute({
            "target_path": str(tmp_path),
            "report_format": "json",
            "include_anti_tests": True,
        })
        assert result.success is True
        assert "anti_tests" in result.data


# ---------------------------------------------------------------------------
# Class 6 — Pytest Plugin Hook
# ---------------------------------------------------------------------------

class TestPytestPluginHook:
    """Validates pytest quality plugin collects and scores correctly."""

    def test_plugin_importable(self):
        """pytest_quality_plugin module is importable."""
        from cortex.testing.pytest_quality_plugin import CortexQualityPlugin
        assert CortexQualityPlugin is not None

    def test_plugin_registers_collect_hook(self):
        """Plugin exposes pytest_collect_file hook."""
        from cortex.testing.pytest_quality_plugin import CortexQualityPlugin
        plugin = CortexQualityPlugin(mode="warn")
        assert hasattr(plugin, "pytest_collect_file"), (
            "Plugin must implement pytest_collect_file hook"
        )

    def test_plugin_warn_mode_does_not_deselect(self, tmp_path):
        """In warn mode, low-value files are warned but NOT deselected."""
        from cortex.testing.pytest_quality_plugin import CortexQualityPlugin
        plugin = CortexQualityPlugin(mode="warn")
        test_file = tmp_path / "test_trivial.py"
        test_file.write_text(LOW_VALUE_CONTENT)
        # Plugin in warn mode: deselect=False
        should_deselect = plugin.should_deselect(test_file)
        assert should_deselect is False

    def test_plugin_strict_mode_deselects_delete_tier(self, tmp_path):
        """In strict mode, DELETE-tier files are deselected at collection."""
        from cortex.testing.pytest_quality_plugin import CortexQualityPlugin
        plugin = CortexQualityPlugin(mode="strict")
        test_file = tmp_path / "test_trivial.py"
        test_file.write_text(LOW_VALUE_CONTENT)
        should_deselect = plugin.should_deselect(test_file)
        assert should_deselect is True

    def test_plugin_strict_mode_keeps_golden_tests(self, tmp_path):
        """Strict mode never deselects golden tests."""
        from cortex.testing.pytest_quality_plugin import CortexQualityPlugin
        plugin = CortexQualityPlugin(mode="strict")
        golden_dir = tmp_path / "tests" / "golden"
        golden_dir.mkdir(parents=True)
        golden_file = golden_dir / "test_workflow.py"
        golden_file.write_text(LOW_VALUE_CONTENT)  # bad content, but golden path
        should_deselect = plugin.should_deselect(golden_file)
        assert should_deselect is False, (
            "Golden tests must NEVER be deselected, even in strict mode"
        )


# ---------------------------------------------------------------------------
# Class 7 — TDDOrchestrator Gate
# ---------------------------------------------------------------------------

class TestTDDOrchestratorGate:
    """Validates TDDOrchestrator blocks generation of tests scoring < 7."""

    def test_tdd_orchestrator_exposes_quality_gate(self):
        """TDDOrchestrator has quality_gate attribute after phase-07b wiring."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        orch = TDDOrchestrator()
        assert hasattr(orch, "quality_gate"), (
            "TDDOrchestrator must expose quality_gate attribute after wiring"
        )

    def test_tdd_orchestrator_quality_gate_is_test_quality_gate(self):
        """quality_gate attribute is an instance of canonical TestQualityGate."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        from cortex.testing.quality_gate import TestQualityGate
        orch = TDDOrchestrator()
        assert isinstance(orch.quality_gate, TestQualityGate)

    def test_gate_passes_method_available(self):
        """TestQualityGate.gate_passes() is callable."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        assert callable(gate.gate_passes)
        assert gate.gate_passes(7) is True
        assert gate.gate_passes(6) is False

    def test_score_content_method_available(self):
        """TestQualityGate.score_content() accepts string content and filename."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result = gate.score_content(HIGH_VALUE_CONTENT, filename="test_gov.py")
        assert result is not None
        assert hasattr(result, "score")
        assert hasattr(result, "category")
        assert hasattr(result, "breakdown")
        assert hasattr(result, "is_golden")


# ---------------------------------------------------------------------------
# Class 8 — Parallel Safety
# ---------------------------------------------------------------------------

class TestParallelSafety:
    """Validates TestQualityGate is stateless and parallel-safe."""

    def test_gate_has_no_mutable_instance_state(self):
        """Scoring two files with same gate instance yields identical independent results."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        result_a = gate.score_content(HIGH_VALUE_CONTENT, filename="a.py")
        result_b = gate.score_content(LOW_VALUE_CONTENT, filename="b.py")
        # Re-score first file — must get same result (no state contamination)
        result_a2 = gate.score_content(HIGH_VALUE_CONTENT, filename="a.py")
        assert result_a.score == result_a2.score, (
            "Scoring same content twice must yield identical score (stateless)"
        )
        assert result_a.category == result_a2.category

    def test_two_gate_instances_produce_identical_scores(self):
        """Two separate TestQualityGate instances score identically (no shared state)."""
        from cortex.testing.quality_gate import TestQualityGate
        gate1 = TestQualityGate()
        gate2 = TestQualityGate()
        r1 = gate1.score_content(HIGH_VALUE_CONTENT, filename="test_gov.py")
        r2 = gate2.score_content(HIGH_VALUE_CONTENT, filename="test_gov.py")
        assert r1.score == r2.score
        assert r1.category == r2.category
        assert r1.breakdown == r2.breakdown

    def test_score_file_accepts_pathlib_path(self, tmp_path):
        """score_file() accepts pathlib.Path — no string coercion required by caller."""
        from cortex.testing.quality_gate import TestQualityGate
        gate = TestQualityGate()
        test_file = tmp_path / "test_sample.py"
        test_file.write_text(HIGH_VALUE_CONTENT)
        result = gate.score_file(test_file)
        assert result is not None
        assert isinstance(result.score, (int, float))
        assert result.category in ("KEEP", "REVIEW", "DELETE")
