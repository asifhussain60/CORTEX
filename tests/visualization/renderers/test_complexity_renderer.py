"""
Tests for ComplexityRenderer.

Authority: CORE-008 (TDD - tests before code)
Phase: 14 - LENS Dashboard Implementation
Task: 007 - Complexity Renderer Tests
AC-ID: LENS-DASH-003
"""

import json
import pytest
from pathlib import Path

from cortex.visualization.renderers.complexity_renderer import (
    ComplexityMetrics,
    ComplexityRenderer,
    ComplexityVisualization,
)


# Fixtures

@pytest.fixture
def sample_ast_analysis():
    """Sample AST analysis data with varying complexity."""
    return {
        "functions": [
            {
                "name": "simple_function",
                "file": "main.py",
                "line_number": 10,
                "loc": 5,
                "complexity": 2,
                "parameters": ["x", "y"],
                "returns_count": 1,
            },
            {
                "name": "complex_function",
                "file": "main.py",
                "line_number": 20,
                "loc": 150,
                "complexity": 25,
                "parameters": ["a", "b", "c", "d"],
                "returns_count": 5,
            },
            {
                "name": "medium_function",
                "file": "utils.py",
                "line_number": 30,
                "loc": 50,
                "complexity": 12,
                "parameters": ["param"],
                "returns_count": 2,
            },
        ]
    }


@pytest.fixture
def renderer():
    """Create ComplexityRenderer instance."""
    return ComplexityRenderer(repo_path=Path("/test/repo"))


# Tests for ComplexityRenderer initialization

def test_renderer_initialization_with_path():
    """Test ComplexityRenderer initializes with custom path."""
    path = Path("/custom/repo")
    renderer = ComplexityRenderer(repo_path=path)
    assert renderer.repo_path == path


def test_renderer_initialization_default_path():
    """Test ComplexityRenderer initializes with default path."""
    renderer = ComplexityRenderer()
    assert renderer.repo_path == Path.cwd()


# Tests for render_complexity_scatter

def test_render_complexity_scatter_basic(renderer, sample_ast_analysis):
    """Test basic scatter plot generation."""
    viz = renderer.render_complexity_scatter(sample_ast_analysis)
    
    assert isinstance(viz, ComplexityVisualization)
    assert len(viz.scatter_data) == 3
    assert "statistics" in dir(viz)
    assert "refactor_candidates" in dir(viz)


def test_render_complexity_scatter_empty_ast(renderer):
    """Test scatter plot with empty AST data."""
    viz = renderer.render_complexity_scatter({"functions": []})
    
    assert len(viz.scatter_data) == 0
    assert viz.statistics["total_functions"] == 0
    assert len(viz.refactor_candidates) == 0


def test_scatter_data_structure(renderer, sample_ast_analysis):
    """Test scatter data has correct structure."""
    viz = renderer.render_complexity_scatter(sample_ast_analysis)
    
    for data_point in viz.scatter_data:
        assert "name" in data_point
        assert "file_path" in data_point
        assert "line_number" in data_point
        assert "loc" in data_point
        assert "complexity" in data_point
        assert "risk_level" in data_point


def test_risk_level_calculation(renderer, sample_ast_analysis):
    """Test risk levels are correctly assigned."""
    viz = renderer.render_complexity_scatter(sample_ast_analysis)
    
    # Simple function: green (low complexity, low LOC)
    simple = next(d for d in viz.scatter_data if d["name"] == "simple_function")
    assert simple["risk_level"] == "green"
    
    # Complex function: red (high complexity)
    complex_func = next(d for d in viz.scatter_data if d["name"] == "complex_function")
    assert complex_func["risk_level"] == "red"
    
    # Medium function: yellow (medium complexity)
    medium = next(d for d in viz.scatter_data if d["name"] == "medium_function")
    assert medium["risk_level"] == "yellow"


# Tests for identify_refactor_candidates

def test_identify_refactor_candidates_basic(renderer):
    """Test basic refactor candidate identification."""
    metrics = [
        {"name": "high_complexity", "complexity": 25, "loc": 50, "risk_level": "red"},
        {"name": "large_function", "complexity": 5, "loc": 150, "risk_level": "yellow"},
        {"name": "simple", "complexity": 3, "loc": 20, "risk_level": "green"},
    ]
    
    candidates = renderer.identify_refactor_candidates(
        metrics,
        complexity_threshold=20,
        loc_threshold=100
    )
    
    assert len(candidates) == 2
    assert candidates[0]["name"] == "high_complexity"  # Sorted by risk


def test_identify_refactor_candidates_empty_list(renderer):
    """Test refactor candidates with empty list."""
    candidates = renderer.identify_refactor_candidates([])
    assert len(candidates) == 0


def test_refactor_candidate_reasons(renderer):
    """Test refactor reasons are correctly generated."""
    metrics = [
        {"name": "both_high", "complexity": 30, "loc": 150, "risk_level": "red"},
    ]
    
    candidates = renderer.identify_refactor_candidates(metrics, 20, 100)
    
    assert "High complexity" in candidates[0]["reason"]
    assert "Large function" in candidates[0]["reason"]


