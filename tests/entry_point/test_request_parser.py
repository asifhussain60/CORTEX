"""
Tests for Request Parser

Tests all parsing capabilities including intent extraction,
context detection, priority analysis, and batch processing.
"""

import pytest
from datetime import datetime

from src.entry_point.request_parser import RequestParser
from src.cortex_agents.base_agent import AgentRequest
from src.cortex_agents.agent_types import Priority


@pytest.fixture
def parser():
    """Create request parser instance."""
    return RequestParser()


class TestInitialization:
    """Test RequestParser initialization."""
    
    def test_parser_creation(self, parser):
        """Test parser can be created."""
        assert parser is not None
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'INTENT_KEYWORDS')


class TestIntentExtraction:
    """Test intent extraction from messages."""
    
    def test_plan_intent(self, parser):
        """Test planning intent extraction."""
        message = "Plan a new authentication system"
        request = parser.parse(message)
        assert request.intent == "plan"
    
    def test_code_intent(self, parser):
        """Test coding intent extraction."""
        message = "Implement the login functionality"
        request = parser.parse(message)
        assert request.intent == "code"
    
    def test_test_intent(self, parser):
        """Test testing intent extraction."""
        message = "Test the auth module functionality"
        request = parser.parse(message)
        assert request.intent == "test"
    
    def test_fix_intent(self, parser):
        """Test fixing intent extraction."""
        message = "Fix the bug in the authentication flow"
        request = parser.parse(message)
        assert request.intent == "fix"
    
    def test_commit_intent(self, parser):
        """Test commit intent extraction."""
        message = "Commit the changes to git"
        request = parser.parse(message)
        assert request.intent == "commit"
    
    def test_resume_intent(self, parser):
        """Test resume intent extraction."""
        message = "Resume the previous conversation"
        request = parser.parse(message)
        assert request.intent == "resume"
    
    def test_health_check_intent(self, parser):
        """Test health check intent extraction."""
        message = "Check the health of the system"
        request = parser.parse(message)
        assert request.intent == "health_check"
    
    def test_unknown_intent(self, parser):
        """Test handling of unknown intent."""
        message = "Just some random text"
        request = parser.parse(message)
        assert request.intent == "unknown"


class TestContextExtraction:
    """Test context extraction from messages."""
    
    def test_file_path_extraction(self, parser):
        """Test extracting file paths."""
        message = "Fix bug in src/auth.py and src/login.py"
        request = parser.parse(message)
        assert "files" in request.context
        files = request.context["files"]
        assert "src/auth.py" in files or "src/login.py" in files
    
    def test_code_block_extraction(self, parser):
        """Test extracting code blocks."""
        message = """Implement this:
```python
def test():
    pass
```
"""
        request = parser.parse(message)
        assert "code" in request.context
        assert "def test()" in request.context["code"]
    
    def test_inline_file_extraction(self, parser):
        """Test extracting files from inline code."""
        message = "Check the `src/config/app.py` file"
        request = parser.parse(message)
        assert "files" in request.context
        assert "src/config/app.py" in request.context["files"]
    
    def test_bug_context_type(self, parser):
        """Test bug context type detection."""
        message = "There's a bug in the system"
        request = parser.parse(message)
        assert request.context.get("type") == "bug"
    
    def test_feature_context_type(self, parser):
        """Test feature context type detection."""
        message = "Add a new feature for authentication"
        request = parser.parse(message)
        assert request.context.get("type") == "feature"
    
    def test_operation_detection_create(self, parser):
        """Test create operation detection."""
        message = "Create a new auth module"
        request = parser.parse(message)
        assert request.context.get("operation") == "create"
    
    def test_operation_detection_modify(self, parser):
        """Test modify operation detection."""
        message = "Edit the existing config file"
        request = parser.parse(message)
        assert request.context.get("operation") == "modify"
    
    def test_operation_detection_delete(self, parser):
        """Test delete operation detection."""
        message = "Remove the old authentication code"
        request = parser.parse(message)
        assert request.context.get("operation") == "delete"


class TestPriorityExtraction:
    """Test priority extraction from messages."""
    
    def test_critical_priority(self, parser):
        """Test critical priority detection."""
        message = "URGENT: Fix production crash"
        request = parser.parse(message)
        assert request.priority == 1  # Priority.CRITICAL value
    
    def test_high_priority(self, parser):
        """Test high priority detection."""
        message = "This is important - fix the auth bug"
        request = parser.parse(message)
        assert request.priority == 2  # Priority.HIGH value
    
    def test_medium_priority(self, parser):
        """Test medium priority (normal level)."""
        message = "Should fix this bug when you can"
        request = parser.parse(message)
        assert request.priority == 3  # Priority.NORMAL value
    
    def test_normal_priority(self, parser):
        """Test normal priority (default)."""
        message = "Fix the typo in the readme"
        request = parser.parse(message)
        assert request.priority == 3  # Priority.NORMAL value


