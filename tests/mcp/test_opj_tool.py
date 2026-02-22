"""
Tests for cortex_query_opj MCP tool — Phase 52 Stage C.

AC-ID: AC-OPJ-PHASE52-MCP
TDD Phase: RED → GREEN → REFACTOR
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-050 (MCP-first)
"""

from __future__ import annotations

import yaml
import pytest
from pathlib import Path


import re


def _snake_test(name: str) -> str:
    """Mirror OPJWriter._snake() for consistent shard file naming in tests."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _seed(root: Path, outcome: str, orch: str, op: str, **kw) -> None:
    """Seed a minimal OPJ entry directly into the YAML shard."""
    from datetime import datetime, timezone
    snake = _snake_test(orch)
    d = root / "integration" / "patterns" / outcome
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{snake}.yaml"
    entry = {
        "pattern_id": f"OPJ-{snake.upper()[:20]}-20260222120000",
        "orchestrator": orch, "operation": op, "outcome": outcome,
        "confidence": kw.get("confidence", 0.8),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **{k: v for k, v in kw.items() if k != "confidence"},
    }
    existing = {"entries": []}
    if f.exists():
        existing = yaml.safe_load(f.read_text()) or {"entries": []}
    existing["entries"].append(entry)
    f.write_text(yaml.safe_dump(existing, sort_keys=False))


class TestCortexQueryOPJTool:
    """Tests for cortex_query_opj MCP tool function."""

    @pytest.fixture()
    def registry(self, tmp_path: Path) -> Path:
        """Pre-seeded temporary registry."""
        _seed(tmp_path, "success", "DigestSessionOrchestrator", "process",
              resolution="chunked ok", confidence=0.9)
        _seed(tmp_path, "failure", "DigestSessionOrchestrator", "process",
              error="binary file", attempted_fix="skip binary", confidence=0.7)
        _seed(tmp_path, "failure", "EnforcementOrchestrator", "holistic_gate",
              error="CORE-008 violated", attempted_fix="add test",
              avoid_in_future="write test first", confidence=0.95)
        return tmp_path

    def test_tool_returns_dict(self, registry: Path) -> None:
        """cortex_query_opj must return a dict."""
        from cortex.mcp.tools.opj_tool import cortex_query_opj

        result = cortex_query_opj(
            orchestrator="DigestSessionOrchestrator",
            operation="process",
            registry_root=str(registry),
        )
        assert isinstance(result, dict)

    def test_tool_returns_entries_key(self, registry: Path) -> None:
        """Result dict must contain an 'entries' list."""
        from cortex.mcp.tools.opj_tool import cortex_query_opj

        result = cortex_query_opj(
            orchestrator="DigestSessionOrchestrator",
            operation="process",
            registry_root=str(registry),
        )
        assert "entries" in result
        assert isinstance(result["entries"], list)

    def test_tool_outcome_filter_failure(self, registry: Path) -> None:
        """outcome_filter='failure' returns only failure entries."""
        from cortex.mcp.tools.opj_tool import cortex_query_opj

        result = cortex_query_opj(
            orchestrator="DigestSessionOrchestrator",
            operation="process",
            outcome_filter="failure",
            registry_root=str(registry),
        )
        for entry in result["entries"]:
            assert entry["outcome"] == "failure"

    def test_tool_outcome_filter_success(self, registry: Path) -> None:
        """outcome_filter='success' returns only success entries."""
        from cortex.mcp.tools.opj_tool import cortex_query_opj

        result = cortex_query_opj(
            orchestrator="DigestSessionOrchestrator",
            operation="process",
            outcome_filter="success",
            registry_root=str(registry),
        )
        for entry in result["entries"]:
            assert entry["outcome"] == "success"

    def test_tool_limit_respected(self, tmp_path: Path) -> None:
        """limit parameter caps the number of returned entries."""
        for i in range(8):
            _seed(tmp_path, "success", "TDDOrchestrator", "red_phase",
                  resolution=f"run {i}", confidence=0.8)

        from cortex.mcp.tools.opj_tool import cortex_query_opj

        result = cortex_query_opj(
            orchestrator="TDDOrchestrator",
            operation="red_phase",
            limit=3,
            registry_root=str(tmp_path),
        )
        assert len(result["entries"]) <= 3

    def test_tool_empty_journal_returns_empty_entries(self, tmp_path: Path) -> None:
        """Empty journal must return entries=[] without error."""
        (tmp_path / "integration" / "patterns").mkdir(parents=True, exist_ok=True)
        from cortex.mcp.tools.opj_tool import cortex_query_opj

        result = cortex_query_opj(
            orchestrator="PhantomOrchestrator",
            operation="ghost",
            registry_root=str(tmp_path),
        )
        assert result["entries"] == []
        assert result.get("error") is None

    def test_tool_returns_metadata(self, registry: Path) -> None:
        """Result must include total_found and query metadata."""
        from cortex.mcp.tools.opj_tool import cortex_query_opj

        result = cortex_query_opj(
            orchestrator="DigestSessionOrchestrator",
            operation="process",
            registry_root=str(registry),
        )
        assert "total_found" in result
        assert "orchestrator" in result
        assert "operation" in result

    def test_tool_no_orchestrator_filter_returns_all(self, registry: Path) -> None:
        """orchestrator=None with operation=None returns cross-orchestrator results."""
        from cortex.mcp.tools.opj_tool import cortex_query_opj

        result = cortex_query_opj(
            orchestrator=None,
            operation=None,
            registry_root=str(registry),
        )
        orchestrators = {e["orchestrator"] for e in result["entries"]}
        assert len(orchestrators) >= 2
