"""
Pydantic data models for DIGEST Quantitative Metrics System.

Phase 41 Stage 2 (ENH-055):
- EfficiencyMetrics: Task completion efficiency
- AccuracyMetrics: Response correctness tracking
- ToolSuccessMetrics: Tool invocation success rate
- LearningVelocityMetrics: Enhancement extraction rate
- ContextEfficiencyMetrics: Token utilization efficiency
- DigestMetrics: Aggregated metrics container

Author: Asif Hussain
Date: 2026-02-07
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EfficiencyMetrics(BaseModel):
    """
    Efficiency score metrics.
    
    Measures how efficiently CORTEX completes tasks relative to expected turns.
    Formula: (expected_turns / actual_turns) × 100, capped at 100%.
    """
    
    score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Efficiency score (0-100%)"
    )
    
    actual_turns: int = Field(
        ...,
        ge=0,
        description="Actual conversation turns taken"
    )
    
    expected_turns: int = Field(
        ...,
        ge=0,
        description="Expected turns for task complexity"
    )
    
    exceeded_expectations: bool = Field(
        default=False,
        description="True if actual < expected (beat expectations)"
    )
    
    task_complexity: Optional[str] = Field(
        default=None,
        description="Task complexity level: simple, medium, complex"
    )


class AccuracyMetrics(BaseModel):
    """
    Accuracy score metrics.
    
    Measures correctness of CORTEX responses by tracking corrections.
    Formula: ((total - corrections) / total) × 100.
    """
    
    score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Accuracy score (0-100%)"
    )
    
    total_turns: int = Field(
        ...,
        ge=0,
        description="Total conversation turns"
    )
    
    corrections: int = Field(
        ...,
        ge=0,
        description="Number of corrections/fixes required"
    )
    
    correct_responses: int = Field(
        ...,
        ge=0,
        description="Number of correct responses (total - corrections)"
    )
    
    correction_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords detected for corrections (wrong, fix, error, etc.)"
    )


class ToolSuccessMetrics(BaseModel):
    """
    Tool invocation success rate metrics.
    
    Tracks success/failure rate of tool invocations.
    Formula: (successful / total) × 100.
    """
    
    success_rate: float = Field(
        ...,
        ge=0,
        le=100,
        description="Tool success rate (0-100%)"
    )
    
    total_invocations: int = Field(
        ...,
        ge=0,
        description="Total tool invocations"
    )
    
    successful_invocations: int = Field(
        ...,
        ge=0,
        description="Successful tool invocations"
    )
    
    failed_invocations: int = Field(
        ...,
        ge=0,
        description="Failed tool invocations"
    )
    
    tool_breakdown: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description="Per-tool success/failure breakdown"
    )


class LearningVelocityMetrics(BaseModel):
    """
    Learning velocity metrics.
    
    Measures rate of enhancement extraction from chat sessions.
    Formula: enhancements_extracted / sessions_analyzed.
    """
    
    velocity: float = Field(
        ...,
        ge=0,
        description="Enhancements per session"
    )
    
    enhancements_extracted: int = Field(
        ...,
        ge=0,
        description="Total enhancements extracted"
    )
    
    sessions_analyzed: int = Field(
        ...,
        gt=0,
        description="Total sessions analyzed"
    )
    
    high_value_session: bool = Field(
        default=False,
        description="True if velocity > 1.0 (multiple enhancements per session)"
    )
    
    improvement_rate: Optional[float] = Field(
        default=None,
        description="Percentage improvement from previous period"
    )


class ContextEfficiencyMetrics(BaseModel):
    """
    Context efficiency metrics.
    
    Measures token utilization efficiency (meaningful vs wasted tokens).
    Formula: (meaningful_tokens / total_tokens) × 100.
    """
    
    efficiency: float = Field(
        ...,
        ge=0,
        le=100,
        description="Context efficiency (0-100%)"
    )
    
    meaningful_tokens: int = Field(
        ...,
        ge=0,
        description="Tokens contributing to task completion"
    )
    
    total_tokens: int = Field(
        ...,
        gt=0,
        description="Total tokens used"
    )
    
    wasted_tokens: int = Field(
        ...,
        ge=0,
        description="Tokens wasted (narration, repetition, etc.)"
    )
    
    waste_patterns: List[str] = Field(
        default_factory=list,
        description="Detected waste patterns (narration, repetition, etc.)"
    )
    
    recommendations: List[str] = Field(
        default_factory=list,
        description="Efficiency improvement recommendations"
    )
    
    needs_improvement: bool = Field(
        default=False,
        description="True if efficiency < 70%"
    )


class DigestMetrics(BaseModel):
    """
    Aggregated DIGEST metrics container.
    
    Contains all 5 metric types plus overall quality score.
    """
    
    efficiency: EfficiencyMetrics = Field(
        ...,
        description="Efficiency metrics"
    )
    
    accuracy: AccuracyMetrics = Field(
        ...,
        description="Accuracy metrics"
    )
    
    tool_success: ToolSuccessMetrics = Field(
        ...,
        description="Tool success metrics"
    )
    
    learning_velocity: LearningVelocityMetrics = Field(
        ...,
        description="Learning velocity metrics"
    )
    
    context_efficiency: ContextEfficiencyMetrics = Field(
        ...,
        description="Context efficiency metrics"
    )
    
    overall_quality_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Weighted average of all metrics (0-100)"
    )
    
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "efficiency": 0.25,
            "accuracy": 0.30,
            "tool_success": 0.20,
            "learning_velocity": 0.15,
            "context_efficiency": 0.10
        },
        description="Weights for overall_quality_score calculation"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (timestamp, session_id, etc.)"
    )
