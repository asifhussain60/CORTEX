"""
Concurrent Audit Hash Chain Implementation (AC-STATE-002-03).

Ensures audit log hash chain remains valid under concurrent writes through
atomic append-only operations, background verification, and automatic repair.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import hashlib
import json
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class HashChainMetrics:
    """Metrics for hash chain operations."""
    total_appends: int = 0
    verifications: int = 0
    breaks_detected: int = 0


class HashChainBroken(Exception):
    """Raised when hash chain integrity check fails."""
    pass


class AuditHashChain:
    """
    Thread-safe audit log with hash chain integrity.
    
    Provides atomic append-only operations, concurrent integrity verification,
    and automatic chain repair capabilities.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize audit hash chain.
        
        Args:
            db_path: Path to SQLite database
        """
        self._db_path = db_path
        self._lock = threading.RLock()  # Recursive lock for nested operations
        self._metrics = HashChainMetrics()
        self._verifier_thread: Optional[threading.Thread] = None
        self._stop_verifier = threading.Event()
    
    def append(self, action: str, data: Dict[str, Any]) -> int:
        """
        Append entry to audit log with hash chain linkage.
        
        Args:
            action: Action type/name
            data: Action data (will be JSON serialized)
            
        Returns:
            ID of appended entry
        """
        with self._lock:  # Serialize appends for hash chain consistency
            conn = sqlite3.connect(self._db_path)
            
            # Get previous hash
            cursor = conn.execute(
                "SELECT hash FROM audit_log ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            prev_hash = row[0] if row else None
            
            # Compute entry hash
            timestamp = datetime.now(timezone.utc).isoformat()
            data_json = json.dumps(data, sort_keys=True)
            
            hash_input = f"{timestamp}|{action}|{data_json}|{prev_hash or ''}"
            entry_hash = hashlib.sha256(hash_input.encode()).hexdigest()
            
            # Insert with atomic transaction
            cursor = conn.execute(
                """
                INSERT INTO audit_log (timestamp, action, data, hash, prev_hash)
                VALUES (?, ?, ?, ?, ?)
                """,
                (timestamp, action, data_json, entry_hash, prev_hash),
            )
            entry_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self._metrics.total_appends += 1
            return entry_id
    
    def verify_integrity(self, raise_on_error: bool = False) -> bool:
        """
        Verify complete hash chain integrity.
        
        Args:
            raise_on_error: If True, raise exception on break
            
        Returns:
            True if chain is valid
            
        Raises:
            HashChainBroken: If chain invalid and raise_on_error=True
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.execute(
            "SELECT id, timestamp, action, data, hash, prev_hash FROM audit_log ORDER BY id"
        )
        
        prev_hash = None
        for row in cursor:
            entry_id, timestamp, action, data, stored_hash, expected_prev = row
            
            # Verify prev_hash linkage
            if prev_hash != expected_prev:
                conn.close()
                self._metrics.breaks_detected += 1
                if raise_on_error:
                    raise HashChainBroken(
                        f"Entry {entry_id}: prev_hash mismatch (expected {prev_hash}, got {expected_prev})"
                    )
                return False
            
            # Recompute hash
            hash_input = f"{timestamp}|{action}|{data}|{prev_hash or ''}"
            computed_hash = hashlib.sha256(hash_input.encode()).hexdigest()
            
            if computed_hash != stored_hash:
                conn.close()
                self._metrics.breaks_detected += 1
                if raise_on_error:
                    raise HashChainBroken(
                        f"Entry {entry_id}: hash mismatch (expected {computed_hash}, got {stored_hash})"
                    )
                return False
            
            prev_hash = stored_hash
        
        conn.close()
        self._metrics.verifications += 1
        return True
    
    def repair_from_break(self) -> int:
        """
        Repair hash chain from detected break point.
        
        Returns:
            Number of entries repaired
        """
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.execute(
                "SELECT id, timestamp, action, data, prev_hash FROM audit_log ORDER BY id"
            )
            
            repaired = 0
            prev_hash = None
            
            for row in cursor:
                entry_id, timestamp, action, data, expected_prev = row
                
                # Recompute correct hash
                hash_input = f"{timestamp}|{action}|{data}|{prev_hash or ''}"
                correct_hash = hashlib.sha256(hash_input.encode()).hexdigest()
                
                # Update if needed
                conn.execute(
                    "UPDATE audit_log SET hash = ?, prev_hash = ? WHERE id = ?",
                    (correct_hash, prev_hash, entry_id),
                )
                
                prev_hash = correct_hash
                repaired += 1
            
            conn.commit()
            conn.close()
            return repaired
    
    def get_entry(self, entry_id: int) -> Dict[str, Any]:
        """Get audit log entry by ID."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM audit_log WHERE id = ?", (entry_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise ValueError(f"Entry {entry_id} not found")
        
        return dict(row)
    
    def get_chain_length(self) -> int:
        """Get total number of entries in chain."""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM audit_log")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def start_background_verification(self, interval: float = 60.0) -> None:
        """
        Start background integrity verification thread.
        
        Args:
            interval: Verification interval in seconds
        """
        if self._verifier_thread and self._verifier_thread.is_alive():
            return  # Already running
        
        self._stop_verifier.clear()
        
        def verifier():
            while not self._stop_verifier.wait(interval):
                try:
                    self.verify_integrity()
                except Exception:
                    pass  # Log errors in production
        
        self._verifier_thread = threading.Thread(target=verifier, daemon=True)
        self._verifier_thread.start()
    
    def stop_background_verification(self) -> None:
        """Stop background verification thread."""
        self._stop_verifier.set()
        if self._verifier_thread:
            self._verifier_thread.join(timeout=5.0)
    
    def get_metrics(self) -> Dict[str, int]:
        """Get hash chain metrics."""
        return {
            "total_appends": self._metrics.total_appends,
            "verifications": self._metrics.verifications,
            "breaks_detected": self._metrics.breaks_detected,
        }
