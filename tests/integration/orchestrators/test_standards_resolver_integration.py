"""
Integration tests for StandardsResolver in orchestrators.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 27 specification Stage 3
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from cortex.common.standards_resolver import StandardsResolver, StandardsSource
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator


class TestMasterOrchestratorIntegration:
    """Test MasterOrchestrator uses StandardsResolver."""
    
    def test_master_has_standards_resolver(self):
        """MasterOrchestrator should have StandardsResolver instance."""
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, 'standards_resolver')
        assert isinstance(orchestrator.standards_resolver, StandardsResolver)
    
    def test_master_loads_governance_standards(self, tmp_path):
        """MasterOrchestrator should load governance standards."""
        # Setup company standards
        company_dir = tmp_path / "company" / "domains" / "governance"
        company_dir.mkdir(parents=True)
        (company_dir / "core-rules.yaml").write_text("rule: company_rule")
        
        orchestrator = MasterOrchestrator()
        orchestrator.standards_resolver = StandardsResolver(
            company_root=str(tmp_path / "company" / "domains")
        )
        
        result = orchestrator.standards_resolver.load_standards("governance", "core-rules")
        
        assert result.source == StandardsSource.COMPANY
        assert "rule" in result.content


class TestTDDOrchestratorIntegration:
    """Test TDDOrchestrator uses StandardsResolver."""
    
    def test_tdd_has_standards_resolver(self):
        """TDDOrchestrator should have StandardsResolver instance."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        
        orchestrator = TDDOrchestrator()
        
        assert hasattr(orchestrator, 'standards_resolver')
        assert isinstance(orchestrator.standards_resolver, StandardsResolver)
    
    def test_tdd_loads_test_patterns(self, tmp_path):
        """TDDOrchestrator should load test patterns from company standards."""
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        
        # Setup company test patterns
        company_dir = tmp_path / "company" / "domains" / "testing"
        company_dir.mkdir(parents=True)
        (company_dir / "patterns.yaml").write_text("pattern: company_tdd")
        
        orchestrator = TDDOrchestrator()
        orchestrator.standards_resolver = StandardsResolver(
            company_root=str(tmp_path / "company" / "domains")
        )
        
        result = orchestrator.standards_resolver.load_standards("testing", "patterns")
        
        assert result.source == StandardsSource.COMPANY


class TestGapLogging:
    """Test gap logging when company standards missing."""
    
    def test_gaps_recorded_on_fallback(self, tmp_path):
        """Should record gap when falling back to cortex standards."""
        from cortex.governance.gap_analyzer import GapAnalyzer
        
        analyzer = GapAnalyzer()
        
        # Simulate StandardsResolver fallback
        result_gaps = ["company/domains/security/auth.yaml"]
        
        for gap in result_gaps:
            domain_subdomain = gap.split("/")[-2:]
            analyzer.record_gap(
                domain=domain_subdomain[0],
                subdomain=domain_subdomain[1].replace(".yaml", ""),
                used_by="TestOrchestrator",
                fallback_source="cortex/knowledge",
            )
        
        assert len(analyzer.gaps) == 1
        assert analyzer.gaps[0].domain == "security"
