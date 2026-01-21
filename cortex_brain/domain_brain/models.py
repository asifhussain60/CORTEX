"""Domain Brain Models - Data models for domain-specific knowledge.

Defines models for domain orchestration, domain-specific operations, and
domain knowledge representation.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class EntityType(Enum):
    """Entity types."""

    DOMAIN = "domain"
    SERVICE = "service"
    RESOURCE = "resource"
    OPERATION = "operation"
    DATA = "data"
    FUNCTION = "function"
    CLASS = "class"
    DATABASE = "database"


class AuditOperationType(Enum):
    """Types of audit operations."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    AC_START = "ac_start"
    AC_EXECUTE = "ac_execute"
    AC_COMPLETE = "ac_complete"


@dataclass
class Entity:
    """Domain entity.

    Attributes:
        entity_id: Entity identifier.
        entity_type: Type of entity.
        name: Entity name.
        domain_id: Domain identifier.
        description: Entity description.
        source: Source of entity (AST, BKIO, etc).
        metadata: Additional metadata.
    """

    entity_id: str
    entity_type: EntityType
    name: str
    description: str = ""
    domain_id: str = ""
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conflict:
    """Conflict between entities or operations.

    Attributes:
        conflict_id: Unique conflict identifier.
        domain_id: Domain ID for this conflict.
        attribute: Attribute involved in conflict.
        source_values: Dictionary of conflicting source values.
        entity_a: First entity involved (optional).
        entity_b: Second entity involved (optional).
        conflict_type: Type of conflict.
        severity: Conflict severity.
        resolution: Proposed resolution.
        resolution_method: Method used to resolve conflict.
        resolved_at: When conflict was resolved.
    """

    conflict_id: str
    domain_id: str
    attribute: str
    source_values: Dict[str, Any] = field(default_factory=dict)
    entity_a: str = ""
    entity_b: str = ""
    conflict_type: str = ""
    severity: str = "medium"
    resolution: str = ""
    resolution_method: str = ""
    resolved_at: Optional[datetime] = None


@dataclass
class DomainModel:
    """Base domain data model.

    Attributes:
        domain_id: Domain identifier.
        name: Model name.
        description: Model description.
        created_at: When model was created.
        entities: Dictionary of entities in the domain.
        conflicts: List of conflicts in the domain.
        metadata: Additional metadata.
    """

    domain_id: str
    name: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    entities: Dict[str, Any] = field(default_factory=dict)
    conflicts: List[Conflict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DomainCapability:
    """Capability within a domain.

    Attributes:
        capability_id: Capability identifier.
        domain_id: Domain identifier.
        name: Capability name.
        description: Capability description.
        methods: Available methods/operations.
        parameters: Capability parameters.
    """

    capability_id: str
    domain_id: str
    name: str
    description: str
    methods: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DomainState:
    """State information for a domain.

    Attributes:
        domain_id: Domain identifier.
        state_key: State key.
        state_value: State value.
        last_updated: When state was last updated.
    """

    domain_id: str
    state_key: str
    state_value: Any
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class DomainContext:
    """Context for domain operations.

    Attributes:
        domain_id: Domain identifier.
        operation_id: Current operation ID.
        user_id: User identifier.
        state: Current domain state.
        capabilities: Available capabilities.
        metadata: Additional context metadata.
    """

    domain_id: str
    operation_id: str
    user_id: str
    state: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DomainRegistry:
    """Registry for domain models and capabilities."""

    def __init__(self) -> None:
        """Initialize domain registry."""
        self.domains: Dict[str, DomainModel] = {}
        self.capabilities: Dict[str, DomainCapability] = {}
        self.states: Dict[str, DomainState] = {}

    def register_domain(self, model: DomainModel) -> None:
        """Register a domain model.

        Args:
            model: DomainModel to register.
        """
        self.domains[model.domain_id] = model

    def register_capability(self, capability: DomainCapability) -> None:
        """Register a domain capability.

        Args:
            capability: DomainCapability to register.
        """
        self.capabilities[capability.capability_id] = capability

    def get_domain(self, domain_id: str) -> Optional[DomainModel]:
        """Get a domain model.

        Args:
            domain_id: Domain identifier.

        Returns:
            DomainModel or None if not found.
        """
        return self.domains.get(domain_id)

    def get_capabilities(self, domain_id: str) -> List[DomainCapability]:
        """Get capabilities for a domain.

        Args:
            domain_id: Domain identifier.

        Returns:
            List of capabilities in domain.
        """
        return [
            c for c in self.capabilities.values()
            if c.domain_id == domain_id
        ]

    def update_state(self, domain_id: str, state_key: str, state_value: Any) -> DomainState:
        """Update domain state.

        Args:
            domain_id: Domain identifier.
            state_key: State key.
            state_value: State value.

        Returns:
            Updated DomainState.
        """
        state_id = f"{domain_id}:{state_key}"
        state = DomainState(
            domain_id=domain_id,
            state_key=state_key,
            state_value=state_value,
        )
        self.states[state_id] = state
        return state


# Global domain registry instance
_global_domain_registry: Optional[DomainRegistry] = None


def get_domain_registry() -> DomainRegistry:
    """Get global domain registry.

    Returns:
        DomainRegistry singleton.
    """
    global _global_domain_registry
    if _global_domain_registry is None:
        _global_domain_registry = DomainRegistry()
    return _global_domain_registry


# Alias for backward compatibility
Domain = DomainModel


@dataclass
class ConflictResolution:
    """Conflict resolution result."""
    conflict_id: str
    resolution_strategy: str
    resolved: bool = False


@dataclass
class ValidationResult:
    """Domain validation result.
    
    Attributes:
        is_valid: Whether domain is valid.
        errors: List of validation errors.
        conflicts_detected: List of detected conflicts.
    """
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    conflicts_detected: List[Any] = field(default_factory=list)


__all__ = [
    "DomainModel",
    "Domain",
    "Entity",
    "EntityType",
    "AuditOperationType",
    "Conflict",
    "ConflictResolution",
    "DomainCapability",
    "DomainState",
    "DomainContext",
    "DomainRegistry",
    "get_domain_registry",
]
