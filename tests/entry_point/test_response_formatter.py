"""
Tests for Response Formatter

Tests all formatting capabilities including text/markdown/JSON formats,
error formatting, batch processing, and metadata handling.
"""

import pytest
import json
from datetime import datetime

from CORTEX.src.entry_point.response_formatter import ResponseFormatter
from CORTEX.src.cortex_agents.base_agent import AgentResponse


@pytest.fixture
def formatter():
    """Create response formatter instance."""
    return ResponseFormatter()


@pytest.fixture
def success_response():
    """Create a successful response."""
    return AgentResponse(
        success=True,
        result={"files": ["src/auth.py", "src/login.py"]},
        message="Task completed successfully",
        agent_name="CodeExecutor",
        duration_ms=2500,
        metadata={"task": "authentication"}
    )


@pytest.fixture
def error_response():
    """Create an error response."""
    return AgentResponse(
        success=False,
        result=None,
        message="Task failed: File not found",
        agent_name="CodeExecutor"
    )


class TestInitialization:
    """Test ResponseFormatter initialization."""
    
    def test_formatter_creation(self, formatter):
        """Test formatter can be created."""
        assert formatter is not None
        assert hasattr(formatter, 'format')
        assert hasattr(formatter, 'format_batch')

class TestTextFormatting:
    """Test plain text formatting."""
    
    def test_format_success_response(self, formatter, success_response):
        """Test formatting successful response."""
        result = formatter.format(success_response, format_type="text")
        assert "✓ SUCCESS" in result
        assert "Task completed successfully" in result
        assert "src/auth.py" in result
        
    def test_format_error_response(self, formatter, error_response):
        """Test formatting error response."""
        result = formatter.format(error_response, format_type="text")
        assert "✗ FAILURE" in result
        assert "Task failed" in result    
    def test_format_with_metadata(self, formatter, success_response):
        """Test formatting includes metadata."""
        result = formatter.format(success_response, include_metadata=True, format_type="text")
        assert "Metadata:" in result
        assert "task:" in result or "authentication" in result    
    def test_format_without_metadata(self, formatter, success_response):
        """Test formatting without metadata."""
        result = formatter.format(success_response, include_metadata=False, format_type="text")
        assert "Metadata:" not in result
    
    def test_format_with_recommendations(self, formatter, success_response):
        """Test formatting includes recommendations."""
        result = formatter.format(success_response, include_recommendations=True, format_type="text")
        assert "Recommendations:" in result
    
    def test_format_without_recommendations(self, formatter, success_response):
        """Test formatting without recommendations."""
        result = formatter.format(success_response, include_recommendations=False, format_type="text")
        assert "Recommendations:" not in result


class TestMarkdownFormatting:
    """Test Markdown formatting."""
    
    def test_format_markdown_success(self, formatter, success_response):
        """Test Markdown formatting of success."""
        result = formatter.format(success_response, format_type="markdown")
        assert "## ✓ SUCCESS" in result
        assert "**files:**" in result or "files:" in result
    
    def test_format_markdown_error(self, formatter, error_response):
        """Test Markdown formatting of error."""
        result = formatter.format(error_response, format_type="markdown")
        assert "## ✗ FAILURE" in result
        assert "Task failed" in result
    
    def test_format_markdown_details(self, formatter, success_response):
        """Test Markdown details section."""
        result = formatter.format(success_response, format_type="markdown")
        assert "### Result" in result
        assert "src/auth.py" in result

class TestJSONFormatting:
    """Test JSON formatting."""
    
    def test_format_json_success(self, formatter, success_response):
        """Test JSON formatting of success."""
        result = formatter.format(success_response, format_type="json")
        data = json.loads(result)
        assert data["success"] is True
        assert "files" in data["result"]
    
    def test_format_json_error(self, formatter, error_response):
        """Test JSON formatting of error."""
        result = formatter.format(error_response, format_type="json")
        data = json.loads(result)
        assert data["success"] is False
        assert data["message"] is not None
    
    def test_json_structure(self, formatter, success_response):
        """Test JSON has expected structure."""
        result = formatter.format(success_response, format_type="json")
        data = json.loads(result)
        assert "success" in data
        assert "result" in data
        assert "message" in data
        assert "metadata" in data
        assert "agent_name" in data

class TestBatchFormatting:
    """Test batch response formatting."""
    
    def test_format_batch_multiple_responses(self, formatter, success_response, error_response):
        """Test formatting multiple responses."""
        responses = [success_response, error_response]
        result = formatter.format_batch(responses)
        assert "Batch Results: 1/2 successful" in result
        assert "Response 1" in result
        assert "Response 2" in result
    
    def test_format_batch_with_summary(self, formatter, success_response):
        """Test batch formatting with summary."""
        responses = [success_response, success_response]
        result = formatter.format_batch(responses, include_summary=True)
        assert "Batch Results: 2/2 successful" in result
    
    def test_format_batch_without_summary(self, formatter, success_response):
        """Test batch formatting without summary."""
        responses = [success_response]
        result = formatter.format_batch(responses, include_summary=False)
        assert "Batch Results" not in result
    
    def test_format_empty_batch(self, formatter):
        """Test formatting empty batch."""
        result = formatter.format_batch([])
        assert "No responses to format" in result


