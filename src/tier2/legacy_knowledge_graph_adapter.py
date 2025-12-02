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
        namespaces: List[str] = None,
        pattern_id: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store pattern using legacy API signature (supports both old and new API parameters)
        
        Args:
            title: Pattern name/title
            pattern_type: Type (workflow, intent, validation)
            confidence: Confidence score (0.0-1.0)
            context: Pattern details (files, steps, etc.) - legacy parameter
            scope: Scope (cortex or application)
            namespaces: Namespace tags for isolation
            pattern_id: Optional pattern ID (generated if not provided)
            content: Pattern content string (new API parameter, takes precedence over context)
            metadata: Structured metadata dict (new API parameter, takes precedence over context)
        
        Returns:
            pattern_id: Unique identifier
        """
        # Generate pattern ID from title (consistent with old implementation)
        if pattern_id is None:
            pattern_id = self._generate_pattern_id(title)
        
        # Determine is_cortex_internal from scope or namespace
        is_cortex_internal = scope == "cortex" or (
            namespaces and any(ns.startswith("cortex.") for ns in namespaces)
        )
        
        # Map context/content: new API uses 'content' (str) for FTS5 and 'metadata' (dict) for structured data
        # Priority: content/metadata params > context param
        if content is None:
            if context:
                # Extract content if available, otherwise serialize context
                content = context.get('content', json.dumps(context))
            else:
                content = ""
        
        # metadata is the structured data (prefer explicit metadata param, fallback to context)
        if metadata is None:
            metadata = context
        
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
            metadata=metadata,  # Use the resolved metadata
            is_pinned=False,
            scope=scope,
            namespaces=namespaces,
            is_cortex_internal=is_cortex_internal
        )
        
        # For backward compatibility: return dict if result is dict, otherwise return str
        # This handles both old code expecting str and new code expecting dict
        if isinstance(result, dict):
            return result  # New code can handle dict
        else:
            return pattern_id  # Old code expects just the ID string
    
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
        # Use modern search (method is 'search', not 'search_patterns')
        results = self.modern_kg.pattern_search.search(
            query=query,
            min_confidence=min_confidence,
            scope=scope,
            limit=limit
        )
        
        # Filter by pattern_type if specified (modern search doesn't have this filter)
        if pattern_type:
            results = [p for p in results if p.get('pattern_type') == pattern_type]
        
        # Transform to legacy format
        legacy_results = [self._to_legacy_format(p) for p in results]
        
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
        # Build namespaces filter list
        namespaces = [namespace_filter] if namespace_filter else None
        
        # Use modern search (method is 'search', not 'search_patterns')
        results = self.modern_kg.pattern_search.search(
            query=query,
            namespaces=namespaces,
            limit=limit
        )
        
        # Filter by pattern_type if specified
        if pattern_type:
            results = [p for p in results if p.get('pattern_type') == pattern_type]
        
        # Transform to legacy format
        return [self._to_legacy_format(p) for p in results]
    
    def store_relationship(
        self,
        file_a: str,
        file_b: str,
        relationship_type: str,
        strength: float = 1.0,
        context: Optional[Dict[str, Any]] = None,
        relationship_id: Optional[str] = None
    ) -> str:
        """
        Store relationship between entities (legacy API)
        
        Args:
            file_a: First file path
            file_b: Second file path
            relationship_type: Type of relationship
            strength: Relationship strength (0.0-1.0)
            context: Additional context
            relationship_id: Optional relationship ID (generated if not provided)
            
        Returns:
            Relationship ID
        """
        # Generate relationship ID if not provided
        if relationship_id is None:
            import hashlib
            rel_data = f"{file_a}_{file_b}_{relationship_type}"
            relationship_id = f"rel_{hashlib.md5(rel_data.encode()).hexdigest()[:12]}"
        
        # Check if modern KG has relationships module
        if hasattr(self.modern_kg, 'relationships') and hasattr(self.modern_kg.relationships, 'add_relationship'):
            # Use modern relationships API
            result = self.modern_kg.relationships.add_relationship(
                entity_a=file_a,
                entity_b=file_b,
                relationship_type=relationship_type,
                strength=strength,
                metadata={"context": context} if context else None
            )
            return result.get("relationship_id", relationship_id)
        else:
            # Fallback: store as pattern with relationship data
            # This ensures compatibility even if relationships module isn't fully implemented
            # Store both file_a/file_b (internal) and source/target (for test compatibility)
            relationship_context = {
                "relationship_id": relationship_id,
                "file_a": file_a,
                "file_b": file_b,
                "source": file_a,  # Map for test compatibility
                "target": file_b,   # Map for test compatibility
                "relationship_type": relationship_type,
                "context": context,
                "entity_type": "relationship"
            }
            
            return self.store_pattern(
                title=f"{file_a} → {file_b}",
                pattern_type="context",  # Use valid pattern type
                confidence=strength,
                context=relationship_context,
                scope="application",
                namespaces=["workspace.relationships"]
            )
    
    def get_relationships(
        self,
        file_a: Optional[str] = None,
        file_b: Optional[str] = None,
        file_path: Optional[str] = None,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get relationships with optional filters (legacy API)
        
        Args:
            file_a: Filter by first file (optional)
            file_b: Filter by second file (optional)
            file_path: Filter by file path (matches file_a or file_b) - legacy param
            relationship_type: Filter by relationship type
            
        Returns:
            List of relationships
        """
        # Handle legacy file_path parameter
        if file_path is not None and file_a is None:
            file_a = file_path
        
        # Check if modern KG has relationships module
        if hasattr(self.modern_kg, 'relationships') and hasattr(self.modern_kg.relationships, 'list_relationships'):
            return self.modern_kg.relationships.list_relationships(
                entity_a=file_a,
                entity_b=file_b,
                relationship_type=relationship_type
            )
        else:
            # Fallback: query patterns with entity_type=relationship
            results = self.search_patterns(
                query="relationship" if not relationship_type else relationship_type,
                pattern_type="context",
                limit=100
            )
            
            # Filter for relationship entities and apply filters
            relationships = []
            for pattern in results:
                # Get metadata from pattern (might be in 'metadata' or 'context_json')
                context = pattern.get('metadata')
                if context is None:
                    context_json = pattern.get('context_json')
                    if context_json:
                        try:
                            context = json.loads(context_json)
                        except:
                            continue
                    else:
                        continue
                
                if isinstance(context, str):
                    try:
                        context = json.loads(context)
                    except:
                        continue
                
                # Check if it's a relationship entity
                if context.get('entity_type') != 'relationship':
                    continue
                
                # Apply filters (support both file_a/file_b and source/target naming)
                source = context.get('source') or context.get('file_a')
                target = context.get('target') or context.get('file_b')
                
                if file_a and source != file_a:
                    continue
                if file_b and target != file_b:
                    continue
                if relationship_type and context.get('relationship_type') != relationship_type:
                    continue
                
                # Ensure the returned dict has expected keys for tests
                relationship = {
                    'relationship_id': context.get('relationship_id'),
                    'source': source,
                    'target': target,
                    'file_a': source,
                    'file_b': target,
                    'relationship_type': context.get('relationship_type'),
                    'strength': pattern.get('confidence', 1.0),
                    'context': context.get('context', '')
                }
                relationships.append(relationship)
            
            return relationships
    
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
