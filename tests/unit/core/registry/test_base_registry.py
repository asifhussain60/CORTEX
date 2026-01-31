"""
Test Suite: BaseRegistry[T] Generic Base Class

AC-8.3B-001: BaseRegistry[T] Generic Base Class Implemented

Tests verify:
- Generic registry base class exists
- Thread-safe singleton pattern (RLock)
- All 6 core methods work: register, get, list, delete, clear
- Health check protocol operational
- Type safety with generics
- Batch operations
- Edge cases and error handling

Author: Asif Hussain
Date: 2026-01-31
"""

from __future__ import annotations

import pytest
from typing import Dict, List, Tuple
from threading import Thread
import time

from cortex.core.registry.base_registry import (
    BaseRegistry,
    HealthCheckResult,
    HealthStatus,
)


# =========================================================================
# TEST FIXTURES
# =========================================================================


class StringRegistry(BaseRegistry[str]):
    """Test registry for strings"""
    
    def _validate_value(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")
        if not value:
            raise ValueError("Value cannot be empty")


class IntRegistry(BaseRegistry[int]):
    """Test registry for integers"""
    
    def _validate_value(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"Expected int, got {type(value).__name__}")


class DictRegistry(BaseRegistry[Dict]):
    """Test registry for dicts"""
    
    def _validate_value(self, value: Dict) -> None:
        if not isinstance(value, dict):
            raise TypeError(f"Expected dict, got {type(value).__name__}")


@pytest.fixture
def string_registry() -> StringRegistry:
    """Create fresh string registry for each test"""
    return StringRegistry(name="test_string_registry")


@pytest.fixture
def int_registry() -> IntRegistry:
    """Create fresh int registry for each test"""
    return IntRegistry(name="test_int_registry")


@pytest.fixture
def dict_registry() -> DictRegistry:
    """Create fresh dict registry for each test"""
    return DictRegistry(name="test_dict_registry")


# =========================================================================
# INITIALIZATION TESTS (2 tests)
# =========================================================================


class TestBaseRegistryInitialization:
    """Test registry initialization"""
    
    def test_registry_initializes_with_name(self) -> None:
        """AC-8.3B-001-01: Registry initializes with name"""
        reg = StringRegistry(name="my_registry")
        assert reg.name == "my_registry"
        assert reg.size() == 0
    
    def test_registry_raises_on_empty_name(self) -> None:
        """AC-8.3B-001-02: Registry raises on empty name"""
        with pytest.raises(ValueError, match="Registry name cannot be empty"):
            StringRegistry(name="")


# =========================================================================
# CORE OPERATIONS TESTS (6 tests)
# =========================================================================


class TestBaseRegistryCoreOperations:
    """Test core registry operations"""
    
    def test_register_and_get(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-03: Register and retrieve item"""
        string_registry.register("key1", "value1")
        assert string_registry.get("key1") == "value1"
    
    def test_register_duplicate_raises(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-04: Register duplicate raises ValueError"""
        string_registry.register("key1", "value1")
        with pytest.raises(ValueError, match="already exists"):
            string_registry.register("key1", "value2")
    
    def test_get_nonexistent_returns_none(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-05: Get nonexistent item returns None"""
        assert string_registry.get("nonexistent") is None
    
    def test_delete_existing_item(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-06: Delete existing item returns True"""
        string_registry.register("key1", "value1")
        assert string_registry.delete("key1") is True
        assert string_registry.get("key1") is None
    
    def test_delete_nonexistent_returns_false(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-07: Delete nonexistent item returns False"""
        assert string_registry.delete("nonexistent") is False
    
    def test_clear_removes_all_items(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-08: Clear removes all items"""
        string_registry.register("key1", "value1")
        string_registry.register("key2", "value2")
        string_registry.clear()
        assert string_registry.size() == 0


# =========================================================================
# QUERY METHODS TESTS (4 tests)
# =========================================================================


class TestBaseRegistryQueryMethods:
    """Test query methods"""
    
    def test_list_all_items(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-09: List returns all items"""
        string_registry.register("key1", "value1")
        string_registry.register("key2", "value2")
        items = string_registry.list()
        assert len(items) == 2
        assert ("key1", "value1") in items
        assert ("key2", "value2") in items
    
    def test_keys_returns_all_keys(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-10: Keys returns all keys"""
        string_registry.register("key1", "value1")
        string_registry.register("key2", "value2")
        keys = string_registry.keys()
        assert set(keys) == {"key1", "key2"}
    
    def test_values_returns_all_values(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-11: Values returns all values"""
        string_registry.register("key1", "value1")
        string_registry.register("key2", "value2")
        values = string_registry.values()
        assert set(values) == {"value1", "value2"}
    
    def test_filter_by_predicate(self, int_registry: IntRegistry) -> None:
        """AC-8.3B-001-12: Filter works with predicate"""
        int_registry.register("a", 10)
        int_registry.register("b", 20)
        int_registry.register("c", 30)
        
        # Filter for values > 15
        result = int_registry.filter(lambda k, v: v > 15)
        assert len(result) == 2
        assert ("b", 20) in result
        assert ("c", 30) in result


# =========================================================================
# HEALTH CHECK TESTS (3 tests)
# =========================================================================


class TestBaseRegistryHealthCheck:
    """Test health check protocol"""
    
    def test_health_check_returns_result(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-13: Health check returns HealthCheckResult"""
        result = string_registry.health_check()
        assert isinstance(result, HealthCheckResult)
        assert result.status == HealthStatus.HEALTHY
        assert "registry_name" in result.details
    
    def test_health_check_tracks_stats(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-14: Health check tracks statistics"""
        string_registry.register("key1", "value1")
        string_registry.get("key1")
        string_registry.get("key2")  # Nonexistent
        
        result = string_registry.health_check()
        assert result.details["item_count"] == 1
        assert result.details["access_count"] >= 3
    
    def test_get_stats_returns_dict(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-15: get_stats returns statistics dict"""
        string_registry.register("key1", "value1")
        stats = string_registry.get_stats()
        
        assert isinstance(stats, dict)
        assert "name" in stats
        assert "health" in stats
        assert "items" in stats


# =========================================================================
# VALIDATION TESTS (2 tests)
# =========================================================================


class TestBaseRegistryValidation:
    """Test value validation"""
    
    def test_register_validates_type(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-16: Register validates value type"""
        with pytest.raises(TypeError):
            string_registry.register("key1", 123)  # int instead of str
    
    def test_register_validates_content(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-17: Register validates value content"""
        with pytest.raises(ValueError, match="cannot be empty"):
            string_registry.register("key1", "")


# =========================================================================
# BATCH OPERATIONS TESTS (2 tests)
# =========================================================================


class TestBaseRegistryBatchOperations:
    """Test batch operations"""
    
    def test_register_batch(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-18: Batch register multiple items"""
        items = {"key1": "value1", "key2": "value2", "key3": "value3"}
        count = string_registry.register_batch(items)
        
        assert count == 3
        assert string_registry.size() == 3
        assert string_registry.get("key1") == "value1"
    
    def test_delete_batch(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-19: Batch delete multiple items"""
        string_registry.register_batch({"key1": "v1", "key2": "v2", "key3": "v3"})
        count = string_registry.delete_batch(["key1", "key2"])
        
        assert count == 2
        assert string_registry.size() == 1
        assert string_registry.get("key3") == "v3"


# =========================================================================
# OPERATOR TESTS (3 tests)
# =========================================================================


class TestBaseRegistryOperators:
    """Test Python operators"""
    
    def test_len_operator(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-20: __len__ operator"""
        string_registry.register("key1", "value1")
        assert len(string_registry) == 1
    
    def test_contains_operator(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-21: __contains__ operator"""
        string_registry.register("key1", "value1")
        assert "key1" in string_registry
        assert "key2" not in string_registry
    
    def test_getitem_operator(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-22: __getitem__ operator"""
        string_registry.register("key1", "value1")
        assert string_registry["key1"] == "value1"


# =========================================================================
# THREAD SAFETY TESTS (2 tests)
# =========================================================================


class TestBaseRegistryThreadSafety:
    """Test thread-safe operations"""
    
    def test_concurrent_register(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-23: Concurrent register operations are safe"""
        
        def register_items(start: int, count: int) -> None:
            for i in range(start, start + count):
                string_registry.register(f"key{i}", f"value{i}")
        
        threads = [
            Thread(target=register_items, args=(0, 10)),
            Thread(target=register_items, args=(10, 10)),
            Thread(target=register_items, args=(20, 10)),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert string_registry.size() == 30
    
    def test_concurrent_read_write(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-24: Concurrent read/write operations are safe"""
        
        # Pre-populate
        for i in range(10):
            string_registry.register(f"key{i}", f"value{i}")
        
        def read_items() -> None:
            for _ in range(100):
                for i in range(10):
                    string_registry.get(f"key{i}")
        
        def write_items(start: int) -> None:
            for i in range(start, start + 10):
                string_registry.delete(f"key{i % 10}")
                string_registry.register(f"key{i}", f"value{i}")
        
        threads = [
            Thread(target=read_items),
            Thread(target=read_items),
            Thread(target=write_items, args=(10,)),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have items without crashes
        assert string_registry.size() > 0


# =========================================================================
# EDGE CASES TESTS (3 tests)
# =========================================================================


class TestBaseRegistryEdgeCases:
    """Test edge cases"""
    
    def test_empty_key_raises(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-25: Empty key raises ValueError"""
        with pytest.raises(ValueError, match="Key cannot be empty"):
            string_registry.register("", "value")
    
    def test_list_empty_registry(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-26: List empty registry returns empty list"""
        assert string_registry.list() == []
    
    def test_exists_method(self, string_registry: StringRegistry) -> None:
        """AC-8.3B-001-27: exists() method works"""
        string_registry.register("key1", "value1")
        assert string_registry.exists("key1") is True
        assert string_registry.exists("key2") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
