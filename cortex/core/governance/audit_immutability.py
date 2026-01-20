"""Audit immutability and integrity verification."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib


class AuditEntry:
    """Immutable audit entry."""
    
    def __init__(self, action: str, actor: str, resource: str, details: Dict[str, Any]):
        self.action = action
        self.actor = actor
        self.resource = resource
        self.details = details
        self.timestamp = datetime.now()
        self.hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute entry hash for integrity."""
        data = f"{self.action}{self.actor}{self.resource}{self.timestamp}".encode()
        return hashlib.sha256(data).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify entry integrity."""
        return self.hash == self._compute_hash()


class AuditImmutability:
    """Enforce audit log immutability."""
    
    def __init__(self):
        self.entries: Dict[str, AuditEntry] = {}
        self.sequence: List[str] = []
    
    def log(self, action: str, actor: str, resource: str, details: Dict[str, Any]) -> str:
        """Log immutable audit entry."""
        entry = AuditEntry(action, actor, resource, details)
        entry_id = f"{len(self.entries)}:{entry.hash[:16]}"
        self.entries[entry_id] = entry
        self.sequence.append(entry_id)
        return entry_id
    
    def verify_chain(self) -> bool:
        """Verify audit chain integrity."""
        for entry_id in self.sequence:
            if entry_id not in self.entries:
                return False
            if not self.entries[entry_id].verify_integrity():
                return False
        return True
    
    def get_entries(self, actor: Optional[str] = None) -> List[AuditEntry]:
        """Get audit entries."""
        if actor:
            return [self.entries[eid] for eid in self.sequence if self.entries[eid].actor == actor]
        return [self.entries[eid] for eid in self.sequence]
