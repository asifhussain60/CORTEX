"""
DevOps Orchestrator for CORTEX 4.0

Provides CI/CD pipeline management and automation capabilities.
Supports multiple platforms: Azure DevOps, GitHub Actions.

Author: Asif Hussain
Version: 1.0
"""

from typing import Dict, Any, Optional, List
import logging

from src.orchestration_4_0.base import BaseOrchestrator
from .schemas import (
    PipelineConfig,
    PipelineRun,
    PipelineStatus,
    BuildLog,
    PlatformType
)
from .platform_client import PlatformClient
from .azure_devops_client import AzureDevOpsClient
from .github_actions_client import GitHubActionsClient


class DevOpsOrchestrator(BaseOrchestrator):
    """
    CI/CD pipeline management orchestrator.
    
    Provides unified interface for:
    - Triggering pipeline runs
    - Monitoring pipeline status
    - Retrieving build logs
    - Cancelling pipelines
    - Accessing pipeline history
    
    Supports multiple platforms:
    - Azure DevOps Pipelines
    - GitHub Actions
    - (Extensible to Jenkins, GitLab CI/CD)
    
    Usage:
        orchestrator = DevOpsOrchestrator(
            logger=logger,
            config={
                "platforms": {
                    "azure_devops": {
                        "organization": "my-org",
                        "project": "my-project",
                        "personal_access_token": "***"
                    },
                    "github_actions": {
                        "owner": "my-owner",
                        "repository": "my-repo",
                        "token": "***"
                    }
                }
            }
        )
        
        # Trigger pipeline
        config = PipelineConfig(
            name="CI-Build",
            repository="my-repo",
            branch="main",
            platform=PlatformType.AZURE_DEVOPS,
            parameters={"BUILD_TYPE": "Release"}
        )
        
        run_id = await orchestrator.trigger_pipeline(config)
        
        # Monitor status
        status = await orchestrator.get_pipeline_status(run_id, PlatformType.AZURE_DEVOPS)
    """
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize DevOps orchestrator.
        
        Args:
            logger: Optional logger instance
            config: Configuration with platform credentials
        """
        super().__init__(
            name="devops",
            logger=logger,
            config=config
        )
        
        # Platform clients
        self.clients: Dict[PlatformType, PlatformClient] = {}
        self._initialize_clients()
        
        self.logger.info("🎭 DevOps orchestrator initialized")
        self.logger.info(f"  Platforms: {list(self.clients.keys())}")
    
    def _initialize_clients(self) -> None:
        """Initialize platform-specific clients"""
        platforms_config = self.config.get("platforms", {})
        
        # Azure DevOps
        if "azure_devops" in platforms_config:
            try:
                self.clients[PlatformType.AZURE_DEVOPS] = AzureDevOpsClient(
                    platforms_config["azure_devops"]
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize Azure DevOps client: {e}")
        
        # GitHub Actions
        if "github_actions" in platforms_config:
            try:
                self.clients[PlatformType.GITHUB_ACTIONS] = GitHubActionsClient(
                    platforms_config["github_actions"]
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize GitHub Actions client: {e}")
        
        if not self.clients:
            self.logger.warning("⚠️ No platform clients initialized")
    
    async def trigger_pipeline(self, config: PipelineConfig) -> str:
        """
        Trigger a pipeline run.
        
        Args:
            config: Pipeline configuration
            
        Returns:
            run_id: Unique identifier for the pipeline run
            
        Raises:
            ValueError: If platform not configured
            RuntimeError: If pipeline trigger fails
        """
        client = self._get_client(config.platform)
        
        self.logger.info(f"🎭 Triggering pipeline: {config.name} on {config.platform}")
        
        run_id = client.trigger_pipeline(
            pipeline_name=config.name,
            repository=config.repository,
            branch=config.branch,
            parameters=config.parameters
        )
        
        self.logger.info(f"✅ Pipeline triggered: {run_id}")
        return run_id
    
    async def get_pipeline_status(
        self,
        run_id: str,
        platform: PlatformType
    ) -> PipelineStatus:
        """
        Get current status of a pipeline run.
        
        Args:
            run_id: Pipeline run identifier
            platform: CI/CD platform
            
        Returns:
            Current pipeline status
        """
        client = self._get_client(platform)
        status = client.get_pipeline_status(run_id)
        
        self.logger.debug(f"Pipeline {run_id} status: {status}")
        return status
    
    async def get_pipeline_run(
        self,
        run_id: str,
        platform: PlatformType
    ) -> PipelineRun:
        """
        Get detailed information about a pipeline run.
        
        Args:
            run_id: Pipeline run identifier
            platform: CI/CD platform
            
        Returns:
            PipelineRun with full details
        """
        client = self._get_client(platform)
        return client.get_pipeline_run(run_id)
    
    async def get_build_logs(
        self,
        run_id: str,
        platform: PlatformType
    ) -> BuildLog:
        """
        Retrieve build logs for a pipeline run.
        
        Args:
            run_id: Pipeline run identifier
            platform: CI/CD platform
            
        Returns:
            BuildLog with logs and parsed errors/warnings
        """
        client = self._get_client(platform)
        
        self.logger.info(f"📋 Retrieving logs for run: {run_id}")
        logs = client.get_build_logs(run_id)
        
        self.logger.info(f"✅ Retrieved logs: {len(logs.logs)} chars, "
                        f"{len(logs.errors)} errors, {len(logs.warnings)} warnings")
        return logs
    
    async def cancel_pipeline(
        self,
        run_id: str,
        platform: PlatformType
    ) -> bool:
        """
        Cancel a running pipeline.
        
        Args:
            run_id: Pipeline run identifier
            platform: CI/CD platform
            
        Returns:
            True if cancellation successful
        """
        client = self._get_client(platform)
        
        self.logger.info(f"🛑 Cancelling pipeline: {run_id}")
        success = client.cancel_pipeline(run_id)
        
        if success:
            self.logger.info(f"✅ Pipeline cancelled: {run_id}")
        else:
            self.logger.error(f"❌ Failed to cancel pipeline: {run_id}")
        
        return success
    
    async def get_pipeline_history(
        self,
        pipeline_name: str,
        repository: str,
        platform: PlatformType,
        limit: int = 10
    ) -> List[PipelineRun]:
        """
        Get recent pipeline runs.
        
        Args:
            pipeline_name: Pipeline name
            repository: Repository identifier
            platform: CI/CD platform
            limit: Maximum number of runs to return
            
        Returns:
            List of recent pipeline runs
        """
        client = self._get_client(platform)
        
        self.logger.info(f"📊 Retrieving pipeline history: {pipeline_name} (limit={limit})")
        runs = client.get_pipeline_history(pipeline_name, repository, limit)
        
        self.logger.info(f"✅ Retrieved {len(runs)} pipeline runs")
        return runs
    
    def _get_client(self, platform: PlatformType) -> PlatformClient:
        """
        Get platform client.
        
        Args:
            platform: CI/CD platform
            
        Returns:
            Platform client
            
        Raises:
            ValueError: If platform not configured
        """
        if platform not in self.clients:
            raise ValueError(
                f"Platform not configured: {platform}. "
                f"Available: {list(self.clients.keys())}"
            )
        
        return self.clients[platform]
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute DevOps operation based on context.
        
        Args:
            context: Operation context with:
                - operation: "trigger", "status", "logs", "cancel", "history"
                - Additional operation-specific parameters
                
        Returns:
            Operation result
        """
        operation = context.get("operation")
        
        if operation == "trigger":
            config = PipelineConfig(**context["config"])
            run_id = await self.trigger_pipeline(config)
            return {"success": True, "run_id": run_id}
        
        elif operation == "status":
            status = await self.get_pipeline_status(
                context["run_id"],
                PlatformType(context["platform"])
            )
            return {"success": True, "status": status.value}
        
        elif operation == "logs":
            logs = await self.get_build_logs(
                context["run_id"],
                PlatformType(context["platform"])
            )
            return {
                "success": True,
                "logs": logs.logs,
                "errors": logs.errors,
                "warnings": logs.warnings
            }
        
        elif operation == "cancel":
            success = await self.cancel_pipeline(
                context["run_id"],
                PlatformType(context["platform"])
            )
            return {"success": success}
        
        elif operation == "history":
            runs = await self.get_pipeline_history(
                context["pipeline_name"],
                context["repository"],
                PlatformType(context["platform"]),
                context.get("limit", 10)
            )
            return {
                "success": True,
                "runs": [run.dict() for run in runs]
            }
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    # BaseOrchestrator abstract method implementations
    
    def _setup(self, context: Dict[str, Any]) -> None:
        """Setup DevOps orchestrator (no additional setup needed)"""
        pass
    
    def _register_phases(self) -> None:
        """Register phases (DevOps operations are direct API calls, no phases)"""
        pass
    
    def _execute_phase(self, phase_name: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute phase (not used for DevOps orchestrator)"""
        return None
    
    def _teardown(self) -> None:
        """Cleanup DevOps orchestrator (no cleanup needed)"""
        pass
