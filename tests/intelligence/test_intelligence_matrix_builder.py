"""
Tests for IntelligenceMatrixBuilder — Cross-Cutting Intelligence Layer
======================================================================
Phase 65 — ENH-MATRIX-001

TDD RED phase: These tests must pass before any implementation changes.
Authority: CORE-008 (TDD mandatory), CORE-011 (type hints), CORE-012 (docstrings)

AC_START: AC-MATRIX-TEST-001
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
    CapabilityDimension,
    CortexCapability,
    IntelligenceCapability,
    IntelligenceMatrix,
    IntelligenceMatrixBuilder,
    IntelligenceScore,
    MatrixCell,
    INTELLIGENCE_CAPABILITIES,
    CORTEX_CAPABILITIES,
)
from cortex.intelligence.cross_cutting import CortexIntelligenceMatrix  # re-export alias


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def builder() -> IntelligenceMatrixBuilder:
    """Return a fresh IntelligenceMatrixBuilder."""
    return IntelligenceMatrixBuilder()


@pytest.fixture
def matrix(builder: IntelligenceMatrixBuilder) -> IntelligenceMatrix:
    """Return a built matrix from default catalogues."""
    return builder.build()


# ─────────────────────────────────────────────────────────────────────────────
# Catalogue completeness
# ─────────────────────────────────────────────────────────────────────────────

class TestCapabilityDataCatalogue:
    """Validate the x and y capability catalogues are complete and well-formed."""

    def test_intelligence_capabilities_non_empty(self) -> None:
        """x-axis catalogue must have at least 8 capabilities."""
        assert len(INTELLIGENCE_CAPABILITIES) >= 8

    def test_cortex_capabilities_non_empty(self) -> None:
        """y-axis catalogue must have at least 8 capabilities."""
        assert len(CORTEX_CAPABILITIES) >= 8

    def test_all_intelligence_capabilities_have_required_fields(self) -> None:
        """Every x-capability must have id, name, module, dimension, description."""
        for cap in INTELLIGENCE_CAPABILITIES:
            assert cap.id, f"Missing id: {cap}"
            assert cap.name, f"Missing name: {cap.id}"
            assert cap.module, f"Missing module: {cap.id}"
            assert isinstance(cap.dimension, CapabilityDimension), f"Bad dimension: {cap.id}"
            assert cap.description, f"Missing description: {cap.id}"
            assert isinstance(cap.tags, list), f"Tags must be list: {cap.id}"

    def test_all_cortex_capabilities_have_required_fields(self) -> None:
        """Every y-capability must have id, name, module, dimension, description."""
        for cap in CORTEX_CAPABILITIES:
            assert cap.id, f"Missing id: {cap}"
            assert cap.name, f"Missing name: {cap.id}"
            assert cap.module, f"Missing module: {cap.id}"
            assert isinstance(cap.dimension, CapabilityDimension), f"Bad dimension: {cap.id}"
            assert cap.description, f"Missing description: {cap.id}"

    def test_intelligence_capability_ids_are_unique(self) -> None:
        """x-axis IDs must be unique."""
        ids = [c.id for c in INTELLIGENCE_CAPABILITIES]
        assert len(ids) == len(set(ids)), "Duplicate intelligence capability IDs detected"

    def test_cortex_capability_ids_are_unique(self) -> None:
        """y-axis IDs must be unique."""
        ids = [c.id for c in CORTEX_CAPABILITIES]
        assert len(ids) == len(set(ids)), "Duplicate CORTEX capability IDs detected"

    def test_coverage_values_in_range(self) -> None:
        """current_coverage must be 0.0–1.0."""
        for cap in INTELLIGENCE_CAPABILITIES:
            assert 0.0 <= cap.current_coverage <= 1.0, (
                f"{cap.id} has invalid coverage: {cap.current_coverage}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Matrix building
# ─────────────────────────────────────────────────────────────────────────────

class TestIntelligenceMatrixBuilder:
    """Test IntelligenceMatrixBuilder.build() logic."""

    def test_build_returns_matrix_instance(self, builder: IntelligenceMatrixBuilder) -> None:
        """build() must return an IntelligenceMatrix."""
        result = builder.build()
        assert isinstance(result, IntelligenceMatrix)

    def test_matrix_has_cells(self, matrix: IntelligenceMatrix) -> None:
        """Matrix must produce at least 1 cell."""
        assert len(matrix.cells) > 0

    def test_matrix_counts_x_and_y(self, matrix: IntelligenceMatrix) -> None:
        """Matrix must record correct x and y catalogue sizes."""
        assert matrix.total_capabilities_x == len(INTELLIGENCE_CAPABILITIES)
        assert matrix.total_capabilities_y == len(CORTEX_CAPABILITIES)

    def test_matrix_has_critical_cells(self, matrix: IntelligenceMatrix) -> None:
        """Matrix must produce at least 1 P0-CRITICAL cell."""
        assert len([c for c in matrix.cells if c.score == IntelligenceScore.CRITICAL]) >= 1

    def test_matrix_has_high_cells(self, matrix: IntelligenceMatrix) -> None:
        """Matrix must produce at least 1 P1-HIGH cell."""
        assert len([c for c in matrix.cells if c.score == IntelligenceScore.HIGH]) >= 1

    def test_all_cells_have_rationale(self, matrix: IntelligenceMatrix) -> None:
        """Every cell must have a non-empty rationale."""
        for cell in matrix.cells:
            assert cell.rationale, f"Cell {cell.intelligence_id}×{cell.cortex_id} missing rationale"

    def test_all_cells_have_wire_action(self, matrix: IntelligenceMatrix) -> None:
        """Every cell must have a non-empty wire_action."""
        for cell in matrix.cells:
            assert cell.wire_action, f"Cell {cell.intelligence_id}×{cell.cortex_id} missing wire_action"

    def test_all_cells_have_valid_dimension_pair(self, matrix: IntelligenceMatrix) -> None:
        """Every cell dimension_pair must be valid CapabilityDimension values."""
        for cell in matrix.cells:
            dim_x, dim_y = cell.dimension_pair
            assert isinstance(dim_x, CapabilityDimension), f"Invalid x dimension: {cell.intelligence_id}"
            assert isinstance(dim_y, CapabilityDimension), f"Invalid y dimension: {cell.cortex_id}"

    def test_wired_count_matches_is_wired_flags(self, matrix: IntelligenceMatrix) -> None:
        """wired_count must equal the number of is_wired=True cells."""
        actual_wired = sum(1 for c in matrix.cells if c.is_wired)
        assert matrix.wired_count == actual_wired

    def test_coverage_score_in_range(self, matrix: IntelligenceMatrix) -> None:
        """coverage_score must be 0.0–1.0."""
        assert 0.0 <= matrix.coverage_score <= 1.0

    def test_custom_catalogues_are_respected(self, builder: IntelligenceMatrixBuilder) -> None:
        """build() with custom catalogues must use only those capabilities."""
        x = [
            IntelligenceCapability(
                id="IC-T1",
                name="TestIntelligence",
                module="cortex.test.intelligence",
                dimension=CapabilityDimension.LENS,
                description="Test intelligence capability",
                tags=["ast", "semantic"],
            )
        ]
        y = [
            CortexCapability(
                id="CC-T1",
                name="TestToolkit",
                module="cortex.test.toolkit",
                dimension=CapabilityDimension.TOOLKIT,
                description="Test cortex capability",
                tags=["scan", "batch"],
            )
        ]
        matrix = builder.build(intelligence_capabilities=x, cortex_capabilities=y)
        assert matrix.total_capabilities_x == 1
        assert matrix.total_capabilities_y == 1


# ─────────────────────────────────────────────────────────────────────────────
# Matrix helpers
# ─────────────────────────────────────────────────────────────────────────────

class TestIntelligenceMatrixHelpers:
    """Test IntelligenceMatrix helper methods."""

    def test_critical_cells_returns_only_unwired_critical(self, matrix: IntelligenceMatrix) -> None:
        """critical_cells() must return only CRITICAL + not wired."""
        for cell in matrix.critical_cells():
            assert cell.score == IntelligenceScore.CRITICAL
            assert not cell.is_wired

    def test_high_cells_returns_only_unwired_high(self, matrix: IntelligenceMatrix) -> None:
        """high_cells() must return only HIGH + not wired."""
        for cell in matrix.high_cells():
            assert cell.score == IntelligenceScore.HIGH
            assert not cell.is_wired

    def test_to_dict_is_json_serializable(self, matrix: IntelligenceMatrix) -> None:
        """to_dict() must produce a JSON-serializable dict."""
        d = matrix.to_dict()
        serialized = json.dumps(d)  # must not raise
        assert isinstance(serialized, str)

    def test_to_dict_has_required_keys(self, matrix: IntelligenceMatrix) -> None:
        """to_dict() must include all required top-level keys."""
        d = matrix.to_dict()
        for key in ("total_x", "total_y", "wired", "coverage_score", "critical_unwired", "high_unwired", "cells"):
            assert key in d, f"Missing key: {key}"

    def test_to_dict_cells_have_required_fields(self, matrix: IntelligenceMatrix) -> None:
        """Each cell dict must include x, y, score, rationale, wire_action, is_wired."""
        d = matrix.to_dict()
        for cell in d["cells"]:
            for field in ("x", "y", "score", "rationale", "wire_action", "is_wired"):
                assert field in cell, f"Cell missing field: {field}"


# ─────────────────────────────────────────────────────────────────────────────
# Report rendering
# ─────────────────────────────────────────────────────────────────────────────

class TestMatrixReportRendering:
    """Test render_matrix_report() for VS Code Copilot Chat formatting."""

    def test_report_returns_string(self, builder: IntelligenceMatrixBuilder, matrix: IntelligenceMatrix) -> None:
        """render_matrix_report() must return a string."""
        report = builder.render_matrix_report(matrix)
        assert isinstance(report, str)

    def test_report_contains_header(self, builder: IntelligenceMatrixBuilder, matrix: IntelligenceMatrix) -> None:
        """Report must contain the matrix header line."""
        report = builder.render_matrix_report(matrix)
        assert "Intelligence Matrix" in report

    def test_report_contains_critical_section(self, builder: IntelligenceMatrixBuilder, matrix: IntelligenceMatrix) -> None:
        """Report must contain P0-CRITICAL section when critical cells exist."""
        report = builder.render_matrix_report(matrix)
        if matrix.critical_cells():
            assert "P0-CRITICAL" in report

    def test_report_contains_ac_complete_marker(self, builder: IntelligenceMatrixBuilder, matrix: IntelligenceMatrix) -> None:
        """Report must contain AC_COMPLETE marker (CORE requirement)."""
        report = builder.render_matrix_report(matrix)
        assert "AC_COMPLETE" in report

    def test_report_never_writes_to_file(self, builder: IntelligenceMatrixBuilder, matrix: IntelligenceMatrix) -> None:
        """render_matrix_report() must never write to filesystem (CORE-002)."""
        report = builder.render_matrix_report(matrix)
        # If it returns a string, it hasn't written to disk
        assert isinstance(report, str)
        # Verify no side-effect files created in CWD
        import os
        new_md_files = [f for f in os.listdir(".") if f.endswith(".md") and "matrix" in f.lower()]
        assert not new_md_files, f"CORE-002 violation: report written to file: {new_md_files}"


# ─────────────────────────────────────────────────────────────────────────────
# Persist matrix
# ─────────────────────────────────────────────────────────────────────────────

class TestMatrixPersistence:
    """Test persist_matrix() writes to .cortex-runtime/ only (CORE-002)."""

    def test_persist_writes_to_cortex_runtime(
        self,
        builder: IntelligenceMatrixBuilder,
        matrix: IntelligenceMatrix,
        tmp_path: Path,
    ) -> None:
        """persist_matrix() must write JSON to the specified path."""
        output = tmp_path / "test-matrix.json"
        result_path = builder.persist_matrix(matrix, output_path=output)
        assert result_path == output
        assert output.exists()

    def test_persist_writes_valid_json(
        self,
        builder: IntelligenceMatrixBuilder,
        matrix: IntelligenceMatrix,
        tmp_path: Path,
    ) -> None:
        """Persisted file must be valid JSON."""
        output = tmp_path / "test-matrix.json"
        builder.persist_matrix(matrix, output_path=output)
        loaded = json.loads(output.read_text(encoding="utf-8"))
        assert "cells" in loaded

    def test_persist_never_writes_md_file(
        self,
        builder: IntelligenceMatrixBuilder,
        matrix: IntelligenceMatrix,
        tmp_path: Path,
    ) -> None:
        """persist_matrix() must only write .json — never .md (CORE-002)."""
        output = tmp_path / "test-matrix.json"
        builder.persist_matrix(matrix, output_path=output)
        md_files = list(tmp_path.glob("*.md"))
        assert not md_files, f"CORE-002 violation: .md file written: {md_files}"


# ─────────────────────────────────────────────────────────────────────────────
# MCP tool class import check
# ─────────────────────────────────────────────────────────────────────────────

class TestMCPToolRegistration:
    """Verify CortexIntelligenceMatrix is importable from the MCP tools layer."""

    def test_cortex_intelligence_matrix_importable(self) -> None:
        """CortexIntelligenceMatrix must be importable from cortex.mcp.tools."""
        from cortex.mcp.tools import CortexIntelligenceMatrix  # noqa: F401
        assert CortexIntelligenceMatrix is not None

    def test_cortex_intelligence_matrix_in_all_tools(self) -> None:
        """CortexIntelligenceMatrix must be in ALL_TOOLS list."""
        from cortex.mcp.tools import ALL_TOOLS, CortexIntelligenceMatrix
        names = [t.__name__ for t in ALL_TOOLS]
        assert "CortexIntelligenceMatrix" in names, (
            "CortexIntelligenceMatrix not registered in ALL_TOOLS — MCP exposure broken"
        )

# AC_COMPLETE: AC-MATRIX-TEST-001 ✅
