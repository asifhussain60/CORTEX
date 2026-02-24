"""
HierarchicalScannerAdapter — bridges HierarchicalScanner to LENS file discovery.

Authority: GAP-66-001 | Phase 66-A | SWEEP-66-INTELLIGENCE-MATRIX
CORE-011: type hints on all functions
CORE-012: docstrings on all public APIs
CORE-035: single canonical implementation — replaces ad-hoc glob patterns
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from cortex.toolkit.filesystem.hierarchical_scanner import HierarchicalScanner


class HierarchicalScannerAdapter:
    """Adapts HierarchicalScanner output for the LENS file discovery pipeline.

    Replaces ad-hoc ``glob.glob`` patterns in the LENS/Intelligence stack with
    the canonical ``HierarchicalScanner`` as the single source of file
    discovery (GAP-66-001).

    Usage::

        from cortex.toolkit.filesystem.hierarchical_scanner import HierarchicalScanner
        from cortex.lens.adapters.hierarchical_scanner_adapter import HierarchicalScannerAdapter

        scanner = HierarchicalScanner(root=Path("cortex/"))
        adapter = HierarchicalScannerAdapter(scanner)
        paths: list[Path] = adapter.adapt()
        # Pass to LENS: facade.analyze(files=paths)
    """

    def __init__(self, scanner: HierarchicalScanner) -> None:
        """Initialise with a configured :class:`HierarchicalScanner` instance.

        Args:
            scanner: Pre-configured HierarchicalScanner ready to scan.
        """
        self._scanner = scanner

    def adapt(self) -> List[Path]:
        """Run the scanner and extract :class:`~pathlib.Path` objects from results.

        Calls :meth:`HierarchicalScanner.scan` and maps each
        :class:`~cortex.toolkit.filesystem.hierarchical_scanner.ScannedFile`
        ``path`` attribute to a plain ``Path``, suitable for LENS
        ``analyze(files=...)`` calls.

        Returns:
            Ordered list of :class:`~pathlib.Path` objects discovered by the
            scanner.
        """
        scanned_files = self._scanner.scan()
        return [sf.path for sf in scanned_files]
