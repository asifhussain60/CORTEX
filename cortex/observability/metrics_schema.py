"""
Metrics Schema - Pydantic models for instrumentation metrics.

AC-ID: AC-PHASE-20.9-01 - Metrics Schema Implementation
Author: Asif Hussain
Created: 2026-02-04

Provides type-safe metric schemas for:
- TDD cycle tracking
- Debug session monitoring
- Code generation metrics
- Orchestrator performance
"""

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class TDDMetric(BaseModel):
    """Metric for TDD cycle tracking."""
    
    cycle_id: str = Field(description="Unique cycle identifier")
    phase: Literal["RED", "GREEN", "REFACTOR"] = Field(description="TDD phase")
    orchestrator: str = Field(description="Orchestrator name")
    test_file: str = Field(description="Test file path")
    duration_ms: int = Field(ge=0, description="Duration in milliseconds")
    success: bool = Field(description="Whether cycle succeeded")
    failure_reason: Optional[str] = Field(default=None, description="Failure reason if failed")
    retry_count: int = Field(default=0, ge=0, description="Number of retries")
    timestamp: datetime = Field(default_factory=datetime.now, description="Recording timestamp")
    
    @field_validator("phase")
    @classmethod
    def validate_phase(cls, v: str) -> str:
        """Validate TDD phase."""
        valid_phases = {"RED", "GREEN", "REFACTOR"}
        if v not in valid_phases:
            raise ValueError(f"Phase must be one of {valid_phases}, got {v}")
        return v


class DebugMetric(BaseModel):
    """Metric for debugging session tracking."""
    
    session_id: str = Field(description="Unique session identifier")
    orchestrator: str = Field(description="Orchestrator name")
    target_file: str = Field(description="File being debugged")
    duration_ms: int = Field(ge=0, description="Duration in milliseconds")
    resolved: bool = Field(description="Whether issue was resolved")
    resolution_method: Optional[str] = Field(default=None, description="How it was resolved")
    steps_taken: int = Field(default=0, ge=0, description="Number of debug steps")
    timestamp: datetime = Field(default_factory=datetime.now, description="Recording timestamp")


class CodeGenMetric(BaseModel):
    """Metric for code generation tracking."""
    
    generation_id: str = Field(description="Unique generation identifier")
    template_name: str = Field(description="Template used")
    target_type: Literal["orchestrator", "tool", "test", "component"] = Field(
        description="Type of code generated"
    )
    duration_ms: int = Field(ge=0, description="Duration in milliseconds")
    success: bool = Field(description="Whether generation succeeded")
    customizations_applied: int = Field(default=0, ge=0, description="Number of customizations")
    manual_edits_needed: bool = Field(default=False, description="Whether manual edits were needed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Recording timestamp")
    
    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, v: str) -> str:
        """Validate target type."""
        valid_types = {"orchestrator", "tool", "test", "component"}
        if v not in valid_types:
            raise ValueError(f"Target type must be one of {valid_types}, got {v}")
        return v


class OrchestratorMetric(BaseModel):
    """Metric for orchestrator invocation tracking."""
    
    invocation_id: str = Field(description="Unique invocation identifier")
    orchestrator_name: str = Field(description="Orchestrator name")
    operation: str = Field(description="Operation performed")
    duration_ms: int = Field(ge=0, description="Duration in milliseconds")
    success: bool = Field(description="Whether operation succeeded")
    error_type: Optional[str] = Field(default=None, description="Error type if failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Recording timestamp")


class MetricAggregation(BaseModel):
    """Aggregated metrics for analysis."""
    
    metric_type: str = Field(description="Type of metrics aggregated")
    count: int = Field(default=0, ge=0, description="Number of metrics")
    avg_duration_ms: float = Field(default=0, ge=0, description="Average duration")
    p90_duration_ms: float = Field(default=0, ge=0, description="90th percentile duration")
    success_rate: float = Field(default=0, ge=0, le=1, description="Success rate (0-1)")
    time_range_start: Optional[datetime] = Field(default=None, description="Start of time range")
    time_range_end: Optional[datetime] = Field(default=None, description="End of time range")
    
    @classmethod
    def from_tdd_metrics(cls, metrics: list[TDDMetric]) -> "MetricAggregation":
        """Create aggregation from TDD metrics."""
        if not metrics:
            return cls(metric_type="tdd", count=0, avg_duration_ms=0, p90_duration_ms=0, success_rate=0)
            
        durations = [m.duration_ms for m in metrics]
        successes = [m.success for m in metrics]
        
        avg_duration = sum(durations) / len(durations)
        success_rate = sum(successes) / len(successes)
        
        # Calculate P90
        sorted_durations = sorted(durations)
        p90_index = int(len(sorted_durations) * 0.9)
        p90_duration = sorted_durations[min(p90_index, len(sorted_durations) - 1)]
        
        return cls(
            metric_type="tdd",
            count=len(metrics),
            avg_duration_ms=avg_duration,
            p90_duration_ms=p90_duration,
            success_rate=success_rate,
            time_range_start=min(m.timestamp for m in metrics),
            time_range_end=max(m.timestamp for m in metrics),
        )
    
    @classmethod
    def from_debug_metrics(cls, metrics: list[DebugMetric]) -> "MetricAggregation":
        """Create aggregation from debug metrics."""
        if not metrics:
            return cls(metric_type="debug", count=0, avg_duration_ms=0, p90_duration_ms=0, success_rate=0)
            
        durations = [m.duration_ms for m in metrics]
        successes = [m.resolved for m in metrics]
        
        avg_duration = sum(durations) / len(durations)
        success_rate = sum(successes) / len(successes)
        
        sorted_durations = sorted(durations)
        p90_index = int(len(sorted_durations) * 0.9)
        p90_duration = sorted_durations[min(p90_index, len(sorted_durations) - 1)]
        
        return cls(
            metric_type="debug",
            count=len(metrics),
            avg_duration_ms=avg_duration,
            p90_duration_ms=p90_duration,
            success_rate=success_rate,
        )


class EnhancementRecommendation(BaseModel):
    """Recommendation for tool enhancement based on metrics."""
    
    priority: Literal["P0", "P1", "P2"] = Field(description="Priority level")
    enhancement: str = Field(description="Enhancement description")
    evidence: dict[str, Any] = Field(description="Evidence supporting recommendation")
    effort: Literal["S", "M", "L"] = Field(description="Estimated effort")
    expected_impact: str = Field(description="Expected impact description")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority level."""
        valid_priorities = {"P0", "P1", "P2"}
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of {valid_priorities}, got {v}")
        return v


class RecordResult(BaseModel):
    """Result of recording a metric."""
    
    success: bool = Field(description="Whether recording succeeded")
    metric_id: Optional[str] = Field(default=None, description="ID of recorded metric")
    message: Optional[str] = Field(default=None, description="Additional message")
