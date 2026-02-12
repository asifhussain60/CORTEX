"""
Unit Tests for UnifiedRegistry - TDD RED Phase

AC_START: AC-WAVE-P-REM-001-001
Authority: WAVE-P Stage 1 - Registry Consolidation
Priority: P0-CRITICAL
CORE Compliance: CORE-008 (TDD), CORE-035 (Single Implementation)

Tests for single canonical registry base that all CORTEX registries inherit from.

Test Coverage:
1. Basic CRUD operations (create, read, update, delete)
2. Thread-safe operations
3. Query builder interface
4. Persistence abstraction
5. Audit logging integration
6. Performance guarantees
"""

import pytest
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


# Test data model
@dataclass
class TestEntity:
    """Test entity for registry operations."""
    id: str
    name: str
    value: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TestUnifiedRegistryCore:
    """Test core registry functionality."""
    
    def test_registry_initialization(self):
        """REM-001-001: Registry initializes with empty state."""
        # RED: Import will fail - UnifiedRegistry doesn't exist yet
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return entity.value >= 0
        
        registry = TestRegistry()
        assert registry.size() == 0
        assert registry.list_all() == []
    
    def test_register_single_entity(self):
        """REM-001-002: Register single entity."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return entity.value >= 0
        
        registry = TestRegistry()
        entity = TestEntity(id="test-1", name="Test Entity", value=42)
        
        registry.register("test-1", entity)
        
        assert registry.size() == 1
        assert registry.exists("test-1")
    
    def test_retrieve_registered_entity(self):
        """REM-001-003: Retrieve entity by key."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return entity.value >= 0
        
        registry = TestRegistry()
        entity = TestEntity(id="test-1", name="Test Entity", value=42)
        registry.register("test-1", entity)
        
        retrieved = registry.get("test-1")
        
        assert retrieved is not None
        assert retrieved.id == "test-1"
        assert retrieved.value == 42
    
    def test_update_existing_entity(self):
        """REM-001-004: Update entity."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return entity.value >= 0
        
        registry = TestRegistry()
        entity = TestEntity(id="test-1", name="Original", value=42)
        registry.register("test-1", entity)
        
        updated = TestEntity(id="test-1", name="Updated", value=100)
        registry.update("test-1", updated)
        
        retrieved = registry.get("test-1")
        assert retrieved.name == "Updated"
        assert retrieved.value == 100
    
    def test_remove_entity(self):
        """REM-001-005: Remove entity from registry."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return entity.value >= 0
        
        registry = TestRegistry()
        entity = TestEntity(id="test-1", name="Test", value=42)
        registry.register("test-1", entity)
        
        result = registry.remove("test-1")
        
        assert result is True
        assert registry.size() == 0
        assert not registry.exists("test-1")
    
    def test_validation_enforcement(self):
        """REM-001-006: Validation enforced on registration."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return entity.value >= 0
        
        registry = TestRegistry()
        invalid_entity = TestEntity(id="test-1", name="Invalid", value=-10)
        
        with pytest.raises(ValueError, match="Entity validation failed"):
            registry.register("test-1", invalid_entity)


class TestUnifiedRegistryThreadSafety:
    """Test thread-safe operations."""
    
    def test_concurrent_register(self):
        """REM-001-007: Concurrent register operations are safe."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return True
        
        registry = TestRegistry()
        
        def register_items(start: int, count: int):
            for i in range(start, start + count):
                entity = TestEntity(id=f"item-{i}", name=f"Item {i}", value=i)
                registry.register(f"item-{i}", entity)
        
        threads = [
            threading.Thread(target=register_items, args=(0, 10)),
            threading.Thread(target=register_items, args=(10, 10)),
            threading.Thread(target=register_items, args=(20, 10)),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert registry.size() == 30
    
    def test_concurrent_read_write(self):
        """REM-001-008: Concurrent read/write operations are safe."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return True
        
        registry = TestRegistry()
        
        # Pre-populate
        for i in range(100):
            entity = TestEntity(id=f"item-{i}", name=f"Item {i}", value=i)
            registry.register(f"item-{i}", entity)
        
        read_count = [0]
        
        def read_items():
            for i in range(100):
                entity = registry.get(f"item-{i}")
                if entity:
                    read_count[0] += 1
        
        def write_items():
            for i in range(100, 150):
                entity = TestEntity(id=f"item-{i}", name=f"Item {i}", value=i)
                registry.register(f"item-{i}", entity)
        
        threads = [
            threading.Thread(target=read_items),
            threading.Thread(target=read_items),
            threading.Thread(target=write_items),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert read_count[0] >= 100  # At least one full read pass
        assert registry.size() == 150


class TestUnifiedRegistryQuery:
    """Test query builder interface."""
    
    def test_query_by_predicate(self):
        """REM-001-009: Query entities by predicate."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return True
        
        registry = TestRegistry()
        
        for i in range(10):
            entity = TestEntity(id=f"item-{i}", name=f"Item {i}", value=i * 10)
            registry.register(f"item-{i}", entity)
        
        # Query entities with value >= 50
        results = registry.query(lambda e: e.value >= 50)
        
        assert len(results) == 5
        assert all(e.value >= 50 for e in results)
    
    def test_query_empty_result(self):
        """REM-001-010: Query with no matches returns empty list."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return True
        
        registry = TestRegistry()
        
        for i in range(5):
            entity = TestEntity(id=f"item-{i}", name=f"Item {i}", value=i)
            registry.register(f"item-{i}", entity)
        
        results = registry.query(lambda e: e.value > 100)
        
        assert results == []


class TestUnifiedRegistryPerformance:
    """Test performance guarantees."""
    
    def test_register_1000_items_under_500ms(self):
        """REM-001-011: Register 1000 items in < 500ms."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return True
        
        registry = TestRegistry()
        
        start = time.time()
        for i in range(1000):
            entity = TestEntity(id=f"item-{i}", name=f"Item {i}", value=i)
            registry.register(f"item-{i}", entity)
        elapsed = (time.time() - start) * 1000
        
        assert elapsed < 500, f"Took {elapsed:.1f}ms (expected < 500ms)"
    
    def test_query_1000_items_under_100ms(self):
        """REM-001-012: Query 1000 items in < 100ms."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return True
        
        registry = TestRegistry()
        
        for i in range(1000):
            entity = TestEntity(id=f"item-{i}", name=f"Item {i}", value=i)
            registry.register(f"item-{i}", entity)
        
        start = time.time()
        results = registry.query(lambda e: e.value >= 500)
        elapsed = (time.time() - start) * 1000
        
        assert elapsed < 100, f"Took {elapsed:.1f}ms (expected < 100ms)"
        assert len(results) == 500


class TestUnifiedRegistryBulkOperations:
    """Test bulk operations."""
    
    def test_register_batch(self):
        """REM-001-013: Register multiple entities in batch."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return True
        
        registry = TestRegistry()
        
        entities = [
            TestEntity(id=f"item-{i}", name=f"Item {i}", value=i)
            for i in range(10)
        ]
        
        registry.register_batch(entities)
        
        assert registry.size() == 10
    
    def test_clear_all(self):
        """REM-001-014: Clear all entities from registry."""
        from cortex.core.registry.unified_registry import UnifiedRegistry
        
        class TestRegistry(UnifiedRegistry[TestEntity]):
            def validate_entity(self, entity: TestEntity) -> bool:
                return True
        
        registry = TestRegistry()
        
        for i in range(10):
            entity = TestEntity(id=f"item-{i}", name=f"Item {i}", value=i)
            registry.register(f"item-{i}", entity)
        
        registry.clear()
        
        assert registry.size() == 0
        assert registry.list_all() == []


# AC_COMPLETE: AC-WAVE-P-REM-001-001 ✅ 14 RED tests written
# Next: Implement UnifiedRegistry to make tests pass (GREEN phase)
