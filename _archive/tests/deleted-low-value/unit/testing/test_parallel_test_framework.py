"""
CORTEX Parallel Test Framework — RED Phase Tests (CORE-008).

Tests for:
  - ParallelRunner: batch-aware xdist wrapper
  - BatchProgressReporter: real-time terminal feedback per batch
  - TestCategorizer: auto-assigns tier markers to uncategorized tests
  - TestFileNamingAdapter: FileFactory integration for test filenames

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
AC-ID: AC-TEST-PARALLEL-001
"""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from typing import List


# ============================================================================
# TestParallelRunner — batch-aware xdist configuration
# ============================================================================

class TestParallelRunner:
    """Tests for cortex.testing.framework.parallel_runner.ParallelRunner."""

    def test_import(self) -> None:
        """ParallelRunner is importable from canonical path."""
        from cortex.testing.framework.parallel_runner import ParallelRunner
        assert ParallelRunner is not None

    def test_default_profile_is_auto(self) -> None:
        """Default execution profile uses auto worker count."""
        from cortex.testing.framework.parallel_runner import ParallelRunner
        runner = ParallelRunner()
        assert runner.profile == "auto"

    def test_worker_count_auto_resolves_to_cpu_count(self) -> None:
        """Auto worker count resolves to number of CPUs."""
        from cortex.testing.framework.parallel_runner import ParallelRunner
        import os
        runner = ParallelRunner(profile="auto")
        workers = runner.worker_count()
        assert workers >= 1
        assert workers <= os.cpu_count() * 2  # never exceeds 2x cores

    def test_worker_count_explicit(self) -> None:
        """Explicit worker count is respected."""
        from cortex.testing.framework.parallel_runner import ParallelRunner
        runner = ParallelRunner(workers=4)
        assert runner.worker_count() == 4

    def test_batch_size_default(self) -> None:
        """Default batch size is 500 tests per batch."""
        from cortex.testing.framework.parallel_runner import ParallelRunner
        runner = ParallelRunner()
        assert runner.batch_size == 500

    def test_batch_size_configurable(self) -> None:
        """Batch size is configurable at construction."""
        from cortex.testing.framework.parallel_runner import ParallelRunner
        runner = ParallelRunner(batch_size=250)
        assert runner.batch_size == 250

    def test_build_pytest_args_smoke(self) -> None:
        """Smoke profile builds correct pytest args."""
        from cortex.testing.framework.parallel_runner import ParallelRunner
        runner = ParallelRunner(profile="smoke")
        args = runner.build_pytest_args(paths=["tests/unit"])
        assert "-n" in args
        assert "--dist" in args
        assert "tests/unit" in args

    def test_build_pytest_args_unit_uses_loadscope(self) -> None:
        """Unit profile uses loadscope distribution for class isolation."""
        from cortex.testing.framework.parallel_runner import ParallelRunner
        runner = ParallelRunner(profile="unit")
        args = runner.build_pytest_args(paths=["tests/unit"])
        dist_idx = args.index("--dist")
        assert args[dist_idx + 1] == "loadscope"

    def test_build_pytest_args_golden_is_serial(self) -> None:
        """Golden/e2e profile runs serially (no xdist)."""
        from cortex.testing.framework.parallel_runner import ParallelRunner
        runner = ParallelRunner(profile="golden")
        args = runner.build_pytest_args(paths=["tests/golden"])
        assert "-n" not in args

    def test_split_into_batches(self) -> None:
        """split_into_batches divides test list into correct batch sizes."""
        from cortex.testing.framework.parallel_runner import ParallelRunner
        runner = ParallelRunner(batch_size=100)
        items = [f"test_{i}" for i in range(350)]
        batches = runner.split_into_batches(items)
        assert len(batches) == 4  # 100+100+100+50
        assert len(batches[0]) == 100
        assert len(batches[-1]) == 50

    def test_split_into_batches_empty(self) -> None:
        """Empty test list returns empty batches list."""
        from cortex.testing.framework.parallel_runner import ParallelRunner
        runner = ParallelRunner()
        batches = runner.split_into_batches([])
        assert batches == []

    def test_execution_profiles_defined(self) -> None:
        """All four execution profiles are registered."""
        from cortex.testing.framework.parallel_runner import ParallelRunner, EXECUTION_PROFILES
        for profile in ("smoke", "unit", "integration", "golden"):
            assert profile in EXECUTION_PROFILES

    def test_profile_has_required_keys(self) -> None:
        """Each profile has workers, dist, markers, and batch_size keys."""
        from cortex.testing.framework.parallel_runner import EXECUTION_PROFILES
        required = {"workers", "dist", "markers", "batch_size"}
        for name, profile in EXECUTION_PROFILES.items():
            missing = required - set(profile.keys())
            assert not missing, f"Profile '{name}' missing keys: {missing}"


