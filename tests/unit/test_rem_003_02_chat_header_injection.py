"""
Test for AC-REM-003-02: Chat Header Injection Wrapper

This test verifies that ChatResponseFormatter properly injects response headers
and maintains JSON parseability while adding CORTEX metadata.

Issue: ISSUE-003 (Response Verbosity & Header Injection)
AC-ID: AC-REM-003-02
Priority: HIGH
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any


class TestChatResponseFormatter:
    """Test suite for ChatResponseFormatter class."""
    
    @pytest.fixture
    def formatter(self):
        """Create ChatResponseFormatter instance for tests."""
        # Import will fail initially (RED state) - that's expected
        try:
            from cortex.api.chat_response_formatter import ChatResponseFormatter
            return ChatResponseFormatter()
        except ImportError:
            pytest.skip("ChatResponseFormatter not yet implemented")
    
    def test_formatter_class_exists(self):
        """Verify ChatResponseFormatter class exists."""
        try:
            from cortex.api.chat_response_formatter import ChatResponseFormatter
            assert ChatResponseFormatter is not None
        except ImportError as e:
            pytest.fail(f"ChatResponseFormatter class not found: {e}")
    
    def test_formatter_has_format_response_method(self, formatter):
        """Verify formatter has format_response method."""
        assert hasattr(formatter, 'format_response'), \
            "ChatResponseFormatter must have format_response method"
        assert callable(getattr(formatter, 'format_response')), \
            "format_response must be callable"
    
    def test_format_response_returns_dict(self, formatter):
        """Verify format_response returns a dictionary."""
        response = formatter.format_response(
            content="Test response",
            operation="TEST_OP",
            phase="PHASE-16",
            orchestrator="MasterOrchestrator"
        )
        assert isinstance(response, dict), "format_response must return dict"
    
    def test_response_contains_required_headers(self, formatter):
        """Verify response contains all required header fields."""
        response = formatter.format_response(
            content="Test response",
            operation="TEST_OP",
            phase="PHASE-16",
            orchestrator="MasterOrchestrator"
        )
        
        required_fields = ['operation', 'phase', 'orchestrator', 'author', 'content', 'copyright']
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"
    
    def test_response_headers_populated_correctly(self, formatter):
        """Verify header values are populated correctly."""
        test_operation = "IMPLEMENTATION"
        test_phase = "PHASE-15"
        test_orchestrator = "PlanningOrchestrator"
        test_content = "This is test content"
        
        response = formatter.format_response(
            content=test_content,
            operation=test_operation,
            phase=test_phase,
            orchestrator=test_orchestrator
        )
        
        assert response['operation'] == test_operation
        assert response['phase'] == test_phase
        assert response['orchestrator'] == test_orchestrator
        assert response['content'] == test_content
        assert response['author'] == "Asif Hussain"
    
    def test_response_includes_copyright_notice(self, formatter):
        """Verify copyright notice is included in response."""
        response = formatter.format_response(
            content="Test",
            operation="TEST",
            phase="PHASE-16",
            orchestrator="TestOrch"
        )
        
        assert 'copyright' in response
        assert "Copyright © 2025-2026 Asif Hussain" in response['copyright']
    
    def test_response_is_json_serializable(self, formatter):
        """Verify response can be serialized to JSON."""
        response = formatter.format_response(
            content="Test response",
            operation="TEST_OP",
            phase="PHASE-16",
            orchestrator="MasterOrchestrator"
        )
        
        try:
            json_str = json.dumps(response)
            assert isinstance(json_str, str)
            # Verify it can be parsed back
            parsed = json.loads(json_str)
            assert parsed == response
        except (TypeError, ValueError) as e:
            pytest.fail(f"Response not JSON serializable: {e}")
    
    def test_formatter_handles_special_characters(self, formatter):
        """Verify formatter handles special characters in content."""
        special_content = 'Test with "quotes", \\backslash, \nnewline'
        response = formatter.format_response(
            content=special_content,
            operation="TEST",
            phase="PHASE-16",
            orchestrator="Test"
        )
        
        # Should be JSON serializable
        json_str = json.dumps(response)
        parsed = json.loads(json_str)
        assert parsed['content'] == special_content
    
    def test_formatter_wraps_plain_text_response(self, formatter):
        """Verify formatter can wrap plain text responses."""
        plain_text = "This is a plain text response without formatting"
        response = formatter.format_response(
            content=plain_text,
            operation="CODE_REVIEW",
            phase="PHASE-16",
            orchestrator="Interaction"
        )
        
        assert response['content'] == plain_text
        assert response['operation'] == "CODE_REVIEW"
    
    def test_formatter_preserves_markdown_content(self, formatter):
        """Verify formatter preserves markdown content."""
        markdown_content = """
