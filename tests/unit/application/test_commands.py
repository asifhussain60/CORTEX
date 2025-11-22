"""Tests for Commands and Command Handlers"""
import pytest
from datetime import datetime
from src.application.commands.conversation_commands import (
    CaptureConversationCommand,
    LearnPatternCommand,
    UpdateContextRelevanceCommand,
    UpdatePatternConfidenceCommand,
    DeleteConversationCommand
)
from src.application.commands.conversation_handlers import (
    CaptureConversationHandler,
    LearnPatternHandler,
    UpdateContextRelevanceHandler,
    UpdatePatternConfidenceHandler,
    DeleteConversationHandler
)


@pytest.mark.asyncio
class TestCaptureConversationCommand:
    """Tests for CaptureConversationCommand"""
    
    async def test_command_creation(self):
        """Test creating a capture conversation command"""
        command = CaptureConversationCommand(
            conversation_id="conv-001",
            title="Test Conversation",
            content="This is test content",
            file_path="/path/to/conv.json"
        )
        
        assert command.conversation_id == "conv-001"
        assert command.title == "Test Conversation"
        assert command.content == "This is test content"
        assert command.file_path == "/path/to/conv.json"
        assert command.quality_score is None
        assert command.entity_count is None
    
    async def test_command_with_optional_fields(self):
        """Test command with optional fields"""
        command = CaptureConversationCommand(
            conversation_id="conv-001",
            title="Test",
            content="Content",
            file_path="/path",
            quality_score=0.85,
            entity_count=15,
            captured_at=datetime.utcnow()
        )
        
        assert command.quality_score == 0.85
        assert command.entity_count == 15
        assert command.captured_at is not None


@pytest.mark.asyncio
class TestCaptureConversationHandler:
    """Tests for CaptureConversationHandler"""
    
    async def test_handler_success_with_quality_score(self):
        """Test handler succeeds with provided quality score"""
        handler = CaptureConversationHandler()
        command = CaptureConversationCommand(
            conversation_id="conv-001",
            title="Test",
            content="This is a test conversation",
            file_path="/path",
            quality_score=0.85,
            entity_count=15
        )
        
        result = await handler.handle(command)
        
        assert result.is_success
        assert result.value == "conv-001"
    
    async def test_handler_calculates_quality_when_missing(self):
        """Test handler calculates quality when not provided"""
        handler = CaptureConversationHandler()
        # Create a conversation with very long content to ensure high quality score
        long_content = "This is a detailed and comprehensive conversation about software engineering practices. " * 20  # Very long content
        command = CaptureConversationCommand(
            conversation_id="conv-001",
            title="Comprehensive Software Engineering Discussion",
            content=long_content,
            file_path="/path",
            entity_count=50  # High entity count
        )
        
        result = await handler.handle(command)
        
        # Should calculate quality heuristically and succeed with long content
        assert result.is_success
    
    async def test_handler_rejects_low_quality(self):
        """Test handler rejects low quality conversations"""
        handler = CaptureConversationHandler()
        command = CaptureConversationCommand(
            conversation_id="conv-001",
            title="Test",
            content="Short",
            file_path="/path",
            quality_score=0.50  # Below 0.70 threshold
        )
        
        result = await handler.handle(command)
        
        assert result.is_failure
        assert "quality too low" in result.errors[0].lower()
    
    async def test_handler_rejects_empty_id(self):
        """Test handler rejects empty conversation ID"""
        handler = CaptureConversationHandler()
        command = CaptureConversationCommand(
            conversation_id="",
            title="Test",
            content="Content",
            file_path="/path"
        )
        
        result = await handler.handle(command)
        
        assert result.is_failure
        assert "conversation_id" in result.errors[0].lower()
    
    async def test_handler_rejects_empty_title(self):
        """Test handler rejects empty title"""
        handler = CaptureConversationHandler()
        command = CaptureConversationCommand(
            conversation_id="conv-001",
            title="",
            content="Content",
            file_path="/path"
        )
        
        result = await handler.handle(command)
        
        assert result.is_failure
        assert "title" in result.errors[0].lower()
    
    async def test_handler_rejects_empty_content(self):
        """Test handler rejects empty content"""
        handler = CaptureConversationHandler()
        command = CaptureConversationCommand(
            conversation_id="conv-001",
            title="Test",
            content="",
            file_path="/path"
        )
        
        result = await handler.handle(command)
        
        assert result.is_failure
        assert "content" in result.errors[0].lower()


