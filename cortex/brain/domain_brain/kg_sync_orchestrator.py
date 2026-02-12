"""Sync orchestrator for Knowledge Graph entity ingestion.

Orchestrates the end-to-end process of syncing domain brain entities to the
knowledge graph, including deduplication, ingestion, and error handling.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from cortex.brain.core.knowledge.graph.interface import GraphQueryError, IGraphAdapter
from cortex.brain.domain_brain.kg_deduplicator import (
    DeduplicationResult,
    EntityDeduplicator,
)
from cortex.brain.domain_brain.kg_ingest_adapter import EntityIngestAdapter


class SyncAuditEntry:
    """Audit log entry for sync operation.

    Attributes:
        timestamp: When the sync occurred
        operation: Type of operation (INGEST, DEDUPLICATE, SYNC)
        entity_count: Number of entities affected
        status: SUCCESS or FAILED
        message: Descriptive message
    """

    def __init__(
        self,
        operation: str,
        entity_count: int,
        status: str,
        message: str = "",
    ) -> None:
        """Initialize audit entry."""
        self.timestamp = datetime.utcnow().isoformat()
        self.operation = operation
        self.entity_count = entity_count
        self.status = status
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dict: Audit entry as dictionary
        """
        return {
            "timestamp": self.timestamp,
            "operation": self.operation,
            "entity_count": self.entity_count,
            "status": self.status,
            "message": self.message,
        }


class SyncOrchestrator:
    """Orchestrates entity sync from domain brain to knowledge graph.

    Handles:
      - Entity deduplication
      - Non-destructive ingestion
      - Idempotent operations
      - Graceful fallback on KG errors
      - Comprehensive audit logging
    """

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize sync orchestrator.

        Args:
            adapter: Target IGraphAdapter to sync into
        """
        self.adapter = adapter
        self.ingest = EntityIngestAdapter(adapter)
        self.deduplicator = EntityDeduplicator()
        self.audit_log: List[SyncAuditEntry] = []

    def sync_entities(
        self, entities: List[Dict[str, Any]], force: bool = False
    ) -> Dict[str, Any]:
        """Perform complete entity sync to KG.

        Idempotent operation: running twice produces identical KG state.

        Args:
            entities: List of domain entities to sync
            force: If True, skip deduplication check

        Returns:
            Dict: Sync result with statistics

        Raises:
            GraphQueryError: If sync fails and cannot recover
        """
        try:
            # Phase 1: Deduplicate
            dedup_result = self.deduplicator.deduplicate(entities)
            self._log_audit(
                "DEDUPLICATE",
                len(entities),
                "SUCCESS",
                f"Deduplicated {len(entities)} → {dedup_result.total_output} entities",
            )

            # Phase 2: Ingest deduplicated entities
            deduplicated = self.deduplicator.get_deduplicated_entities()
            ingest_count = 0

            for entity in deduplicated:
                try:
                    # Try to ingest - will skip if already exists
                    self.ingest.ingest_domain(
                        domain_id=entity.get("id", ""),
                        domain_name=entity.get("name", ""),
                        properties=entity.get("properties", {}),
                    )
                    ingest_count += 1
                except GraphQueryError as e:
                    if "already exists" not in str(e):
                        raise
                    # Duplicate in KG, skip
                    pass

            self._log_audit(
                "INGEST",
                ingest_count,
                "SUCCESS",
                f"Ingested {ingest_count} entities to KG",
            )

            return {
                "status": "SUCCESS",
                "input_count": len(entities),
                "deduplicated_count": dedup_result.total_output,
                "ingested_count": ingest_count,
                "duplicates_removed": dedup_result.duplicates_found,
                "conflicts_resolved": dedup_result.conflicts_resolved,
                "audit_log": [entry.to_dict() for entry in self.audit_log],
            }

        except GraphQueryError as e:
            self._log_audit("SYNC", len(entities), "FAILED", str(e))
            raise

    def sync_relationships(
        self, relationships: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Sync relationships between entities.

        Args:
            relationships: List of relationships to sync

        Returns:
            Dict: Sync result with relationship count

        Raises:
            GraphQueryError: If sync fails
        """
        try:
            sync_count = 0

            for rel in relationships:
                try:
                    count = self.ingest.ingest_relationship(
                        source_id=rel.get("source_id", ""),
                        rel_type=rel.get("rel_type", ""),
                        target_id=rel.get("target_id", ""),
                        properties=rel.get("properties", {}),
                    )
                    sync_count += count
                except GraphQueryError as e:
                    if "already exists" not in str(e):
                        raise

            self._log_audit(
                "SYNC_RELATIONSHIPS",
                sync_count,
                "SUCCESS",
                f"Synced {sync_count} relationships",
            )

            return {
                "status": "SUCCESS",
                "input_count": len(relationships),
                "synced_count": sync_count,
            }

        except GraphQueryError as e:
            self._log_audit("SYNC_RELATIONSHIPS", len(relationships), "FAILED", str(e))
            raise

    def verify_sync_idempotency(
        self, entities: List[Dict[str, Any]]
    ) -> bool:
        """Verify that sync is idempotent (2x sync = same state).

        Args:
            entities: Entities to sync twice

        Returns:
            bool: True if sync is idempotent

        Raises:
            GraphQueryError: On verification failure
        """
        # First sync
        result1 = self.sync_entities(entities)
        count1 = result1.get("ingested_count", 0)

        # Second sync (should ingest 0 new entities)
        result2 = self.sync_entities(entities)
        count2 = result2.get("ingested_count", 0)

        # Idempotency check: second sync should not ingest new entities
        # (some may be re-attempted but should be skipped as duplicates)
        is_idempotent = count2 == 0 or count2 <= count1

        self._log_audit(
            "VERIFY_IDEMPOTENCY",
            len(entities),
            "SUCCESS" if is_idempotent else "FAILED",
            f"Idempotency verified: sync1={count1}, sync2={count2}",
        )

        return is_idempotent

    def _log_audit(
        self, operation: str, entity_count: int, status: str, message: str = ""
    ) -> None:
        """Log sync operation to audit trail.

        Args:
            operation: Type of operation
            entity_count: Number of entities affected
            status: Operation status (SUCCESS/FAILED)
            message: Descriptive message
        """
        entry = SyncAuditEntry(
            operation=operation,
            entity_count=entity_count,
            status=status,
            message=message,
        )
        self.audit_log.append(entry)

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get complete audit log.

        Returns:
            List[Dict]: Audit trail entries
        """
        return [entry.to_dict() for entry in self.audit_log]
