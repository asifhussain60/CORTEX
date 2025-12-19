#!/usr/bin/env python3
"""
Collector Schema Integration Tests

Tests that real collector output matches template expectations.
This catches schema mismatches that mock-based tests miss.

Author: Asif Hussain
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def cortex_root():
    """Get CORTEX repository root."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def overview_output(cortex_root):
    """Get real overview collector output."""
    from src.dashboard.data.overview_collector import OverviewCollector
    
    collector = OverviewCollector(str(cortex_root))
    return collector.collect()


@pytest.fixture
def expected_overview_schema():
    """Expected schema for overview data."""
    return {
        "required_keys": [
            "project_name",
            "overall_health",
            "key_metrics",
            "health_categories",
            "critical_issues",
            "composition",
            "trends"
        ],
        "overall_health_keys": ["score", "status", "trend", "last_scan"],
        "trends_keys": ["health_trend", "velocity_trend", "quality_trend"]
    }


def test_overview_has_required_fields(overview_output, expected_overview_schema):
    """Test that overview output has all required fields."""
    for key in expected_overview_schema["required_keys"]:
        assert key in overview_output, f"Missing required field: {key}"


def test_overview_field_types(overview_output):
    """Test that overview fields have correct types."""
    assert isinstance(overview_output["project_name"], str)
    assert isinstance(overview_output["overall_health"], dict)
    assert isinstance(overview_output["key_metrics"], dict)
    
    health = overview_output["overall_health"]
    assert isinstance(health["score"], (int, float))
    assert isinstance(health["status"], str)
    assert 0 <= health["score"] <= 100


def test_overview_output_is_serializable(overview_output):
    """Test that overview output can be JSON serialized."""
    try:
        json.dumps(overview_output)
    except (TypeError, ValueError) as e:
        pytest.fail(f"Overview output not JSON serializable: {e}")


def test_overview_overall_health_structure(overview_output, expected_overview_schema):
    """Test that overall_health has required nested fields."""
    health = overview_output["overall_health"]
    for key in expected_overview_schema["overall_health_keys"]:
        assert key in health, f"Missing overall_health field: {key}"


def test_overview_trends_structure(overview_output, expected_overview_schema):
    """Test that trends has required nested fields."""
    trends = overview_output["trends"]
    for key in expected_overview_schema["trends_keys"]:
        assert key in trends, f"Missing trends field: {key}"


def test_multiple_collectors_schema_consistency(cortex_root):
    """Test that multiple collector runs return consistent schema."""
    from src.dashboard.data.overview_collector import OverviewCollector
    
    collector = OverviewCollector(str(cortex_root))
    
    # Run collector multiple times
    output1 = collector.collect()
    output2 = collector.collect()
    
    # Schema should be consistent
    assert set(output1.keys()) == set(output2.keys()), "Collector schema inconsistent across runs"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
