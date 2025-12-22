"""
Platform Client Base Class

Abstract interface for CI/CD platform integrations.

Author: Asif Hussain
Version: 1.0
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime

from .schemas import PipelineStatus, PipelineRun, BuildLog


class PlatformClient(ABC):
    """
    Abstract base class for CI/CD platform clients.
    
    Each platform (Azure DevOps, GitHub Actions, etc.) implements this interface.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize platform client.
        
        Args:
            config: Platform-specific configuration (credentials, org, etc.)
        """
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate required configuration parameters"""
        pass
    
    @abstractmethod
    def trigger_pipeline(
        self,
        pipeline_name: str,
        repository: str,
        branch: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Trigger a pipeline run.
        
        Args:
            pipeline_name: Name of the pipeline to trigger
            repository: Repository identifier
            branch: Branch to run pipeline on
            parameters: Optional pipeline parameters
            
        Returns:
            run_id: Unique identifier for the pipeline run
        """
        pass
    
    @abstractmethod
    def get_pipeline_status(self, run_id: str) -> PipelineStatus:
        """
        Get current status of a pipeline run.
        
        Args:
            run_id: Pipeline run identifier
            
        Returns:
            Current pipeline status
        """
        pass
    
    @abstractmethod
    def get_pipeline_run(self, run_id: str) -> PipelineRun:
        """
        Get detailed information about a pipeline run.
        
        Args:
            run_id: Pipeline run identifier
            
        Returns:
            PipelineRun object with full details
        """
        pass
    
    @abstractmethod
    def get_build_logs(self, run_id: str) -> BuildLog:
        """
        Retrieve build logs for a pipeline run.
        
        Args:
            run_id: Pipeline run identifier
            
        Returns:
            BuildLog object with logs and parsed errors
        """
        pass
    
    @abstractmethod
    def cancel_pipeline(self, run_id: str) -> bool:
        """
        Cancel a running pipeline.
        
        Args:
            run_id: Pipeline run identifier
            
        Returns:
            True if cancellation successful
        """
        pass
    
    @abstractmethod
    def get_pipeline_history(
        self,
        pipeline_name: str,
        repository: str,
        limit: int = 10
    ) -> List[PipelineRun]:
        """
        Get recent pipeline runs.
        
        Args:
            pipeline_name: Pipeline name
            repository: Repository identifier
            limit: Maximum number of runs to return
            
        Returns:
            List of recent pipeline runs
        """
        pass
