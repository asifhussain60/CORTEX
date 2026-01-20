"""
Test suite for CORE-034: Reasoning Trace Requirements.

Validates:
- Step-by-step reasoning documentation
- Confidence scoring at each step
- Evidence chain tracking
- Explanation generation and trace comparison
"""

import pytest
from datetime import datetime
from cortex.core.governance.reasoning_trace import (
    ReasoningTrace,
    ReasoningTraceStep,
    ReasoningTraceValidator,
    ReasoningStep,
    StepConfidence,
)


class TestReasoningTraceStep:
    """Tests for individual reasoning steps."""
    
    def test_create_reasoning_step(self):
        """Test creating a reasoning step."""
        step = ReasoningTraceStep(
            step_type=ReasoningStep.ANALYSIS,
            description="Analyze input data",
            reasoning="Examined data structure",
            confidence=0.85
        )
        assert step.step_type == ReasoningStep.ANALYSIS
        assert step.confidence == 0.85
    
    def test_step_with_evidence(self):
        """Test step with evidence."""
        step = ReasoningTraceStep(
            step_type=ReasoningStep.INFERENCE,
            description="Make inference",
            reasoning="Based on analysis",
            confidence=0.75,
            evidence=["source1", "source2"]
        )
        assert len(step.evidence) == 2
    
    def test_step_with_assumptions(self):
        """Test step with assumptions."""
        step = ReasoningTraceStep(
            step_type=ReasoningStep.INFERENCE,
            description="Make inference",
            reasoning="Based on assumptions",
            confidence=0.60,
            assumptions=["Data is accurate", "Model is trained"]
        )
        assert len(step.assumptions) == 2
    
    def test_get_confidence_level_very_low(self):
        """Test confidence level - very low."""
        step = ReasoningTraceStep(
            step_type=ReasoningStep.ANALYSIS,
            description="Test",
            reasoning="Test",
            confidence=0.15
        )
        assert step.get_confidence_level() == StepConfidence.VERY_LOW
    
    def test_get_confidence_level_low(self):
        """Test confidence level - low."""
        step = ReasoningTraceStep(
            step_type=ReasoningStep.ANALYSIS,
            description="Test",
            reasoning="Test",
            confidence=0.40
        )
        assert step.get_confidence_level() == StepConfidence.LOW
    
    def test_get_confidence_level_medium(self):
        """Test confidence level - medium."""
        step = ReasoningTraceStep(
            step_type=ReasoningStep.ANALYSIS,
            description="Test",
            reasoning="Test",
            confidence=0.60
        )
        assert step.get_confidence_level() == StepConfidence.MEDIUM
    
    def test_get_confidence_level_high(self):
        """Test confidence level - high."""
        step = ReasoningTraceStep(
            step_type=ReasoningStep.ANALYSIS,
            description="Test",
            reasoning="Test",
            confidence=0.80
        )
        assert step.get_confidence_level() == StepConfidence.HIGH
    
    def test_get_confidence_level_very_high(self):
        """Test confidence level - very high."""
        step = ReasoningTraceStep(
            step_type=ReasoningStep.ANALYSIS,
            description="Test",
            reasoning="Test",
            confidence=0.95
        )
        assert step.get_confidence_level() == StepConfidence.VERY_HIGH


