"""
Tests for DeploymentOrchestrator - Production Deployment Workflow (Phase 73).

TDD RED Phase - Test suite for production deployment orchestration:
1. Two-branch git strategy (CORTEX + main)
2. Vacuum cleanup verification
3. Production readiness gates
4. Version management
5. Deployment reporting

AC-ID: AC-DEPLOY-ORCH-001
"""

import pytest
from pytest import fixture
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from dataclasses import dataclass, asdict
from datetime import datetime
import yaml
import json


@dataclass
class MockValidationResult:
    """Mock validation result."""
    passed: bool
    checks_count: int = 5
    failures: list = None
    readiness_score: int = 100
    
    def __post_init__(self):
        if self.failures is None:
            self.failures = []


@dataclass
class MockCleanupResult:
    """Mock cleanup result."""
    success: bool
    files_archived: int = 47
    root_consolidated: int = 8
    orchestrators_verified: int = 28
    mcp_tools_verified: int = 50


@dataclass
class MockGitResult:
    """Mock git operation result."""
    success: bool
    commits_pushed: int = 0
    files_modified: int = 0
    message: str = ""


@dataclass
class MockVersionResult:
    """Mock version result."""
    success: bool
    version_old: str = "8.3.0"
    version_new: str = "8.4.0"


@fixture
def mock_workspace(tmp_path):
    """Create mock workspace structure."""
    workspace_root = tmp_path / "CORTEX"
    workspace_root.mkdir()
    
    # Create necessary directories
    (workspace_root / "cortex").mkdir()
    (workspace_root / "cortex_brain").mkdir()
    (workspace_root / "tests").mkdir()
    (workspace_root / "deployment").mkdir()
    (workspace_root / ".github" / "prompts").mkdir(parents=True)
    (workspace_root / ".github" / "workflows").mkdir(parents=True)
    (workspace_root / "docs").mkdir()
    (workspace_root / "_workspaces").mkdir()
    (workspace_root / "cortex-registry" / "_cortex-master").mkdir(parents=True)
    
    # Create key files
    (workspace_root / "README.md").write_text("# CORTEX\n")
    (workspace_root / "requirements.txt").write_text("pytest==7.0.0\n")
    (workspace_root / "Makefile").write_text("test:\n\tpytest\n")
    (workspace_root / "pytest.ini").write_text("[pytest]\n")
    
    return workspace_root


@fixture
def mock_vacuum_orchestrator():
    """Create mock VacuumOrchestrator."""
    mock = MagicMock()
    mock.verify_production_structure.return_value = MockCleanupResult(success=True)
    mock.execute_full_cleanup.return_value = MockCleanupResult(success=True)
    mock.verify_orchestrator_wiring.return_value = MockCleanupResult(success=True)
    mock.verify_mcp_tools_registered.return_value = MockCleanupResult(success=True)
    mock.consolidate_root_folders.return_value = MockCleanupResult(success=True)
    mock.archive_session_markers.return_value = MockCleanupResult(success=True)
    return mock


@fixture
def mock_readiness_assessment():
    """Create mock ProductionReadinessAssessment."""
    mock = MagicMock()
    mock.full_check.return_value = MockValidationResult(passed=True, checks_count=100)
    return mock


@fixture
def mock_release_manager():
    """Create mock ProductionReleaseManager."""
    mock = MagicMock()
    mock.get_current_version.return_value = "8.3.0"
    mock.bump_version.return_value = "8.4.0"
    mock.regenerate_cortex_prompt.return_value = {"success": True}
    mock.regenerate_copilot_instructions.return_value = {"success": True}
    mock.generate_changelog.return_value = "## v8.4.0\n\n- Feature 1\n- Feature 2"
    return mock


class TestDeploymentOrchestrator:
    """Test DeploymentOrchestrator basic functionality."""
    
    def test_deployment_orchestrator_initialization(self, mock_workspace):
        """Should initialize with workspace root."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        assert orchestrator is not None
        assert orchestrator.workspace_root == mock_workspace
    
    def test_deployment_config_creation(self):
        """Should create valid deployment config."""
        from cortex.orchestrators.core.deployment_orchestrator import (
            DeploymentOrchestrator,
            DeploymentConfig
        )
        
        config = DeploymentConfig(
            deployment_type="full",
            version_bump_type="patch"
        )
        
        assert config.deployment_type == "full"
        assert config.version_bump_type == "patch"
        assert config.target_branch_cortex == "CORTEX"
        assert config.target_branch_main == "main"


class TestPreFlightValidation:
    """Test pre-flight validation stage."""
    
    def test_pre_flight_validation_returns_result(self, mock_workspace):
        """Should return ValidationResult from pre_flight_validation."""
        from cortex.orchestrators.core.deployment_orchestrator import (
            DeploymentOrchestrator,
            ValidationResult
        )
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        with patch.object(orchestrator, 'run_all_tests', return_value={"passed": 65, "failed": 0}):
            with patch.object(orchestrator, 'verify_git_clean', return_value=True):
                with patch.object(orchestrator, 'verify_git_24h_history', return_value={"commits": 5}):
                    result = orchestrator.pre_flight_validation()
        
        assert result is not None
        assert isinstance(result, ValidationResult)
    
    def test_challenge_gate_generation(self, mock_workspace):
        """Should generate challenge gate with alternatives."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        challenges = orchestrator.generate_challenge_gate()
        
        assert isinstance(challenges, list)
        assert len(challenges) > 0
        assert any("deployment" in c.lower() for c in challenges)


