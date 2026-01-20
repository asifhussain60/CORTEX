"""Domain Brain data models.

Defines the core data structures for domain entities, conflicts, and audit entries.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from datetime import datetime


class EntityType(Enum):
    """Types of entities in domain brain."""

    SERVICE = "service"
    FUNCTION = "function"
    CLASS = "class"
    DATABASE = "database"
    API = "api"
    WORKFLOW = "workflow"
    CONFIGURATION = "configuration"
    OTHER = "other"


class ConflictResolution(Enum):
    """Resolution strategies for conflicts."""

    HIERARCHY = "hierarchy"  # Use source priority hierarchy
    LENS_QUERY = "lens_query"  # Query LENS for synthesis
    MANUAL_REVIEW = "manual_review"  # Mark for human review
    MERGED = "merged"  # Conflicts merged into unified view


class AuditOperationType(Enum):
    """Types of audit operations."""

    AC_START = "AC_START"
    AC_EXECUTE = "AC_EXECUTE"
    AC_COMPLETE = "AC_COMPLETE"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    QUERY = "QUERY"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    CONFLICT_RESOLVED = "CONFLICT_RESOLVED"


@dataclass
class Entity:
    """Represents an entity within a domain.

    Attributes:
        entity_id: Unique identifier for the entity
        entity_type: Type of entity (service, function, class, etc.)
        name: Human-readable name
        description: Detailed description
        source: Source of this entity (AST, Git, Comments, Relationships, BKIO)
        metadata: Additional metadata as key-value pairs
        created_at: Timestamp when entity was created
        updated_at: Timestamp when entity was last updated
    """

    entity_id: str
    entity_type: EntityType
    name: str
    description: str
    source: str  # AST, Git, Comments, Relationships, BKIO
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entity":
        """Create entity from dictionary."""
        return cls(
            entity_id=data["entity_id"],
            entity_type=EntityType(data["entity_type"]),
            name=data["name"],
            description=data["description"],
            source=data["source"],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.utcnow().isoformat())),
        )


@dataclass
class Conflict:
    """Represents a conflict between sources on a domain attribute.

    Attributes:
        conflict_id: Unique identifier for the conflict
        domain_id: Domain where conflict exists
        attribute: Attribute name where conflict exists
        source_values: Mapping of source -> value (conflicting values)
        resolution_status: Current resolution status
        resolution_method: Method used to resolve (if resolved)
        created_at: Timestamp when conflict was detected
        resolved_at: Timestamp when conflict was resolved (if applicable)
    """

    conflict_id: str
    domain_id: str
    attribute: str
    source_values: Dict[str, Any]  # source -> value mapping
    resolution_status: ConflictResolution = ConflictResolution.HIERARCHY
    resolution_method: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert conflict to dictionary."""
        return {
            "conflict_id": self.conflict_id,
            "domain_id": self.domain_id,
            "attribute": self.attribute,
            "source_values": self.source_values,
            "resolution_status": self.resolution_status.value,
            "resolution_method": self.resolution_method,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


@dataclass
class AuditEntry:
    """Represents an audit log entry.

    Attributes:
        entry_id: Unique identifier for the entry
        operation: Type of operation (CREATE, UPDATE, DELETE, etc.)
        entity_id: ID of entity affected (if applicable)
        domain_id: ID of domain affected (if applicable)
        description: Human-readable description of operation
        previous_value: Previous value (for updates)
        new_value: New value (for creates/updates)
        user: User who performed the operation
        timestamp: When the operation occurred
        hash: SHA-256 hash of entry for chain integrity
        previous_hash: Hash of previous entry (for hash chain)
    """

    entry_id: str
    operation: AuditOperationType
    entity_id: Optional[str] = None
    domain_id: Optional[str] = None
    description: str = ""
    previous_value: Optional[Any] = None
    new_value: Optional[Any] = None
    user: str = "system"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    hash: str = ""
    previous_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary."""
        return {
            "entry_id": self.entry_id,
            "operation": self.operation.value,
            "entity_id": self.entity_id,
            "domain_id": self.domain_id,
            "description": self.description,
            "previous_value": self.previous_value,
            "new_value": self.new_value,
            "user": self.user,
            "timestamp": self.timestamp.isoformat(),
            "hash": self.hash,
            "previous_hash": self.previous_hash,
        }


@dataclass
class Domain:
    """Represents a business domain.

    A domain is a logical grouping of related entities and concepts within
    the business system. It serves as the primary coordination unit for the
    Domain Brain.

    Attributes:
        domain_id: Unique identifier for the domain
        name: Human-readable name
        description: Detailed description of the domain
        entities: Map of entity_id -> Entity
        conflicts: List of conflicts within this domain
        source_priority: Priority order for source hierarchy
        created_at: Timestamp when domain was created
        updated_at: Timestamp when domain was last updated
        metadata: Additional metadata as key-value pairs
    """

    domain_id: str
    name: str
    description: str
    entities: Dict[str, Entity] = field(default_factory=dict)
    conflicts: List[Conflict] = field(default_factory=list)
    source_priority: List[str] = field(
        default_factory=lambda: ["BKIO", "RELATIONSHIPS", "AST", "GIT", "LENS"]
    )
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert domain to dictionary."""
        return {
            "domain_id": self.domain_id,
            "name": self.name,
            "description": self.description,
            "entities": {eid: e.to_dict() for eid, e in self.entities.items()},
            "conflicts": [c.to_dict() for c in self.conflicts],
            "source_priority": self.source_priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Domain":
        """Create domain from dictionary."""
        entities = {
            eid: Entity.from_dict(e) for eid, e in data.get("entities", {}).items()
        }
        conflicts = [Conflict(**c) for c in data.get("conflicts", [])]
        return cls(
            domain_id=data["domain_id"],
            name=data["name"],
            description=data["description"],
            entities=entities,
            conflicts=conflicts,
            source_priority=data.get("source_priority", ["BKIO", "RELATIONSHIPS", "AST", "GIT", "LENS"]),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.utcnow().isoformat())),
            metadata=data.get("metadata", {}),
        )