class TestReasoningTrace:
    """Tests for reasoning traces."""
    
    def test_create_trace(self):
        """Test creating a reasoning trace."""
        trace = ReasoningTrace(
            trace_id="trace_1",
            task_description="Analyze sentiment"
        )
        assert trace.trace_id == "trace_1"
        assert len(trace.steps) == 0
    
    def test_add_step_to_trace(self):
        """Test adding steps to trace."""
        trace = ReasoningTrace(
            trace_id="trace_1",
            task_description="Test task"
        )
        
        trace.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Analyze",
            reasoning="Analyzed data",
            confidence=0.85,
            evidence=["evidence1"]
        )
        
        assert len(trace.steps) == 1
        assert trace.steps[0].description == "Analyze"
    
    def test_overall_confidence_calculation(self):
        """Test overall confidence calculation."""
        trace = ReasoningTrace(
            trace_id="trace_1",
            task_description="Test"
        )
        
        trace.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Step 1",
            reasoning="Reasoning 1",
            confidence=0.80
        )
        trace.add_step(
            step_type=ReasoningStep.INFERENCE,
            description="Step 2",
            reasoning="Reasoning 2",
            confidence=0.90
        )
        
        # Average should be (0.80 + 0.90) / 2 = 0.85
        assert abs(trace.overall_confidence - 0.85) < 0.01
    
    def test_set_conclusion(self):
        """Test setting trace conclusion."""
        trace = ReasoningTrace(
            trace_id="trace_1",
            task_description="Test"
        )
        
        trace.set_conclusion("This is the conclusion")
        assert trace.final_conclusion == "This is the conclusion"
    
    def test_trace_summary_empty(self):
        """Test summary for empty trace."""
        trace = ReasoningTrace(
            trace_id="trace_1",
            task_description="Test"
        )
        
        summary = trace.get_trace_summary()
        assert summary["steps"] == 0
        assert summary["overall_confidence"] == 0.0
    
    def test_trace_summary_with_steps(self):
        """Test summary with multiple steps."""
        trace = ReasoningTrace(
            trace_id="trace_1",
            task_description="Test"
        )
        
        trace.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Analyze",
            reasoning="Analysis",
            confidence=0.80
        )
        trace.add_step(
            step_type=ReasoningStep.INFERENCE,
            description="Infer",
            reasoning="Inference",
            confidence=0.90
        )
        trace.set_conclusion("Conclusion")
        
        summary = trace.get_trace_summary()
        assert summary["steps"] == 2
        assert "step_types" in summary
        assert summary["conclusion"] == "Conclusion"
    
    def test_get_overall_confidence_level(self):
        """Test getting overall confidence level."""
        trace = ReasoningTrace(
            trace_id="trace_1",
            task_description="Test"
        )
        
        trace.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Step",
            reasoning="Reasoning",
            confidence=0.85
        )
        
        level = trace._get_overall_confidence_level()
        assert level == "high"
    
    def test_count_evidence(self):
        """Test counting evidence sources."""
        trace = ReasoningTrace(
            trace_id="trace_1",
            task_description="Test"
        )
        
        trace.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Step 1",
            reasoning="Reasoning",
            confidence=0.80,
            evidence=["e1", "e2"]
        )
        trace.add_step(
            step_type=ReasoningStep.INFERENCE,
            description="Step 2",
            reasoning="Reasoning",
            confidence=0.80,
            evidence=["e3"]
        )
        
        count = trace._count_evidence()
        assert count == 3