@pytest.mark.asyncio
class TestLearnPatternCommand:
    """Tests for LearnPatternCommand"""
    
    async def test_command_creation(self):
        """Test creating a learn pattern command"""
        command = LearnPatternCommand(
            pattern_id="pat-001",
            pattern_name="Test Pattern",
            pattern_type="code_structure",
            pattern_content="# Test pattern",
            source_conversation_id="conv-001",
            namespace="test.namespace",
            confidence_score=0.85
        )
        
        assert command.pattern_id == "pat-001"
        assert command.pattern_name == "Test Pattern"
        assert command.pattern_type == "code_structure"
        assert command.namespace == "test.namespace"
        assert command.confidence_score == 0.85


@pytest.mark.asyncio
class TestLearnPatternHandler:
    """Tests for LearnPatternHandler"""
    
    async def test_handler_success(self):
        """Test handler succeeds with valid pattern"""
        handler = LearnPatternHandler()
        command = LearnPatternCommand(
            pattern_id="pat-001",
            pattern_name="Test Pattern",
            pattern_type="code_structure",
            pattern_content="# Pattern content",
            source_conversation_id="conv-001",
            namespace="test.namespace",
            confidence_score=0.85
        )
        
        result = await handler.handle(command)
        
        assert result.is_success
        assert result.value == "pat-001"
    
    async def test_handler_warns_experimental_confidence(self, caplog):
        """Test handler warns on experimental confidence"""
        import logging
        caplog.set_level(logging.WARNING)
        
        handler = LearnPatternHandler()
        command = LearnPatternCommand(
            pattern_id="pat-001",
            pattern_name="Test Pattern",
            pattern_type="code_structure",
            pattern_content="# Pattern content",
            source_conversation_id="conv-001",
            namespace="test.namespace",
            confidence_score=0.65  # Experimental level
        )
        
        result = await handler.handle(command)
        
        assert result.is_success
        assert "experimental" in caplog.text.lower()
    
    async def test_handler_rejects_invalid_namespace(self):
        """Test handler rejects invalid namespace"""
        handler = LearnPatternHandler()
        command = LearnPatternCommand(
            pattern_id="pat-001",
            pattern_name="Test Pattern",
            pattern_type="code_structure",
            pattern_content="# Pattern content",
            source_conversation_id="conv-001",
            namespace="",  # Invalid
            confidence_score=0.85
        )
        
        result = await handler.handle(command)
        
        assert result.is_failure
    
    async def test_handler_rejects_empty_pattern_name(self):
        """Test handler rejects empty pattern name"""
        handler = LearnPatternHandler()
        command = LearnPatternCommand(
            pattern_id="pat-001",
            pattern_name="",
            pattern_type="code_structure",
            pattern_content="# Pattern content",
            source_conversation_id="conv-001",
            namespace="test.namespace",
            confidence_score=0.85
        )
        
        result = await handler.handle(command)
        
        assert result.is_failure
        assert "pattern_name" in result.errors[0].lower()


@pytest.mark.asyncio
class TestUpdateContextRelevanceCommand:
    """Tests for UpdateContextRelevanceCommand"""
    
    async def test_command_creation(self):
        """Test creating update relevance command"""
        command = UpdateContextRelevanceCommand(
            conversation_id="conv-001",
            new_relevance_score=0.90,
            reason="User marked as highly relevant"
        )
        
        assert command.conversation_id == "conv-001"
        assert command.new_relevance_score == 0.90
        assert command.reason == "User marked as highly relevant"


