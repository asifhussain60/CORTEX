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
                # Get namespaces from result (stored as JSON string in legacy format)
                pattern_namespaces = self._extract_namespaces(result)
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
    
    def _extract_namespaces(self, result: Dict[str, Any]) -> List[str]:
        """Extract namespaces from pattern result"""
        import json
        
        namespaces = []
        
        # First try the namespaces field directly (returned by adapter)
        if 'namespaces' in result:
            namespaces_data = result['namespaces']
            
            # If it's already a list, return it
            if isinstance(namespaces_data, list):
                return namespaces_data
            
            # If it's a JSON string, parse it
            if isinstance(namespaces_data, str):
                try:
                    namespaces = json.loads(namespaces_data)
                    if isinstance(namespaces, list):
                        return namespaces
                except json.JSONDecodeError:
                    pass
        
        # Fallback: try to extract from context_json
        context_json = result.get('context_json', '')
        if context_json:
            try:
                context = json.loads(context_json) if context_json else {}
                if 'namespaces' in context:
                    namespaces = context['namespaces']
            except (json.JSONDecodeError, TypeError):
                pass
        
        return namespaces if isinstance(namespaces, list) else []
