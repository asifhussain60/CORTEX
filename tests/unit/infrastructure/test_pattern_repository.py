"""
Tests for Pattern Repository
"""

import pytest
import tempfile
import os

from src.infrastructure.persistence.db_context import DatabaseContext
from src.infrastructure.persistence.repositories.pattern_repository import (
    Pattern,
    PatternRepository
)
from src.infrastructure.migrations.migration_runner import MigrationRunner


class TestPatternRepository:
    """Test suite for PatternRepository"""
    
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
    def sample_pattern(self):
        """Create a sample pattern"""
        return Pattern(
            pattern_id="pattern_001",
            name="Test Pattern",
            pattern_type="code_pattern",
            context="Test context for the pattern",
            confidence=0.85,
            namespace="engineering",
            examples=["Example 1", "Example 2"],
            related_patterns=["pattern_002", "pattern_003"]
        )
    
    @pytest.mark.asyncio
    async def test_add_pattern(self, db_context, sample_pattern):
        """Test adding a pattern"""
        repo = PatternRepository(db_context)
        
        await db_context.begin()
        await repo.add(sample_pattern)
        await db_context.commit()
        
        # Verify pattern was added
        retrieved = await repo.get_by_id("pattern_001")
        assert retrieved is not None
        assert retrieved.pattern_id == "pattern_001"
        assert retrieved.name == "Test Pattern"
        assert retrieved.confidence == 0.85
        assert retrieved.examples == ["Example 1", "Example 2"]
    
    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(self, db_context):
        """Test get_by_id returns None for non-existent pattern"""
        repo = PatternRepository(db_context)
        
        result = await repo.get_by_id("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_all_patterns(self, db_context):
        """Test retrieving all patterns"""
        repo = PatternRepository(db_context)
        
        # Add multiple patterns
        await db_context.begin()
        for i in range(3):
            pattern = Pattern(
                pattern_id=f"pattern_{i:03d}",
                name=f"Pattern {i}",
                pattern_type="code_pattern",
                context=f"Context {i}",
                confidence=0.75 + (i * 0.05),
                namespace="test"
            )
            await repo.add(pattern)
        await db_context.commit()
        
        # Get all
        all_patterns = await repo.get_all()
        assert len(all_patterns) == 3
        # Should be ordered by confidence DESC
        assert all_patterns[0].confidence == 0.85
    
    @pytest.mark.asyncio
    async def test_update_pattern(self, db_context, sample_pattern):
        """Test updating a pattern"""
        repo = PatternRepository(db_context)
        
        # Add pattern
        await db_context.begin()
        await repo.add(sample_pattern)
        await db_context.commit()
        
        # Update pattern
        sample_pattern.name = "Updated Pattern"
        sample_pattern.confidence = 0.95
        sample_pattern.examples.append("Example 3")
        
        await db_context.begin()
        await repo.update(sample_pattern)
        await db_context.commit()
        
        # Verify update
        retrieved = await repo.get_by_id("pattern_001")
        assert retrieved.name == "Updated Pattern"
        assert retrieved.confidence == 0.95
        assert len(retrieved.examples) == 3
    
    @pytest.mark.asyncio
    async def test_delete_pattern(self, db_context, sample_pattern):
        """Test deleting a pattern"""
        repo = PatternRepository(db_context)
        
        # Add pattern
        await db_context.begin()
        await repo.add(sample_pattern)
        await db_context.commit()
        
        # Verify it exists
        assert await repo.get_by_id("pattern_001") is not None
        
        # Delete pattern
        await db_context.begin()
        await repo.delete(sample_pattern)
        await db_context.commit()
        
        # Verify deletion
        assert await repo.get_by_id("pattern_001") is None
    
    @pytest.mark.asyncio
    async def test_get_by_namespace(self, db_context):
        """Test retrieving patterns by namespace"""
        repo = PatternRepository(db_context)
        
        # Add patterns in different namespaces
        await db_context.begin()
        for i in range(5):
            pattern = Pattern(
                pattern_id=f"pattern_{i:03d}",
                name=f"Pattern {i}",
                pattern_type="code_pattern",
                context=f"Context {i}",
                confidence=0.75,
                namespace="engineering" if i < 3 else "product"
            )
            await repo.add(pattern)
        await db_context.commit()
        
        # Get by namespace
        engineering_patterns = await repo.get_by_namespace("engineering")
        product_patterns = await repo.get_by_namespace("product")
        
        assert len(engineering_patterns) == 3
        assert len(product_patterns) == 2
        assert all(p.namespace == "engineering" for p in engineering_patterns)
        assert all(p.namespace == "product" for p in product_patterns)
    
    @pytest.mark.asyncio
    async def test_get_by_confidence(self, db_context):
        """Test retrieving patterns by confidence threshold"""
        repo = PatternRepository(db_context)
        
        # Add patterns with varying confidence
        await db_context.begin()
        confidences = [0.50, 0.65, 0.75, 0.85, 0.95]
        for i, confidence in enumerate(confidences):
            pattern = Pattern(
                pattern_id=f"pattern_{i:03d}",
                name=f"Pattern {i}",
                pattern_type="code_pattern",
                context=f"Context {i}",
                confidence=confidence,
                namespace="test"
            )
            await repo.add(pattern)
        await db_context.commit()
        
        # Get high confidence (>= 0.70)
        high_confidence = await repo.get_by_confidence(0.70)
        
        assert len(high_confidence) == 3
        assert all(p.confidence >= 0.70 for p in high_confidence)
        # Should be ordered by confidence DESC
        assert high_confidence[0].confidence == 0.95
    
    @pytest.mark.asyncio
    async def test_get_by_type(self, db_context):
        """Test retrieving patterns by type"""
        repo = PatternRepository(db_context)
        
        # Add patterns of different types
        await db_context.begin()
        types = ["code_pattern", "code_pattern", "design_pattern", "workflow_pattern"]
        for i, pattern_type in enumerate(types):
            pattern = Pattern(
                pattern_id=f"pattern_{i:03d}",
                name=f"Pattern {i}",
                pattern_type=pattern_type,
                context=f"Context {i}",
                confidence=0.80,
                namespace="test"
            )
            await repo.add(pattern)
        await db_context.commit()
        
        # Get by type
        code_patterns = await repo.get_by_type("code_pattern")
        design_patterns = await repo.get_by_type("design_pattern")
        
        assert len(code_patterns) == 2
        assert len(design_patterns) == 1
        assert all(p.pattern_type == "code_pattern" for p in code_patterns)
    
    @pytest.mark.asyncio
    async def test_count_patterns(self, db_context):
        """Test counting patterns"""
        repo = PatternRepository(db_context)
        
        # Add patterns
        await db_context.begin()
        for i in range(5):
            pattern = Pattern(
                pattern_id=f"pattern_{i:03d}",
                name=f"Pattern {i}",
                pattern_type="code_pattern",
                context=f"Context {i}",
                confidence=0.80,
                namespace="test"
            )
            await repo.add(pattern)
        await db_context.commit()
        
        count = await repo.count()
        assert count == 5
    
    @pytest.mark.asyncio
    async def test_pattern_with_empty_lists(self, db_context):
        """Test pattern with empty examples and related_patterns"""
        repo = PatternRepository(db_context)
        
        pattern = Pattern(
            pattern_id="pattern_empty",
            name="Pattern with Empty Lists",
            pattern_type="code_pattern",
            context="Test context",
            confidence=0.75,
            namespace="test",
            examples=[],
            related_patterns=[]
        )
        
        await db_context.begin()
        await repo.add(pattern)
        await db_context.commit()
        
        retrieved = await repo.get_by_id("pattern_empty")
        assert retrieved.examples == []
        assert retrieved.related_patterns == []
