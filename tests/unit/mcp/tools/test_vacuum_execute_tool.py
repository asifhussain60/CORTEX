"""Unit Tests — MCP vacuum_execute_tool.py

Phase: PHASE-51
CORE: CORE-008 (TDD)
"""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Workspace for vacuum MCP tool tests."""
    (tmp_path / "cortex").mkdir()
    (tmp_path / "cortex" / "__init__.py").write_text("")
    (tmp_path / "README.md").write_text("# Hi\n")
    (tmp_path / "SCREAMING.txt").write_text("bad\n")
    (tmp_path / "empty.txt").write_text("")
    (tmp_path / "scratch.txt").write_text("scratch\n")
    return tmp_path


class TestVacuumExecuteTool:
    """MCP vacuum_execute_tool — parameter validation and routing."""

    def test_run_standalone(self, workspace: Path) -> None:
        from cortex.mcp.tools.vacuum_execute_tool import cortex_vacuum_execute

        result = cortex_vacuum_execute(str(workspace), operation="run")
        assert isinstance(result, dict)
        assert "total_operations" in result

    def test_preview(self, workspace: Path) -> None:
        from cortex.mcp.tools.vacuum_execute_tool import cortex_vacuum_execute

        result = cortex_vacuum_execute(str(workspace), operation="preview")
        assert isinstance(result, dict)
        assert result.get("dry_run") is True
        # Files should still exist
        assert (workspace / "SCREAMING.txt").exists()

    def test_nonexistent_workspace(self, tmp_path: Path) -> None:
        from cortex.mcp.tools.vacuum_execute_tool import cortex_vacuum_execute

        result = cortex_vacuum_execute(str(tmp_path / "nope"), operation="run")
        assert "error" in result

    def test_naming_fix_standalone(self, workspace: Path) -> None:
        from cortex.mcp.tools.vacuum_execute_tool import cortex_vacuum_execute

        result = cortex_vacuum_execute(str(workspace), operation="naming_fix")
        assert isinstance(result, dict)
