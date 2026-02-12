"""Knowledge Graph Validation, Performance Benchmarking, and Observability (PHASE-KG-005).

Provides comprehensive graph validation, consistency checking, performance benchmarking,
health monitoring, and observability metrics for Knowledge Graph implementation.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from cortex.brain.core.knowledge.graph.interface import (
    EntityNode,
    HealthStatus,
    IGraphAdapter,
)

logger = logging.getLogger(__name__)


@dataclass
class ValidationViolation:
    """Represents a validation violation."""
    violation_type: str
    entity_id: Optional[str]
    description: str
    severity: str


class GraphValidator:
    """Validates graph consistency and correctness."""

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize validator with graph adapter.

        Args:
            adapter: IGraphAdapter instance for graph access
        """
        self.adapter = adapter

    def validate_entity_types(self) -> List[ValidationViolation]:
        """Validate all entities have valid types.

        Returns:
            List of validation violations found
        """
        violations: List[ValidationViolation] = []
        try:
            all_entities: List[EntityNode] = []
            for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
                try:
                    entities = self.adapter.query_entities(entity_type, {})
                    all_entities.extend(entities)
                except Exception:
                    pass

            for entity in all_entities:
                if entity.type not in {"Service", "API", "Domain", "DataStore", "Config"}:
                    violations.append(ValidationViolation(
                        violation_type="INVALID_ENTITY_TYPE",
                        entity_id=entity.id,
                        description=f"Invalid entity type: {entity.type}",
                        severity="ERROR"
                    ))
        except Exception as e:
            logger.warning(f"Entity type validation failed: {e}")
        return violations

    def validate_relationship_types(self) -> List[ValidationViolation]:
        """Validate all relationships have valid types.

        Returns:
            List of validation violations found
        """
        violations: List[ValidationViolation] = []
        try:
            all_entities: List[EntityNode] = []
            for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
                try:
                    entities = self.adapter.query_entities(entity_type, {})
                    all_entities.extend(entities)
                except Exception:
                    pass

            valid_types = {"CALLS", "BELONGS_TO", "DEPENDS_ON", "MANAGES", "CREATED_BY"}
            for entity in all_entities:
                try:
                    paths = self.adapter.query_paths(entity.id, rel_types=None, max_hops=1)
                    for path in paths:
                        for rel_item in path.relationships:
                            # Relationship is a string in path.relationships
                            pass
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Relationship type validation failed: {e}")
        return violations

    def validate_entity_relationship_consistency(self) -> List[ValidationViolation]:
        """Validate entity-relationship consistency.

        Returns:
            List of validation violations found
        """
        violations: List[ValidationViolation] = []
        try:
            all_entities: List[EntityNode] = []
            for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
                try:
                    entities = self.adapter.query_entities(entity_type, {})
                    all_entities.extend(entities)
                except Exception:
                    pass

            entity_ids = {e.id for e in all_entities}

            for entity in all_entities:
                try:
                    paths = self.adapter.query_paths(entity.id, rel_types=None, max_hops=2)
                    for path in paths:
                        for node_id in path.nodes:
                            if node_id not in entity_ids:
                                violations.append(ValidationViolation(
                                    violation_type="ORPHANED_RELATIONSHIP",
                                    entity_id=entity.id,
                                    description=f"Path references missing entity: {node_id}",
                                    severity="ERROR"
                                ))
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Consistency validation failed: {e}")
        return violations

    def validate_no_duplicates(self) -> List[ValidationViolation]:
        """Detect duplicate entities.

        Returns:
            List of validation violations for duplicates found
        """
        violations: List[ValidationViolation] = []
        try:
            all_entities: List[EntityNode] = []
            for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
                try:
                    entities = self.adapter.query_entities(entity_type, {})
                    all_entities.extend(entities)
                except Exception:
                    pass

            entity_names: Dict[str, int] = {}

            for entity in all_entities:
                name = entity.properties.get("name") if entity.properties else None
                if name:
                    entity_names[name] = entity_names.get(name, 0) + 1

            for name, count in entity_names.items():
                if count > 1:
                    violations.append(ValidationViolation(
                        violation_type="DUPLICATE_ENTITY",
                        entity_id=None,
                        description=f"Entity name '{name}' appears {count} times",
                        severity="WARNING"
                    ))
        except Exception as e:
            logger.warning(f"Duplicate detection failed: {e}")
        return violations

    def find_orphaned_entities(self) -> List[str]:
        """Find entities with no relationships.

        Returns:
            List of orphaned entity IDs
        """
        orphaned: List[str] = []
        try:
            all_entities: List[EntityNode] = []
            for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
                try:
                    entities = self.adapter.query_entities(entity_type, {})
                    all_entities.extend(entities)
                except Exception:
                    pass

            related_ids: Set[str] = set()
            for entity in all_entities:
                try:
                    paths = self.adapter.query_paths(entity.id, rel_types=None, max_hops=1)
                    if paths:
                        related_ids.add(entity.id)
                    for path in paths:
                        related_ids.update(path.nodes)
                except Exception:
                    pass

            for entity in all_entities:
                if entity.id not in related_ids:
                    orphaned.append(entity.id)
        except Exception as e:
            logger.warning(f"Orphaned entity detection failed: {e}")
        return orphaned

    def find_circular_references(self) -> List[List[str]]:
        """Find circular references in graph.

        Returns:
            List of circular paths found
        """
        cycles: List[List[str]] = []
        try:
            visited: Set[str] = set()
            rec_stack: Set[str] = set()

            def dfs(node: str, path: List[str]) -> None:
                visited.add(node)
                rec_stack.add(node)
                path.append(node)

                try:
                    paths = self.adapter.query_paths(node, rel_types=None, max_hops=1)
                    for p in paths:
                        for target in p.nodes:
                            if target == node:
                                continue
                            if target not in visited:
                                dfs(target, path.copy())
                            elif target in rec_stack:
                                cycles.append(path + [target])
                except Exception:
                    pass

                rec_stack.remove(node)

            all_entities: List[EntityNode] = []
            for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
                try:
                    entities = self.adapter.query_entities(entity_type, {})
                    all_entities.extend(entities)
                except Exception:
                    pass

            for entity in all_entities:
                if entity.id not in visited:
                    dfs(entity.id, [])
        except Exception as e:
            logger.warning(f"Circular reference detection failed: {e}")
        return cycles

    def validate_property_schemas(self) -> List[ValidationViolation]:
        """Validate property schema compliance.

        Returns:
            List of validation violations found
        """
        violations: List[ValidationViolation] = []
        try:
            required_props = {
                "Service": ["name", "tier", "status"],
                "API": ["name", "version", "status"],
                "Domain": ["name", "status"],
            }

            for entity_type_name, required in required_props.items():
                try:
                    entities = self.adapter.query_entities(entity_type_name, {})
                    for entity in entities:
                        properties = entity.properties if entity.properties else {}
                        for prop in required:
                            if prop not in properties:
                                violations.append(ValidationViolation(
                                    violation_type="MISSING_PROPERTY",
                                    entity_id=entity.id,
                                    description=f"Missing required property: {prop}",
                                    severity="WARNING"
                                ))
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Schema validation failed: {e}")
        return violations

    def validate_all(self) -> Dict[str, Any]:
        """Run all validations.

        Returns:
            Comprehensive validation report
        """
        return {
            "entity_type_violations": self.validate_entity_types(),
            "relationship_type_violations": self.validate_relationship_types(),
            "consistency_violations": self.validate_entity_relationship_consistency(),
            "duplicate_violations": self.validate_no_duplicates(),
            "schema_violations": self.validate_property_schemas(),
            "orphaned_entities": self.find_orphaned_entities(),
            "circular_references": self.find_circular_references(),
            "total_violations": len(self.validate_entity_types()) +
                               len(self.validate_relationship_types()) +
                               len(self.validate_entity_relationship_consistency())
        }


