"""Test D3.js Visualization System (STATIC-VIZ-005)."""
import pytest
from cortex.visualization.d3_visualization_system import D3VisualizationSystem

def test_force_graph():
    d3 = D3VisualizationSystem()
    html = d3.generate_force_graph([{"id": "A"}, {"id": "B"}], [{"source": "A", "target": "B"}])
    assert "d3" in html.lower() and "force" in html.lower()

def test_heatmap():
    d3 = D3VisualizationSystem()
    html = d3.generate_heatmap([[1, 2], [3, 4]])
    assert "d3" in html.lower() and "heatmap" in html.lower()
