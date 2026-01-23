"""
Tests for CORE-002 Artifact Validation
AC-IDs tested: CORE-002, AC-CORE-002

Validates that markdown report/status files are suppressed unless explicitly 
requested by user. Rule applies workspace-wide (root + subdirectories).

"""

import pytest
from cortex.brain.core.governance_registry import GovernanceRegistry


class TestCore002ArtifactValidation:
    """Tests for CORE-002 - Markdown Report Suppression (Workspace-Wide)"""
    
    @pytest.fixture
    def registry(self) -> GovernanceRegistry:
        """Create test registry instance."""
        GovernanceRegistry.reset_instance()
        registry = GovernanceRegistry.instance()
        init_result = registry.initialize()
        assert init_result.is_ok(), f"Registry initialization failed: {init_result.error}"
        return registry
    
    # ========================================================================
    # APPROVED LOCATIONS - ALWAYS ALLOWED
    # ========================================================================
    
    def test_markdown_in_docs_approved(self, registry: GovernanceRegistry) -> None:
        """Test AC-CORE-002: Markdown in docs/ is always approved"""
        result = registry.validate_artifact_creation("docs/my-feature.md")
        assert result.is_ok(), f"docs/ markdown should be approved: {result.error}"
        assert result.unwrap() is True
    
    def test_markdown_in_workspaces_docs_approved(self, registry: GovernanceRegistry) -> None:
        """Test AC-CORE-002: Markdown in _workspaces/docs/ is always approved"""
        result = registry.validate_artifact_creation("_workspaces/docs/README.md")
        assert result.is_ok(), f"_workspaces/docs/ markdown should be approved: {result.error}"
        assert result.unwrap() is True
    
    def test_non_markdown_artifacts_approved(self, registry: GovernanceRegistry) -> None:
        """Test AC-CORE-002: Non-markdown files are not restricted"""
        test_cases = [
            "DEPLOYMENT-script.sh",
            "build-config.yaml",
            "requirements.txt",
            "root-script.py",
        ]
        
        for artifact in test_cases:
            result = registry.validate_artifact_creation(artifact)
            assert result.is_ok(), f"{artifact} should be approved: {result.error}"
            assert result.unwrap() is True
    
    # ========================================================================
    # REPORT/STATUS MARKDOWN - SUPPRESSED BY DEFAULT
    # ========================================================================
    
    def test_deployment_status_md_suppressed(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: DEPLOYMENT-STATUS-*.md suppressed unless user requests"""
        result = registry.validate_artifact_creation("DEPLOYMENT-STATUS-2026-01-23.md")
        assert result.is_err(), "DEPLOYMENT-STATUS should be suppressed"
        assert "CORE-002" in result.error
        assert "suppressed" in result.error.lower()
    
    def test_deployment_commands_md_suppressed(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: DEPLOYMENT-QUICK-COMMANDS.md suppressed unless user requests"""
        result = registry.validate_artifact_creation("DEPLOYMENT-QUICK-COMMANDS.md")
        assert result.is_err(), "DEPLOYMENT-QUICK-COMMANDS should be suppressed"
        assert "CORE-002" in result.error
    
    def test_orchestrator_summary_suppressed(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: ORCHESTRATOR-*-SUMMARY.md suppressed unless user requests"""
        result = registry.validate_artifact_creation("ORCHESTRATOR-BOOTSTRAP-SUMMARY.md")
        assert result.is_err(), "ORCHESTRATOR summary should be suppressed"
        assert "CORE-002" in result.error
    
    def test_review_md_suppressed(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: CORTEX-REVIEW-*.md suppressed unless user requests"""
        result = registry.validate_artifact_creation("CORTEX-REVIEW-v4.1-FILE-INDEX.md")
        assert result.is_err(), "CORTEX-REVIEW should be suppressed"
        assert "CORE-002" in result.error
    
    def test_generic_summary_md_suppressed(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: *-summary.md suppressed unless user requests"""
        result = registry.validate_artifact_creation("project-summary.md")
        assert result.is_err(), "*-summary.md should be suppressed"
        assert "CORE-002" in result.error
    
    def test_generic_report_md_suppressed(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: *-report.md suppressed unless user requests"""
        result = registry.validate_artifact_creation("execution-report.md")
        assert result.is_err(), "*-report.md should be suppressed"
        assert "CORE-002" in result.error
    
    def test_status_md_suppressed(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: *-status.md suppressed unless user requests"""
        result = registry.validate_artifact_creation("deployment-status.md")
        assert result.is_err(), "*-status.md should be suppressed"
        assert "CORE-002" in result.error
    
    def test_readme_md_suppressed(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: README.md suppressed unless user requests"""
        result = registry.validate_artifact_creation("README.md")
        assert result.is_err(), "README.md should be suppressed"
        assert "CORE-002" in result.error
    
    # ========================================================================
    # USER EXPLICIT REQUEST - OVERRIDE SUPPRESSION
    # ========================================================================
    
    def test_deployment_status_approved_with_explicit_request(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: User can override suppression with explicit request"""
        result = registry.validate_artifact_creation(
            "DEPLOYMENT-STATUS-2026-01-23.md",
            user_explicit_request=True
        )
        assert result.is_ok(), "User-requested DEPLOYMENT-STATUS should be approved"
        assert result.unwrap() is True
    
    def test_report_approved_with_explicit_request(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: User-requested reports are approved"""
        test_cases = [
            "execution-report.md",
            "project-summary.md",
            "deployment-status.md",
            "README.md",
        ]
        
        for artifact in test_cases:
            result = registry.validate_artifact_creation(
                artifact,
                user_explicit_request=True
            )
            assert result.is_ok(), f"User-requested {artifact} should be approved"
    
    def test_with_ac_id_tracking(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: AC-ID is included in violation message"""
        result = registry.validate_artifact_creation(
            "DEPLOYMENT-TEST.md",
            ac_id="AC-TEST-001"
        )
        assert result.is_err(), "Should be suppressed"
        assert "AC-TEST-001" in result.error, "AC-ID should be in error message"
    
    # ========================================================================
    # WORKSPACE-WIDE APPLICATION
    # ========================================================================
    
    def test_report_suppressed_in_subdirectories(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: Report suppression applies to all subdirectories"""
        test_cases = [
            "scripts/deployment-status.md",
            "cortex/reports/execution-report.md",
            "docs_custom/project-summary.md",  # Not in approved docs paths
            "subdir/nested/README.md",
        ]
        
        for artifact in test_cases:
            result = registry.validate_artifact_creation(artifact)
            assert result.is_err(), f"{artifact} should be suppressed anywhere in workspace"
    
    def test_approved_docs_in_any_nesting(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: Approved docs/ paths work at any nesting level"""
        test_cases = [
            "docs/report.md",  # Allowed: top-level docs/
            "docs/guides/deep/report.md",  # Allowed: nested in docs/
            "_workspaces/docs/status.md",  # Allowed: workspaces docs
        ]
        
        for artifact in test_cases:
            result = registry.validate_artifact_creation(artifact)
            assert result.is_ok(), f"{artifact} should be approved in docs/"


class TestCore002Integration:
    """Integration tests for CORE-002 enforcement"""
    
    def test_governance_rule_loaded(self) -> None:
        """Test that CORE-002 rule is loaded from YAML"""
        GovernanceRegistry.reset_instance()
        registry = GovernanceRegistry.instance()
        init_result = registry.initialize()
        
        assert init_result.is_ok(), "Registry should initialize"
        
        rule_result = registry.get_rule("CORE-002")
        assert rule_result.is_ok(), "CORE-002 rule should be retrievable"
        
        rule = rule_result.unwrap()
        assert rule is not None, "CORE-002 rule should exist"
        assert rule.rule_id == "CORE-002"
        assert rule.tier == 0, "CORE-002 should be TIER 0 (immutable)"
        assert rule.severity == "blocked", "CORE-002 severity should be 'blocked'"
