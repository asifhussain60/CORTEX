"""
Integration Module - Cross-orchestrator communication

This module handles:
- Domain Brain queries
- Knowledge router integration
- Audit logging integration
"""

from .domain_brain_connector import DomainBrainConnector, DomainBrainResult
from .knowledge_router_connector import KnowledgeRouterConnector, KnowledgeSynthesisResult
from .audit_logger_connector import AuditLoggerConnector, AuditLogEntry

__all__ = [
    "DomainBrainConnector",
    "DomainBrainResult",
    "KnowledgeRouterConnector",
    "KnowledgeSynthesisResult",
    "AuditLoggerConnector",
    "AuditLogEntry",
]
