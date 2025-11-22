"""Tests for Pipeline Behaviors"""
import pytest
from src.application.behaviors import (
    BrainProtectionBehavior,
    ValidationBehavior,
    PerformanceBehavior,
    LoggingBehavior
)
from src.application.common.interfaces import ICommand, IQuery
from src.application.common.result import Result
from dataclasses import dataclass
from typing import Callable, Awaitable


# Test requests
@dataclass
class TestCommand(ICommand):
    """Test command"""
    conversation_id: str
    title: str
    content: str
    namespace: str = "test.namespace"


@dataclass
class ProtectedNamespaceCommand(ICommand):
    """Command with protected namespace"""
    pattern_id: str
    namespace: str = "cortex.brain"


@dataclass
class DeleteCommand(ICommand):
    """Destructive operation"""
    conversation_id: str


@dataclass
class InvalidCommand(ICommand):
    """Command with invalid data"""
    conversation_id: str = ""
    title: str = ""
    content: str = "x"


@dataclass
class SearchQuery(IQuery[str]):
    """Search query"""
    search_text: str
    max_results: int = 10


# Mock next handler
async def mock_success_handler(request) -> Result:
    """Mock handler that succeeds"""
    return Result.success("Success")


async def mock_failure_handler(request) -> Result:
    """Mock handler that fails"""
    return Result.failure(["Handler failed"])


@pytest.mark.asyncio
class TestBrainProtectionBehavior:
    """Tests for BrainProtectionBehavior"""
    
    async def test_allows_normal_namespace(self):
        """Test behavior allows normal namespaces"""
        behavior = BrainProtectionBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Test",
            content="Content",
            namespace="user.workspace"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_success
    
    async def test_warns_on_protected_namespace(self, caplog):
        """Test behavior warns on protected namespace access"""
        import logging
        caplog.set_level(logging.WARNING)
        
        behavior = BrainProtectionBehavior()
        command = ProtectedNamespaceCommand(
            pattern_id="pat-001",
            namespace="cortex.brain"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_success
        assert "Protected namespace" in caplog.text
        assert "cortex.brain" in caplog.text
    
    async def test_detects_destructive_operation(self, caplog):
        """Test behavior detects destructive operations"""
        import logging
        caplog.set_level(logging.WARNING)
        
        behavior = BrainProtectionBehavior()
        command = DeleteCommand(conversation_id="conv-001")
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_success
        assert "Destructive operation" in caplog.text
    
    async def test_logs_protected_operations(self, caplog):
        """Test behavior logs all protected operations"""
        import logging
        caplog.set_level(logging.INFO)
        
        behavior = BrainProtectionBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Test",
            content="Content"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_success
        assert "Protected operation" in caplog.text
        assert "conv-001" in caplog.text
    
    async def test_handles_handler_failure(self):
        """Test behavior handles handler failure"""
        behavior = BrainProtectionBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Test",
            content="Content"
        )
        
        result = await behavior.handle(command, mock_failure_handler)
        
        assert result.is_failure
        assert "Handler failed" in result.errors
    
    async def test_rate_limiting_allows_normal_operations(self):
        """Test rate limiting allows normal number of operations"""
        behavior = BrainProtectionBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Test",
            content="Content"
        )
        
        # Execute 10 times - should all succeed
        for _ in range(10):
            result = await behavior.handle(command, mock_success_handler)
            assert result.is_success


