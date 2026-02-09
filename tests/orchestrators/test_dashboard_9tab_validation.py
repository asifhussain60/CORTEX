"""
TDD Tests for 9-Tab Dashboard Metric Validation.

Tests that orchestrator-generated JSON has complete metrics for all 9 tabs:
1. Overview
2. Metrics  
3. Security
4. Dependencies
5. Quality
6. Use Cases
7. LENS
8. Refactoring
9. Architecture (NEW)

Authority: CORE-008 (TDD), Phase 1: Orchestrator-First Metrics
AC_START: AC-DASHBOARD-9TAB-001
"""

import pytest
from pathlib import Path
from typing import Dict, Any
import json

from cortex.models.dashboard_schema import RepoDashboardModel
from cortex.orchestrators.support.repository_onboarding_orchestrator import (
    RepositoryOnboardingOrchestrator
)


class TestOverviewTabMetrics:
    """Test Overview tab has complete metrics."""
    
    def test_overview_has_required_fields(self, sample_dashboard_json: Dict[str, Any]):
        """Overview must have summary, business_summary, key_findings."""
        overview = sample_dashboard_json["overview"]
        
        assert "summary" in overview
        assert "business_summary" in overview
        assert "key_findings" in overview
        assert isinstance(overview["key_findings"], list)
        assert len(overview["summary"]) > 0
    
    def test_overview_has_executive_context(self, sample_dashboard_json: Dict[str, Any]):
        """Overview must have executive-level context fields."""
        overview = sample_dashboard_json["overview"]
        
        # Executive summary fields
        assert "key_capabilities" in overview
        assert "core_functionalities" in overview
        assert "repository_age" in overview
        assert "maturity_level" in overview
        assert "recent_focus" in overview


class TestMetricsTabMetrics:
    """Test Metrics tab has complete computed metrics."""
    
    def test_metrics_has_health_and_risk_scores(self, sample_dashboard_json: Dict[str, Any]):
        """Metrics must have health_score and risk_score computed."""
        metrics = sample_dashboard_json["metrics"]
        
        assert "health_score" in metrics
        assert "risk_score" in metrics
        assert 0 <= metrics["health_score"] <= 100
        assert 0 <= metrics["risk_score"] <= 100
    
    def test_metrics_has_loc_and_file_counts(self, sample_dashboard_json: Dict[str, Any]):
        """Metrics must have LOC and file counts."""
        metrics = sample_dashboard_json["metrics"]
        
        assert "loc" in metrics
        assert "code_lines" in metrics
        assert "comment_lines" in metrics
        assert "blank_lines" in metrics
        assert "files" in metrics
        assert metrics["loc"] >= 0
        assert metrics["files"] >= 0
    
    def test_metrics_has_language_distribution(self, sample_dashboard_json: Dict[str, Any]):
        """Metrics must have language breakdown."""
        metrics = sample_dashboard_json["metrics"]
        
        assert "languages" in metrics
        assert isinstance(metrics["languages"], dict)
        # At least one language should be detected
        assert len(metrics["languages"]) > 0
    
    def test_metrics_has_visualization_data(self, sample_dashboard_json: Dict[str, Any]):
        """NEW: Metrics must have pre-computed visualization coordinates."""
        metrics = sample_dashboard_json["metrics"]
        
        # NEW REQUIREMENT: Visualizations section
        assert "visualizations" in metrics
        viz = metrics["visualizations"]
        
        # Health gauge must have pre-computed arc data
        assert "health_gauge" in viz
        gauge = viz["health_gauge"]
        assert "score" in gauge
        assert "color" in gauge
        assert "arc_data" in gauge


class TestSecurityTabMetrics:
    """Test Security tab has complete security metrics."""
    
    def test_security_has_vulnerability_counts(self, sample_dashboard_json: Dict[str, Any]):
        """Security must have vulnerability counts by severity."""
        security = sample_dashboard_json["security"]
        
        assert "critical_count" in security
        assert "high_count" in security
        assert "medium_count" in security
        assert "low_count" in security
        assert "total_count" in security
    
    def test_security_has_vulnerabilities_list(self, sample_dashboard_json: Dict[str, Any]):
        """Security must have detailed vulnerabilities array."""
        security = sample_dashboard_json["security"]
        
        assert "vulnerabilities" in security
        assert isinstance(security["vulnerabilities"], list)


