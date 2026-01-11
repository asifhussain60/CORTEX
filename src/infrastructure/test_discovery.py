"""
AC-TEST-001: Test Discovery
Automated discovery of test files by AC-ID metadata.

Provides decorator to link tests to AC-IDs and functions to discover
tests that validate specific acceptance criteria.
"""

import functools
from typing import Callable, Dict, List, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

# Global registry of test-to-AC-ID mappings
_TEST_AC_REGISTRY: Dict[str, str] = {}


def validate_ac_id(ac_id: str):
    """
    Decorator to link a test function to an AC-ID.
    
    Usage:
        @validate_ac_id("AC-AUDIT-001")
        def test_queryable_storage():
            '''Validates AC-AUDIT-001: Queryable Audit Storage'''
            assert storage.query(...) works
    
    Args:
        ac_id: Acceptance Criteria ID (format: AC-CATEGORY-NNN)
    """
    def decorator(func: Callable) -> Callable:
        if not ac_id.startswith("AC-"):
            raise ValueError(f"Invalid AC-ID format: {ac_id}")
        
        _TEST_AC_REGISTRY[func.__name__] = ac_id
        func._ac_id = ac_id
        
        logger.debug(f"Registered test {func.__name__} for {ac_id}")
        return func
    
    return decorator


def get_ac_id(test_func: Callable) -> Optional[str]:
    """Get AC-ID for a test function."""
    return getattr(test_func, '_ac_id', None)


def discover_tests_by_ac_id(ac_id: str) -> List[str]:
    """
    Find all tests that validate a given AC-ID.
    
    Args:
        ac_id: Acceptance Criteria ID to search for
        
    Returns:
        List of test function names that validate this AC-ID
    """
    return [
        test_name
        for test_name, test_ac in _TEST_AC_REGISTRY.items()
        if test_ac == ac_id
    ]


def get_registry() -> Dict[str, str]:
    """Get current test-AC-ID mapping registry."""
    return _TEST_AC_REGISTRY.copy()


def export_registry(output_file: Optional[Path] = None) -> Dict[str, str]:
    """
    Export test-AC-ID mapping as JSON.
    
    Args:
        output_file: Optional path to write JSON registry
        
    Returns:
        Dictionary of test_name -> ac_id mappings
    """
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(_TEST_AC_REGISTRY, f, indent=2)
        logger.info(f"Exported test registry to {output_file}")
    
    return _TEST_AC_REGISTRY.copy()


def clear_registry():
    """Clear the test registry (for testing purposes)."""
    global _TEST_AC_REGISTRY
    _TEST_AC_REGISTRY.clear()