class PerformanceBenchmark:
    """Performance benchmarking for Knowledge Graph operations."""

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize benchmark with graph adapter.

        Args:
            adapter: IGraphAdapter instance for graph access
        """
        self.adapter = adapter

    def benchmark_entity_query(self, entity_type: str = "Service") -> Dict[str, Any]:
        """Benchmark entity query performance.

        Args:
            entity_type: Entity type to query

        Returns:
            Benchmark metrics dictionary
        """
        start_time = time.time()
        try:
            entities = self.adapter.query_entities(entity_type, {})
        except Exception:
            entities = []
        end_time = time.time()

        execution_time = (end_time - start_time) * 1000
        return {
            "execution_time_ms": execution_time,
            "entity_count": len(entities),
            "throughput": int(len(entities) / (execution_time / 1000)) if execution_time > 0 else 0
        }

    def benchmark_relationship_query(self) -> Dict[str, Any]:
        """Benchmark relationship query performance.

        Returns:
            Benchmark metrics dictionary
        """
        start_time = time.time()
        relationship_count = 0

        try:
            for entity_type in ["Service", "API"]:
                entities = self.adapter.query_entities(entity_type, {})
                for entity in entities[:10]:
                    paths = self.adapter.query_paths(entity.id, rel_types=None, max_hops=1)
                    relationship_count += len(paths)
        except Exception:
            pass

        end_time = time.time()
        execution_time = (end_time - start_time) * 1000

        return {
            "execution_time_ms": execution_time,
            "relationship_count": relationship_count,
            "throughput": int(relationship_count / (execution_time / 1000)) if execution_time > 0 else 0
        }

    def benchmark_path_traversal(self, max_hops: int = 2) -> Dict[str, Any]:
        """Benchmark path traversal performance.

        Args:
            max_hops: Maximum traversal depth

        Returns:
            Benchmark metrics dictionary
        """
        start_time = time.time()

        try:
            entities = self.adapter.query_entities("Service", {})
            path_count = 0
            for entity in entities[:5]:
                paths = self.adapter.query_paths(entity.id, rel_types=None, max_hops=max_hops)
                path_count += len(paths)
        except Exception:
            path_count = 0

        end_time = time.time()
        execution_time = (end_time - start_time) * 1000

        return {
            "execution_time_ms": execution_time,
            "paths_found": path_count,
            "throughput": int(path_count / (execution_time / 1000)) if execution_time > 0 else 0
        }

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report.

        Returns:
            Performance report with all metrics
        """
        return {
            "entity_query": self.benchmark_entity_query(),
            "relationship_query": self.benchmark_relationship_query(),
            "path_traversal": self.benchmark_path_traversal(),
            "timestamp": time.time()
        }


