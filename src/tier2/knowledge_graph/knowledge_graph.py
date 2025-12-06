"""
KnowledgeGraph Facade (Coordinator)

Provides a backward-compatible, high-level API aggregating modular components:
    - PatternStore (CRUD + confidence/access tracking)
    - PatternSearch (FTS5 BM25 ranked search + namespace boosting)
    - PatternDecay (scheduled confidence decay + audit trail)
    - RelationshipManager (graph edges CRUD + traversal)
    - TagManager (tag CRUD + queries)

Design Goals:
    - Keep each module <500 LOC (SOLID single responsibility)
    - Orchestrate operations without duplicating logic
    - Provide stable API while legacy code migrates off monolith
    - Allow eventual consolidation of database abstraction

NOTE:
    Two database abstractions currently exist (DatabaseConnection & ConnectionManager).
    This facade uses ConnectionManager for slimmer transactional helpers. A future
    consolidation can rename it to KGDatabase and remove DatabaseConnection.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

from .database.connection import ConnectionManager
from .patterns.pattern_store import PatternStore
from .patterns.pattern_search import PatternSearch
from .patterns.pattern_decay import PatternDecay
from .relationships.relationship_manager import RelationshipManager
from .tags.tag_manager import TagManager


class KnowledgeGraph:
    """High-level orchestration for Knowledge Graph operations."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # Default consistent with existing database modules
            root = Path(__file__).parent.parent.parent.parent / "cortex-brain" / "tier2"
            root.mkdir(parents=True, exist_ok=True)
            db_path = root / "knowledge_graph.db"
        self.connection_manager = ConnectionManager(db_path=db_path)

        # Component instances
        self.pattern_store = PatternStore(self.connection_manager)
        self.pattern_search = PatternSearch(self.connection_manager)
        self.pattern_decay = PatternDecay(self.connection_manager)
        self.relationships = RelationshipManager(self.connection_manager)
        self.tags = TagManager(self.connection_manager)

    # ---------------------- Pattern CRUD ----------------------
    def store_pattern(self, **kwargs) -> Dict[str, Any]:
        return self.pattern_store.store_pattern(**kwargs)
    
    def learn_pattern(self, pattern: Dict[str, Any], namespace: str, is_cortex_internal: bool = False) -> Dict[str, Any]:
        """
        Learn a new pattern with namespace protection.
        
        Wrapper for store_pattern that accepts pattern dict and namespace separately.
        Useful for cleaner test syntax.
        """
        import uuid
        
        if namespace is None or namespace == "":
            raise ValueError(
                "namespace is required. Use 'cortex.*' for framework patterns "
                "or 'workspace.*' for application patterns."
            )
        
        pattern_id = pattern.get("pattern_id", str(uuid.uuid4()))
        return self.pattern_store.store_pattern(
            pattern_id=pattern_id,
            title=pattern.get("title", "Untitled Pattern"),
            content=pattern.get("content", ""),
            pattern_type=pattern.get("pattern_type", "workflow"),
            confidence=pattern.get("confidence", 1.0),
            source=pattern.get("source"),
            metadata=pattern.get("metadata"),
            is_pinned=pattern.get("is_pinned", False),
            scope=pattern.get("scope", "cortex" if namespace.startswith("cortex.") else "application"),
            namespaces=[namespace],
            is_cortex_internal=is_cortex_internal
        )
    
    def query(self, namespace_filter: str = "*", **kwargs) -> List[Dict[str, Any]]:
        """
        Query patterns with namespace filtering.
        
        Wrapper that provides namespace-based filtering on top of search.
        DB-level filtering for optimal performance (O(log n) vs O(n)).
        """
        # Push namespace filtering to database layer for performance
        if namespace_filter != "*":
            kwargs['namespace_filter'] = namespace_filter
        
        return self.pattern_store.list_patterns(**kwargs)

    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        return self.pattern_store.get_pattern(pattern_id)

    def update_pattern(self, pattern_id: str, updates: Dict[str, Any]) -> bool:
        return self.pattern_store.update_pattern(pattern_id, updates)

    def delete_pattern(self, pattern_id: str) -> bool:
        return self.pattern_store.delete_pattern(pattern_id)

    def list_patterns(self, **filters) -> List[Dict[str, Any]]:
        return self.pattern_store.list_patterns(**filters)

    # ---------------------- Search ----------------------
    def search_patterns(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_search.search(query=query, **kwargs)
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Alias for search_patterns for backward compatibility."""
        return self.search_patterns(query=query, **kwargs)

    def search_patterns_with_namespace_priority(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_search.search_with_namespace_priority(query=query, **kwargs)
    
    def add_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a pattern (alias for store_pattern for backward compatibility).
        
        Args:
            pattern: Pattern dictionary containing fields like:
                - pattern_id: Optional unique ID
                - title: Pattern title
                - content: Pattern content
                - pattern_type: Type of pattern (workflow, intent, validation, etc.)
                - confidence: Confidence score (0.0-1.0)
                - etc.
            
        Returns:
            Result dictionary with pattern_id and status
        """
        # Extract fields from pattern dict with defaults
        import uuid
        
        return self.store_pattern(
            pattern_id=pattern.get('pattern_id', str(uuid.uuid4())),
            title=pattern.get('title', 'Untitled Pattern'),
            content=pattern.get('content', ''),
            pattern_type=pattern.get('pattern_type', 'workflow'),
            confidence=pattern.get('confidence', 1.0),
            source=pattern.get('source'),
            metadata=pattern.get('metadata'),
            is_pinned=pattern.get('is_pinned', False),
            scope=pattern.get('scope', 'application'),
            namespaces=pattern.get('namespaces', []),
            is_cortex_internal=pattern.get('is_cortex_internal', False)
        )

    def get_cortex_patterns(self, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_search.get_cortex_patterns(**kwargs)

    def get_application_patterns(self, namespace: str, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_search.get_application_patterns(namespace=namespace, **kwargs)

    # ---------------------- Decay ----------------------
    def apply_decay(self) -> Dict[str, Any]:
        return self.pattern_decay.apply_decay()

    def get_decay_candidates(self) -> List[Dict[str, Any]]:
        return self.pattern_decay.get_decay_candidates()

    def pin_pattern(self, pattern_id: str) -> bool:
        return self.pattern_decay.pin_pattern(pattern_id)

    def unpin_pattern(self, pattern_id: str) -> bool:
        return self.pattern_decay.unpin_pattern(pattern_id)

    def get_decay_log(self, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_decay.get_decay_log(**kwargs)

    # ---------------------- Relationships ----------------------
    def create_relationship(self, **kwargs) -> Dict[str, Any]:
        return self.relationships.create_relationship(**kwargs)

    def get_relationships(self, pattern_id: str, direction: str = "both") -> List[Dict[str, Any]]:
        return self.relationships.get_relationships(pattern_id=pattern_id, direction=direction)

    def traverse_graph(self, start_pattern: str, **kwargs) -> Dict[str, Any]:
        return self.relationships.traverse_graph(start_pattern=start_pattern, **kwargs)

    # ---------------------- Tags ----------------------
    def add_tag(self, pattern_id: str, tag: str) -> bool:
        return self.tags.add_tag(pattern_id, tag)

    def remove_tag(self, pattern_id: str, tag: str) -> bool:
        return self.tags.remove_tag(pattern_id, tag)

    def get_tags(self, pattern_id: str) -> List[str]:
        return self.tags.get_tags(pattern_id)

    def get_patterns_by_tag(self, tag: str, **kwargs) -> List[Dict[str, Any]]:
        return self.tags.get_patterns_by_tag(tag=tag, **kwargs)

    def list_all_tags(self) -> List[Dict[str, int]]:
        return self.tags.list_all_tags()

    # ---------------------- Architectural Analysis Saving ----------------------
    def detect_analysis_namespace(self, request: str, context: Dict[str, Any]) -> str:
        """
        Detect appropriate namespace for analysis based on request and context.
        
        Args:
            request: User's request text
            context: Analysis context (files analyzed, workspace, etc.)
        
        Returns:
            Namespace string (e.g., 'ksessions_architecture', 'workspace.features.etymology')
        """
        import re
        
        # Extract workspace name from context
        workspace_path = context.get('workspace_path', '')
        workspace_name = None
        
        # Try to extract workspace name from common patterns
        if 'KSESSIONS' in workspace_path.upper():
            workspace_name = 'ksessions'
        elif workspace_path:
            # Extract last folder name as workspace
            workspace_name = Path(workspace_path).name.lower()
        
        request_lower = request.lower()
        files_analyzed = context.get('files_analyzed', [])
        
        if workspace_name:
            # Architecture-level analysis patterns
            architecture_patterns = [
                'architecture', 'routing', 'shell', 'structure', 'crawl', 'understand',
                'layout', 'navigation', 'view injection', 'component system'
            ]
            
            feature_patterns = [
                'feature', 'etymology', 'quran', 'ahadees', 'admin', 'album', 
                'session', 'manage', 'registration'
            ]
            
            if any(pattern in request_lower for pattern in architecture_patterns):
                return f'{workspace_name}_architecture'
            
            for pattern in feature_patterns:
                if pattern in request_lower:
                    # Extract the specific feature name, not just the word "feature"
                    if pattern == 'feature':
                        # Look for specific feature names after "feature"
                        for specific_feature in ['etymology', 'quran', 'ahadees', 'admin', 'album', 'session', 'manage', 'registration']:
                            if specific_feature in request_lower:
                                return f'{workspace_name}_features.{specific_feature}'
                    else:
                        return f'{workspace_name}_features.{pattern}'
                    
            architectural_files = [
                'shell.html', 'config.route.js', 'app.js', 'layout', 'topnav'
            ]
            if any(any(arch_file in analyzed_file for arch_file in architectural_files) 
                   for analyzed_file in files_analyzed):
                return f'{workspace_name}_architecture'
                
            # Default workspace namespace
            return f'{workspace_name}_general'
        
        # Fallback to general validation insights
        return 'validation_insights'

    def save_architectural_analysis(self, namespace: str, analysis_data: Dict[str, Any], 
                                  metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Save architectural analysis to knowledge graph with proper namespace.
        
        Args:
            namespace: Detected namespace for this analysis
            analysis_data: Structured analysis results
            metadata: Optional metadata about the analysis
            
        Returns:
            Dict with save results and confirmation data
        """
        from datetime import datetime
        import uuid
        
        # Generate pattern ID based on namespace and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pattern_id = f"{namespace}_{timestamp}_{str(uuid.uuid4())[:8]}"
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
            
        analysis_metadata = {
            'analyzed_date': datetime.now().isoformat(),
            'analyzed_by': 'CORTEX (GitHub Copilot)',
            'namespace': namespace,
            'analysis_type': 'architectural',
            'confidence': 1.0,
            **metadata
        }
        
        content = self._format_analysis_content(analysis_data, namespace)
        
        # Store pattern in knowledge graph
        pattern_result = self.store_pattern(
            pattern_id=pattern_id,
            title=f"Architecture Analysis: {namespace}",
            content=content,
            pattern_type="architectural",
            confidence=1.0,
            source="cortex_analysis",
            metadata=analysis_metadata,
            is_pinned=True,  # Important analysis should be pinned
            scope="application",
            namespaces=[namespace],
            is_cortex_internal=False
        )
        
        return {
            'saved': pattern_result.get('success', False),
            'pattern_id': pattern_id,
            'namespace': namespace,
            'items_saved': len(analysis_data) if isinstance(analysis_data, dict) else 1,
            'save_confirmation': self._generate_save_confirmation(namespace, analysis_data)
        }
    
    def _format_analysis_content(self, analysis_data: Dict[str, Any], namespace: str) -> str:
        """Format analysis data into readable content for pattern storage."""
        import yaml
        from datetime import datetime
        
        content_parts = [
            f"# {namespace.replace('_', ' ').title()} Analysis",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Analysis Results:",
            "",
            "```yaml",
            yaml.dump(analysis_data, default_flow_style=False, indent=2),
            "```"
        ]
        
        return "\n".join(content_parts)
    
    def _generate_save_confirmation(self, namespace: str, analysis_data: Dict[str, Any]) -> str:
        """Generate user-visible confirmation message."""
        items_count = len(analysis_data) if isinstance(analysis_data, dict) else 1
        
        return f"""✅ **Architecture Analysis Saved to Brain**

Namespace: {namespace}
File: CORTEX/cortex-brain/knowledge-graph.yaml
Items Saved: {items_count} components

This analysis will persist across sessions and can be referenced in future conversations."""

    # ---------------------- Phase 3: TDD Workflow Enhancement ----------------------
    
    def store_tdd_cycle_pattern(
        self,
        feature: str,
        test_strategy: str,
        implementation_approach: str,
        refactoring_type: str,
        confidence: float = 0.7
    ) -> str:
        """
        Store a completed TDD cycle as a pattern for future reference.
        
        Part of Phase 3 Deliverable 3.2: Pattern Learning from TDD Cycles
        
        Args:
            feature: Feature name that was implemented
            test_strategy: Testing strategy used (e.g., 'happy_path_first', 'edge_cases_first')
            implementation_approach: Implementation approach (e.g., 'minimal_then_extend')
            refactoring_type: Type of refactoring performed (e.g., 'extract_method')
            confidence: Initial confidence score (default: 0.7)
        
        Returns:
            pattern_id: Unique identifier for the stored pattern
        """
        import uuid
        from datetime import datetime
        
        pattern_id = f"tdd_{feature.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        metadata = {
            'test_strategy': test_strategy,
            'implementation_approach': implementation_approach,
            'refactoring_type': refactoring_type,
            'source': 'tdd_cycle',
            'captured_at': datetime.now().isoformat()
        }
        
        content = f"""# TDD Cycle: {feature}

## Test Strategy
{test_strategy}

## Implementation Approach
{implementation_approach}

## Refactoring Type
{refactoring_type}
"""
        
        result = self.store_pattern(
            pattern_id=pattern_id,
            title=feature,
            content=content,
            pattern_type='tdd_cycle',
            confidence=confidence,
            source='tdd_cycle',
            metadata=metadata,
            scope='application',
            namespaces=['tdd', 'development']
        )
        
        return result.get('pattern_id', pattern_id)
    
    def get_implementation_dependencies(self, feature: str) -> List[Dict[str, Any]]:
        """
        Get implementation dependencies captured during GREEN phase.
        
        Args:
            feature: Feature name to retrieve dependencies for
        
        Returns:
            List of dependency dictionaries
        """
        patterns = self.search_patterns(query=feature, limit=10)
        
        dependencies = []
        for pattern in patterns:
            pattern_type = pattern.get('pattern_type', '')
            if pattern_type in ['implementation', 'tdd_cycle']:
                metadata = pattern.get('metadata', {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                if 'dependencies' in metadata or 'implementation_approach' in metadata:
                    dependencies.append({
                        'pattern_id': pattern.get('pattern_id'),
                        'feature': pattern.get('title'),
                        'description': metadata.get('implementation_approach', ''),
                        'dependencies': metadata.get('dependencies', []),
                        'created_at': pattern.get('created_at')
                    })
        
        return dependencies
    
    def get_implementation_decisions(self, feature: str) -> List[Dict[str, Any]]:
        """
        Get implementation decisions captured during GREEN phase.
        
        Args:
            feature: Feature name to retrieve decisions for
        
        Returns:
            List of decision dictionaries with rationale
        """
        patterns = self.search_patterns(query=feature, limit=10)
        
        decisions = []
        for pattern in patterns:
            pattern_type = pattern.get('pattern_type', '')
            if pattern_type in ['implementation', 'tdd_cycle']:
                metadata = pattern.get('metadata', {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                implementation_approach = metadata.get('implementation_approach', '')
                
                if implementation_approach:
                    decisions.append({
                        'pattern_id': pattern.get('pattern_id'),
                        'feature': pattern.get('title'),
                        'decision': implementation_approach,
                        'rationale': f"Applied {implementation_approach} based on TDD cycle",
                        'test_strategy': metadata.get('test_strategy', 'unknown'),
                        'created_at': pattern.get('created_at')
                    })
        
        return decisions
    
    def suggest_patterns_for_feature(self, feature_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Suggest relevant patterns for a new feature based on semantic similarity.
        
        Part of Phase 3 Deliverable 3.2: Future TDD cycles get pattern suggestions
        
        Args:
            feature_name: New feature being implemented
            limit: Maximum number of suggestions
        
        Returns:
            List of relevant pattern suggestions
        """
        # Search for semantically similar patterns
        patterns = self.search_patterns(query=feature_name, limit=limit * 2)
        
        suggestions = []
        for pattern in patterns:
            if pattern.get('pattern_type') == 'tdd_cycle':
                metadata = pattern.get('metadata', {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                suggestions.append({
                    'pattern_id': pattern.get('pattern_id'),
                    'title': pattern.get('title'),
                    'confidence': pattern.get('confidence', 0.5),
                    'test_strategy': metadata.get('test_strategy', ''),
                    'implementation_approach': metadata.get('implementation_approach', ''),
                    'refactoring_type': metadata.get('refactoring_type', ''),
                    'context': pattern.get('content', '')
                })
        
        # Sort by confidence and return top N
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:limit]
    
    def fts5_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Full-text search using FTS5 for semantic pattern matching.
        
        Part of Phase 3 Deliverable 3.2: Pattern matching uses FTS5
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of matching patterns
        """
        # Use the existing search infrastructure
        return self.search_patterns(query=query, limit=limit)
    
    # ---------------------- Maintenance ----------------------
    def health_check(self) -> Dict[str, Any]:
        return self.connection_manager.health_check()

    def migrate(self, target_version: Optional[int] = None):
        return self.connection_manager.migrate(target_version)

    def close(self):
        self.connection_manager.close()

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


__all__ = ["KnowledgeGraph"]