class TestVacuumCleanup:
    """Test vacuum cleanup stage."""
    
    def test_cleanup_execution(self, mock_workspace, mock_vacuum_orchestrator):
        """Should execute cleanup successfully."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        orchestrator.vacuum = mock_vacuum_orchestrator
        
        result = orchestrator.cleanup_and_consolidate()
        
        assert result is not None
        assert result["vacuum"]["success"] is True
    
    def test_cleanup_verifies_wiring(self, mock_workspace, mock_vacuum_orchestrator):
        """Should verify orchestrator wiring."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        orchestrator.vacuum = mock_vacuum_orchestrator
        
        result = orchestrator.cleanup_and_consolidate()
        
        assert result["wiring_check"]["success"] is True
    
    def test_cleanup_verifies_mcp_tools(self, mock_workspace, mock_vacuum_orchestrator):
        """Should verify MCP tools registered."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        orchestrator.vacuum = mock_vacuum_orchestrator
        
        result = orchestrator.cleanup_and_consolidate()
        
        assert result["mcp_check"]["success"] is True


class TestBranchPushStrategy:
    """Test two-branch push strategy."""
    
    def test_push_to_cortex_branch(self, mock_workspace):
        """Should push all files to CORTEX branch."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        with patch.object(orchestrator, '_git_push_branch') as mock_push:
            mock_push.return_value = MockGitResult(success=True, commits_pushed=3)
            result = orchestrator.push_to_cortex_branch()
        
        assert result.success is True
        mock_push.assert_called()
    
    def test_push_to_main_filtered(self, mock_workspace):
        """Should push filtered files to main branch."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        with patch.object(orchestrator, '_git_push_branch_filtered') as mock_push:
            mock_push.return_value = MockGitResult(success=True, commits_pushed=1)
            result = orchestrator.push_to_main_branch(filter_excluded=True)
        
        assert result.success is True
        mock_push.assert_called()
    
    def test_excluded_files_not_in_main(self, mock_workspace):
        """Should exclude development files from main branch."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        excluded = orchestrator.get_excluded_files()
        
        # Verify key exclusions
        assert any("docs/" in item or "docs**" in item for item in excluded)
        assert any("_workspaces" in item for item in excluded)
        assert any("agents" in item for item in excluded)
        assert any(".github/prompts/cortex-architect" in item for item in excluded)


