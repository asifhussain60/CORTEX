"""
Unit tests for Response Format Validator.

Tests advanced response format validation including status icons,
linear narrative flow, markdown structure, and compliance checking.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 Stage 1 specification
"""

import pytest
from typing import List, Dict, Any

from cortex.brain.core.response_format_validator import (
    ResponseFormatValidator,
    FormatViolation,
    ViolationSeverity,
    StatusIcon,
    ValidationResult,
    FormatError,
)


class TestStatusIcon:
    """Test status icon enum and validation."""
    
    def test_status_icon_types_defined(self):
        """Test all status icon types are defined."""
        assert hasattr(StatusIcon, "COMPLETED")  # 🟢
        assert hasattr(StatusIcon, "IN_PROGRESS")  # 🔵
        assert hasattr(StatusIcon, "PLANNED")  # ⚪
        assert hasattr(StatusIcon, "WARNING")  # 🟡
        assert hasattr(StatusIcon, "CRITICAL")  # 🔴
        assert hasattr(StatusIcon, "SUCCESS")  # ✅
        assert hasattr(StatusIcon, "FAILED")  # ❌
        assert hasattr(StatusIcon, "ATTENTION")  # ⚠️
    
    def test_status_icon_values(self):
        """Test status icon emoji values."""
        assert StatusIcon.COMPLETED.value == "🟢"
        assert StatusIcon.IN_PROGRESS.value == "🔵"
        assert StatusIcon.PLANNED.value == "⚪"
        assert StatusIcon.WARNING.value == "🟡"
        assert StatusIcon.CRITICAL.value == "🔴"


class TestFormatViolation:
    """Test format violation dataclass."""
    
    def test_violation_creation(self):
        """Test FormatViolation creation."""
        violation = FormatViolation(
            severity=ViolationSeverity.ERROR,
            message="Missing response header",
            location="line 1",
            rule_id="FMT-001",
        )
        
        assert violation.severity == ViolationSeverity.ERROR
        assert violation.message == "Missing response header"
        assert violation.rule_id == "FMT-001"
    
    def test_violation_severity_levels(self):
        """Test violation severity enum."""
        assert hasattr(ViolationSeverity, "ERROR")
        assert hasattr(ViolationSeverity, "WARNING")
        assert hasattr(ViolationSeverity, "INFO")


class TestValidationResult:
    """Test validation result dataclass."""
    
    def test_validation_result_pass(self):
        """Test passing validation result."""
        result = ValidationResult(
            is_valid=True,
            violations=[],
            score=1.0,
            suggestions=[],
        )
        
        assert result.is_valid is True
        assert len(result.violations) == 0
        assert result.score == 1.0
    
    def test_validation_result_fail(self):
        """Test failing validation result."""
        violation = FormatViolation(
            ViolationSeverity.ERROR,
            "Invalid format",
            "line 10",
            "FMT-002",
        )
        
        result = ValidationResult(
            is_valid=False,
            violations=[violation],
            score=0.6,
            suggestions=["Add proper header"],
        )
        
        assert result.is_valid is False
        assert len(result.violations) == 1
        assert result.score < 1.0


class TestResponseFormatValidator:
    """Test response format validator core functionality."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return ResponseFormatValidator()
    
    def test_validator_initialization(self, validator):
        """Test validator initializes properly."""
        assert validator is not None
    
    def test_validate_response_header(self, validator):
        """Test response header validation."""
        # Valid header
        valid_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Content here."""
        
        result = validator.validate(valid_response)
        assert result.is_valid is True
        
        # Invalid header
        invalid_response = """Just some content without header."""
        
        result = validator.validate(invalid_response)
        assert result.is_valid is False
        assert any("header" in v.message.lower() for v in result.violations)
    
    def test_validate_status_icons(self, validator):
        """Test status icon validation."""
        # Correct usage: ✅ for completed work
        correct_usage = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

✅ Implementation complete
🟢 All tests passing"""
        
        result = validator.validate_status_icons(correct_usage)
        assert len(result.violations) == 0
        
        # Incorrect: ✅ for planned work
        incorrect_usage = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

✅ Will implement later
✅ Planning to add tests"""
        
        result = validator.validate_status_icons(incorrect_usage)
        # Should have warnings about misuse
        assert len(result.violations) > 0 or len(result.suggestions) > 0
    
    def test_validate_linear_narrative_flow(self, validator):
        """Test linear narrative flow validation."""
        # Good: Context → Analysis → Action → Result
        good_flow = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

### Context
User requested feature implementation.

### Analysis
Analyzed requirements and dependencies.

### Action
Implemented feature with TDD.

### Result
All 25 tests passing."""
        
        result = validator.validate_narrative_flow(good_flow)
        assert len(result.violations) == 0
        
        # Bad: Repetitive sections
        bad_flow = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Implementation details...

### Next Steps
- Will do X

More content...

### Next Steps
- Will do Y"""
        
        result = validator.validate_narrative_flow(bad_flow)
        # Should detect repetition
        assert len(result.violations) > 0
    
    def test_validate_numbered_prompts(self, validator):
        """Test numbered prompt validation."""
        # Bad: Numbers after completion
        bad_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

