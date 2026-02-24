"""
Phase 66-C tests — GAP-66-018, GAP-66-019 + Coverage Gate.

TDD-66-C-001: LENS domain context → DomainAdapter hints.
TDD-66-C-002: Coverage gate ≥50% enforcement.

Author: Asif Hussain
Phase: 66-C
Sweep: SWEEP-66-INTELLIGENCE-MATRIX
"""

import pytest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

# AC_START: AC-66-C-COVERAGE-GATE-TESTS-20260224T000000Z


class TestMatrixCoverageGate:
    """GAP-66-C: IntelligenceMatrixBuilder must enforce ≥50% coverage gate."""

    def test_coverage_gate_constant_exists(self) -> None:
        """COVERAGE_GATE must be defined as 0.50."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import COVERAGE_GATE

        assert COVERAGE_GATE == 0.50, (
            f"COVERAGE_GATE must be 0.50, got {COVERAGE_GATE}"
        )

    def test_matrix_coverage_error_exists(self) -> None:
        """MatrixCoverageError must be importable."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import MatrixCoverageError

        assert issubclass(MatrixCoverageError, Exception)

    def test_builder_has_check_coverage_gate(self) -> None:
        """IntelligenceMatrixBuilder must have check_coverage_gate() method."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import IntelligenceMatrixBuilder

        assert hasattr(IntelligenceMatrixBuilder, "check_coverage_gate"), (
            "IntelligenceMatrixBuilder must have check_coverage_gate() (Phase 66-C)"
        )

    def test_check_coverage_gate_raises_when_below_threshold(self) -> None:
        """check_coverage_gate() must raise MatrixCoverageError when coverage < 0.50."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            IntelligenceMatrixBuilder,
            IntelligenceMatrix,
            MatrixCoverageError,
            COVERAGE_GATE,
        )

        builder = IntelligenceMatrixBuilder()
        low_coverage_matrix = IntelligenceMatrix(
            total_capabilities_x=10,
            total_capabilities_y=10,
            wired_count=3,
            coverage_score=0.10,
        )
        with pytest.raises(MatrixCoverageError):
            builder.check_coverage_gate(low_coverage_matrix)

    def test_check_coverage_gate_passes_when_above_threshold(self) -> None:
        """check_coverage_gate() must NOT raise when coverage ≥ 0.50."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            IntelligenceMatrixBuilder,
            IntelligenceMatrix,
        )

        builder = IntelligenceMatrixBuilder()
        good_matrix = IntelligenceMatrix(
            total_capabilities_x=10,
            total_capabilities_y=10,
            wired_count=6,
            coverage_score=0.60,
        )
        # Must not raise
        builder.check_coverage_gate(good_matrix)

    def test_x_axis_extended_to_ic015(self) -> None:
        """INTELLIGENCE_CAPABILITIES must include IC-011 through IC-015."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            INTELLIGENCE_CAPABILITIES,
        )

        ids = {cap.id for cap in INTELLIGENCE_CAPABILITIES}
        for expected_id in ("IC-011", "IC-012", "IC-013", "IC-014", "IC-015"):
            assert expected_id in ids, (
                f"x-axis must include {expected_id} (Phase 66-C). Missing from INTELLIGENCE_CAPABILITIES."
            )

    def test_y_axis_extended_to_cc015(self) -> None:
        """CORTEX_CAPABILITIES must include CC-011 through CC-015."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            CORTEX_CAPABILITIES,
        )

        ids = {cap.id for cap in CORTEX_CAPABILITIES}
        for expected_id in ("CC-011", "CC-012", "CC-013", "CC-014", "CC-015"):
            assert expected_id in ids, (
                f"y-axis must include {expected_id} (Phase 66-C). Missing from CORTEX_CAPABILITIES."
            )


class TestLensDomainAdapterBridge:
    """GAP-66-018: LENS domain context → DomainAdapter resolution hints."""

    def test_lens_domain_bridge_importable(self) -> None:
        """LENS domain context bridge function must be importable."""
        from cortex.intelligence.intelligence_wiring_bridges import lens_enrich_domain_adapter  # noqa: F401

    def test_lens_enrich_domain_adapter_adds_context(self) -> None:
        """lens_enrich_domain_adapter() must inject lens context into adapter context."""
        from cortex.intelligence.intelligence_wiring_bridges import lens_enrich_domain_adapter

        lens_context: Dict[str, Any] = {
            "domain": "cortex",
            "language": "python",
            "file_type": "orchestrator",
        }
        adapter_context: Dict[str, Any] = {"existing": "data"}
        result = lens_enrich_domain_adapter(lens_context, adapter_context)

        assert result["lens_enriched"] is True
        assert result["lens_context"] == lens_context
        assert result["existing"] == "data"


class TestT3HierarchicalScannerBridge:
    """GAP-66-019: T3 strategic mode uses HierarchicalScanner(depth=full)."""

    def test_t3_deep_scan_importable(self) -> None:
        """T3 deep scan bridge function must be importable."""
        from cortex.intelligence.intelligence_wiring_bridges import t3_strategic_deep_scan  # noqa: F401

    def test_t3_strategic_deep_scan_uses_scanner(self) -> None:
        """t3_strategic_deep_scan() must call scanner.scan() for full depth analysis."""
        from cortex.intelligence.intelligence_wiring_bridges import t3_strategic_deep_scan
        from cortex.toolkit.filesystem.hierarchical_scanner import HierarchicalScanner

        mock_scanner = MagicMock(spec=HierarchicalScanner)
        mock_scanner.scan.return_value = []

        result = t3_strategic_deep_scan(scanner=mock_scanner, analysis_target="architecture")

        mock_scanner.scan.assert_called_once()
        assert isinstance(result, dict)
        assert "files_scanned" in result


# AC_COMPLETE: AC-66-C-COVERAGE-GATE-TESTS-20260224T000000Z ✅
