"""
Integration tests for Tier 3 (Development Context).

Tests metrics storage, hotspot detection, and project insights.
"""

import pytest


def test_tier3_initialization(temp_brain):
    """Test Tier 3 development context initialization."""
    from src.tier3.development_context import DevelopmentContext
    
    dev_context = DevelopmentContext(brain_path=temp_brain)
    
    assert dev_context is not None
    assert dev_context.is_initialized()


def test_tier3_metrics_storage(temp_brain):
    """Test metrics storage and retrieval."""
    from src.tier3.development_context import DevelopmentContext
    
    dev_context = DevelopmentContext(brain_path=temp_brain)
    
    # Store multiple metrics
    dev_context.store_metric(
        file_path="src/module_a.py",
        metric_type="complexity",
        value=15.5
    )
    
    dev_context.store_metric(
        file_path="src/module_a.py",
        metric_type="change_frequency",
        value=25
    )
    
    # Retrieve metrics
    metrics = dev_context.get_metrics("src/module_a.py")
    
    assert len(metrics) >= 2
    metric_types = [m["metric_type"] for m in metrics]
    assert "complexity" in metric_types
    assert "change_frequency" in metric_types


def test_tier3_hotspot_detection(temp_brain):
    """Test hotspot detection based on metrics."""
    from src.tier3.development_context import DevelopmentContext
    
    dev_context = DevelopmentContext(brain_path=temp_brain)
    
    # Store metrics for multiple files
    files_data = [
        ("src/hotspot1.py", "change_frequency", 50),
        ("src/hotspot1.py", "complexity", 45),
        ("src/normal.py", "change_frequency", 5),
        ("src/normal.py", "complexity", 10),
    ]
    
    for file_path, metric_type, value in files_data:
        dev_context.store_metric(file_path, metric_type, value)
    
    # Identify hotspots
    hotspots = dev_context.identify_hotspots(
        change_threshold=20,
        complexity_threshold=30
    )
    
    assert len(hotspots) > 0
    assert "src/hotspot1.py" in [h["file_path"] for h in hotspots]


def test_tier3_project_insights(temp_brain):
    """Test project insights generation."""
    from src.tier3.development_context import DevelopmentContext
    
    dev_context = DevelopmentContext(brain_path=temp_brain)
    
    # Store various metrics
    dev_context.store_metric("src/file1.py", "complexity", 20)
    dev_context.store_metric("src/file2.py", "complexity", 30)
    dev_context.store_metric("src/file3.py", "complexity", 10)
    
    # Get insights
    insights = dev_context.get_project_insights()
    
    assert insights is not None
    assert isinstance(insights, dict)
