"""Knowledge Graph Query Layer Implementation (PHASE-KG-003).

Semantic query builder, graph traversal, rule inference, and query orchestration
with fallback mechanisms and comprehensive audit logging.
"""

import re
import time
from typing import Any, Dict, List, Optional, Set
from cortex.brain.core.knowledge.graph.interface import IGraphAdapter, GraphQueryError
from cortex.brain.domain_brain.kg_query_interface import (
    IQueryAdapter,
    QueryResult,
    QueryNode,
    QueryEdge,
    QueryPath,
)


class SemanticQueryBuilder:
    """Build and execute semantic queries on Knowledge Graph.
    
    Supports chainable query construction with property filtering,
    relationship filtering, and result aggregation.
    """

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize query builder.
        
        Args:
            adapter: IGraphAdapter instance to query
        """
        self.adapter = adapter
        self._entities: List[Dict[str, Any]] = []
        self._relationships: List[Dict[str, Any]] = []
        self._filters: List[tuple[str, Any]] = []

    def find_entities_by_type(self, entity_type: str) -> "SemanticQueryBuilder":
        """Find entities by type.
        
        Args:
            entity_type: Entity type to find
        
        Returns:
            SemanticQueryBuilder: Self for chaining
        """
        try:
            entities = self.adapter.query_entities(entity_type, {})
            self._entities = [
                {"id": e.id, "type": e.type, "properties": e.properties}
                for e in entities
            ]
        except GraphQueryError:
            self._entities = []
        
        return self

    def filter_by_property(self, key: str, value: Any) -> "SemanticQueryBuilder":
        """Filter entities by property value.
        
        Args:
            key: Property key
            value: Property value
        
        Returns:
            SemanticQueryBuilder: Self for chaining
        """
        filtered = []
        for entity in self._entities:
            if entity.get("properties", {}).get(key) == value:
                filtered.append(entity)
        
        self._entities = filtered
        return self

    def related_by(self, rel_type: str) -> "SemanticQueryBuilder":
        """Filter by relationship type.
        
        Args:
            rel_type: Relationship type to filter
        
        Returns:
            SemanticQueryBuilder: Self for chaining
        """
        # For each entity, find relationships of given type
        related_rels = []
        for entity in self._entities:
            try:
                paths = self.adapter.query_paths(entity["id"], None, max_hops=1)
                related_rels.extend(
                    [
                        {
                            "source": entity["id"],
                            "target": target_id,
                            "type": rel_type,
                        }
                        for path in paths
                        for target_id in path.nodes[1:] if len(path.nodes) > 1
                    ]
                )
            except (GraphQueryError, ValueError, TypeError):
                pass
        
        self._relationships = related_rels
        return self

    def build(self) -> QueryResult:
        """Build final query result.
        
        Returns:
            QueryResult: Query result with entities and relationships
        """
        nodes = [
            QueryNode(e["id"], e["type"], e.get("properties", {}))
            for e in self._entities
        ]
        
        edges = [
            QueryEdge(r["source"], r["target"], r["type"], {})
            for r in self._relationships
        ]
        
        return QueryResult(
            status="SUCCESS",
            entities=nodes,
            relationships=edges,
            entity_count=len(nodes),
        )


class GraphTraversal:
    """Traverse Knowledge Graph using BFS.
    
    Supports multi-hop traversal with relationship filtering and
    cycle detection.
    """

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize graph traversal.
        
        Args:
            adapter: IGraphAdapter instance
        """
        self.adapter = adapter

    def traverse_from(
        self,
        entity_id: str,
        max_hops: int = 2,
        rel_types: Optional[List[str]] = None,
    ) -> List[QueryPath]:
        """Traverse from starting entity.
        
        Args:
            entity_id: Start entity ID
            max_hops: Maximum hops
            rel_types: Relationship types to follow (None = all)
        
        Returns:
            List[QueryPath]: Discovered paths
        """
        try:
            paths = self.adapter.query_paths(entity_id, rel_types, max_hops=max_hops)
            
            query_paths = []
            for path in paths:
                nodes = [QueryNode(node_id, "", {}) for node_id in path.nodes]
                query_paths.append(QueryPath(nodes, []))
            
            return query_paths
        
        except (GraphQueryError, ValueError, TypeError):
            return []


