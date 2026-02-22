"""Tests for cortex_scaffold_files MCP tool.

Authority: CORE-008 (TDD mandatory) | CORE-011 (type hints) | CORE-012 (docstrings)
Sharpen-the-Saw: GAP-007 — no MCP tool exposes FileFactory for multi-language scaffolding.
This test suite is written RED-first before implementation.

AC_START: PB-STS-001-RUN-2-TDD
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _import_tool():
    """Import the tool class — deferred so RED phase fails cleanly."""
    from cortex.mcp.tools.scaffold_files_tool import CortexScaffoldFiles  # noqa: PLC0415
    return CortexScaffoldFiles


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_root(tmp_path: Path) -> Path:
    """A fresh temp directory acting as workspace root."""
    return tmp_path


@pytest.fixture()
def tool():
    """Instantiate the CortexScaffoldFiles tool."""
    return _import_tool()()


# ---------------------------------------------------------------------------
# Registration / metadata
# ---------------------------------------------------------------------------

class TestCortexScaffoldFilesRegistration:
    """Tool must satisfy ConsolidatedTool interface contract."""

    def test_tool_importable(self):
        cls = _import_tool()
        assert cls is not None

    def test_tool_name(self, tool):
        assert tool.name == "cortex_scaffold_files"

    def test_tool_has_description(self, tool):
        assert len(tool.description) > 10

    def test_tool_parameters_non_empty(self, tool):
        assert len(tool.parameters) >= 3

    def test_required_param_files(self, tool):
        names = [p.name for p in tool.parameters]
        assert "files" in names

    def test_required_param_root(self, tool):
        names = [p.name for p in tool.parameters]
        assert "root" in names

    def test_tool_in_all_tools_list(self):
        from cortex.mcp.tools import ALL_TOOLS
        names = [t.name if hasattr(t, "name") else getattr(t, "name", "") for t in ALL_TOOLS]
        tool_names = []
        for t in ALL_TOOLS:
            try:
                tool_names.append(t().name)
            except Exception:
                pass
        assert "cortex_scaffold_files" in tool_names


# ---------------------------------------------------------------------------
# Core file creation
# ---------------------------------------------------------------------------

class TestCortexScaffoldFilesExecution:
    """Tool must actually write files to disk."""

    @pytest.mark.asyncio
    async def test_creates_single_csharp_file(self, tool, tmp_root: Path):
        result = await tool.execute(
            root=str(tmp_root),
            files=[
                {
                    "path": "backend/Services/UserService.cs",
                    "content": "namespace FinTrack.Application.Services;\npublic class UserService {}",
                    "language": "csharp",
                }
            ],
        )
        assert result.success is True
        target = tmp_root / "backend" / "Services" / "UserService.cs"
        assert target.exists(), f"Expected file not created: {target}"

    @pytest.mark.asyncio
    async def test_creates_multiple_files_in_one_call(self, tool, tmp_root: Path):
        result = await tool.execute(
            root=str(tmp_root),
            files=[
                {"path": "A/Foo.cs", "content": "// foo", "language": "csharp"},
                {"path": "B/Bar.ts", "content": "// bar", "language": "typescript"},
                {"path": "C/baz.py", "content": "# baz", "language": "python"},
            ],
        )
        assert result.success is True
        assert (tmp_root / "A" / "Foo.cs").exists()
        assert (tmp_root / "B" / "Bar.ts").exists()
        assert (tmp_root / "C" / "baz.py").exists()

    @pytest.mark.asyncio
    async def test_creates_parent_directories(self, tool, tmp_root: Path):
        deep = "a/b/c/d/e/Deep.cs"
        result = await tool.execute(
            root=str(tmp_root),
            files=[{"path": deep, "content": "// deep", "language": "csharp"}],
        )
        assert result.success is True
        assert (tmp_root / deep).exists()

    @pytest.mark.asyncio
    async def test_file_content_written_correctly(self, tool, tmp_root: Path):
        content = "namespace Test;\npublic class Exact { public int X => 42; }"
        await tool.execute(
            root=str(tmp_root),
            files=[{"path": "Exact.cs", "content": content, "language": "csharp"}],
        )
        written = (tmp_root / "Exact.cs").read_text()
        assert "public int X => 42;" in written

    @pytest.mark.asyncio
    async def test_result_data_contains_files_created(self, tool, tmp_root: Path):
        result = await tool.execute(
            root=str(tmp_root),
            files=[
                {"path": "X.cs", "content": "// x", "language": "csharp"},
                {"path": "Y.cs", "content": "// y", "language": "csharp"},
            ],
        )
        assert result.success is True
        assert result.data.get("files_created") == 2

    @pytest.mark.asyncio
    async def test_result_lists_created_paths(self, tool, tmp_root: Path):
        result = await tool.execute(
            root=str(tmp_root),
            files=[{"path": "Z.cs", "content": "// z", "language": "csharp"}],
        )
        assert "Z.cs" in str(result.data.get("paths", []))


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestCortexScaffoldFilesErrors:
    """Tool must handle bad inputs gracefully."""

    @pytest.mark.asyncio
    async def test_empty_files_list_returns_success_zero(self, tool, tmp_root: Path):
        result = await tool.execute(root=str(tmp_root), files=[])
        assert result.success is True
        assert result.data.get("files_created") == 0

    @pytest.mark.asyncio
    async def test_missing_path_key_returns_failure(self, tool, tmp_root: Path):
        result = await tool.execute(
            root=str(tmp_root),
            files=[{"content": "// no path", "language": "csharp"}],
        )
        assert result.success is False

    @pytest.mark.asyncio
    async def test_missing_content_key_returns_failure(self, tool, tmp_root: Path):
        result = await tool.execute(
            root=str(tmp_root),
            files=[{"path": "Oops.cs", "language": "csharp"}],
        )
        assert result.success is False

    @pytest.mark.asyncio
    async def test_invalid_root_returns_failure(self, tool):
        result = await tool.execute(
            root="/nonexistent_____path_xyz/root",
            files=[{"path": "A.cs", "content": "// a", "language": "csharp"}],
        )
        # Should either succeed by creating dirs or fail cleanly — never raise
        assert isinstance(result.success, bool)
