"""
Integration tests for CORTEX handlers with repository layer.

These tests verify that command/query handlers work correctly with
the repository layer, database context, and Unit of Work pattern.
"""

import pytest
import os
import tempfile
import asyncio
from datetime import datetime
from pathlib import Path

# Application layer
from src.application.commands.conversation_commands import (
    CaptureConversationCommand,
    LearnPatternCommand,
    UpdatePatternConfidenceCommand,
    DeleteConversationCommand
)
from src.application.commands.conversation_handlers import (
    CaptureConversationHandler,
    LearnPatternHandler,
    UpdatePatternConfidenceHandler,
    DeleteConversationHandler
)
from src.application.queries.conversation_queries import (
    GetConversationByIdQuery,
    GetPatternByIdQuery
)
from src.application.queries.conversation_handlers import (
    GetConversationByIdHandler,
    GetPatternByIdHandler
)

# Infrastructure layer
from src.infrastructure.persistence.db_context import DatabaseContext
from src.infrastructure.persistence.unit_of_work import UnitOfWork
from src.infrastructure.migrations.migration_runner import MigrationRunner


@pytest.fixture
def test_database():
    """Create a temporary test database"""
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_cortex.db")
    
    # Initialize database context
    db_context = DatabaseContext(db_path)
    
    # Run migrations synchronously
    migrations_dir = Path(__file__).parent.parent.parent / "src" / "infrastructure" / "migrations"
    runner = MigrationRunner(db_path, str(migrations_dir))
    asyncio.run(runner.migrate())
    
    yield db_context
    
    # Cleanup
    asyncio.run(db_context.close())
    if os.path.exists(db_path):
        os.remove(db_path)
    os.rmdir(temp_dir)


@pytest.fixture
def unit_of_work(test_database):
    """Create Unit of Work with test database"""
    return UnitOfWork(test_database)


@pytest.mark.asyncio
async def test_capture_conversation_handler_persists_to_database(unit_of_work):
    """Test CaptureConversationHandler stores conversation in database"""
    # Arrange
    handler = CaptureConversationHandler(unit_of_work)
    command = CaptureConversationCommand(
        conversation_id="test-conv-001",
        title="Test Conversation",
        content="User: Hello\nAssistant: Hi there!\nUser: How are you?\nAssistant: I'm doing great!",
        file_path="/test/conv.json",
        quality_score=0.85,
        entity_count=5,
        captured_at=datetime.now()
    )
    
    # Act
    result = await handler.handle(command)
    
    # Assert
    assert result.is_success
    assert result.value == "test-conv-001"
    
    # Verify persistence
    async with unit_of_work as uow:
        conversation = await uow.conversations.get_by_id("test-conv-001")
        assert conversation is not None
        assert conversation.title == "Test Conversation"
        assert conversation.quality == 0.85


@pytest.mark.asyncio
async def test_learn_pattern_handler_persists_to_database(unit_of_work):
    """Test LearnPatternHandler stores pattern in database"""
    # Arrange
    handler = LearnPatternHandler(unit_of_work)
    command = LearnPatternCommand(
        pattern_id="test-pat-001",
        pattern_name="Test Pattern",
        pattern_type="code_structure",
        pattern_content="def test(): pass",
        source_conversation_id="test-conv-001",
        namespace="test.patterns",
        confidence_score=0.85,
        tags=["test", "pattern"],
        learned_at=datetime.now()
    )
    
    # Act
    result = await handler.handle(command)
    
    # Assert
    assert result.is_success
    assert result.value == "test-pat-001"
    
    # Verify persistence
    async with unit_of_work as uow:
        pattern = await uow.patterns.get_by_id("test-pat-001")
        assert pattern is not None
        assert pattern.pattern_name == "Test Pattern"
        assert pattern.confidence == 0.85


@pytest.mark.asyncio
async def test_get_conversation_by_id_retrieves_from_database(unit_of_work):
    """Test GetConversationByIdHandler retrieves conversation from database"""
    # Arrange - Create conversation
    capture_handler = CaptureConversationHandler(unit_of_work)
    capture_command = CaptureConversationCommand(
        conversation_id="test-conv-retrieve",
        title="Retrieve Test",
        content="User: Hello\nAssistant: Hi\nUser: Test\nAssistant: Response",
        file_path="/test/retrieve.json",
        quality_score=0.85
    )
    await capture_handler.handle(capture_command)
    
    # Act - Retrieve conversation
    query_handler = GetConversationByIdHandler(unit_of_work)
    query = GetConversationByIdQuery(conversation_id="test-conv-retrieve")
    result = await query_handler.handle(query)
    
    # Assert
    assert result.is_success
    assert result.value is not None
    assert result.value.conversation_id == "test-conv-retrieve"
    assert result.value.title == "Retrieve Test"
    assert result.value.quality_score == 0.85


@pytest.mark.asyncio
async def test_get_pattern_by_id_retrieves_from_database(unit_of_work):
    """Test GetPatternByIdHandler retrieves pattern from database"""
    # Arrange - Create pattern
    learn_handler = LearnPatternHandler(unit_of_work)
    learn_command = LearnPatternCommand(
        pattern_id="test-pat-retrieve",
        pattern_name="Retrieve Pattern",
        pattern_type="test",
        pattern_content="def test(): return True",
        source_conversation_id="conv-001",
        namespace="test",
        confidence_score=0.90,
        learned_at=datetime.now()
    )
    await learn_handler.handle(learn_command)
    
    # Act - Retrieve pattern
    query_handler = GetPatternByIdHandler(unit_of_work)
    query = GetPatternByIdQuery(pattern_id="test-pat-retrieve")
    result = await query_handler.handle(query)
    
    # Assert
    assert result.is_success
    assert result.value is not None
    assert result.value.pattern_id == "test-pat-retrieve"
    assert result.value.pattern_name == "Retrieve Pattern"
    assert result.value.confidence_score == 0.90


@pytest.mark.asyncio
async def test_delete_conversation_removes_from_database(unit_of_work):
    """Test DeleteConversationHandler removes conversation from database"""
    # Arrange - Create conversation
    capture_handler = CaptureConversationHandler(unit_of_work)
    capture_command = CaptureConversationCommand(
        conversation_id="test-conv-delete",
        title="To Delete",
        content="User: Test\nAssistant: Response\nUser: More\nAssistant: More response",
        file_path="/test/delete.json",
        quality_score=0.85
    )
    await capture_handler.handle(capture_command)
    
    # Act - Delete conversation
    delete_handler = DeleteConversationHandler(unit_of_work)
    delete_command = DeleteConversationCommand(
        conversation_id="test-conv-delete",
        delete_related_patterns=False
    )
    result = await delete_handler.handle(delete_command)
    
    # Assert
    assert result.is_success
    
    # Verify deletion
    async with unit_of_work as uow:
        conversation = await uow.conversations.get_by_id("test-conv-delete")
        assert conversation is None
