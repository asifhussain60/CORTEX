"""
DevOps Orchestrator Schemas

Pydantic models for pipeline management and CI/CD operations.

Author: Asif Hussain
Version: 1.0
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class PipelineStatus(str, Enum):
    """Pipeline run status"""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class PlatformType(str, Enum):
    """Supported CI/CD platforms"""
    AZURE_DEVOPS = "azure_devops"
    GITHUB_ACTIONS = "github_actions"
    JENKINS = "jenkins"
    GITLAB_CI = "gitlab_ci"


class PipelineConfig(BaseModel):
    """Configuration for triggering a pipeline"""
    name: str = Field(..., description="Pipeline name")
    repository: str = Field(..., description="Repository URL or identifier")
    branch: str = Field(default="main", description="Branch to run pipeline on")
    platform: PlatformType = Field(..., description="CI/CD platform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Pipeline parameters")
    
    class Config:
        use_enum_values = True


class PipelineRun(BaseModel):
    """Information about a pipeline run"""
    run_id: str = Field(..., description="Unique run identifier")
    pipeline_name: str = Field(..., description="Pipeline name")
    status: PipelineStatus = Field(..., description="Current status")
    start_time: datetime = Field(..., description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    duration_seconds: Optional[float] = Field(None, description="Duration in seconds")
    platform: PlatformType = Field(..., description="CI/CD platform")
    branch: str = Field(default="main", description="Branch")
    commit_sha: Optional[str] = Field(None, description="Commit SHA")
    url: Optional[str] = Field(None, description="Pipeline run URL")
    
    class Config:
        use_enum_values = True


class BuildLog(BaseModel):
    """Build log information"""
    run_id: str = Field(..., description="Pipeline run ID")
    platform: PlatformType = Field(..., description="CI/CD platform")
    logs: str = Field(..., description="Raw log content")
    errors: List[str] = Field(default_factory=list, description="Extracted error messages")
    warnings: List[str] = Field(default_factory=list, description="Extracted warnings")
    timestamp: datetime = Field(default_factory=datetime.now, description="Log retrieval time")
    
    class Config:
        use_enum_values = True


class PipelineError(BaseModel):
    """Pipeline execution error"""
    run_id: str = Field(..., description="Pipeline run ID")
    error_type: str = Field(..., description="Error type/category")
    message: str = Field(..., description="Error message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error time")
    recoverable: bool = Field(default=False, description="Whether error is recoverable")
    
    class Config:
        use_enum_values = True