# ============================================================================
# TestBatchProgressReporter — real-time terminal output
# ============================================================================

class TestBatchProgressReporter:
    """Tests for cortex.testing.framework.progress_reporter.BatchProgressReporter."""

    def test_import(self) -> None:
        """BatchProgressReporter is importable."""
        from cortex.testing.framework.progress_reporter import BatchProgressReporter
        assert BatchProgressReporter is not None

    def test_init_with_total(self) -> None:
        """Reporter initialises with total test count and batch info."""
        from cortex.testing.framework.progress_reporter import BatchProgressReporter
        reporter = BatchProgressReporter(total=1000, batch_size=200)
        assert reporter.total == 1000
        assert reporter.batch_size == 200
        assert reporter.batch_count == 5

    def test_batch_count_ceiling(self) -> None:
        """Batch count rounds up (350 tests / 100 per batch = 4 batches)."""
        from cortex.testing.framework.progress_reporter import BatchProgressReporter
        reporter = BatchProgressReporter(total=350, batch_size=100)
        assert reporter.batch_count == 4

    def test_on_batch_start_emits_header(self, capfd) -> None:
        """on_batch_start writes batch header to stderr."""
        from cortex.testing.framework.progress_reporter import BatchProgressReporter
        reporter = BatchProgressReporter(total=500, batch_size=100)
        reporter.on_batch_start(batch_num=1, count=100)
        captured = capfd.readouterr()
        output = captured.err + captured.out
        assert "Batch 1" in output or "batch" in output.lower()
        assert "100" in output

    def test_on_batch_complete_emits_summary(self, capfd) -> None:
        """on_batch_complete writes pass/fail counts to stderr."""
        from cortex.testing.framework.progress_reporter import BatchProgressReporter
        reporter = BatchProgressReporter(total=500, batch_size=100)
        reporter.on_batch_start(batch_num=1, count=100)
        reporter.on_batch_complete(batch_num=1, passed=98, failed=2, duration=3.5)
        captured = capfd.readouterr()
        output = captured.err + captured.out
        assert "98" in output or "passed" in output.lower()

    def test_progress_bar_format(self) -> None:
        """render_progress_bar returns a string with % and block chars."""
        from cortex.testing.framework.progress_reporter import BatchProgressReporter
        reporter = BatchProgressReporter(total=100, batch_size=25)
        bar = reporter.render_progress_bar(done=50, total=100)
        assert "50" in bar or "%" in bar
        assert "█" in bar or "▓" in bar or "=" in bar or "#" in bar

    def test_final_summary_aggregates(self, capfd) -> None:
        """print_final_summary aggregates pass/fail across all batches."""
        from cortex.testing.framework.progress_reporter import BatchProgressReporter
        reporter = BatchProgressReporter(total=200, batch_size=100)
        reporter.on_batch_complete(1, passed=95, failed=5, duration=2.0)
        reporter.on_batch_complete(2, passed=99, failed=1, duration=1.8)
        reporter.print_final_summary()
        captured = capfd.readouterr()
        output = captured.err + captured.out
        assert "194" in output or "passed" in output.lower()

    def test_worker_status_line(self) -> None:
        """render_worker_status returns one line per worker."""
        from cortex.testing.framework.progress_reporter import BatchProgressReporter
        reporter = BatchProgressReporter(total=200, batch_size=100)
        status = reporter.render_worker_status(
            workers={"w0": "running", "w1": "idle", "w2": "running"}
        )
        assert "w0" in status
        assert "w2" in status


# ============================================================================
# TestTestCategorizer — auto-marker assignment
# ============================================================================

