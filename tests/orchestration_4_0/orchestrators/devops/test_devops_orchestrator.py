"""
Tests for DevOps Orchestrator

Tests CI/CD pipeline management capabilities across platforms.

Author: Asif Hussain
Version: 1.0
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from datetime import datetime

from src.orchestration_4_0.orchestrators.devops import (
    DevOpsOrchestrator,
    PipelineConfig,
    PipelineRun,
    PipelineStatus,
    BuildLog,
    PlatformType
)


# ========================================
# Platform Client Tests
# ========================================

class TestAzureDevOpsClient:
    """Tests for Azure DevOps client"""
    
    def test_client_initialization_success(self):
        """Test successful client initialization"""
        config = {
            "organization": "test-org",
            "project": "test-project",
            "personal_access_token": "test-token"
        }
        
        from src.orchestration_4_0.orchestrators.devops.azure_devops_client import AzureDevOpsClient
        
        client = AzureDevOpsClient(config)
        
        assert client.config == config
        assert client.base_url == "https://dev.azure.com/test-org"
        assert client.session is not None
    
    def test_client_initialization_missing_config(self):
        """Test client initialization with missing config"""
        from src.orchestration_4_0.orchestrators.devops.azure_devops_client import AzureDevOpsClient
        
        config = {"organization": "test-org"}  # Missing project and token
        
        with pytest.raises(ValueError, match="Missing required config"):
            AzureDevOpsClient(config)


class TestGitHubActionsClient:
    """Tests for GitHub Actions client"""
    
    def test_client_initialization_success(self):
        """Test successful client initialization"""
        config = {
            "owner": "test-owner",
            "repository": "test-repo",
            "token": "test-token"
        }
        
        from src.orchestration_4_0.orchestrators.devops.github_actions_client import GitHubActionsClient
        
        client = GitHubActionsClient(config)
        
        assert client.config == config
        assert client.base_url == "https://api.github.com"
        assert client.session is not None
    
    def test_client_initialization_missing_config(self):
        """Test client initialization with missing config"""
        from src.orchestration_4_0.orchestrators.devops.github_actions_client import GitHubActionsClient
        
        config = {"owner": "test-owner"}  # Missing repository and token
        
        with pytest.raises(ValueError, match="Missing required config"):
            GitHubActionsClient(config)


# ========================================
# DevOps Orchestrator Tests
# ========================================

class TestDevOpsOrchestratorInitialization:
    """Tests for orchestrator initialization"""
    
    def test_orchestrator_initialization_no_platforms(self):
        """Test orchestrator initialization without platform config"""
        orchestrator = DevOpsOrchestrator(config={})
        
        assert orchestrator.name == "devops"
        assert len(orchestrator.clients) == 0
    
    def test_orchestrator_initialization_with_platforms(self):
        """Test orchestrator initialization with platform config"""
        config = {
            "platforms": {
                "azure_devops": {
                    "organization": "test-org",
                    "project": "test-project",
                    "personal_access_token": "test-token"
                },
                "github_actions": {
                    "owner": "test-owner",
                    "repository": "test-repo",
                    "token": "test-token"
                }
            }
        }
        
        orchestrator = DevOpsOrchestrator(config=config)
        
        assert PlatformType.AZURE_DEVOPS in orchestrator.clients
        assert PlatformType.GITHUB_ACTIONS in orchestrator.clients


class TestTriggerPipeline:
    """Tests for triggering pipelines"""
    
    @pytest.mark.asyncio
    async def test_trigger_pipeline_azure_devops(self):
        """Test triggering Azure DevOps pipeline"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock Azure DevOps client
        mock_client = Mock()
        mock_client.trigger_pipeline = Mock(return_value="12345")
        orchestrator.clients[PlatformType.AZURE_DEVOPS] = mock_client
        
        config = PipelineConfig(
            name="CI-Build",
            repository="my-repo",
            branch="main",
            platform=PlatformType.AZURE_DEVOPS,
            parameters={"BUILD_TYPE": "Release"}
        )
        
        run_id = await orchestrator.trigger_pipeline(config)
        
        assert run_id == "12345"
        mock_client.trigger_pipeline.assert_called_once_with(
            pipeline_name="CI-Build",
            repository="my-repo",
            branch="main",
            parameters={"BUILD_TYPE": "Release"}
        )
    
    @pytest.mark.asyncio
    async def test_trigger_pipeline_github_actions(self):
        """Test triggering GitHub Actions workflow"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock GitHub Actions client
        mock_client = Mock()
        mock_client.trigger_pipeline = Mock(return_value="67890")
        orchestrator.clients[PlatformType.GITHUB_ACTIONS] = mock_client
        
        config = PipelineConfig(
            name="CI-Workflow",
            repository="my-repo",
            branch="develop",
            platform=PlatformType.GITHUB_ACTIONS
        )
        
        run_id = await orchestrator.trigger_pipeline(config)
        
        assert run_id == "67890"
        mock_client.trigger_pipeline.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_trigger_pipeline_platform_not_configured(self):
        """Test triggering pipeline with unconfigured platform"""
        orchestrator = DevOpsOrchestrator(config={})
        
        config = PipelineConfig(
            name="CI-Build",
            repository="my-repo",
            branch="main",
            platform=PlatformType.AZURE_DEVOPS
        )
        
        with pytest.raises(ValueError, match="Platform not configured"):
            await orchestrator.trigger_pipeline(config)


class TestGetPipelineStatus:
    """Tests for getting pipeline status"""
    
    @pytest.mark.asyncio
    async def test_get_pipeline_status_success(self):
        """Test getting pipeline status"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock client
        mock_client = Mock()
        mock_client.get_pipeline_status = Mock(return_value=PipelineStatus.RUNNING)
        orchestrator.clients[PlatformType.AZURE_DEVOPS] = mock_client
        
        status = await orchestrator.get_pipeline_status("12345", PlatformType.AZURE_DEVOPS)
        
        assert status == PipelineStatus.RUNNING
        mock_client.get_pipeline_status.assert_called_once_with("12345")
    
    @pytest.mark.asyncio
    async def test_get_pipeline_status_completed(self):
        """Test getting completed pipeline status"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock client
        mock_client = Mock()
        mock_client.get_pipeline_status = Mock(return_value=PipelineStatus.SUCCESS)
        orchestrator.clients[PlatformType.GITHUB_ACTIONS] = mock_client
        
        status = await orchestrator.get_pipeline_status("67890", PlatformType.GITHUB_ACTIONS)
        
        assert status == PipelineStatus.SUCCESS


class TestGetPipelineRun:
    """Tests for getting pipeline run details"""
    
    @pytest.mark.asyncio
    async def test_get_pipeline_run_success(self):
        """Test getting pipeline run details"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock pipeline run
        mock_run = PipelineRun(
            run_id="12345",
            pipeline_name="CI-Build",
            status=PipelineStatus.SUCCESS,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=120.5,
            platform=PlatformType.AZURE_DEVOPS,
            branch="main",
            commit_sha="abc123"
        )
        
        # Mock client
        mock_client = Mock()
        mock_client.get_pipeline_run = Mock(return_value=mock_run)
        orchestrator.clients[PlatformType.AZURE_DEVOPS] = mock_client
        
        run = await orchestrator.get_pipeline_run("12345", PlatformType.AZURE_DEVOPS)
        
        assert run.run_id == "12345"
        assert run.status == PipelineStatus.SUCCESS
        assert run.duration_seconds == 120.5


