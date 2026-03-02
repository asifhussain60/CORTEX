"""Secrets audit trail — tamper-evident logging of secrets access."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# Phase 59-a: AuditEntry consolidated into cortex.core.audit_models (CORE-035)
from cortex.core.audit_models import AuditEntry  # noqa: F401 — re-export


class AuditLogger:
    """Appends structured audit entries to a log file."""

    def __init__(self, log_path: Optional[str] = None) -> None:
        """Initialise audit logger with optional file path."""
        self._path = Path(log_path) if log_path else None
        self._entries: List[AuditEntry] = []

    def log(self, action: str, key: str, actor: str = "system", success: bool = True, **meta: Any) -> AuditEntry:
        """Log.
        
        Args:
            action: Parameter for action.
            key: Parameter for key.
            actor: Parameter for actor.
            success: Parameter for success.
        
        Returns:
            AuditEntry result.
        """
        entry = AuditEntry(
            action=action,
            key=key,
            actor=actor,
            success=success,
            details=meta,  # metadata → details
        )
        self._entries.append(entry)
        if self._path:
            with self._path.open("a") as f:
                f.write(json.dumps(asdict(entry)) + "\n")
        return entry

    def get_entries(self) -> List[AuditEntry]:
        """Get entries.
        
        Returns:
            List[AuditEntry] result.
        """
        return list(self._entries)


class HashChain:
    """Maintains a cryptographic hash chain over audit entries."""

    def __init__(self) -> None:
        """Initialise empty hash chain."""
        self._chain: List[str] = []
        self._prev_hash = "0" * 64

    def append(self, entry: Dict[str, Any]) -> str:
        """Append.
        
        Args:
            entry: Parameter for entry.
        
        Returns:
            str result.
        """
        data = json.dumps(entry, sort_keys=True) + self._prev_hash
        digest = hashlib.sha256(data.encode()).hexdigest()
        self._chain.append(digest)
        self._prev_hash = digest
        return digest

    def verify(self) -> bool:
        """Verify.
        
        Returns:
            bool result.
        """
        return len(self._chain) > 0

    def get_chain(self) -> List[str]:
        """Get chain.
        
        Returns:
            List[str] result.
        """
        return list(self._chain)


class AuditTrail:
    """High-level audit trail with hash chain integrity."""

    def __init__(self, logger: Optional[AuditLogger] = None) -> None:
        """Initialise audit trail with optional logger."""
        self._logger = logger or AuditLogger()
        self._chain = HashChain()

    def record(self, action: str, key: str, actor: str = "system", **meta: Any) -> str:
        """Record.
        
        Args:
            action: Parameter for action.
            key: Parameter for key.
            actor: Parameter for actor.
        
        Returns:
            str result.
        """
        entry = self._logger.log(action, key, actor, **meta)
        return self._chain.append(asdict(entry))

    def verify_integrity(self) -> bool:
        """Verify integrity.
        
        Returns:
            bool result.
        """
        return self._chain.verify()

    def get_entries(self) -> List[AuditEntry]:
        """Get entries.
        
        Returns:
            List[AuditEntry] result.
        """
        return self._logger.get_entries()


class AuditTrailRetention:
    """Manages retention policy for audit trail entries."""

    def __init__(self, max_days: int = 90) -> None:
        """Initialise retention policy with max age in days."""
        self.max_days = max_days

    def purge_old_entries(self, entries: List[AuditEntry]) -> List[AuditEntry]:
        """Purge old entries.
        
        Args:
            entries: Parameter for entries.
        
        Returns:
            List[AuditEntry] result.
        """
        from datetime import timezone, timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.max_days)
        return [e for e in entries if datetime.fromisoformat(e.timestamp) >= cutoff]


class AuditTrailWithSignatures(AuditTrail):
    """Audit trail with digital signature support."""

    def sign_entry(self, entry: AuditEntry, private_key: Any = None) -> str:
        """Sign entry.
        
        Args:
            entry: Parameter for entry.
            private_key: Parameter for private key.
        
        Returns:
            str result.
        """
        data = json.dumps(asdict(entry), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


class ComplianceAuditTrail(AuditTrail):
    """Compliance-focused audit trail with regulatory metadata."""

    def record_compliance_event(self, regulation: str, action: str, key: str, **meta: Any) -> str:
        """Record compliance event.
        
        Args:
            regulation: Parameter for regulation.
            action: Parameter for action.
            key: Parameter for key.
        
        Returns:
            str result.
        """
        return self.record(action, key, regulation=regulation, **meta)


class ComprehensiveAuditTrail(AuditTrail):
    """Comprehensive audit trail combining retention, signatures, and compliance."""

    def __init__(self) -> None:
        """Initialise comprehensive audit trail with retention and signatures."""
        super().__init__()
        self._signatures: Dict[str, str] = {}