✅ Implementation Complete

1️⃣ What would you like to do next?
2️⃣ Run more tests?"""
        
        result = validator.validate_numbered_prompts(bad_response)
        # Should flag inappropriate numbering
        assert len(result.violations) > 0
        
        # Good: Numbers only for decision points
        good_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

### Decision Required

1️⃣ Proceed with option A
2️⃣ Proceed with option B"""
        
        result = validator.validate_numbered_prompts(good_response)
        # Should be acceptable
        assert result.is_valid is True
    
    def test_validate_exit_options(self, validator):
        """Test exit option detection during holistic implementation."""
        # Bad: Exit options during active implementation
        bad_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

🔵 Implementing Stage 2...

Would you like to:
1. Continue
2. Exit
3. Pause"""
        
        result = validator.validate_exit_options(bad_response)
        # Should flag exit options during implementation
        assert len(result.violations) > 0
        
        # Good: No exit options during holistic implementation
        good_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

🔵 Implementing Stage 2...

Continuing with implementation."""
        
        result = validator.validate_exit_options(good_response)
        assert len(result.violations) == 0


class TestMarkdownStructure:
    """Test markdown structure validation."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return ResponseFormatValidator()
    
    def test_validate_header_hierarchy(self, validator):
        """Test header hierarchy validation."""
        # Good: Proper hierarchy
        good_structure = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

### Stage 1
#### Details
Content here."""
        
        result = validator.validate_markdown_structure(good_structure)
        assert result.is_valid is True
        
        # Bad: Skipped levels
        bad_structure = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

##### Skipped levels"""
        
        result = validator.validate_markdown_structure(bad_structure)
        # Should warn about skipped levels
        assert len(result.violations) > 0 or len(result.suggestions) > 0
    
    def test_validate_table_structure(self, validator):
        """Test table structure validation."""
        # Good table
        good_table = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

| Stage | Status |
|-------|--------|
| 1     | ✅     |
| 2     | 🔵     |"""
        
        result = validator.validate_markdown_structure(good_table)
        assert result.is_valid is True
    
    def test_validate_code_blocks(self, validator):
        """Test code block validation."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

```python
def example():
    pass
```"""
        
        result = validator.validate_markdown_structure(response)
        assert result.is_valid is True


class TestCompletionIndicators:
    """Test completion indicator validation."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return ResponseFormatValidator()
    
    def test_detect_completion_vs_next_steps(self, validator):
        """Test completion indicator vs next steps."""
        # Good: Shows completion
        completion_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

✅ Implementation Complete

All 25 tests passing."""
        
        result = validator.validate_completion_indicators(completion_response)
        assert result.is_valid is True
        
        # Bad: Says complete but lists next steps
        confused_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

✅ Implementation Complete

### Next Steps
- Need to implement feature X
- Need to add tests"""
        
        result = validator.validate_completion_indicators(confused_response)
        # Should flag contradiction
        assert len(result.violations) > 0
    
    def test_validate_misleading_checkmarks(self, validator):
        """Test detection of misleading checkmarks."""
        # Bad: ✅ for future work
        misleading = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

✅ Will implement tomorrow
✅ Planning to add tests"""
        
        result = validator.validate_completion_indicators(misleading)
        # Should flag misleading usage
        assert len(result.violations) > 0


class TestRepetitionDetection:
    """Test repetition detection."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return ResponseFormatValidator()
    
    def test_detect_repeated_sections(self, validator):
        """Test detection of repeated content."""
        repetitive = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Implementation details here.

Implementation details here.

Implementation details here."""
        
        result = validator.detect_repetition(repetitive)
        assert len(result.violations) > 0
    
    def test_detect_redundant_explanations(self, validator):
        """Test detection of redundant explanations."""
        redundant = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Created file X successfully.
Created file X successfully.
Created file X successfully."""
        
        result = validator.detect_repetition(redundant)
        # Should detect duplicate lines
        assert len(result.violations) > 0


class TestFormatScoring:
    """Test format quality scoring."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return ResponseFormatValidator()
    
    def test_perfect_score(self, validator):
        """Test perfect format score."""
        perfect_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

### Context
User requested feature implementation.

### Implementation
Implemented with TDD approach.

### Result
✅ All 25 tests passing."""
        
        result = validator.validate(perfect_response)
        assert result.score >= 0.9
    
    def test_score_degradation(self, validator):
        """Test score decreases with violations."""
        poor_response = """Some content without header.
✅ Will do later.
Next Steps
Next Steps"""
        
        result = validator.validate(poor_response)
        assert result.score < 0.7


class TestFormatErrorHandling:
    """Test format error handling."""
    
    def test_format_error_inheritance(self):
        """Test FormatError inherits from Exception."""
        error = FormatError("test error")
        assert isinstance(error, Exception)
    
    def test_handles_invalid_input(self):
        """Test handling of invalid input."""
        validator = ResponseFormatValidator()
        
        # None input
        result = validator.validate(None)
        assert result.is_valid is False
        
        # Empty input
        result = validator.validate("")
        assert result.is_valid is False
