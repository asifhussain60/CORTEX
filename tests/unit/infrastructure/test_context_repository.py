"""
Tests for Context Repository
"""

import pytest
import tempfile
import os
from datetime import datetime

from src.infrastructure.persistence.db_context import DatabaseContext
from src.infrastructure.persistence.repositories.context_repository import (
    ContextItem,
    ContextRepository
)
from src.infrastructure.migrations.migration_runner import MigrationRunner


class TestContextRepository:
    """Test suite for ContextRepository"""
    
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
    def sample_context_item(self):
        """Create a sample context item"""
        return ContextItem(
            context_id="context_001",
            content="Test context item content",
            relevance_score=0.85,
            namespace="engineering",
            tier=1,
            source_id="source_001"
        )
    
    @pytest.mark.asyncio
    async def test_add_context_item(self, db_context, sample_context_item):
        """Test adding a context item"""
        repo = ContextRepository(db_context)
        
        await db_context.begin()
        await repo.add(sample_context_item)
        await db_context.commit()
        
        # Verify context item was added
        retrieved = await repo.get_by_id("context_001")
        assert retrieved is not None
        assert retrieved.context_id == "context_001"
        assert retrieved.content == "Test context item content"
        assert retrieved.relevance_score == 0.85
        assert retrieved.tier == 1
    
    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(self, db_context):
        """Test get_by_id returns None for non-existent context item"""
        repo = ContextRepository(db_context)
        
        result = await repo.get_by_id("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_all_context_items(self, db_context):
        """Test retrieving all context items"""
        repo = ContextRepository(db_context)
        
        # Add multiple context items
        await db_context.begin()
        for i in range(3):
            item = ContextItem(
                context_id=f"context_{i:03d}",
                content=f"Content {i}",
                relevance_score=0.75 + (i * 0.05),
                namespace="test",
                tier=1
            )
            await repo.add(item)
        await db_context.commit()
        
        # Get all
        all_items = await repo.get_all()
        assert len(all_items) == 3
        # Should be ordered by relevance_score DESC
        assert all_items[0].relevance_score == 0.85
    
    @pytest.mark.asyncio
    async def test_update_context_item(self, db_context, sample_context_item):
        """Test updating a context item"""
        repo = ContextRepository(db_context)
        
        # Add context item
        await db_context.begin()
        await repo.add(sample_context_item)
        await db_context.commit()
        
        # Update context item
        sample_context_item.content = "Updated content"
        sample_context_item.relevance_score = 0.95
        
        await db_context.begin()
        await repo.update(sample_context_item)
        await db_context.commit()
        
        # Verify update
        retrieved = await repo.get_by_id("context_001")
        assert retrieved.content == "Updated content"
        assert retrieved.relevance_score == 0.95
    
    @pytest.mark.asyncio
    async def test_delete_context_item(self, db_context, sample_context_item):
        """Test deleting a context item"""
        repo = ContextRepository(db_context)
        
        # Add context item
        await db_context.begin()
        await repo.add(sample_context_item)
        await db_context.commit()
        
        # Verify it exists
        assert await repo.get_by_id("context_001") is not None
        
        # Delete context item
        await db_context.begin()
        await repo.delete(sample_context_item)
        await db_context.commit()
        
        # Verify deletion
        assert await repo.get_by_id("context_001") is None
    
    @pytest.mark.asyncio
    async def test_get_by_tier(self, db_context):
        """Test retrieving context items by tier"""
        repo = ContextRepository(db_context)
        
        # Add context items in different tiers
        await db_context.begin()
        for i in range(6):
            item = ContextItem(
                context_id=f"context_{i:03d}",
                content=f"Content {i}",
                relevance_score=0.80,
                namespace="test",
                tier=(i % 3) + 1  # Tiers 1, 2, 3
            )
            await repo.add(item)
        await db_context.commit()
        
        # Get by tier
        tier1_items = await repo.get_by_tier(1)
        tier2_items = await repo.get_by_tier(2)
        tier3_items = await repo.get_by_tier(3)
        
        assert len(tier1_items) == 2
        assert len(tier2_items) == 2
        assert len(tier3_items) == 2
        assert all(item.tier == 1 for item in tier1_items)
        assert all(item.tier == 2 for item in tier2_items)
        assert all(item.tier == 3 for item in tier3_items)
    
    @pytest.mark.asyncio
    async def test_get_by_relevance(self, db_context):
        """Test retrieving context items by relevance threshold"""
        repo = ContextRepository(db_context)
        
        # Add context items with varying relevance
        await db_context.begin()
        relevances = [0.50, 0.65, 0.75, 0.85, 0.95]
        for i, relevance in enumerate(relevances):
            item = ContextItem(
                context_id=f"context_{i:03d}",
                content=f"Content {i}",
                relevance_score=relevance,
                namespace="test",
                tier=1
            )
            await repo.add(item)
        await db_context.commit()
        
        # Get high relevance (>= 0.70)
        high_relevance = await repo.get_by_relevance(0.70)
        
        assert len(high_relevance) == 3
        assert all(item.relevance_score >= 0.70 for item in high_relevance)
        # Should be ordered by relevance DESC
        assert high_relevance[0].relevance_score == 0.95
    
    @pytest.mark.asyncio
    async def test_get_by_namespace(self, db_context):
        """Test retrieving context items by namespace"""
        repo = ContextRepository(db_context)
        
        # Add context items in different namespaces
        await db_context.begin()
        for i in range(5):
            item = ContextItem(
                context_id=f"context_{i:03d}",
                content=f"Content {i}",
                relevance_score=0.80,
                namespace="engineering" if i < 3 else "product",
                tier=1
            )
            await repo.add(item)
        await db_context.commit()
        
        # Get by namespace
        engineering_items = await repo.get_by_namespace("engineering")
        product_items = await repo.get_by_namespace("product")
        
        assert len(engineering_items) == 3
        assert len(product_items) == 2
        assert all(item.namespace == "engineering" for item in engineering_items)
        assert all(item.namespace == "product" for item in product_items)
    
    @pytest.mark.asyncio
    async def test_count_context_items(self, db_context):
        """Test counting context items"""
        repo = ContextRepository(db_context)
        
        # Add context items
        await db_context.begin()
        for i in range(8):
            item = ContextItem(
                context_id=f"context_{i:03d}",
                content=f"Content {i}",
                relevance_score=0.80,
                namespace="test",
                tier=1
            )
            await repo.add(item)
        await db_context.commit()
        
        count = await repo.count()
        assert count == 8
    
    @pytest.mark.asyncio
    async def test_context_item_without_source_id(self, db_context):
        """Test context item with None source_id"""
        repo = ContextRepository(db_context)
        
        item = ContextItem(
            context_id="context_no_source",
            content="Content without source",
            relevance_score=0.75,
            namespace="test",
            tier=1,
            source_id=None
        )
        
        await db_context.begin()
        await repo.add(item)
        await db_context.commit()
        
        retrieved = await repo.get_by_id("context_no_source")
        assert retrieved.source_id is None
    
    @pytest.mark.asyncio
    async def test_context_item_timestamp(self, db_context, sample_context_item):
        """Test that created_at timestamp is set"""
        repo = ContextRepository(db_context)
        
        await db_context.begin()
        await repo.add(sample_context_item)
        await db_context.commit()
        
        retrieved = await repo.get_by_id("context_001")
        assert retrieved.created_at is not None
        assert isinstance(retrieved.created_at, datetime)