class TestGetBuildLogs:
    """Tests for retrieving build logs"""
    
    @pytest.mark.asyncio
    async def test_get_build_logs_success(self):
        """Test retrieving build logs"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock build log
        mock_log = BuildLog(
            run_id="12345",
            platform=PlatformType.AZURE_DEVOPS,
            logs="Build started\nBuild succeeded",
            errors=[],
            warnings=["Warning: Deprecated API"]
        )
        
        # Mock client
        mock_client = Mock()
        mock_client.get_build_logs = Mock(return_value=mock_log)
        orchestrator.clients[PlatformType.AZURE_DEVOPS] = mock_client
        
        logs = await orchestrator.get_build_logs("12345", PlatformType.AZURE_DEVOPS)
        
        assert logs.run_id == "12345"
        assert "Build succeeded" in logs.logs
        assert len(logs.warnings) == 1
    
    @pytest.mark.asyncio
    async def test_get_build_logs_with_errors(self):
        """Test retrieving build logs with errors"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock build log with errors
        mock_log = BuildLog(
            run_id="67890",
            platform=PlatformType.GITHUB_ACTIONS,
            logs="Build started\nError: Compilation failed\nBuild failed",
            errors=["Error: Compilation failed"],
            warnings=[]
        )
        
        # Mock client
        mock_client = Mock()
        mock_client.get_build_logs = Mock(return_value=mock_log)
        orchestrator.clients[PlatformType.GITHUB_ACTIONS] = mock_client
        
        logs = await orchestrator.get_build_logs("67890", PlatformType.GITHUB_ACTIONS)
        
        assert len(logs.errors) == 1
        assert "Compilation failed" in logs.errors[0]


