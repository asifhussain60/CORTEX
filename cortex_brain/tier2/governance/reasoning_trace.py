"""Tier2 Governance: Reasoning Trace

Implements CORE-034: Reasoning Trace Requirements.
Tracks step-by-step reasoning with confidence scoring and evidence chains.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ReasoningStep(Enum):
    """Reasoning step types."""
    ANALYSIS = "analysis"
    INFERENCE = "inference"
    VALIDATION = "validation"
    SYNTHESIS = "synthesis"
    DECISION = "decision"


class StepConfidence(Enum):
    """Confidence levels for reasoning steps."""
    VERY_LOW = "very_low"  # < 0.25
    LOW = "low"  # 0.25-0.50
    MEDIUM = "medium"  # 0.50-0.75
    HIGH = "high"  # 0.75-0.90
    VERY_HIGH = "very_high"  # > 0.90


@dataclass
class ReasoningTraceStep:
    """Individual step in reasoning trace."""
    step_type: ReasoningStep
    description: str
    reasoning: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def get_confidence_level(self) -> StepConfidence:
        """Get confidence level enum.
        
        Returns:
            StepConfidence enum
        """
        if self.confidence > 0.90:
            return StepConfidence.VERY_HIGH
        elif self.confidence > 0.75:
            return StepConfidence.HIGH
        elif self.confidence > 0.50:
            return StepConfidence.MEDIUM
        elif self.confidence >= 0.25:
            return StepConfidence.LOW
        else:
            return StepConfidence.VERY_LOW


@dataclass
class ReasoningTrace:
    """Complete reasoning trace for a task."""
    trace_id: str
    task_description: str
    steps: List[ReasoningTraceStep] = field(default_factory=list)
    final_conclusion: str = ""
    overall_confidence: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def add_step(
        self,
        step_type: ReasoningStep,
        description: str,
        reasoning: str,
        confidence: float,
        evidence: Optional[List[str]] = None,
        assumptions: Optional[List[str]] = None
    ) -> None:
        """Add a reasoning step to the trace.
        
        Args:
            step_type: Type of reasoning step
            description: Step description
            reasoning: Reasoning explanation
            confidence: Confidence score (0-1)
            evidence: Optional list of evidence sources
            assumptions: Optional list of assumptions
        """
        if evidence is None:
            evidence = []
        if assumptions is None:
            assumptions = []
        
        step = ReasoningTraceStep(
            step_type=step_type,
            description=description,
            reasoning=reasoning,
            confidence=confidence,
            evidence=evidence,
            assumptions=assumptions
        )
        
        self.steps.append(step)
        self._update_overall_confidence()
    
    def set_conclusion(self, conclusion: str) -> None:
        """Set the final conclusion.
        
        Args:
            conclusion: Final conclusion text
        """
        self.final_conclusion = conclusion
    
    def _update_overall_confidence(self) -> None:
        """Update overall confidence based on steps."""
        if not self.steps:
            self.overall_confidence = 0.0
        else:
            self.overall_confidence = sum(s.confidence for s in self.steps) / len(self.steps)
    
    def get_trace_summary(self) -> Dict[str, Any]:
        """Get trace summary.
        
        Returns:
            Summary dictionary
        """
        step_types = {}
        for step in self.steps:
            step_type = step.step_type.value
            step_types[step_type] = step_types.get(step_type, 0) + 1
        
        return {
            "trace_id": self.trace_id,
            "task": self.task_description,
            "steps": len(self.steps),
            "overall_confidence": self.overall_confidence,
            "step_types": step_types,
            "conclusion": self.final_conclusion
        }
    
    def _get_overall_confidence_level(self) -> str:
        """Get overall confidence level as string.
        
        Returns:
            Confidence level string
        """
        if self.overall_confidence > 0.90:
            return "very_high"
        elif self.overall_confidence > 0.75:
            return "high"
        elif self.overall_confidence > 0.50:
            return "medium"
        elif self.overall_confidence >= 0.25:
            return "low"
        else:
            return "very_low"
    
    def _count_evidence(self) -> int:
        """Count total evidence sources.
        
        Returns:
            Total count of evidence
        """
        return sum(len(step.evidence) for step in self.steps)


class ReasoningTraceValidator:
    """Validate reasoning traces."""
    
    def __init__(self):
        """Initialize the validator."""
        self.traces: Dict[str, ReasoningTrace] = {}
    
    def create_trace(self, trace_id: str, task_description: str) -> ReasoningTrace:
        """Create a new trace.
        
        Args:
            trace_id: Unique trace identifier
            task_description: Description of task
            
        Returns:
            New ReasoningTrace instance
        """
        trace = ReasoningTrace(
            trace_id=trace_id,
            task_description=task_description
        )
        self.traces[trace_id] = trace
        return trace
    
    def validate_trace(self, trace_id: str) -> Dict[str, Any]:
        """Validate a reasoning trace.
        
        Args:
            trace_id: Trace to validate
            
        Returns:
            Validation result dictionary
        """
        if trace_id not in self.traces:
            return {
                "valid": False,
                "error": f"Trace '{trace_id}' not found",
                "issues": []
            }
        
        trace = self.traces[trace_id]
        issues = []
        
        # Check if trace has steps
        if not trace.steps:
            issues.append("Trace has no reasoning steps")
        
        # Check if trace has conclusion
        if not trace.final_conclusion:
            issues.append("Trace has no conclusion")
        
        # Validate each step
        for i, step in enumerate(trace.steps):
            # Check confidence range
            if step.confidence < 0 or step.confidence > 1:
                issues.append(f"Step {i}: Confidence out of range (0-1)")
            
            # Check if step has reasoning
            if not step.reasoning:
                issues.append(f"Step {i}: Missing reasoning explanation")
            
            # Check if description is provided
            if not step.description:
                issues.append(f"Step {i}: Missing description")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "total_steps": len(trace.steps),
            "overall_confidence": trace.overall_confidence
        }
    
    def get_trace_explanation(self, trace_id: str) -> str:
        """Generate human-readable explanation of trace.
        
        Args:
            trace_id: Trace to explain
            
        Returns:
            Explanation text
        """
        if trace_id not in self.traces:
            return ""
        
        trace = self.traces[trace_id]
        lines = []
        
        lines.append(f"Task: {trace.task_description}")
        lines.append("")
        lines.append("Reasoning Steps:")
        
        for i, step in enumerate(trace.steps, 1):
            lines.append(f"{i}. {step.description}")
            lines.append(f"   Type: {step.step_type.value}")
            lines.append(f"   Reasoning: {step.reasoning}")
            lines.append(f"   Confidence: {step.confidence:.2f}")
            
            if step.evidence:
                lines.append(f"   Evidence: {', '.join(step.evidence)}")
            
            if step.assumptions:
                lines.append(f"   Assumptions: {', '.join(step.assumptions)}")
            
            lines.append("")
        
        if trace.final_conclusion:
            lines.append(f"Conclusion: {trace.final_conclusion}")
            lines.append(f"Overall Confidence: {trace.overall_confidence:.2f}")
        
        return "\n".join(lines)
    
    def compare_traces(self, trace_id1: str, trace_id2: str) -> Dict[str, Any]:
        """Compare two reasoning traces.
        
        Args:
            trace_id1: First trace ID
            trace_id2: Second trace ID
            
        Returns:
            Comparison result dictionary
        """
        trace1 = self.traces.get(trace_id1)
        trace2 = self.traces.get(trace_id2)
        
        if not trace1 or not trace2:
            return {
                "error": "One or both traces not found"
            }
        
        return {
            "trace1_id": trace_id1,
            "trace2_id": trace_id2,
            "steps_difference": len(trace1.steps) - len(trace2.steps),
            "confidence_difference": trace1.overall_confidence - trace2.overall_confidence,
            "conclusions_match": trace1.final_conclusion == trace2.final_conclusion
        }
    
    def get_trace_statistics(self) -> Dict[str, Any]:
        """Get statistics across all traces.
        
        Returns:
            Statistics dictionary
        """
        if not self.traces:
            return {
                "total_traces": 0,
                "average_steps": 0.0,
                "average_confidence": 0.0
            }
        
        total_steps = sum(len(t.steps) for t in self.traces.values())
        avg_steps = total_steps / len(self.traces) if self.traces else 0
        
        avg_confidence = sum(t.overall_confidence for t in self.traces.values()) / len(self.traces)
        
        return {
            "total_traces": len(self.traces),
            "average_steps": avg_steps,
            "average_confidence": avg_confidence
        }


__all__ = [
    "ReasoningTraceStep",
    "ReasoningTrace",
    "ReasoningStep",
    "StepConfidence",
    "ReasoningTraceValidator"
]
