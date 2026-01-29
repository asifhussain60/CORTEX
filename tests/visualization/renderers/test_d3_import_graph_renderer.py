"""
TDD Tests for D3.js Import Graph Renderer.

Tests D3.js force-directed graph rendering for module import relationships:
- Node generation from module data
- Edge generation from import relationships
- Circular dependency detection
- JSON output for frontend

Authority: CORE-008 (TDD First)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-003
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest

from cortex.visualization.renderers.d3_import_graph_renderer import (
    D3ImportGraphRenderer,
    render_import_graph,
)


class TestD3ImportGraphRenderer:
    """Test D3ImportGraphRenderer for module dependencies."""
    
    def test_render_simple_import_graph(self):
        """Test rendering simple import graph with 2 modules."""
        renderer = D3ImportGraphRenderer()
        
        graph_data = {
            "nodes": [
                {"id": "module_a", "type": "module"},
                {"id": "module_b", "type": "module"},
            ],
            "edges": [
                {"source": "module_a", "target": "module_b"},
            ],
        }
        
        d3_graph = renderer.render(graph_data)
        
        assert len(d3_graph.nodes) == 2
        assert len(d3_graph.edges) == 1
        # Nodes should be marked as internal or external
        assert d3_graph.nodes[0].group in ["internal", "external"]
    
    def test_detect_circular_dependencies(self):
        """Test circular dependency detection."""
        renderer = D3ImportGraphRenderer()
        
        graph_data = {
            "nodes": [
                {"id": "module_a", "type": "module"},
                {"id": "module_b", "type": "module"},
            ],
            "edges": [
                {"source": "module_a", "target": "module_b"},
                {"source": "module_b", "target": "module_a"},  # Circular!
            ],
        }
        
        d3_graph = renderer.render(graph_data)
        circular_deps = renderer.detect_circular_dependencies(graph_data)
        
        assert len(circular_deps) > 0
        assert ("module_a", "module_b") in circular_deps or ("module_b", "module_a") in circular_deps
    
    def test_module_color_by_package(self):
        """Test module coloring based on package hierarchy."""
        renderer = D3ImportGraphRenderer()
        
        graph_data = {
            "nodes": [
                {"id": "cortex.brain.module", "type": "module"},
                {"id": "cortex.orchestrators.module", "type": "module"},
                {"id": "external.module", "type": "module"},
            ],
            "edges": [],
        }
        
        d3_graph = renderer.render(graph_data)
        
        # Modules from same package should have same color
        brain_node = next(n for n in d3_graph.nodes if "brain" in n.id)
        orch_node = next(n for n in d3_graph.nodes if "orchestrators" in n.id)
        
        # Different packages → different colors
        assert brain_node.color != orch_node.color
    
    def test_external_vs_internal_modules(self):
        """Test differentiation between external and internal modules."""
        renderer = D3ImportGraphRenderer()
        
        graph_data = {
            "nodes": [
                {"id": "cortex.module", "type": "module", "is_external": False},
                {"id": "pandas", "type": "module", "is_external": True},
            ],
            "edges": [],
        }
        
        d3_graph = renderer.render(graph_data)
        
        # External modules should have different visual treatment
        internal_node = next(n for n in d3_graph.nodes if n.id == "cortex.module")
        external_node = next(n for n in d3_graph.nodes if n.id == "pandas")
        
        # Could be different color or size
        assert internal_node.group != external_node.group or internal_node.color != external_node.color
    
    def test_to_json_output(self):
        """Test JSON serialization."""
        renderer = D3ImportGraphRenderer()
        
        graph_data = {
            "nodes": [{"id": "module_a", "type": "module"}],
            "edges": [],
        }
        
        d3_graph = renderer.render(graph_data)
        json_output = renderer.to_json(d3_graph)
        
        assert isinstance(json_output, dict)
        assert "nodes" in json_output
        assert "links" in json_output
        assert "circular_dependencies" in json_output
    
    def test_convenience_function(self):
        """Test convenience function."""
        graph_data = {
            "nodes": [{"id": "module_a", "type": "module"}],
            "edges": [],
        }
        
        json_output = render_import_graph(graph_data)
        
        assert isinstance(json_output, dict)
        assert "nodes" in json_output
