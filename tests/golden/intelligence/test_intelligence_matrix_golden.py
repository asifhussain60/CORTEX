"""
Phase 71-G: Intelligence Matrix Golden Tests — Full-Spectrum Coverage

Closes: GAP-71-G1 (no golden tests for matrix dimensions/wiring/coverage gate)
Tracks: C (P0 cells), D (P1 clusters), E (20×20 extension), G (golden + template)

TDD RED — all assertions target the post-implementation state.
Tests will FAIL until Phase 71 tracks C, D, E are implemented.

AC_START: AC-71-MATRIX-GOLDEN-001
"""
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


# ─────────────────────────────────────────────────────────────────────────────
# Class 1: Matrix Dimension Validation
# ─────────────────────────────────────────────────────────────────────────────
class TestMatrixDimensions:
    """Verify the 20×20 extended matrix dimensions (Phase 71-F)."""

    def test_matrix_has_20_intelligence_capabilities(self) -> None:
        """IC-001..IC-020 must all be registered after 20×20 extension."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            INTELLIGENCE_CAPABILITIES,
        )
        ids = [ic.id for ic in INTELLIGENCE_CAPABILITIES]
        assert len(INTELLIGENCE_CAPABILITIES) == 20, (
            f"Expected 20 IntelligenceCapabilities, got {len(INTELLIGENCE_CAPABILITIES)}. "
            f"Missing: {sorted(set(f'IC-{i:03d}' for i in range(1, 21)) - set(ids))}"
        )

    def test_matrix_has_20_cortex_capabilities(self) -> None:
        """CC-001..CC-020 must all be registered after 20×20 extension."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            CORTEX_CAPABILITIES,
        )
        ids = [cc.id for cc in CORTEX_CAPABILITIES]
        assert len(CORTEX_CAPABILITIES) == 20, (
            f"Expected 20 CortexCapabilities, got {len(CORTEX_CAPABILITIES)}. "
            f"Missing: {sorted(set(f'CC-{i:03d}' for i in range(1, 21)) - set(ids))}"
        )

    def test_ic_016_through_020_exist(self) -> None:
        """New IC-016..IC-020 capabilities must be registered."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            INTELLIGENCE_CAPABILITIES,
        )
        ids = {ic.id for ic in INTELLIGENCE_CAPABILITIES}
        new_ids = {"IC-016", "IC-017", "IC-018", "IC-019", "IC-020"}
        missing = new_ids - ids
        assert not missing, f"Missing new intelligence capabilities: {missing}"

    def test_cc_016_through_020_exist(self) -> None:
        """New CC-016..CC-020 capabilities must be registered."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            CORTEX_CAPABILITIES,
        )
        ids = {cc.id for cc in CORTEX_CAPABILITIES}
        new_ids = {"CC-016", "CC-017", "CC-018", "CC-019", "CC-020"}
        missing = new_ids - ids
        assert not missing, f"Missing new cortex capabilities: {missing}"

    def test_build_returns_matrix_with_20x20_dimensions(self) -> None:
        """IntelligenceMatrixBuilder.build() must return a matrix with 20×20 dimensions."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            IntelligenceMatrixBuilder,
        )
        matrix = IntelligenceMatrixBuilder().build()
        assert matrix.total_capabilities_x == 20, (
            f"Expected x=20, got {matrix.total_capabilities_x}"
        )
        assert matrix.total_capabilities_y == 20, (
            f"Expected y=20, got {matrix.total_capabilities_y}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Class 2: P0-CRITICAL Cells Wired
# ─────────────────────────────────────────────────────────────────────────────
class TestP0CriticalCellsWired:
    """Every P0-CRITICAL matrix cell must be wired after Phase 71-C."""

    @pytest.fixture
    def matrix(self):
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            IntelligenceMatrixBuilder,
        )
        return IntelligenceMatrixBuilder().build()

    def test_no_p0_critical_cells_unwired(self, matrix) -> None:
        """After Phase 71-C all 7 P0 cells must be wired — critical_cells() must be empty."""
        critical = matrix.critical_cells()
        unwired = [c for c in critical if not c.is_wired]
        assert not unwired, (
            f"Still {len(unwired)} P0-CRITICAL unwired cells: "
            + ", ".join(f"{c.intelligence_id}×{c.cortex_id}" for c in unwired)
        )

    def test_ic001_cc001_wired_lens_hierarchical_scanner(self, matrix) -> None:
        """IC-001 (HierarchicalScanning) × CC-001 (LENS) must be wired."""
        cell = next(
            (c for c in matrix.cells if c.intelligence_id == "IC-001" and c.cortex_id == "CC-001"),
            None,
        )
        assert cell is not None, "Cell IC-001×CC-001 not found in matrix"
        assert cell.is_wired, (
            f"IC-001×CC-001 is NOT wired. wire_action: {cell.wire_action}"
        )

    def test_ic004_cc008_wired_pattern_recognition_opj(self, matrix) -> None:
        """IC-004 (PatternRecognition) × CC-008 (OPJ) must be wired."""
        cell = next(
            (c for c in matrix.cells if c.intelligence_id == "IC-004" and c.cortex_id == "CC-008"),
            None,
        )
        assert cell is not None, "Cell IC-004×CC-008 not found in matrix"
        assert cell.is_wired, (
            f"IC-004×CC-008 is NOT wired. wire_action: {cell.wire_action}"
        )

    def test_ic007_cc001_wired_language_analysis_lens(self, matrix) -> None:
        """IC-007 (LanguageAnalysis) × CC-001 (LENS) must be wired."""
        cell = next(
            (c for c in matrix.cells if c.intelligence_id == "IC-007" and c.cortex_id == "CC-001"),
            None,
        )
        assert cell is not None, "Cell IC-007×CC-001 not found in matrix"
        assert cell.is_wired, (
            f"IC-007×CC-001 is NOT wired. wire_action: {cell.wire_action}"
        )

    def test_ic008_cc008_wired_response_template_opj(self, matrix) -> None:
        """IC-008 (ResponseTemplate) × CC-008 (OPJ) must be wired."""
        cell = next(
            (c for c in matrix.cells if c.intelligence_id == "IC-008" and c.cortex_id == "CC-008"),
            None,
        )
        assert cell is not None, "Cell IC-008×CC-008 not found in matrix"
        assert cell.is_wired, (
            f"IC-008×CC-008 is NOT wired. wire_action: {cell.wire_action}"
        )

    def test_ic010_cc004_wired_adaptive_learning_governance(self, matrix) -> None:
        """IC-010 (AdaptiveLearning) × CC-004 (Governance) must be wired."""
        cell = next(
            (c for c in matrix.cells if c.intelligence_id == "IC-010" and c.cortex_id == "CC-004"),
            None,
        )
        assert cell is not None, "Cell IC-010×CC-004 not found in matrix"
        assert cell.is_wired, (
            f"IC-010×CC-004 is NOT wired. wire_action: {cell.wire_action}"
        )

    def test_ic012_cc004_wired_blind_spot_detection_governance(self, matrix) -> None:
        """IC-012 (BlindSpotDetection) × CC-004 (Governance) must be wired."""
        cell = next(
            (c for c in matrix.cells if c.intelligence_id == "IC-012" and c.cortex_id == "CC-004"),
            None,
        )
        assert cell is not None, "Cell IC-012×CC-004 not found in matrix"
        assert cell.is_wired, (
            f"IC-012×CC-004 is NOT wired. wire_action: {cell.wire_action}"
        )

    def test_ic014_cc008_wired_knowledge_retention_opj(self, matrix) -> None:
        """IC-014 (KnowledgeRetention) × CC-008 (OPJ) must be wired."""
        cell = next(
            (c for c in matrix.cells if c.intelligence_id == "IC-014" and c.cortex_id == "CC-008"),
            None,
        )
        assert cell is not None, "Cell IC-014×CC-008 not found in matrix"
        assert cell.is_wired, (
            f"IC-014×CC-008 is NOT wired. wire_action: {cell.wire_action}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Class 3: Coverage Gate
# ─────────────────────────────────────────────────────────────────────────────
class TestCoverageGate:
    """Matrix coverage must meet or exceed COVERAGE_GATE after Phase 71 wiring."""

    def test_coverage_gate_passes_after_wiring(self) -> None:
        """check_coverage_gate() must NOT raise MatrixCoverageError after P0+P1 wiring."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            IntelligenceMatrixBuilder,
            MatrixCoverageError,
        )
        matrix = IntelligenceMatrixBuilder().build()
        try:
            matrix.check_coverage_gate()
        except MatrixCoverageError as e:
            pytest.fail(f"Coverage gate FAILED: {e}")

    def test_coverage_score_at_least_50_percent(self) -> None:
        """matrix.coverage_score must be ≥ 0.50 (COVERAGE_GATE threshold)."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            IntelligenceMatrixBuilder,
        )
        matrix = IntelligenceMatrixBuilder().build()
        score = matrix.coverage_score
        assert score >= 0.50, (
            f"Coverage score {score:.1%} is below 50% gate. "
            f"Wired: {sum(1 for c in matrix.cells if c.is_wired)}/{len(matrix.cells)} cells."
        )

    def test_coverage_score_at_least_80_percent_target(self) -> None:
        """Phase 71 target: matrix.coverage_score must be ≥ 0.80."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            IntelligenceMatrixBuilder,
        )
        matrix = IntelligenceMatrixBuilder().build()
        score = matrix.coverage_score
        assert score >= 0.80, (
            f"Coverage score {score:.1%} is below Phase 71 target of 80%. "
            f"Wired: {sum(1 for c in matrix.cells if c.is_wired)}/{len(matrix.cells)} cells."
        )

    def test_known_wired_pairs_still_wired(self) -> None:
        """Pre-existing wired pairs (IC-008×CC-005, IC-009×CC-006) must remain wired."""
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            IntelligenceMatrixBuilder,
        )
        matrix = IntelligenceMatrixBuilder().build()
        pairs = [("IC-008", "CC-005"), ("IC-009", "CC-006")]
        for ic_id, cc_id in pairs:
            cell = next(
                (c for c in matrix.cells if c.intelligence_id == ic_id and c.cortex_id == cc_id),
                None,
            )
            assert cell is not None, f"Cell {ic_id}×{cc_id} missing from matrix"
            assert cell.is_wired, f"Pre-existing wired cell {ic_id}×{cc_id} is no longer wired"


