"""
Integration Module - Cross-orchestrator communication

This module handles:
- Domain Brain queries
- Knowledge router integration
- Audit logging integration
"""

from .audit_logger_connector import AuditLogEntry, AuditLoggerConnector
from .domain_brain_connector import DomainBrainConnector, DomainBrainResult
from .knowledge_router_connector import (
    KnowledgeRouterConnector,
    KnowledgeSynthesisResult,
)

__all__ = [
    "DomainBrainConnector",
    "DomainBrainResult",
    "KnowledgeRouterConnector",
    "KnowledgeSynthesisResult",
    "AuditLoggerConnector",
    "AuditLogEntry",
]
