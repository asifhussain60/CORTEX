"""Integration tests for validation pipeline with commands and queries"""
import pytest
from datetime import datetime, timedelta
from src.application.commands.conversation_commands import (
    CaptureConversationCommand,
    LearnPatternCommand,
    UpdateContextRelevanceCommand,
    UpdatePatternConfidenceCommand
)
from src.application.queries.conversation_queries import (
    SearchContextQuery,
    GetConversationQualityQuery,
    FindSimilarPatternsQuery
)
from src.application.validation import (
    CaptureConversationValidator,
    LearnPatternValidator,
    UpdateContextRelevanceValidator,
    UpdatePatternConfidenceValidator,
    SearchContextQueryValidator,
    GetConversationQualityQueryValidator,
    FindSimilarPatternsQueryValidator,
    get_validator_registry
)


class TestCaptureConversationValidation:
    """Test CaptureConversationCommand validation"""
    
    def test_valid_command_passes(self):
        """Valid capture conversation command should pass validation"""
        command = CaptureConversationCommand(
            conversation_id="conv-123",
            title="Test Conversation",
            content="This is a test conversation with sufficient length for validation.",
            file_path="/path/to/file.py",
            quality_score=0.85,
            entity_count=5,
            captured_at=datetime.now()
        )
        
        validator = CaptureConversationValidator()
        result = validator.validate(command)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_missing_conversation_id_fails(self):
        """Missing conversation_id should fail validation"""
        command = CaptureConversationCommand(
            conversation_id="",
            title="Test",
            content="Valid content here",
            file_path="/path/to/file.py"
        )
        
        validator = CaptureConversationValidator()
        result = validator.validate(command)
        
        assert not result.is_valid
        assert any("Conversation ID" in error.error_message for error in result.errors)
    
    def test_short_content_fails(self):
        """Content shorter than 10 characters should fail"""
        command = CaptureConversationCommand(
            conversation_id="conv-123",
            title="Test",
            content="Short",
            file_path="/path/to/file.py"
        )
        
        validator = CaptureConversationValidator()
        result = validator.validate(command)
        
        assert not result.is_valid
        assert any("at least 10 characters" in error.error_message for error in result.errors)
    
    def test_long_title_fails(self):
        """Title longer than 500 characters should fail"""
        command = CaptureConversationCommand(
            conversation_id="conv-123",
            title="A" * 501,
            content="Valid content here",
            file_path="/path/to/file.py"
        )
        
        validator = CaptureConversationValidator()
        result = validator.validate(command)
        
        assert not result.is_valid
        assert any("cannot exceed 500 characters" in error.error_message for error in result.errors)
    
    def test_invalid_quality_score_fails(self):
        """Quality score outside 0.0-1.0 range should fail"""
        command = CaptureConversationCommand(
            conversation_id="conv-123",
            title="Test",
            content="Valid content here",
            file_path="/path/to/file.py",
            quality_score=1.5
        )
        
        validator = CaptureConversationValidator()
        result = validator.validate(command)
        
        assert not result.is_valid
        assert any("between 0.0 and 1.0" in error.error_message for error in result.errors)
    
    def test_negative_entity_count_fails(self):
        """Negative entity count should fail"""
        command = CaptureConversationCommand(
            conversation_id="conv-123",
            title="Test",
            content="Valid content here",
            file_path="/path/to/file.py",
            entity_count=-1
        )
        
        validator = CaptureConversationValidator()
        result = validator.validate(command)
        
        assert not result.is_valid
        assert any("cannot be negative" in error.error_message for error in result.errors)
    
    def test_future_captured_at_fails(self):
        """Captured date in the future should fail"""
        command = CaptureConversationCommand(
            conversation_id="conv-123",
            title="Test",
            content="Valid content here",
            file_path="/path/to/file.py",
            captured_at=datetime.now() + timedelta(days=1)
        )
        
        validator = CaptureConversationValidator()
        result = validator.validate(command)
        
        assert not result.is_valid
        assert any("cannot be in the future" in error.error_message for error in result.errors)


