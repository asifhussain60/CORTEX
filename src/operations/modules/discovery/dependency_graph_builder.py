"""
Dependency graph construction from code elements
"""
import logging
from typing import List, Dict, Set, Tuple

from .models import CodeElement, DependencyGraph

logger = logging.getLogger(__name__)


class DependencyGraphBuilder:
    """Build and analyze dependency graphs"""
    
    def __init__(self):
        """Initialize dependency graph builder"""
        pass
    
    def build_graph(self, elements: List[CodeElement]) -> DependencyGraph:
        """
        Construct dependency graph from code elements
        
        Args:
            elements: List of code elements
            
        Returns:
            DependencyGraph with nodes and edges
        """
        graph = DependencyGraph()
        
        # Add all elements as nodes
        for element in elements:
            graph.nodes[element.name] = element
        
        # Build edges from dependencies
        for element in elements:
            for dep_name in element.dependencies:
                if dep_name in graph.nodes:
                    graph.edges.append((element.name, dep_name))
        
        # Detect cycles
        graph.cycles = self.detect_cycles(graph)
        
        return graph
    
    def find_dependencies(self, element: CodeElement, all_elements: List[CodeElement]) -> List[str]:
        """
        Find dependencies for a code element
        
        Args:
            element: Code element to analyze
            all_elements: All available code elements
            
        Returns:
            List of dependency names
        """
        # Return existing dependencies
        return element.dependencies
    
    def detect_cycles(self, graph: DependencyGraph) -> List[List[str]]:
        """
        Detect circular dependencies in graph
        
        Args:
            graph: Dependency graph
            
        Returns:
            List of cycles (each cycle is a list of element names)
        """
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> bool:
            """DFS to detect cycles"""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Find neighbors
            neighbors = [target for source, target in graph.edges if source == node]
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    if dfs(neighbor, path[:]):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check each node
        for node_name in graph.nodes:
            if node_name not in visited:
                dfs(node_name, [])
        
        return cycles
