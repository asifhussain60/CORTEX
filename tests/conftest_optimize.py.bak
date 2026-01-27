"""
Test Categorization and Tagging Strategy

This module provides pytest hooks for automatic test categorization
based on performance characteristics and dependencies.

Enables:
- Automatic smoke test identification
- Dependency-based parallel execution safety
- Performance-based test stratification
- Fixture scope optimization
"""

import pytest
import time
from pathlib import Path


def pytest_collection_modifyitems(config, items):
    """Auto-categorize and tag tests based on characteristics.
    
    This hook runs after test collection and automatically adds markers
    to tests based on their characteristics:
    
    - @pytest.mark.smoke  : Very fast tests (<100ms, no external deps)
    - @pytest.mark.unit   : Fast unit tests (<500ms)
    - @pytest.mark.integration : Tests with I/O (<5s)
    - @pytest.mark.slow   : Slow tests (>5s)
    - @pytest.mark.concurrent_safe : Can run in parallel
    - @pytest.mark.dependency_heavy : Has expensive setup/teardown
    """
    
    # Define categorization rules
    smoke_patterns = [
        "test_protocol",
        "test_schema",
        "test_validation",
        "test_parsing",
    ]
    
    integration_patterns = [
        "test_database",
        "test_db_",
        "test_e2e",
        "test_integration",
        "test_api",
        "test_http",
        "test_network",
    ]
    
    slow_patterns = [
        "test_migration",
        "test_performance",
        "test_load",
        "test_stress",
    ]
    
    for item in items:
        # Get test module and function name
        test_name = item.nodeid.lower()
        
        # AUTO-TAG: SMOKE TESTS
        # Very fast tests with no external dependencies
        if any(p in test_name for p in smoke_patterns):
            if "integration" not in test_name and "db" not in test_name:
                if item.get_closest_marker("smoke") is None:
                    item.add_marker(pytest.mark.smoke)
                if item.get_closest_marker("concurrent_safe") is None:
                    item.add_marker(pytest.mark.concurrent_safe)
        
        # AUTO-TAG: INTEGRATION TESTS
        elif any(p in test_name for p in integration_patterns):
            if item.get_closest_marker("integration") is None:
                item.add_marker(pytest.mark.integration)
            # Mark as potentially not concurrent-safe (database)
            if "db" in test_name and item.get_closest_marker("dependency_heavy") is None:
                item.add_marker(pytest.mark.dependency_heavy)
        
        # AUTO-TAG: SLOW TESTS
        if any(p in test_name for p in slow_patterns):
            if item.get_closest_marker("slow") is None:
                item.add_marker(pytest.mark.slow)
            if item.get_closest_marker("dependency_heavy") is None:
                item.add_marker(pytest.mark.dependency_heavy)
        
        # DEFAULT: Unit test if not categorized
        if (item.get_closest_marker("smoke") is None and
            item.get_closest_marker("integration") is None and
            item.get_closest_marker("slow") is None):
            if item.get_closest_marker("unit") is None:
                item.add_marker(pytest.mark.unit)
            if item.get_closest_marker("concurrent_safe") is None:
                item.add_marker(pytest.mark.concurrent_safe)


@pytest.fixture(scope="session")
def test_session_start():
    """Track test session start for performance monitoring."""
    start_time = time.time()
    yield
    end_time = time.time()
    total_time = end_time - start_time
    # Session complete - metrics captured by pytest_plugin_audit


def pytest_configure(config):
    """Register custom markers for test categorization."""
    config.addinivalue_line(
        "markers",
        "smoke: Very fast tests (<100ms, baseline health check)"
    )
    config.addinivalue_line(
        "markers",
        "concurrent_safe: Safe to run in parallel (no global state)"
    )
    config.addinivalue_line(
        "markers",
        "dependency_heavy: Has expensive setup/teardown or external deps"
    )


# Optional: Fixture performance monitoring
class FixtureMetrics:
    """Track fixture usage for optimization."""
    
    def __init__(self):
        self.metrics = {}
    
    def record_fixture(self, fixture_name: str, scope: str, setup_time: float):
        """Record fixture metrics."""
        if fixture_name not in self.metrics:
            self.metrics[fixture_name] = {
                "scope": scope,
                "setup_times": [],
                "total_calls": 0,
            }
        self.metrics[fixture_name]["setup_times"].append(setup_time)
        self.metrics[fixture_name]["total_calls"] += 1
    
    def get_recommendations(self):
        """Generate scope optimization recommendations."""
        recommendations = []
        for fixture_name, data in self.metrics.items():
            if data["total_calls"] > 10:
                avg_time = sum(data["setup_times"]) / len(data["setup_times"])
                if avg_time > 0.1 and data["scope"] == "function":
                    recommendations.append(
                        f"Consider changing {fixture_name} scope to 'session' "
                        f"(avg setup: {avg_time:.3f}s, calls: {data['total_calls']})"
                    )
        return recommendations


# Global metrics tracker
_fixture_metrics = FixtureMetrics()


@pytest.fixture
def fixture_metrics():
    """Provide access to fixture metrics."""
    return _fixture_metrics