class TestReasoningTraceValidator:
    """Tests for trace validator."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = ReasoningTraceValidator()
        assert len(validator.traces) == 0
    
    def test_create_trace(self):
        """Test creating trace via validator."""
        validator = ReasoningTraceValidator()
        trace = validator.create_trace("trace_1", "Test task")
        
        assert trace.trace_id == "trace_1"
        assert "trace_1" in validator.traces
    
    def test_validate_empty_trace(self):
        """Test validating empty trace."""
        validator = ReasoningTraceValidator()
        trace = validator.create_trace("trace_1", "Test task")
        
        result = validator.validate_trace("trace_1")
        
        assert not result["valid"]
        assert len(result["issues"]) > 0
    
    def test_validate_complete_trace(self):
        """Test validating complete trace."""
        validator = ReasoningTraceValidator()
        trace = validator.create_trace("trace_1", "Test task")
        
        trace.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Analyze",
            reasoning="Analyzed",
            confidence=0.85
        )
        trace.set_conclusion("Conclusion")
        
        result = validator.validate_trace("trace_1")
        
        assert result["valid"] or len(result["issues"]) < 3
    
    def test_validate_nonexistent_trace(self):
        """Test validating non-existent trace."""
        validator = ReasoningTraceValidator()
        result = validator.validate_trace("nonexistent")
        
        assert not result["valid"]
        assert "not found" in result["error"]
    
    def test_validate_trace_missing_confidence(self):
        """Test validation detects confidence issues."""
        validator = ReasoningTraceValidator()
        trace = validator.create_trace("trace_1", "Test task")
        
        # Create step with out-of-range confidence
        step = ReasoningTraceStep(
            step_type=ReasoningStep.ANALYSIS,
            description="Test",
            reasoning="Test",
            confidence=1.5  # Out of range
        )
        trace.steps.append(step)
        
        result = validator.validate_trace("trace_1")
        
        assert not result["valid"]
        assert any("confidence out of range" in str(issue).lower() for issue in result["issues"])


class TestExplanationGeneration:
    """Tests for trace explanation generation."""
    
    def test_get_trace_explanation(self):
        """Test generating trace explanation."""
        validator = ReasoningTraceValidator()
        trace = validator.create_trace("trace_1", "Sentiment analysis")
        
        trace.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Extract features",
            reasoning="Extracted key words",
            confidence=0.90,
            evidence=["word_freq", "polarity"]
        )
        trace.set_conclusion("Positive sentiment")
        
        explanation = validator.get_trace_explanation("trace_1")
        
        assert "Sentiment analysis" in explanation
        assert "Extract features" in explanation
        assert "Positive sentiment" in explanation
    
    def test_explanation_for_nonexistent_trace(self):
        """Test explanation for non-existent trace."""
        validator = ReasoningTraceValidator()
        explanation = validator.get_trace_explanation("nonexistent")
        
        assert explanation == ""


class TestTraceComparison:
    """Tests for trace comparison."""
    
    def test_compare_traces(self):
        """Test comparing two traces."""
        validator = ReasoningTraceValidator()
        
        trace1 = validator.create_trace("trace_1", "Task A")
        trace1.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Step 1",
            reasoning="Reasoning 1",
            confidence=0.85
        )
        trace1.set_conclusion("Conclusion A")
        
        trace2 = validator.create_trace("trace_2", "Task B")
        trace2.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Step 2",
            reasoning="Reasoning 2",
            confidence=0.90
        )
        trace2.set_conclusion("Conclusion B")
        
        comparison = validator.compare_traces("trace_1", "trace_2")
        
        assert comparison["trace1_id"] == "trace_1"
        assert comparison["trace2_id"] == "trace_2"
        assert comparison["conclusions_match"] == False
    
    def test_compare_identical_traces(self):
        """Test comparing identical traces."""
        validator = ReasoningTraceValidator()
        
        trace1 = validator.create_trace("trace_1", "Task")
        trace1.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Step",
            reasoning="Reasoning",
            confidence=0.85
        )
        trace1.set_conclusion("Same conclusion")
        
        trace2 = validator.create_trace("trace_2", "Task")
        trace2.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Step",
            reasoning="Reasoning",
            confidence=0.85
        )
        trace2.set_conclusion("Same conclusion")
        
        comparison = validator.compare_traces("trace_1", "trace_2")
        
        assert comparison["conclusions_match"] == True
        assert abs(comparison["confidence_difference"]) < 0.01


class TestTraceStatistics:
    """Tests for trace statistics."""
    
    def test_statistics_empty(self):
        """Test statistics with no traces."""
        validator = ReasoningTraceValidator()
        stats = validator.get_trace_statistics()
        
        assert stats["total_traces"] == 0
    
    def test_statistics_with_traces(self):
        """Test statistics with multiple traces."""
        validator = ReasoningTraceValidator()
        
        for i in range(3):
            trace = validator.create_trace(f"trace_{i}", f"Task {i}")
            for j in range(2):
                trace.add_step(
                    step_type=ReasoningStep.ANALYSIS,
                    description=f"Step {j}",
                    reasoning="Reasoning",
                    confidence=0.80 + (j * 0.05)
                )
        
        stats = validator.get_trace_statistics()
        
        assert stats["total_traces"] == 3
        assert stats["average_steps"] == 2.0


class TestIntegration:
    """Integration tests for reasoning traces."""
    
    def test_end_to_end_trace_workflow(self):
        """Test complete trace workflow."""
        validator = ReasoningTraceValidator()
        
        # Create trace
        trace = validator.create_trace("analysis_trace", "Analyze customer feedback")
        
        # Add reasoning steps
        trace.add_step(
            step_type=ReasoningStep.ANALYSIS,
            description="Extract sentiment keywords",
            reasoning="Identified positive and negative terms",
            confidence=0.90,
            evidence=["word_list", "polarity_scores"],
            assumptions=["Text is in English", "No slang abbreviations"]
        )
        
        trace.add_step(
            step_type=ReasoningStep.INFERENCE,
            description="Calculate overall sentiment",
            reasoning="Weighted keyword occurrences",
            confidence=0.85,
            evidence=["keyword_weights"],
            assumptions=["Weights are balanced"]
        )
        
        trace.add_step(
            step_type=ReasoningStep.VALIDATION,
            description="Validate against baseline",
            reasoning="Compared to known examples",
            confidence=0.88,
            evidence=["baseline_comparison"]
        )
        
        # Set conclusion
        trace.set_conclusion("Overall sentiment is positive with high confidence")
        
        # Validate trace
        validation = validator.validate_trace("analysis_trace")
        assert validation["valid"] or len(validation["issues"]) < 4
        
        # Get explanation
        explanation = validator.get_trace_explanation("analysis_trace")
        assert len(explanation) > 0
        
        # Get statistics
        stats = validator.get_trace_statistics()
        assert stats["total_traces"] == 1