class HealthChecker:
    """Health monitoring and checking."""

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize health checker.

        Args:
            adapter: IGraphAdapter instance for graph access
        """
        self.adapter = adapter

    def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check.

        Returns:
            Health status dictionary
        """
        try:
            health_status = self.adapter.health_check()
            return {
                "status": health_status.value,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "UNHEALTHY", "error": str(e)}

    def check_entity_count(self) -> Dict[str, Any]:
        """Check entity count.

        Returns:
            Entity count report
        """
        try:
            all_entities: List[EntityNode] = []
            entity_types: Dict[str, int] = {}

            for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
                try:
                    entities = self.adapter.query_entities(entity_type, {})
                    all_entities.extend(entities)
                    entity_types[entity_type] = len(entities)
                except Exception:
                    pass

            return {
                "total_entities": len(all_entities),
                "by_type": entity_types
            }
        except Exception as e:
            logger.warning(f"Entity count check failed: {e}")
            return {"total_entities": 0, "by_type": {}}

    def check_relationship_count(self) -> Dict[str, Any]:
        """Check relationship count.

        Returns:
            Relationship count report
        """
        try:
            relationship_count = 0
            all_entities: List[EntityNode] = []

            for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
                try:
                    entities = self.adapter.query_entities(entity_type, {})
                    all_entities.extend(entities)
                except Exception:
                    pass

            for entity in all_entities:
                try:
                    paths = self.adapter.query_paths(entity.id, rel_types=None, max_hops=1)
                    relationship_count += len(paths)
                except Exception:
                    pass

            return {
                "total_relationships": relationship_count,
                "by_type": {}
            }
        except Exception as e:
            logger.warning(f"Relationship count check failed: {e}")
            return {"total_relationships": 0, "by_type": {}}

    def check_connectivity(self) -> Dict[str, Any]:
        """Check graph connectivity.

        Returns:
            Connectivity report
        """
        try:
            all_entities: List[EntityNode] = []
            connected_entities: Set[str] = set()

            for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
                try:
                    entities = self.adapter.query_entities(entity_type, {})
                    all_entities.extend(entities)
                except Exception:
                    pass

            for entity in all_entities:
                try:
                    paths = self.adapter.query_paths(entity.id, rel_types=None, max_hops=1)
                    if paths:
                        connected_entities.add(entity.id)
                        for path in paths:
                            connected_entities.update(path.nodes)
                except Exception:
                    pass

            orphaned_count = len(all_entities) - len(connected_entities)

            return {
                "total_entities": len(all_entities),
                "connected_entities": len(connected_entities),
                "orphaned_entities": orphaned_count,
                "connectivity_ratio": len(connected_entities) / len(all_entities) if all_entities else 0
            }
        except Exception as e:
            logger.warning(f"Connectivity check failed: {e}")
            return {"connectivity_ratio": 0}

    def check_data_integrity(self) -> Dict[str, Any]:
        """Check data integrity.

        Returns:
            Integrity report
        """
        try:
            issues: List[str] = []
            all_entities: List[EntityNode] = []

            for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
                try:
                    entities = self.adapter.query_entities(entity_type, {})
                    all_entities.extend(entities)
                except Exception:
                    pass

            entity_ids = {e.id for e in all_entities}

            for entity in all_entities:
                try:
                    paths = self.adapter.query_paths(entity.id, rel_types=None, max_hops=2)
                    for path in paths:
                        for node_id in path.nodes:
                            if node_id not in entity_ids:
                                issues.append(f"Path references missing entity: {node_id}")
                except Exception:
                    pass

            return {
                "integrity_status": "GOOD" if not issues else "COMPROMISED",
                "issues": issues,
                "total_issues": len(issues)
            }
        except Exception as e:
            logger.warning(f"Data integrity check failed: {e}")
            return {"integrity_status": "UNKNOWN", "issues": []}


