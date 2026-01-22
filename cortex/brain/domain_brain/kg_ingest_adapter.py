"""Entity ingest adapter for Knowledge Graph backend.

Converts Domain Brain entities and relationships into Knowledge Graph nodes
and edges for ingestion into the KG system.
"""

from typing import Any, Dict, List, Optional
from cortex.brain.core.knowledge.graph.interface import (
    IGraphAdapter,
    EntityNode,
    Relationship,
    GraphQueryError,
)


class EntityIngestAdapter:
    """Adapter for ingesting Domain Brain entities into Knowledge Graph.

    Converts business domain entities into KG entity and relationship objects
    that can be ingested into any IGraphAdapter backend (mock, SQLite, Neo4j).

    Non-destructive: converts entities without modifying original BKIO data.
    """

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize ingest adapter with target KG adapter.

        Args:
            adapter: Target IGraphAdapter to ingest entities into
        """
        self.adapter = adapter

    def ingest_domain(
        self, domain_id: str, domain_name: str, properties: Optional[Dict[str, Any]] = None
    ) -> int:
        """Ingest a domain entity into the KG.

        Args:
            domain_id: Unique identifier for domain
            domain_name: Human-readable domain name
            properties: Optional domain properties

        Returns:
            int: Number of entities created

        Raises:
            GraphQueryError: On ingestion failure
        """
        props = properties or {}
        props.update({"name": domain_name, "domain_id": domain_id})

        self.adapter.create_entity(
            entity_id=domain_id,
            entity_type="Domain",
            properties=props,
        )

        return 1

    def ingest_service(
        self,
        service_id: str,
        service_name: str,
        domain_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Ingest a service entity into the KG.

        Args:
            service_id: Unique identifier for service
            service_name: Human-readable service name
            domain_id: Parent domain ID
            properties: Optional service properties

        Returns:
            int: Number of entities created

        Raises:
            GraphQueryError: On ingestion failure
        """
        props = properties or {}
        props.update({"name": service_name, "service_id": service_id})

        # Create service entity
        self.adapter.create_entity(
            entity_id=service_id,
            entity_type="Service",
            properties=props,
        )

        # Create BELONGS_TO relationship
        self.adapter.create_relationship(
            source_id=service_id,
            rel_type="BELONGS_TO",
            target_id=domain_id,
            properties={"relationship_type": "domain_member"},
        )

        return 2  # Entity + relationship

    def ingest_api(
        self,
        api_id: str,
        api_name: str,
        service_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Ingest an API entity into the KG.

        Args:
            api_id: Unique identifier for API
            api_name: Human-readable API name
            service_id: Parent service ID
            properties: Optional API properties

        Returns:
            int: Number of entities created

        Raises:
            GraphQueryError: On ingestion failure
        """
        props = properties or {}
        props.update({"name": api_name, "api_id": api_id})

        # Create API entity
        self.adapter.create_entity(
            entity_id=api_id,
            entity_type="API",
            properties=props,
        )

        # Create BELONGS_TO relationship
        self.adapter.create_relationship(
            source_id=api_id,
            rel_type="BELONGS_TO",
            target_id=service_id,
            properties={"relationship_type": "service_member"},
        )

        return 2  # Entity + relationship

    def ingest_relationship(
        self,
        source_id: str,
        rel_type: str,
        target_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Ingest a relationship between two entities.

        Args:
            source_id: Source entity ID
            rel_type: Relationship type
            target_id: Target entity ID
            properties: Optional relationship properties

        Returns:
            int: Number of relationships created (1 or 0)

        Raises:
            GraphQueryError: On ingestion failure
        """
        props = properties or {}

        try:
            self.adapter.create_relationship(
                source_id=source_id,
                rel_type=rel_type,
                target_id=target_id,
                properties=props,
            )
            return 1
        except GraphQueryError as e:
            if "already exists" in str(e):
                return 0  # Duplicate relationship, skip
            raise