# ─────────────────────────────────────────────────────────────────────────────
# Class 4: P1-HIGH Cluster Wiring
# ─────────────────────────────────────────────────────────────────────────────
class TestP1HighClusterWiring:
    """All four P1-HIGH clusters must be wired after Phase 71-D."""

    @pytest.fixture
    def matrix(self):
        from cortex.intelligence.cross_cutting.intelligence_matrix_builder import (
            IntelligenceMatrixBuilder,
        )
        return IntelligenceMatrixBuilder().build()

    @pytest.mark.parametrize("ic_id,cc_id,label", [
        ("IC-001", "CC-004", "HierarchicalScanning × Governance"),
        ("IC-001", "CC-008", "HierarchicalScanning × OPJ"),
        ("IC-002", "CC-001", "ContextualUnderstanding × LENS"),
        ("IC-003", "CC-001", "SemanticAnalysis × LENS"),
    ])
    def test_p1_cluster_alpha_wired(self, matrix, ic_id: str, cc_id: str, label: str) -> None:
        """Cluster-Alpha P1 cell must be wired: {label}."""
        cell = next(
            (c for c in matrix.cells if c.intelligence_id == ic_id and c.cortex_id == cc_id),
            None,
        )
        assert cell is not None, f"Cell {ic_id}×{cc_id} ({label}) not in matrix"
        assert cell.is_wired, f"P1 cell {ic_id}×{cc_id} ({label}) NOT wired"

    @pytest.mark.parametrize("ic_id,cc_id,label", [
        ("IC-005", "CC-008", "AnomalyDetection × OPJ"),
        ("IC-006", "CC-001", "TemporalReasoning × LENS"),
        ("IC-010", "CC-008", "AdaptiveLearning × OPJ"),
        ("IC-011", "CC-001", "MetaLearning × LENS"),
    ])
    def test_p1_cluster_beta_wired(self, matrix, ic_id: str, cc_id: str, label: str) -> None:
        """Cluster-Beta P1 cell must be wired: {label}."""
        cell = next(
            (c for c in matrix.cells if c.intelligence_id == ic_id and c.cortex_id == cc_id),
            None,
        )
        assert cell is not None, f"Cell {ic_id}×{cc_id} ({label}) not in matrix"
        assert cell.is_wired, f"P1 cell {ic_id}×{cc_id} ({label}) NOT wired"

    @pytest.mark.parametrize("ic_id,cc_id,label", [
        ("IC-012", "CC-001", "BlindSpotDetection × LENS"),
        ("IC-012", "CC-008", "BlindSpotDetection × OPJ"),
        ("IC-013", "CC-001", "CrossDomainTransfer × LENS"),
        ("IC-013", "CC-004", "CrossDomainTransfer × Governance"),
    ])
    def test_p1_cluster_gamma_wired(self, matrix, ic_id: str, cc_id: str, label: str) -> None:
        """Cluster-Gamma P1 cell must be wired: {label}."""
        cell = next(
            (c for c in matrix.cells if c.intelligence_id == ic_id and c.cortex_id == cc_id),
            None,
        )
        assert cell is not None, f"Cell {ic_id}×{cc_id} ({label}) not in matrix"
        assert cell.is_wired, f"P1 cell {ic_id}×{cc_id} ({label}) NOT wired"

    @pytest.mark.parametrize("ic_id,cc_id,label", [
        ("IC-014", "CC-001", "KnowledgeRetention × LENS"),
        ("IC-014", "CC-004", "KnowledgeRetention × Governance"),
        ("IC-015", "CC-001", "SelfCalibration × LENS"),
        ("IC-015", "CC-004", "SelfCalibration × Governance"),
        ("IC-015", "CC-008", "SelfCalibration × OPJ"),
        ("IC-004", "CC-004", "PatternRecognition × Governance"),
    ])
    def test_p1_cluster_delta_wired(self, matrix, ic_id: str, cc_id: str, label: str) -> None:
        """Cluster-Delta P1 cell must be wired: {label}."""
        cell = next(
            (c for c in matrix.cells if c.intelligence_id == ic_id and c.cortex_id == cc_id),
            None,
        )
        assert cell is not None, f"Cell {ic_id}×{cc_id} ({label}) not in matrix"
        assert cell.is_wired, f"P1 cell {ic_id}×{cc_id} ({label}) NOT wired"


