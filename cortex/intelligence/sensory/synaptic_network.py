"""Synaptic Network - Graph storage and querying layer.

Phase 11 - CMS-2: Dependency Synaptic Network + Compliance Graphs

Three graph networks:
1. Dependency Synaptic Network - Package dependencies
2. Compliance Synaptic Network - Compliance mappings
3. Service Topology Network - Service API contracts
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generator, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class SynapticNetworkType(Enum):
    """Types of synaptic networks."""
    DEPENDENCY = "dependency"
    COMPLIANCE = "compliance"
    SERVICE_TOPOLOGY = "service_topology"


class RelationshipType(Enum):
    """Types of relationships between nodes."""
    # Dependency relationships
    DEPENDS_ON = "depends_on"
    DEPENDS_ON_TRANSITIVELY = "depends_on_transitively"
    HAS_VULNERABILITY = "has_vulnerability"
    INCOMPATIBLE_WITH = "incompatible_with"

    # Compliance relationships
    VIOLATES = "violates"
    REQUIRES = "requires"
    COMPLIES_WITH = "complies_with"

    # Service topology relationships
    CALLS = "calls"
    PROVIDES = "provides"
    EXPOSES = "exposes"
    IMPLEMENTS = "implements"


@dataclass
class SynapticNode:
    """Graph node in synaptic network.

    Attributes:
        node_id: Unique identifier
        node_type: Type (package, version, vulnerability, compliance_rule, service, etc.)
        label: Human-readable label
        properties: Node properties
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    node_id: str
    node_type: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get property value.

        Args:
            key: Property key
            default: Default value if not found

        Returns:
            Property value or default
        """
        return self.properties.get(key, default)

    def set_property(self, key: str, value: Any) -> None:
        """Set property value.

        Args:
            key: Property key
            value: Property value
        """
        self.properties[key] = value
        self.updated_at = datetime.utcnow().isoformat()


@dataclass
class SynapticConnection:
    """Connection between nodes in synaptic network.

    Attributes:
        connection_id: Unique identifier
        source_node_id: Source node
        target_node_id: Target node
        relationship_type: Type of relationship
        properties: Connection properties
        created_at: Creation timestamp
    """
    connection_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: RelationshipType
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get property value.

        Args:
            key: Property key
            default: Default value if not found

        Returns:
            Property value or default
        """
        return self.properties.get(key, default)


class SynapticNetworkInterface(ABC):
    """Abstract interface for synaptic network storage."""

    @abstractmethod
    def add_node(self, node: SynapticNode) -> bool:
        """Add node to network.

        Args:
            node: Node to add

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[SynapticNode]:
        """Get node by ID.

        Args:
            node_id: Node ID

        Returns:
            Node or None if not found
        """
        pass

    @abstractmethod
    def add_connection(self, connection: SynapticConnection) -> bool:
        """Add connection between nodes.

        Args:
            connection: Connection to add

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def get_connections(
        self,
        source_node_id: str,
        relationship_type: Optional[RelationshipType] = None
    ) -> List[SynapticConnection]:
        """Get outgoing connections from node.

        Args:
            source_node_id: Source node ID
            relationship_type: Optional filter by relationship type

        Returns:
            List of connections
        """
        pass

    @abstractmethod
    def find_paths(
        self,
        start_node_id: str,
        end_node_id: str,
        max_depth: int = 5
    ) -> List[List[str]]:
        """Find all paths between nodes.

        Args:
            start_node_id: Starting node ID
            end_node_id: Ending node ID
            max_depth: Maximum path depth

        Returns:
            List of node ID paths
        """
        pass

    @abstractmethod
    def get_node_count(self) -> int:
        """Get total node count.

        Returns:
            Number of nodes
        """
        pass

    @abstractmethod
    def get_connection_count(self) -> int:
        """Get total connection count.

        Returns:
            Number of connections
        """
        pass