class TestErrorFormatting:
    """Test error message formatting."""
    
    def test_format_exception(self, formatter):
        """Test formatting exception."""
        error = ValueError("Invalid input")
        result = formatter.format_error(error)
        assert "✗ ERROR: ValueError" in result
        assert "Invalid input" in result
    
    def test_format_exception_with_context(self, formatter):
        """Test formatting exception with context."""
        error = FileNotFoundError("File missing")
        context = {"file": "src/auth.py", "operation": "read"}
        result = formatter.format_error(error, context)
        assert "FileNotFoundError" in result
        assert "File missing" in result
        assert "Context:" in result
        assert "src/auth.py" in result


class TestProgressFormatting:
    """Test progress indicator formatting."""
    
    def test_format_progress_partial(self, formatter):
        """Test progress formatting at 50%."""
        result = formatter.format_progress(5, 10)
        assert "[" in result
        assert "]" in result
        assert "50%" in result
        assert "(5/10)" in result
    
    def test_format_progress_complete(self, formatter):
        """Test progress formatting at 100%."""
        result = formatter.format_progress(10, 10)
        assert "100%" in result
        assert "(10/10)" in result
    
    def test_format_progress_with_message(self, formatter):
        """Test progress formatting with message."""
        result = formatter.format_progress(3, 10, "Processing files")
        assert "Processing files" in result
    
    def test_format_progress_zero_total(self, formatter):
        """Test progress formatting with zero total."""
        result = formatter.format_progress(0, 0)
        assert "0%" in result
        assert "(0/0)" in result


class TestRecommendations:
    """Test recommendation extraction and generation."""
    
    def test_extract_recommendations_from_next_actions(self, formatter):
        """Test extracting recommendations from next_actions."""
        response = AgentResponse(
            success=True,
            result={},
            message="Task complete",
            next_actions=["Review the code", "Run tests"]
        )
        result = formatter.format(response, format_type="text")
        assert "Review the code" in result
        assert "Run tests" in result
    
    def test_extract_next_steps_from_metadata(self, formatter):
        """Test extracting next steps from metadata."""
        response = AgentResponse(
            success=True,
            result={},
            message="Task complete",
            metadata={"next_steps": ["Commit changes", "Deploy"]}
        )
        result = formatter.format(response, format_type="text")
        assert "Commit changes" in result or "Deploy" in result
    
    def test_default_recommendations_success(self, formatter):
        """Test default recommendations for success."""
        response = AgentResponse(
            success=True,
            result={"files": ["src/auth.py"]},
            message="Task complete"
        )
        result = formatter.format(response, include_recommendations=True, format_type="text")
        assert "Recommendations:" in result
    
    def test_default_recommendations_failure(self, formatter):
        """Test default recommendations for failure."""
        response = AgentResponse(
            success=False,
            result=None,
            message="Task failed"
        )
        result = formatter.format(response, include_recommendations=True, format_type="text")
        assert "Recommendations:" in result


class TestStatusSymbols:
    """Test status symbol rendering."""
    
    def test_success_symbol(self, formatter):
        """Test success symbol."""
        response = AgentResponse(success=True, result=None, message="Done")
        result = formatter.format(response, format_type="text")
        assert "✓" in result
    
    def test_failure_symbol(self, formatter):
        """Test failure symbol."""
        response = AgentResponse(success=False, result=None, message="Failed")
        result = formatter.format(response, format_type="text")
        assert "✗" in result


class TestDataFormatting:
    """Test data structure formatting."""
    
    def test_format_list_result(self, formatter):
        """Test formatting list result."""
        response = AgentResponse(
            success=True,
            result={"files": ["file1.py", "file2.py"]},
            message="Files processed"
        )
        result = formatter.format(response, format_type="text")
        assert "file1.py" in result
        assert "file2.py" in result
    
    def test_format_dict_result(self, formatter):
        """Test formatting nested dict result."""
        response = AgentResponse(
            success=True,
            result={"config": {"timeout": 30, "retries": 3}},
            message="Config updated"
        )
        result = formatter.format(response, format_type="text")
        assert "config:" in result
        assert "timeout" in result or "30" in result
    
    def test_format_simple_result(self, formatter):
        """Test formatting simple key-value result."""
        response = AgentResponse(
            success=True,
            result={"count": 42, "status": "done"},
            message="Task complete"
        )
        result = formatter.format(response, format_type="text")
        assert "count" in result or "42" in result
        assert "status" in result or "done" in result


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_format_empty_response(self, formatter):
        """Test formatting response with no result."""
        response = AgentResponse(success=True, result=None, message="Done")
        result = formatter.format(response, format_type="text")
        assert "SUCCESS" in result
    
    def test_format_response_no_message(self, formatter):
        """Test formatting response without message."""
        response = AgentResponse(success=True, result=None, message="")
        result = formatter.format(response, format_type="text")
        assert "SUCCESS" in result
    
    def test_format_response_with_special_characters(self, formatter):
        """Test formatting with special characters."""
        response = AgentResponse(
            success=True,
            result=None,
            message="File with special chars: <test> & 'quotes'"
        )
        result = formatter.format(response, format_type="text")
        assert "special chars" in result
    
    def test_format_very_long_message(self, formatter):
        """Test formatting very long message."""
        long_message = "x" * 10000
        response = AgentResponse(
            success=True,
            result=None,
            message=long_message
        )
        result = formatter.format(response, format_type="text")
        assert len(result) > 10000
