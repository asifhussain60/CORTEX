"""
Integration tests for CORTEX handlers with repository layer.

These tests verify that command/query handlers work correctly with
the repository layer, database context, and Unit of Work pattern.

Test Coverage:
- Command handlers with database persistence
- Query handlers with database retrieval
- Transaction management (commit/rollback)
- End-to-end workflows
"""

import pytest
import os
import tempfile
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
    SearchContextQuery,
    GetConversationByIdQuery,
    GetPatternByIdQuery,
    GetRecentConversationsQuery,
    GetPatternsByNamespaceQuery
)
from src.application.queries.conversation_handlers import (
    SearchContextHandler,
    GetConversationByIdHandler,
    GetPatternByIdHandler,
    GetRecentConversationsHandler,
    GetPatternsByNamespaceHandler
)

# Infrastructure layer
from src.infrastructure.persistence.db_context import DatabaseContext
from src.infrastructure.persistence.unit_of_work import UnitOfWork
from src.infrastructure.migrations.migration_runner import MigrationRunner


@pytest.fixture
async def test_database():
    """Create a temporary test database"""
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_cortex.db")
    
    # Initialize database context
    db_context = DatabaseContext(db_path)
    
    # Run migrations
    migrations_dir = Path(__file__).parent.parent.parent / "src" / "infrastructure" / "migrations"
    runner = MigrationRunner(db_path, str(migrations_dir))
    await runner.apply_pending_migrations()
    
    yield db_context
    
    # Cleanup
    await db_context.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    os.rmdir(temp_dir)


@pytest.fixture
def unit_of_work(test_database):
    """Create Unit of Work with test database"""
    return UnitOfWork(test_database)


# ============================================================================
# COMMAND HANDLER INTEGRATION TESTS
# ============================================================================

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
        assert conversation.namespace == "test"


@pytest.mark.asyncio
async def test_capture_conversation_rejects_low_quality(unit_of_work):
    """Test CaptureConversationHandler rejects low-quality conversations"""
    # Arrange
    handler = CaptureConversationHandler(unit_of_work)
    command = CaptureConversationCommand(
        conversation_id="test-conv-low",
        title="Low Quality",
        content="Short",  # Too short
        file_path="/test/conv.json",
        quality_score=None,  # Let handler calculate
        entity_count=0
    )
    
    # Act
    result = await handler.handle(command)
    
    # Assert
    assert result.is_failure
    assert "quality too low" in result.errors[0].lower()


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
        assert pattern.pattern_type == "code_structure"


@pytest.mark.asyncio
async def test_update_pattern_confidence_modifies_existing_pattern(unit_of_work):
    """Test UpdatePatternConfidenceHandler updates pattern confidence"""
    # Arrange - Create initial pattern
    learn_handler = LearnPatternHandler(unit_of_work)
    learn_command = LearnPatternCommand(
        pattern_id="test-pat-002",
        pattern_name="Confidence Test",
        pattern_type="test",
        pattern_content="content",
        source_conversation_id="conv-001"
        confidence_score=0.75,
        learned_at=datetime.now()
    )
    await learn_handler.handle(learn_command)
    
    # Act - Update confidence
    update_handler = UpdatePatternConfidenceHandler(unit_of_work)
    update_command = UpdatePatternConfidenceCommand(
        pattern_id="test-pat-002",
        was_successful=True,
        context_id="ctx-001",
        updated_at=datetime.now()
    )
    result = await update_handler.handle(update_command)
    
    # Assert
    assert result.is_success
    
    # Verify update
    async with unit_of_work as uow:
        pattern = await uow.patterns.get_by_id("test-pat-002")
        assert pattern.observation_count == 2  # 1 initial + 1 new
        assert pattern.confidence > 0.75  # Should increase with successful observation


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