class TestMetadata:
    """Test metadata handling."""
    
    def test_conversation_id(self, parser):
        """Test conversation ID assignment."""
        message = "Fix the bug"
        conv_id = "conv-123"
        request = parser.parse(message, conversation_id=conv_id)
        assert request.conversation_id == conv_id
    
    def test_custom_metadata(self, parser):
        """Test custom metadata merging."""
        message = "Fix the bug"
        metadata = {"user_id": "user-456", "session": "sess-789"}
        request = parser.parse(message, metadata=metadata)
        assert request.context["user_id"] == "user-456"
        assert request.context["session"] == "sess-789"
    
    def test_parsed_timestamp(self, parser):
        """Test that parsed timestamp is added."""
        message = "Fix the bug"
        request = parser.parse(message)
        assert "parsed_at" in request.metadata
        # Verify it's a valid ISO format timestamp
        datetime.fromisoformat(request.metadata["parsed_at"])


class TestBatchProcessing:
    """Test batch message processing."""
    
    def test_batch_parse(self, parser):
        """Test parsing multiple messages."""
        messages = [
            "Plan the authentication system",
            "Implement the login feature",
            "Test the auth module"
        ]
        requests = parser.parse_batch(messages)
        assert len(requests) == 3
        assert requests[0].intent == "plan"
        assert requests[1].intent == "code"
        assert requests[2].intent == "test"
    
    def test_batch_with_conversation_id(self, parser):
        """Test batch parsing with shared conversation ID."""
        messages = ["Fix bug", "Write tests"]
        conv_id = "conv-batch-123"
        requests = parser.parse_batch(messages, conversation_id=conv_id)
        assert all(r.conversation_id == conv_id for r in requests)


class TestHelperMethods:
    """Test helper methods."""
    
    def test_extract_files_from_context(self, parser):
        """Test extracting files from context dict."""
        context = {"files": ["src/auth.py", "src/login.py"]}
        files = parser.extract_files_from_context(context)
        assert len(files) == 2
        assert "src/auth.py" in files
    
    def test_extract_files_single_string(self, parser):
        """Test extracting single file string."""
        context = {"files": "src/auth.py"}
        files = parser.extract_files_from_context(context)
        assert len(files) == 1
        assert files[0] == "src/auth.py"
    
    def test_extract_files_empty(self, parser):
        """Test extracting files when none present."""
        context = {}
        files = parser.extract_files_from_context(context)
        assert files == []
    
    def test_infer_agent_type_planner(self, parser):
        """Test agent type inference for planning."""
        request = parser.parse("Plan a new feature")
        agent_type = parser.infer_agent_type(request)
        assert agent_type == "WorkPlanner"
    
    def test_infer_agent_type_code_executor(self, parser):
        """Test agent type inference for coding."""
        request = parser.parse("Implement the auth system")
        agent_type = parser.infer_agent_type(request)
        assert agent_type == "CodeExecutor"
    
    def test_infer_agent_type_unknown(self, parser):
        """Test agent type inference for unknown intent."""
        request = parser.parse("Random message")
        agent_type = parser.infer_agent_type(request)
        assert agent_type == "IntentRouter"


class TestRequestValidation:
    """Test request validation."""
    
    def test_validate_valid_request(self, parser):
        """Test validating a valid request."""
        request = parser.parse("Fix the bug in auth.py")
        is_valid, error = parser.validate_request(request)
        assert is_valid is True
        assert error is None
    
    def test_validate_empty_message(self, parser):
        """Test validating request with empty message."""
        request = AgentRequest(
            intent="fix",
            context={},
            user_message=""
        )
        is_valid, error = parser.validate_request(request)
        assert is_valid is False
        assert "User message is required" in error
    
    def test_validate_no_intent(self, parser):
        """Test validating request without intent."""
        request = AgentRequest(
            intent="",
            context={},
            user_message="Fix this"
        )
        is_valid, error = parser.validate_request(request)
        assert is_valid is False
        assert "Intent is required" in error
    
    def test_validate_unknown_intent_warning(self, parser):
        """Test validating request with unknown intent."""
        request = parser.parse("Some random text")
        is_valid, error = parser.validate_request(request)
        assert is_valid is True
        assert "could not be determined" in error


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_message(self, parser):
        """Test parsing empty message."""
        request = parser.parse("")
        assert request.intent == "unknown"
        assert request.user_message == ""
    
    def test_very_long_message(self, parser):
        """Test parsing very long message."""
        message = "Fix the bug " * 1000
        request = parser.parse(message)
        assert request.intent == "fix"
        assert len(request.user_message) == len(message)
    
    def test_message_with_special_characters(self, parser):
        """Test parsing message with special characters."""
        message = "Fix bug in src/auth@v2.py (urgent!!! #123)"
        request = parser.parse(message)
        assert request.intent == "fix"
    
    def test_mixed_case_intent_keywords(self, parser):
        """Test intent extraction is case insensitive."""
        message = "PLAN the new FEATURE"
        request = parser.parse(message)
        assert request.intent == "plan"
    
    def test_multiple_intents(self, parser):
        """Test message with multiple intent keywords."""
        # Should extract first matching intent
        message = "Plan and implement the new feature"
        request = parser.parse(message)
        # Either plan or code is acceptable
        assert request.intent in ["plan", "code"]
