"""Tier2 Governance: Audit Immutability

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any
import hashlib


class TamperStatus(Enum):
    """Tamper detection status."""
    INTACT = "intact"
    TAMPERED = "tampered"
    SUSPICIOUS = "suspicious"
    CLEAN = "clean"


@dataclass
class ImmutableRecord:
    """Immutable audit record.
    
    Attributes:
        record_id: Unique record identifier
        content: Record content
        signature: Content signature for tamper detection
        tamper_status: Current tamper status
        content_hash: Hash of original content
    """
    record_id: str
    content: str
    signature: str
    tamper_status: TamperStatus = TamperStatus.INTACT
    content_hash: str = field(default="", init=False)
    
    def __post_init__(self):
        """Initialize content hash."""
        self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()


class AuditImmutability:
    """Audit immutability enforcer.
    
    Manages immutable audit records with tamper detection.
    
    Attributes:
        records: Dictionary of immutable records
        enabled: Whether immutability enforcement is enabled
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize immutability manager.
        
        Args:
            enabled: Enable immutability enforcement
        """
        self.enabled = enabled
        self.records: Dict[str, ImmutableRecord] = {}
    
    def create_record(
        self,
        record_id: str,
        content: str,
        signature: str
    ) -> ImmutableRecord:
        """Create immutable record.
        
        Args:
            record_id: Unique record identifier
            content: Record content
            signature: Content signature
            
        Returns:
            ImmutableRecord instance
        """
        record = ImmutableRecord(
            record_id=record_id,
            content=content,
            signature=signature,
            tamper_status=TamperStatus.INTACT
        )
        self.records[record_id] = record
        return record
    
    def verify_record(self, record_id: str) -> TamperStatus:
        """Verify record integrity.
        
        Args:
            record_id: Record to verify
            
        Returns:
            TamperStatus indicating integrity
        """
        if record_id not in self.records:
            return TamperStatus.SUSPICIOUS
        
        record = self.records[record_id]
        current_hash = hashlib.sha256(record.content.encode()).hexdigest()
        
        if current_hash == record.content_hash:
            record.tamper_status = TamperStatus.INTACT
            return TamperStatus.INTACT
        else:
            record.tamper_status = TamperStatus.TAMPERED
            return TamperStatus.TAMPERED
    
    def get_immutability_report(self) -> Dict[str, Any]:
        """Get immutability report.
        
        Returns:
            Dictionary with integrity metrics
        """
        if not self.records:
            return {
                "total_records": 0,
                "intact": 0,
                "tampered": 0,
                "suspicious": 0,
            }
        
        # Verify all records
        for record_id in self.records:
            self.verify_record(record_id)
        
        intact = sum(1 for r in self.records.values() if r.tamper_status == TamperStatus.INTACT)
        tampered = sum(1 for r in self.records.values() if r.tamper_status == TamperStatus.TAMPERED)
        suspicious = sum(1 for r in self.records.values() if r.tamper_status == TamperStatus.SUSPICIOUS)
        
        return {
            "total_records": len(self.records),
            "intact": intact,
            "tampered": tampered,
            "suspicious": suspicious,
        }
    
    def verify(self, audit_id: str) -> bool:
        """Verify audit record (backward compatibility).
        
        Args:
            audit_id: Audit record ID
            
        Returns:
            True if intact
        """
        status = self.verify_record(audit_id)
        return status == TamperStatus.INTACT


__all__ = ["TamperStatus", "ImmutableRecord", "AuditImmutability"]
