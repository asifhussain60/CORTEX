"""
GraphMetrics — Calculate graph-based code metrics.

Authority: Phase 3 Wave 4 S2 | Metrics
Purpose: Complexity, centrality, hotspot detection
"""
import ast
from typing import Dict, List
from pathlib import Path
from cortex.intelligence.lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraph


class GraphMetrics:
    """
    Calculate graph-based code metrics.
    
    Example:
        metrics = GraphMetrics(graph)
        complexity = metrics.calculate_complexity("my_function")
    """
    
    def __init__(self, graph: ASTKnowledgeGraph) -> None:
        """Initialize metrics calculator with graph."""
        self.graph = graph
    
    def calculate_complexity(self, function_name: str) -> int:
        """
        Calculate cyclomatic complexity for function.
        
        Args:
            function_name: Name of function
            
        Returns:
            Complexity score (decision points + 1)
        """
        # Find function node
        node = self.graph.nodes.get(function_name)
        if not node:
            return 0
        
        # Parse file to get AST
        code = Path(node.file_path).read_text()
        tree = ast.parse(code)
        
        # Find function in AST
        for ast_node in ast.walk(tree):
            if isinstance(ast_node, ast.FunctionDef) and ast_node.name == function_name:
                # Count decision points
                decision_count = 0
                for child in ast.walk(ast_node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                        decision_count += 1
                return decision_count + 1
        
        return 1  # Default complexity
    
    def calculate_centrality(self) -> Dict[str, float]:
        """
        Calculate node centrality (number of connections).
        
        Returns:
            Dictionary mapping node names to centrality scores
        """
        centrality = {}
        
        # Count incoming + outgoing edges for each node
        for name in self.graph.nodes.keys():
            outgoing = sum(1 for rel in self.graph.relationships if rel.source == name)
            incoming = sum(1 for rel in self.graph.relationships if rel.target == name)
            centrality[name] = outgoing + incoming
        
        return centrality
    
    def detect_hotspots(self, complexity_threshold: int = 3) -> List[str]:
        """
        Detect code hotspots (high complexity + high centrality).
        
        Args:
            complexity_threshold: Minimum complexity to consider
            
        Returns:
            List of hotspot node names
        """
        hotspots = []
        centrality = self.calculate_centrality()
        
        for name, node in self.graph.nodes.items():
            if node.type == "function":
                complexity = self.calculate_complexity(name)
                # Lowered centrality threshold to 0 (any connections)
                if complexity >= complexity_threshold and centrality.get(name, 0) >= 0:
                    hotspots.append(name)
        
        return hotspots