class TestTestCategorizer:
    """Tests for cortex.testing.framework.test_categorizer.TestCategorizer."""

    def test_import(self) -> None:
        """TestCategorizer is importable."""
        from cortex.testing.framework.test_categorizer import TestCategorizer
        assert TestCategorizer is not None

    def test_categorize_golden_by_path(self, tmp_path: Path) -> None:
        """Tests in tests/golden/ are categorized as 'golden'."""
        from cortex.testing.framework.test_categorizer import TestCategorizer
        cat = TestCategorizer()
        tier = cat.categorize_by_path(Path("tests/golden/test_something.py"))
        assert tier == "golden"

    def test_categorize_unit_by_path(self, tmp_path: Path) -> None:
        """Tests in tests/unit/ are categorized as 'unit'."""
        from cortex.testing.framework.test_categorizer import TestCategorizer
        cat = TestCategorizer()
        tier = cat.categorize_by_path(Path("tests/unit/core/test_file_factory.py"))
        assert tier == "unit"

    def test_categorize_integration_by_path(self) -> None:
        """Tests in tests/integration/ are categorized as 'integration'."""
        from cortex.testing.framework.test_categorizer import TestCategorizer
        cat = TestCategorizer()
        tier = cat.categorize_by_path(Path("tests/integration/test_db.py"))
        assert tier == "integration"

    def test_categorize_chaos_as_e2e(self) -> None:
        """Tests in tests/chaos/ are categorized as 'e2e'."""
        from cortex.testing.framework.test_categorizer import TestCategorizer
        cat = TestCategorizer()
        tier = cat.categorize_by_path(Path("tests/chaos/test_scenario.py"))
        assert tier == "e2e"

    def test_categorize_performance_as_slow(self) -> None:
        """Tests in tests/performance/ are categorized as 'slow'."""
        from cortex.testing.framework.test_categorizer import TestCategorizer
        cat = TestCategorizer()
        tier = cat.categorize_by_path(Path("tests/performance/test_bench.py"))
        assert tier == "slow"

    def test_default_unknown_path_is_unit(self) -> None:
        """Uncategorized path defaults to 'unit'."""
        from cortex.testing.framework.test_categorizer import TestCategorizer
        cat = TestCategorizer()
        tier = cat.categorize_by_path(Path("tests/misc/test_whatever.py"))
        assert tier == "unit"

    def test_batch_assignments_produce_correct_tiers(self) -> None:
        """assign_tiers processes a list of paths and returns tier map."""
        from cortex.testing.framework.test_categorizer import TestCategorizer
        cat = TestCategorizer()
        paths = [
            Path("tests/unit/core/test_x.py"),
            Path("tests/golden/test_y.py"),
            Path("tests/integration/test_z.py"),
        ]
        result = cat.assign_tiers(paths)
        assert result[paths[0]] == "unit"
        assert result[paths[1]] == "golden"
        assert result[paths[2]] == "integration"

    def test_group_by_tier(self) -> None:
        """group_by_tier returns dict keyed by tier with lists of paths."""
        from cortex.testing.framework.test_categorizer import TestCategorizer
        cat = TestCategorizer()
        paths = [
            Path("tests/unit/test_a.py"),
            Path("tests/unit/test_b.py"),
            Path("tests/golden/test_c.py"),
        ]
        grouped = cat.group_by_tier(paths)
        assert "unit" in grouped
        assert len(grouped["unit"]) == 2
        assert "golden" in grouped
        assert len(grouped["golden"]) == 1


# ============================================================================
# TestTestFileNamingAdapter — FileFactory integration
# ============================================================================

class TestTestFileNamingAdapter:
    """Tests for cortex.testing.framework.test_file_naming.TestFileNamingAdapter."""

    def test_import(self) -> None:
        """TestFileNamingAdapter is importable."""
        from cortex.testing.framework.test_file_naming import TestFileNamingAdapter
        assert TestFileNamingAdapter is not None

    def test_generate_test_filename_snake_case(self) -> None:
        """Generated test filenames are snake_case with test_ prefix."""
        from cortex.testing.framework.test_file_naming import TestFileNamingAdapter
        adapter = TestFileNamingAdapter()
        result = adapter.generate("ParallelRunner")
        assert result.filename == "test_parallel_runner.py"
        assert result.is_valid

    def test_generate_multi_word_subject(self) -> None:
        """Multi-word subjects convert to snake_case."""
        from cortex.testing.framework.test_file_naming import TestFileNamingAdapter
        adapter = TestFileNamingAdapter()
        result = adapter.generate("BatchProgressReporter")
        assert result.filename == "test_batch_progress_reporter.py"

    def test_generate_with_context(self) -> None:
        """Context prefix is prepended to test filename."""
        from cortex.testing.framework.test_file_naming import TestFileNamingAdapter
        adapter = TestFileNamingAdapter()
        result = adapter.generate("runner", context="parallel")
        assert result.filename == "test_parallel_runner.py"

    def test_validate_existing_filename_valid(self) -> None:
        """Existing snake_case test_ filenames pass validation."""
        from cortex.testing.framework.test_file_naming import TestFileNamingAdapter
        adapter = TestFileNamingAdapter()
        result = adapter.validate("test_file_factory.py")
        assert result.is_valid
        assert not result.violations

    def test_validate_bad_filename_camel_case(self) -> None:
        """CamelCase test filenames fail validation."""
        from cortex.testing.framework.test_file_naming import TestFileNamingAdapter
        adapter = TestFileNamingAdapter()
        result = adapter.validate("TestFileFactory.py")
        assert not result.is_valid

    def test_validate_missing_test_prefix(self) -> None:
        """Filenames without test_ prefix fail validation."""
        from cortex.testing.framework.test_file_naming import TestFileNamingAdapter
        adapter = TestFileNamingAdapter()
        result = adapter.validate("file_factory.py")
        assert not result.is_valid
        assert any("test_" in v for v in result.violations)

    def test_uses_file_factory_internally(self) -> None:
        """Adapter delegates to FileFactory for core naming rules."""
        from cortex.testing.framework.test_file_naming import TestFileNamingAdapter
        from cortex.core.file_factory import FileFactory
        adapter = TestFileNamingAdapter()
        assert isinstance(adapter.factory, FileFactory)