def test_refactor_candidate_sorting(renderer):
    """Test refactor candidates are sorted by risk."""
    metrics = [
        {"name": "medium", "complexity": 15, "loc": 80, "risk_level": "yellow"},
        {"name": "high", "complexity": 30, "loc": 200, "risk_level": "red"},
        {"name": "low", "complexity": 25, "loc": 50, "risk_level": "red"},
    ]
    
    candidates = renderer.identify_refactor_candidates(metrics, 10, 50)
    
    # high should be first (highest combined score)
    assert candidates[0]["name"] == "high"


# Tests for generate_complexity_heatmap

def test_generate_heatmap_groups_by_file(renderer, sample_ast_analysis):
    """Test heatmap groups functions by file."""
    heatmap = renderer.generate_complexity_heatmap(sample_ast_analysis)
    
    assert "main.py" in heatmap
    assert "utils.py" in heatmap
    assert len(heatmap["main.py"]) == 2  # Two functions in main.py
    assert len(heatmap["utils.py"]) == 1  # One function in utils.py


def test_heatmap_sorts_by_complexity(renderer):
    """Test heatmap sorts functions within files by complexity."""
    ast_data = {
        "functions": [
            {"name": "low", "file": "test.py", "complexity": 5, "loc": 20, "line_number": 1, "parameters": [], "returns_count": 1},
            {"name": "high", "file": "test.py", "complexity": 20, "loc": 50, "line_number": 10, "parameters": [], "returns_count": 2},
            {"name": "medium", "file": "test.py", "complexity": 12, "loc": 30, "line_number": 5, "parameters": [], "returns_count": 1},
        ]
    }
    
    heatmap = renderer.generate_complexity_heatmap(ast_data)
    
    # Should be sorted by complexity descending
    assert heatmap["test.py"][0]["name"] == "high"
    assert heatmap["test.py"][1]["name"] == "medium"
    assert heatmap["test.py"][2]["name"] == "low"


# Tests for format_for_d3

def test_format_for_d3_returns_valid_json(renderer):
    """Test D3 format returns valid JSON string."""
    viz = ComplexityVisualization(
        scatter_data=[],
        heatmap_data={},
        refactor_candidates=[],
        statistics={}
    )
    
    json_str = renderer.format_for_d3(viz)
    
    # Should be valid JSON
    data = json.loads(json_str)
    assert "scatter_data" in data
    assert "heatmap_data" in data
    assert "refactor_candidates" in data
    assert "statistics" in data


def test_format_for_d3_with_data(renderer, sample_ast_analysis):
    """Test D3 format with actual data."""
    viz = renderer.render_complexity_scatter(sample_ast_analysis)
    json_str = renderer.format_for_d3(viz)
    
    data = json.loads(json_str)
    assert len(data["scatter_data"]) == 3
    assert "statistics" in data


# Tests for statistics calculation

def test_statistics_mean_complexity(renderer, sample_ast_analysis):
    """Test mean complexity calculation."""
    viz = renderer.render_complexity_scatter(sample_ast_analysis)
    
    # (2 + 25 + 12) / 3 = 13
    assert viz.statistics["mean_complexity"] == pytest.approx(13.0, rel=0.1)


def test_statistics_median_complexity(renderer):
    """Test median complexity calculation."""
    ast_data = {
        "functions": [
            {"name": "f1", "complexity": 5, "loc": 20, "file": "test.py", "line_number": 1, "parameters": [], "returns_count": 1},
            {"name": "f2", "complexity": 10, "loc": 30, "file": "test.py", "line_number": 5, "parameters": [], "returns_count": 1},
            {"name": "f3", "complexity": 15, "loc": 40, "file": "test.py", "line_number": 10, "parameters": [], "returns_count": 1},
        ]
    }
    
    viz = renderer.render_complexity_scatter(ast_data)
    
    assert viz.statistics["median_complexity"] == 10.0


def test_statistics_high_risk_count(renderer, sample_ast_analysis):
    """Test high risk count calculation."""
    viz = renderer.render_complexity_scatter(sample_ast_analysis)
    
    # Only complex_function should be red (complexity 25)
    assert viz.statistics["high_risk_count"] == 1


def test_statistics_empty_data(renderer):
    """Test statistics with empty data."""
    viz = renderer.render_complexity_scatter({"functions": []})
    
    assert viz.statistics["mean_complexity"] == 0.0
    assert viz.statistics["total_functions"] == 0
    assert viz.statistics["high_risk_count"] == 0


# Integration tests

def test_end_to_end_visualization_pipeline(renderer, sample_ast_analysis):
    """Test complete visualization generation pipeline."""
    # Generate visualization
    viz = renderer.render_complexity_scatter(sample_ast_analysis)
    
    # Verify all components
    assert len(viz.scatter_data) == 3
    assert len(viz.heatmap_data) == 2  # Two files
    assert len(viz.refactor_candidates) >= 1  # At least complex_function
    assert viz.statistics["total_functions"] == 3
    
    # Format for D3
    json_str = renderer.format_for_d3(viz)
    data = json.loads(json_str)
    
    # Verify JSON structure
    assert "scatter_data" in data
    assert "heatmap_data" in data
    assert len(data["refactor_candidates"]) >= 1
