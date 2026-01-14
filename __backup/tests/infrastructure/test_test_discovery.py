"""
Tests for AC-TEST-001: Test Discovery
"""

import pytest
from src.infrastructure.test_discovery import (
    validate_ac_id,
    get_ac_id,
    discover_tests_by_ac_id,
    get_registry,
    clear_registry,
)


@validate_ac_id("AC-TEST-001")
def test_decorator_registers_ac_id():
    """Decorator registers test with AC-ID."""
    assert get_ac_id(test_decorator_registers_ac_id) == "AC-TEST-001"


def test_get_ac_id_returns_none_for_unregistered():
    """get_ac_id returns None for tests without decorator."""
    def undecorated_test():
        pass
    
    assert get_ac_id(undecorated_test) is None


@validate_ac_id("AC-TEST-001")
def test_discover_finds_registered_tests():
    """discover_tests_by_ac_id finds all tests for AC-ID."""
    tests = discover_tests_by_ac_id("AC-TEST-001")
    assert "test_discover_finds_registered_tests" in tests


def test_discover_returns_empty_for_unknown_ac():
    """discover_tests_by_ac_id returns empty list for unknown AC-ID."""
    tests = discover_tests_by_ac_id("AC-NONEXISTENT-999")
    assert tests == []


def test_get_registry_returns_all_mappings():
    """get_registry returns all registered test-AC-ID mappings."""
    registry = get_registry()
    assert isinstance(registry, dict)
    assert len(registry) > 0


def test_invalid_ac_id_format_raises_error():
    """Decorator raises error for invalid AC-ID format."""
    with pytest.raises(ValueError, match="Invalid AC-ID format"):
        @validate_ac_id("INVALID-FORMAT")
        def test_func():
            pass


@validate_ac_id("AC-TEST-001")
def test_multiple_tests_same_ac():
    """Multiple tests can validate same AC-ID."""
    tests = discover_tests_by_ac_id("AC-TEST-001")
    # Should find multiple tests
    assert len(tests) > 1
