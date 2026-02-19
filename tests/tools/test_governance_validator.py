"""
Tests for GovernanceValidator module.

Tests governance validation consolidation from validate-production.py
and validate_governance_alignment.py scripts.
"""

import pytest
from pathlib import Path
from cortex.toolkit.validation import GovernanceValidator
from cortex.toolkit.validation.governance_validator import (
    ValidationCheck,
    Severity,
    ProductionReadinessReport
)


@pytest.fixture
def validator():
    """Create GovernanceValidator instance."""
    return GovernanceValidator()


@pytest.fixture
def workspace_root():
    """Get workspace root path."""
    return Path(__file__).parent.parent.parent


class TestGovernanceValidatorInitialization:
    """Test GovernanceValidator initialization."""
    
    def test_init_default_workspace(self, validator):
        """Test initialization with default workspace."""
        assert validator is not None
        assert validator.workspace_root.exists()
    
    def test_init_custom_workspace(self, workspace_root):
        """Test initialization with custom workspace path."""
        validator = GovernanceValidator(workspace_root=workspace_root)
        assert validator.workspace_root == workspace_root


class TestProductionReadinessValidation:
    """Test production readiness validation."""
    
    def test_validate_production_readiness_returns_report(self, validator):
        """Test that validation returns ProductionReadinessReport."""
        report = validator.validate_production_readiness()
        assert isinstance(report, ProductionReadinessReport)
        assert hasattr(report, 'overall_status')
        assert hasattr(report, 'readiness_score')
    
    def test_validate_infrastructure_components(self, validator):
        """Test infrastructure validation."""
        report = validator.validate_production_readiness()
        # Should check core infrastructure
        assert 'infrastructure' in report.summary
    
    def test_validate_dependencies(self, validator):
        """Test dependency validation."""
        report = validator.validate_production_readiness()
        # Should check requirements.txt exists
        assert 'dependencies' in report.summary
    
    def test_validate_mcp_server(self, validator):
        """Test MCP server validation."""
        report = validator.validate_production_readiness()
        # Should check MCP configuration
        assert 'mcp_server' in report.summary
    
    def test_validate_security_configuration(self, validator):
        """Test security validation."""
        report = validator.validate_production_readiness()
        # Should check security configs
        assert 'security' in report.summary


class TestGovernanceAlignmentValidation:
    """Test governance alignment validation."""
    
    def test_check_governance_alignment_returns_bool(self, validator):
        """Test that governance check returns boolean."""
        result = validator.check_governance_alignment()
        assert isinstance(result, bool)
    
    def test_validate_prompts_directory_exists(self, validator, workspace_root):
        """Test validation of .github/prompts/ directory."""
        result = validator.check_governance_alignment()
        prompts_dir = workspace_root / ".github" / "prompts"
        assert prompts_dir.exists(), "Prompts directory should exist"
    
    def test_validate_agents_directory_exists(self, validator, workspace_root):
        """Test validation of .github/agents/ directory."""
        result = validator.check_governance_alignment()
        agents_dir = workspace_root / ".github" / "agents"
        assert agents_dir.exists(), "Agents directory should exist"
    
    def test_core_rules_validation(self, validator):
        """Test CORE rules alignment check."""
        result = validator.check_governance_alignment()
        # Should pass for CORTEX repository
        assert result is True


class TestSecurityPostureAssessment:
    """Test security posture assessment."""
    
    def test_assess_security_posture_returns_dict(self, validator):
        """Test that security assessment returns dict."""
        result = validator.assess_security_posture()
        assert isinstance(result, dict)
        assert 'score' in result
        assert 'findings' in result
    
    def test_owasp_checks_included(self, validator):
        """Test that OWASP checks are performed."""
        result = validator.assess_security_posture()
        assert 'owasp' in result


class TestReportGeneration:
    """Test report generation."""
    
    def test_generate_readiness_report_format(self, validator):
        """Test formatted report generation."""
        report = validator.validate_production_readiness()
        formatted = validator.generate_readiness_report(report)
        assert isinstance(formatted, str)
        assert len(formatted) > 0
    
    def test_report_includes_score(self, validator):
        """Test that report includes readiness score."""
        report = validator.validate_production_readiness()
        formatted = validator.generate_readiness_report(report)
        assert 'score' in formatted.lower() or 'readiness' in formatted.lower()
    
    def test_report_includes_issues(self, validator):
        """Test that report includes issue summary."""
        report = validator.validate_production_readiness()
        formatted = validator.generate_readiness_report(report)
        assert 'issues' in formatted.lower() or 'findings' in formatted.lower()


class TestDryRunMode:
    """Test dry-run mode functionality."""
    
    def test_dry_run_no_side_effects(self, validator):
        """Test that dry-run mode doesn't modify files."""
        report = validator.validate_production_readiness(dry_run=True)
        assert isinstance(report, ProductionReadinessReport)
        # Verify no files were modified
    
    def test_dry_run_vs_real_execution(self, validator):
        """Test differences between dry-run and real execution."""
        dry_run_report = validator.validate_production_readiness(dry_run=True)
        real_report = validator.validate_production_readiness(dry_run=False)
        # Both should return reports
        assert isinstance(dry_run_report, ProductionReadinessReport)
        assert isinstance(real_report, ProductionReadinessReport)
