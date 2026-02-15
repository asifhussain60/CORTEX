"""
GraphVisualizer — Generate interactive visualizations.

Authority: Phase 3 Wave 4 S2 | Visualization
Purpose: Create HTML visualizations of code graphs
"""
from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraph


class GraphVisualizer:
    """
    Generate interactive graph visualizations.
    
    Example:
        viz = GraphVisualizer(graph)
        html = viz.generate_dependency_graph()
    """
    
    def __init__(self, graph: ASTKnowledgeGraph) -> None:
        """Initialize visualizer with graph."""
        self.graph = graph
    
    def generate_dependency_graph(self) -> str:
        """
        Generate interactive dependency graph HTML.
        
        Returns:
            HTML string with embedded graph visualization
        """
        nodes_html = ""
        for name, node in self.graph.nodes.items():
            nodes_html += f'<div class="node">{name}</div>\n'
        
        edges_html = ""
        for rel in self.graph.relationships:
            if rel.relation_type == "IMPORTS":
                edges_html += f'<div class="edge">{rel.source} → {rel.target}</div>\n'
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dependency Graph</title>
    <style>
        .node {{ padding: 10px; margin: 5px; background: #4CAF50; color: white; }}
        .edge {{ padding: 5px; margin: 2px; background: #2196F3; color: white; }}
    </style>
</head>
<body>
    <h1>Dependency Graph</h1>
    <div id="nodes">{nodes_html}</div>
    <div id="edges">{edges_html}</div>
</body>
</html>"""
        return html
    
    def generate_class_diagram(self) -> str:
        """
        Generate class diagram HTML.
        
        Returns:
            HTML string with class diagram
        """
        classes_html = ""
        for name, node in self.graph.nodes.items():
            if node.type == "class":
                methods = [
                    rel.target for rel in self.graph.relationships
                    if rel.source == name and rel.relation_type == "CONTAINS"
                ]
                methods_html = "".join(f"<li>{m}</li>" for m in methods)
                classes_html += f"""
                <div class="class">
                    <h3>{name}</h3>
                    <ul>{methods_html}</ul>
                </div>
                """
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Class Diagram</title>
    <style>
        .class {{ border: 2px solid #333; margin: 10px; padding: 10px; }}
    </style>
</head>
<body>
    <h1>Class Diagram</h1>
    {classes_html}
</body>
</html>"""
        return html
    
    def generate_call_graph(self) -> str:
        """
        Generate function call graph HTML.
        
        Returns:
            HTML string with call graph
        """
        functions_html = ""
        for name, node in self.graph.nodes.items():
            if node.type == "function":
                calls = [
                    rel.target for rel in self.graph.relationships
                    if rel.source == name and rel.relation_type == "CALLS"
                ]
                calls_html = " → ".join(calls) if calls else "(no calls)"
                functions_html += f'<div>{name}: {calls_html}</div>\n'
        
        html = f"""<!DOCTYPE html>
<html>
<head><title>Call Graph</title></head>
<body>
    <h1>Call Graph</h1>
    {functions_html}
</body>
</html>"""
        return html