@pytest.mark.asyncio
async def test_delete_conversation_cascades_patterns(unit_of_work):
    """Test DeleteConversationHandler with cascade delete of patterns"""
    # Arrange - Create conversation and pattern
    capture_handler = CaptureConversationHandler(unit_of_work)
    capture_command = CaptureConversationCommand(
        conversation_id="test-conv-cascade",
        title="Cascade Test",
        content="User: Test\nAssistant: Response\nUser: More\nAssistant: More response",
        file_path="/test/cascade.json",
        quality_score=0.85
    )
    await capture_handler.handle(capture_command)
    
    learn_handler = LearnPatternHandler(unit_of_work)
    learn_command = LearnPatternCommand(
        pattern_id="test-pat-cascade",
        pattern_name="Cascade Pattern",
        pattern_type="test",
        pattern_content="content",
        source_conversation_id="test-conv-cascade"
        confidence_score=0.85,
        learned_at=datetime.now()
    )
    await learn_handler.handle(learn_command)
    
    # Act - Delete conversation with cascade
    delete_handler = DeleteConversationHandler(unit_of_work)
    delete_command = DeleteConversationCommand(
        conversation_id="test-conv-cascade",
        delete_related_patterns=True
    )
    result = await delete_handler.handle(delete_command)
    
    # Assert
    assert result.is_success
    
    # Verify cascade deletion
    async with unit_of_work as uow:
        conversation = await uow.conversations.get_by_id("test-conv-cascade")
        pattern = await uow.patterns.get_by_id("test-pat-cascade")
        assert conversation is None
        assert pattern is None


# ============================================================================
# QUERY HANDLER INTEGRATION TESTS
# ============================================================================

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
        source_conversation_id="conv-001"
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
async def test_search_context_finds_matching_conversations(unit_of_work):
    """Test SearchContextHandler finds conversations matching search text"""
    # Arrange - Create multiple conversations
    capture_handler = CaptureConversationHandler(unit_of_work)
    
    conversations = [
        ("search-001", "Python Testing", "User: How to test Python?\nAssistant: Use pytest\nUser: Thanks\nAssistant: Welcome"),
        ("search-002", "JavaScript Testing", "User: How to test JS?\nAssistant: Use Jest\nUser: Great\nAssistant: Glad to help"),
        ("search-003", "Database Design", "User: How to design database?\nAssistant: Use normalization\nUser: OK\nAssistant: Good"),
    ]
    
    for conv_id, title, content in conversations:
        command = CaptureConversationCommand(
            conversation_id=conv_id,
            title=title,
            content=content,
            file_path=f"/test/{conv_id}.json",
            quality_score=0.85
        )
        await capture_handler.handle(command)
    
    # Act - Search for "testing"
    search_handler = SearchContextHandler(unit_of_work)
    query = SearchContextQuery(
        search_text="testing",
        namespace_filter="test",
        min_relevance=0.70,
        max_results=10
    )
    result = await search_handler.handle(query)
    
    # Assert
    assert result.is_success
    assert len(result.value) == 2  # Should find Python Testing and JavaScript Testing
    assert all("Testing" in conv.title for conv in result.value)


@pytest.mark.asyncio
async def test_get_recent_conversations_returns_sorted_list(unit_of_work):
    """Test GetRecentConversationsHandler returns conversations sorted by date"""
    # Arrange - Create conversations with different dates
    capture_handler = CaptureConversationHandler(unit_of_work)
    
    base_date = datetime(2024, 1, 1, 12, 0, 0)
    for i in range(5):
        command = CaptureConversationCommand(
            conversation_id=f"recent-{i:03d}",
            title=f"Conversation {i}",
            content="User: Test\nAssistant: Response\nUser: More\nAssistant: More response",
            file_path=f"/test/recent-{i}.json",
            quality_score=0.85
            captured_at=datetime(2024, 1, i+1, 12, 0, 0)  # Different dates
        )
        await capture_handler.handle(command)
    
    # Act - Get recent conversations
    query_handler = GetRecentConversationsHandler(unit_of_work)
    query = GetRecentConversationsQuery(
        namespace_filter="test",
        max_results=3
    )
    result = await query_handler.handle(query)
    
    # Assert
    assert result.is_success
    assert len(result.value) == 3
    # Most recent first
    assert result.value[0].conversation_id == "recent-004"
    assert result.value[1].conversation_id == "recent-003"
    assert result.value[2].conversation_id == "recent-002"


