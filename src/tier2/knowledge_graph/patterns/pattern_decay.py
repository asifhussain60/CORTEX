"""
Pattern Decay Module

Implements confidence decay based on access patterns (Governance Rule #12).

Decay Logic:
    - Patterns unused for >60 days start decaying
    - Decay rate: 1% per day
    - Minimum confidence: 0.3 (delete below this)
    - Pinned patterns: immune to decay

Responsibilities:
    - Calculate decay for patterns
    - Apply decay adjustments
    - Delete low-confidence patterns
    - Log decay operations (audit trail)

Performance Targets:
    - Decay calculation: <5ms per pattern
    - Batch decay (1000 patterns): <500ms
    - Cleanup operation: <200ms

Example:
    >>> from tier2.knowledge_graph.patterns.pattern_decay import PatternDecay
    >>> decay = PatternDecay(db)
    >>> results = decay.apply_decay()
    >>> print(f"Decayed: {results['decayed']}, Deleted: {results['deleted']}")
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json


class PatternDecay:
    """
    Manages confidence decay for patterns.
    
    Implements time-based decay algorithm that reduces confidence
    for patterns that haven't been accessed recently.
    """
    
    # Decay configuration (Governance Rule #12)
    DECAY_RATE = 0.01  # 1% per day
    DECAY_THRESHOLD_DAYS = 60  # Days before decay starts
    MIN_CONFIDENCE = 0.3  # Delete below this
    
    def __init__(self, db):
        """
        Initialize Pattern Decay manager.
        
        Args:
            db: DatabaseConnection instance
        """
        self.db = db
    
    def calculate_decay(
        self,
        pattern_id: str,
        as_of_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate decay for a single pattern (without applying it).
        
        Args:
            pattern_id: Pattern to calculate decay for
            as_of_date: Date to calculate decay from (default: now)
        
        Returns:
            Dictionary with:
                - pattern_id
                - current_confidence
                - days_since_access
                - decay_amount
                - new_confidence
                - should_delete
        
        Performance: <5ms
        """
        if as_of_date is None:
            as_of_date = datetime.now()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get pattern data
        cursor.execute("""
            SELECT confidence, last_accessed, is_pinned
            FROM patterns
            WHERE pattern_id = ?
        """, (pattern_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {
                "pattern_id": pattern_id,
                "error": "Pattern not found"
            }
        
        current_confidence = row[0]
        last_accessed = datetime.fromisoformat(row[1])
        is_pinned = bool(row[2])
        
        # Calculate days since last access
        days_since_access = (as_of_date - last_accessed).days
        days_to_decay = max(0, days_since_access - self.DECAY_THRESHOLD_DAYS)
        
        # No decay if pinned or within threshold
        if is_pinned or days_to_decay == 0:
            return {
                "pattern_id": pattern_id,
                "current_confidence": current_confidence,
                "days_since_access": days_since_access,
                "decay_amount": 0.0,
                "new_confidence": current_confidence,
                "should_delete": False,
                "reason": "Pinned" if is_pinned else "Within threshold"
            }
        
        # Calculate decay
        decay_amount = self.DECAY_RATE * days_to_decay
        new_confidence = max(0.0, current_confidence - decay_amount)
        should_delete = new_confidence < self.MIN_CONFIDENCE
        
        return {
            "pattern_id": pattern_id,
            "current_confidence": current_confidence,
            "days_since_access": days_since_access,
            "decay_amount": decay_amount,
            "new_confidence": new_confidence,
            "should_delete": should_delete,
            "reason": f"{days_to_decay} days since last access"
        }
    
    def apply_decay(self) -> Dict[str, Any]:
        """
        Apply decay to all eligible patterns.
        
        Process:
        1. Find patterns eligible for decay (not pinned, >60 days old)
        2. Calculate decay for each
        3. Update confidence or delete if below minimum
        4. Log all operations
        
        Returns:
            Dictionary with:
                - patterns_checked: Total patterns evaluated
                - patterns_decayed: Patterns with confidence reduced
                - patterns_deleted: Patterns removed (confidence < MIN_CONFIDENCE)
                - decay_log_entries: Audit trail records created
        
        Performance: <500ms for 1000 patterns
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now()
        decay_threshold_date = (now - timedelta(days=self.DECAY_THRESHOLD_DAYS)).isoformat()
        
        # Get patterns eligible for decay or already below minimum
        cursor.execute("""
            SELECT pattern_id, confidence, last_accessed
            FROM patterns
            WHERE is_pinned = 0
              AND (last_accessed < ? OR confidence <= ?)
        """, (decay_threshold_date, self.MIN_CONFIDENCE))
        
        candidates = cursor.fetchall()
        patterns_checked = len(candidates)
        patterns_decayed = 0
        patterns_deleted = 0
        decay_log_entries = 0
        
        for pattern_id, confidence, last_accessed in candidates:
            # Check if already below threshold
            if confidence < self.MIN_CONFIDENCE:
                # Delete immediately
                cursor.execute("DELETE FROM patterns WHERE pattern_id = ?", (pattern_id,))
                patterns_deleted += 1
                
                # Log deletion
                cursor.execute("""
                    INSERT INTO confidence_decay_log (pattern_id, old_confidence, new_confidence, reason)
                    VALUES (?, ?, ?, ?)
                """, (pattern_id, confidence, 0.0, "Deleted: Already below minimum confidence"))
                decay_log_entries += 1
                continue
            
            # Calculate decay
            last_access_date = datetime.fromisoformat(last_accessed)
            days_since_access = (now - last_access_date).days
            days_to_decay = max(0, days_since_access - self.DECAY_THRESHOLD_DAYS)
            
            # Skip if no decay needed
            if days_to_decay == 0:
                continue
            
            # Apply decay
            decay_amount = self.DECAY_RATE * days_to_decay
            new_confidence = max(0.0, confidence - decay_amount)
            
            if new_confidence < self.MIN_CONFIDENCE:
                # Delete pattern
                cursor.execute("DELETE FROM patterns WHERE pattern_id = ?", (pattern_id,))
                patterns_deleted += 1
                
                # Log deletion
                cursor.execute("""
                    INSERT INTO confidence_decay_log (pattern_id, old_confidence, new_confidence, reason)
                    VALUES (?, ?, ?, ?)
                """, (pattern_id, confidence, new_confidence, 
                      f"Deleted: Decayed below minimum confidence ({days_to_decay} days since access)"))
                decay_log_entries += 1
            else:
                # Update confidence
                cursor.execute("""
                    UPDATE patterns SET confidence = ? WHERE pattern_id = ?
                """, (new_confidence, pattern_id))
                patterns_decayed += 1
                
                # Log decay
                cursor.execute("""
                    INSERT INTO confidence_decay_log (pattern_id, old_confidence, new_confidence, reason)
                    VALUES (?, ?, ?, ?)
                """, (pattern_id, confidence, new_confidence, 
                      f"Decayed: {days_to_decay} days since last access"))
                decay_log_entries += 1
        
        conn.commit()
        
        return {
            "patterns_checked": patterns_checked,
            "patterns_decayed": patterns_decayed,
            "patterns_deleted": patterns_deleted,
            "decay_log_entries": decay_log_entries
        }
    
    def get_decay_candidates(self) -> List[Dict[str, Any]]:
        """
        Find patterns eligible for decay.
        
        Criteria:
            - Not pinned
            - last_accessed > DECAY_THRESHOLD_DAYS ago
            - confidence > MIN_CONFIDENCE
        
        Returns:
            List of pattern dictionaries with decay calculations
        
        Performance: <50ms
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now()
        decay_threshold_date = (now - timedelta(days=self.DECAY_THRESHOLD_DAYS)).isoformat()
        
        cursor.execute("""
            SELECT pattern_id, title, confidence, last_accessed
            FROM patterns
            WHERE is_pinned = 0
              AND last_accessed < ?
              AND confidence > ?
            ORDER BY confidence ASC, last_accessed ASC
        """, (decay_threshold_date, self.MIN_CONFIDENCE))
        
        rows = cursor.fetchall()
        
        candidates = []
        for row in rows:
            pattern_id, title, confidence, last_accessed = row
            last_access_date = datetime.fromisoformat(last_accessed)
            days_since_access = (now - last_access_date).days
            days_to_decay = max(0, days_since_access - self.DECAY_THRESHOLD_DAYS)
            decay_amount = self.DECAY_RATE * days_to_decay
            new_confidence = max(0.0, confidence - decay_amount)
            
            candidates.append({
                "pattern_id": pattern_id,
                "title": title,
                "current_confidence": confidence,
                "last_accessed": last_accessed,
                "days_since_access": days_since_access,
                "decay_amount": decay_amount,
                "new_confidence": new_confidence,
                "will_be_deleted": new_confidence < self.MIN_CONFIDENCE
            })
        
        return candidates
    
    def pin_pattern(self, pattern_id: str) -> bool:
        """
        Pin a pattern to protect it from confidence decay.
        
        Args:
            pattern_id: Pattern to pin
        
        Returns:
            True if pinned successfully, False if pattern not found
        
        Performance: <10ms
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE patterns SET is_pinned = 1 WHERE pattern_id = ?", (pattern_id,))
        pinned = cursor.rowcount > 0
        
        conn.commit()
        
        return pinned
    
    def unpin_pattern(self, pattern_id: str) -> bool:
        """
        Unpin a pattern to allow confidence decay.
        
        Args:
            pattern_id: Pattern to unpin
        
        Returns:
            True if unpinned successfully, False if pattern not found
        
        Performance: <10ms
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE patterns SET is_pinned = 0 WHERE pattern_id = ?", (pattern_id,))
        unpinned = cursor.rowcount > 0
        
        conn.commit()
        
        return unpinned
    
    def get_decay_log(
        self,
        pattern_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get confidence decay audit trail.
        
        Args:
            pattern_id: Filter by specific pattern (optional)
            limit: Maximum entries to return
        
        Returns:
            List of decay log entries
        
        Performance: <30ms
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if pattern_id:
            cursor.execute("""
                SELECT pattern_id, old_confidence, new_confidence, decay_date, reason
                FROM confidence_decay_log
                WHERE pattern_id = ?
                ORDER BY decay_date DESC
                LIMIT ?
            """, (pattern_id, limit))
        else:
            cursor.execute("""
                SELECT pattern_id, old_confidence, new_confidence, decay_date, reason
                FROM confidence_decay_log
                ORDER BY decay_date DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        
        log_entries = []
        for row in rows:
            log_entries.append({
                "pattern_id": row[0],
                "old_confidence": row[1],
                "new_confidence": row[2],
                "decay_date": row[3],
                "reason": row[4]
            })
        
        return log_entries