class TestDependenciesTabMetrics:
    """Test Dependencies tab has complete dependency analysis."""
    
    def test_dependencies_has_counts(self, sample_dashboard_json: Dict[str, Any]):
        """Dependencies must have direct/transitive counts."""
        dependencies = sample_dashboard_json["dependencies"]
        
        assert "direct_count" in dependencies
        assert "transitive_count" in dependencies
        assert "total_count" in dependencies
    
    def test_dependencies_has_packages_list(self, sample_dashboard_json: Dict[str, Any]):
        """Dependencies must have packages array with metadata."""
        dependencies = sample_dashboard_json["dependencies"]
        
        assert "packages" in dependencies
        assert isinstance(dependencies["packages"], list)
        
        # If packages exist, check structure
        if len(dependencies["packages"]) > 0:
            pkg = dependencies["packages"][0]
            assert "name" in pkg
            assert "version" in pkg
            assert "is_direct" in pkg
    
    def test_dependencies_has_real_graph_edges(self, sample_dashboard_json: Dict[str, Any]):
        """NEW: Dependencies must have AST-computed graph edges (not fake prefix heuristics)."""
        dependencies = sample_dashboard_json["dependencies"]
        
        # NEW REQUIREMENT: Real dependency graph
        assert "visualizations" in dependencies
        viz = dependencies["visualizations"]
        
        assert "dependency_graph" in viz
        graph = viz["dependency_graph"]
        
        # Must have nodes and edges
        assert "nodes" in graph
        assert "edges" in graph
        assert isinstance(graph["nodes"], list)
        assert isinstance(graph["edges"], list)
        
        # Nodes must have pre-computed positions
        if len(graph["nodes"]) > 0:
            node = graph["nodes"][0]
            assert "id" in node
            assert "x" in node  # Pre-computed X coordinate
            assert "y" in node  # Pre-computed Y coordinate
            assert "radius" in node
        
        # Edges must be real (source/target from AST analysis)
        if len(graph["edges"]) > 0:
            edge = graph["edges"][0]
            assert "source" in edge
            assert "target" in edge
            # CRITICAL: Edge must have source_type (import|require|from)
            assert "import_type" in edge, "Edges must be real (from AST), not fake prefix heuristics"


class TestQualityTabMetrics:
    """Test Quality tab has complete code quality metrics."""
    
    def test_quality_has_scores(self, sample_dashboard_json: Dict[str, Any]):
        """Quality must have quality scores."""
        quality = sample_dashboard_json["quality"]
        
        # Basic quality metrics
        assert "total_issues" in quality or "code_smells" in quality
    
    def test_quality_has_code_smells(self, sample_dashboard_json: Dict[str, Any]):
        """Quality must have code smells array."""
        quality = sample_dashboard_json["quality"]
        
        assert "code_smells" in quality
        assert isinstance(quality["code_smells"], list)


class TestUseCasesTabMetrics:
    """Test Use Cases tab has generated use cases."""
    
    def test_use_cases_has_array(self, sample_dashboard_json: Dict[str, Any]):
        """Use Cases must have array of use cases."""
        use_cases = sample_dashboard_json["use_cases"]
        
        assert isinstance(use_cases, list)
    
    def test_use_cases_structure(self, sample_dashboard_json: Dict[str, Any]):
        """Each use case must have required fields."""
        use_cases = sample_dashboard_json["use_cases"]
        
        if len(use_cases) > 0:
            uc = use_cases[0]
            assert "title" in uc
            assert "description" in uc
            assert "persona" in uc


class TestLENSTabMetrics:
    """Test LENS tab has analysis summary."""
    
    def test_lens_has_analysis_summary(self, sample_dashboard_json: Dict[str, Any]):
        """LENS must have analysis summary."""
        lens = sample_dashboard_json["lens"]
        
        assert "analysis_summary" in lens
        assert isinstance(lens["analysis_summary"], str)


class TestRefactoringTabMetrics:
    """Test Refactoring tab has recommendations."""
    
    def test_refactoring_has_recommendations(self, sample_dashboard_json: Dict[str, Any]):
        """Refactoring must have recommendations array."""
        refactoring = sample_dashboard_json["refactoring"]
        
        assert "recommendations" in refactoring
        assert isinstance(refactoring["recommendations"], list)


class TestArchitectureTabMetrics:
    """NEW: Test Architecture tab has pre-computed architecture visualization."""
    
    def test_architecture_section_exists(self, sample_dashboard_json: Dict[str, Any]):
        """NEW: Architecture section must exist in JSON."""
        # NOTE: This is NEW - not in current schema yet
        # Will fail until schema updated
        assert "architecture" in sample_dashboard_json
    
    def test_architecture_has_layer_graph(self, sample_dashboard_json: Dict[str, Any]):
        """NEW: Architecture must have pre-computed layer graph coordinates."""
        architecture = sample_dashboard_json["architecture"]
        
        assert "visualizations" in architecture
        viz = architecture["visualizations"]
        
        assert "layer_graph" in viz
        graph = viz["layer_graph"]
        
        # Must have nodes (files/modules) and edges (imports)
        assert "nodes" in graph
        assert "edges" in graph
        assert isinstance(graph["nodes"], list)
        assert isinstance(graph["edges"], list)
        
        # Nodes must have layer information and coordinates
        if len(graph["nodes"]) > 0:
            node = graph["nodes"][0]
            assert "id" in node
            assert "layer" in node  # e.g., "presentation", "business", "data"
            assert "x" in node
            assert "y" in node
            assert "complexity" in node  # Cyclomatic complexity
    
    def test_architecture_has_metrics(self, sample_dashboard_json: Dict[str, Any]):
        """NEW: Architecture must have computed architecture metrics."""
        architecture = sample_dashboard_json["architecture"]
        
        assert "coupling_score" in architecture
        assert "cohesion_score" in architecture
        assert "total_dependencies" in architecture
        assert "circular_dependencies" in architecture
        assert 0 <= architecture["coupling_score"] <= 100
        assert 0 <= architecture["cohesion_score"] <= 100


