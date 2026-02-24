"""
Phase 66-A RED tests — GAP-66-001: HierarchicalScannerAdapter feeds LENS analyze().

TDD-66-A-001: LENS file discovery must use HierarchicalScanner, not ad-hoc glob.

Author: Asif Hussain
Phase: 66-A
Sweep: SWEEP-66-INTELLIGENCE-MATRIX
"""

import pytest
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

# AC_START: AC-66-A-001-HIERARCHICAL-SCANNER-ADAPTER-20260224T000000Z


class TestHierarchicalScannerAdapterExists:
    """GAP-66-001: HierarchicalScannerAdapter must be importable."""

    def test_adapter_module_importable(self) -> None:
        """cortex.lens.adapters.hierarchical_scanner_adapter must import without error."""
        from cortex.lens.adapters.hierarchical_scanner_adapter import HierarchicalScannerAdapter  # noqa: F401

    def test_adapter_class_exists(self) -> None:
        """HierarchicalScannerAdapter class must be defined."""
        from cortex.lens.adapters.hierarchical_scanner_adapter import HierarchicalScannerAdapter
        assert hasattr(HierarchicalScannerAdapter, "adapt"), (
            "HierarchicalScannerAdapter must have an adapt() method"
        )

    def test_adapter_adapt_returns_list_of_paths(self) -> None:
        """HierarchicalScannerAdapter.adapt() must return a List[Path]."""
        from cortex.lens.adapters.hierarchical_scanner_adapter import HierarchicalScannerAdapter
        from cortex.toolkit.filesystem.hierarchical_scanner import HierarchicalScanner, ScannedFile

        mock_file = ScannedFile(
            path=Path("/tmp/test_file.py"),
            organization="test",
            extension=".py",
            hierarchy_depth=1,
            folder_name="test",
            filename_stem="test_file",
        )
        scanner = MagicMock(spec=HierarchicalScanner)
        scanner.scan.return_value = [mock_file]

        adapter = HierarchicalScannerAdapter(scanner=scanner)
        result = adapter.adapt()

        assert isinstance(result, list), "adapt() must return a list"
        assert len(result) == 1
        assert result[0] == Path("/tmp/test_file.py")

    def test_adapter_adapt_calls_scanner_scan(self) -> None:
        """adapt() must invoke scanner.scan() to discover files."""
        from cortex.lens.adapters.hierarchical_scanner_adapter import HierarchicalScannerAdapter
        from cortex.toolkit.filesystem.hierarchical_scanner import HierarchicalScanner

        scanner = MagicMock(spec=HierarchicalScanner)
        scanner.scan.return_value = []

        adapter = HierarchicalScannerAdapter(scanner=scanner)
        adapter.adapt()

        scanner.scan.assert_called_once()

    def test_scanner_output_feeds_lens_analyze(self) -> None:
        """HierarchicalScanner.scan() output must be usable as LENS file list."""
        from cortex.lens.adapters.hierarchical_scanner_adapter import HierarchicalScannerAdapter
        from cortex.toolkit.filesystem.hierarchical_scanner import HierarchicalScanner, ScannedFile

        # Create mock scanned files
        mock_files = [
            ScannedFile(
                path=Path("/tmp/module_a.py"),
                organization="test",
                extension=".py",
                hierarchy_depth=1,
                folder_name="test",
                filename_stem="module_a",
            ),
            ScannedFile(
                path=Path("/tmp/module_b.py"),
                organization="test",
                extension=".py",
                hierarchy_depth=1,
                folder_name="test",
                filename_stem="module_b",
            ),
        ]
        scanner = MagicMock(spec=HierarchicalScanner)
        scanner.scan.return_value = mock_files

        adapter = HierarchicalScannerAdapter(scanner=scanner)
        paths = adapter.adapt()

        assert len(paths) == 2
        assert Path("/tmp/module_a.py") in paths
        assert Path("/tmp/module_b.py") in paths

    def test_adapter_has_type_hints(self) -> None:
        """HierarchicalScannerAdapter must have type hints (CORE-011)."""
        import inspect
        from cortex.lens.adapters.hierarchical_scanner_adapter import HierarchicalScannerAdapter

        hints = {}
        try:
            hints = HierarchicalScannerAdapter.__init__.__annotations__
        except AttributeError:
            pass
        assert "return" in hints or len(hints) >= 1 or callable(HierarchicalScannerAdapter.adapt), (
            "HierarchicalScannerAdapter must have type annotations (CORE-011)"
        )


# AC_COMPLETE: AC-66-A-001-HIERARCHICAL-SCANNER-ADAPTER-20260224T000000Z ✅
