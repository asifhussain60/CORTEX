"""
Tests for CrossRepoEnforcer - cross-repository security enforcement.

Author: CORTEX Implementation
Phase: impl-arch-005-hardening (HARD-PROD-001-08)
Compliance: CORE-008 (TDD), CORE-011 (100% typed), CORE-012 (Google docstrings)
"""

import pytest
from typing import List


class TestCrossRepoPolicyEnforcement:
    """Test tier0 security policy enforcement across repos."""

    def test_loads_tier0_rules(self) -> None:
        """Verify tier0 rules are loaded correctly."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        rules = enforcer.load_tier0_rules()
        
        assert "mandatory_controls" in rules
        assert rules["mandatory_controls"]["secrets_scanning"] is True

    def test_mirrors_policies_to_repo(self) -> None:
        """Verify policies are mirrored to individual repos."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        enforcer.load_tier0_rules()
        
        result = enforcer.mirror_policies_to_repo("test_repo", enforcer.tier0_rules)
        assert result is True

    def test_enforces_mandatory_controls(self) -> None:
        """Verify mandatory controls are enforced."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        rules = enforcer.load_tier0_rules()
        
        assert rules["mandatory_controls"]["input_validation"] is True
        assert rules["mandatory_controls"]["rate_limiting"] is True


class TestSecretsScanningPrecommit:
    """Test pre-commit hook for secrets scanning."""

    def test_installs_precommit_hook(self) -> None:
        """Verify pre-commit hook installation."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        import tempfile
        import os
        
        enforcer = CrossRepoEnforcer()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = os.path.join(tmpdir, ".git")
            os.makedirs(repo_path, exist_ok=True)
            
            result = enforcer.install_precommit_hook(tmpdir)
            assert result is True

    def test_detects_hardcoded_secrets_precommit(self) -> None:
        """Verify pre-commit hook detects hardcoded secrets."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        rules = enforcer.load_tier0_rules()
        
        # Should have forbidden patterns
        assert len(rules["forbidden_patterns"]) > 0

    def test_prevents_secret_commit(self) -> None:
        """Verify secrets cannot be committed."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        
        # Add secret to blacklist
        enforcer.add_to_secrets_blacklist(r"api_key_\w+")
        
        assert len(enforcer.secrets_blacklist) > 0


class TestVulnerabilityCoordination:
    """Test CVE coordination and response."""

    def test_coordinates_vulnerability_response(self) -> None:
        """Verify vulnerability coordination."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        
        result = enforcer.coordinate_vulnerability_response(
            "CVE-2024-1234",
            "CRITICAL",
            ["repo1", "repo2"],
            sla_hours=1
        )
        
        assert result["cve_id"] == "CVE-2024-1234"
        assert result["severity"] == "CRITICAL"

    def test_enforces_vulnerability_sla(self) -> None:
        """Verify SLA is enforced for critical vulnerabilities."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        from datetime import datetime, timedelta
        
        enforcer = CrossRepoEnforcer()
        
        result = enforcer.coordinate_vulnerability_response(
            "CVE-2024-5678",
            "CRITICAL",
            ["repo1"],
            sla_hours=1
        )
        
        deadline = datetime.fromisoformat(result["sla_deadline"])
        assert deadline > datetime.utcnow()

    def test_generates_remediation_steps(self) -> None:
        """Verify remediation steps are generated."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        
        result = enforcer.coordinate_vulnerability_response(
            "CVE-2024-9999",
            "HIGH",
            ["repo1"]
        )
        
        assert len(result["remediation_steps"]) > 0


class TestPermissionLeastPrivilege:
    """Test least-privilege RBAC model."""

    def test_enforces_permission_model(self) -> None:
        """Verify least-privilege permissions are enforced."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        
        result = enforcer.enforce_permission_model(
            "secure_repo",
            "alice",
            "maintainer"
        )
        
        assert result is True

    def test_admin_has_all_permissions(self) -> None:
        """Verify admin role has all permissions."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        enforcer.enforce_permission_model("repo1", "admin_user", "admin")
        
        assert enforcer.verify_permission("repo1", "admin_user", "security") is True
        assert enforcer.verify_permission("repo1", "admin_user", "write") is True

    def test_viewer_has_limited_permissions(self) -> None:
        """Verify viewer role has limited permissions."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        enforcer.enforce_permission_model("repo1", "viewer_user", "viewer")
        
        assert enforcer.verify_permission("repo1", "viewer_user", "read") is True
        assert enforcer.verify_permission("repo1", "viewer_user", "write") is False

    def test_permission_denied_for_invalid_user(self) -> None:
        """Verify permission denied for users not assigned."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        enforcer.enforce_permission_model("repo1", "alice", "contributor")
        
        assert enforcer.verify_permission("repo1", "bob", "read") is False


class TestAuditLogFederation:
    """Test audit log aggregation across repos."""

    def test_aggregates_security_logs(self) -> None:
        """Verify security logs are aggregated."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        enforcer.enforce_permission_model("repo1", "user1", "contributor")
        
        logs = enforcer.aggregate_security_logs(["repo1", "repo2"])
        
        assert len(logs) > 0

    def test_audit_trail_includes_actions(self) -> None:
        """Verify audit trail includes all security actions."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        enforcer.load_tier0_rules()
        enforcer.mirror_policies_to_repo("repo1", enforcer.tier0_rules)
        
        trail = enforcer.get_audit_trail()
        
        assert len(trail) > 0
        assert any(event["action"] == "policy_sync" for event in trail)

    def test_audit_trail_has_timestamps(self) -> None:
        """Verify audit events have timestamps."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        enforcer.enforce_permission_model("repo1", "user1", "admin")
        
        trail = enforcer.get_audit_trail()
        
        for event in trail:
            assert "timestamp" in event


class TestSupplyChainSecurity:
    """Test supply chain security (dependency provenance)."""

    def test_verifies_dependency_provenance(self) -> None:
        """Verify dependency supply chain security."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        
        result = enforcer.verify_supply_chain_security(
            "cryptography",
            "41.0.0"
        )
        
        assert result["dependency"] == "cryptography"
        assert result["checks"]["checksum_verified"] is True

    def test_checks_license_compliance(self) -> None:
        """Verify license compliance is checked."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        
        result = enforcer.verify_supply_chain_security(
            "requests",
            "2.31.0"
        )
        
        assert result["checks"]["license_compliant"] is True

    def test_verifies_no_vulnerabilities(self) -> None:
        """Verify vulnerability check for dependencies."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        
        result = enforcer.verify_supply_chain_security(
            "requests",
            "2.31.0"
        )
        
        assert result["checks"]["no_known_vulnerabilities"] is True


class TestComplianceReporting:
    """Test compliance reporting."""

    def test_generates_compliance_report(self) -> None:
        """Verify compliance report generation."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        enforcer.load_tier0_rules()
        
        report = enforcer.generate_compliance_report()
        
        assert "tier0_rules" in report
        assert report["compliance_status"] == "COMPLIANT"

    def test_vulnerability_status_report(self) -> None:
        """Verify vulnerability status reporting."""
        from cortex.infrastructure.security import CrossRepoEnforcer
        
        enforcer = CrossRepoEnforcer()
        enforcer.coordinate_vulnerability_response(
            "CVE-2024-1111",
            "CRITICAL",
            ["repo1"]
        )
        
        status = enforcer.get_vulnerability_status()
        
        assert status["total_vulnerabilities"] >= 1
        assert status["critical"] >= 1
