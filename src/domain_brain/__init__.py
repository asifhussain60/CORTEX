"""Domain Brain: Strategic Knowledge Centralization Module.

This module provides a unified interface for managing business domain knowledge
across multiple sources (AST Intelligence, Git, Comments, Relationships, BKIO).

Exports:
    - DomainBrainAPI: Main API for domain coordination
    - Domain: Domain entity model
    - Entity: Entity within a domain
    - Conflict: Conflict between sources
    - ConsistencyValidator: Schema validation and conflict detection
    - AuditLogger: Immutable hash chain logger

Example:
    >>> from src.domain_brain import DomainBrainAPI, Domain
    >>> api = DomainBrainAPI()
    >>> domain = api.query_domain("auth-service")
    >>> entities = api.search_entities("authentication")
"""

from src.domain_brain.api import DomainBrainAPI
from src.domain_brain.models import Domain, Entity, Conflict, AuditEntry
from src.domain_brain.validator import ConsistencyValidator
from src.domain_brain.audit_logger import AuditLogger

__all__ = [
    "DomainBrainAPI",
    "Domain",
    "Entity",
    "Conflict",
    "AuditEntry",
    "ConsistencyValidator",
    "AuditLogger",
]
