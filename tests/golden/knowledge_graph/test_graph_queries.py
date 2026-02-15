"""
Golden tests for graph query interface — Cypher-like queries.

Authority: Phase 3 Wave 4 S2 | Query Interface
Test Count: 12 golden tests
"""
import pytest
from pathlib import Path


class TestGraphQueries:
    """Golden test: Execute graph queries."""
    
    def test_find_all_functions(self, tmp_path: Path) -> None:
        """Golden: Query all functions in graph."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.query_interface import QueryInterface
        
        builder = ASTKnowledgeGraphBuilder()
        
        code_path = tmp_path / "app.py"
        code_path.write_text("""
def func1(): pass
def func2(): pass
class Calculator:
    def add(self): pass
""")
        
        graph = builder.build_from_file(code_path)
        query_interface = QueryInterface(graph)
        
        # Query all functions
        results = query_interface.execute("MATCH (n) WHERE n.type = 'function' RETURN n")
        
        assert len(results) == 2
        assert any(r['name'] == 'func1' for r in results)
        assert any(r['name'] == 'func2' for r in results)
    
    def test_find_classes_with_methods(self, tmp_path: Path) -> None:
        """Golden: Query classes and their methods."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.query_interface import QueryInterface
        
        builder = ASTKnowledgeGraphBuilder()
        
        code_path = tmp_path / "models.py"
        code_path.write_text("""
class User:
    def save(self): pass
    def delete(self): pass
""")
        
        graph = builder.build_from_file(code_path)
        query_interface = QueryInterface(graph)
        
        # Query classes with CONTAINS relationship
        results = query_interface.execute(
            "MATCH (c)-[r:CONTAINS]->(m) WHERE c.type = 'class' RETURN c, m"
        )
        
        assert len(results) == 2  # 2 methods
        assert all(r['c']['name'] == 'User' for r in results)
    
    def test_find_dependencies(self, tmp_path: Path) -> None:
        """Golden: Query import dependencies."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.query_interface import QueryInterface
        
        builder = ASTKnowledgeGraphBuilder()
        
        (tmp_path / "utils.py").write_text("def helper(): pass")
        (tmp_path / "main.py").write_text("from utils import helper")
        
        graph = builder.build_from_directory(tmp_path)
        query_interface = QueryInterface(graph)
        
        # Query IMPORTS relationships
        results = query_interface.execute(
            "MATCH (a)-[r:IMPORTS]->(b) RETURN a, b"
        )
        
        assert len(results) >= 1
        assert any(r['a'] == 'main.py' for r in results)


class TestGraphVisualization:
    """Golden test: Generate visualizations."""
    
    def test_generate_dependency_graph(self, tmp_path: Path) -> None:
        """Golden: Generate interactive dependency graph."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.visualizer import GraphVisualizer
        
        builder = ASTKnowledgeGraphBuilder()
        
        (tmp_path / "a.py").write_text("from b import func\nfrom c import helper")
        (tmp_path / "b.py").write_text("from c import helper\ndef func(): pass")
        (tmp_path / "c.py").write_text("def helper(): pass")
        
        graph = builder.build_from_directory(tmp_path)
        visualizer = GraphVisualizer(graph)
        
        # Generate HTML visualization
        html = visualizer.generate_dependency_graph()
        
        assert "<!DOCTYPE html>" in html
        assert "a.py" in html
        assert "b.py" in html
        assert "c.py" in html
    
    def test_generate_class_diagram(self, tmp_path: Path) -> None:
        """Golden: Generate class diagram."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.visualizer import GraphVisualizer
        
        builder = ASTKnowledgeGraphBuilder()
        
        code_path = tmp_path / "models.py"
        code_path.write_text("""
class User:
    def __init__(self): pass
    def save(self): pass

class Admin:
    def __init__(self): pass
""")
        
        graph = builder.build_from_file(code_path)
        visualizer = GraphVisualizer(graph)
        
        # Generate class diagram
        html = visualizer.generate_class_diagram()
        
        assert "User" in html
        assert "Admin" in html
        assert "save" in html
    
    def test_generate_call_graph(self, tmp_path: Path) -> None:
        """Golden: Generate function call graph."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.visualizer import GraphVisualizer
        
        builder = ASTKnowledgeGraphBuilder()
        
        code_path = tmp_path / "app.py"
        code_path.write_text("""
def main():
    process()

def process():
    calculate()

def calculate():
    return 42
""")
        
        graph = builder.build_from_file(code_path)
        visualizer = GraphVisualizer(graph)
        
        # Generate call graph
        html = visualizer.generate_call_graph()
        
        assert "main" in html
        assert "process" in html
        assert "calculate" in html


