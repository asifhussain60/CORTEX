"""
Pattern Search Module

Handles semantic search across patterns using SQLite FTS5 (Full-Text Search).

Responsibilities:
    - FTS5 index management
    - BM25-ranked search queries
    - Namespace-aware search (boundary enforcement)
    - Multi-filter search (tags, confidence, scope)
    - Related pattern discovery

Performance Targets:
    - Simple search: <50ms
    - Complex search (multi-filter): <100ms
    - FTS5 ranking: <20ms overhead

Example:
    >>> from tier2.knowledge_graph.patterns.pattern_search import PatternSearch
    >>> search = PatternSearch(db)
    >>> results = search.search("TDD workflow", min_confidence=0.8)
    >>> for result in results:
    ...     print(f"{result['title']}: {result['score']}")
"""

from typing import List, Dict, Any, Optional
import json


class PatternSearch:
    """
    Semantic pattern search using FTS5.
    
    Implements BM25-ranked full-text search with namespace awareness
    and confidence-based filtering.
    """
    
    def __init__(self, db):
        """
        Initialize Pattern Search engine.
        
        Args:
            db: DatabaseConnection instance
        """
        self.db = db
    
    def search(
        self,
        query: str,
        min_confidence: float = 0.5,
        scope: Optional[str] = None,
        namespaces: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search patterns using FTS5 semantic search with BM25 ranking.
        
        Supports FTS5 query syntax:
        - Simple keywords: "testing"
        - Phrase search: '"test driven development"'
        - Boolean operators: "testing AND refactoring"
        - Prefix matching: "refactor*"
        - NOT operator: "testing NOT manual"
        
        Args:
            query: Search query string (FTS5 syntax)
            min_confidence: Minimum confidence threshold (0.0-1.0)
            scope: Filter by scope ('cortex' or 'application')
            namespaces: Filter by specific namespaces
            limit: Maximum results to return
        
        Returns:
            List of patterns ranked by BM25 score (lower score = better match)
        
        Performance: <50ms for simple queries
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Build WHERE clause for filters
        where_clauses = ["p.confidence >= ?"]
        params = [min_confidence]
        
        if scope:
            where_clauses.append("p.scope = ?")
            params.append(scope)
        
        if namespaces:
            # Check if any namespace matches (JSON array contains check)
            namespace_conditions = []
            for ns in namespaces:
                namespace_conditions.append(f"p.namespaces LIKE ?")
                params.append(f'%"{ns}"%')
            where_clauses.append(f"({' OR '.join(namespace_conditions)})")
        
        where_sql = " AND ".join(where_clauses)
        
        # FTS5 search with BM25 ranking
        query_sql = f"""
            SELECT p.pattern_id, p.title, p.content, p.pattern_type, p.confidence,
                   p.created_at, p.last_accessed, p.access_count, p.source, p.metadata,
                   p.is_pinned, p.scope, p.namespaces,
                   bm25(pattern_fts) as rank
            FROM patterns p
            JOIN pattern_fts ON p.id = pattern_fts.rowid
            WHERE pattern_fts MATCH ? AND {where_sql}
            ORDER BY rank
            LIMIT ?
        """
        
        params_full = [query] + params + [limit]
        cursor.execute(query_sql, params_full)
        
        rows = cursor.fetchall()
        
        # Convert to dictionaries
        results = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces_data = json.loads(row[12]) if row[12] else ["CORTEX-core"]
            
            results.append({
                "pattern_id": row[0],
                "title": row[1],
                "content": row[2],
                "pattern_type": row[3],
                "confidence": row[4],
                "created_at": row[5],
                "last_accessed": row[6],
                "access_count": row[7],
                "source": row[8],
                "metadata": metadata,
                "is_pinned": bool(row[10]),
                "scope": row[11] if row[11] else "cortex",
                "namespaces": namespaces_data,
                "score": row[13]  # BM25 score (lower = better)
            })
        
        return results
    
    def search_with_namespace_priority(
        self,
        query: str,
        current_namespace: Optional[str] = None,
        include_cortex: bool = True,
        min_confidence: float = 0.5,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search patterns with namespace priority boosting.
        
        Priority ranking:
        1. Current namespace patterns (highest priority)
        2. Cortex core patterns (if include_cortex=True)
        3. Other namespace patterns (lowest priority)
        
        Args:
            query: Search query (FTS5 syntax)
            current_namespace: Current application context (e.g., 'KSESSIONS')
            include_cortex: Include CORTEX-core patterns (default True)
            min_confidence: Minimum confidence threshold
            limit: Maximum results
        
        Returns:
            List of patterns with namespace-boosted ranking
        
        Performance: <100ms
        """
        # Get all matching patterns
        all_results = self.search(
            query=query,
            min_confidence=min_confidence,
            limit=limit * 3  # Get more to allow for reranking
        )
        
        # Apply namespace boosting
        boosted_results = []
        for result in all_results:
            result_namespaces = result.get("namespaces", [])
            
            # Calculate priority weight
            if current_namespace and current_namespace in result_namespaces:
                weight = 2.0  # Current namespace boost
            elif include_cortex and "CORTEX-core" in result_namespaces:
                weight = 1.5  # Core patterns boost
            else:
                weight = 0.5  # Other namespaces
            
            # Adjust BM25 score (lower is better, so divide by weight)
            result["weighted_score"] = result["score"] / weight
            boosted_results.append(result)
        
        # Re-sort by weighted score and limit
        boosted_results.sort(key=lambda x: x["weighted_score"])
        return boosted_results[:limit]
    
    def get_patterns_by_namespace(
        self,
        namespace: str,
        min_confidence: float = 0.5,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get all patterns in a specific namespace.
        
        Args:
            namespace: Namespace to filter by
            min_confidence: Minimum confidence threshold
            limit: Maximum results
        
        Returns:
            List of patterns in the namespace
        
        Performance: <30ms
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_id, title, content, pattern_type, confidence,
                   created_at, last_accessed, access_count, source, metadata,
                   is_pinned, scope, namespaces
            FROM patterns
            WHERE namespaces LIKE ? AND confidence >= ?
            ORDER BY confidence DESC, last_accessed DESC
            LIMIT ?
        """, (f'%"{namespace}"%', min_confidence, limit))
        
        rows = cursor.fetchall()
        
        patterns = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces = json.loads(row[12]) if row[12] else ["CORTEX-core"]
            
            patterns.append({
                "pattern_id": row[0],
                "title": row[1],
                "content": row[2],
                "pattern_type": row[3],
                "confidence": row[4],
                "created_at": row[5],
                "last_accessed": row[6],
                "access_count": row[7],
                "source": row[8],
                "metadata": metadata,
                "is_pinned": bool(row[10]),
                "scope": row[11] if row[11] else "cortex",
                "namespaces": namespaces
            })
        
        return patterns
    
    def get_cortex_patterns(
        self,
        min_confidence: float = 0.5,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get all CORTEX core patterns.
        
        Args:
            min_confidence: Minimum confidence threshold
            limit: Maximum results
        
        Returns:
            List of CORTEX-core patterns
        """
        return self.get_patterns_by_namespace("CORTEX-core", min_confidence, limit)
    
    def get_application_patterns(
        self,
        namespace: str,
        min_confidence: float = 0.5,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get application-specific patterns (non-CORTEX).
        
        Args:
            namespace: Application namespace (e.g., 'KSESSIONS')
            min_confidence: Minimum confidence threshold
            limit: Maximum results
        
        Returns:
            List of application patterns
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_id, title, content, pattern_type, confidence,
                   created_at, last_accessed, access_count, source, metadata,
                   is_pinned, scope, namespaces
            FROM patterns
            WHERE scope = 'application' 
              AND namespaces LIKE ? 
              AND confidence >= ?
            ORDER BY confidence DESC, last_accessed DESC
            LIMIT ?
        """, (f'%"{namespace}"%', min_confidence, limit))
        
        rows = cursor.fetchall()
        
        patterns = []
        for row in rows:
            metadata = json.loads(row[9]) if row[9] else None
            namespaces = json.loads(row[12]) if row[12] else [namespace]
            
            patterns.append({
                "pattern_id": row[0],
                "title": row[1],
                "content": row[2],
                "pattern_type": row[3],
                "confidence": row[4],
                "created_at": row[5],
                "last_accessed": row[6],
                "access_count": row[7],
                "source": row[8],
                "metadata": metadata,
                "is_pinned": bool(row[10]),
                "scope": row[11] if row[11] else "application",
                "namespaces": namespaces
            })
        
        return patterns
