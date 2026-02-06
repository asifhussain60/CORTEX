"""
Unit tests for ChatResponsePolicy.

Tests 3-section structure enforcement, narration suppression,
and PROCEED directive requirement.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 specification (AC-29-F1, AC-29-F2, AC-29-F3, AC-29-F7)
"""

import pytest
from cortex.orchestrators.policies.chat_response_policy import (
    ChatResponsePolicy,
    ResponseStructureError,
    NarrationDetectedError
)


class TestChatResponsePolicyStructure:
    """Test 3-section structure validation (AC-29-F1)."""
    
    def test_three_section_structure_valid(self):
        """Valid response has exactly 3 sections."""
        policy = ChatResponsePolicy()
        
        response = """
## 🧠 CORTEX Design
**Author:** Asif Hussain | **Mode:** Design | **Scope:** Test ✅

### 1) What was asked
- Implement feature X
- Follow TDD approach

### 2) What's recommended and why
- Use adapter pattern for extensibility
- Start with JSON implementation

### 3) Next steps
**Next Step:** PROCEED
"""
        
        is_valid, errors = policy.validate_response_structure(response)
        assert is_valid
        assert len(errors) == 0
    
    def test_three_section_structure_invalid_too_few(self):
        """Response with <3 sections is rejected."""
        policy = ChatResponsePolicy()
        
        response = """
## 🧠 CORTEX Design
**Author:** Asif Hussain

### 1) What was asked
- Something

### 2) What's recommended
- Something else
"""
        
        is_valid, errors = policy.validate_response_structure(response)
        assert not is_valid
        assert "exactly 3 sections" in errors[0].lower()
    
    def test_three_section_structure_invalid_too_many(self):
        """Response with >3 sections is rejected."""
        policy = ChatResponsePolicy()
        
        response = """
## 🧠 CORTEX Design

### 1) First
- Content

### 2) Second
- Content

### 3) Third
- Content

### 4) Fourth
- Content
"""
        
        is_valid, errors = policy.validate_response_structure(response)
        assert not is_valid
        assert "exactly 3 sections" in errors[0].lower()
    
    def test_response_header_mandatory(self):
        """Response must have CORE-029 compliant header (AC-29-F7)."""
        policy = ChatResponsePolicy()
        
        response_no_header = """
### 1) What was asked
- Test

### 2) Recommendation
- Test

### 3) Next
- PROCEED
"""
        
        is_valid, errors = policy.validate_response_structure(response_no_header)
        assert not is_valid
        assert "header" in errors[0].lower()
    
    def test_section_naming_flexible(self):
        """Section names can vary but count must be 3."""
        policy = ChatResponsePolicy()
        
        response = """
## 🧠 CORTEX
**Author:** Asif Hussain

### What you asked for
- Feature X

### Our recommendation
- Approach Y

### What happens next
- PROCEED
"""
        
        is_valid, errors = policy.validate_response_structure(response)
        assert is_valid


class TestChatResponsePolicyNarration:
    """Test tool narration suppression (AC-29-F2)."""
    
    def test_tool_narration_blocked(self):
        """Common narration phrases are detected and blocked."""
        policy = ChatResponsePolicy()
        
        blocked_phrases = [
            "Let me read the file",
            "Perfect! Now let's",
            "Great! I can see",
            "Looking at the code",
            "I'll search for",
            "Let me check if",
            "I notice that",
            "After reviewing",
        ]
        
        for phrase in blocked_phrases:
            has_narration = policy.contains_tool_narration(phrase)
            assert has_narration, f"Failed to detect: {phrase}"
    
    def test_technical_content_allowed(self):
        """Technical descriptions without narration are allowed."""
        policy = ChatResponsePolicy()
        
        allowed_content = [
            "The adapter pattern provides extensibility",
            "JSON load time is <10ms",
            "Tests pass with 100% coverage",
            "Type hints enforce contract",
        ]
        
        for content in allowed_content:
            has_narration = policy.contains_tool_narration(content)
            assert not has_narration, f"False positive: {content}"
    
    def test_suppress_narration_removes_phrases(self):
        """Narration phrases are removed from response."""
        policy = ChatResponsePolicy()
        
        response_with_narration = """
Let me read the implementation.

Perfect! The code shows JSON adapter with <10ms load time.

Great! I can see 14 tests passing.
"""
        
        cleaned = policy.suppress_narration(response_with_narration)
        
        assert "Let me read" not in cleaned
        assert "Perfect!" not in cleaned
        assert "Great!" not in cleaned
        assert "JSON adapter with <10ms load time" in cleaned
        assert "14 tests passing" in cleaned


