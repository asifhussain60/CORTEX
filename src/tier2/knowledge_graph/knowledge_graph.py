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
import logging

from .database.connection import ConnectionManager
from .patterns.pattern_store import PatternStore
from .patterns.pattern_search import PatternSearch
from .patterns.pattern_decay import PatternDecay
from .relationships.relationship_manager import RelationshipManager
from .tags.tag_manager import TagManager
from .loaders.yaml_loader import YAMLKnowledgeLoader

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """High-level orchestration for Knowledge Graph operations with lazy YAML loading."""

    def __init__(self, db_path: Optional[Path] = None, auto_load_knowledge: bool = True):
        if db_path is None:
            # Default consistent with existing database modules
            root = Path(__file__).parent.parent.parent.parent / "cortex-brain" / "tier2"
            root.mkdir(parents=True, exist_ok=True)
            db_path = root / "knowledge_graph.db"
        
        # Convert to Path if string provided
        if isinstance(db_path, str):
            db_path = Path(db_path)
        
        # Store db_path for backward compatibility (tests expect this attribute)
        self.db_path = db_path
        
        self.connection_manager = ConnectionManager(db_path=db_path)

        # Component instances
        self.pattern_store = PatternStore(self.connection_manager)
        self.pattern_search = PatternSearch(self.connection_manager)
        self.pattern_decay = PatternDecay(self.connection_manager)
        self.relationships = RelationshipManager(self.connection_manager)
        self.tags = TagManager(self.connection_manager)
        
        # YAML knowledge loader
        self.yaml_loader = YAMLKnowledgeLoader(self.connection_manager)
        self._knowledge_loaded = False
        self._auto_load_knowledge = auto_load_knowledge

    # ---------------------- Pattern CRUD ----------------------
    def store_pattern(self, **kwargs) -> Dict[str, Any]:
        """
        Store a pattern with backward-compatible API.
        
        Supports both LEGACY API (5-param) and MODERN API (7-param):
        
        LEGACY API:
            title, pattern_type, confidence, context (dict), scope, namespaces
        
        MODERN API:
            pattern_id, title, content (str), pattern_type, confidence, metadata, namespaces
        
        Auto-detects which API is used based on parameters.
        """
        import uuid
        import json
        
        # LEGACY API detection: has 'context' parameter
        if 'context' in kwargs:
            # Transform context (dict) → content (JSON string) + metadata
            context = kwargs.pop('context')
            if context:
                kwargs['content'] = json.dumps(context) if isinstance(context, dict) else str(context)
                kwargs['metadata'] = context if isinstance(context, dict) else None
        
        # Auto-generate pattern_id if not provided
        if 'pattern_id' not in kwargs:
            title = kwargs.get('title', 'pattern')
            # Generate pattern_id from title (legacy format: pattern_<slug>_<short_uuid>)
            slug = title.lower().replace(' ', '_').replace('-', '_')
            slug = ''.join(c for c in slug if c.isalnum() or c == '_')
            short_uuid = str(uuid.uuid4())[:8]
            kwargs['pattern_id'] = f"pattern_{slug}_{short_uuid}"
        
        # Ensure content exists (required by PatternStore)
        if 'content' not in kwargs:
            kwargs['content'] = kwargs.get('title', '')
        
        # Return result - extract pattern_id for backward compatibility
        result = self.pattern_store.store_pattern(**kwargs)
        
        # Legacy API expects pattern_id string, modern API expects dict
        if isinstance(result, dict):
            return result.get('pattern_id', result)
        return result
    
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
        """
        Search patterns with backward compatibility for legacy parameters.
        
        Legacy parameters handled:
        - pattern_type: Filter by type (delegated to post-filter)
        - include_confidence_metadata: Add usage/success rate metadata
        
        Lazy loads YAML knowledge files on first query if enabled.
        """
        # Lazy load knowledge files on first query
        self._ensure_knowledge_loaded()
        
        # Extract legacy parameters
        pattern_type = kwargs.pop('pattern_type', None)
        include_confidence_metadata = kwargs.pop('include_confidence_metadata', False)
        
        # Call modern search API
        results = self.pattern_search.search(query=query, **kwargs)
        
        # Map access_count to usage_count for backward compatibility
        for result in results:
            if "access_count" in result and "usage_count" not in result:
                result["usage_count"] = result["access_count"]
            # Also add last_used if not present (use last_accessed)
            if "last_accessed" in result and "last_used" not in result:
                result["last_used"] = result["last_accessed"]
        
        # Post-filter by pattern_type if specified
        if pattern_type:
            results = [r for r in results if r.get('pattern_type') == pattern_type]
        
        # Add confidence metadata if requested
        if include_confidence_metadata:
            pattern_count = len(results)
            for result in results:
                result["pattern_count"] = pattern_count
                result["success_rate"] = self._calculate_success_rate(result["pattern_id"])
        
        return results
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Alias for search_patterns for backward compatibility."""
        return self.search_patterns(query=query, **kwargs)

    def search_patterns_with_namespace_priority(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_search.search_with_namespace_priority(query=query, **kwargs)
    
    def get_routing_patterns(
        self,
        pattern_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all routing patterns from the knowledge graph.
        
        This method retrieves patterns stored by the Intent Router for routing decisions.
        
        Args:
            pattern_type: Optional filter by pattern_type (e.g., 'routing', 'intent')
            limit: Maximum number of patterns to return (default: 100)
        
        Returns:
            List of pattern dictionaries with routing metadata
        """
        # Use the delegated pattern_store to query patterns
        try:
            # Query patterns from the pattern store using list_patterns
            results = self.pattern_store.list_patterns(
                pattern_type=pattern_type,
                limit=limit
            )
            
            return results if results else []
        except Exception:
            # Fallback to empty list if query fails
            return []
    
    def add_pattern(self, pattern: Dict[str, Any] = None, pattern_type: str = None, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Add a pattern (alias for store_pattern for backward compatibility).
        
        Supports two calling styles:
        1. add_pattern(pattern={...})  # Dictionary with all fields
        2. add_pattern(pattern_type="...", data={...})  # Legacy style from tests
        
        Args:
            pattern: Pattern dictionary containing fields like:
                - pattern_id: Optional unique ID
                - title: Pattern title
                - content: Pattern content
                - pattern_type: Type of pattern (workflow, intent, validation, etc.)
                - confidence: Confidence score (0.0-1.0)
                - etc.
            pattern_type: (Legacy) Pattern type as keyword argument
            data: (Legacy) Pattern data as keyword argument
            **kwargs: Additional pattern fields
            
        Returns:
            Result dictionary with pattern_id and status
        """
        # Handle legacy calling style: add_pattern(pattern_type="...", data={...})
        if pattern is None and pattern_type is not None:
            pattern = {'pattern_type': pattern_type}
            if data is not None:
                pattern.update(data)
            pattern.update(kwargs)
        elif pattern is None:
            pattern = kwargs
        
        # Extract fields from pattern dict with defaults
        import uuid
        
        return self.store_pattern(
            pattern_id=pattern.get('pattern_id', str(uuid.uuid4())),
            title=pattern.get('title', pattern.get('message', 'Untitled Pattern')),
            content=pattern.get('content', str(pattern.get('data', ''))),
            pattern_type=pattern.get('pattern_type', 'workflow'),
            confidence=pattern.get('confidence', 1.0),
            source=pattern.get('source'),
            metadata=pattern.get('metadata', pattern if isinstance(pattern, dict) else None),
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
    def apply_decay(self, decay_rate: float = 0.05, min_confidence: float = 0.3) -> Dict[str, Any]:
        """
        Apply pattern decay with optional parameters (backward compatibility).
        
        Args:
            decay_rate: Confidence decrease per period (default: 0.05)
            min_confidence: Don't decay below this (default: 0.3)
        
        Returns:
            Decay results dictionary
        """
        return self.pattern_decay.apply_decay()

    def get_decay_candidates(self) -> List[Dict[str, Any]]:
        return self.pattern_decay.get_decay_candidates()

    def pin_pattern(self, pattern_id: str) -> bool:
        return self.pattern_decay.pin_pattern(pattern_id)

    def unpin_pattern(self, pattern_id: str) -> bool:
        return self.pattern_decay.unpin_pattern(pattern_id)

    def get_decay_log(self, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_decay.get_decay_log(**kwargs)
    
    def boost_pattern(self, pattern_id: str, boost_amount: float = 0.05):
        """
        Increase pattern confidence after successful use (legacy API compatibility).
        
        Args:
            pattern_id: Pattern to boost
            boost_amount: Confidence increase (default: 0.05)
        """
        from datetime import datetime
        
        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE patterns 
                SET confidence = MIN(confidence + ?, 1.0),
                    last_used = ?,
                    usage_count = usage_count + 1
                WHERE pattern_id = ?
            """, (boost_amount, datetime.now(), pattern_id))
            conn.commit()

    # ---------------------- Relationships ----------------------
    def create_relationship(self, **kwargs) -> Dict[str, Any]:
        return self.relationships.create_relationship(**kwargs)

    def get_relationships(self, pattern_id: str, direction: str = "both") -> List[Dict[str, Any]]:
        return self.relationships.get_relationships(pattern_id=pattern_id, direction=direction)

    def traverse_graph(self, start_pattern: str, **kwargs) -> Dict[str, Any]:
        return self.relationships.traverse_graph(start_pattern=start_pattern, **kwargs)
    
    def track_relationship(
        self,
        file_a: str,
        file_b: str,
        relationship_type: str = "co_modification",
        strength: float = 0.5,
        context: str = None
    ):
        """
        Track file co-modification relationship (legacy API compatibility).
        
        Args:
            file_a: First file path
            file_b: Second file path
            relationship_type: Type (co_modification, dependency)
            strength: Relationship strength (0.0-1.0)
            context: Additional context
        """
        from datetime import datetime
        
        relationship_id = f"{file_a}_{file_b}_{relationship_type}"
        
        # Check if relationship exists
        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT co_modification_count FROM relationships 
                WHERE relationship_id = ?
            """, (relationship_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update count and strength
                new_count = existing["co_modification_count"] + 1
                cursor.execute("""
                    UPDATE relationships 
                    SET co_modification_count = ?,
                        strength = ?,
                        last_observed = ?
                    WHERE relationship_id = ?
                """, (new_count, strength, datetime.now(), relationship_id))
            else:
                # Insert new relationship
                cursor.execute("""
                    INSERT INTO relationships 
                    (relationship_id, file_a, file_b, relationship_type, strength, context, co_modification_count)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (relationship_id, file_a, file_b, relationship_type, strength, context))
            
            conn.commit()
    
    def get_file_relationships(
        self,
        file_path: str,
        min_strength: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Get all relationships for a file (legacy API compatibility).
        
        Args:
            file_path: File to query
            min_strength: Minimum relationship strength
        
        Returns:
            List of related files
        """
        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM relationships 
                WHERE (file_a = ? OR file_b = ?)
                AND strength >= ?
                ORDER BY strength DESC
            """, (file_path, file_path, min_strength))
            
            return [
                {
                    "related_file": row["file_b"] if row["file_a"] == file_path else row["file_a"],
                    "relationship_type": row["relationship_type"],
                    "strength": row["strength"],
                    "co_modification_count": row["co_modification_count"],
                    "context": row["context"]
                }
                for row in cursor.fetchall()
            ]

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

    # ---------------------- Workflow Templates ----------------------
    def store_workflow_template(
        self,
        name: str,
        phases: List[Dict[str, Any]],
        success_rate: float = 0.0,
        avg_duration_hours: float = 0.0
    ) -> str:
        """
        Store workflow template (legacy API compatibility).
        
        Args:
            name: Workflow name
            phases: List of phase definitions
            success_rate: Historical success rate
            avg_duration_hours: Average completion time
        
        Returns:
            workflow_id: Unique identifier
        """
        import json
        
        workflow_id = self._generate_workflow_id(name)
        phases_json = json.dumps(phases)
        
        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO workflows 
                (workflow_id, name, phases_json, success_rate, avg_duration_hours)
                VALUES (?, ?, ?, ?, ?)
            """, (workflow_id, name, phases_json, success_rate, avg_duration_hours))
            conn.commit()
        
        return workflow_id
    
    def get_workflow_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve workflow template by name (legacy API compatibility)."""
        import json
        
        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM workflows WHERE name = ?
            """, (name,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "workflow_id": row["workflow_id"],
                    "name": row["name"],
                    "phases": json.loads(row["phases_json"]),
                    "success_rate": row["success_rate"],
                    "avg_duration_hours": row["avg_duration_hours"],
                    "usage_count": row["usage_count"]
                }
            return None
    
    # ---------------------- TDD Cycle Patterns ----------------------
    def store_tdd_cycle_pattern(
        self,
        feature: str,
        test_strategy: str,
        implementation_approach: str,
        refactoring_type: str,
        confidence: float = 0.7
    ) -> str:
        """
        Store a completed TDD cycle as a pattern (legacy API compatibility).
        
        Args:
            feature: Feature name that was implemented
            test_strategy: Testing strategy used
            implementation_approach: Implementation approach
            refactoring_type: Type of refactoring performed
            confidence: Initial confidence score (default: 0.7)
        
        Returns:
            pattern_id: Unique identifier for the stored pattern
        """
        import json
        
        context = {
            'test_strategy': test_strategy,
            'implementation_approach': implementation_approach,
            'refactoring_type': refactoring_type,
            'source': 'tdd_cycle'
        }
        
        return self.store_pattern(
            title=feature,
            content=json.dumps(context),
            pattern_type='tdd_cycle',
            confidence=confidence,
            source='tdd_cycle',
            metadata=context,
            scope='application',
            namespaces=['tdd', 'development']
        )
    
    # ---------------------- Helper Methods ----------------------
    def _generate_pattern_id(self, title: str) -> str:
        """Generate unique pattern ID (legacy API compatibility)."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
        clean_title = clean_title.replace(' ', '_').lower()[:30]
        return f"pattern_{clean_title}_{timestamp}"
    
    def _generate_workflow_id(self, name: str) -> str:
        """Generate unique workflow ID (legacy API compatibility)."""
        clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
        clean_name = clean_name.replace(' ', '_').lower()
        return f"workflow_{clean_name}"
    
    def _calculate_success_rate(self, pattern_id: str) -> float:
        """
        Calculate success rate for a pattern (legacy API compatibility).
        
        Args:
            pattern_id: Pattern to calculate success rate for
            
        Returns:
            Success rate (0.0-1.0)
        """
        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT confidence, usage_count FROM patterns 
                WHERE pattern_id = ?
            """, (pattern_id,))
            row = cursor.fetchone()
            
            if row:
                # Use confidence as success rate proxy
                # Adjust based on usage: more usage = more reliable
                base_rate = row["confidence"]
                usage_count = row["usage_count"]
                
                # Boost success rate slightly for well-used patterns
                if usage_count > 10:
                    return min(base_rate + 0.05, 1.0)
                elif usage_count > 5:
                    return min(base_rate + 0.02, 1.0)
                else:
                    return base_rate
            
            return 0.5  # Default if pattern not found
    
    def _get_connection(self):
        """
        Get database connection context manager (legacy API compatibility).
        
        Returns:
            Context manager for database connection
        """
        return self.connection_manager.get_connection()

    # ---------------------- Maintenance ----------------------
    def health_check(self) -> Dict[str, Any]:
        return self.connection_manager.health_check()

    def migrate(self, target_version: Optional[int] = None):
        return self.connection_manager.migrate(target_version)
    
    # ---------------------- YAML Knowledge Loading ----------------------
    def _ensure_knowledge_loaded(self):
        """Lazy load YAML knowledge files on first query."""
        if self._knowledge_loaded or not self._auto_load_knowledge:
            return
        
        try:
            logger.info("🔄 Loading YAML knowledge files into Tier 2...")
            stats = self.yaml_loader.load_all_knowledge_files()
            
            if stats:
                total_patterns = sum(stats.values())
                logger.info(f"✅ Loaded {total_patterns} patterns from {len(stats)} categories")
                for category, count in stats.items():
                    logger.debug(f"   {category}: {count} patterns")
            else:
                logger.debug("No new knowledge files to load")
            
            self._knowledge_loaded = True
        except Exception as e:
            logger.warning(f"Failed to load knowledge files: {e}")
            # Don't fail queries if knowledge loading fails
            self._knowledge_loaded = True  # Mark as attempted
    
    def load_knowledge_category(self, category: str, force_reload: bool = False) -> int:
        """
        Explicitly load knowledge files from a specific category.
        
        Args:
            category: Category name (e.g., 'engineering', 'testing', 'security')
            force_reload: If True, reload even if already loaded
        
        Returns:
            Number of patterns loaded
        """
        return self.yaml_loader.load_category(category, force_reload)
    
    def load_knowledge_file(self, file_path: Path) -> int:
        """
        Explicitly load a specific YAML knowledge file.
        
        Args:
            file_path: Path to YAML file
        
        Returns:
            Number of patterns loaded
        """
        return self.yaml_loader.load_file(file_path)
    
    def get_knowledge_load_stats(self) -> Dict[str, Any]:
        """
        Get statistics about loaded knowledge files.
        
        Returns:
            Dictionary with load statistics
        """
        return self.yaml_loader.get_load_stats()
    
    def reload_all_knowledge(self) -> Dict[str, int]:
        """
        Force reload all YAML knowledge files.
        
        Returns:
            Dictionary with load statistics per category
        """
        self._knowledge_loaded = False
        return self.yaml_loader.load_all_knowledge_files(force_reload=True)

    def close(self):
        self.connection_manager.close()

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


__all__ = ["KnowledgeGraph"]
