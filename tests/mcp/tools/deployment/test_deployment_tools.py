"""Tests for MCP Deployment Tools - PHASE-DEPLOYMENT-003-mcp-expansion.

AC-DEP-003-04: Deployment tools expose sanitization and health checks.
Tests 5 deployment tools callable via MCP.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestSanitizerRunsPhaseDep001:
    """Test sanitizer runs PHASE-DEPLOYMENT-001 sanitization."""

    def test_runs_governance_db_sanitization(self):
        """Should run governance.db sanitization."""
        from cortex.mcp.tools.deployment.sanitizer import Sanitizer
        
        sanitizer = Sanitizer()
        
        with patch.object(sanitizer, "_run_sanitization") as mock_run:
            mock_run.return_value = {"removed_entries": 5, "preserved_entries": 10}
            
            result = sanitizer.sanitize()
        
        assert "removed_entries" in result
        assert "preserved_entries" in result

    def test_validates_sanitization_complete(self):
        """Should validate sanitization is complete."""
        from cortex.mcp.tools.deployment.sanitizer import Sanitizer
        
        sanitizer = Sanitizer()
        
        with patch.object(sanitizer, "_validate_sanitization") as mock_validate:
            mock_validate.return_value = {"valid": True, "issues": []}
            
            result = sanitizer.validate()
        
        assert result["valid"] is True

    def test_returns_sanitization_report(self):
        """Should return detailed sanitization report."""
        from cortex.mcp.tools.deployment.sanitizer import Sanitizer
        
        sanitizer = Sanitizer()
        
        with patch.object(sanitizer, "_run_sanitization") as mock_run:
            mock_run.return_value = {
                "removed_entries": 5,
                "preserved_entries": 10,
                "patterns_matched": ["TEST%", "DEV%"],
            }
            
            result = sanitizer.sanitize()
        
        assert "patterns_matched" in result


class TestReleaseBuilderCreatesTag:
    """Test release builder creates release tags."""

    def test_creates_release_tag(self):
        """Should create release tag."""
        from cortex.mcp.tools.deployment.release_builder import ReleaseBuilder
        
        builder = ReleaseBuilder()
        
        with patch.object(builder, "_create_tag") as mock_tag:
            mock_tag.return_value = {"tag": "v1.0.0", "sha": "abc123"}
            
            result = builder.create_release(version="1.0.0")
        
        assert result["tag"] == "v1.0.0"

    def test_validates_version_format(self):
        """Should validate semantic version format."""
        from cortex.mcp.tools.deployment.release_builder import ReleaseBuilder
        
        builder = ReleaseBuilder()
        
        assert builder.validate_version("1.0.0") is True
        assert builder.validate_version("invalid") is False

    def test_triggers_ci_cd_pipeline(self):
        """Should trigger CI/CD pipeline after tag."""
        from cortex.mcp.tools.deployment.release_builder import ReleaseBuilder
        
        builder = ReleaseBuilder()
        
        with patch.object(builder, "_create_tag") as mock_tag:
            mock_tag.return_value = {"tag": "v1.0.0", "sha": "abc123"}
            
            with patch.object(builder, "_trigger_cicd") as mock_cicd:
                mock_cicd.return_value = {"pipeline_id": "12345", "status": "started"}
                
                result = builder.create_release(version="1.0.0", trigger_cicd=True)
        
        assert "pipeline_id" in result


class TestHealthCheckerValidatesReadiness:
    """Test health checker validates CORTEX readiness."""

    def test_checks_all_tests_pass(self):
        """Should check all tests pass."""
        from cortex.mcp.tools.deployment.health_checker import HealthChecker
        
        checker = HealthChecker()
        
        with patch.object(checker, "_run_tests") as mock_tests:
            mock_tests.return_value = {"total": 100, "passed": 100, "failed": 0}
            
            result = checker.check_readiness()
        
        assert result["tests_passed"] is True

    def test_checks_sanitization_complete(self):
        """Should check sanitization is complete."""
        from cortex.mcp.tools.deployment.health_checker import HealthChecker
        
        checker = HealthChecker()
        
        with patch.object(checker, "_check_sanitization") as mock_sanitize:
            mock_sanitize.return_value = {"clean": True}
            
            result = checker.check_readiness()
        
        assert result["sanitization_clean"] is True

    def test_returns_readiness_report(self):
        """Should return comprehensive readiness report."""
        from cortex.mcp.tools.deployment.health_checker import HealthChecker
        
        checker = HealthChecker()
        
        with patch.object(checker, "_run_all_checks") as mock_checks:
            mock_checks.return_value = {
                "tests_passed": True,
                "sanitization_clean": True,
                "linting_passed": True,
                "type_checks_passed": True,
                "ready_for_release": True,
            }
            
            result = checker.check_readiness()
        
        assert "ready_for_release" in result

    def test_identifies_blocking_issues(self):
        """Should identify blocking issues."""
        from cortex.mcp.tools.deployment.health_checker import HealthChecker
        
        checker = HealthChecker()
        
        with patch.object(checker, "_run_all_checks") as mock_checks:
            mock_checks.return_value = {
                "tests_passed": False,
                "ready_for_release": False,
                "blocking_issues": ["5 tests failing"],
            }
            
            result = checker.check_readiness()
        
        assert result["ready_for_release"] is False
        assert len(result["blocking_issues"]) >= 1


class TestRollbackRevertsRelease:
    """Test rollback reverts to previous release."""

    def test_reverts_to_previous_version(self):
        """Should revert to previous version."""
        from cortex.mcp.tools.deployment.rollback import Rollback
        
        rollback = Rollback()
        
        with patch.object(rollback, "_get_previous_version") as mock_prev:
            mock_prev.return_value = "0.9.0"
            
            with patch.object(rollback, "_execute_rollback") as mock_exec:
                mock_exec.return_value = {"success": True, "version": "0.9.0"}
                
                result = rollback.rollback()
        
        assert result["success"] is True
        assert result["version"] == "0.9.0"

    def test_rollback_to_specific_version(self):
        """Should rollback to specific version."""
        from cortex.mcp.tools.deployment.rollback import Rollback
        
        rollback = Rollback()
        
        with patch.object(rollback, "_execute_rollback") as mock_exec:
            mock_exec.return_value = {"success": True, "version": "0.8.0"}
            
            result = rollback.rollback(target_version="0.8.0")
        
        assert result["version"] == "0.8.0"

    def test_validates_rollback_target(self):
        """Should validate rollback target exists."""
        from cortex.mcp.tools.deployment.rollback import Rollback
        
        rollback = Rollback()
        
        with patch.object(rollback, "_version_exists") as mock_exists:
            mock_exists.return_value = False
            
            result = rollback.rollback(target_version="0.0.1")
        
        assert result["success"] is False
        assert "not found" in result.get("error", "").lower()


class TestCanaryDeployerStagedRollout:
    """Test canary deployer staged rollout."""

    def test_deploys_10_percent_first(self):
        """Should deploy to 10% first."""
        from cortex.mcp.tools.deployment.canary_deployer import CanaryDeployer
        
        deployer = CanaryDeployer()
        
        with patch.object(deployer, "_deploy_canary") as mock_deploy:
            mock_deploy.return_value = {"percentage": 10, "status": "deployed"}
            
            result = deployer.start_canary(version="1.0.0")
        
        assert result["percentage"] == 10

    def test_promotes_to_50_percent(self):
        """Should promote to 50% after validation."""
        from cortex.mcp.tools.deployment.canary_deployer import CanaryDeployer
        
        deployer = CanaryDeployer()
        
        with patch.object(deployer, "_promote_canary") as mock_promote:
            mock_promote.return_value = {"percentage": 50, "status": "promoted"}
            
            result = deployer.promote(target_percentage=50)
        
        assert result["percentage"] == 50

    def test_promotes_to_100_percent(self):
        """Should promote to 100% for full rollout."""
        from cortex.mcp.tools.deployment.canary_deployer import CanaryDeployer
        
        deployer = CanaryDeployer()
        
        with patch.object(deployer, "_promote_canary") as mock_promote:
            mock_promote.return_value = {"percentage": 100, "status": "complete"}
            
            result = deployer.promote(target_percentage=100)
        
        assert result["percentage"] == 100
        assert result["status"] == "complete"

    def test_aborts_on_failure(self):
        """Should abort deployment on failure detection."""
        from cortex.mcp.tools.deployment.canary_deployer import CanaryDeployer
        
        deployer = CanaryDeployer()
        
        with patch.object(deployer, "_abort_canary") as mock_abort:
            mock_abort.return_value = {"status": "aborted", "reason": "Error rate too high"}
            
            result = deployer.abort(reason="Error rate too high")
        
        assert result["status"] == "aborted"

    def test_returns_metrics_during_canary(self):
        """Should return metrics during canary deployment."""
        from cortex.mcp.tools.deployment.canary_deployer import CanaryDeployer
        
        deployer = CanaryDeployer()
        
        with patch.object(deployer, "_get_canary_metrics") as mock_metrics:
            mock_metrics.return_value = {
                "error_rate": 0.01,
                "latency_p95": 150,
                "success_rate": 0.99,
            }
            
            result = deployer.get_metrics()
        
        assert "error_rate" in result
        assert "latency_p95" in result
