"""
Golden Tests: FileContext shared-walk refactor — FC-001 to FC-015

Proves:
  FC-001  FileContext is built by a single rglob call inside scan()
  FC-002  All _check_* methods receive the shared context (no re-walk)
  FC-003  content_cache stores text per file; each file read at most once
  FC-004  hash_cache stores MD5 per file; each file hashed at most once
  FC-005  InventoryAgent.check() accepts FileContext and uses content_cache
          instead of spawning subprocess git grep
  FC-006  _has_no_imports(ctx=FileContext) returns False when prefix found
  FC-007  _has_no_imports(ctx=FileContext) returns True when prefix absent
  FC-008  PHASE-92 HealthOrchestrator.run_health_check() delegates to
          Phase-48 scan() via FileContext (single walk, 15 agents)
  FC-009  FileContext.files contains only non-excluded paths
  FC-010  FileContext.dirs contains only non-excluded directories
  FC-011  scan() with shared context produces identical ScanResult
          counts as before the refactor (regression guard)
  FC-012  content_cache is lazily populated on first access
  FC-013  hash_cache is lazily populated on first access
  FC-014  No subprocess.run calls during InventoryAgent.check(ctx=ctx)
  FC-015  PHASE-92 run_health_check() result has 0 rglob calls beyond
          the single walk performed by Phase-48 scan()

Authority: Phase 48 + PHASE-92, CORE-008, CORE-011, CORE-012
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, call
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_repo(tmp_path: Path) -> Path:
    """Create a minimal CORTEX-like repo layout."""
    (tmp_path / "cortex").mkdir()
    (tmp_path / "cortex" / "__init__.py").write_text("")
    (tmp_path / "cortex" / "orchestrators").mkdir()
    (tmp_path / "cortex" / "orchestrators" / "__init__.py").write_text("")
    (tmp_path / "docs").mkdir()
    (tmp_path / "_workspaces").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "tests").mkdir()
    return tmp_path


# ===========================================================================
# FC-001  Single rglob inside scan()
# ===========================================================================

class TestSingleRglobWalk:
    """FC-001: scan() walks the workspace filesystem exactly once."""

    def test_rglob_called_once(self, tmp_path):
        """scan() must call rglob on workspace_root exactly 1 time."""
        repo = _make_repo(tmp_path)
        (repo / "cortex" / "sample.py").write_text("x = 1")

        from cortex.orchestrators.support.health_orchestrator import HealthOrchestrator

        workspace_rglob_calls = []
        orig_rglob = Path.rglob

        def counting_rglob(self, pattern, **kwargs):
            # Only count the workspace-root-level wildcard walk
            if pattern == "*" and self == repo:
                workspace_rglob_calls.append(pattern)
            return orig_rglob(self, pattern, **kwargs)

        orch = HealthOrchestrator(workspace_root=repo)
        with patch.object(Path, "rglob", counting_rglob):
            result = orch.scan()

        # Only ONE workspace rglob("*") — all _check_* methods share the context
        assert len(workspace_rglob_calls) == 1, (
            f"Expected 1 workspace rglob('*') call, got {len(workspace_rglob_calls)}. "
            "Check methods must NOT walk files independently."
        )
        assert result.total_files_scanned > 0


# ===========================================================================
# FC-002  All check methods share context — no independent walks
# ===========================================================================

class TestCheckMethodsShareContext:
    """FC-002: Each _check_* method uses injected FileContext, not its own walk."""

    def test_screaming_case_uses_context(self, tmp_path):
        """_check_screaming_case uses FileContext.files, not rglob."""
        repo = _make_repo(tmp_path)
        (repo / "SCREAMING-FILE.txt").write_text("x")

        from cortex.orchestrators.support.health_orchestrator import (
            HealthOrchestrator,
            FileContext,
        )
        orch = HealthOrchestrator(workspace_root=repo)
        # Build context externally and inject — check method must not re-walk
        ctx = FileContext.build(repo)
        result_cat = orch._check_screaming_case(ctx)
        assert result_cat.count >= 1

    def test_empty_files_uses_context(self, tmp_path):
        """_check_empty_files uses FileContext.files."""
        repo = _make_repo(tmp_path)
        (repo / "empty.py").write_text("")

        from cortex.orchestrators.support.health_orchestrator import (
            HealthOrchestrator,
            FileContext,
        )
        orch = HealthOrchestrator(workspace_root=repo)
        ctx = FileContext.build(repo)
        result_cat = orch._check_empty_files(ctx)
        assert result_cat.count >= 1

    def test_wrong_refs_uses_context_cache(self, tmp_path):
        """_check_wrong_references reads from FileContext.content_cache."""
        repo = _make_repo(tmp_path)
        bad = repo / "cortex" / "bad_ref.py"
        bad.write_text("from cortex_brain import something")

        from cortex.orchestrators.support.health_orchestrator import (
            HealthOrchestrator,
            FileContext,
        )
        orch = HealthOrchestrator(workspace_root=repo)
        ctx = FileContext.build(repo)

        # Warm entire cache for all files in ctx
        for f in ctx.files:
            ctx.get_content(f)

        read_calls = []
        orig_read = Path.read_text

        def spy_read(self, *args, **kwargs):
            read_calls.append(str(self))
            return orig_read(self, *args, **kwargs)

        with patch.object(Path, "read_text", spy_read):
            result_cat = orch._check_wrong_references(ctx)

        # No disk reads — all served from pre-warmed cache
        assert len(read_calls) == 0, (
            "_check_wrong_references should read from context cache, not disk"
        )
        assert result_cat.count >= 1


# ===========================================================================
# FC-003  content_cache — read at most once per file
# ===========================================================================

class TestContentCache:
    """FC-003: FileContext.content_cache ensures each file is read once."""

    def test_get_content_cached(self, tmp_path):
        repo = _make_repo(tmp_path)
        f = repo / "cortex" / "module.py"
        f.write_text("# hello")

        from cortex.orchestrators.support.health_orchestrator import FileContext

        ctx = FileContext.build(repo)

        # First call — populates cache
        c1 = ctx.get_content(f)
        assert c1 == "# hello"

        # Subsequent calls must be served from cache
        read_calls = []
        orig = Path.read_text
        def spy(self, *a, **kw):
            read_calls.append(str(self))
            return orig(self, *a, **kw)

        with patch.object(Path, "read_text", spy):
            c2 = ctx.get_content(f)

        assert c1 == c2
        # Zero disk reads on second access — cache hit
        assert len(read_calls) == 0

    def test_get_content_populates_on_miss(self, tmp_path):
        repo = _make_repo(tmp_path)
        f = repo / "fresh.py"
        f.write_text("fresh content")

        from cortex.orchestrators.support.health_orchestrator import FileContext

        ctx = FileContext(files=[], dirs=[], workspace_root=repo)
        # Cache is empty — first call reads disk
        content = ctx.get_content(f)
        assert content == "fresh content"
        # Second call is cached
        content2 = ctx.get_content(f)
        assert content2 == "fresh content"


# ===========================================================================
# FC-004  hash_cache — MD5 computed at most once per file
# ===========================================================================

class TestHashCache:
    """FC-004: FileContext.hash_cache ensures each file is hashed once."""

    def test_get_hash_cached(self, tmp_path):
        repo = _make_repo(tmp_path)
        f = repo / "dup.py"
        f.write_bytes(b"binary content")

        from cortex.orchestrators.support.health_orchestrator import FileContext

        ctx = FileContext.build(repo)
        calls = []
        orig = hashlib.md5

        def spy_md5(data):
            calls.append(len(data))
            return orig(data)

        with patch("hashlib.md5", spy_md5):
            h1 = ctx.get_hash(f)
            h2 = ctx.get_hash(f)

        assert h1 == h2
        # md5 called at most once — second access served from cache
        assert len(calls) <= 1


# ===========================================================================
# FC-005  InventoryAgent.check() accepts FileContext
# ===========================================================================

class TestInventoryAgentFileContext:
    """FC-005: InventoryAgent.check() accepts optional ctx=FileContext."""

    def test_check_accepts_file_context(self, tmp_path):
        """InventoryAgent.check(workspace_root, ctx=ctx) must not raise."""
        repo = _make_repo(tmp_path)

        from cortex.orchestrators.support.health_orchestrator import FileContext
        from cortex.orchestrators.health.agents.inventory_agent import InventoryAgent

        ctx = FileContext.build(repo)
        agent = InventoryAgent()
        result = agent.check(repo, ctx=ctx)
        assert result is not None
        assert result.agent_name == "InventoryAgent"

    def test_check_without_ctx_still_works(self, tmp_path):
        """Backward compat: check(workspace_root) with no ctx still works."""
        repo = _make_repo(tmp_path)

        from cortex.orchestrators.health.agents.inventory_agent import InventoryAgent

        agent = InventoryAgent()
        result = agent.check(repo)
        assert result is not None


# ===========================================================================
# FC-006 / FC-007  _has_no_imports uses content_cache
# ===========================================================================

class TestHasNoImportsUsesCache:
    """FC-006/007: _has_no_imports(prefixes, ctx) uses context cache."""

    def test_finds_import_in_cache(self, tmp_path):
        repo = _make_repo(tmp_path)
        f = repo / "cortex" / "user.py"
        f.write_text("from cortex.phase_38 import something")

        from cortex.orchestrators.support.health_orchestrator import FileContext
        from cortex.orchestrators.health.agents.inventory_agent import InventoryAgent

        ctx = FileContext.build(repo)
        # Warm cache
        ctx.get_content(f)

        agent = InventoryAgent()
        has_none = agent._has_no_imports(
            workspace_root=repo,
            prefixes=["from cortex.phase_38"],
            ctx=ctx,
        )
        assert has_none is False

    def test_no_import_in_cache(self, tmp_path):
        repo = _make_repo(tmp_path)
        f = repo / "cortex" / "clean.py"
        f.write_text("x = 1")

        from cortex.orchestrators.support.health_orchestrator import FileContext
        from cortex.orchestrators.health.agents.inventory_agent import InventoryAgent

        ctx = FileContext.build(repo)
        ctx.get_content(f)

        agent = InventoryAgent()
        has_none = agent._has_no_imports(
            workspace_root=repo,
            prefixes=["from cortex.phase_38"],
            ctx=ctx,
        )
        assert has_none is True


# ===========================================================================
# FC-008  PHASE-92 delegates to Phase-48 scan()
# ===========================================================================

class TestPhase92DelegatesToPhase48:
    """FC-008: PHASE-92 HealthOrchestrator.run_health_check() calls Phase-48 scan()."""

    def test_run_health_check_calls_phase48_scan(self, tmp_path):
        """run_health_check() must invoke Phase-48 HealthOrchestrator.scan()."""
        repo = _make_repo(tmp_path)

        from cortex.orchestrators.health.health_orchestrator import (
            HealthOrchestrator as Phase92Orch,
        )
        from cortex.orchestrators.support.health_orchestrator import (
            HealthOrchestrator as Phase48Orch,
            ScanResult,
        )

        phase92 = Phase92Orch(workspace_root=repo)
        scan_called = []

        dummy_result = ScanResult(generated_at="2026-01-01T00:00:00Z")

        def fake_scan(self_inner):
            scan_called.append(True)
            return dummy_result

        with patch.object(Phase48Orch, "scan", fake_scan):
            report = phase92.run_health_check()

        assert len(scan_called) == 1, (
            "PHASE-92 run_health_check() must delegate to Phase-48 scan()"
        )

    def test_run_health_check_returns_health_report(self, tmp_path):
        """run_health_check() still returns a HealthReport (not ScanResult)."""
        repo = _make_repo(tmp_path)

        from cortex.orchestrators.health.health_orchestrator import (
            HealthOrchestrator as Phase92Orch,
        )
        from cortex.orchestrators.health.reports.health_report import HealthReport

        phase92 = Phase92Orch(workspace_root=repo)
        report = phase92.run_health_check()
        assert isinstance(report, HealthReport)


# ===========================================================================
# FC-009 / FC-010  FileContext excludes excluded paths
# ===========================================================================

class TestFileContextExclusion:
    """FC-009/010: FileContext.build() applies _is_excluded rules."""

    def test_venv_excluded_from_files(self, tmp_path):
        repo = _make_repo(tmp_path)
        venv = repo / ".venv" / "lib" / "site-packages"
        venv.mkdir(parents=True)
        (venv / "some_package.py").write_text("x=1")

        from cortex.orchestrators.support.health_orchestrator import FileContext

        ctx = FileContext.build(repo)
        venv_paths = [str(f) for f in ctx.files if ".venv" in str(f)]
        assert len(venv_paths) == 0, ".venv must be excluded from FileContext.files"

    def test_pycache_excluded_from_dirs(self, tmp_path):
        repo = _make_repo(tmp_path)
        cache = repo / "cortex" / "__pycache__"
        cache.mkdir()

        from cortex.orchestrators.support.health_orchestrator import FileContext

        ctx = FileContext.build(repo)
        cache_dirs = [str(d) for d in ctx.dirs if "__pycache__" in str(d)]
        assert len(cache_dirs) == 0, "__pycache__ must be excluded from FileContext.dirs"


# ===========================================================================
# FC-011  Regression: ScanResult counts unchanged after refactor
# ===========================================================================

class TestRegressionScanResultCounts:
    """FC-011: Refactored scan() produces same counts as before."""

    def test_screaming_case_count_unchanged(self, tmp_path):
        repo = _make_repo(tmp_path)
        (repo / "LOUD-FILE.txt").write_text("hello")
        (repo / "quiet-file.txt").write_text("hello")

        from cortex.orchestrators.support.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace_root=repo)
        result = orch.scan()
        assert result.screaming_case.count == 1

    def test_empty_file_count_unchanged(self, tmp_path):
        repo = _make_repo(tmp_path)
        # Give __init__.py files content so they're not flagged as empty
        (repo / "cortex" / "__init__.py").write_text("# cortex package")
        (repo / "cortex" / "orchestrators" / "__init__.py").write_text("# orch pkg")
        (repo / "cortex" / "empty.py").write_text("")
        (repo / "cortex" / "nonempty.py").write_text("x = 1")

        from cortex.orchestrators.support.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace_root=repo)
        result = orch.scan()
        assert result.empty_files.count == 1

    def test_issues_found_nonzero(self, tmp_path):
        repo = _make_repo(tmp_path)
        (repo / "UPPER.txt").write_text("x")
        (repo / "cortex" / "blank.py").write_text("")

        from cortex.orchestrators.support.health_orchestrator import HealthOrchestrator

        orch = HealthOrchestrator(workspace_root=repo)
        result = orch.scan()
        assert result.issues_found > 0


# ===========================================================================
# FC-012 / FC-013  Lazy cache population
# ===========================================================================

class TestLazyCache:
    """FC-012/013: content_cache and hash_cache populated lazily."""

    def test_content_cache_empty_before_access(self, tmp_path):
        repo = _make_repo(tmp_path)
        (repo / "cortex" / "lazy.py").write_text("y=2")

        from cortex.orchestrators.support.health_orchestrator import FileContext

        ctx = FileContext.build(repo)
        # Cache should be empty immediately after build (lazy)
        assert len(ctx._content_cache) == 0

    def test_hash_cache_empty_before_access(self, tmp_path):
        repo = _make_repo(tmp_path)
        (repo / "cortex" / "lazy.py").write_text("y=2")

        from cortex.orchestrators.support.health_orchestrator import FileContext

        ctx = FileContext.build(repo)
        assert len(ctx._hash_cache) == 0


# ===========================================================================
# FC-014  No subprocess.run during InventoryAgent with FileContext
# ===========================================================================

class TestNoSubprocessWithFileContext:
    """FC-014: InventoryAgent.check(ctx=ctx) spawns zero subprocess.run calls."""

    def test_zero_subprocess_calls(self, tmp_path):
        repo = _make_repo(tmp_path)

        from cortex.orchestrators.support.health_orchestrator import FileContext
        from cortex.orchestrators.health.agents.inventory_agent import InventoryAgent
        import subprocess as sp

        ctx = FileContext.build(repo)
        agent = InventoryAgent()

        with patch.object(sp, "run") as mock_run:
            agent.check(repo, ctx=ctx)
            assert mock_run.call_count == 0, (
                f"Expected 0 subprocess.run calls with FileContext, "
                f"got {mock_run.call_count}"
            )


# ===========================================================================
# FC-015  PHASE-92 rglob calls == 1 via Phase-48 delegation
# ===========================================================================

class TestPhase92SingleWalk:
    """FC-015: PHASE-92 run_health_check() results in exactly 1 workspace rglob call."""

    def test_single_rglob_through_delegation(self, tmp_path):
        repo = _make_repo(tmp_path)
        (repo / "cortex" / "module.py").write_text("x=1")

        from cortex.orchestrators.health.health_orchestrator import (
            HealthOrchestrator as Phase92Orch,
        )

        workspace_rglob_calls = []
        orig_rglob = Path.rglob

        def counting_rglob(self, pattern, **kwargs):
            # Count only workspace-root-level wildcard walks
            if pattern == "*" and self == repo:
                workspace_rglob_calls.append(pattern)
            return orig_rglob(self, pattern, **kwargs)

        phase92 = Phase92Orch(workspace_root=repo)
        with patch.object(Path, "rglob", counting_rglob):
            phase92.run_health_check()

        assert len(workspace_rglob_calls) == 1, (
            f"Expected 1 workspace rglob('*') through Phase-92 → Phase-48 delegation, "
            f"got {len(workspace_rglob_calls)}"
        )