class TestLearnPatternValidation:
    """Test LearnPatternCommand validation"""
    
    def test_valid_command_passes(self):
        """Valid learn pattern command should pass validation"""
        command = LearnPatternCommand(
            pattern_id="pattern-123",
            pattern_name="Repository Pattern",
            pattern_type="architecture",
            pattern_content="class Repository...",
            source_conversation_id="conv-123",
            namespace="workspace.backend",
            confidence_score=0.85,
            tags=["architecture", "database"],
            learned_at=datetime.now()
        )
        
        validator = LearnPatternValidator()
        result = validator.validate(command)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_invalid_pattern_type_fails(self):
        """Invalid pattern type should fail"""
        command = LearnPatternCommand(
            pattern_id="pattern-123",
            pattern_name="Test Pattern",
            pattern_type="invalid_type",
            pattern_content="content",
            source_conversation_id="conv-123",
            namespace="test",
            confidence_score=0.5
        )
        
        validator = LearnPatternValidator()
        result = validator.validate(command)
        
        assert not result.is_valid
        assert any("Pattern type must be one of" in error.error_message for error in result.errors)
    
    def test_invalid_namespace_format_fails(self):
        """Invalid namespace format should fail"""
        command = LearnPatternCommand(
            pattern_id="pattern-123",
            pattern_name="Test Pattern",
            pattern_type="architecture",
            pattern_content="content",
            source_conversation_id="conv-123",
            namespace="invalid namespace!",
            confidence_score=0.5
        )
        
        validator = LearnPatternValidator()
        result = validator.validate(command)
        
        assert not result.is_valid
        assert any("Namespace must contain only" in error.error_message for error in result.errors)
    
    def test_invalid_confidence_score_fails(self):
        """Confidence score outside 0.0-1.0 should fail"""
        command = LearnPatternCommand(
            pattern_id="pattern-123",
            pattern_name="Test Pattern",
            pattern_type="architecture",
            pattern_content="content",
            source_conversation_id="conv-123",
            namespace="test",
            confidence_score=1.5
        )
        
        validator = LearnPatternValidator()
        result = validator.validate(command)
        
        assert not result.is_valid
        assert any("between 0.0 and 1.0" in error.error_message for error in result.errors)
    
    def test_empty_tags_fail(self):
        """Empty strings in tags should fail"""
        command = LearnPatternCommand(
            pattern_id="pattern-123",
            pattern_name="Test Pattern",
            pattern_type="architecture",
            pattern_content="content",
            source_conversation_id="conv-123",
            namespace="test",
            confidence_score=0.5,
            tags=["valid", "", "also-valid"]
        )
        
        validator = LearnPatternValidator()
        result = validator.validate(command)
        
        assert not result.is_valid
        assert any("non-empty strings" in error.error_message for error in result.errors)


class TestSearchContextQueryValidation:
    """Test SearchContextQuery validation"""
    
    def test_valid_query_passes(self):
        """Valid search context query should pass validation"""
        query = SearchContextQuery(
            search_text="test query",
            namespace_filter="workspace.backend",
            min_relevance=0.5,
            max_results=10
        )
        
        validator = SearchContextQueryValidator()
        result = validator.validate(query)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_short_search_text_fails(self):
        """Search text shorter than 2 characters should fail"""
        query = SearchContextQuery(
            search_text="a"
        )
        
        validator = SearchContextQueryValidator()
        result = validator.validate(query)
        
        assert not result.is_valid
        assert any("at least 2 characters" in error.error_message for error in result.errors)
    
    def test_long_search_text_fails(self):
        """Search text longer than 500 characters should fail"""
        query = SearchContextQuery(
            search_text="a" * 501
        )
        
        validator = SearchContextQueryValidator()
        result = validator.validate(query)
        
        assert not result.is_valid
        assert any("cannot exceed 500 characters" in error.error_message for error in result.errors)
    
    def test_invalid_max_results_fails(self):
        """Max results > 100 should fail"""
        query = SearchContextQuery(
            search_text="test",
            max_results=101
        )
        
        validator = SearchContextQueryValidator()
        result = validator.validate(query)
        
        assert not result.is_valid
        assert any("cannot exceed 100" in error.error_message for error in result.errors)
    
    def test_invalid_min_relevance_fails(self):
        """Min relevance outside 0.0-1.0 should fail"""
        query = SearchContextQuery(
            search_text="test",
            min_relevance=1.5
        )
        
        validator = SearchContextQueryValidator()
        result = validator.validate(query)
        
        assert not result.is_valid
        assert any("between 0.0 and 1.0" in error.error_message for error in result.errors)


