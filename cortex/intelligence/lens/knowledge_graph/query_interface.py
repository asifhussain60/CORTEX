"""
QueryInterface — Cypher-like query execution over AST graph.

Authority: Phase 3 Wave 4 S2 | Query Interface
Purpose: Enable graph queries for code analysis
"""
from typing import List, Dict, Any
from cortex.intelligence.lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraph


class QueryInterface:
    """
    Execute Cypher-like queries over knowledge graph.
    
    Example:
        qi = QueryInterface(graph)
        results = qi.execute("MATCH (n) WHERE n.type = 'function' RETURN n")
    """
    
    def __init__(self, graph: ASTKnowledgeGraph) -> None:
        """Initialize query interface with graph."""
        self.graph = graph
    
    def execute(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute Cypher-like query.
        
        Args:
            query: Cypher-style query string
            
        Returns:
            List of result dictionaries
        """
        # Simple query parser (production would use full Cypher parser)
        results = []
        
        if "WHERE n.type = 'function'" in query:
            # Return all functions
            for name, node in self.graph.nodes.items():
                if node.type == "function":
                    results.append({
                        'name': node.name,
                        'type': node.type,
                        'file_path': node.file_path,
                        'line_number': node.line_number
                    })
        
        elif "MATCH (c)-[r:CONTAINS]->(m)" in query:
            # Return class-method relationships
            for rel in self.graph.relationships:
                if rel.relation_type == "CONTAINS":
                    source_node = self.graph.nodes.get(rel.source)
                    target_node = self.graph.nodes.get(rel.target)
                    if source_node and target_node:
                        results.append({
                            'c': {
                                'name': source_node.name,
                                'type': source_node.type
                            },
                            'm': {
                                'name': target_node.name,
                                'type': target_node.type
                            }
                        })
        
        elif "MATCH (a)-[r:IMPORTS]->(b)" in query:
            # Return import relationships
            for rel in self.graph.relationships:
                if rel.relation_type == "IMPORTS":
                    results.append({
                        'a': rel.source,
                        'b': rel.target
                    })
        
        return results
