"""Module: api.py."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from cortex.domain_brain.models import EntityType
from cortex_brain.domain_brain.models import Conflict


@dataclass
class AuditEntry:
    """Audit entry."""
    entry_id: str
    operation: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation.
        """
        return {
            "entry_id": self.entry_id,
            "operation": self.operation,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "details": self.details
        }


class AuditLogger:
    """Audit logger for tracking operations."""
    
    def __init__(self) -> None:
        """Initialize audit logger."""
        self.entries: List[AuditEntry] = []
    
    def log(self, entry_id: str, operation: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log an operation.
        
        Args:
            entry_id: Entry identifier.
            operation: Operation type.
            details: Optional operation details.
        """
        entry = AuditEntry(
            entry_id=entry_id,
            operation=operation,
            details=details or {},
        )
        self.entries.append(entry)
    
    def get_all_entries(self) -> List[AuditEntry]:
        """Get all entries.
        
        Returns:
            List of audit entries.
        """
        return self.entries


@dataclass
class Entity:
    """Domain entity."""
    entity_id: str
    entity_type: EntityType
    name: str
    description: str = ""
    source: str = "AST"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Domain:
    """Domain model."""
    domain_id: str
    name: str
    description: str
    entities: Dict[str, Entity] = field(default_factory=dict)
    conflicts: List[Conflict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DomainBrainAPI:
    """Domain Brain API for managing domains and entities."""

    def __init__(self) -> None:
        """Initialize API."""
        self.domains: Dict[str, Domain] = {}
        self.audit_logger = AuditLogger()
    
    def upsert_domain(self, domain: Domain) -> None:
        """Create or update domain.
        
        Args:
            domain: Domain to upsert.
        """
        self.domains[domain.domain_id] = domain
        self.audit_logger.log(domain.domain_id, "upsert_domain")
    
    def query_domain(self, domain_id: str) -> Optional[Domain]:
        """Query domain by ID.
        
        Args:
            domain_id: Domain identifier.
        
        Returns:
            Domain if found, None otherwise.
        """
        return self.domains.get(domain_id)
    
    def get_all_domains(self) -> List[Domain]:
        """Get all domains.
        
        Returns:
            List of all domains.
        """
        return list(self.domains.values())
    
    def delete_domain(self, domain_id: str) -> bool:
        """Delete domain.
        
        Args:
            domain_id: Domain identifier.
        
        Returns:
            True if deleted, False if not found.
        """
        if domain_id in self.domains:
            del self.domains[domain_id]
            self.audit_logger.log(domain_id, "delete_domain")
            return True
        return False
    
    def add_entity_to_domain(self, domain_id: str, entity: Entity) -> bool:
        """Add entity to domain.
        
        Args:
            domain_id: Domain identifier.
            entity: Entity to add.
        
        Returns:
            True if added, False if domain not found.
        """
        domain = self.query_domain(domain_id)
        if domain:
            domain.entities[entity.entity_id] = entity
            self.audit_logger.log(entity.entity_id, "add_entity")
            return True
        return False
    
    def audit_domain(self, domain_id: str) -> List[Dict[str, Any]]:
        """Get audit entries for a domain.
        
        Args:
            domain_id: Domain identifier to filter by.
        
        Returns:
            List of audit entries as dicts related to the domain.
        """
        return [e.to_dict() for e in self.audit_logger.entries if e.entry_id == domain_id]
    
    def search_entities(self, query: str) -> List[Entity]:
        """Search entities by query.
        
        Args:
            query: Search query string.
        
        Returns:
            List of matching entities.
        """
        results = []
        for domain in self.domains.values():
            for entity in domain.entities.values():
                if query.lower() in entity.name.lower() or query.lower() in entity.description.lower():
                    results.append(entity)
        return results
    
    def get_conflicts(self, domain_id: str) -> List[Conflict]:
        """Get conflicts for a domain.
        
        Args:
            domain_id: Domain identifier.
        
        Returns:
            List of conflicts in the domain.
        """
        domain = self.domains.get(domain_id)
        if domain:
            return domain.conflicts
        return []
    
    def resolve_conflict(self, conflict_id: str, resolved_value: Any) -> bool:
        """Resolve a conflict.
        
        Args:
            conflict_id: Conflict identifier.
            resolved_value: Resolution value.
        
        Returns:
            True if resolved, False otherwise.
        """
        for domain in self.domains.values():
            for i, conflict in enumerate(domain.conflicts):
                if conflict.conflict_id == conflict_id:
                    domain.conflicts.pop(i)
                    self.audit_logger.log(conflict_id, "resolve_conflict", {"value": str(resolved_value)})
                    return True
        return False
    
    def list_domains(self) -> List[Domain]:
        """List all domains.
        
        Returns:
            List of all domains.
        """
        return list(self.domains.values())
    
    def validate_domain(self, domain: Domain) -> Dict[str, Any]:
        """Validate a domain.
        
        Args:
            domain: Domain to validate.
        
        Returns:
            Validation result dictionary.
        """
        errors = []
        
        if not domain.domain_id:
            errors.append("domain_id is required")
        if not domain.name:
            errors.append("name is required")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "domain_id": domain.domain_id
        }


__all__ = [
    "DomainBrainAPI",
    "Domain",
    "Entity",
    "AuditLogger",
    "AuditEntry",
]