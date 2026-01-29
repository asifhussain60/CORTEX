"""
TDD Tests for D3.js Call Graph Renderer.

Tests D3.js force-directed graph rendering for function call relationships:
- Node generation from function data
- Edge generation from call relationships
- D3.js configuration (force simulation, colors, sizes)
- JSON output for frontend

Authority: CORE-008 (TDD First)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-003
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest

from cortex.visualization.renderers.d3_call_graph_renderer import (
    D3CallGraphRenderer,
    D3Graph,
    D3Node,
    D3Edge,
    D3Configuration,
    render_call_graph,
)


class TestD3Node:
    """Test D3Node dataclass."""
    
    def test_create_function_node(self):
        """Test creating D3 node for function."""
        node = D3Node(
            id="create_user",
            label="create_user",
            group="function",
            size=10,
            color="#4299e1",
        )
        
        assert node.id == "create_user"
        assert node.label == "create_user"
        assert node.group == "function"
        assert node.size == 10
        assert node.color == "#4299e1"


class TestD3Edge:
    """Test D3Edge dataclass."""
    
    def test_create_call_edge(self):
        """Test creating D3 edge for function call."""
        edge = D3Edge(
            source="main",
            target="process_data",
            value=1,
            label="calls",
        )
        
        assert edge.source == "main"
        assert edge.target == "process_data"
        assert edge.value == 1
        assert edge.label == "calls"


class TestD3Configuration:
    """Test D3Configuration dataclass."""
    
    def test_create_default_configuration(self):
        """Test creating default D3 force simulation configuration."""
        config = D3Configuration(
            width=1200,
            height=800,
            charge_strength=-300,
            link_distance=100,
            node_radius_min=5,
            node_radius_max=20,
        )
        
        assert config.width == 1200
        assert config.height == 800
        assert config.charge_strength == -300
        assert config.link_distance == 100


class TestD3Graph:
    """Test D3Graph dataclass."""
    
    def test_create_d3_graph(self):
        """Test creating D3Graph with nodes and edges."""
        nodes = [
            D3Node(id="func1", label="func1", group="function", size=10, color="#4299e1"),
            D3Node(id="func2", label="func2", group="function", size=10, color="#4299e1"),
        ]
        edges = [
            D3Edge(source="func1", target="func2", value=1, label="calls"),
        ]
        config = D3Configuration(width=1200, height=800)
        
        graph = D3Graph(nodes=nodes, edges=edges, config=config)
        
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        assert graph.config.width == 1200


class TestD3CallGraphRenderer:
    """Test D3CallGraphRenderer main renderer."""
    
    def test_render_simple_call_graph(self):
        """Test rendering simple call graph with 2 functions."""
        renderer = D3CallGraphRenderer()
        
        # Input data from LENS analysis
        graph_data = {
            "nodes": [
                {"id": "main", "type": "function"},
                {"id": "process_data", "type": "function"},
            ],
            "edges": [
                {"source": "main", "target": "process_data"},
            ],
        }
        
        d3_graph = renderer.render(graph_data)
        
        assert isinstance(d3_graph, D3Graph)
        assert len(d3_graph.nodes) == 2
        assert len(d3_graph.edges) == 1
        assert d3_graph.nodes[0].id == "main"
        assert d3_graph.edges[0].source == "main"
        assert d3_graph.edges[0].target == "process_data"
    
    def test_render_complex_call_graph(self):
        """Test rendering complex call graph with multiple functions."""
        renderer = D3CallGraphRenderer()
        
        graph_data = {
            "nodes": [
                {"id": "main", "type": "function"},
                {"id": "process_data", "type": "function"},
                {"id": "validate_input", "type": "function"},
                {"id": "save_results", "type": "function"},
            ],
            "edges": [
                {"source": "main", "target": "process_data"},
                {"source": "main", "target": "save_results"},
                {"source": "process_data", "target": "validate_input"},
            ],
        }
        
        d3_graph = renderer.render(graph_data)
        
        assert len(d3_graph.nodes) == 4
        assert len(d3_graph.edges) == 3
    
    def test_calculate_node_size_by_connections(self):
        """Test node size calculation based on number of connections."""
        renderer = D3CallGraphRenderer()
        
        graph_data = {
            "nodes": [
                {"id": "main", "type": "function"},  # 2 connections
                {"id": "helper", "type": "function"},  # 0 connections
            ],
            "edges": [
                {"source": "main", "target": "func1"},
                {"source": "main", "target": "func2"},
            ],
        }
        
        d3_graph = renderer.render(graph_data)
        
        # main should have larger size (more connections)
        main_node = next(n for n in d3_graph.nodes if n.id == "main")
        helper_node = next(n for n in d3_graph.nodes if n.id == "helper")
        
        assert main_node.size > helper_node.size
    
    def test_node_color_by_type(self):
        """Test node color assignment based on node type."""
        renderer = D3CallGraphRenderer()
        
        graph_data = {
            "nodes": [
                {"id": "func1", "type": "function"},
                {"id": "Class1", "type": "class"},
            ],
            "edges": [],
        }
        
        d3_graph = renderer.render(graph_data)
        
        func_node = next(n for n in d3_graph.nodes if n.id == "func1")
        class_node = next(n for n in d3_graph.nodes if n.id == "Class1")
        
        # Different colors for different types
        assert func_node.color != class_node.color
    
    def test_to_json_output(self):
        """Test JSON serialization for frontend."""
        renderer = D3CallGraphRenderer()
        
        graph_data = {
            "nodes": [{"id": "main", "type": "function"}],
            "edges": [{"source": "main", "target": "func1"}],
        }
        
        d3_graph = renderer.render(graph_data)
        json_output = renderer.to_json(d3_graph)
        
        assert isinstance(json_output, dict)
        assert "nodes" in json_output
        assert "links" in json_output  # D3.js uses "links" not "edges"
        assert "config" in json_output
        assert len(json_output["nodes"]) == 1
    
    def test_custom_configuration(self):
        """Test rendering with custom D3 configuration."""
        renderer = D3CallGraphRenderer()
        
        custom_config = D3Configuration(
            width=1600,
            height=1000,
            charge_strength=-500,
            link_distance=150,
        )
        
        graph_data = {
            "nodes": [{"id": "main", "type": "function"}],
            "edges": [],
        }
        
        d3_graph = renderer.render(graph_data, config=custom_config)
        
        assert d3_graph.config.width == 1600
        assert d3_graph.config.height == 1000
        assert d3_graph.config.charge_strength == -500
    
    def test_empty_graph(self):
        """Test rendering empty graph (no nodes/edges)."""
        renderer = D3CallGraphRenderer()
        
        graph_data = {
            "nodes": [],
            "edges": [],
        }
        
        d3_graph = renderer.render(graph_data)
        
        assert len(d3_graph.nodes) == 0
        assert len(d3_graph.edges) == 0
    
    def test_convenience_function_render_call_graph(self):
        """Test convenience function."""
        graph_data = {
            "nodes": [{"id": "main", "type": "function"}],
            "edges": [],
        }
        
        json_output = render_call_graph(graph_data)
        
        assert isinstance(json_output, dict)
        assert "nodes" in json_output
        assert "links" in json_output