class TestVersionManagement:
    """Test version management stage."""
    
    def test_version_bump_patch(self, mock_workspace, mock_release_manager):
        """Should bump patch version."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        orchestrator.release_manager = mock_release_manager
        
        result = orchestrator.create_release_version()
        
        assert result.success is True
        assert result.version_new == "8.4.0"
    
    def test_version_regenerates_prompts(self, mock_workspace, mock_release_manager):
        """Should regenerate prompt files on version bump."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        orchestrator.release_manager = mock_release_manager
        
        result = orchestrator.create_release_version()
        
        mock_release_manager.regenerate_cortex_prompt.assert_called()
        mock_release_manager.regenerate_copilot_instructions.assert_called()
    
    def test_version_creates_git_tag(self, mock_workspace, mock_release_manager):
        """Should create git tag for release."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        orchestrator.release_manager = mock_release_manager
        
        with patch.object(orchestrator, '_git_tag') as mock_tag:
            mock_tag.return_value = True
            result = orchestrator.create_release_version()
        
        mock_tag.assert_called()


class TestDeploymentReport:
    """Test deployment report generation."""
    
    def test_generate_deployment_report(self, mock_workspace):
        """Should generate comprehensive deployment report."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        report = orchestrator.generate_deployment_report(
            pre_flight=MockValidationResult(passed=True),
            cleanup=MockCleanupResult(success=True),
            cortex_branch=MockGitResult(success=True),
            main_branch=MockGitResult(success=True),
            version=MockVersionResult(success=True)
        )
        
        assert report is not None
        assert "pre_flight_validation" in report
        assert "cleanup_consolidation" in report
        assert "branch_strategy" in report
        assert "version_release" in report
    
    def test_deployment_report_includes_metrics(self, mock_workspace):
        """Should include deployment metrics."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        report = orchestrator.generate_deployment_report(
            pre_flight=MockValidationResult(passed=True, checks_count=100),
            cleanup=MockCleanupResult(success=True, files_archived=47),
            cortex_branch=MockGitResult(success=True, commits_pushed=3),
            main_branch=MockGitResult(success=True, commits_pushed=1),
            version=MockVersionResult(success=True, version_new="8.4.0")
        )
        
        assert "metrics" in report
        assert report["metrics"]["files_archived"] == 47
        assert report["metrics"]["commits_pushed"] == 4


class TestDeploymentWorkflow:
    """Test complete deployment workflow."""
    
    @patch('cortex.orchestrators.core.deployment_orchestrator.ProductionReleaseManager')
    def test_full_deployment_workflow(self, mock_release_class, mock_workspace):
        """Should execute complete deployment workflow."""
        from cortex.orchestrators.core.deployment_orchestrator import (
            DeploymentOrchestrator,
            DeploymentConfig
        )
        
        config = DeploymentConfig(
            deployment_type="full",
            version_bump_type="patch"
        )
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        # Mock all components
        orchestrator.readiness_assessment = MagicMock()
        orchestrator.readiness_assessment.full_check.return_value = MockValidationResult(passed=True)
        
        orchestrator.vacuum = MagicMock()
        orchestrator.vacuum.execute_full_cleanup.return_value = MockCleanupResult(success=True)
        
        orchestrator.release_manager = MagicMock()
        orchestrator.release_manager.get_current_version.return_value = "8.3.0"
        orchestrator.release_manager.bump_version.return_value = "8.4.0"
        
        with patch.object(orchestrator, 'pre_flight_validation', return_value=MockValidationResult(passed=True)):
            with patch.object(orchestrator, 'run_all_tests', return_value={"passed": 65}):
                with patch.object(orchestrator, 'verify_git_clean', return_value=True):
                    with patch.object(orchestrator, 'cleanup_and_consolidate', return_value={"success": True}):
                        with patch.object(orchestrator, 'push_to_cortex_branch', return_value=MockGitResult(success=True)):
                            with patch.object(orchestrator, 'push_to_main_branch', return_value=MockGitResult(success=True)):
                                result = orchestrator.deploy_to_production(config)
        
        assert result is not None
    
    def test_deployment_stops_on_validation_failure(self, mock_workspace):
        """Should stop deployment if validation fails."""
        from cortex.orchestrators.core.deployment_orchestrator import (
            DeploymentOrchestrator,
            DeploymentConfig
        )
        
        config = DeploymentConfig(deployment_type="full")
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        with patch.object(orchestrator, 'pre_flight_validation', return_value=MockValidationResult(passed=False)):
            result = orchestrator.deploy_to_production(config)
        
        assert result.success is False


class TestAuditTrail:
    """Test audit trail integration."""
    
    def test_deployment_logs_ac_markers(self, mock_workspace):
        """Should log AC_START and AC_COMPLETE markers."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        with patch.object(orchestrator, '_log_ac_start') as mock_start:
            with patch.object(orchestrator, '_log_ac_complete') as mock_complete:
                with patch.object(orchestrator, 'pre_flight_validation', return_value=MockValidationResult(passed=True)):
                    with patch.object(orchestrator, 'run_all_tests', return_value={"passed": 65}):
                        with patch.object(orchestrator, 'verify_git_clean', return_value=True):
                            with patch.object(orchestrator, 'cleanup_and_consolidate', return_value={"success": True}):
                                with patch.object(orchestrator, 'push_to_cortex_branch', return_value=MockGitResult(success=True)):
                                    with patch.object(orchestrator, 'push_to_main_branch', return_value=MockGitResult(success=True)):
                                        orchestrator.deploy_to_production()
        
        mock_start.assert_called()
        mock_complete.assert_called()


class TestErrorHandling:
    """Test error handling and recovery."""
    
    def test_deployment_reports_cleanup_failure(self, mock_workspace):
        """Should report cleanup failures."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        orchestrator.vacuum = MagicMock()
        orchestrator.vacuum.execute_full_cleanup.return_value = MockCleanupResult(
            success=False
        )
        
        result = orchestrator.cleanup_and_consolidate()
        
        assert result is not None
    
    def test_deployment_handles_git_push_failure(self, mock_workspace):
        """Should handle git push failures gracefully."""
        from cortex.orchestrators.core.deployment_orchestrator import DeploymentOrchestrator
        
        orchestrator = DeploymentOrchestrator(workspace_root=mock_workspace)
        
        with patch.object(orchestrator, '_git_push_branch') as mock_push:
            mock_push.return_value = MockGitResult(success=False, message="Network error")
            result = orchestrator.push_to_cortex_branch()
        
        assert result.success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
