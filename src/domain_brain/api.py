"""Domain Brain API: Main interface for domain coordination.

Provides methods for querying, creating, updating, and deleting domains,
as well as managing conflicts and audit trails.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from src.domain_brain.models import Domain, Entity, Conflict, AuditOperationType, ConflictResolution
from src.domain_brain.validator import ConsistencyValidator, ValidationResult
from src.domain_brain.audit_logger import AuditLogger


class DomainBrainAPI:
    """Query/write interface for domain coordination.

    Provides high-level API for managing domains, entities, and conflicts.
    All operations are audit-logged with hash chain integrity.

    Methods:
        - query_domain(domain_id) -> Domain
        - list_domains() -> List[Domain]
        - search_entities(query) -> List[Entity]
        - upsert_domain(domain) -> void
        - delete_domain(domain_id) -> void
        - get_conflicts(domain_id) -> List[Conflict]
        - resolve_conflict(conflict_id, resolution) -> void
        - audit_domain(domain_id) -> List[AuditEntry]
        - validate_domain(domain) -> ValidationResult
    """

    def __init__(self) -> None:
        """Initialize Domain Brain API."""
        self.domains: Dict[str, Domain] = {}
        self.validator = ConsistencyValidator()
        self.audit_logger = AuditLogger()

    def query_domain(self, domain_id: str) -> Optional[Domain]:
        """Query a domain by ID.

        Args:
            domain_id: ID of domain to retrieve

        Returns:
            Domain if found, None otherwise
        """
        self.audit_logger.log_operation(
            AuditOperationType.QUERY,
            domain_id=domain_id,
            description=f"Query domain {domain_id}",
        )
        return self.domains.get(domain_id)

    def list_domains(self) -> List[Domain]:
        """List all domains.

        Returns:
            List of all domains
        """
        self.audit_logger.log_operation(
            AuditOperationType.QUERY,
            description="List all domains",
        )
        return list(self.domains.values())

    def search_entities(self, query: str) -> List[Entity]:
        """Search for entities across all domains.

        Searches entity names, descriptions, and metadata.

        Args:
            query: Search query string

        Returns:
            List of matching entities
        """
        self.audit_logger.log_operation(
            AuditOperationType.QUERY,
            description=f"Search entities: {query}",
        )

        results = []
        query_lower = query.lower()

        for domain in self.domains.values():
            for entity in domain.entities.values():
                if (
                    query_lower in entity.name.lower()
                    or query_lower in entity.description.lower()
                ):
                    results.append(entity)

        return results

    def upsert_domain(self, domain: Domain) -> None:
        """Create or update a domain.

        Validates domain before upserting. Audit logs the operation
        with hash chain integrity.

        Args:
            domain: Domain to create or update

        Raises:
            ValueError: If domain validation fails
        """
        # Validate domain
        validation = self.validate_domain(domain)
        if not validation.is_valid:
            raise ValueError(f"Domain validation failed: {validation.errors}")

        # Check if creating or updating
        is_update = domain.domain_id in self.domains
        operation = AuditOperationType.UPDATE if is_update else AuditOperationType.CREATE

        # Store domain
        self.domains[domain.domain_id] = domain

        # Log operation
        self.audit_logger.log_operation(
            operation,
            domain_id=domain.domain_id,
            description=f"Upsert domain: {domain.name}",
            new_value=domain.to_dict(),
        )

    def delete_domain(self, domain_id: str) -> None:
        """Delete a domain.

        Args:
            domain_id: ID of domain to delete
        """
        if domain_id in self.domains:
            domain = self.domains[domain_id]
            del self.domains[domain_id]

            self.audit_logger.log_operation(
                AuditOperationType.DELETE,
                domain_id=domain_id,
                description=f"Delete domain: {domain.name}",
                previous_value=domain.to_dict(),
            )

    def get_conflicts(self, domain_id: str) -> List[Conflict]:
        """Get all conflicts for a domain.

        Args:
            domain_id: ID of domain

        Returns:
            List of conflicts in the domain
        """
        domain = self.domains.get(domain_id)
        if not domain:
            return []

        self.audit_logger.log_operation(
            AuditOperationType.QUERY,
            domain_id=domain_id,
            description=f"Get conflicts for domain {domain_id}",
        )

        return domain.conflicts

    def resolve_conflict(
        self,
        conflict_id: str,
        domain_id: str,
        resolution_value: Any,
        resolution_method: str = "hierarchy",
    ) -> None:
        """Resolve a conflict in a domain.

        Updates the conflict resolution status and method.

        Args:
            conflict_id: ID of conflict to resolve
            domain_id: ID of domain containing conflict
            resolution_value: Resolved value for the conflict
            resolution_method: Method used for resolution (hierarchy, lens, manual)
        """
        domain = self.domains.get(domain_id)
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")

        # Find conflict
        conflict = None
        for c in domain.conflicts:
            if c.conflict_id == conflict_id:
                conflict = c
                break

        if not conflict:
            raise ValueError(f"Conflict not found: {conflict_id}")

        # Update conflict
        old_status = conflict.resolution_status
        conflict.resolution_status = ConflictResolution(resolution_method)
        conflict.resolution_method = resolution_method
        conflict.resolved_at = datetime.utcnow()

        # Log resolution
        self.audit_logger.log_operation(
            AuditOperationType.CONFLICT_RESOLVED,
            domain_id=domain_id,
            entity_id=conflict_id,
            description=f"Resolve conflict {conflict_id}: {old_status.value} -> {resolution_method}",
            new_value=resolution_value,
        )

    def audit_domain(self, domain_id: str) -> List[Any]:
        """Get audit trail for a domain.

        Args:
            domain_id: ID of domain

        Returns:
            List of audit entries for the domain
        """
        entries = self.audit_logger.get_domain_audit_trail(domain_id)
        return [e.to_dict() for e in entries]

    def validate_domain(self, domain: Domain) -> ValidationResult:
        """Validate a domain.

        Checks:
        - JSON Schema validation
        - Referential integrity
        - Circular dependencies
        - Conflicts between sources

        Args:
            domain: Domain to validate

        Returns:
            ValidationResult with details
        """
        return self.validator.validate_domain(domain)

    def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit trail statistics.

        Returns:
            Dictionary with audit metrics
        """
        stats = self.audit_logger.get_cache_stats()
        stats["domains_count"] = len(self.domains)
        return stats