class TestValidatorRegistry:
    """Test validator registry integration"""
    
    def test_registry_has_command_validators(self):
        """Registry should have validators for all commands"""
        registry = get_validator_registry()
        
        # Check all command validators are registered
        assert 'CaptureConversationCommand' in registry.get_registered_types()
        assert 'LearnPatternCommand' in registry.get_registered_types()
        assert 'UpdateContextRelevanceCommand' in registry.get_registered_types()
        assert 'UpdatePatternConfidenceCommand' in registry.get_registered_types()
    
    def test_registry_has_query_validators(self):
        """Registry should have validators for all queries"""
        registry = get_validator_registry()
        
        # Check all query validators are registered
        assert 'SearchContextQuery' in registry.get_registered_types()
        assert 'GetConversationQualityQuery' in registry.get_registered_types()
        assert 'FindSimilarPatternsQuery' in registry.get_registered_types()
    
    def test_registry_can_find_validator_by_request(self):
        """Registry should find validator by request instance"""
        registry = get_validator_registry()
        
        command = CaptureConversationCommand(
            conversation_id="test",
            title="Test",
            content="Valid content here",
            file_path="/path"
        )
        
        validator = registry.get_validator(command)
        
        assert validator is not None
        assert isinstance(validator, CaptureConversationValidator)
    
    def test_registry_returns_none_for_unregistered_request(self):
        """Registry should return None for unregistered request types"""
        registry = get_validator_registry()
        
        # Create a dummy request class
        class UnregisteredCommand:
            pass
        
        unregistered = UnregisteredCommand()
        validator = registry.get_validator(unregistered)
        
        assert validator is None


class TestValidationPipelineIntegration:
    """Test validation behavior in pipeline context"""
    
    @pytest.mark.asyncio
    async def test_valid_command_proceeds_to_handler(self):
        """Valid command should proceed to handler"""
        from src.application.behaviors.validation_behavior import ValidationBehavior
        from src.application.common.result import Result
        
        # Create valid command
        command = CaptureConversationCommand(
            conversation_id="conv-123",
            title="Test",
            content="Valid content here with enough characters",
            file_path="/path"
        )
        
        # Mock next handler
        handler_called = False
        async def next_handler(request):
            nonlocal handler_called
            handler_called = True
            return Result.success("Handler executed")
        
        # Run through validation behavior
        behavior = ValidationBehavior()
        result = await behavior.handle(command, next_handler)
        
        # Should succeed and call handler
        assert result.is_success
        assert handler_called
        assert result.value == "Handler executed"
    
    @pytest.mark.asyncio
    async def test_invalid_command_fails_before_handler(self):
        """Invalid command should fail before reaching handler"""
        from src.application.behaviors.validation_behavior import ValidationBehavior
        from src.application.common.result import Result
        
        # Create invalid command (missing conversation_id)
        command = CaptureConversationCommand(
            conversation_id="",  # Invalid!
            title="Test",
            content="Valid content here",
            file_path="/path"
        )
        
        # Mock next handler
        handler_called = False
        async def next_handler(request):
            nonlocal handler_called
            handler_called = True
            return Result.success("Handler executed")
        
        # Run through validation behavior
        behavior = ValidationBehavior()
        result = await behavior.handle(command, next_handler)
        
        # Should fail without calling handler
        assert not result.is_success
        assert not handler_called
        assert any("Conversation ID" in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_unregistered_request_skips_validation(self):
        """Unregistered request should skip validation and proceed"""
        from src.application.behaviors.validation_behavior import ValidationBehavior
        from src.application.common.result import Result
        from src.application.common.interfaces import IRequest
        
        # Create unregistered request type
        class UnregisteredRequest(IRequest):
            pass
        
        request = UnregisteredRequest()
        
        # Mock next handler
        handler_called = False
        async def next_handler(req):
            nonlocal handler_called
            handler_called = True
            return Result.success("Handler executed")
        
        # Run through validation behavior
        behavior = ValidationBehavior()
        result = await behavior.handle(request, next_handler)
        
        # Should skip validation and proceed to handler
        assert result.is_success
        assert handler_called
        assert result.value == "Handler executed"