## Section 1
- Bullet point 1
- Bullet point 2

### Subsection
```python
code_example = True
```
"""
        response = formatter.format_response(
            content=markdown_content,
            operation="ANALYSIS",
            phase="PHASE-16",
            orchestrator="Master"
        )
        
        assert response['content'] == markdown_content
    
    def test_formatter_maintains_timestamp(self, formatter):
        """Verify formatter includes timestamp."""
        response = formatter.format_response(
            content="Test",
            operation="TEST",
            phase="PHASE-16",
            orchestrator="Test"
        )
        
        # Should have a timestamp field
        assert 'timestamp' in response or 'created_at' in response, \
            "Response should include timestamp"
    
    def test_multiple_format_calls_independent(self, formatter):
        """Verify multiple format calls don't interfere with each other."""
        response1 = formatter.format_response(
            content="First response",
            operation="OP1",
            phase="PHASE-15",
            orchestrator="Orch1"
        )
        
        response2 = formatter.format_response(
            content="Second response",
            operation="OP2",
            phase="PHASE-16",
            orchestrator="Orch2"
        )
        
        # Verify they don't cross-contaminate
        assert response1['operation'] == "OP1"
        assert response2['operation'] == "OP2"
        assert response1['content'] != response2['content']
        assert response1['phase'] == "PHASE-15"
        assert response2['phase'] == "PHASE-16"


class TestChatResponseFormatterIntegration:
    """Integration tests for ChatResponseFormatter."""
    
    @pytest.fixture
    def formatter(self):
        """Create formatter instance."""
        try:
            from cortex.api.chat_response_formatter import ChatResponseFormatter
            return ChatResponseFormatter()
        except ImportError:
            pytest.skip("ChatResponseFormatter not yet implemented")
    
    def test_formatter_with_typical_cortex_response(self, formatter):
        """Test formatter with typical CORTEX response pattern."""
        cortex_response = """
### Implementation Result

✓ AC-REM-003-02 COMPLETED

Changes made:
1. Created ChatResponseFormatter class
2. Added header injection
3. Verified JSON compatibility

Tests: 16/16 PASSED
Compliance: CORE-024 ✓
"""
        response = formatter.format_response(
            content=cortex_response,
            operation="IMPLEMENTATION",
            phase="PHASE-REMEDIATION-01",
            orchestrator="MasterOrchestrator"
        )
        
        # Should be valid and complete
        assert response is not None
        assert json.dumps(response)  # Should be serializable
    
    def test_formatter_output_format_for_chat_api(self, formatter):
        """Verify output format is suitable for chat APIs."""
        response = formatter.format_response(
            content="Test response",
            operation="TEST",
            phase="PHASE-16",
            orchestrator="Test"
        )
        
        # Should have the structure expected by chat APIs
        assert 'content' in response
        assert isinstance(response['content'], str)
        
        # Headers should be present for logging/audit
        assert 'operation' in response
        assert 'phase' in response
        assert 'orchestrator' in response
        assert 'author' in response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
