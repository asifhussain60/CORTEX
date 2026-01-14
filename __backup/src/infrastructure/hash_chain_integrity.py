"""
AC-AUDIT-007: Hash Chain Integrity

Implements cryptographic hash chain for tamper detection.
Each audit event contains hash of previous event, creating tamper-evident audit trail.

Hash chain flow:
1. Event 1: sha256("content") -> hash1
2. Event 2: sha256("content" + hash1) -> hash2  (links to previous)
3. Event 3: sha256("content" + hash2) -> hash3  (links to Event 2)
...

Any tampering breaks the chain and is immediately detectable.

Status: COMPLETE
Author: GitHub Copilot
Version: 1.0.0
"""

import hashlib
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict

from src.utils.path_utils import audit_logs_path, project_root


@dataclass
class HashChainEvent:
    """Represents an event in the hash chain."""
    event_id: int
    timestamp: str
    level: str
    category: str
    message: str
    event_hash: str  # SHA256 hash of this event's content
    prev_event_hash: str  # SHA256 hash of previous event's content
    chain_valid: bool = True  # Whether chain link is valid


class HashChainIntegrity:
    """
    Manages cryptographic hash chain for audit event integrity.
    Enables detection of any audit log tampering.
    """
    
    HASH_ALGORITHM = "sha256"
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize hash chain system.
        
        Args:
            db_path: Path to audit database
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        try:
            db_dir = audit_logs_path()
        except Exception:
            db_dir = Path(project_root()) / "cortex-brain" / "audit-logs"
        
        self.db_path = db_path or str(db_dir / "audit_chain.db")
    
    @staticmethod
    def compute_event_hash(
        timestamp: str,
        level: str,
        category: str,
        message: str,
        actor: Optional[str] = None,
        resource: Optional[str] = None
    ) -> str:
        """
        Compute SHA256 hash of event content.
        
        Args:
            timestamp: Event timestamp
            level: Log level
            category: Event category
            message: Event message
            actor: Actor performing action
            resource: Resource affected
            
        Returns:
            SHA256 hash as hex string
        """
        # Create canonical representation for hashing
        content_parts = [
            timestamp,
            level,
            category,
            message,
            actor or "",
            resource or "",
        ]
        
        content = "|".join(content_parts)
        event_hash = hashlib.sha256(content.encode()).hexdigest()
        
        return event_hash
    
    def compute_chain_hash(self, event_hash: str, prev_event_hash: str) -> str:
        """
        Compute hash linking to previous event (chain hash).
        
        Args:
            event_hash: Current event's hash
            prev_event_hash: Previous event's hash
            
        Returns:
            SHA256 hash of chain link
        """
        chain_content = f"{event_hash}|{prev_event_hash}"
        chain_hash = hashlib.sha256(chain_content.encode()).hexdigest()
        
        return chain_hash
    
    def initialize_chain_db(self) -> str:
        """
        Initialize hash chain database.
        
        Returns:
            Path to database
        """
        db_path_obj = Path(self.db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='hash_chain'
        """)
        
        if not cursor.fetchone():
            # Create hash chain table
            cursor.execute("""
                CREATE TABLE hash_chain (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    category TEXT NOT NULL,
                    message TEXT NOT NULL,
                    actor TEXT,
                    resource TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    prev_event_hash TEXT,
                    chain_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create verification index
            cursor.execute("""
                CREATE INDEX idx_chain_hash_verification
                ON hash_chain(event_id, event_hash, prev_event_hash)
            """)
            
            conn.commit()
            self.logger.info(f"Initialized hash chain database: {self.db_path}")
        
        conn.close()
        return self.db_path
    
    def append_to_chain(
        self,
        timestamp: str,
        level: str,
        category: str,
        message: str,
        actor: Optional[str] = None,
        resource: Optional[str] = None
    ) -> Dict:
        """
        Append event to hash chain.
        
        Args:
            timestamp: Event timestamp
            level: Log level
            category: Event category
            message: Event message
            actor: Actor performing action
            resource: Resource affected
            
        Returns:
            Dict with event details and hashes
        """
        self.initialize_chain_db()
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get previous event hash
            cursor.execute("""
                SELECT event_hash FROM hash_chain
                ORDER BY event_id DESC LIMIT 1
            """)
            
            prev_row = cursor.fetchone()
            prev_event_hash = prev_row["event_hash"] if prev_row else "0" * 64  # Genesis block
            
            # Compute current event hash
            event_hash = self.compute_event_hash(
                timestamp, level, category, message, actor, resource
            )
            
            # Compute chain hash (links to previous)
            chain_hash = self.compute_chain_hash(event_hash, prev_event_hash)
            
            # Insert into chain
            cursor.execute("""
                INSERT INTO hash_chain
                (timestamp, level, category, message, actor, resource,
                 event_hash, prev_event_hash, chain_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, level, category, message, actor, resource,
                event_hash, prev_event_hash, chain_hash, datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            
            # Get inserted event ID using last_insert_rowid
            event_id = cursor.lastrowid
            
            conn.close()
            
            return {
                "event_id": event_id,
                "event_hash": event_hash,
                "prev_event_hash": prev_event_hash,
                "chain_hash": chain_hash,
                "status": "appended",
            }
            
        except Exception as e:
            self.logger.error(f"Error appending to hash chain: {e}")
            return {"status": "error", "message": str(e)}
    
    def verify_chain_integrity(self) -> Tuple[bool, Dict]:
        """
        Verify entire hash chain for tampering.
        
        Returns:
            Tuple of (is_valid, verification_results)
        """
        try:
            # Ensure database is initialized
            self.initialize_chain_db()
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all events in chain order
            cursor.execute("""
                SELECT * FROM hash_chain
                ORDER BY event_id ASC
            """)
            
            events = cursor.fetchall()
            conn.close()
            
            if not events:
                return True, {"message": "Chain is empty", "events_verified": 0}
            
            # Genesis block verification
            first_event = events[0]
            if first_event["prev_event_hash"] != "0" * 64:
                return False, {
                    "message": "Genesis block has invalid previous hash",
                    "events_verified": 0
                }
            
            # Recompute hash for genesis block
            first_hash = self.compute_event_hash(
                first_event["timestamp"],
                first_event["level"],
                first_event["category"],
                first_event["message"],
                first_event["actor"],
                first_event["resource"]
            )
            
            if first_hash != first_event["event_hash"]:
                return False, {
                    "message": f"Genesis block hash mismatch at event 1",
                    "events_verified": 0,
                    "details": f"Expected {first_hash}, got {first_event['event_hash']}"
                }
            
            # Verify chain links
            for i in range(1, len(events)):
                curr = events[i]
                prev = events[i - 1]
                
                # Verify event hash
                curr_hash = self.compute_event_hash(
                    curr["timestamp"],
                    curr["level"],
                    curr["category"],
                    curr["message"],
                    curr["actor"],
                    curr["resource"]
                )
                
                if curr_hash != curr["event_hash"]:
                    return False, {
                        "message": f"Event hash mismatch at event {i + 1}",
                        "events_verified": i,
                        "details": f"Expected {curr_hash}, got {curr['event_hash']}"
                    }
                
                # Verify previous hash reference
                if curr["prev_event_hash"] != prev["event_hash"]:
                    return False, {
                        "message": f"Chain link broken at event {i + 1}",
                        "events_verified": i,
                        "details": f"Previous hash mismatch"
                    }
                
                # Verify chain hash
                expected_chain_hash = self.compute_chain_hash(
                    curr["event_hash"],
                    curr["prev_event_hash"]
                )
                
                if expected_chain_hash != curr["chain_hash"]:
                    return False, {
                        "message": f"Chain hash mismatch at event {i + 1}",
                        "events_verified": i,
                        "details": f"Expected {expected_chain_hash}, got {curr['chain_hash']}"
                    }
            
            return True, {
                "message": "Chain integrity verified",
                "events_verified": len(events),
                "chain_valid": True
            }
            
        except Exception as e:
            self.logger.error(f"Error verifying chain integrity: {e}")
            return False, {"message": f"Error: {e}"}
    
    def get_chain_stats(self) -> Dict:
        """
        Get statistics about the hash chain.
        
        Returns:
            Dict with chain statistics
        """
        try:
            # Make sure database exists
            self.initialize_chain_db()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM hash_chain")
            result = cursor.fetchone()
            count = result[0] if result else 0
            
            cursor.execute("""
                SELECT MIN(created_at) as first_event, MAX(created_at) as last_event
                FROM hash_chain
            """)
            row = cursor.fetchone()
            
            conn.close()
            
            return {
                "total_events": count,
                "first_event": row[0] if row and row[0] else None,
                "last_event": row[1] if row and row[1] else None,
                "status": "active"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting chain stats: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_event_chain(self, event_id: int) -> List[Dict]:
        """
        Get chain of events leading to specific event (ancestry).
        
        Args:
            event_id: Event ID to trace back
            
        Returns:
            List of events from genesis to target
        """
        chain = []
        
        try:
            if not Path(self.db_path).exists():
                return chain
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get target event
            cursor.execute("""
                SELECT * FROM hash_chain WHERE event_id = ?
            """, (event_id,))
            
            target = cursor.fetchone()
            if not target:
                return chain
            
            # Trace back to genesis
            current = target
            while current:
                chain.insert(0, dict(current))
                
                if current["prev_event_hash"] == "0" * 64:
                    break  # Reached genesis
                
                cursor.execute("""
                    SELECT * FROM hash_chain WHERE event_hash = ?
                """, (current["prev_event_hash"],))
                
                current = cursor.fetchone()
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error getting event chain: {e}")
        
        return chain
