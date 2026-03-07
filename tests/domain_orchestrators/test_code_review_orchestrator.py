"""Tests for CodeReviewOrchestrator — phase-132-b (GAP-132-02).

TDD RED → GREEN cycle. Tests must FAIL before implementation, PASS after.

Coverage:
  - REVIEW intent in IntentType enum
  - CodeReviewOrchestrator: verdict logic (APPROVE/REQUEST_CHANGES/BLOCK)
  - cortex_review MCP tool: all 5 operations
  - OWASP knowledge YAML files exist and are parseable
  - code-review-workflow.yaml exists

CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# 1. REVIEW intent in IntentType
# ─────────────────────────────────────────────────────────────────────────────


class TestReviewIntentType:
    def test_review_in_intent_type(self) -> None:
        from cortex.models.canonical_enums import IntentType

        assert hasattr(IntentType, "REVIEW")

    def test_review_value_is_review(self) -> None:
        from cortex.models.canonical_enums import IntentType

        assert IntentType.REVIEW.value == "review"


# ─────────────────────────────────────────────────────────────────────────────
# 2. CodeReviewOrchestrator — import + instantiation
# ─────────────────────────────────────────────────────────────────────────────


class TestCodeReviewOrchestratorImport:
    def test_module_importable(self) -> None:
        from cortex.orchestrators.domain import code_review_orchestrator  # noqa: F401

    def test_class_importable(self) -> None:
        from cortex.orchestrators.domain.code_review_orchestrator import CodeReviewOrchestrator  # noqa: F401

    def test_instantiates_without_args(self) -> None:
        from cortex.orchestrators.domain.code_review_orchestrator import CodeReviewOrchestrator

        orchestrator = CodeReviewOrchestrator()
        assert orchestrator is not None

    def test_has_review_method(self) -> None:
        from cortex.orchestrators.domain.code_review_orchestrator import CodeReviewOrchestrator

        assert hasattr(CodeReviewOrchestrator, "review")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Verdict logic
# ─────────────────────────────────────────────────────────────────────────────


class TestCodeReviewVerdictLogic:
    """Test the APPROVE / REQUEST_CHANGES / BLOCK verdict rules."""

    def _make_diff(self, lines: list[str]) -> str:
        return "\n".join(lines)

    def test_clean_diff_produces_approve(self) -> None:
        from cortex.orchestrators.domain.code_review_orchestrator import CodeReviewOrchestrator

        orchestrator = CodeReviewOrchestrator()
        result = orchestrator.review(diff="+ print('hello world')\n", context={})
        assert result["verdict"] in ("APPROVE", "REQUEST_CHANGES", "BLOCK")
        # Clean diff — no critical patterns — should not BLOCK
        assert result["verdict"] != "BLOCK"

    def test_p0_finding_produces_block(self) -> None:
        from cortex.orchestrators.domain.code_review_orchestrator import CodeReviewOrchestrator

        orchestrator = CodeReviewOrchestrator()
        # SQL injection pattern
        diff = '+ query = "SELECT * FROM users WHERE id = " + user_input\n'
        result = orchestrator.review(diff=diff, context={})
        assert result["verdict"] == "BLOCK"

    def test_p1_finding_produces_request_changes(self) -> None:
        from cortex.orchestrators.domain.code_review_orchestrator import CodeReviewOrchestrator

        orchestrator = CodeReviewOrchestrator()
        # Hardcoded password (P1)
        diff = '+ password = "mysecret123"\n'
        result = orchestrator.review(diff=diff, context={})
        assert result["verdict"] in ("REQUEST_CHANGES", "BLOCK")

    def test_result_has_findings(self) -> None:
        from cortex.orchestrators.domain.code_review_orchestrator import CodeReviewOrchestrator

        orchestrator = CodeReviewOrchestrator()
        result = orchestrator.review(diff="+ x = 1\n", context={})
        assert "findings" in result
        assert isinstance(result["findings"], list)

    def test_result_has_verdict(self) -> None:
        from cortex.orchestrators.domain.code_review_orchestrator import CodeReviewOrchestrator

        orchestrator = CodeReviewOrchestrator()
        result = orchestrator.review(diff="+ x = 1\n", context={})
        assert "verdict" in result

    def test_result_has_summary(self) -> None:
        from cortex.orchestrators.domain.code_review_orchestrator import CodeReviewOrchestrator

        orchestrator = CodeReviewOrchestrator()
        result = orchestrator.review(diff="+ x = 1\n", context={})
        assert "summary" in result

    def test_verdict_values_are_canonical(self) -> None:
        from cortex.orchestrators.domain.code_review_orchestrator import CodeReviewOrchestrator, VALID_VERDICTS

        assert set(VALID_VERDICTS) == {"APPROVE", "REQUEST_CHANGES", "BLOCK"}


# ─────────────────────────────────────────────────────────────────────────────
# 4. OWASP knowledge YAMLs
# ─────────────────────────────────────────────────────────────────────────────

_REGISTRY_ROOT = Path(__file__).parents[2] / "cortex-registry"


class TestOwaspKnowledgeYamls:
    def test_owasp_top10_exists(self) -> None:
        yaml_path = _REGISTRY_ROOT / "knowledge" / "security" / "owasp-top-10.yaml"
        assert yaml_path.exists(), f"Missing: {yaml_path}"

    def test_owasp_top10_parseable(self) -> None:
        import yaml

        yaml_path = _REGISTRY_ROOT / "knowledge" / "security" / "owasp-top-10.yaml"
        data = yaml.safe_load(yaml_path.read_text())
        assert isinstance(data, dict)

    def test_owasp_api_security_exists(self) -> None:
        yaml_path = _REGISTRY_ROOT / "knowledge" / "security" / "owasp-api-security.yaml"
        assert yaml_path.exists(), f"Missing: {yaml_path}"

    def test_owasp_api_security_parseable(self) -> None:
        import yaml

        yaml_path = _REGISTRY_ROOT / "knowledge" / "security" / "owasp-api-security.yaml"
        data = yaml.safe_load(yaml_path.read_text())
        assert isinstance(data, dict)

    def test_owasp_top10_has_risks(self) -> None:
        import yaml

        yaml_path = _REGISTRY_ROOT / "knowledge" / "security" / "owasp-top-10.yaml"
        data = yaml.safe_load(yaml_path.read_text())
        assert "risks" in data
        assert len(data["risks"]) >= 10


# ─────────────────────────────────────────────────────────────────────────────
# 5. code-review-workflow.yaml
# ─────────────────────────────────────────────────────────────────────────────


class TestCodeReviewWorkflowYaml:
    def test_workflow_yaml_exists(self) -> None:
        yaml_path = (
            _REGISTRY_ROOT
            / "workflows"
            / "templates"
            / "sdlc"
            / "code-review-workflow.yaml"
        )
        assert yaml_path.exists(), f"Missing: {yaml_path}"

    def test_workflow_yaml_parseable(self) -> None:
        import yaml

        yaml_path = (
            _REGISTRY_ROOT
            / "workflows"
            / "templates"
            / "sdlc"
            / "code-review-workflow.yaml"
        )
        data = yaml.safe_load(yaml_path.read_text())
        assert isinstance(data, dict)

    def test_workflow_yaml_has_stages(self) -> None:
        import yaml

        yaml_path = (
            _REGISTRY_ROOT
            / "workflows"
            / "templates"
            / "sdlc"
            / "code-review-workflow.yaml"
        )
        data = yaml.safe_load(yaml_path.read_text())
        assert "stages" in data
        assert len(data["stages"]) >= 6


# ─────────────────────────────────────────────────────────────────────────────
# 6. cortex_review MCP tool
# ─────────────────────────────────────────────────────────────────────────────


class TestCortexReviewMcpTool:
    def test_cortex_review_in_registry(self) -> None:
        from cortex.mcp.mcp_registry import ToolRegistry

        registry = ToolRegistry()
        tool_ids = [t.id for t in registry.list_all()]
        assert "cortex_review" in tool_ids

    def test_cortex_review_has_review_op(self) -> None:
        from cortex.mcp.mcp_registry import ToolRegistry

        registry = ToolRegistry()
        tool = next(t for t in registry.list_all() if t.id == "cortex_review")
        assert "review" in (tool.operations or [])

    def test_cortex_review_has_findings_op(self) -> None:
        from cortex.mcp.mcp_registry import ToolRegistry

        registry = ToolRegistry()
        tool = next(t for t in registry.list_all() if t.id == "cortex_review")
        assert "findings" in (tool.operations or [])

    def test_cortex_review_has_history_op(self) -> None:
        from cortex.mcp.mcp_registry import ToolRegistry

        registry = ToolRegistry()
        tool = next(t for t in registry.list_all() if t.id == "cortex_review")
        assert "history" in (tool.operations or [])

    def test_cortex_review_has_health_op(self) -> None:
        from cortex.mcp.mcp_registry import ToolRegistry

        registry = ToolRegistry()
        tool = next(t for t in registry.list_all() if t.id == "cortex_review")
        assert "health" in (tool.operations or [])

    def test_tool_file_exists(self) -> None:
        tool_path = Path(__file__).parents[2] / "cortex" / "mcp" / "tools" / "cortex_review.py"
        assert tool_path.exists(), f"Missing: {tool_path}"

    def test_registry_tool_count_is_36(self) -> None:
        from cortex.mcp.mcp_registry import ToolRegistry

        registry = ToolRegistry()
        count = len(registry.list_all())
        assert count == 36, f"Expected 36 tools, got {count}"
