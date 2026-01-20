"""Duplicate Upload Detection: Hash-Based Deduplication (AC-DB-E01).

Prevents audit trail corruption from duplicate uploads by detecting and
skipping idempotent re-uploads of domains.
"""

import hashlib
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from cortex.brain.domain_brain.models import Domain, AuditOperationType


@dataclass
class DuplicateEntry:
    """Record of a duplicate upload detection."""

    domain_id: str
    domain_hash: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    original_upload_time: Optional[datetime] = None
    times_detected: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "domain_id": self.domain_id,
            "domain_hash": self.domain_hash,
            "detected_at": self.detected_at.isoformat(),
            "original_upload_time": (
                self.original_upload_time.isoformat()
                if self.original_upload_time
                else None
            ),
            "times_detected": self.times_detected,
        }


class DuplicateDetector:
    """Hash-based duplicate detection for domain uploads.

    Prevents idempotent re-execution by computing SHA-256 hash of serialized
    domain objects and comparing with existing entries.

    Uses mark-and-track approach:
    - First upload: compute hash, store with audit entry
    - Subsequent uploads: compare hash
    - If identical: skip UPDATE, log as duplicate
    - If different: proceed with UPSERT
    """

    def __init__(self) -> None:
        """Initialize duplicate detector."""
        self.domain_hashes: Dict[str, str] = {}  # domain_id -> hash
        self.duplicate_log: Dict[str, DuplicateEntry] = {}  # hash -> entry
        self.duplicate_uploads_prevented = 0
        self.unique_uploads_processed = 0

    def compute_domain_hash(self, domain: Domain) -> str:
        """Compute SHA-256 hash of domain object.

        Args:
            domain: Domain to hash

        Returns:
            SHA-256 hex digest of serialized domain
        """
        # Convert domain to dictionary for hashing
        domain_dict = {
            "domain_id": domain.domain_id,
            "name": domain.name,
            "description": domain.description,
            "entities": {
                eid: {
                    "entity_id": e.entity_id,
                    "name": e.name,
                    "description": e.description,
                    "entity_type": e.entity_type.value,
                    "source": e.source,
                }
                for eid, e in domain.entities.items()
            },
            "conflicts": [
                {
                    "conflict_id": c.conflict_id,
                    "attribute": c.attribute,
                    "source_values": c.source_values,
                }
                for c in domain.conflicts
            ],
        }

        # Serialize to JSON (sorted for consistency)
        serialized = json.dumps(domain_dict, sort_keys=True, default=str)

        # Compute SHA-256 hash
        return hashlib.sha256(serialized.encode()).hexdigest()

    def check_duplicate(self, domain_id: str, new_hash: str) -> bool:
        """Check if domain is a duplicate based on hash.

        Args:
            domain_id: Domain ID to check
            new_hash: Hash of new domain

        Returns:
            True if duplicate, False if new or modified
        """
        if domain_id not in self.domain_hashes:
            return False

        # Check if hash is identical
        existing_hash = self.domain_hashes[domain_id]
        return existing_hash == new_hash

    def log_duplicate(
        self,
        domain_id: str,
        domain_hash: str,
        original_upload_time: Optional[datetime] = None,
    ) -> None:
        """Log duplicate upload detection.

        Args:
            domain_id: Domain ID
            domain_hash: Hash of domain
            original_upload_time: When the original was uploaded
        """
        if domain_hash not in self.duplicate_log:
            self.duplicate_log[domain_hash] = DuplicateEntry(
                domain_id=domain_id,
                domain_hash=domain_hash,
                original_upload_time=original_upload_time,
            )
        else:
            # Increment counter for repeated duplicates
            self.duplicate_log[domain_hash].times_detected += 1

        self.duplicate_uploads_prevented += 1

    def register_upload(self, domain_id: str, domain_hash: str) -> None:
        """Register a unique upload.

        Args:
            domain_id: Domain ID
            domain_hash: Hash of domain
        """
        self.domain_hashes[domain_id] = domain_hash
        self.unique_uploads_processed += 1

    def is_duplicate(self, domain: Domain) -> bool:
        """Check if domain upload is a duplicate.

        Args:
            domain: Domain to check

        Returns:
            True if duplicate, False otherwise
        """
        new_hash = self.compute_domain_hash(domain)
        return self.check_duplicate(domain.domain_id, new_hash)

    def process_domain_upload(
        self, domain: Domain, original_upload_time: Optional[datetime] = None
    ) -> bool:
        """Process domain upload and return if it's a duplicate.

        Args:
            domain: Domain to process
            original_upload_time: When original was uploaded

        Returns:
            True if duplicate (skip UPSERT), False if new (proceed with UPSERT)
        """
        new_hash = self.compute_domain_hash(domain)

        if self.check_duplicate(domain.domain_id, new_hash):
            # Duplicate detected
            self.log_duplicate(domain.domain_id, new_hash, original_upload_time)
            return True

        # New or modified domain
        self.register_upload(domain.domain_id, new_hash)
        return False

    def get_deduplication_status(self) -> Dict[str, Any]:
        """Get deduplication status.

        Returns:
            Status dictionary
        """
        total_uploads = self.unique_uploads_processed + self.duplicate_uploads_prevented
        duplicate_rate = (
            (
                self.duplicate_uploads_prevented / total_uploads * 100
                if total_uploads > 0
                else 0
            )
        )

        return {
            "unique_uploads_processed": self.unique_uploads_processed,
            "duplicate_uploads_prevented": self.duplicate_uploads_prevented,
            "total_uploads_attempted": total_uploads,
            "duplicate_rate_percent": duplicate_rate,
            "unique_hashes_stored": len(self.domain_hashes),
            "duplicate_events_logged": len(self.duplicate_log),
        }

    def get_duplicate_log(self) -> Dict[str, Dict[str, Any]]:
        """Get complete duplicate log.

        Returns:
            Dictionary of duplicate entries
        """
        return {
            domain_hash: entry.to_dict()
            for domain_hash, entry in self.duplicate_log.items()
        }

    def clear_duplicates(self) -> int:
        """Clear duplicate log (e.g., for new archival cycle).

        Returns:
            Number of duplicates cleared
        """
        count = len(self.duplicate_log)
        self.duplicate_log.clear()
        return count