class TestCancelPipeline:
    """Tests for cancelling pipelines"""
    
    @pytest.mark.asyncio
    async def test_cancel_pipeline_success(self):
        """Test successful pipeline cancellation"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock client
        mock_client = Mock()
        mock_client.cancel_pipeline = Mock(return_value=True)
        orchestrator.clients[PlatformType.AZURE_DEVOPS] = mock_client
        
        success = await orchestrator.cancel_pipeline("12345", PlatformType.AZURE_DEVOPS)
        
        assert success is True
        mock_client.cancel_pipeline.assert_called_once_with("12345")
    
    @pytest.mark.asyncio
    async def test_cancel_pipeline_failure(self):
        """Test failed pipeline cancellation"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock client
        mock_client = Mock()
        mock_client.cancel_pipeline = Mock(return_value=False)
        orchestrator.clients[PlatformType.GITHUB_ACTIONS] = mock_client
        
        success = await orchestrator.cancel_pipeline("67890", PlatformType.GITHUB_ACTIONS)
        
        assert success is False


class TestGetPipelineHistory:
    """Tests for getting pipeline history"""
    
    @pytest.mark.asyncio
    async def test_get_pipeline_history_success(self):
        """Test getting pipeline history"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock pipeline runs
        mock_runs = [
            PipelineRun(
                run_id=f"run-{i}",
                pipeline_name="CI-Build",
                status=PipelineStatus.SUCCESS,
                start_time=datetime.now(),
                platform=PlatformType.AZURE_DEVOPS,
                branch="main"
            )
            for i in range(5)
        ]
        
        # Mock client
        mock_client = Mock()
        mock_client.get_pipeline_history = Mock(return_value=mock_runs)
        orchestrator.clients[PlatformType.AZURE_DEVOPS] = mock_client
        
        runs = await orchestrator.get_pipeline_history(
            "CI-Build",
            "my-repo",
            PlatformType.AZURE_DEVOPS,
            limit=5
        )
        
        assert len(runs) == 5
        assert all(run.pipeline_name == "CI-Build" for run in runs)


class TestExecuteOperation:
    """Tests for execute method"""
    
    @pytest.mark.asyncio
    async def test_execute_trigger_operation(self):
        """Test execute with trigger operation"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock client
        mock_client = Mock()
        mock_client.trigger_pipeline = Mock(return_value="12345")
        orchestrator.clients[PlatformType.AZURE_DEVOPS] = mock_client
        
        context = {
            "operation": "trigger",
            "config": {
                "name": "CI-Build",
                "repository": "my-repo",
                "branch": "main",
                "platform": "azure_devops"
            }
        }
        
        result = await orchestrator.execute(context)
        
        assert result["success"] is True
        assert result["run_id"] == "12345"
    
    @pytest.mark.asyncio
    async def test_execute_status_operation(self):
        """Test execute with status operation"""
        orchestrator = DevOpsOrchestrator(config={})
        
        # Mock client
        mock_client = Mock()
        mock_client.get_pipeline_status = Mock(return_value=PipelineStatus.RUNNING)
        orchestrator.clients[PlatformType.AZURE_DEVOPS] = mock_client
        
        context = {
            "operation": "status",
            "run_id": "12345",
            "platform": "azure_devops"
        }
        
        result = await orchestrator.execute(context)
        
        assert result["success"] is True
        assert result["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_execute_unknown_operation(self):
        """Test execute with unknown operation"""
        orchestrator = DevOpsOrchestrator(config={})
        
        context = {"operation": "invalid_op"}
        
        with pytest.raises(ValueError, match="Unknown operation"):
            await orchestrator.execute(context)
