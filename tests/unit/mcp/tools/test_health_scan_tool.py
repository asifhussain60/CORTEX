"""Unit Tests — MCP health_scan_tool.py

Phase: PHASE-51
CORE: CORE-008 (TDD)
"""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Minimal workspace for MCP tool tests."""
    (tmp_path / "cortex").mkdir()
    (tmp_path / "cortex" / "__init__.py").write_text("")
    (tmp_path / "README.md").write_text("# Hi\n")
    (tmp_path / "SCREAMING.txt").write_text("bad\n")
    return tmp_path


class TestHealthScanTool:
    """MCP health_scan_tool — parameter validation and routing."""

    def test_scan_returns_dict(self, workspace: Path) -> None:
        from cortex.mcp.tools.health_scan_tool import cortex_health_scan

        result = cortex_health_scan(str(workspace), operation="scan")
        assert isinstance(result, dict)
        assert "health_score" in result
        assert "total_issues" in result

    def test_scan_nonexistent_workspace(self, tmp_path: Path) -> None:
        from cortex.mcp.tools.health_scan_tool import cortex_health_scan

        result = cortex_health_scan(str(tmp_path / "nope"), operation="scan")
        assert "error" in result

    def test_classify_operation(self, workspace: Path) -> None:
        from cortex.mcp.tools.health_scan_tool import cortex_health_scan

        result = cortex_health_scan(str(workspace), operation="classify")
        assert isinstance(result, dict)
        assert "categories" in result

    def test_status_operation(self, workspace: Path) -> None:
        from cortex.mcp.tools.health_scan_tool import cortex_health_scan

        result = cortex_health_scan(str(workspace), operation="status")
        assert isinstance(result, dict)
