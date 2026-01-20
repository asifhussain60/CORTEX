"""
CORE-027c: Audit Immutability & Tamper Detection
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import hashlib


class TamperStatus(Enum):
    """Status of tamper detection."""
    INTACT = "intact"
    SUSPICIOUS = "suspicious"
    TAMPERED = "tampered"


@dataclass
class AuditRecord:
    """Immutable audit record."""
    record_id: str
    content: str
    timestamp: datetime
    content_hash: str
    signature: str
    tamper_status: TamperStatus = TamperStatus.INTACT


class AuditImmutability:
    """Manages immutable audit records with tamper detection."""
    
    def __init__(self):
        """Initialize audit immutability manager."""
        self.records: Dict[str, AuditRecord] = {}
    
    def create_record(
        self,
        record_id: str,
        content: str,
        signature: str
    ) -> AuditRecord:
        """Create immutable audit record."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        record = AuditRecord(
            record_id=record_id,
            content=content,
            timestamp=datetime.utcnow(),
            content_hash=content_hash,
            signature=signature,
            tamper_status=TamperStatus.INTACT
        )
        
        self.records[record_id] = record
        return record
    
    def verify_record(self, record_id: str) -> TamperStatus:
        """Verify record integrity."""
        if record_id not in self.records:
            return TamperStatus.TAMPERED
        
        record = self.records[record_id]
        current_hash = hashlib.sha256(record.content.encode()).hexdigest()
        
        if current_hash != record.content_hash:
            record.tamper_status = TamperStatus.TAMPERED
            return TamperStatus.TAMPERED
        
        return TamperStatus.INTACT
    
    def get_immutability_report(self) -> Dict[str, Any]:
        """Get immutability report."""
        if not self.records:
            return {"total_records": 0, "intact": 0, "tampered": 0}
        
        intact_count = sum(1 for r in self.records.values() if self.verify_record(r.record_id) == TamperStatus.INTACT)
        
        return {
            "total_records": len(self.records),
            "intact": intact_count,
            "tampered": len(self.records) - intact_count,
        }
