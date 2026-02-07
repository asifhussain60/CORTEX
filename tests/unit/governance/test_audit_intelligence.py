"""
Tests for AuditIntelligence - Auto-discover orchestrators and track coverage.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 27 specification Stage 4
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from cortex.governance.audit_intelligence import (
    AuditIntelligence,
    OrchestratorCoverage,
    CoverageReport,
)


class TestAuditIntelligenceBasic:
    """Test basic AuditIntelligence functionality."""
    
    def test_intelligence_initializes(self):
        """AuditIntelligence initializes with wiring path."""
        intelligence = AuditIntelligence()
        
        assert intelligence is not None
        assert hasattr(intelligence, 'wiring_path')
    
    def test_orchestrator_coverage_dataclass(self):
        """OrchestratorCoverage tracks integration status."""
        coverage = OrchestratorCoverage(
            name="MasterOrchestrator",
            has_standards_resolver=True,
            integration_status="INTEGRATED",
        )
        
        assert coverage.name == "MasterOrchestrator"
        assert coverage.has_standards_resolver is True
        assert coverage.integration_status == "INTEGRATED"


class TestOrchestratorDiscovery:
    """Test orchestrator discovery from wiring.yaml."""
    
    def test_discovers_orchestrators_from_wiring(self, tmp_path):
        """Should discover orchestrators from wiring.yaml."""
        # Create mock wiring.yaml
        wiring_file = tmp_path / "wiring.yaml"
        wiring_content = """
orchestrators:
  - name: MasterOrchestrator
    class: cortex.orchestrators.core.master_orchestrator.MasterOrchestrator
  - name: TDDOrchestrator
    class: cortex.orchestrators.core.tdd_orchestrator.TDDOrchestrator
  - name: PlanOrchestrator
    class: cortex.orchestrators.support.plan_orchestrator.PlanOrchestrator
"""
        wiring_file.write_text(wiring_content)
        
        intelligence = AuditIntelligence(wiring_path=str(wiring_file))
        orchestrators = intelligence.discover_orchestrators()
        
        assert len(orchestrators) >= 3
        assert any(o == "MasterOrchestrator" for o in orchestrators)
    
    def test_handles_missing_wiring_file(self, tmp_path):
        """Should handle missing wiring.yaml gracefully."""
        intelligence = AuditIntelligence(wiring_path=str(tmp_path / "nonexistent.yaml"))
        
        orchestrators = intelligence.discover_orchestrators()
        
        assert orchestrators == []


class TestCoverageTracking:
    """Test standards integration coverage tracking."""
    
    def test_checks_orchestrator_integration_status(self):
        """Should check if orchestrator has StandardsResolver."""
        intelligence = AuditIntelligence()
        
        # Mock orchestrator with standards_resolver
        mock_orch = Mock()
        mock_orch.standards_resolver = Mock()
        
        has_resolver = intelligence._check_has_standards_resolver(mock_orch)
        
        assert has_resolver is True
    
    def test_generates_coverage_report(self):
        """Should generate coverage report with statistics."""
        intelligence = AuditIntelligence()
        
        # Mock discovered orchestrators
        intelligence._orchestrators = [
            "MasterOrchestrator",
            "TDDOrchestrator",
            "PlanOrchestrator",
        ]
        
        # Mock coverage data
        intelligence._coverage = [
            OrchestratorCoverage("MasterOrchestrator", True, "INTEGRATED"),
            OrchestratorCoverage("TDDOrchestrator", True, "INTEGRATED"),
            OrchestratorCoverage("PlanOrchestrator", False, "NOT_INTEGRATED"),
        ]
        
        report = intelligence.generate_coverage_report()
        
        assert isinstance(report, CoverageReport)
        assert report.total_orchestrators == 3
        assert report.integrated_count == 2
        assert report.coverage_percentage == pytest.approx(66.67, abs=0.1)


class TestRecommendationGeneration:
    """Test integration recommendation generation."""
    
    def test_generates_recommendations_for_unintegrated(self):
        """Should generate recommendations for orchestrators without integration."""
        intelligence = AuditIntelligence()
        
        intelligence._coverage = [
            OrchestratorCoverage("PlanOrchestrator", False, "NOT_INTEGRATED"),
        ]
        
        report = intelligence.generate_coverage_report()
        
        assert len(report.recommendations) == 1
        assert "PlanOrchestrator" in report.recommendations[0]
        assert "StandardsResolver" in report.recommendations[0]
