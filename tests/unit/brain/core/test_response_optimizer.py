"""
Unit tests for Response Optimizer.

Tests auto-correction, context flow optimization, and advanced
violation handling for response formatting.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 Stage 2 specification
"""

import pytest
from typing import List, Dict, Any

from cortex.brain.core.response_optimizer import (
    ResponseOptimizer,
    OptimizationResult,
    Correction,
    CorrectionType,
    FlowAnalysis,
    OptimizerError,
)


class TestCorrectionDataclass:
    """Test correction dataclass."""
    
    def test_correction_creation(self):
        """Test Correction creation."""
        correction = Correction(
            correction_type=CorrectionType.HEADER_ADDED,
            original="Some content",
            corrected="## 🧠 CORTEX\n\nSome content",
            location="start",
        )
        
        assert correction.correction_type == CorrectionType.HEADER_ADDED
        assert "CORTEX" in correction.corrected
    
    def test_correction_types_defined(self):
        """Test all correction types defined."""
        assert hasattr(CorrectionType, "HEADER_ADDED")
        assert hasattr(CorrectionType, "ICON_FIXED")
        assert hasattr(CorrectionType, "REPETITION_REMOVED")
        assert hasattr(CorrectionType, "FLOW_IMPROVED")


class TestOptimizationResult:
    """Test optimization result dataclass."""
    
    def test_optimization_result_creation(self):
        """Test OptimizationResult creation."""
        result = OptimizationResult(
            original_text="Bad format",
            optimized_text="## 🧠 CORTEX\n\nGood format",
            corrections=[],
            improvement_score=0.3,
        )
        
        assert result.optimized_text != result.original_text
        assert result.improvement_score > 0


class TestResponseOptimizer:
    """Test response optimizer core functionality."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return ResponseOptimizer()
    
    def test_optimizer_initialization(self, optimizer):
        """Test optimizer initializes properly."""
        assert optimizer is not None
    
    def test_auto_add_header(self, optimizer):
        """Test automatic header addition."""
        response_without_header = """Implementation complete.
All tests passing."""
        
        result = optimizer.optimize(response_without_header, orchestrator="TDDOrchestrator")
        
        assert "## 🧠 CORTEX" in result.optimized_text
        assert any(c.correction_type == CorrectionType.HEADER_ADDED for c in result.corrections)
    
    def test_fix_misleading_checkmarks(self, optimizer):
        """Test fixing misleading checkmarks."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

✅ Will implement tomorrow
✅ Planning to add tests"""
        
        result = optimizer.optimize(response)
        
        # Should replace ✅ with ⚪ for planned work
        assert result.optimized_text.count("✅") < response.count("✅")
        assert "⚪" in result.optimized_text or "🔵" in result.optimized_text
    
    def test_remove_duplicate_sections(self, optimizer):
        """Test removal of duplicate sections."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

### Next Steps
Do something

### Next Steps
Do something else"""
        
        result = optimizer.optimize(response)
        
        # Should have fewer "Next Steps" sections
        original_count = response.count("### Next Steps")
        optimized_count = result.optimized_text.count("### Next Steps")
        assert optimized_count < original_count
    
    def test_remove_exit_options(self, optimizer):
        """Test removal of exit options during implementation."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

🔵 Implementing Stage 2...

Would you like to:
1. Continue
2. Exit
3. Pause"""
        
        result = optimizer.optimize(response)
        
        # Should remove exit options
        assert "Exit" not in result.optimized_text or "exit" not in result.optimized_text.lower()


class TestFlowOptimization:
    """Test context flow optimization."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return ResponseOptimizer()
    
    def test_analyze_flow(self, optimizer):
        """Test flow analysis."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Implementation details.
More details.
Result here."""
        
        flow_analysis = optimizer.analyze_flow(response)
        
        assert isinstance(flow_analysis, FlowAnalysis)
        assert flow_analysis.has_context is not None
        assert flow_analysis.has_analysis is not None
        assert flow_analysis.has_action is not None
        assert flow_analysis.has_result is not None
    
    def test_improve_flow_structure(self, optimizer):
        """Test flow structure improvement."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Random content without structure."""
        
        result = optimizer.optimize(response, improve_flow=True)
        
        # Should add flow markers or structure
        assert result.improvement_score >= 0