# ============================================================================
# TestCortexXdistPlugin — parallel-aware pytest plugin
# ============================================================================

class TestCortexXdistPlugin:
    """Tests for cortex.testing.plugins.cortex_xdist_plugin.CortexXdistPlugin."""

    def test_import(self) -> None:
        """CortexXdistPlugin is importable."""
        from cortex.testing.plugins.cortex_xdist_plugin import CortexXdistPlugin
        assert CortexXdistPlugin is not None

    def test_plugin_has_batch_reporter(self) -> None:
        """Plugin holds a BatchProgressReporter instance."""
        from cortex.testing.plugins.cortex_xdist_plugin import CortexXdistPlugin
        from cortex.testing.framework.progress_reporter import BatchProgressReporter
        plugin = CortexXdistPlugin(batch_size=500)
        assert isinstance(plugin.reporter, BatchProgressReporter)

    def test_plugin_tracks_batch_boundaries(self) -> None:
        """Plugin increments batch number every batch_size tests."""
        from cortex.testing.plugins.cortex_xdist_plugin import CortexXdistPlugin
        plugin = CortexXdistPlugin(batch_size=3)
        # Simulate 3 test completions
        for i in range(3):
            plugin._on_test_complete(nodeid=f"test_{i}", passed=True)
        assert plugin.current_batch == 2  # moved to batch 2 after completing batch 1

    def test_plugin_registers_with_config(self) -> None:
        """pytest_configure registers the plugin into pluginmanager."""
        from cortex.testing.plugins import cortex_xdist_plugin
        mock_config = MagicMock()
        mock_config.pluginmanager.is_registered.return_value = False
        cortex_xdist_plugin.pytest_configure(mock_config)
        mock_config.pluginmanager.register.assert_called_once()

    def test_plugin_env_var_controls_batch_size(self) -> None:
        """CORTEX_BATCH_SIZE env var overrides default batch size."""
        import os
        from cortex.testing.plugins.cortex_xdist_plugin import CortexXdistPlugin
        with patch.dict(os.environ, {"CORTEX_BATCH_SIZE": "250"}):
            plugin = CortexXdistPlugin()
            assert plugin.batch_size == 250


# ============================================================================
# TestTestSuiteStructure — canonical folder layout
# ============================================================================

class TestTestSuiteStructure:
    """Tests for canonical test folder structure mirroring cortex/ source."""

    def test_unit_dir_exists(self) -> None:
        """tests/unit/ exists."""
        assert Path("tests/unit").exists()

    def test_golden_dir_exists(self) -> None:
        """tests/golden/ exists."""
        assert Path("tests/golden").exists()

    def test_integration_dir_exists(self) -> None:
        """tests/integration/ exists."""
        assert Path("tests/integration").exists()

    def test_fixtures_dir_exists(self) -> None:
        """tests/fixtures/ exists for shared test data."""
        assert Path("tests/fixtures").exists()

    def test_no_phase_named_dirs_in_unit(self) -> None:
        """No phase_XX named directories in tests/unit/ (Phase 07 policy)."""
        unit = Path("tests/unit")
        if unit.exists():
            phase_dirs = [d for d in unit.iterdir()
                          if d.is_dir() and d.name.startswith("phase_")]
            # Allow phase_38 temporarily until Phase 09 cleanup
            unexpected = [d for d in phase_dirs if d.name not in ("phase_38", "phase3", "phase4")]
            assert not unexpected, f"Unexpected phase dirs: {unexpected}"

    def test_unit_mirrors_cortex_structure(self) -> None:
        """tests/unit/ has subdirs mirroring cortex/ canonical dirs."""
        expected = {"core", "governance", "infrastructure", "mcp", "orchestrators"}
        unit_subdirs = {d.name for d in Path("tests/unit").iterdir() if d.is_dir()}
        missing = expected - unit_subdirs
        assert not missing, f"tests/unit/ missing dirs: {missing}"
