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
        
        # Validate namespace is provided
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
        """
        import fnmatch
        
        # Get all patterns (TODO: optimize with DB-level filtering)
        all_patterns = self.pattern_store.list_patterns(**kwargs)
        
        # Filter by namespace
        if namespace_filter == "*":
            return all_patterns
        
        # Use _namespace field for filtering (primary namespace)
        return [p for p in all_patterns if fnmatch.fnmatch(p.get("_namespace", ""), namespace_filter)]

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

    def search_patterns_with_namespace_priority(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_search.search_with_namespace_priority(query=query, **kwargs)

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
        
        # Check analysis type based on request and context
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
            
            # Check for architectural analysis
            if any(pattern in request_lower for pattern in architecture_patterns):
                return f'{workspace_name}_architecture'
            
            # Check for feature-specific analysis
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
                    
            # Check file patterns for architectural indicators
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
        
        # Create pattern content from analysis data
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
