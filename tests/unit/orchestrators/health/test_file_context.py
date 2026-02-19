"""Unit Tests — file_context.py

Phase: PHASE-51
CORE: CORE-008 (TDD — tests first)
"""

import os
from pathlib import Path

import pytest


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Create a minimal workspace for FileContext tests."""
    # Python file
    (tmp_path / "cortex").mkdir()
    (tmp_path / "cortex" / "__init__.py").write_text("")
    (tmp_path / "cortex" / "module.py").write_text("# hello\nprint('hi')\n")

    # Non-Python files
    (tmp_path / "README.md").write_text("# Readme\n")
    (tmp_path / "config.yaml").write_text("key: value\n")

    # Excluded directory — should be skipped
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main\n")

    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "module.cpython-312.pyc").write_bytes(b"\x00")

    # Empty file
    (tmp_path / "empty.txt").write_text("")

    return tmp_path


class TestFileContextBuild:
    """FileContext.build() — single rglob walk."""

    def test_build_returns_file_context(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        assert ctx.workspace_root == workspace

    def test_build_captures_files(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        # Should include real files, not excluded dirs
        names = {p.name for p in ctx.all_files}
        assert "module.py" in names
        assert "README.md" in names
        assert "config.yaml" in names

    def test_build_excludes_git(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        paths_str = {str(p) for p in ctx.all_files}
        assert not any(".git" in s for s in paths_str)

    def test_build_excludes_pycache(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        paths_str = {str(p) for p in ctx.all_files}
        assert not any("__pycache__" in s for s in paths_str)


class TestFileContextContent:
    """FileContext.get_content() — cached text reads."""

    def test_content_returns_text(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        module_path = workspace / "cortex" / "module.py"
        content = ctx.get_content(module_path)
        assert "print('hi')" in content

    def test_content_cached(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        module_path = workspace / "cortex" / "module.py"
        c1 = ctx.get_content(module_path)
        c2 = ctx.get_content(module_path)
        assert c1 is c2  # Same object — from cache

    def test_content_unknown_file_returns_none(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        result = ctx.get_content(workspace / "nonexistent.py")
        assert result is None


class TestFileContextHash:
    """FileContext.get_hash() — cached MD5 hashes."""

    def test_hash_returns_string(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        module_path = workspace / "cortex" / "module.py"
        h = ctx.get_hash(module_path)
        assert isinstance(h, str)
        assert len(h) == 32  # MD5 hex digest

    def test_hash_cached(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        module_path = workspace / "cortex" / "module.py"
        h1 = ctx.get_hash(module_path)
        h2 = ctx.get_hash(module_path)
        assert h1 is h2  # Same object — from cache

    def test_hash_unknown_file_returns_none(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        result = ctx.get_hash(workspace / "nonexistent.py")
        assert result is None


class TestFileContextProperties:
    """Convenience properties."""

    def test_python_files(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        py = list(ctx.python_files)
        names = {p.name for p in py}
        assert "module.py" in names
        assert "__init__.py" in names

    def test_directories(self, workspace: Path) -> None:
        from cortex.orchestrators.health.file_context import FileContext

        ctx = FileContext.build(workspace)
        dir_names = {d.name for d in ctx.directories}
        assert "cortex" in dir_names
        # Excluded dirs should not appear
        assert ".git" not in dir_names
        assert "__pycache__" not in dir_names
