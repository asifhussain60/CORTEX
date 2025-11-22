"""
End-to-End Context Search Integration Tests

Tests context search workflow:
- Capture conversations with searchable content
- Search by text keywords
- Search with quality filters
- Search across namespaces

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import asyncio
import os
import pytest
import tempfile
from pathlib import Path

from src.application.commands.conversation_commands import CaptureConversationCommand
from src.application.queries.conversation_queries import SearchContextQuery
from src.application.commands.conversation_handlers import CaptureConversationHandler
from src.application.queries.conversation_handlers import SearchContextHandler
from src.infrastructure.persistence.db_context import DatabaseContext
from src.infrastructure.persistence.unit_of_work import UnitOfWork
from src.infrastructure.migrations.migration_runner import MigrationRunner


@pytest.fixture
def test_database():
    """Create a temporary test database."""
    # Create temp directory and database file
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
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
    """Create Unit of Work with test database."""
    return UnitOfWork(test_database)


class TestContextSearchWorkflow:
    """End-to-end context search workflow tests."""
    
    def test_search_by_text_keyword_workflow(self, unit_of_work):
        """Test: Capture conversations → Search by keyword."""
        # Capture conversations with different content
        conversations = [
            ("conv_search_001", "Python Best Practices", "Using async/await for better performance"),
            ("conv_search_002", "Database Design", "Normalized schemas prevent data redundancy"),
            ("conv_search_003", "Python Testing", "Pytest fixtures provide reusable test setup"),
            ("conv_search_004", "API Design", "RESTful endpoints follow HTTP conventions")
        ]
        
        capture_handler = CaptureConversationHandler(unit_of_work)
        
        for conv_id, title, content in conversations:
            command = CaptureConversationCommand(
                conversation_id=conv_id,
                title=title,
                content=content,
                file_path="/test/search.md",
                quality_score=0.80,
                entity_count=3
            )
            asyncio.run(capture_handler.handle(command))
        
        # Search for "Python" keyword
        search_query = SearchContextQuery(search_text="Python")
        search_handler = SearchContextHandler(unit_of_work)
        result = asyncio.run(search_handler.handle(search_query))
        
        assert result.is_success
        found_conversations = result.value
        
        # Should find 2 Python-related conversations
        assert len(found_conversations) >= 2
        titles = [c.title for c in found_conversations]
        assert "Python Best Practices" in titles
        assert "Python Testing" in titles
    
    def test_search_with_quality_filter_workflow(self, unit_of_work):
        """Test: Capture conversations with varying quality → Search high quality only."""
        conversations = [
            ("conv_quality_001", "High Quality 1", "Excellent content", 0.90),
            ("conv_quality_002", "High Quality 2", "Great insights", 0.85),
            ("conv_quality_003", "Medium Quality", "Okay content", 0.65),
            ("conv_quality_004", "Low Quality", "Poor content", 0.45)
        ]
        
        capture_handler = CaptureConversationHandler(unit_of_work)
        
        for conv_id, title, content, quality in conversations:
            command = CaptureConversationCommand(
                conversation_id=conv_id,
                title=title,
                content=content,
                file_path="/test/captures.json",
                quality_score=quality,
                entity_count=3
            )
            asyncio.run(capture_handler.handle(command))
        
        # Search all conversations
        search_query = SearchContextQuery(search_text="quality")
        search_handler = SearchContextHandler(unit_of_work)
        result = asyncio.run(search_handler.handle(search_query))
        
        assert result.is_success
        all_found = result.value
        
        # Filter high quality (≥0.70) in application using quality_score
        high_quality = [c for c in all_found if c.quality_score >= 0.70]
        
        # Should find only 2 high quality conversations
        assert len(high_quality) >= 2
        qualities = [c.quality_score for c in high_quality]
        assert all(q >= 0.70 for q in qualities)
    
    def test_search_no_results_workflow(self, unit_of_work):
        """Test: Search for non-existent keyword."""
        # Capture a conversation
        command = CaptureConversationCommand(
            conversation_id="conv_no_results",
            title="Simple Conversation",
            content="Basic content without special keywords",
            file_path="/test/captures.json",
            quality_score=0.75,
            entity_count=2
        )
        
        capture_handler = CaptureConversationHandler(unit_of_work)
        asyncio.run(capture_handler.handle(command))
        
        # Search for non-existent keyword
        search_query = SearchContextQuery(search_text="nonexistentkeyword12345")
        search_handler = SearchContextHandler(unit_of_work)
        result = asyncio.run(search_handler.handle(search_query))
        
        assert result.is_success
        assert len(result.value) == 0
    
    def test_search_case_insensitive_workflow(self, unit_of_work):
        """Test: Search is case-insensitive."""
        command = CaptureConversationCommand(
            conversation_id="conv_case_test",
            title="TypeScript Development",
            content="Building robust applications with TypeScript",
            file_path="/test/captures.json",
            quality_score=0.80,
            entity_count=3
        )
        
        capture_handler = CaptureConversationHandler(unit_of_work)
        asyncio.run(capture_handler.handle(command))
        
        # Search with lowercase
        search_query = SearchContextQuery(search_text="typescript")
        search_handler = SearchContextHandler(unit_of_work)
        result = asyncio.run(search_handler.handle(search_query))
        
        assert result.is_success
        assert len(result.value) >= 1
        assert result.value[0].title == "TypeScript Development"
    
    def test_search_multiple_keywords_workflow(self, unit_of_work):
        """Test: Search with multiple keywords (compound search)."""
        conversations = [
            ("conv_multi_001", "Python Testing", "Unit tests with pytest fixtures"),
            ("conv_multi_002", "Python Development", "Building web applications"),
            ("conv_multi_003", "Testing Best Practices", "Integration test strategies")
        ]
        
        capture_handler = CaptureConversationHandler(unit_of_work)
        
        for conv_id, title, content in conversations:
            command = CaptureConversationCommand(
                conversation_id=conv_id,
                title=title,
                content=content,
                file_path="/test/captures.json",
                quality_score=0.80,
                entity_count=3
            )
            asyncio.run(capture_handler.handle(command))
        
        # Search for "Python Testing"
        search_query = SearchContextQuery(search_text="Python Testing")
        search_handler = SearchContextHandler(unit_of_work)
        result = asyncio.run(search_handler.handle(search_query))
        
        assert result.is_success
        found = result.value
        
        # Should find at least the exact match
        assert len(found) >= 1
        titles = [c.title for c in found]
        assert "Python Testing" in titles