class TestChatResponsePolicyProceed:
    """Test PROCEED directive enforcement (AC-29-F3)."""
    
    def test_proceed_directive_forced(self):
        """Response ends with 'Next Step: PROCEED' only."""
        policy = ChatResponsePolicy()
        
        response = """
## 🧠 CORTEX

### 1) Request
- Feature

### 2) Recommendation  
- Approach

### 3) Next
Some content here.
"""
        
        enforced = policy.enforce_proceed_directive(response)
        
        assert "**Next Step:** PROCEED" in enforced
        assert "Option 1" not in enforced
        assert "Option 2" not in enforced
    
    def test_preference_questions_removed(self):
        """'Which approach do you prefer?' questions are removed."""
        policy = ChatResponsePolicy()
        
        response = """
### 3) Next steps

Which approach do you prefer?

1️⃣ **Option 1:** Approach A
2️⃣ **Option 2:** Approach B
3️⃣ **Option 3:** Approach C

Please select your preferred option.
"""
        
        cleaned = policy.enforce_proceed_directive(response)
        
        assert "Which approach do you prefer?" not in cleaned
        assert "Option 1" not in cleaned
        assert "Option 2" not in cleaned
        assert "Please select" not in cleaned
        assert "**Next Step:** PROCEED" in cleaned
    
    def test_existing_proceed_preserved(self):
        """If response already has PROCEED, don't duplicate."""
        policy = ChatResponsePolicy()
        
        response = """
### 3) Next steps

**Next Step:** PROCEED
"""
        
        enforced = policy.enforce_proceed_directive(response)
        
        # Count occurrences - should be exactly 1
        proceed_count = enforced.count("**Next Step:** PROCEED")
        assert proceed_count == 1


class TestChatResponsePolicyConfiguration:
    """Test policy configuration and edge cases."""
    
    def test_policy_initializes_with_defaults(self):
        """Policy can be created with default settings."""
        policy = ChatResponsePolicy()
        
        assert policy.required_section_count == 3
        assert policy.suppress_narration_enabled is True
        assert policy.enforce_proceed_enabled is True
    
    def test_policy_configurable(self):
        """Policy settings can be customized."""
        policy = ChatResponsePolicy(
            required_section_count=4,
            suppress_narration_enabled=False
        )
        
        assert policy.required_section_count == 4
        assert policy.suppress_narration_enabled is False
    
    def test_empty_response_handled(self):
        """Empty response is rejected gracefully."""
        policy = ChatResponsePolicy()
        
        is_valid, errors = policy.validate_response_structure("")
        
        assert not is_valid
        assert len(errors) > 0


class TestChatResponsePolicyIntegration:
    """Integration tests for full policy application."""
    
    def test_apply_all_policies(self):
        """Apply all policies in sequence."""
        policy = ChatResponsePolicy()
        
        response_raw = """
Let me read the specification.

Perfect! The spec shows 3 phases.

### 1) What was asked
- Implement Phase 29

### 2) Recommendation
- Use ChatResponsePolicy

Great! This will work well.

### 3) Next steps

Which approach do you prefer?

1️⃣ Option A
2️⃣ Option B
"""
        
        # Apply all policies
        response_final = policy.apply(response_raw)
        
        # Verify structure (can't validate without header, just check suppression works)
        assert "Let me read" not in response_final
        assert "Perfect!" not in response_final
        assert "Great!" not in response_final
        assert "Which approach do you prefer?" not in response_final
        assert "Option A" not in response_final
        assert "**Next Step:** PROCEED" in response_final


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