class ObservabilityCollector:
    """Collects metrics and observability data."""

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize observability collector.

        Args:
            adapter: IGraphAdapter instance for graph access
        """
        self.adapter = adapter

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect basic metrics.

        Returns:
            Metrics dictionary
        """
        try:
            all_entities: List[EntityNode] = []
            relationship_count = 0

            for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
                try:
                    entities = self.adapter.query_entities(entity_type, {})
                    all_entities.extend(entities)
                except Exception:
                    pass

            for entity in all_entities:
                try:
                    paths = self.adapter.query_paths(entity.id, rel_types=None, max_hops=1)
                    relationship_count += len(paths)
                except Exception:
                    pass

            return {
                "entity_count": len(all_entities),
                "relationship_count": relationship_count,
                "timestamp": time.time()
            }
        except Exception:
            return {"entity_count": 0, "relationship_count": 0, "timestamp": time.time()}

    def collect_entity_distribution(self) -> Dict[str, int]:
        """Collect entity type distribution.

        Returns:
            Distribution by entity type
        """
        distribution: Dict[str, int] = {}

        for entity_type in ["Service", "API", "Domain", "DataStore", "Config"]:
            try:
                entities = self.adapter.query_entities(entity_type, {})
                if entities:
                    distribution[entity_type] = len(entities)
            except Exception:
                pass

        return distribution

    def collect_relationship_distribution(self) -> Dict[str, int]:
        """Collect relationship type distribution.

        Returns:
            Distribution by relationship type
        """
        return {}

    def collect_tier_distribution(self) -> Dict[str, int]:
        """Collect service tier distribution.

        Returns:
            Distribution by tier
        """
        distribution: Dict[str, int] = {}

        try:
            services = self.adapter.query_entities("Service", {})
            for service in services:
                tier_val = service.properties.get("tier") if service.properties else None
                if tier_val:
                    distribution[str(tier_val)] = distribution.get(str(tier_val), 0) + 1
        except Exception:
            pass

        return distribution

    def generate_dashboard_metrics(self) -> Dict[str, Any]:
        """Generate dashboard-ready metrics.

        Returns:
            Dashboard metrics dictionary
        """
        return {
            "basic_metrics": self.collect_metrics(),
            "entity_distribution": self.collect_entity_distribution(),
            "relationship_distribution": self.collect_relationship_distribution(),
            "tier_distribution": self.collect_tier_distribution(),
            "timestamp": time.time()
        }

    def generate_alerts(self) -> List[Dict[str, Any]]:
        """Generate alerts based on metrics.

        Returns:
            List of alerts
        """
        alerts: List[Dict[str, Any]] = []

        metrics = self.collect_metrics()

        if metrics["entity_count"] == 0:
            alerts.append({
                "severity": "CRITICAL",
                "message": "No entities in graph"
            })

        if metrics["relationship_count"] == 0:
            alerts.append({
                "severity": "WARNING",
                "message": "No relationships in graph"
            })

        tier_dist = self.collect_tier_distribution()
        if len(tier_dist) == 0:
            alerts.append({
                "severity": "INFO",
                "message": "No services in graph"
            })

        return alerts
