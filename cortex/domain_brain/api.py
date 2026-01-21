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


__all__ = [
    "DomainBrainAPI",
    "Domain",
    "Entity",
    "AuditLogger",
    "AuditEntry",
]