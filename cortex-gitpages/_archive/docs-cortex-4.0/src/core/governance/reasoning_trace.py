"""
CORE-034: Reasoning Trace Requirements

Captures and validates reasoning traces through model execution:
- Step-by-step reasoning documentation
- Confidence scores at each step
- Evidence chain tracking
- Explanation generation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class ReasoningStep(Enum):
    """Type of reasoning step."""
    ANALYSIS = "analysis"
    INFERENCE = "inference"
    VALIDATION = "validation"
    SYNTHESIS = "synthesis"
    CONCLUSION = "conclusion"


class StepConfidence(Enum):
    """Confidence level for a reasoning step."""
    VERY_LOW = "very_low"      # < 0.30
    LOW = "low"                 # 0.30-0.50
    MEDIUM = "medium"           # 0.50-0.75
    HIGH = "high"               # 0.75-0.90
    VERY_HIGH = "very_high"     # >= 0.90


@dataclass
class ReasoningTraceStep:
    """Single step in a reasoning trace."""
    step_type: ReasoningStep
    description: str
    reasoning: str
    confidence: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def get_confidence_level(self) -> StepConfidence:
        """Get confidence level from score."""
        if self.confidence < 0.30:
            return StepConfidence.VERY_LOW
        elif self.confidence < 0.50:
            return StepConfidence.LOW
        elif self.confidence < 0.75:
            return StepConfidence.MEDIUM
        elif self.confidence < 0.90:
            return StepConfidence.HIGH
        else:
            return StepConfidence.VERY_HIGH


@dataclass
class ReasoningTrace:
    """Complete reasoning trace for a decision or output."""
    trace_id: str
    task_description: str
    steps: List[ReasoningTraceStep] = field(default_factory=list)
    final_conclusion: Optional[str] = None
    overall_confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_step(
        self,
        step_type: ReasoningStep,
        description: str,
        reasoning: str,
        confidence: float,
        evidence: Optional[List[str]] = None,
        assumptions: Optional[List[str]] = None
    ) -> None:
        """
        Add a reasoning step to the trace.
        
        Args:
            step_type: Type of reasoning step.
            description: Short description of step.
            reasoning: Detailed reasoning.
            confidence: Confidence score (0.0-1.0).
            evidence: Supporting evidence.
            assumptions: Underlying assumptions.
        """
        step = ReasoningTraceStep(
            step_type=step_type,
            description=description,
            reasoning=reasoning,
            confidence=confidence,
            evidence=evidence or [],
            assumptions=assumptions or []
        )
        self.steps.append(step)
        self._update_overall_confidence()
    
    def _update_overall_confidence(self) -> None:
        """Update overall confidence from all steps."""
        if not self.steps:
            self.overall_confidence = 0.0
            return
        
        # Average confidence weighted by step importance
        total_confidence = sum(s.confidence for s in self.steps)
        self.overall_confidence = total_confidence / len(self.steps)
    
    def set_conclusion(self, conclusion: str) -> None:
        """
        Set final conclusion.
        
        Args:
            conclusion: Final reasoning conclusion.
        """
        self.final_conclusion = conclusion
    
    def get_trace_summary(self) -> Dict[str, Any]:
        """
        Get summary of reasoning trace.
        
        Returns:
            Dictionary with trace summary.
        """
        if not self.steps:
            return {
                "task": self.task_description,
                "steps": 0,
                "overall_confidence": 0.0,
                "conclusion": self.final_conclusion,
            }
        
        step_types = {}
        for step in self.steps:
            step_type = step.step_type.value
            step_types[step_type] = step_types.get(step_type, 0) + 1
        
        return {
            "task": self.task_description,
            "steps": len(self.steps),
            "step_types": step_types,
            "overall_confidence": self.overall_confidence,
            "confidence_level": self._get_overall_confidence_level(),
            "conclusion": self.final_conclusion,
            "evidence_sources": self._count_evidence(),
        }
    
    def _get_overall_confidence_level(self) -> str:
        """Get confidence level for overall trace."""
        if self.overall_confidence < 0.30:
            return "very_low"
        elif self.overall_confidence < 0.50:
            return "low"
        elif self.overall_confidence < 0.75:
            return "medium"
        elif self.overall_confidence < 0.90:
            return "high"
        else:
            return "very_high"
    
    def _count_evidence(self) -> int:
        """Count total evidence sources in trace."""
        return sum(len(s.evidence) for s in self.steps)


class ReasoningTraceValidator:
    """Validates and manages reasoning traces."""
    
    def __init__(self):
        """Initialize validator."""
        self.traces: Dict[str, ReasoningTrace] = {}
        self.validation_results: List[Dict[str, Any]] = []
    
    def create_trace(self, trace_id: str, task_description: str) -> ReasoningTrace:
        """
        Create a new reasoning trace.
        
        Args:
            trace_id: Unique trace identifier.
            task_description: Description of the task.
            
        Returns:
            New ReasoningTrace object.
        """
        trace = ReasoningTrace(
            trace_id=trace_id,
            task_description=task_description
        )
        self.traces[trace_id] = trace
        return trace
    
    def validate_trace(self, trace_id: str) -> Dict[str, Any]:
        """
        Validate a reasoning trace.
        
        Args:
            trace_id: ID of trace to validate.
            
        Returns:
            Dictionary with validation results.
        """
        if trace_id not in self.traces:
            return {
                "valid": False,
                "error": f"Trace {trace_id} not found"
            }
        
        trace = self.traces[trace_id]
        issues = []
        
        # Validate trace has steps
        if len(trace.steps) == 0:
            issues.append("Trace has no reasoning steps")
        
        # Validate each step has confidence
        for step in trace.steps:
            if step.confidence < 0.0 or step.confidence > 1.0:
                issues.append(f"Step confidence out of range: {step.confidence}")
            
            if not step.reasoning:
                issues.append(f"Step missing reasoning: {step.description}")
        
        # Validate has conclusion
        if not trace.final_conclusion:
            issues.append("Trace missing final conclusion")
        
        # Validate overall confidence is reasonable
        if trace.steps and trace.overall_confidence < 0.3:
            issues.append("Overall confidence is very low")
        
        validation_result = {
            "trace_id": trace_id,
            "valid": len(issues) == 0,
            "issues": issues,
            "step_count": len(trace.steps),
            "overall_confidence": trace.overall_confidence,
        }
        
        self.validation_results.append(validation_result)
        return validation_result
    
    def get_trace_explanation(self, trace_id: str) -> str:
        """
        Get human-readable explanation of trace.
        
        Args:
            trace_id: ID of trace.
            
        Returns:
            Formatted explanation string.
        """
        if trace_id not in self.traces:
            return ""
        
        trace = self.traces[trace_id]
        explanation = f"Task: {trace.task_description}\n\n"
        explanation += "Reasoning Trace:\n"
        explanation += "-" * 50 + "\n"
        
        for i, step in enumerate(trace.steps, 1):
            explanation += f"\nStep {i}: {step.step_type.value.upper()}\n"
            explanation += f"Description: {step.description}\n"
            explanation += f"Reasoning: {step.reasoning}\n"
            explanation += f"Confidence: {step.confidence:.2f} ({step.get_confidence_level().value})\n"
            
            if step.evidence:
                explanation += f"Evidence: {', '.join(step.evidence)}\n"
            
            if step.assumptions:
                explanation += f"Assumptions: {', '.join(step.assumptions)}\n"
        
        explanation += "\n" + "-" * 50 + "\n"
        explanation += f"Final Conclusion: {trace.final_conclusion}\n"
        explanation += f"Overall Confidence: {trace.overall_confidence:.2f}\n"
        
        return explanation
    
    def compare_traces(self, trace_id1: str, trace_id2: str) -> Dict[str, Any]:
        """
        Compare two reasoning traces.
        
        Args:
            trace_id1: First trace ID.
            trace_id2: Second trace ID.
            
        Returns:
            Comparison results.
        """
        if trace_id1 not in self.traces or trace_id2 not in self.traces:
            return {"error": "One or both traces not found"}
        
        trace1 = self.traces[trace_id1]
        trace2 = self.traces[trace_id2]
        
        return {
            "trace1_id": trace_id1,
            "trace2_id": trace_id2,
            "trace1_steps": len(trace1.steps),
            "trace2_steps": len(trace2.steps),
            "trace1_confidence": trace1.overall_confidence,
            "trace2_confidence": trace2.overall_confidence,
            "confidence_difference": abs(trace1.overall_confidence - trace2.overall_confidence),
            "trace1_conclusion": trace1.final_conclusion,
            "trace2_conclusion": trace2.final_conclusion,
            "conclusions_match": trace1.final_conclusion == trace2.final_conclusion,
        }
    
    def get_trace_statistics(self) -> Dict[str, Any]:
        """
        Get statistics on all traces.
        
        Returns:
            Dictionary with trace statistics.
        """
        if not self.traces:
            return {
                "total_traces": 0,
                "average_steps": 0.0,
                "average_confidence": 0.0,
            }
        
        total_steps = sum(len(t.steps) for t in self.traces.values())
        total_confidence = sum(t.overall_confidence for t in self.traces.values())
        
        return {
            "total_traces": len(self.traces),
            "average_steps": total_steps / len(self.traces),
            "average_confidence": total_confidence / len(self.traces),
            "traces_with_low_confidence": sum(
                1 for t in self.traces.values() if t.overall_confidence < 0.5
            ),
        }
