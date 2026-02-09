"""
Phase 61: Legacy Code Audit Orchestrator - Test Suite

Tests for LegacyCodeAuditOrchestrator workflow integration.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from cortex.orchestrators.support.legacy_code_audit_orchestrator import (
    LegacyCodeAuditOrchestrator,
)


class TestLegacyCodeAuditOrchestrator:
    """Tests for LegacyCodeAuditOrchestrator"""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository"""
        tmpdir = tempfile.mkdtemp()
        repo_path = Path(tmpdir)
        
        # Create directory structure
        (repo_path / "cortex" / "modules").mkdir(parents=True)
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(tmpdir)
    
    def test_orchestrator_initialization(self, temp_repo):
        """Test orchestrator initialization"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        assert orchestrator.repo_root == temp_repo
        assert orchestrator.issues == []
    
    def test_execute_audit_returns_dict(self, temp_repo):
        """Test execute_audit returns dict"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        result = orchestrator.execute_audit()
        
        assert isinstance(result, dict)
        assert "status" in result
        assert "timestamp" in result
        assert "total_issues" in result
    
    def test_get_audit_results(self, temp_repo):
        """Test retrieving audit results"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        orchestrator.execute_audit()
        
        results = orchestrator.get_audit_results()
        assert isinstance(results, list)
    
    def test_get_high_priority_issues(self, temp_repo):
        """Test filtering high priority issues"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        orchestrator.execute_audit()
        
        high_priority = orchestrator.get_high_priority_issues()
        assert isinstance(high_priority, list)
    
    def test_get_removal_candidates(self, temp_repo):
        """Test getting removal candidates"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        orchestrator.execute_audit()
        
        candidates = orchestrator.get_removal_candidates()
        assert isinstance(candidates, list)
    
    def test_removal_approval_workflow(self, temp_repo):
        """Test removal approval workflow"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        orchestrator.execute_audit()
        
        candidates = orchestrator.get_removal_candidates()
        
        if candidates:
            file_path = candidates[0].file_path
            success = orchestrator.approve_removal(file_path)
            assert isinstance(success, bool)
    
    def test_rejection_workflow(self, temp_repo):
        """Test removal rejection workflow"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        orchestrator.execute_audit()
        
        candidates = orchestrator.get_removal_candidates()
        
        if candidates:
            file_path = candidates[0].file_path
            success = orchestrator.reject_removal(file_path, "Still needed")
            assert isinstance(success, bool)
    
    def test_get_approved_removals(self, temp_repo):
        """Test retrieving approved removals"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        orchestrator.execute_audit()
        
        approved = orchestrator.get_approved_removals()
        assert isinstance(approved, list)
    
    def test_generate_audit_report(self, temp_repo):
        """Test audit report generation"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        orchestrator.execute_audit()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "audit_report.yaml"
            orchestrator.generate_audit_report(output_path)
            assert output_path.exists()
    
    def test_get_removal_cost_analysis(self, temp_repo):
        """Test cost analysis of removals"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        orchestrator.execute_audit()
        
        analysis = orchestrator.get_removal_cost_analysis()
        
        assert isinstance(analysis, dict)
        assert "safe_removal_count" in analysis
        assert "estimated_lines_to_remove" in analysis
        assert "risk_level" in analysis
    
    def test_generate_migration_guide(self, temp_repo):
        """Test migration guide generation"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        orchestrator.execute_audit()
        
        guide = orchestrator.generate_migration_guide()
        
        assert isinstance(guide, dict)
        assert "title" in guide
        assert "total_items" in guide
        assert "migrations" in guide
    
    def test_export_governance_audit(self, temp_repo):
        """Test governance audit export"""
        orchestrator = LegacyCodeAuditOrchestrator(temp_repo)
        orchestrator.execute_audit()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "governance_audit.json"
            orchestrator.export_governance_audit(output_path)
            assert output_path.exists()


class TestOrchestratorWorkflow:
    """Integration tests for complete workflow"""
    
    def test_complete_audit_workflow(self):
        """Test complete audit workflow from start to finish"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            (repo_path / "cortex").mkdir()
            
            # Initialize orchestrator
            orchestrator = LegacyCodeAuditOrchestrator(repo_path)
            
            # Execute audit
            result = orchestrator.execute_audit()
            assert result["status"] == "audit_complete"
            
            # Get results
            issues = orchestrator.get_audit_results()
            assert isinstance(issues, list)
            
            # Get candidates
            candidates = orchestrator.get_removal_candidates()
            assert isinstance(candidates, list)


class TestOrchhestratorIntegration:
    """Integration with governance systems"""
    
    def test_audit_timestamp_present(self):
        """Test that audit includes timestamp"""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = LegacyCodeAuditOrchestrator(Path(tmpdir))
            result = orchestrator.execute_audit()
            
            assert "timestamp" in result
            assert result["timestamp"]  # Not empty
    
    def test_governance_audit_export(self):
        """Test governance audit trail export"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            orchestrator = LegacyCodeAuditOrchestrator(repo_path)
            orchestrator.execute_audit()
            
            output_path = Path(tmpdir) / "governance.json"
            orchestrator.export_governance_audit(output_path)
            
            assert output_path.exists()
            
            # Verify JSON content
            import json
            with open(output_path) as f:
                data = json.load(f)
                assert "phase" in data
                assert data["phase"] == "phase-61"
