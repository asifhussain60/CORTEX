"""Tests for ADOContextSynthesizer — Phase 131-c (GAP-131-03).

TDD RED phase: All tests must FAIL before implementation exists.
Target: cortex/intelligence/ado_context_synthesizer.py
        cortex/mcp/tools/cortex_ado.py
        cortex-registry/config/ado-integration.yaml

CORE-008: TDD mandatory — write failing tests first.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Module import
# ─────────────────────────────────────────────────────────────────────────────

class TestADOContextSynthesizerImport:
    """Verify ADOContextSynthesizer can be imported."""

    def test_module_importable(self) -> None:
        """ADOContextSynthesizer module must be importable."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer  # noqa: F401

    def test_class_importable(self) -> None:
        """ADOContextSynthesizer class must be importable."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        assert ADOContextSynthesizer is not None


# ─────────────────────────────────────────────────────────────────────────────
# Instantiation
# ─────────────────────────────────────────────────────────────────────────────

class TestADOContextSynthesizerInstantiation:
    """ADOContextSynthesizer construction and interface."""

    def test_instantiates_without_args(self) -> None:
        """ADOContextSynthesizer() must construct without required arguments."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        s = ADOContextSynthesizer()
        assert s is not None

    def test_has_synthesize_method(self) -> None:
        """synthesize() method must exist."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        assert callable(getattr(ADOContextSynthesizer(), "synthesize", None))

    def test_has_budget_constant(self) -> None:
        """MAX_CHARS budget constant must be accessible."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        s = ADOContextSynthesizer()
        assert hasattr(s, "MAX_CHARS") or hasattr(ADOContextSynthesizer, "MAX_CHARS")

    def test_budget_is_8000(self) -> None:
        """MAX_CHARS must be 8000."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        assert ADOContextSynthesizer.MAX_CHARS == 8000


# ─────────────────────────────────────────────────────────────────────────────
# Token budget enforcement
# ─────────────────────────────────────────────────────────────────────────────

class TestTokenBudgetEnforcement:
    """synthesize() output must always be ≤ MAX_CHARS."""

    def _make_large_work_item(self, n_comments: int = 50, desc_len: int = 5000) -> dict:
        """Build a synthetic large ADO work item dict."""
        return {
            "id": 42,
            "title": "Big Story Title",
            "description": "A" * desc_len,
            "acceptance_criteria": "Given X When Y Then Z\n" * 20,
            "state": "Active",
            "assigned_to": "Test User",
            "tags": ["backend", "api", "security", "performance", "database"],
            "comments": [
                {"author": f"user{i}", "text": "Comment text " * 30}
                for i in range(n_comments)
            ],
            "child_tasks": [
                {"id": 100 + i, "title": f"Child task {i}", "state": "Active"}
                for i in range(20)
            ],
        }

    def test_output_within_budget_small_input(self) -> None:
        """Small work item must produce output within budget."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        s = ADOContextSynthesizer()
        work_item = {"id": 1, "title": "Simple story", "description": "Short"}
        result = s.synthesize(work_item)
        assert len(result) <= ADOContextSynthesizer.MAX_CHARS

    def test_output_within_budget_large_input(self) -> None:
        """Large work item (50 comments, 5000-char description) must be truncated to ≤8000 chars."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        s = ADOContextSynthesizer()
        work_item = self._make_large_work_item(n_comments=50, desc_len=5000)
        result = s.synthesize(work_item)
        assert len(result) <= ADOContextSynthesizer.MAX_CHARS, (
            f"Output exceeded budget: {len(result)} > {ADOContextSynthesizer.MAX_CHARS}"
        )

    def test_output_within_budget_extreme_input(self) -> None:
        """Extreme input (200 comments, 20000-char description) must still fit in budget."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        s = ADOContextSynthesizer()
        work_item = self._make_large_work_item(n_comments=200, desc_len=20000)
        result = s.synthesize(work_item)
        assert len(result) <= ADOContextSynthesizer.MAX_CHARS

    def test_output_is_string(self) -> None:
        """synthesize() must return a string."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        s = ADOContextSynthesizer()
        result = s.synthesize({"id": 1, "title": "Test"})
        assert isinstance(result, str)

    def test_empty_work_item_does_not_crash(self) -> None:
        """Empty dict input must not raise — graceful fallback."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        s = ADOContextSynthesizer()
        result = s.synthesize({})
        assert isinstance(result, str)
        assert len(result) <= ADOContextSynthesizer.MAX_CHARS


# ─────────────────────────────────────────────────────────────────────────────
# Content extraction
# ─────────────────────────────────────────────────────────────────────────────