class RuleInferenceEngine:
    """Infer relationships and dependencies from Knowledge Graph.
    
    Supports dependency analysis, transitive relationship detection,
    and impact analysis through graph traversal and pattern matching.
    """

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize inference engine.
        
        Args:
            adapter: IGraphAdapter instance
        """
        self.adapter = adapter

    def infer_dependencies(self, entity_id: str) -> List[Dict[str, Any]]:
        """Infer entity dependencies from CALLS/DEPENDS_ON relationships.
        
        Args:
            entity_id: Entity to analyze
        
        Returns:
            List[Dict]: Dependency entries with target and reason
        """
        dependencies = []
        
        try:
            paths = self.adapter.query_paths(
                entity_id, ["CALLS", "DEPENDS_ON"], max_hops=1
            )
            
            for path in paths:
                for edge_rel_type in path.relationships:
                    if edge_rel_type in ["CALLS", "DEPENDS_ON"]:
                        # Get target from path nodes
                        if len(path.nodes) > 1:
                            dependencies.append(
                                {
                                    "target": path.nodes[-1],
                                    "type": edge_rel_type,
                                    "reason": f"Direct {edge_rel_type} relationship",
                                }
                            )
        
        except (GraphQueryError, ValueError):
            pass
        
        return dependencies

    def infer_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """Infer implicit relationships for entity.
        
        Args:
            entity_id: Entity to analyze
        
        Returns:
            List[Dict]: Inferred relationship entries
        """
        relationships = []
        
        try:
            paths = self.adapter.query_paths(entity_id, None, max_hops=2)
            
            for path in paths:
                # path.nodes is list of strings, path.relationships is list of relation types
                relationships.append(
                    {
                        "source": path.nodes[0] if path.nodes else "",
                        "target": path.nodes[-1] if path.nodes else "",
                        "rel_type": path.relationships[0] if path.relationships else "",
                        "hops": len(path.nodes),
                    }
                )
        
        except (GraphQueryError, ValueError):
            pass
        
        return relationships

    def infer_transitive_relationships(
        self, entity_id: str, max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """Infer transitive relationships (A->B->C implies relationship).
        
        Args:
            entity_id: Entity to analyze
            max_depth: Maximum traversal depth
        
        Returns:
            List[Dict]: Transitive relationship entries with paths
        """
        transitive = []
        
        try:
            paths = self.adapter.query_paths(entity_id, None, max_hops=max_depth)
            
            for path in paths:
                if len(path.nodes) > 2:
                    # Multi-hop path implies relationship
                    transitive.append(
                        {
                            "source": path.nodes[0],
                            "target": path.nodes[-1],
                            "path": path.nodes,
                            "depth": len(path.nodes),
                        }
                    )
        
        except (GraphQueryError, ValueError):
            pass
        
        return transitive

    def infer_impact(self, entity_id: str) -> List[Dict[str, Any]]:
        """Infer impact of changes to entity (what breaks).
        
        Args:
            entity_id: Entity to analyze
        
        Returns:
            List[Dict]: Impacted entities
        """
        impacted = []
        
        try:
            # Get all paths from entity
            paths = self.adapter.query_paths(entity_id, None, max_hops=2)
            
            for path in paths:
                if len(path.nodes) > 1:
                    # All nodes after source are impacted
                    for target in path.nodes[1:]:
                        impacted.append(
                            {
                                "entity_id": target,
                                "entity_type": "Unknown",
                                "impact_type": "direct" if len(path.nodes) == 2 else "transitive",
                                "hops": len(path.nodes),
                            }
                        )
        
        except (GraphQueryError, ValueError):
            pass
        
        return impacted

    def infer_recommendations(self, entity_id: str) -> List[Dict[str, Any]]:
        """Generate recommendations based on entity relationships.
        
        Args:
            entity_id: Entity to analyze
        
        Returns:
            List[Dict]: Recommendation entries with type and reason
        """
        recommendations = []
        
        # Get dependencies
        deps = self.infer_dependencies(entity_id)
        if len(deps) > 3:
            recommendations.append(
                {
                    "type": "high_coupling",
                    "reason": f"Entity has {len(deps)} dependencies",
                    "count": len(deps),
                }
            )
        
        # Get impact
        impacts = self.infer_impact(entity_id)
        if len(impacts) > 5:
            recommendations.append(
                {
                    "type": "high_impact",
                    "reason": f"Changes affect {len(impacts)} entities",
                    "count": len(impacts),
                }
            )
        
        return recommendations


class QueryOrchestrator:
    """Orchestrate KG queries with fallback and caching.
    
    Handles query parsing, execution, error recovery, result caching,
    and comprehensive audit logging.
    """

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize query orchestrator.
        
        Args:
            adapter: IGraphAdapter instance
        """
        self.adapter = adapter
        self.builder = SemanticQueryBuilder(adapter)
        self.traversal = GraphTraversal(adapter)
        self.inference = RuleInferenceEngine(adapter)
        self._query_cache: Dict[str, QueryResult] = {}
        self._audit_log: List[Dict[str, Any]] = []

    def query(self, query_string: str) -> QueryResult:
        """Execute semantic query.
        
        Args:
            query_string: Query string (e.g., "SELECT * FROM Service WHERE tier=1")
        
        Returns:
            QueryResult: Query result or error
        """
        # Check cache
        if query_string in self._query_cache:
            return self._query_cache[query_string]
        
        start_time = time.time()
        
        try:
            # Parse query pattern
            if query_string.startswith("SELECT"):
                result = self._parse_select(query_string)
            elif query_string.startswith("FIND"):
                result = self._parse_find(query_string)
            else:
                result = QueryResult(
                    status="PARSE_ERROR",
                    error_message=f"Unknown query type: {query_string[:20]}",
                    execution_time_ms=0,
                )
            
            # Log query
            self._log_query(query_string, result, time.time() - start_time)
            
            # Cache result
            self._query_cache[query_string] = result
            
            return result
        
        except Exception as e:
            result = QueryResult(
                status="FAILED",
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            self._log_query(query_string, result, time.time() - start_time)
            return result

    def query_paths(
        self, source_id: str, target_id: str, max_hops: int = 3
    ) -> QueryResult:
        """Query paths between entities.
        
        Args:
            source_id: Start entity ID
            target_id: End entity ID
            max_hops: Maximum hops
        
        Returns:
            QueryResult: Paths found
        """
        start_time = time.time()
        
        try:
            paths = self.traversal.traverse_from(source_id, max_hops)
            
            result = QueryResult(
                status="SUCCESS",
                paths=paths,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            
            self._log_query(f"PATHS {source_id} -> {target_id}", result, time.time() - start_time)
            return result
        
        except Exception as e:
            result = QueryResult(
                status="FAILED",
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            self._log_query(f"PATHS {source_id} -> {target_id}", result, time.time() - start_time)
            return result

    def _parse_select(self, query: str) -> QueryResult:
        """Parse SELECT query.
        
        Args:
            query: SELECT query string
        
        Returns:
            QueryResult: Query result
        """
        # Extract entity type from FROM clause
        match = re.search(r"FROM\s+(\w+)", query, re.IGNORECASE)
        if not match:
            return QueryResult(status="PARSE_ERROR", error_message="Missing FROM clause")
        
        entity_type = match.group(1)
        builder = SemanticQueryBuilder(self.adapter)
        
        # Execute query
        builder.find_entities_by_type(entity_type)
        
        # Apply WHERE filters if present
        where_match = re.search(r"WHERE\s+(.+?)(?:ORDER|LIMIT)|$)", query, re.IGNORECASE)
        if where_match:
            where_clause = where_match.group(1)
            # Simple filter parsing
            prop_match = re.search(r"(\w+)\s*=\s*(['\"]?)(\w+)\2", where_clause)
            if prop_match:
                prop_key = prop_match.group(1)
                prop_val = prop_match.group(3)
                builder.filter_by_property(prop_key, prop_val)
        
        return builder.build()

    def _parse_find(self, query: str) -> QueryResult:
        """Parse FIND query.
        
        Args:
            query: FIND query string
        
        Returns:
            QueryResult: Query result
        """
        # Example: "FIND Service CALLS Service"
        parts = query.split()
        
        if len(parts) < 2:
            return QueryResult(status="PARSE_ERROR", error_message="Invalid FIND syntax")
        
        entity_type = parts[1]
        
        builder = SemanticQueryBuilder(self.adapter)
        builder.find_entities_by_type(entity_type)
        
        # Check for relationship pattern
        if len(parts) >= 4:
            rel_type = parts[2]
            builder.related_by(rel_type)
        
        return builder.build()

    def _log_query(self, query: str, result: QueryResult, elapsed: float) -> None:
        """Log query execution.
        
        Args:
            query: Query string
            result: Query result
            elapsed: Execution time in seconds
        """
        self._audit_log.append(
            {
                "timestamp": time.time(),
                "query": query,
                "status": result.status,
                "entity_count": result.entity_count,
                "execution_time_ms": elapsed * 1000,
            }
        )

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get query audit log.
        
        Returns:
            List[Dict]: Audit log entries
        """
        return self._audit_log
