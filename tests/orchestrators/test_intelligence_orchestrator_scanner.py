"""
Phase 66-A RED tests — GAP-66-003: IntelligenceOrchestrator → HierarchicalScanner wiring.

TDD-66-A-003: IntelligenceOrchestrator.analyze() must use HierarchicalScanner for
file discovery instead of ad-hoc glob patterns.

Author: Asif Hussain
Phase: 66-A
Sweep: SWEEP-66-INTELLIGENCE-MATRIX
"""

import pytest
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

# AC_START: AC-66-A-003-INTELLIGENCE-ORCHESTRATOR-SCANNER-WIRING-20260224T000000Z


class TestIntelligenceOrchestratorUsesHierarchicalScanner:
    """GAP-66-003: analyze() must route through HierarchicalScannerAdapter."""

    def test_intelligence_orchestrator_accepts_scanner(self) -> None:
        """IntelligenceOrchestrator.__init__() must accept a HierarchicalScanner arg."""
        from cortex.orchestrators.intelligence.intelligence_orchestrator import (
            IntelligenceOrchestrator,
        )
        from cortex.toolkit.filesystem.hierarchical_scanner import HierarchicalScanner

        import inspect
        sig = inspect.signature(IntelligenceOrchestrator.__init__)
        params = list(sig.parameters.keys())
        assert "scanner" in params, (
            f"IntelligenceOrchestrator.__init__() must accept 'scanner' param (GAP-66-003). "
            f"Got params: {params}"
        )

    def test_analyze_uses_scanner_not_glob(self) -> None:
        """IntelligenceOrchestrator.analyze() must call scanner.scan() not glob.glob()."""
        from cortex.orchestrators.intelligence.intelligence_orchestrator import (
            IntelligenceOrchestrator,
        )
        from cortex.toolkit.filesystem.hierarchical_scanner import (
            HierarchicalScanner,
            ScannedFile,
        )
        from cortex.lens.adapters.hierarchical_scanner_adapter import (
            HierarchicalScannerAdapter,
        )

        mock_scanner = MagicMock(spec=HierarchicalScanner)
        mock_scanner.scan.return_value = []
        orchestrator = IntelligenceOrchestrator(scanner=mock_scanner)

        with patch("glob.glob") as mock_glob:
            orchestrator.analyze(target_path=Path("/tmp"))
            mock_glob.assert_not_called(), (
                "analyze() must NOT use glob.glob — use HierarchicalScanner instead (GAP-66-003)"
            )
        mock_scanner.scan.assert_called_once()

    def test_scanner_files_passed_to_lens_analyze(self) -> None:
        """Files from HierarchicalScanner must be passed into LENS.analyze()."""
        from cortex.orchestrators.intelligence.intelligence_orchestrator import (
            IntelligenceOrchestrator,
        )
        from cortex.toolkit.filesystem.hierarchical_scanner import (
            HierarchicalScanner,
            ScannedFile,
        )

        fake_path = Path("/tmp/fake_file.py")
        mock_file = MagicMock(spec=ScannedFile)
        mock_file.path = fake_path

        mock_scanner = MagicMock(spec=HierarchicalScanner)
        mock_scanner.scan.return_value = [mock_file]

        orchestrator = IntelligenceOrchestrator(scanner=mock_scanner)

        with patch.object(
            orchestrator, "_lens_analyze", return_value=[]
        ) as mock_lens:
            orchestrator.analyze(target_path=Path("/tmp"))
            if mock_lens.called:
                args, kwargs = mock_lens.call_args
                files_arg = kwargs.get("files", args[0] if args else [])
                assert fake_path in files_arg, (
                    "LENS analyze must receive paths from HierarchicalScanner (GAP-66-003)"
                )

    def test_intelligence_orchestrator_has_scanner_attribute(self) -> None:
        """Instantiated orchestrator must expose ._scanner attribute."""
        from cortex.orchestrators.intelligence.intelligence_orchestrator import (
            IntelligenceOrchestrator,
        )
        from cortex.toolkit.filesystem.hierarchical_scanner import HierarchicalScanner

        mock_scanner = MagicMock(spec=HierarchicalScanner)
        orchestrator = IntelligenceOrchestrator(scanner=mock_scanner)

        assert hasattr(orchestrator, "_scanner"), (
            "IntelligenceOrchestrator must store scanner as self._scanner (GAP-66-003)"
        )
        assert orchestrator._scanner is mock_scanner


# AC_COMPLETE: AC-66-A-003-INTELLIGENCE-ORCHESTRATOR-SCANNER-WIRING-20260224T000000Z ✅
