"""
Integration layer for audit logging and self-healing.

Provides base classes and utilities for integrating audit logging
capabilities into CORTEX orchestrators.
"""

from .orchestrator_integration import (
    AuditedOrchestrator,
    OrchestratorHealthCheck
)

__all__ = [
    "AuditedOrchestrator",
    "OrchestratorHealthCheck"
]