# ─────────────────────────────────────────────────────────────────────────────
# Class 5: Wiring Bridge Module
# ─────────────────────────────────────────────────────────────────────────────
class TestIntelligenceWiringBridges:
    """intelligence_wiring_bridges.py must exist and expose wire_p0_cells() + wire_p1_cells()."""

    def test_wiring_bridges_module_importable(self) -> None:
        """cortex.intelligence.cross_cutting.intelligence_wiring_bridges must be importable."""
        from cortex.intelligence.cross_cutting import intelligence_wiring_bridges  # noqa: F401
        assert intelligence_wiring_bridges is not None

    def test_wire_p0_cells_callable(self) -> None:
        """intelligence_wiring_bridges.wire_p0_cells() must be callable."""
        from cortex.intelligence.cross_cutting.intelligence_wiring_bridges import wire_p0_cells
        assert callable(wire_p0_cells)

    def test_wire_p1_cells_callable(self) -> None:
        """intelligence_wiring_bridges.wire_p1_cells() must be callable."""
        from cortex.intelligence.cross_cutting.intelligence_wiring_bridges import wire_p1_cells
        assert callable(wire_p1_cells)

    def test_wire_p0_cells_returns_wired_count(self) -> None:
        """wire_p0_cells() must return 7 — one for each P0 cell wired."""
        from cortex.intelligence.cross_cutting.intelligence_wiring_bridges import wire_p0_cells
        count = wire_p0_cells()
        assert count == 7, f"Expected wire_p0_cells() to return 7, got {count}"

    def test_workflow_template_exists(self) -> None:
        """intelligence-matrix-wiring-pipeline.yaml must exist in workflow templates."""
        template = (
            REPO_ROOT
            / "cortex-registry"
            / "workflows"
            / "templates"
            / "intelligence"
            / "intelligence-matrix-wiring-pipeline.yaml"
        )
        assert template.exists(), (
            f"Workflow template not found: {template}"
        )

    def test_workflow_template_valid_yaml(self) -> None:
        """intelligence-matrix-wiring-pipeline.yaml must be valid YAML."""
        import yaml
        template = (
            REPO_ROOT
            / "cortex-registry"
            / "workflows"
            / "templates"
            / "intelligence"
            / "intelligence-matrix-wiring-pipeline.yaml"
        )
        data = yaml.safe_load(template.read_text())
        assert "id" in data, "Workflow template missing 'id' field"
        assert "stages" in data, "Workflow template missing 'stages' field"
