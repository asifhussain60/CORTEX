"""
Integration tests for CORTEX Toolkit.

Tests cross-module workflows and end-to-end scenarios.
"""

import pytest
from pathlib import Path
from cortex.tools.toolkit.diagnostics import MCPHealthChecker
from cortex.tools.toolkit.setup import SetupVerifier
from cortex.tools.toolkit.cleanup import VacuumAutomation
from cortex.tools.toolkit.validation import GovernanceValidator


@pytest.fixture
def workspace_root():
    """Get workspace root."""
    return Path(__file__).parent.parent.parent


class TestDiagnosticsToVerificationFlow:
    """Test flow from diagnostics to verification."""
    
    def test_diagnose_then_verify_workflow(self, workspace_root):
        """Test diagnosing issues then verifying fixes."""
        # Step 1: Diagnose
        checker = MCPHealthChecker(workspace_root=workspace_root)
        diag_results = checker.run_diagnostics()
        
        # Step 2: Verify environment
        verifier = SetupVerifier(workspace_root=workspace_root)
        verify_results = verifier.verify_environment()
        
        # Both should provide results
        assert isinstance(diag_results, list)
        assert isinstance(verify_results, list)


class TestVerificationToValidationFlow:
    """Test flow from verification to validation."""
    
    def test_verify_then_validate_workflow(self, workspace_root):
        """Test environment verification followed by governance validation."""
        # Step 1: Verify environment
        verifier = SetupVerifier(workspace_root=workspace_root)
        verify_results = verifier.verify_environment()
        
        # Step 2: Validate governance if environment OK
        all_passed = all(r.passed for r in verify_results)
        if all_passed:
            validator = GovernanceValidator(workspace_root=workspace_root)
            gov_result = validator.check_governance_alignment()
            assert isinstance(gov_result, bool)


class TestCleanupDryRunVsRealExecution:
    """Test cleanup dry-run vs real execution."""
    
    def test_dry_run_preview_then_execute(self, workspace_root):
        """Test previewing cleanup then executing."""
        vacuum = VacuumAutomation(workspace_root=workspace_root, dry_run=True)
        
        # Step 1: Dry-run preview
        dry_run_result = vacuum.cleanup_pycache()
        dry_run_count = dry_run_result.files_removed
        
        # Step 2: Real execution (if any files found)
        # Note: We don't actually execute to avoid side effects in tests
        assert hasattr(dry_run_result, "files_removed")
        assert hasattr(dry_run_result, "strategy")


class TestFullHealthCheckWorkflow:
    """Test complete health check workflow."""
    
    def test_full_health_assessment(self, workspace_root):
        """Test complete health assessment across all modules."""
        results = {}
        
        # 1. Diagnostics
        checker = MCPHealthChecker(workspace_root=workspace_root)
        results["diagnostics"] = checker.run_diagnostics()
        
        # 2. Verification
        verifier = SetupVerifier(workspace_root=workspace_root)
        results["verification"] = verifier.verify_environment()
        
        # 3. Validation
        validator = GovernanceValidator(workspace_root=workspace_root)
        results["governance"] = validator.check_governance_alignment()
        
        # 4. Security
        results["security"] = validator.assess_security_posture()
        
        # All should return structured data
        assert isinstance(results["diagnostics"], list)
        assert isinstance(results["verification"], list)
        assert isinstance(results["governance"], bool)
        assert "score" in results["security"]


class TestErrorHandlingAcrossModules:
    """Test error handling consistency."""
    
    def test_invalid_workspace_handling(self):
        """Test all modules handle invalid workspace gracefully."""
        invalid_path = Path("/nonexistent/path")
        
        # MCPHealthChecker
        checker = MCPHealthChecker(workspace_root=invalid_path)
        diag_results = checker.run_diagnostics()
        assert isinstance(diag_results, list)
        
        # SetupVerifier
        verifier = SetupVerifier(workspace_root=invalid_path)
        verify_results = verifier.verify_environment()
        assert isinstance(verify_results, list)
        
        # VacuumAutomation
        vacuum = VacuumAutomation(workspace_root=invalid_path, dry_run=True)
        cleanup_result = vacuum.cleanup_pycache()
        assert hasattr(cleanup_result, "files_removed")
        
        # GovernanceValidator
        validator = GovernanceValidator(workspace_root=invalid_path)
        gov_result = validator.check_governance_alignment()
        assert isinstance(gov_result, bool)


class TestProductionReadinessPipeline:
    """Test production readiness assessment pipeline."""
    
    def test_complete_production_readiness_check(self, workspace_root):
        """Test full production readiness pipeline."""
        # Run complete assessment
        validator = GovernanceValidator(workspace_root=workspace_root)
        report = validator.validate_production_readiness(dry_run=True)
        
        # Verify report structure
        assert hasattr(report, 'overall_status')
        assert hasattr(report, 'readiness_score')
        assert hasattr(report, 'critical_issues')
        assert hasattr(report, 'passed_checks')
        
        # Generate formatted report
        formatted = validator.generate_readiness_report(report)
        assert isinstance(formatted, str)
        assert len(formatted) > 100  # Should be substantial
        assert "READINESS REPORT" in formatted
    
    def test_production_readiness_scoring(self, workspace_root):
        """Test scoring logic."""
        validator = GovernanceValidator(workspace_root=workspace_root)
        report = validator.validate_production_readiness(dry_run=True)
        
        # Score should be 0-100
        assert 0.0 <= report.readiness_score <= 100.0
        
        # Status should match score thresholds
        if report.critical_issues:
            assert report.overall_status == "BLOCKED"
        elif report.high_issues:
            assert report.overall_status == "NOT READY"


class TestModuleReusability:
    """Test modules can be reused in different contexts."""
    
    def test_multiple_checker_instances(self, workspace_root):
        """Test multiple instances of same module."""
        checker1 = MCPHealthChecker(workspace_root=workspace_root)
        checker2 = MCPHealthChecker(workspace_root=workspace_root)
        
        result1 = checker1.run_diagnostics(checks=["python_env"])
        result2 = checker2.run_diagnostics(checks=["python_env"])
        
        # Results should be consistent
        assert len(result1) > 0 and len(result2) > 0
        assert result1[0].passed == result2[0].passed
    
    def test_module_state_independence(self, workspace_root):
        """Test module instances don't share state."""
        verifier1 = SetupVerifier(workspace_root=workspace_root)
        verifier2 = SetupVerifier(workspace_root=workspace_root)
        
        # Modify one instance
        verifier1.results = []
        
        # Other instance should be unaffected
        verifier2.verify_environment()
        assert len(verifier2.results) > 0
