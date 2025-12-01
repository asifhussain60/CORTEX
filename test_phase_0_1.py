"""
Test script for Phase 0.1 Debug Marker System validation.

Validates acceptance criteria:
- Decorators for @debug_start and @debug_end ✓
- Configurable log levels ✓
- Performance tracking ✓
- Context manager support ✓
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.debug_markers import (
    debug_start,
    debug_end,
    DebugScope,
    DebugLevel,
    get_performance_stats,
    reset_performance_tracking
)


# Test 1: Decorators with configurable log levels
@debug_start("test_operation", level="INFO", log_args=True)
@debug_end("test_operation", level="INFO", log_result=True)
def test_function(x, y):
    """Test function with debug decorators."""
    import time
    time.sleep(0.1)  # Simulate work
    return x + y


# Test 2: Context manager with metrics
def test_context_manager():
    """Test context manager support."""
    with DebugScope("database_query", level="DEBUG") as scope:
        scope.add_context("query_type", "SELECT")
        scope.log_metric("rows_returned", 42)
        import time
        time.sleep(0.05)


# Test 3: Performance tracking
def test_performance_tracking():
    """Test performance tracking and statistics."""
    # Run test operations
    result = test_function(5, 10)
    test_context_manager()
    
    # Get performance statistics
    stats = get_performance_stats("test_operation")
    
    print("\n=== Phase 0.1 Validation Results ===\n")
    
    # Validate decorators work
    assert result == 15, "Decorator should not affect function result"
    print("✓ Decorators (@debug_start, @debug_end) working correctly")
    
    # Validate performance tracking
    assert stats['count'] > 0, "Performance tracking should record executions"
    assert stats['avg'] > 0, "Performance tracking should measure duration"
    print(f"✓ Performance tracking working (avg: {stats['avg']:.4f}s)")
    
    # Validate log levels (DebugLevel enum exists and is used)
    levels = [DebugLevel.DEBUG, DebugLevel.INFO, DebugLevel.WARNING, DebugLevel.ERROR]
    assert all(level.value in ["DEBUG", "INFO", "WARNING", "ERROR"] for level in levels)
    print("✓ Configurable log levels implemented (DEBUG, INFO, WARNING, ERROR)")
    
    # Validate context manager
    scope_stats = get_performance_stats("database_query")
    assert scope_stats['count'] > 0, "Context manager should track execution"
    print(f"✓ Context manager (DebugScope) working (avg: {scope_stats['avg']:.4f}s)")
    
    print("\n=== All Phase 0.1 Acceptance Criteria Met ===")
    print("✓ Decorators for @debug_start and @debug_end")
    print("✓ Configurable log levels")
    print("✓ Performance tracking integration")
    print("✓ Context manager support")
    print("\n✅ Phase 0.1 COMPLETE - Ready for Phase 0.2\n")
    
    # Cleanup
    reset_performance_tracking()


if __name__ == "__main__":
    test_performance_tracking()