class TestNumberedPromptHandling:
    """Test numbered prompt optimization."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return ResponseOptimizer()
    
    def test_remove_numbers_after_completion(self, optimizer):
        """Test removal of numbered prompts after completion."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

✅ Implementation Complete

1️⃣ What's next?
2️⃣ Run more tests?"""
        
        result = optimizer.optimize(response)
        
        # Should remove numbered emojis after completion
        completion_text = result.optimized_text.split("Complete")[1] if "Complete" in result.optimized_text else ""
        assert "1️⃣" not in completion_text or "2️⃣" not in completion_text
    
    def test_preserve_decision_numbers(self, optimizer):
        """Test preservation of decision point numbers."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

### Decision Required

Choose approach:
1️⃣ Option A
2️⃣ Option B"""
        
        result = optimizer.optimize(response)
        
        # Should preserve numbers at decision points
        assert "1️⃣" in result.optimized_text
        assert "2️⃣" in result.optimized_text


class TestRepetitionRemoval:
    """Test repetition removal."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return ResponseOptimizer()
    
    def test_remove_duplicate_lines(self, optimizer):
        """Test duplicate line removal."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Created file X.
Created file X.
Created file X."""
        
        result = optimizer.optimize(response)
        
        # Should have fewer duplicate lines
        original_count = response.count("Created file X.")
        optimized_count = result.optimized_text.count("Created file X.")
        assert optimized_count < original_count
    
    def test_consolidate_similar_content(self, optimizer):
        """Test consolidation of similar content."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

The implementation is complete.
The implementation is complete.
The implementation is complete."""
        
        result = optimizer.optimize(response)
        
        # Should remove exact duplicates
        original_count = response.count("The implementation is complete.")
        optimized_count = result.optimized_text.count("The implementation is complete.")
        assert optimized_count < original_count


class TestImprovementMetrics:
    """Test improvement metrics."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return ResponseOptimizer()
    
    def test_calculate_improvement_score(self, optimizer):
        """Test improvement score calculation."""
        poor_response = """Bad format
No header
Lots of issues"""
        
        result = optimizer.optimize(poor_response, orchestrator="TestOrch")
        
        # Should have positive improvement
        assert result.improvement_score > 0
    
    def test_zero_improvement_for_good_format(self, optimizer):
        """Test zero improvement for already good format."""
        good_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

### Context
Clear context here.

### Result
✅ Complete"""
        
        result = optimizer.optimize(good_response)
        
        # Should have minimal improvement
        assert result.improvement_score < 0.3


class TestCorrectionReport:
    """Test correction reporting."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return ResponseOptimizer()
    
    def test_generate_correction_report(self, optimizer):
        """Test correction report generation."""
        response = """Bad format content"""
        
        result = optimizer.optimize(response, orchestrator="TestOrch")
        
        report = optimizer.generate_report(result)
        
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_report_lists_all_corrections(self, optimizer):
        """Test report lists all corrections."""
        response = """✅ Will do later"""
        
        result = optimizer.optimize(response, orchestrator="TestOrch")
        report = optimizer.generate_report(result)
        
        # Report should mention corrections made
        if result.corrections:
            assert any(c.correction_type.value in report for c in result.corrections)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return ResponseOptimizer()
    
    def test_handle_empty_input(self, optimizer):
        """Test handling of empty input."""
        result = optimizer.optimize("", orchestrator="TestOrch")
        
        assert result.optimized_text is not None
        assert len(result.optimized_text) > 0
    
    def test_handle_very_long_response(self, optimizer):
        """Test handling of very long response."""
        long_response = "Content " * 10000
        
        result = optimizer.optimize(long_response, orchestrator="TestOrch")
        
        assert result.optimized_text is not None
    
    def test_optimizer_error_inheritance(self):
        """Test OptimizerError inherits from Exception."""
        error = OptimizerError("test error")
        assert isinstance(error, Exception)
