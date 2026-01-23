"""
Tests for CORE-002 Artifact Validation
AC-IDs tested: CORE-002, AC-CORE-002

Validates that markdown file creation is restricted to approved locations.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from cortex.brain.core.governance_registry import GovernanceRegistry


class TestCore002ArtifactValidation:
    """Tests for CORE-002 - No Markdown Files in Root"""
    
    @pytest.fixture
    def registry(self) -> GovernanceRegistry:
        """Create test registry instance."""
        GovernanceRegistry.reset_instance()
        registry = GovernanceRegistry.instance()
        init_result = registry.initialize()
        assert init_result.is_ok(), f"Registry initialization failed: {init_result.error}"
        return registry
    
    # ========================================================================
    # APPROVED LOCATIONS - SHOULD PASS
    # ========================================================================
    
    def test_markdown_in_docs_approved(self, registry: GovernanceRegistry) -> None:
        """Test AC-CORE-002: Markdown in docs/ is approved"""
        result = registry.validate_artifact_creation("docs/my-feature.md")
        assert result.is_ok(), f"docs/ markdown should be approved: {result.error}"
        assert result.unwrap() is True
    
    def test_markdown_in_workspaces_docs_approved(self, registry: GovernanceRegistry) -> None:
        """Test AC-CORE-002: Markdown in _workspaces/docs/ is approved"""
        result = registry.validate_artifact_creation("_workspaces/docs/README.md")
        assert result.is_ok(), f"_workspaces/docs/ markdown should be approved: {result.error}"
        assert result.unwrap() is True
    
    def test_readme_md_blocked(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: README.md in root is blocked (non-functional, documentation-only)"""
        result = registry.validate_artifact_creation("README.md")
        assert result.is_err(), "README.md in root should be blocked (non-functional)"
        assert "CORE-002" in result.error
    
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
    # BLOCKED LOCATIONS - SHOULD FAIL
    # ========================================================================
    
    def test_deployment_status_md_blocked(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: DEPLOYMENT-STATUS-*.md in root is blocked"""
        result = registry.validate_artifact_creation("DEPLOYMENT-STATUS-2026-01-23.md")
        assert result.is_err(), "DEPLOYMENT-STATUS in root should be blocked"
        assert "CORE-002" in result.error
    
    def test_deployment_commands_md_blocked(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: DEPLOYMENT-QUICK-COMMANDS.md in root is blocked"""
        result = registry.validate_artifact_creation("DEPLOYMENT-QUICK-COMMANDS.md")
        assert result.is_err(), "DEPLOYMENT-QUICK-COMMANDS in root should be blocked"
        assert "CORE-002" in result.error
    
    def test_orchestrator_summary_blocked(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: ORCHESTRATOR-*-SUMMARY.md in root is blocked"""
        result = registry.validate_artifact_creation("ORCHESTRATOR-BOOTSTRAP-SUMMARY.md")
        assert result.is_err(), "ORCHESTRATOR summary in root should be blocked"
        assert "CORE-002" in result.error
    
    def test_review_summary_md_blocked(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: CORTEX-REVIEW-*.md in root is blocked"""
        result = registry.validate_artifact_creation("CORTEX-REVIEW-v4.1-FILE-INDEX.md")
        assert result.is_err(), "CORTEX-REVIEW in root should be blocked"
        assert "CORE-002" in result.error
    
    def test_generic_summary_md_blocked(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: *-summary.md in root is blocked"""
        result = registry.validate_artifact_creation("project-summary.md")
        assert result.is_err(), "*-summary.md in root should be blocked"
        assert "CORE-002" in result.error
    
    def test_generic_report_md_blocked(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: *-report.md in root is blocked"""
        result = registry.validate_artifact_creation("execution-report.md")
        assert result.is_err(), "*-report.md in root should be blocked"
        assert "CORE-002" in result.error
    
    def test_completion_md_blocked(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: completion-*.md in root is blocked"""
        result = registry.validate_artifact_creation("completion-phase-1.md")
        assert result.is_err(), "completion-*.md in root should be blocked"
        assert "CORE-002" in result.error
    
    # ========================================================================
    # EDGE CASES
    # ========================================================================
    
    def test_deeply_nested_docs_approved(self, registry: GovernanceRegistry) -> None:
        """Test AC-CORE-002: Deeply nested docs/ paths are approved"""
        result = registry.validate_artifact_creation("docs/guides/deep/nested/feature.md")
        assert result.is_ok(), f"docs/ nested markdown should be approved: {result.error}"
    
    def test_markdown_in_subdir_blocked(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: Markdown in arbitrary subdirs (not docs/) is blocked"""
        result = registry.validate_artifact_creation("scripts/deployment-info.md")
        assert result.is_err(), "Markdown in scripts/ should be blocked"
        assert "CORE-002" in result.error
    
    def test_readme_in_root_blocked(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: README.md in root is blocked (non-functional)"""
        result = registry.validate_artifact_creation("scripts/README.md")
        assert result.is_err(), "README.md in subdir should be blocked"
        assert "CORE-002" in result.error
    
    def test_with_ac_id_tracking(self, registry: GovernanceRegistry) -> None:
        """Test CORE-002: AC-ID is included in violation message"""
        result = registry.validate_artifact_creation(
            "DEPLOYMENT-TEST.md",
            ac_id="AC-TEST-001"
        )
        assert result.is_err(), "Should be blocked"
        assert "AC-TEST-001" in result.error, "AC-ID should be in error message"


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