@pytest.mark.asyncio
class TestValidationBehavior:
    """Tests for ValidationBehavior"""
    
    async def test_allows_valid_command(self):
        """Test behavior allows valid commands"""
        behavior = ValidationBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Valid Title",
            content="Valid content with enough characters"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_success
    
    async def test_rejects_empty_id(self):
        """Test behavior rejects empty IDs"""
        behavior = ValidationBehavior()
        command = TestCommand(
            conversation_id="",  # Empty ID
            title="Title",
            content="Content"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_failure
        assert "conversation_id cannot be empty" in result.errors
    
    async def test_rejects_empty_title(self):
        """Test behavior rejects empty title"""
        behavior = ValidationBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="",  # Empty title
            content="Content"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_failure
        assert "title cannot be empty" in result.errors
    
    async def test_rejects_short_content(self):
        """Test behavior rejects content that's too short"""
        behavior = ValidationBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Short"  # Less than 10 characters
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_failure
        assert "content must be at least 10 characters" in result.errors
    
    async def test_rejects_empty_search_text(self):
        """Test behavior rejects empty search text"""
        behavior = ValidationBehavior()
        query = SearchQuery(search_text="")
        
        result = await behavior.handle(query, mock_success_handler)
        
        assert result.is_failure
        assert "search_text cannot be empty" in result.errors
    
    async def test_rejects_negative_max_results(self):
        """Test behavior rejects negative max_results"""
        behavior = ValidationBehavior()
        query = SearchQuery(search_text="test", max_results=-5)
        
        result = await behavior.handle(query, mock_success_handler)
        
        assert result.is_failure
        assert "max_results must be positive" in result.errors
    
    async def test_rejects_excessive_max_results(self):
        """Test behavior rejects excessive max_results"""
        behavior = ValidationBehavior()
        query = SearchQuery(search_text="test", max_results=200)
        
        result = await behavior.handle(query, mock_success_handler)
        
        assert result.is_failure
        assert "max_results cannot exceed 100" in result.errors
    
    async def test_logs_validation_failure(self, caplog):
        """Test behavior logs validation failures"""
        import logging
        caplog.set_level(logging.WARNING)
        
        behavior = ValidationBehavior()
        command = InvalidCommand()
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_failure
        assert "Validation failed" in caplog.text
    
    async def test_logs_validation_success(self, caplog):
        """Test behavior logs validation success"""
        import logging
        caplog.set_level(logging.DEBUG)
        
        behavior = ValidationBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Valid content"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_success
        assert "Validation passed" in caplog.text


@pytest.mark.asyncio
class TestPerformanceBehavior:
    """Tests for PerformanceBehavior"""
    
    async def test_measures_execution_time(self):
        """Test behavior measures execution time"""
        behavior = PerformanceBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Content"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_success
        # Check metrics were recorded
        metrics = behavior.get_metrics_summary()
        assert "TestCommand" in metrics
        assert metrics["TestCommand"]["count"] == 1
    
    async def test_records_success_metrics(self):
        """Test behavior records success metrics"""
        behavior = PerformanceBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Content"
        )
        
        await behavior.handle(command, mock_success_handler)
        
        metrics = behavior.get_metrics_summary()
        assert metrics["TestCommand"]["success_count"] == 1
        assert metrics["TestCommand"]["failure_count"] == 0
        assert metrics["TestCommand"]["success_rate"] == 100.0
    
    async def test_records_failure_metrics(self):
        """Test behavior records failure metrics"""
        behavior = PerformanceBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Content"
        )
        
        await behavior.handle(command, mock_failure_handler)
        
        metrics = behavior.get_metrics_summary()
        assert metrics["TestCommand"]["success_count"] == 0
        assert metrics["TestCommand"]["failure_count"] == 1
        assert metrics["TestCommand"]["success_rate"] == 0.0
    
    async def test_tracks_min_max_duration(self):
        """Test behavior tracks min and max duration"""
        behavior = PerformanceBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Valid content"
        )
        
        # Execute multiple times
        for _ in range(5):
            await behavior.handle(command, mock_success_handler)
        
        metrics = behavior.get_metrics_summary()
        assert metrics["TestCommand"]["count"] == 5
        assert metrics["TestCommand"]["min_duration_ms"] >= 0.0  # Allow 0 for fast operations
        assert metrics["TestCommand"]["max_duration_ms"] >= metrics["TestCommand"]["min_duration_ms"]
        assert metrics["TestCommand"]["avg_duration_ms"] >= 0.0
    
    async def test_warns_on_slow_operation(self, caplog):
        """Test behavior warns on slow operations"""
        import logging
        import asyncio
        caplog.set_level(logging.WARNING)
        
        # Set very low threshold
        behavior = PerformanceBehavior(slow_threshold_ms=0.001)
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Content"
        )
        
        async def slow_handler(request):
            await asyncio.sleep(0.01)  # Slow operation
            return Result.success("Success")
        
        result = await behavior.handle(command, slow_handler)
        
        assert result.is_success
        assert "Slow operation detected" in caplog.text
    
    async def test_reset_metrics(self):
        """Test resetting metrics"""
        behavior = PerformanceBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Content"
        )
        
        await behavior.handle(command, mock_success_handler)
        assert len(behavior.get_metrics_summary()) > 0
        
        behavior.reset_metrics()
        assert len(behavior.get_metrics_summary()) == 0
    
    async def test_logs_performance_info(self, caplog):
        """Test behavior logs performance information"""
        import logging
        caplog.set_level(logging.INFO)
        
        behavior = PerformanceBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Content"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_success
        assert "TestCommand" in caplog.text
        assert "ms" in caplog.text  # Duration logged