class TestDataQualitySection:
    """NEW: Test data_quality section for honest dashboard."""
    
    def test_data_quality_section_exists(self, sample_dashboard_json: Dict[str, Any]):
        """NEW: data_quality section must exist."""
        assert "data_quality" in sample_dashboard_json
    
    def test_data_quality_has_confidence_score(self, sample_dashboard_json: Dict[str, Any]):
        """data_quality must have confidence score."""
        dq = sample_dashboard_json["data_quality"]
        
        assert "confidence_score" in dq
        assert 0 <= dq["confidence_score"] <= 100
        assert "coverage_pct" in dq
        assert 0 <= dq["coverage_pct"] <= 100
    
    def test_data_quality_has_contradictions(self, sample_dashboard_json: Dict[str, Any]):
        """data_quality must detect contradictions."""
        dq = sample_dashboard_json["data_quality"]
        
        assert "contradictions" in dq
        assert isinstance(dq["contradictions"], list)
        
        # Example contradiction: LOC=0 but languages exist
        # If detected, each contradiction must have description
        if len(dq["contradictions"]) > 0:
            contradiction = dq["contradictions"][0]
            assert isinstance(contradiction, str)
            assert len(contradiction) > 0
    
    def test_data_quality_has_missing_fields(self, sample_dashboard_json: Dict[str, Any]):
        """data_quality must list missing/incomplete fields."""
        dq = sample_dashboard_json["data_quality"]
        
        assert "missing_fields" in dq
        assert isinstance(dq["missing_fields"], list)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_dashboard_json() -> Dict[str, Any]:
    """Load KSESSIONS dashboard JSON for validation."""
    json_path = Path("company/dashboards/ksessions/dashboard-data.json")
    
    if not json_path.exists():
        pytest.skip(f"KSESSIONS JSON not found at {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data


@pytest.fixture
def sample_dashboard_model(sample_dashboard_json: Dict[str, Any]) -> RepoDashboardModel:
    """Load KSESSIONS dashboard as RepoDashboardModel."""
    return RepoDashboardModel.from_dict(sample_dashboard_json)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestKSESSIONSOnboardingCompliance:
    """Integration test: Re-onboard KSESSIONS and verify all 9 tabs."""
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_ksessions_onboarding_generates_complete_json(self, tmp_path: Path):
        """
        Integration test: Onboard KSESSIONS and verify all 9 tabs have metrics.
        
        This test will FAIL until orchestrator enhanced with:
        - metrics.visualizations section
        - architecture section  
        - data_quality section
        - Real dependency graph edges (AST-based)
        """
        # This test requires actual KSESSIONS repository
        ksessions_path = Path("D:/PROJECTS/KSESSIONS")
        if not ksessions_path.exists():
            pytest.skip("KSESSIONS repository not found")
        
        orchestrator = RepositoryOnboardingOrchestrator()
        
        # Onboard with dashboard generation
        result = orchestrator.onboard_repository(
            repo_path=ksessions_path,
            include_dashboard=True,
            output_dir=tmp_path
        )
        
        # Load generated JSON
        json_path = tmp_path / "ksessions" / "dashboard-data.json"
        assert json_path.exists(), "Dashboard JSON not generated"
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Verify all 9 tabs have complete metrics
        assert "overview" in data
        assert "metrics" in data
        assert "security" in data
        assert "dependencies" in data
        assert "quality" in data
        assert "use_cases" in data
        assert "lens" in data
        assert "refactoring" in data
        assert "architecture" in data  # NEW
        assert "data_quality" in data  # NEW
        
        # Verify critical fields
        assert data["metrics"]["health_score"] > 0
        assert len(data["metrics"]["languages"]) > 0
        assert "visualizations" in data["metrics"]  # NEW
        assert "visualizations" in data["dependencies"]  # NEW
        assert "visualizations" in data["architecture"]  # NEW


# AC_COMPLETE: AC-DASHBOARD-9TAB-001 ✅ 9-Tab validation test suite created