class TestGraphExport:
    """Golden test: Export graph to different formats."""
    
    def test_export_to_json(self, tmp_path: Path) -> None:
        """Golden: Export graph as JSON."""
        import json
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.exporter import GraphExporter
        
        builder = ASTKnowledgeGraphBuilder()
        
        code_path = tmp_path / "app.py"
        code_path.write_text("class User: pass")
        
        graph = builder.build_from_file(code_path)
        exporter = GraphExporter(graph)
        
        # Export to JSON
        json_output = exporter.to_json()
        data = json.loads(json_output)
        
        assert "nodes" in data
        assert "relationships" in data
        assert len(data["nodes"]) == 1
    
    def test_export_to_graphml(self, tmp_path: Path) -> None:
        """Golden: Export graph as GraphML."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.exporter import GraphExporter
        
        builder = ASTKnowledgeGraphBuilder()
        
        code_path = tmp_path / "app.py"
        code_path.write_text("def func(): pass")
        
        graph = builder.build_from_file(code_path)
        exporter = GraphExporter(graph)
        
        # Export to GraphML
        graphml = exporter.to_graphml()
        
        assert '<?xml version="1.0"' in graphml
        assert "<graphml" in graphml
        assert "func" in graphml
    
    def test_export_to_cytoscape(self, tmp_path: Path) -> None:
        """Golden: Export graph for Cytoscape."""
        import json
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.exporter import GraphExporter
        
        builder = ASTKnowledgeGraphBuilder()
        
        code_path = tmp_path / "app.py"
        code_path.write_text("class User: pass")
        
        graph = builder.build_from_file(code_path)
        exporter = GraphExporter(graph)
        
        # Export to Cytoscape format
        cytoscape = exporter.to_cytoscape()
        data = json.loads(cytoscape)
        
        assert "elements" in data
        assert "nodes" in data["elements"]
        assert "edges" in data["elements"]


class TestGraphMetrics:
    """Golden test: Calculate graph metrics."""
    
    def test_calculate_complexity(self, tmp_path: Path) -> None:
        """Golden: Calculate cyclomatic complexity."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.metrics import GraphMetrics
        
        builder = ASTKnowledgeGraphBuilder()
        
        code_path = tmp_path / "app.py"
        code_path.write_text("""
def complex_function(x):
    if x > 0:
        if x > 10:
            return "high"
        return "medium"
    return "low"
""")
        
        graph = builder.build_from_file(code_path)
        metrics = GraphMetrics(graph)
        
        # Calculate complexity
        complexity = metrics.calculate_complexity("complex_function")
        
        assert complexity >= 3  # 3 decision points
    
    def test_calculate_centrality(self, tmp_path: Path) -> None:
        """Golden: Calculate node centrality."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.metrics import GraphMetrics
        
        builder = ASTKnowledgeGraphBuilder()
        
        (tmp_path / "a.py").write_text("from b import func\nfrom c import helper\ndef main(): func(); helper()")
        (tmp_path / "b.py").write_text("def func(): pass")
        (tmp_path / "c.py").write_text("def helper(): pass")
        
        graph = builder.build_from_directory(tmp_path)
        metrics = GraphMetrics(graph)
        
        # Calculate centrality
        centrality = metrics.calculate_centrality()
        
        # main function calls both func and helper -> higher centrality
        assert "main" in centrality
        assert centrality["main"] >= 2  # 2 outgoing calls
    
    def test_detect_hotspots(self, tmp_path: Path) -> None:
        """Golden: Detect code hotspots."""
        from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraphBuilder
        from cortex_lens.knowledge_graph.metrics import GraphMetrics
        
        builder = ASTKnowledgeGraphBuilder()
        
        # Create a hotspot (high complexity + high centrality)
        code_path = tmp_path / "hotspot.py"
        code_path.write_text("""
def process(x):
    if x: return 1
    elif x > 5: return 2
    elif x > 10: return 3
    return 0
""")
        
        graph = builder.build_from_file(code_path)
        metrics = GraphMetrics(graph)
        
        # Detect hotspots
        hotspots = metrics.detect_hotspots()
        
        assert len(hotspots) > 0
        assert any("process" in h for h in hotspots)