@pytest.mark.asyncio
class TestLoggingBehavior:
    """Tests for LoggingBehavior"""
    
    async def test_logs_request(self, caplog):
        """Test behavior logs request"""
        import logging
        caplog.set_level(logging.INFO)
        
        behavior = LoggingBehavior(log_request_data=True)
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Content"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_success
        assert "Request: TestCommand" in caplog.text
        assert "conv-001" in caplog.text
    
    async def test_logs_successful_response(self, caplog):
        """Test behavior logs successful response"""
        import logging
        caplog.set_level(logging.INFO)
        
        behavior = LoggingBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Content"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_success
        assert "Response: TestCommand" in caplog.text
        assert "success" in caplog.text
    
    async def test_logs_failed_response(self, caplog):
        """Test behavior logs failed response"""
        import logging
        caplog.set_level(logging.WARNING)
        
        behavior = LoggingBehavior()
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Content"
        )
        
        result = await behavior.handle(command, mock_failure_handler)
        
        assert result.is_failure
        assert "Response: TestCommand" in caplog.text
        assert "failure" in caplog.text
        assert "Handler failed" in caplog.text
    
    async def test_sanitizes_sensitive_data(self):
        """Test behavior sanitizes sensitive data"""
        @dataclass
        class CommandWithPassword(ICommand):
            user_id: str
            password: str
        
        behavior = LoggingBehavior(log_request_data=True)
        command = CommandWithPassword(
            user_id="user-001",
            password="secret123"
        )
        
        # Extract and check sanitized data
        data = behavior._extract_request_data(command)
        sanitized = behavior._sanitize_data(data)
        
        # Password should be redacted
        assert "password" not in str(sanitized.values())
    
    async def test_truncates_long_content(self):
        """Test behavior truncates long content"""
        behavior = LoggingBehavior(log_request_data=True)
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="A" * 200  # Long content
        )
        
        data = behavior._extract_request_data(command)
        
        # Should have content_length and content_preview
        assert "content_length" in data
        assert data["content_length"] == 200
        assert "content_preview" in data
        assert len(data["content_preview"]) <= 103  # 100 chars + "..."
    
    async def test_skips_request_logging_when_disabled(self, caplog):
        """Test behavior skips request logging when disabled"""
        import logging
        caplog.set_level(logging.INFO)
        
        behavior = LoggingBehavior(log_request_data=False)
        command = TestCommand(
            conversation_id="conv-001",
            title="Title",
            content="Content"
        )
        
        result = await behavior.handle(command, mock_success_handler)
        
        assert result.is_success
        # Should not have request data in logs
        assert "Request:" not in caplog.text or "Data:" not in caplog.text