@pytest.mark.asyncio
class TestUpdateContextRelevanceHandler:
    """Tests for UpdateContextRelevanceHandler"""
    
    async def test_handler_success(self):
        """Test handler succeeds with valid input"""
        handler = UpdateContextRelevanceHandler()
        command = UpdateContextRelevanceCommand(
            conversation_id="conv-001",
            new_relevance_score=0.90,
            reason="User feedback"
        )
        
        result = await handler.handle(command)
        
        assert result.is_success
        assert result.value is True
    
    async def test_handler_rejects_invalid_score(self):
        """Test handler rejects invalid relevance score"""
        handler = UpdateContextRelevanceHandler()
        command = UpdateContextRelevanceCommand(
            conversation_id="conv-001",
            new_relevance_score=1.5,  # Out of range
            reason="Test"
        )
        
        result = await handler.handle(command)
        
        assert result.is_failure
    
    async def test_handler_logs_score_change(self, caplog):
        """Test handler logs score changes"""
        import logging
        caplog.set_level(logging.INFO)
        
        handler = UpdateContextRelevanceHandler()
        command = UpdateContextRelevanceCommand(
            conversation_id="conv-001",
            new_relevance_score=0.90,
            reason="User feedback"
        )
        
        result = await handler.handle(command)
        
        assert result.is_success
        assert "Relevance updated" in caplog.text or "conv-001" in caplog.text


@pytest.mark.asyncio
class TestUpdatePatternConfidenceCommand:
    """Tests for UpdatePatternConfidenceCommand"""
    
    async def test_command_creation(self):
        """Test creating update confidence command"""
        command = UpdatePatternConfidenceCommand(
            pattern_id="pat-001",
            was_successful=True,
            context_id="ctx-001"
        )
        
        assert command.pattern_id == "pat-001"
        assert command.was_successful is True
        assert command.context_id == "ctx-001"


@pytest.mark.asyncio
class TestUpdatePatternConfidenceHandler:
    """Tests for UpdatePatternConfidenceHandler"""
    
    async def test_handler_success(self):
        """Test handler succeeds with valid input"""
        handler = UpdatePatternConfidenceHandler()
        command = UpdatePatternConfidenceCommand(
            pattern_id="pat-001",
            was_successful=True,
            context_id="ctx-001"
        )
        
        result = await handler.handle(command)
        
        assert result.is_success
        assert result.value is True
    
    async def test_handler_tracks_failure(self):
        """Test handler tracks pattern failures"""
        handler = UpdatePatternConfidenceHandler()
        command = UpdatePatternConfidenceCommand(
            pattern_id="pat-001",
            was_successful=False,
            context_id="ctx-001"
        )
        
        result = await handler.handle(command)
        
        assert result.is_success
    
    async def test_handler_rejects_empty_pattern_id(self):
        """Test handler rejects empty pattern ID"""
        handler = UpdatePatternConfidenceHandler()
        command = UpdatePatternConfidenceCommand(
            pattern_id="",
            was_successful=True,
            context_id="ctx-001"
        )
        
        result = await handler.handle(command)
        
        assert result.is_failure


@pytest.mark.asyncio
class TestDeleteConversationCommand:
    """Tests for DeleteConversationCommand"""
    
    async def test_command_creation(self):
        """Test creating delete command"""
        command = DeleteConversationCommand(
            conversation_id="conv-001",
            delete_related_patterns=True
        )
        
        assert command.conversation_id == "conv-001"
        assert command.delete_related_patterns is True


@pytest.mark.asyncio
class TestDeleteConversationHandler:
    """Tests for DeleteConversationHandler"""
    
    async def test_handler_success(self):
        """Test handler succeeds"""
        handler = DeleteConversationHandler()
        command = DeleteConversationCommand(
            conversation_id="conv-001",
            delete_related_patterns=False
        )
        
        result = await handler.handle(command)
        
        assert result.is_success
        assert result.value is True
    
    async def test_handler_with_cascade_delete(self):
        """Test handler with cascade delete"""
        handler = DeleteConversationHandler()
        command = DeleteConversationCommand(
            conversation_id="conv-001",
            delete_related_patterns=True
        )
        
        result = await handler.handle(command)
        
        assert result.is_success
    
    async def test_handler_rejects_empty_id(self):
        """Test handler rejects empty ID"""
        handler = DeleteConversationHandler()
        command = DeleteConversationCommand(
            conversation_id="",
            delete_related_patterns=False
        )
        
        result = await handler.handle(command)
        
        assert result.is_failure
        assert "conversation_id" in result.errors[0].lower()
