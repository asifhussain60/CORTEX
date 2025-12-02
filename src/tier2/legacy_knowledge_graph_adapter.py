"""
Legacy Knowledge Graph Adapter

Bridges old KnowledgeGraph API (5-param store_pattern) to new modular facade API.
Enables Phase 7.2 pattern learning components to work with either implementation.

Design:
- Wraps new KnowledgeGraph facade
- Translates old API calls → new API calls
- Maps pattern types and handles namespace translation
- Maintains backward compatibility during migration

Usage:
    # Old code using monolithic API
    kg = KnowledgeGraph(db_path)
    pattern_id = kg.store_pattern(
        title="My Pattern",
        pattern_type="workflow",
        confidence=0.8,
        context={'key': 'value'},
        namespaces=['test']
    )
    
    # New code using adapter
    from src.tier2.legacy_knowledge_graph_adapter import LegacyKnowledgeGraphAdapter
    kg = LegacyKnowledgeGraphAdapter(db_path)
    pattern_id = kg.store_pattern(...)  # Same API, works!

Author: Asif Hussain
"""

import hashlib
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import the new modular facade
from src.tier2.knowledge_graph.knowledge_graph import KnowledgeGraph as ModernKnowledgeGraph


class LegacyKnowledgeGraphAdapter:
    """
    Adapter wrapping modern KnowledgeGraph facade with legacy API.
    
    Translates old store_pattern(title, pattern_type, confidence, context, scope, namespaces)
    to new store_pattern(pattern_id, title, content, pattern_type, confidence, metadata, ...).
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize adapter with modern KnowledgeGraph backend
        
        Args:
            db_path: Path to SQLite database (optional, uses default if None)
        """
        if db_path is not None:
            db_path = Path(db_path)
        self.modern_kg = ModernKnowledgeGraph(db_path=db_path)
    
    def store_pattern(
        self,
        title: str,
        pattern_type: str,
        confidence: float = 0.5,
        context: Dict[str, Any] = None,
        scope: str = "application",
        namespaces: List[str] = None
    ) -> str:
        """
        Store pattern using legacy API signature
        
        Args:
            title: Pattern name/title
            pattern_type: Type (workflow, intent, validation)
            confidence: Confidence score (0.0-1.0)
            context: Pattern details (files, steps, etc.)
            scope: Scope (cortex or application)
            namespaces: Namespace tags for isolation
        
        Returns:
            pattern_id: Unique identifier
        """
        # Generate pattern ID from title (consistent with old implementation)
        pattern_id = self._generate_pattern_id(title)
        
        # Convert context dict to content string (for new API)
        content = ""
        if context:
            # Extract content if available, otherwise serialize context
            content = context.get('content', json.dumps(context))
        
        # Map old pattern types to new valid types
        # Old: workflow, intent, validation
        # New: workflow, principle, anti_pattern, solution, context
        pattern_type_mapping = {
            'workflow': 'workflow',
            'intent': 'workflow',
            'validation': 'principle',
            'solution': 'solution',
            'context': 'context',
            'principle': 'principle',
            'anti_pattern': 'anti_pattern'
        }
        mapped_type = pattern_type_mapping.get(pattern_type, 'workflow')
        
        # Default namespaces
        if namespaces is None:
            namespaces = ["CORTEX-core"]
        
        # Store using modern API
        result = self.modern_kg.store_pattern(
            pattern_id=pattern_id,
            title=title,
            content=content,
            pattern_type=mapped_type,
            confidence=confidence,
            source=None,
            metadata=context,  # Store original context as metadata
            is_pinned=False,
            scope=scope,
            namespaces=namespaces,
            is_cortex_internal=True  # Adapter is framework code
        )
        
        return result.get('pattern_id', pattern_id)
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Get pattern by ID
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            Pattern dict or None if not found
        """
        pattern = self.modern_kg.get_pattern(pattern_id)
        
        if pattern is None:
            return None
        
        # Transform modern pattern format to legacy format
        legacy_pattern = {
            'pattern_id': pattern.get('pattern_id'),
            'title': pattern.get('title'),
            'pattern_type': pattern.get('pattern_type'),
            'confidence': pattern.get('confidence'),
            'scope': pattern.get('scope'),
            'created_at': pattern.get('created_at'),
            'last_used': pattern.get('last_used'),
            'usage_count': pattern.get('usage_count', 0)
        }
        
        # Convert metadata back to context_json
        metadata = pattern.get('metadata')
        if metadata:
            if isinstance(metadata, str):
                legacy_pattern['context_json'] = metadata
            else:
                legacy_pattern['context_json'] = json.dumps(metadata)
        else:
            legacy_pattern['context_json'] = None
        
        # Convert namespaces list to JSON string (legacy format)
        namespaces = pattern.get('namespaces', [])
        if isinstance(namespaces, list):
            legacy_pattern['namespaces'] = json.dumps(namespaces)
        else:
            legacy_pattern['namespaces'] = namespaces
        
        return legacy_pattern
    
    def search_patterns(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        min_confidence: float = 0.7,
        scope: Optional[str] = None,
        limit: int = 5,
        include_confidence_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search patterns using FTS5 (legacy API)
        
        Args:
            query: Search query string
            pattern_type: Filter by pattern type
            min_confidence: Minimum confidence threshold
            scope: Filter by scope (cortex/application)
            limit: Maximum results
            include_confidence_metadata: Include confidence metadata
            
        Returns:
            List of matching patterns
        """
        # Use modern search
        results = self.modern_kg.pattern_search.search_patterns(
            query=query,
            pattern_type=pattern_type,
            min_confidence=min_confidence,
            limit=limit
        )
        
        # Transform to legacy format
        legacy_results = []
        for pattern in results:
            legacy_pattern = self._to_legacy_format(pattern)
            
            # Filter by scope if specified
            if scope and legacy_pattern.get('scope') != scope:
                continue
            
            legacy_results.append(legacy_pattern)
        
        return legacy_results[:limit]
    
    def fts5_search(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        namespace_filter: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        FTS5 full-text search (legacy API)
        
        Args:
            query: Search query
            pattern_type: Filter by pattern type
            namespace_filter: Filter by namespace
            limit: Maximum results
            
        Returns:
            List of matching patterns
        """
        # Use modern search
        results = self.modern_kg.pattern_search.search_patterns(
            query=query,
            pattern_type=pattern_type,
            limit=limit
        )
        
        # Filter by namespace if specified
        if namespace_filter:
            filtered_results = []
            for pattern in results:
                namespaces = pattern.get('namespaces', [])
                if isinstance(namespaces, str):
                    namespaces = json.loads(namespaces)
                if namespace_filter in namespaces:
                    filtered_results.append(pattern)
            results = filtered_results
        
        # Transform to legacy format
        return [self._to_legacy_format(p) for p in results]
    
    def store_relationship(
        self,
        file_a: str,
        file_b: str,
        relationship_type: str,
        strength: float = 1.0,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store relationship between entities (legacy API)
        
        Args:
            file_a: First file path
            file_b: Second file path
            relationship_type: Type of relationship
            strength: Relationship strength (0.0-1.0)
            context: Additional context
            
        Returns:
            Relationship ID
        """
        return self.modern_kg.relationships.store_relationship(
            file_a=file_a,
            file_b=file_b,
            relationship_type=relationship_type,
            strength=strength,
            context=context
        )
    
    def get_relationships(
        self,
        file_path: Optional[str] = None,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get relationships with optional filters (legacy API)
        
        Args:
            file_path: Filter by file path (matches file_a or file_b)
            relationship_type: Filter by relationship type
            
        Returns:
            List of relationships
        """
        return self.modern_kg.relationships.get_relationships(
            file_path=file_path,
            relationship_type=relationship_type
        )
    
    def _generate_pattern_id(self, title: str) -> str:
        """
        Generate pattern ID from title (consistent with old implementation)
        
        Args:
            title: Pattern title
            
        Returns:
            Pattern ID
        """
        # Use hash of title + timestamp for uniqueness
        unique_string = f"{title}_{uuid.uuid4().hex[:8]}"
        hash_obj = hashlib.md5(unique_string.encode())
        return f"pattern_{hash_obj.hexdigest()[:16]}"
    
    def _to_legacy_format(self, modern_pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert modern pattern format to legacy format
        
        Args:
            modern_pattern: Pattern from modern KnowledgeGraph
            
        Returns:
            Pattern in legacy format
        """
        legacy_pattern = {
            'pattern_id': modern_pattern.get('pattern_id'),
            'title': modern_pattern.get('title'),
            'pattern_type': modern_pattern.get('pattern_type'),
            'confidence': modern_pattern.get('confidence'),
            'scope': modern_pattern.get('scope'),
            'created_at': modern_pattern.get('created_at'),
            'last_used': modern_pattern.get('last_used'),
            'usage_count': modern_pattern.get('usage_count', 0)
        }
        
        # Convert metadata to context_json
        metadata = modern_pattern.get('metadata')
        if metadata:
            if isinstance(metadata, str):
                legacy_pattern['context_json'] = metadata
            else:
                legacy_pattern['context_json'] = json.dumps(metadata)
        else:
            # Fallback to content field
            content = modern_pattern.get('content', '')
            legacy_pattern['context_json'] = json.dumps({'content': content})
        
        # Convert namespaces to JSON string
        namespaces = modern_pattern.get('namespaces', [])
        if isinstance(namespaces, list):
            legacy_pattern['namespaces'] = json.dumps(namespaces)
        else:
            legacy_pattern['namespaces'] = namespaces
        
        return legacy_pattern
    
    # Delegate other methods to modern KnowledgeGraph
    def __getattr__(self, name):
        """
        Delegate unknown methods to modern KnowledgeGraph
        
        This allows the adapter to work with new methods added to modern KG
        without needing explicit wrappers.
        """
        return getattr(self.modern_kg, name)
