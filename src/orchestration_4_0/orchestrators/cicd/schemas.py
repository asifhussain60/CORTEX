"""
CI/CD Self-Healing Orchestrator Schemas

Pydantic models for failure analysis and auto-fix workflows.

Author: Asif Hussain
Version: 1.0
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class FailureCategory(str, Enum):
    """Build failure categories"""
    DEPENDENCY_CONFLICT = "dependency_conflict"
    TEST_FAILURE = "test_failure"
    CONFIGURATION_ERROR = "configuration_error"
    SYNTAX_ERROR = "syntax_error"
    SECURITY_ISSUE = "security_issue"
    TIMEOUT = "timeout"
    RESOURCE_LIMIT = "resource_limit"
    UNKNOWN = "unknown"


class FixStrategy(str, Enum):
    """Available fix strategies"""
    DEPENDENCY_UPDATE = "dependency_update"
    DEPENDENCY_ROLLBACK = "dependency_rollback"
    TEST_RETRY = "test_retry"
    TEST_ISOLATION = "test_isolation"
    CONFIG_FIX = "config_fix"
    ENV_VAR_ADD = "env_var_add"
    TIMEOUT_INCREASE = "timeout_increase"
    RESOURCE_INCREASE = "resource_increase"
    CODE_FIX = "code_fix"
    ROLLBACK = "rollback"
    MANUAL_INTERVENTION = "manual_intervention"


class FailureAnalysis(BaseModel):
    """Analysis of a build failure"""
    category: FailureCategory = Field(..., description="Failure category")
    root_cause: str = Field(..., description="Root cause description")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    affected_files: List[str] = Field(default_factory=list, description="Files affected by failure")
    affected_dependencies: List[str] = Field(default_factory=list, description="Dependencies involved")
    error_messages: List[str] = Field(default_factory=list, description="Extracted error messages")
    suggested_fixes: List[FixStrategy] = Field(default_factory=list, description="Suggested fix strategies")
    auto_fixable: bool = Field(..., description="Whether failure can be auto-fixed")
    requires_human: bool = Field(default=False, description="Whether human intervention required")
    analysis_time_ms: float = Field(..., description="Time taken for analysis (ms)")
    
    class Config:
        use_enum_values = True


class FixAttempt(BaseModel):
    """Record of a fix attempt"""
    strategy: FixStrategy = Field(..., description="Fix strategy used")
    success: bool = Field(..., description="Whether fix was successful")
    fixes_applied: List[str] = Field(default_factory=list, description="List of fixes applied")
    changes_made: Dict[str, Any] = Field(default_factory=dict, description="Changes made (files, configs, etc.)")
    time_seconds: float = Field(..., description="Time taken for fix (seconds)")
    error_message: Optional[str] = Field(None, description="Error message if fix failed")
    verification_passed: bool = Field(default=False, description="Whether verification passed")
    
    class Config:
        use_enum_values = True


class HealingResult(BaseModel):
    """Result of self-healing workflow"""
    run_id: str = Field(..., description="Pipeline run ID")
    platform: str = Field(..., description="CI/CD platform")
    initial_failure: Optional[FailureAnalysis] = Field(None, description="Initial failure analysis (None if no failure)")
    fix_attempts: List[FixAttempt] = Field(default_factory=list, description="Fix attempts made")
    final_status: str = Field(..., description="Final pipeline status")
    healed: bool = Field(..., description="Whether pipeline was successfully healed")
    total_healing_time_seconds: float = Field(..., description="Total time for healing (seconds)")
    human_escalation_triggered: bool = Field(default=False, description="Whether escalated to human")
    learning_feedback: Optional[Dict[str, Any]] = Field(None, description="Feedback for learning engine")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")
    
    class Config:
        use_enum_values = True


class EscalationRequest(BaseModel):
    """Request for human intervention"""
    run_id: str = Field(..., description="Pipeline run ID")
    platform: str = Field(..., description="CI/CD platform")
    failure: FailureAnalysis = Field(..., description="Failure analysis")
    failed_fixes: List[FixAttempt] = Field(default_factory=list, description="Failed fix attempts")
    urgency: str = Field(..., description="Urgency level: LOW, MEDIUM, HIGH, CRITICAL")
    notification_sent: bool = Field(default=False, description="Whether notification sent")
    assigned_to: Optional[str] = Field(None, description="Human assignee")
    timestamp: datetime = Field(default_factory=datetime.now, description="Escalation timestamp")
    
    class Config:
        use_enum_values = True
