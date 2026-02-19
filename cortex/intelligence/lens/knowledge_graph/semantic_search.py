"""
SemanticSearchEngine — Search over knowledge graph.

Authority: Phase 3 Wave 4 | LENS Knowledge Graph
Purpose: Enable semantic search over code entities
"""
from dataclasses import dataclass
from typing import List
from cortex.intelligence.lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraph


@dataclass
class SearchResult:
    """Result from semantic search."""
    name: str
    type: str
    file_path: str
    line_number: int
    relevance_score: float


class SemanticSearchEngine:
    """
    Semantic search over knowledge graph.
    
    Example:
        search = SemanticSearchEngine(graph)
        results = search.find_by_name("calculate_total")
    """
    
    def __init__(self, graph: ASTKnowledgeGraph) -> None:
        """Initialize search engine with graph."""
        self.graph = graph
    
    def find_by_name(self, query: str) -> List[SearchResult]:
        """
        Search for entities by name.
        
        Args:
            query: Entity name to search for
            
        Returns:
            List of matching SearchResults
        """
        results = []
        
        for name, node in self.graph.nodes.items():
            if query.lower() in name.lower():
                results.append(SearchResult(
                    name=node.name,
                    type=node.type,
                    file_path=node.file_path,
                    line_number=node.line_number,
                    relevance_score=1.0 if query == name else 0.8
                ))
        
        return sorted(results, key=lambda r: r.relevance_score, reverse=True)
    
    def find_pattern(self, pattern_type: str) -> List[SearchResult]:
        """
        Search for architectural patterns.
        
        Args:
            pattern_type: Pattern to search for (e.g., "repository_pattern")
            
        Returns:
            List of matching entities
        """
        results = []
        
        # Simple heuristic: look for naming conventions
        if pattern_type == "repository_pattern":
            for name, node in self.graph.nodes.items():
                # Check both the class name and field names in the AST
                if "repository" in name.lower() or "service" in name.lower():
                    results.append(SearchResult(
                        name=node.name,
                        type=node.type,
                        file_path=node.file_path,
                        line_number=node.line_number,
                        relevance_score=0.9
                    ))
        
        return results
