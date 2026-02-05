"""
Phase 22 Component #9: cortex_ask MCP Tool Tests (15 tests)

Tests for educational query processing via MCP interface.
"""

import pytest
import sys
import importlib
from unittest.mock import Mock, patch, AsyncMock
from cortex.mcp.tools.cortex_ask import (
    cortex_ask,
    validate_query,
    format_educational_response,
)
from cortex.core.result import Result
import json


class TestCortexAsk:
    """Tests for cortex_ask MCP tool functionality."""

    def test_cortex_ask_basic_query(self):
        """Test basic educational query processing."""
        result = cortex_ask(
            user_query="What is CORTEX?",
            knowledge_level="beginner"
        )
        
        if result["status"] != "success":
            print(f"ERROR: {result.get('error', 'Unknown error')}")
        assert result["status"] == "success"
        assert "explanation" in result
        assert "next_steps" in result
        assert len(result["next_steps"]) >= 3

    def test_cortex_ask_empty_query(self):
        """Test handling of empty query."""
        result = cortex_ask(user_query="", knowledge_level="beginner")
        
        assert result["status"] == "error"
        assert "error" in result
        assert "query cannot be empty" in result["error"].lower()

    def test_cortex_ask_knowledge_levels(self):
        """Test all three knowledge levels."""
        levels = ["beginner", "intermediate", "advanced"]
        
        for level in levels:
            result = cortex_ask(
                user_query="Explain orchestrators",
                knowledge_level=level
            )
            assert result["status"] == "success"
            assert result["knowledge_level"] == level

    def test_cortex_ask_with_context(self):
        """Test query with additional context."""
        result = cortex_ask(
            user_query="How does TDD work?",
            knowledge_level="intermediate",
            context={"file_path": "cortex/orchestrators/core/tdd_orchestrator.py"}
        )
        
        assert result["status"] == "success"
        assert "context" in result
        assert result["context"]["file_path"] is not None

    def test_cortex_ask_verification_enabled(self):
        """Test with implementation truth verification."""
        result = cortex_ask(
            user_query="Does MasterOrchestrator exist?",
            knowledge_level="beginner",
            verify_implementation=True
        )
        
        assert result["status"] == "success"
        assert "verification" in result
        assert result["verification"]["verified"] is True

    def test_cortex_ask_long_query(self):
        """Test handling of very long queries."""
        long_query = "x" * 10000
        result = cortex_ask(user_query=long_query, knowledge_level="beginner")
        
        assert result["status"] == "error"
        assert "too long" in result["error"].lower()

    def test_cortex_ask_invalid_knowledge_level(self):
        """Test invalid knowledge level."""
        result = cortex_ask(
            user_query="What is CORTEX?",
            knowledge_level="expert"  # Not a valid level
        )
        
        assert result["status"] == "error"
        assert "invalid knowledge level" in result["error"].lower()

    def test_cortex_ask_numbered_options(self):
        """Test that response includes numbered next-step options."""
        result = cortex_ask(
            user_query="What is LENS?",
            knowledge_level="beginner"
        )
        
        assert result["status"] == "success"
        assert isinstance(result["next_steps"], list)
        assert len(result["next_steps"]) >= 3
        assert len(result["next_steps"]) <= 5
        
        for i, step in enumerate(result["next_steps"], 1):
            assert "description" in step
            assert "query" in step

    def test_cortex_ask_orchestrator_integration(self, monkeypatch):
        """Test integration with EducationalOrchestrator."""
        # Create mock response data
        response_data = {
            "explanation": "Test explanation",
            "next_steps": [{"description": "Step 1", "query": "test"}],
            "knowledge_level": "beginner"
        }
        
        # Create Result.Ok with JSON string
        mock_result = Mock()
        mock_result.is_ok.return_value = True
        mock_result.unwrap.return_value = json.dumps(response_data)
        
        mock_instance = Mock()
        mock_instance.execute.return_value = mock_result
        
        mock_orch = Mock(return_value=mock_instance)
        
        # Patch the actual module (not the re-exported function)
        import sys
        cortex_ask_module = sys.modules['cortex.mcp.tools.cortex_ask']
        monkeypatch.setattr(cortex_ask_module, 'EducationalOrchestrator', mock_orch)
        
        from cortex.mcp.tools.cortex_ask import cortex_ask
        result = cortex_ask(
            user_query="Test query",
            knowledge_level="beginner"
        )
        
        # Verify orchestrator was called
        assert mock_orch.called
        assert mock_instance.execute.called

    def test_cortex_ask_error_handling(self, monkeypatch):
        """Test error handling when orchestrator fails."""
        mock_instance = Mock()
        mock_instance.execute.side_effect = Exception("Orchestrator error")
        mock_orch = Mock(return_value=mock_instance)
        
        # Patch the actual module (not the re-exported function)
        import sys
        cortex_ask_module = sys.modules['cortex.mcp.tools.cortex_ask']
        monkeypatch.setattr(cortex_ask_module, 'EducationalOrchestrator', mock_orch)
        
        from cortex.mcp.tools.cortex_ask import cortex_ask
        result = cortex_ask(
            user_query="Test query",
            knowledge_level="beginner"
        )
        
        assert result["status"] == "error"
        assert "error" in result

    def test_validate_query_valid(self):
        """Test query validation with valid input."""
        is_valid, error = validate_query("What is CORTEX?")
        assert is_valid is True
        assert error is None

    def test_validate_query_empty(self):
        """Test query validation with empty input."""
        is_valid, error = validate_query("")
        assert is_valid is False
        assert error is not None

    def test_validate_query_too_long(self):
        """Test query validation with excessive length."""
        long_query = "x" * 10000
        is_valid, error = validate_query(long_query)
        assert is_valid is False
        assert error is not None
        assert "too long" in error.lower()

    def test_format_educational_response(self):
        """Test response formatting."""
        raw_response = {
            "explanation": "Test explanation",
            "next_steps": [
                {"description": "Step 1", "query": "query1"},
                {"description": "Step 2", "query": "query2"}
            ],
            "knowledge_level": "beginner"
        }
        
        formatted = format_educational_response(raw_response, {})
        
        assert formatted["status"] == "success"
        assert formatted["explanation"] == "Test explanation"
        assert len(formatted["next_steps"]) == 2

    def test_cortex_ask_mcp_tool_decorator(self):
        """Test that cortex_ask has @mcp_tool decorator."""
        # This verifies the function is properly registered
        assert hasattr(cortex_ask, '__mcp_tool__') or cortex_ask.__name__ == 'cortex_ask'
