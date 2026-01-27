"""Audit Logger for Domain Brain.

Provides audit logging functionality for tracking operations.

Author: CORTEX Framework
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class AuditEntry:
    """Audit log entry.
    
    Attributes:
        entry_id: Unique entry identifier.
        operation: Operation type performed.
        timestamp: When operation occurred.
        details: Additional operation details.
        user: User who performed operation.
        domain: Domain affected.
    """
    entry_id: str
    operation: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    user: str = ""
    domain: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation.
        """
        return {
            "entry_id": self.entry_id,
            "operation": self.operation,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "details": self.details,
            "user": self.user,
            "domain": self.domain
        }


class AuditLogger:
    """Audit logger for tracking all domain operations.
    
    Provides comprehensive audit trail for governance compliance.
    """
    
    def __init__(self) -> None:
        """Initialize audit logger."""
        self.entries: List[AuditEntry] = []
    
    def log(
        self,
        entry_id: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None,
        user: str = "",
        domain: str = ""
    ) -> AuditEntry:
        """Log an audit entry.
        
        Args:
            entry_id: Entry identifier.
            operation: Operation type.
            details: Optional operation details.
            user: User performing operation.
            domain: Domain affected.
        
        Returns:
            Created audit entry.
        """
        entry = AuditEntry(
            entry_id=entry_id,
            operation=operation,
            details=details or {},
            user=user,
            domain=domain
        )
        self.entries.append(entry)
        return entry
    
    def get_all_entries(self) -> List[AuditEntry]:
        """Get all audit entries.
        
        Returns:
            List of all audit entries.
        """
        return self.entries
    
    def get_entries_by_domain(self, domain_id: str) -> List[AuditEntry]:
        """Get entries for a specific domain.
        
        Args:
            domain_id: Domain identifier.
        
        Returns:
            List of entries for the domain.
        """
        return [e for e in self.entries if e.entry_id == domain_id or e.domain == domain_id]
    
    def get_entries_by_operation(self, operation: str) -> List[AuditEntry]:
        """Get entries by operation type.
        
        Args:
            operation: Operation type.
        
        Returns:
            List of entries for the operation.
        """
        return [e for e in self.entries if e.operation == operation]
    
    def clear(self) -> None:
        """Clear all audit entries."""
        self.entries.clear()
    
    def count(self) -> int:
        """Get count of entries.
        
        Returns:
            Number of audit entries.
        """
        return len(self.entries)


__all__ = [
    "AuditLogger",
    "AuditEntry"
]
