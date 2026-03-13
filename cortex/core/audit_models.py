"""
cortex.core.audit_models — Canonical AuditEntry Definition
===========================================================

Single source of truth for ``AuditEntry`` across the CORTEX framework.

**Phase 59-a** consolidates 9 duplicate definitions from:
- cortex.orchestrators.core.intent_router.intent_reflection_protocol
- cortex.intelligence.domain_brain.audit_log_manager
- cortex.intelligence.domain_brain.domain_brain_models
- cortex.intelligence.domain_brain.api
- cortex.governance.audit_navigator
- cortex.infrastructure.secrets.audit_trail
- cortex.infrastructure.secrets.secrets_management
- cortex.infrastructure.enhanced_audit_logger
- cortex.infrastructure.audit_db

The canonical model is the **superset** of all variant fields, with every
field (except ``entry_id``) carrying a safe default so that all existing
call sites continue to work without modification.

CORE Rules: CORE-035 (single canonical), CORE-011 (type hints), CORE-012 (docstrings)
AC_START: AC-AUDIT-MODELS-5901
"""
from __future__ import annotations

import os
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


def _thread_safe_uuid4() -> str:
    """Generate a unique entry ID using secrets — thread-safe on all platforms.

    Uses secrets.token_hex which relies on os.urandom and avoids the native
    libuuid C extension (which can segfault on macOS Python 3.9 in threads).
    """
    raw = secrets.token_bytes(16)
    # Format as UUID-like string for backward compatibility
    hex_str = raw.hex()
    return f"{hex_str[:8]}-{hex_str[8:12]}-4{hex_str[13:16]}-{hex_str[16:20]}-{hex_str[20:]}"

__all__ = ["AuditEntry"]


@dataclass
class AuditEntry:
    """Canonical audit log entry — superset of all 9 legacy AuditEntry variants.

    Every field except ``entry_id`` has a default value so that code that
    previously constructed a narrower AuditEntry variant continues to work.

    Attributes:
        entry_id: Unique identifier for this entry (primary key).
        operation: Type/name of the operation being audited.
        timestamp: When the operation occurred (UTC).
        status: Lifecycle status — PENDING, COMPLETED, FAILED, etc.
        details: Arbitrary key/value context (replaces ``metadata`` from some variants).
        message: Human-readable description of the audit event.
        ac_id: AC marker ID linking this entry to an orchestrator AC session.
        orchestrator_id: Canonical ID of the orchestrator that produced the entry.
        duration_ms: Elapsed time of the operation in milliseconds.
        error_message: Error detail on failure (``None`` on success).
        domain: Domain context (e.g. ``"knowledge"``, ``"planning"``).
        entity_id: ID of the primary entity being audited.
        entity_type: Type name of the primary entity (e.g. ``"Orchestrator"``).
        actor: User or service account that triggered the operation.
        action: Verb form of the operation (e.g. ``"read"``, ``"write"``, ``"delete"``).
        key: Secret key name — used by secrets-domain audit entries.
        success: Whether the operation succeeded (used by secrets audit trail).
        entry_hash: Cryptographic hash of this entry for chain integrity.
        previous_hash: Hash of the preceding entry in the chain.
        description: Longer free-form description (domain_brain_models variant).
        source_ip: Source IP address — used by secrets/management audit entries.
        previous_value: Value before a mutation (domain_brain_models variant).
        new_value: Value after a mutation (domain_brain_models variant).
    """

    # ── Mandatory ──────────────────────────────────────────────────────────
    entry_id: str = field(default_factory=_thread_safe_uuid4)

    # ── Core audit fields ──────────────────────────────────────────────────
    operation: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "PENDING"

    # ── Content ────────────────────────────────────────────────────────────
    details: dict[str, Any] = field(default_factory=dict)
    message: str = ""

    # ── Orchestrator tracking ───────────────────────────────────────────────
    ac_id: str = ""
    orchestrator_id: str = ""
    duration_ms: int = 0
    error_message: Optional[str] = None

    # ── Domain context ─────────────────────────────────────────────────────
    domain: str = ""
    entity_id: Optional[str] = None
    entity_type: str = ""

    # ── Actor / secrets ────────────────────────────────────────────────────
    actor: str = "system"
    action: str = ""
    key: str = ""
    success: bool = True
    source_ip: Optional[str] = None

    # ── Chain integrity ────────────────────────────────────────────────────
    entry_hash: str = ""
    previous_hash: str = ""

    # ── Extended description ───────────────────────────────────────────────
    description: str = ""
    previous_value: Optional[dict[str, Any]] = None
    new_value: Optional[dict[str, Any]] = None

    # ── Legacy / audit_db compat ───────────────────────────────────────────
    event_type: str = ""        # DB audit event type (audit_db.py compatibility)
    metadata: Optional[dict[str, Any]] = None  # Legacy metadata field (audit_db.py compatibility)

    # ── Backward-compat shims ──────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary.

        Provides backward compatibility for callers that relied on the
        ``to_dict()`` method present on the ``audit_db`` and ``api`` variants.

        Returns:
            Dictionary representation of the audit entry.
        """
        return {
            "entry_id": self.entry_id,
            "operation": self.operation,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "status": self.status,
            "details": self.details,
            "message": self.message,
            "ac_id": self.ac_id,
            "orchestrator_id": self.orchestrator_id,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "domain": self.domain,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "actor": self.actor,
            "action": self.action,
            "key": self.key,
            "success": self.success,
            "source_ip": self.source_ip,
            "entry_hash": self.entry_hash,
            "previous_hash": self.previous_hash,
            "description": self.description,
            "previous_value": self.previous_value,
            "new_value": self.new_value,
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like attribute access.

        Provides backward compatibility for the ``intent_reflection_protocol``
        variant that exposed ``get()`` for dict-style access.

        Args:
            key: Attribute name to retrieve.
            default: Value to return if the attribute does not exist.

        Returns:
            Attribute value or *default*.
        """
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        """Dict-like subscript access.

        Args:
            key: Attribute name.

        Returns:
            Attribute value.

        Raises:
            KeyError: If *key* is not an attribute of this entry.
        """
        value = self.get(key)
        if value is None and not hasattr(self, key):
            raise KeyError(key)
        return value

    def __contains__(self, key: object) -> bool:
        """Dict-like ``in`` operator — checks if *key* is a known field.

        Args:
            key: Attribute name to test.

        Returns:
            True if *key* is an attribute of this dataclass.
        """
        return hasattr(self, key)


# AC_COMPLETE: AC-AUDIT-MODELS-5901 (canonical module) ✅
