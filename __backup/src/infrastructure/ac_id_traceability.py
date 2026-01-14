"""
AC-AUDIT-004: AC-ID Traceability

Links all audit events to acceptance criteria (AC-IDs) for compliance tracking.
Enables queries like: "Show all audit events for AC-AUDIT-001" or 
"Prove this AC-ID has been implemented, tested, and audited."
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
import sqlite3
import logging

logger = logging.getLogger(__name__)


class ACIDTraceability:
    """
    AC-AUDIT-004: AC-ID Traceability
    
    Links audit log entries to acceptance criteria for compliance tracking.
    """
    
    def __init__(self, audit_db: sqlite3.Connection):
        """
        Initialize with audit database connection.
        
        Args:
            audit_db: SQLite connection to audit database
        """
        self.db = audit_db
        self._ensure_ac_id_column()
    
    def _ensure_ac_id_column(self):
        """Ensure ac_id column exists in audit_log table."""
        try:
            # Check if column exists
            cursor = self.db.execute("PRAGMA table_info(audit_log)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'ac_id' not in columns:
                # Add ac_id column if not present
                self.db.execute("""
                    ALTER TABLE audit_log 
                    ADD COLUMN ac_id TEXT
                """)
                self.db.commit()
                logger.info("Added ac_id column to audit_log table")
        except Exception as e:
            logger.warning(f"Could not ensure ac_id column: {e}")
    
    def link_event_to_ac(self, event_id: int, ac_id: str) -> bool:
        """
        Link an existing audit event to an AC-ID.
        
        Args:
            event_id: Primary key of audit event
            ac_id: AC-ID to link (format: AC-CATEGORY-NNN)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._validate_ac_id(ac_id):
            logger.error(f"Invalid AC-ID format: {ac_id}")
            return False
        
        try:
            self.db.execute(
                "UPDATE audit_log SET ac_id = ? WHERE id = ?",
                (ac_id, event_id)
            )
            self.db.commit()
            logger.debug(f"Linked event {event_id} to {ac_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to link event to AC-ID: {e}")
            return False
    
    def log_with_ac_id(self, ac_id: str, level: str, category: str,
                      message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log an audit event linked to an AC-ID.
        
        This is the preferred way to create audit entries that are automatically
        linked to acceptance criteria.
        
        Args:
            ac_id: AC-ID being validated/implemented
            level: Audit level (CRITICAL, ERROR, WARNING, INFO, DEBUG, TRACE)
            category: Audit category (governance, orchestrator, validation, etc.)
            message: Log message
            context: Optional additional context
            
        Returns:
            True if successful
        """
        if not self._validate_ac_id(ac_id):
            logger.error(f"Invalid AC-ID format: {ac_id}")
            return False
        
        try:
            self.db.execute("""
                INSERT INTO audit_log 
                (timestamp, level, category, component, operation, message, ac_id, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.utcnow().isoformat(),
                level,
                category,
                'AC-VALIDATOR',
                'AC_VALIDATION',
                message,
                ac_id,
                json.dumps(context or {})
            ))
            self.db.commit()
            logger.debug(f"Logged audit event for {ac_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to log AC-ID audit event: {e}")
            return False
    
    def query_events_by_ac_id(self, ac_id: str) -> List[Dict[str, Any]]:
        """
        Query all audit events linked to a specific AC-ID.
        
        Args:
            ac_id: AC-ID to query
            
        Returns:
            List of audit events
        """
        try:
            cursor = self.db.execute(
                "SELECT * FROM audit_log WHERE ac_id = ? ORDER BY timestamp DESC",
                (ac_id,)
            )
            
            columns = [desc[0] for desc in cursor.description]
            events = []
            
            for row in cursor.fetchall():
                events.append(dict(zip(columns, row)))
            
            logger.debug(f"Found {len(events)} events for {ac_id}")
            return events
        except Exception as e:
            logger.error(f"Failed to query events for {ac_id}: {e}")
            return []
    
    def get_ac_implementation_proof(self, ac_id: str) -> Dict[str, Any]:
        """
        Get all evidence that an AC-ID has been implemented.
        
        Returns dictionary showing:
        - Implementation events (code changes)
        - Test events (validation)
        - Audit events (governance compliance)
        - Timeline
        
        Args:
            ac_id: AC-ID to get proof for
            
        Returns:
            Dictionary with implementation evidence
        """
        events = self.query_events_by_ac_id(ac_id)
        
        return {
            "ac_id": ac_id,
            "total_events": len(events),
            "events": events,
            "has_implementation": any(e.get('operation') == 'IMPLEMENTATION' for e in events),
            "has_testing": any(e.get('operation') == 'TEST_EXECUTION' for e in events),
            "has_governance": any(e.get('operation') == 'GOVERNANCE_CHECK' for e in events),
            "first_event": events[-1].get('timestamp') if events else None,
            "last_event": events[0].get('timestamp') if events else None,
        }
    
    @staticmethod
    def _validate_ac_id(ac_id: str) -> bool:
        """Validate AC-ID format (AC-CATEGORY-NNN)."""
        if not isinstance(ac_id, str):
            return False
        
        parts = ac_id.split('-')
        if len(parts) != 3:
            return False
        
        if parts[0] != 'AC':
            return False
        
        if not parts[2].isdigit():
            return False
        
        return True
