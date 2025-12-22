"""
Pydantic Schemas for Execution Orchestrator

Structured outputs for type-safe execution results.

Author: Asif Hussain
Version: 1.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ExecutionMode(str, Enum):
    """Execution mode for orchestrator"""
    AUTONOMOUS = "autonomous"
    SUPERVISED = "supervised"
    MANUAL = "manual"


class PhaseStatus(str, Enum):
    """Phase execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PhaseResult(BaseModel):
    """Result of a single phase execution"""
    phase_name: str
    status: PhaseStatus
    success: bool
    duration_ms: float
    output: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class ExecutionResult(BaseModel):
    """Structured execution result"""
    success: bool
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phases_completed: List[str]
    phases_failed: List[str] = Field(default_factory=list)
    phase_results: List[PhaseResult]
    total_duration_ms: float
    context: Dict[str, Any]
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
    execution_mode: ExecutionMode = ExecutionMode.SUPERVISED
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility"""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return self.model_dump_json(indent=2)


class ContextValidation(BaseModel):
    """Result of context validation"""
    has_requirements: bool
    missing_required: List[str] = Field(default_factory=list)
    missing_optional: List[str] = Field(default_factory=list)
    quality_issues: List[str] = Field(default_factory=list)
    context: Dict[str, Any]
    auto_retrieved: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed"""
        return self.has_requirements and len(self.quality_issues) == 0


class RiskSeverity(str, Enum):
    """Risk severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Risk(BaseModel):
    """Execution risk"""
    severity: RiskSeverity
    category: str
    message: str
    recommendation: str
    
    class Config:
        use_enum_values = True


class SafetyCheck(BaseModel):
    """Result of safety check"""
    safe: bool
    risks: List[Risk] = Field(default_factory=list)
    max_risk: RiskSeverity = RiskSeverity.LOW
    requires_approval: bool = False
    
    class Config:
        use_enum_values = True
    
    @property
    def is_critical(self) -> bool:
        """Check if critical risks found"""
        return self.max_risk == RiskSeverity.CRITICAL
    
    @property
    def is_high_risk(self) -> bool:
        """Check if high risks found"""
        return self.max_risk in [RiskSeverity.CRITICAL, RiskSeverity.HIGH]