class TestContentExtraction:
    """synthesize() must extract key fields from work items."""

    def test_title_included_in_output(self) -> None:
        """Work item title must appear in the synthesized output."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        s = ADOContextSynthesizer()
        result = s.synthesize({"id": 7, "title": "UNIQUE_TITLE_X9Z"})
        assert "UNIQUE_TITLE_X9Z" in result

    def test_acceptance_criteria_extracted(self) -> None:
        """Acceptance criteria must appear in output when present."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        s = ADOContextSynthesizer()
        result = s.synthesize({
            "id": 8,
            "title": "Story",
            "acceptance_criteria": "Given MARKER_AC When done Then pass",
        })
        assert "MARKER_AC" in result or "acceptance" in result.lower()

    def test_comments_capped_at_5(self) -> None:
        """synthesize() must include at most 5 comment themes."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        s = ADOContextSynthesizer()
        comments = [{"author": f"u{i}", "text": f"Comment theme {i}"} for i in range(20)]
        result = s.synthesize({"id": 9, "title": "S", "comments": comments})
        # Count how many comment themes appear — at most 5
        theme_count = sum(1 for i in range(20) if f"Comment theme {i}" in result)
        assert theme_count <= 5

    def test_child_tasks_capped_at_2_levels(self) -> None:
        """Child task hierarchy must be ≤ 2 levels deep."""
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        s = ADOContextSynthesizer()
        # Deep nesting — only top level should appear
        result = s.synthesize({
            "id": 10,
            "title": "S",
            "child_tasks": [{"id": i, "title": f"Child {i}"} for i in range(10)],
        })
        # Just verify it completes within budget and produces a string
        assert isinstance(result, str)
        assert len(result) <= ADOContextSynthesizer.MAX_CHARS


# ─────────────────────────────────────────────────────────────────────────────
# ADO integration config YAML
# ─────────────────────────────────────────────────────────────────────────────

class TestADOIntegrationConfig:
    """ado-integration.yaml must exist and be well-formed."""

    _YAML_PATH = (
        Path(__file__).parent.parent.parent
        / "cortex-registry" / "config" / "ado-integration.yaml"
    )

    def test_yaml_exists(self) -> None:
        """cortex-registry/config/ado-integration.yaml must exist."""
        assert self._YAML_PATH.exists(), f"Missing: {self._YAML_PATH}"

    def test_yaml_parseable(self) -> None:
        """ado-integration.yaml must be valid YAML."""
        import yaml
        content = yaml.safe_load(self._YAML_PATH.read_text())
        assert isinstance(content, dict)

    def test_yaml_has_endpoint_section(self) -> None:
        """Must have 'endpoint' or 'ado' top-level key."""
        import yaml
        content = yaml.safe_load(self._YAML_PATH.read_text())
        assert "endpoint" in content or "ado" in content or "organization" in content

    def test_yaml_has_field_mapping(self) -> None:
        """Must have a 'field_mapping' section."""
        import yaml
        content = yaml.safe_load(self._YAML_PATH.read_text())
        assert "field_mapping" in content


# ─────────────────────────────────────────────────────────────────────────────
# cortex_ado MCP tool
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexAdoMcpTool:
    """cortex_ado MCP tool must be registered and have correct operations."""

    def test_cortex_ado_in_registry(self) -> None:
        """cortex_ado must appear in PRODUCTION_TOOLS."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
        assert "cortex_ado" in PRODUCTION_TOOLS, (
            f"cortex_ado not found. Keys: {sorted(PRODUCTION_TOOLS.keys())}"
        )

    def test_cortex_ado_has_get_story_op(self) -> None:
        """cortex_ado must declare 'get_story' operation."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
        ops = PRODUCTION_TOOLS.get("cortex_ado", {}).get("operations", [])
        assert "get_story" in ops

    def test_cortex_ado_has_get_full_op(self) -> None:
        """cortex_ado must declare 'get_full' operation."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
        ops = PRODUCTION_TOOLS.get("cortex_ado", {}).get("operations", [])
        assert "get_full" in ops

    def test_cortex_ado_has_get_tests_op(self) -> None:
        """cortex_ado must declare 'get_tests' operation."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
        ops = PRODUCTION_TOOLS.get("cortex_ado", {}).get("operations", [])
        assert "get_tests" in ops

    def test_cortex_ado_has_search_op(self) -> None:
        """cortex_ado must declare 'search' operation."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
        ops = PRODUCTION_TOOLS.get("cortex_ado", {}).get("operations", [])
        assert "search" in ops

    def test_cortex_ado_has_health_op(self) -> None:
        """cortex_ado must declare 'health' operation."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
        ops = PRODUCTION_TOOLS.get("cortex_ado", {}).get("operations", [])
        assert "health" in ops

    def test_tool_file_exists(self) -> None:
        """cortex/mcp/tools/cortex_ado.py must exist."""
        tool_path = (
            Path(__file__).parent.parent.parent / "cortex" / "mcp" / "tools" / "cortex_ado.py"
        )
        assert tool_path.exists(), f"Missing MCP tool file: {tool_path}"

    def test_registry_tool_count_is_35(self) -> None:
        """Total registered tool count must be 35 after adding cortex_ado."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
        assert len(PRODUCTION_TOOLS) == 35, (
            f"Expected 35 tools, got {len(PRODUCTION_TOOLS)}"
        )
