"""
Tests for Conversation Repository
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta

from src.infrastructure.persistence.db_context import DatabaseContext
from src.infrastructure.persistence.repositories.conversation_repository import (
    Conversation,
    ConversationRepository
)
from src.infrastructure.migrations.migration_runner import MigrationRunner


class TestConversationRepository:
    """Test suite for ConversationRepository"""
    
    @pytest.fixture
    async def db_context(self):
        """Create test database with schema"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
            db_path = f.name
        
        # Run migrations
        runner = MigrationRunner(db_path)
        await runner.migrate()
        
        # Create and return context
        context = DatabaseContext(db_path)
        return context
    
    @pytest.fixture
    def sample_conversation(self):
        """Create a sample conversation"""
        return Conversation(
            conversation_id="conv_001",
            title="Test Conversation",
            content="This is test conversation content.",
            quality=0.85,
            participant_count=3,
            entity_count=10,
            captured_at=datetime.now(),
            namespace="engineering"
        )
    
    @pytest.mark.asyncio
    async def test_add_conversation(self, db_context, sample_conversation):
        """Test adding a conversation"""
        repo = ConversationRepository(db_context)
        
        await db_context.begin()
        await repo.add(sample_conversation)
        await db_context.commit()
        
        # Verify conversation was added
        retrieved = await repo.get_by_id("conv_001")
        assert retrieved is not None
        assert retrieved.conversation_id == "conv_001"
        assert retrieved.title == "Test Conversation"
        assert retrieved.quality == 0.85
    
    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(self, db_context):
        """Test get_by_id returns None for non-existent conversation"""
        repo = ConversationRepository(db_context)
        
        result = await repo.get_by_id("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_all_conversations(self, db_context):
        """Test retrieving all conversations"""
        repo = ConversationRepository(db_context)
        
        # Add multiple conversations
        await db_context.begin()
        for i in range(3):
            conv = Conversation(
                conversation_id=f"conv_{i:03d}",
                title=f"Conversation {i}",
                content=f"Content {i}",
                quality=0.75 + (i * 0.05),
                participant_count=2,
                entity_count=5,
                captured_at=datetime.now() - timedelta(days=i),
                namespace="test"
            )
            await repo.add(conv)
        await db_context.commit()
        
        # Get all
        all_conversations = await repo.get_all()
        assert len(all_conversations) == 3
        # Should be ordered by captured_at DESC
        assert all_conversations[0].conversation_id == "conv_000"
    
    @pytest.mark.asyncio
    async def test_update_conversation(self, db_context, sample_conversation):
        """Test updating a conversation"""
        repo = ConversationRepository(db_context)
        
        # Add conversation
        await db_context.begin()
        await repo.add(sample_conversation)
        await db_context.commit()
        
        # Update conversation
        sample_conversation.title = "Updated Title"
        sample_conversation.quality = 0.95
        
        await db_context.begin()
        await repo.update(sample_conversation)
        await db_context.commit()
        
        # Verify update
        retrieved = await repo.get_by_id("conv_001")
        assert retrieved.title == "Updated Title"
        assert retrieved.quality == 0.95
    
    @pytest.mark.asyncio
    async def test_delete_conversation(self, db_context, sample_conversation):
        """Test deleting a conversation"""
        repo = ConversationRepository(db_context)
        
        # Add conversation
        await db_context.begin()
        await repo.add(sample_conversation)
        await db_context.commit()
        
        # Verify it exists
        assert await repo.get_by_id("conv_001") is not None
        
        # Delete conversation
        await db_context.begin()
        await repo.delete(sample_conversation)
        await db_context.commit()
        
        # Verify deletion
        assert await repo.get_by_id("conv_001") is None
    
    @pytest.mark.asyncio
    async def test_get_by_namespace(self, db_context):
        """Test retrieving conversations by namespace"""
        repo = ConversationRepository(db_context)
        
        # Add conversations in different namespaces
        await db_context.begin()
        for i in range(5):
            conv = Conversation(
                conversation_id=f"conv_{i:03d}",
                title=f"Conversation {i}",
                content=f"Content {i}",
                quality=0.75,
                participant_count=2,
                entity_count=5,
                captured_at=datetime.now(),
                namespace="engineering" if i < 3 else "product"
            )
            await repo.add(conv)
        await db_context.commit()
        
        # Get by namespace
        engineering_convs = await repo.get_by_namespace("engineering")
        product_convs = await repo.get_by_namespace("product")
        
        assert len(engineering_convs) == 3
        assert len(product_convs) == 2
        assert all(c.namespace == "engineering" for c in engineering_convs)
        assert all(c.namespace == "product" for c in product_convs)
    
    @pytest.mark.asyncio
    async def test_get_high_quality(self, db_context):
        """Test retrieving high quality conversations"""
        repo = ConversationRepository(db_context)
        
        # Add conversations with varying quality
        await db_context.begin()
        qualities = [0.50, 0.65, 0.75, 0.85, 0.95]
        for i, quality in enumerate(qualities):
            conv = Conversation(
                conversation_id=f"conv_{i:03d}",
                title=f"Conversation {i}",
                content=f"Content {i}",
                quality=quality,
                participant_count=2,
                entity_count=5,
                captured_at=datetime.now(),
                namespace="test"
            )
            await repo.add(conv)
        await db_context.commit()
        
        # Get high quality (>= 0.70)
        high_quality = await repo.get_high_quality(0.70)
        
        assert len(high_quality) == 3
        assert all(c.quality >= 0.70 for c in high_quality)
        # Should be ordered by quality DESC
        assert high_quality[0].quality == 0.95
        assert high_quality[1].quality == 0.85
        assert high_quality[2].quality == 0.75
    
    @pytest.mark.asyncio
    async def test_count_conversations(self, db_context):
        """Test counting conversations"""
        repo = ConversationRepository(db_context)
        
        # Add conversations
        await db_context.begin()
        for i in range(7):
            conv = Conversation(
                conversation_id=f"conv_{i:03d}",
                title=f"Conversation {i}",
                content=f"Content {i}",
                quality=0.75,
                participant_count=2,
                entity_count=5,
                captured_at=datetime.now(),
                namespace="test"
            )
            await repo.add(conv)
        await db_context.commit()
        
        count = await repo.count()
        assert count == 7
    
    @pytest.mark.asyncio
    async def test_conversation_timestamps(self, db_context, sample_conversation):
        """Test that timestamps are set correctly"""
        repo = ConversationRepository(db_context)
        
        await db_context.begin()
        await repo.add(sample_conversation)
        await db_context.commit()
        
        retrieved = await repo.get_by_id("conv_001")
        assert retrieved.created_at is not None
        assert retrieved.updated_at is not None
        assert isinstance(retrieved.created_at, datetime)
        assert isinstance(retrieved.updated_at, datetime)
