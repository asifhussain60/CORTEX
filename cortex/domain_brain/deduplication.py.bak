"""Deduplication - Hash-Based Duplicate Upload Detection.

Author: CORTEX Framework
Implements: AC-DB-E01 (Duplicate Upload Detection)
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class DuplicateEntry:
    """Duplicate entry record.
    
    Attributes:
        entry_id: Unique entry identifier.
        duplicate_of: ID of the original entry.
        confidence: Confidence score for match.
        detected_at: When duplicate was detected.
    """
    entry_id: str
    duplicate_of: str
    confidence: float = 0.9
    detected_at: Optional[datetime] = None


class DuplicateDetector:
    """Detect duplicate domain uploads using hash-based deduplication.
    
    Uses SHA-256 hashing to identify identical domain uploads and
    prevent unnecessary processing of duplicate data.
    
    Attributes:
        threshold: Similarity threshold for detection.
    """
    
    def __init__(self, threshold: float = 0.9) -> None:
        """Initialize duplicate detector.
        
        Args:
            threshold: Similarity threshold for fuzzy matching.
        """
        self.threshold = threshold
        self._hash_store: Dict[str, Dict[str, Any]] = {}  # hash -> {domain_id, first_seen}
        self._duplicate_log: Dict[str, Dict[str, Any]] = {}  # hash -> {domain_id, times_detected}
        self.unique_uploads_processed: int = 0
        self.duplicate_uploads_prevented: int = 0
        self._total_uploads: int = 0
    
    def detect(self, item1: str, item2: str) -> bool:
        """Detect if items are duplicates.
        
        Args:
            item1: First item to compare.
            item2: Second item to compare.
            
        Returns:
            True if items are duplicates.
        """
        return item1 == item2
    
    def compute_domain_hash(self, domain: Any) -> str:
        """Compute SHA-256 hash for a domain.
        
        Args:
            domain: Domain object to hash.
            
        Returns:
            64-character hexadecimal hash string.
        """
        # Build canonical representation
        data = {
            "domain_id": getattr(domain, "domain_id", ""),
            "name": getattr(domain, "name", ""),
            "description": getattr(domain, "description", ""),
        }
        
        # Add entities if present
        entities = getattr(domain, "entities", {})
        if entities:
            entity_data = []
            for entity_id, entity in sorted(entities.items()):
                entity_dict = {
                    "entity_id": getattr(entity, "entity_id", entity_id),
                    "entity_type": str(getattr(entity, "entity_type", "")),
                    "name": getattr(entity, "name", ""),
                    "description": getattr(entity, "description", ""),
                    "source": getattr(entity, "source", ""),
                }
                entity_data.append(entity_dict)
            data["entities"] = entity_data
        
        # Add conflicts if present
        conflicts = getattr(domain, "conflicts", [])
        if conflicts:
            conflict_data = []
            for conflict in conflicts:
                conflict_dict = {
                    "conflict_id": getattr(conflict, "conflict_id", ""),
                    "domain_id": getattr(conflict, "domain_id", ""),
                    "attribute": getattr(conflict, "attribute", ""),
                    "source_values": getattr(conflict, "source_values", {}),
                }
                conflict_data.append(conflict_dict)
            data["conflicts"] = conflict_data
        
        # Compute hash
        canonical = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def process_domain_upload(
        self,
        domain: Any,
        original_upload_time: Optional[datetime] = None
    ) -> bool:
        """Process a domain upload and check for duplicates.
        
        Args:
            domain: Domain object being uploaded.
            original_upload_time: Optional timestamp for first upload.
            
        Returns:
            True if this is a duplicate, False if unique.
        """
        self._total_uploads += 1
        domain_hash = self.compute_domain_hash(domain)
        domain_id = getattr(domain, "domain_id", "unknown")
        
        if domain_hash in self._hash_store:
            # Duplicate detected
            self.duplicate_uploads_prevented += 1
            
            # Log duplicate
            if domain_hash not in self._duplicate_log:
                self._duplicate_log[domain_hash] = {
                    "domain_id": domain_id,
                    "times_detected": 0,
                    "first_detected": datetime.utcnow().isoformat()
                }
            self._duplicate_log[domain_hash]["times_detected"] += 1
            
            return True
        else:
            # Unique upload
            self.unique_uploads_processed += 1
            self._hash_store[domain_hash] = {
                "domain_id": domain_id,
                "first_seen": (original_upload_time or datetime.utcnow()).isoformat()
            }
            return False
    
    def log_duplicate(
        self,
        domain_id: str,
        hash_value: str,
        original_time: datetime
    ) -> None:
        """Log a duplicate detection event.
        
        Args:
            domain_id: Domain that was duplicated.
            hash_value: Hash of the duplicate.
            original_time: When original was first uploaded.
        """
        if hash_value not in self._duplicate_log:
            self._duplicate_log[hash_value] = {
                "domain_id": domain_id,
                "times_detected": 0,
                "original_time": original_time.isoformat()
            }
        self._duplicate_log[hash_value]["times_detected"] += 1
    
    def get_duplicate_log(self) -> Dict[str, Dict[str, Any]]:
        """Get the duplicate detection log.
        
        Returns:
            Dictionary of hash -> duplicate info.
        """
        return self._duplicate_log.copy()
    
    def clear_duplicates(self) -> int:
        """Clear all duplicate log entries.
        
        Returns:
            Number of entries cleared.
        """
        count = len(self._duplicate_log)
        self._duplicate_log.clear()
        return count
    
    def get_deduplication_status(self) -> Dict[str, Any]:
        """Get deduplication status and metrics.
        
        Returns:
            Dictionary with status information.
        """
        total = self._total_uploads
        dup_rate = (
            (self.duplicate_uploads_prevented / total * 100)
            if total > 0 else 0.0
        )
        
        return {
            "unique_uploads_processed": self.unique_uploads_processed,
            "duplicate_uploads_prevented": self.duplicate_uploads_prevented,
            "total_uploads_attempted": total,
            "duplicate_rate_percent": dup_rate,
            "unique_hashes_stored": len(self._hash_store),
            "duplicate_events_logged": len(self._duplicate_log)
        }


__all__ = ["DuplicateDetector", "DuplicateEntry"]
