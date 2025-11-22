"""
Tests for Generic Repository Interface
"""

import pytest
from typing import List, Optional
from dataclasses import dataclass

from src.infrastructure.persistence.repository import (
    IRepository, 
    BaseRepository, 
    ISpecification
)


# Test entity
@dataclass
class TestEntity:
    id: str
    name: str
    value: int


# Test specification
class HighValueSpec:
    """Specification for entities with value > 50"""
    
    def is_satisfied_by(self, entity: TestEntity) -> bool:
        return entity.value > 50


# Concrete test repository
class TestRepository(BaseRepository[TestEntity]):
    """In-memory repository for testing"""
    
    def __init__(self):
        super().__init__(db_context=None)
        self._storage: dict[str, TestEntity] = {}
    
    async def get_by_id(self, id: str) -> Optional[TestEntity]:
        return self._storage.get(id)
    
    async def get_all(self) -> List[TestEntity]:
        return list(self._storage.values())
    
    async def add(self, entity: TestEntity) -> None:
        await super().add(entity)
        self._storage[entity.id] = entity
    
    async def delete(self, entity: TestEntity) -> None:
        await super().delete(entity)
        if entity.id in self._storage:
            del self._storage[entity.id]


class TestRepositoryInterface:
    """Test suite for IRepository interface"""
    
    @pytest.fixture
    def repository(self):
        """Create a test repository"""
        return TestRepository()
    
    @pytest.fixture
    def sample_entities(self):
        """Create sample test entities"""
        return [
            TestEntity("1", "Entity One", 25),
            TestEntity("2", "Entity Two", 75),
            TestEntity("3", "Entity Three", 100),
        ]
    
    @pytest.mark.asyncio
    async def test_add_entity(self, repository: TestRepository):
        """Test adding an entity"""
        entity = TestEntity("1", "Test", 42)
        await repository.add(entity)
        
        retrieved = await repository.get_by_id("1")
        assert retrieved is not None
        assert retrieved.id == "1"
        assert retrieved.name == "Test"
        assert retrieved.value == 42
    
    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(self, repository: TestRepository):
        """Test get_by_id returns None for non-existent entity"""
        result = await repository.get_by_id("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_all_returns_all_entities(
        self, 
        repository: TestRepository, 
        sample_entities: List[TestEntity]
    ):
        """Test get_all returns all added entities"""
        for entity in sample_entities:
            await repository.add(entity)
        
        all_entities = await repository.get_all()
        assert len(all_entities) == 3
        assert set(e.id for e in all_entities) == {"1", "2", "3"}
    
    @pytest.mark.asyncio
    async def test_get_all_returns_empty_list_when_no_entities(self, repository: TestRepository):
        """Test get_all returns empty list when repository is empty"""
        result = await repository.get_all()
        assert result == []
    
    @pytest.mark.asyncio
    async def test_find_with_specification(
        self, 
        repository: TestRepository, 
        sample_entities: List[TestEntity]
    ):
        """Test finding entities using specification"""
        for entity in sample_entities:
            await repository.add(entity)
        
        spec = HighValueSpec()
        high_value_entities = await repository.find(spec)
        
        assert len(high_value_entities) == 2
        assert all(e.value > 50 for e in high_value_entities)
        assert set(e.id for e in high_value_entities) == {"2", "3"}
    
    @pytest.mark.asyncio
    async def test_find_returns_empty_when_no_matches(self, repository: TestRepository):
        """Test find returns empty list when no entities match specification"""
        entity = TestEntity("1", "Low Value", 10)
        await repository.add(entity)
        
        spec = HighValueSpec()
        result = await repository.find(spec)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_delete_entity(self, repository: TestRepository):
        """Test deleting an entity"""
        entity = TestEntity("1", "Test", 42)
        await repository.add(entity)
        
        # Verify entity exists
        assert await repository.get_by_id("1") is not None
        
        # Delete entity
        await repository.delete(entity)
        
        # Verify entity no longer exists
        assert await repository.get_by_id("1") is None
    
    @pytest.mark.asyncio
    async def test_count_without_specification(
        self, 
        repository: TestRepository, 
        sample_entities: List[TestEntity]
    ):
        """Test counting all entities"""
        for entity in sample_entities:
            await repository.add(entity)
        
        count = await repository.count()
        assert count == 3
    
    @pytest.mark.asyncio
    async def test_count_with_specification(
        self, 
        repository: TestRepository, 
        sample_entities: List[TestEntity]
    ):
        """Test counting entities matching specification"""
        for entity in sample_entities:
            await repository.add(entity)
        
        spec = HighValueSpec()
        count = await repository.count(spec)
        assert count == 2
    
    @pytest.mark.asyncio
    async def test_count_returns_zero_when_empty(self, repository: TestRepository):
        """Test count returns zero for empty repository"""
        count = await repository.count()
        assert count == 0
    
    @pytest.mark.asyncio
    async def test_update_entity(self, repository: TestRepository):
        """Test updating an entity"""
        entity = TestEntity("1", "Original", 42)
        await repository.add(entity)
        
        # Modify entity
        entity.name = "Updated"
        entity.value = 99
        await repository.update(entity)
        
        # Retrieve and verify changes
        retrieved = await repository.get_by_id("1")
        assert retrieved is not None
        assert retrieved.name == "Updated"
        assert retrieved.value == 99
    
    @pytest.mark.asyncio
    async def test_repository_tracks_entities(self, repository: TestRepository):
        """Test that repository tracks added entities internally"""
        entity = TestEntity("1", "Test", 42)
        await repository.add(entity)
        
        # BaseRepository tracks entities in _entities list
        assert len(repository._entities) == 1
        assert repository._entities[0] == entity
    
    @pytest.mark.asyncio
    async def test_multiple_operations_sequence(
        self, 
        repository: TestRepository, 
        sample_entities: List[TestEntity]
    ):
        """Test a sequence of multiple repository operations"""
        # Add entities
        for entity in sample_entities:
            await repository.add(entity)
        
        # Count all
        assert await repository.count() == 3
        
        # Find high value
        high_value = await repository.find(HighValueSpec())
        assert len(high_value) == 2
        
        # Delete one
        entity_to_delete = sample_entities[0]
        await repository.delete(entity_to_delete)
        
        # Verify deletion
        assert await repository.count() == 2
        assert await repository.get_by_id(entity_to_delete.id) is None
        
        # Update another
        entity_to_update = sample_entities[1]
        entity_to_update.value = 200
        await repository.update(entity_to_update)
        
        retrieved = await repository.get_by_id(entity_to_update.id)
        assert retrieved.value == 200