@pytest.mark.asyncio
async def test_get_patterns_by_namespace_filters_by_confidence(unit_of_work):
    """Test GetPatternsByNamespaceHandler filters patterns by confidence"""
    # Arrange - Create patterns with different confidence scores
    learn_handler = LearnPatternHandler(unit_of_work)
    
    patterns = [
        ("pat-ns-001", "High Confidence", 0.95),
        ("pat-ns-002", "Medium Confidence", 0.75),
        ("pat-ns-003", "Low Confidence", 0.55),
    ]
    
    for pat_id, name, confidence in patterns:
        command = LearnPatternCommand(
            pattern_id=pat_id,
            pattern_name=name,
            pattern_type="test",
            pattern_content="content",
            source_conversation_id="conv-001",
            namespace="test.namespace",
            confidence_score=confidence,
            learned_at=datetime.now()
        )
        await learn_handler.handle(command)
    
    # Act - Get patterns with min confidence 0.70
    query_handler = GetPatternsByNamespaceHandler(unit_of_work)
    query = GetPatternsByNamespaceQuery(
        namespace="test.namespace",
        min_confidence=0.70,
        max_results=10
    )
    result = await query_handler.handle(query)
    
    # Assert
    assert result.is_success
    assert len(result.value) == 2  # Should find only high and medium confidence
    assert all(p.confidence_score >= 0.70 for p in result.value)
    # Should be sorted by confidence (highest first)
    assert result.value[0].confidence_score >= result.value[1].confidence_score


# ============================================================================
# END-TO-END WORKFLOW TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_complete_workflow_capture_learn_search(unit_of_work):
    """Test complete workflow: capture conversation → learn pattern → search"""
    # Step 1: Capture conversation
    capture_handler = CaptureConversationHandler(unit_of_work)
    capture_command = CaptureConversationCommand(
        conversation_id="workflow-conv",
        title="API Design Pattern",
        content="User: How to design REST API?\nAssistant: Use RESTful principles\nUser: Examples?\nAssistant: GET /users, POST /users",
        file_path="/workflow/api.json",
        quality_score=0.90
    )
    capture_result = await capture_handler.handle(capture_command)
    assert capture_result.is_success
    
    # Step 2: Learn pattern from conversation
    learn_handler = LearnPatternHandler(unit_of_work)
    learn_command = LearnPatternCommand(
        pattern_id="workflow-pattern",
        pattern_name="REST API Design",
        pattern_type="architecture",
        pattern_content="RESTful API design with resource-based URLs",
        source_conversation_id="workflow-conv",
        namespace="workflow.patterns",
        confidence_score=0.85,
        learned_at=datetime.now()
    )
    learn_result = await learn_handler.handle(learn_command)
    assert learn_result.is_success
    
    # Step 3: Search for conversation
    search_handler = SearchContextHandler(unit_of_work)
    search_query = SearchContextQuery(
        search_text="API",
        namespace_filter="workflow",
        min_relevance=0.70,
        max_results=10
    )
    search_result = await search_handler.handle(search_query)
    assert search_result.is_success
    assert len(search_result.value) == 1
    assert search_result.value[0].conversation_id == "workflow-conv"
    
    # Step 4: Get conversation by ID
    get_conv_handler = GetConversationByIdHandler(unit_of_work)
    get_conv_query = GetConversationByIdQuery(conversation_id="workflow-conv")
    get_conv_result = await get_conv_handler.handle(get_conv_query)
    assert get_conv_result.is_success
    assert get_conv_result.value.title == "API Design Pattern"
    
    # Step 5: Get pattern by ID
    get_pat_handler = GetPatternByIdHandler(unit_of_work)
    get_pat_query = GetPatternByIdQuery(pattern_id="workflow-pattern")
    get_pat_result = await get_pat_handler.handle(get_pat_query)
    assert get_pat_result.is_success
    assert get_pat_result.value.pattern_name == "REST API Design"


@pytest.mark.asyncio
async def test_transaction_rollback_on_failure(unit_of_work):
    """Test that Unit of Work rolls back on failure"""
    # Arrange
    capture_handler = CaptureConversationHandler(unit_of_work)
    
    # Act - Create conversation that will be committed
    good_command = CaptureConversationCommand(
        conversation_id="rollback-good",
        title="Good Conversation",
        content="User: Test\nAssistant: Response\nUser: More\nAssistant: More response",
        file_path="/test/good.json",
        quality_score=0.85
    )
    good_result = await capture_handler.handle(good_command)
    assert good_result.is_success
    
    # Act - Try to create conversation with invalid data (should fail validation)
    bad_command = CaptureConversationCommand(
        conversation_id="",  # Empty ID should fail
        title="Bad Conversation",
        content="Content",
        file_path="/test/bad.json",
        quality_score=0.85
    )
    bad_result = await capture_handler.handle(bad_command)
    assert bad_result.is_failure
    
    # Assert - Good conversation should exist, bad one should not
    async with unit_of_work as uow:
        good_conv = await uow.conversations.get_by_id("rollback-good")
        bad_conv = await uow.conversations.get_by_id("")
        assert good_conv is not None
        assert bad_conv is None