class InMemorySynapticNetwork(SynapticNetworkInterface):
    """In-memory implementation of synaptic network.

    Used for testing and development. Production should use Neo4j.
    """

    def __init__(self):
        """Initialize in-memory network."""
        self.nodes: Dict[str, SynapticNode] = {}
        self.connections: Dict[str, List[SynapticConnection]] = {}
        self.reverse_connections: Dict[str, List[SynapticConnection]] = {}

    def add_node(self, node: SynapticNode) -> bool:
        """Add node to network."""
        if node.node_id in self.nodes:
            logger.warning(f"Node already exists: {node.node_id}")
            return False

        self.nodes[node.node_id] = node
        if node.node_id not in self.connections:
            self.connections[node.node_id] = []
        if node.node_id not in self.reverse_connections:
            self.reverse_connections[node.node_id] = []

        return True

    def get_node(self, node_id: str) -> Optional[SynapticNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def add_connection(self, connection: SynapticConnection) -> bool:
        """Add connection between nodes."""
        # Verify nodes exist
        if connection.source_node_id not in self.nodes:
            logger.warning(f"Source node not found: {connection.source_node_id}")
            return False
        if connection.target_node_id not in self.nodes:
            logger.warning(f"Target node not found: {connection.target_node_id}")
            return False

        # Add to forward and reverse indices
        self.connections[connection.source_node_id].append(connection)
        self.reverse_connections[connection.target_node_id].append(connection)

        return True

    def get_connections(
        self,
        source_node_id: str,
        relationship_type: Optional[RelationshipType] = None
    ) -> List[SynapticConnection]:
        """Get outgoing connections from node."""
        connections = self.connections.get(source_node_id, [])

        if relationship_type:
            return [c for c in connections if c.relationship_type == relationship_type]

        return connections

    def find_paths(
        self,
        start_node_id: str,
        end_node_id: str,
        max_depth: int = 5
    ) -> List[List[str]]:
        """Find all paths between nodes using DFS."""
        if start_node_id not in self.nodes or end_node_id not in self.nodes:
            return []

        paths = []

        def dfs(current: str, target: str, path: List[str], depth: int) -> None:
            """Depth-first search for paths."""
            if depth > max_depth:
                return

            if current == target:
                paths.append(path)
                return

            for connection in self.connections.get(current, []):
                next_node = connection.target_node_id
                if next_node not in path:  # Prevent cycles
                    dfs(next_node, target, path + [next_node], depth + 1)

        dfs(start_node_id, end_node_id, [start_node_id], 0)
        return paths

    def get_node_count(self) -> int:
        """Get total node count."""
        return len(self.nodes)

    def get_connection_count(self) -> int:
        """Get total connection count."""
        return sum(len(conns) for conns in self.connections.values())

    def get_all_nodes(self) -> List[SynapticNode]:
        """Get all nodes.

        Returns:
            List of all nodes
        """
        return list(self.nodes.values())

    def get_all_connections(self) -> List[SynapticConnection]:
        """Get all connections.

        Returns:
            List of all connections
        """
        all_connections = []
        for conns in self.connections.values():
            all_connections.extend(conns)
        return all_connections

    def clear(self) -> None:
        """Clear all nodes and connections."""
        self.nodes.clear()
        self.connections.clear()
        self.reverse_connections.clear()


class DependencySynapticNetwork:
    """Dependency-specific synaptic network.

    Tracks package dependencies, versions, and vulnerabilities.
    """

    def __init__(self, backend: Optional[SynapticNetworkInterface] = None):
        """Initialize dependency network.

        Args:
            backend: Storage backend (defaults to in-memory)
        """
        self.backend = backend or InMemorySynapticNetwork()

    def add_package(self, name: str, version: str, ecosystem: str) -> bool:
        """Add package version to network.

        Args:
            name: Package name
            version: Package version
            ecosystem: Ecosystem (python, nodejs, etc.)

        Returns:
            True if successful
        """
        node_id = f"{ecosystem}:{name}:{version}"
        node = SynapticNode(
            node_id=node_id,
            node_type="package_version",
            label=f"{name}@{version}",
            properties={
                "name": name,
                "version": version,
                "ecosystem": ecosystem,
            }
        )
        return self.backend.add_node(node)

    def add_dependency(
        self,
        parent_name: str,
        parent_version: str,
        parent_ecosystem: str,
        child_name: str,
        child_version: str,
        child_ecosystem: str,
        constraint: Optional[str] = None
    ) -> bool:
        """Add dependency relationship.

        Args:
            parent_name: Parent package name
            parent_version: Parent package version
            parent_ecosystem: Parent ecosystem
            child_name: Child package name
            child_version: Child package version
            child_ecosystem: Child ecosystem
            constraint: Version constraint if any

        Returns:
            True if successful
        """
        parent_id = f"{parent_ecosystem}:{parent_name}:{parent_version}"
        child_id = f"{child_ecosystem}:{child_name}:{child_version}"

        # Ensure nodes exist
        if not self.backend.get_node(parent_id):
            self.add_package(parent_name, parent_version, parent_ecosystem)
        if not self.backend.get_node(child_id):
            self.add_package(child_name, child_version, child_ecosystem)

        # Add connection
        connection = SynapticConnection(
            connection_id=f"{parent_id}_depends_on_{child_id}",
            source_node_id=parent_id,
            target_node_id=child_id,
            relationship_type=RelationshipType.DEPENDS_ON,
            properties={
                "constraint": constraint or "*",
            }
        )
        return self.backend.add_connection(connection)

    def get_dependencies(self, package_name: str, version: str, ecosystem: str) -> List[SynapticNode]:
        """Get direct dependencies of package.

        Args:
            package_name: Package name
            version: Package version
            ecosystem: Ecosystem

        Returns:
            List of dependency nodes
        """
        node_id = f"{ecosystem}:{package_name}:{version}"
        connections = self.backend.get_connections(
            node_id,
            RelationshipType.DEPENDS_ON
        )

        return [
            self.backend.get_node(conn.target_node_id)
            for conn in connections
            if self.backend.get_node(conn.target_node_id)
        ]

    def get_transitive_dependencies(
        self,
        package_name: str,
        version: str,
        ecosystem: str
    ) -> List[SynapticNode]:
        """Get all transitive dependencies.

        Args:
            package_name: Package name
            version: Package version
            ecosystem: Ecosystem

        Returns:
            List of all transitive dependency nodes
        """
        node_id = f"{ecosystem}:{package_name}:{version}"
        visited = set()
        stack = [node_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            deps = self.backend.get_connections(current, RelationshipType.DEPENDS_ON)
            for dep in deps:
                if dep.target_node_id not in visited:
                    stack.append(dep.target_node_id)

        # Remove start node from results
        visited.discard(node_id)

        return [
            self.backend.get_node(n_id)
            for n_id in visited
            if self.backend.get_node(n_id)
        ]


class ComplianceSynapticNetwork:
    """Compliance-specific synaptic network.

    Tracks compliance requirements, violations, and mappings.
    """

    def __init__(self, backend: Optional[SynapticNetworkInterface] = None):
        """Initialize compliance network.

        Args:
            backend: Storage backend (defaults to in-memory)
        """
        self.backend = backend or InMemorySynapticNetwork()

    def add_compliance_rule(self, rule_id: str, rule_name: str, rule_text: str) -> bool:
        """Add compliance rule to network.

        Args:
            rule_id: Rule identifier
            rule_name: Rule name
            rule_text: Full rule text

        Returns:
            True if successful
        """
        node = SynapticNode(
            node_id=rule_id,
            node_type="compliance_rule",
            label=rule_name,
            properties={
                "rule_text": rule_text,
            }
        )
        return self.backend.add_node(node)

    def add_violation(self, artifact_id: str, rule_id: str, severity: str) -> bool:
        """Add violation relationship.

        Args:
            artifact_id: Artifact ID (package, code, etc.)
            rule_id: Compliance rule ID
            severity: Violation severity (low, medium, high, critical)

        Returns:
            True if successful
        """
        connection = SynapticConnection(
            connection_id=f"{artifact_id}_violates_{rule_id}",
            source_node_id=artifact_id,
            target_node_id=rule_id,
            relationship_type=RelationshipType.VIOLATES,
            properties={
                "severity": severity,
            }
        )
        return self.backend.add_connection(connection)


class ServiceTopologySynapticNetwork:
    """Service topology-specific synaptic network.

    Tracks service relationships, API contracts, and dependencies.
    """

    def __init__(self, backend: Optional[SynapticNetworkInterface] = None):
        """Initialize service topology network.

        Args:
            backend: Storage backend (defaults to in-memory)
        """
        self.backend = backend or InMemorySynapticNetwork()

    def add_service(self, service_id: str, service_name: str, version: str) -> bool:
        """Add service to network.

        Args:
            service_id: Service ID
            service_name: Service name
            version: Service version

        Returns:
            True if successful
        """
        node = SynapticNode(
            node_id=service_id,
            node_type="service",
            label=service_name,
            properties={
                "version": version,
            }
        )
        return self.backend.add_node(node)

    def add_service_call(
        self,
        caller_service_id: str,
        callee_service_id: str,
        endpoint: str
    ) -> bool:
        """Add service-to-service call relationship.

        Args:
            caller_service_id: Calling service ID
            callee_service_id: Called service ID
            endpoint: Called endpoint

        Returns:
            True if successful
        """
        connection = SynapticConnection(
            connection_id=f"{caller_service_id}_calls_{callee_service_id}",
            source_node_id=caller_service_id,
            target_node_id=callee_service_id,
            relationship_type=RelationshipType.CALLS,
            properties={
                "endpoint": endpoint,
            }
        )
        return self.backend.add_connection(connection)


if __name__ == "__main__":
    logger.info("Synaptic Network - Graph Storage & Querying Layer")
