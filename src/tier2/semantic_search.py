"""
Semantic Search - Enhanced FTS5 search wrapper with filters

Provides:
- FTS5 full-text search with ranking
- Pattern type filtering
- Namespace filtering
- Performance optimization (<100ms target)

Built on top of KnowledgeGraph FTS5 capabilities.

Author: Asif Hussain
"""

from typing import Dict, List, Any, Optional
import time


class SemanticSearch:
    """Enhanced semantic search with FTS5"""
    
    def __init__(self, knowledge_graph):
        """
        Initialize semantic search
        
        Args:
            knowledge_graph: Tier 2 KnowledgeGraph instance
        """
        self.knowledge_graph = knowledge_graph
    
    def search(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        namespaces: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search patterns with optional filters
        
        Args:
            query: Search query
            pattern_type: Optional filter by pattern type
            namespaces: Optional filter by namespaces
            limit: Maximum results
            
        Returns:
            List of matching patterns with scores
        """
        # Use FTS5 search from knowledge graph
        results = self.knowledge_graph.fts5_search(query, limit=limit * 2)  # Get more for filtering
        
        filtered_results = []
        
        for result in results:
            # Apply pattern type filter
            if pattern_type and result.get('pattern_type') != pattern_type:
                continue
            
            # Apply namespace filter
            if namespaces:
                pattern_namespaces = self._extract_namespaces(result.get('context_json', ''))
                if not any(ns in pattern_namespaces for ns in namespaces):
                    continue
            
            # Add rank/score to result
            if 'relevance' in result:
                result['rank'] = result['relevance']
                result['score'] = abs(result['relevance'])  # FTS5 rank is negative
            else:
                result['rank'] = 0
                result['score'] = result.get('confidence', 0.5)
            
            filtered_results.append(result)
            
            # Stop when we have enough results
            if len(filtered_results) >= limit:
                break
        
        return filtered_results
    
    def _extract_namespaces(self, context_json: str) -> List[str]:
        """Extract namespaces from context JSON or pattern namespaces field"""
        import json
        
        namespaces = []
        
        try:
            # Try to parse as JSON
            context = json.loads(context_json) if context_json else {}
            
            # Check for namespaces in context
            if 'namespaces' in context:
                namespaces = context['namespaces']
            
        except (json.JSONDecodeError, TypeError):
            # If not JSON, try comma-separated string
            if context_json:
                namespaces = [ns.strip() for ns in context_json.split(',')]
        
        return namespaces
