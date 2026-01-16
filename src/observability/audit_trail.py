"""
Enhanced Audit Trail Management Module

Provides searchable, queryable audit history with configurable retention.

AC-OB-003-01: Audit Trail Enhancement
- Searchable audit trail
- Configurable retention policies
- Export functionality (JSON, CSV)
- Advanced querying and filtering
"""

import logging
import json
import csv
import sqlite3
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    EXECUTE = "execute"
    ACCESS = "access"
    MODIFY = "modify"
    ERROR = "error"
    ALERT = "alert"


class AuditSeverity(Enum):
    """Severity level of audit events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Single audit trail entry."""
    event_id: str
    event_type: AuditEventType
    component: str
    action: str
    user: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: AuditSeverity = AuditSeverity.MEDIUM
    details: Dict[str, Any] = field(default_factory=dict)
    resource_id: Optional[str] = None
    status: str = "success"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "component": self.component,
            "action": self.action,
            "user": self.user,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "details": self.details,
            "resource_id": self.resource_id,
            "status": self.status
        }


class RetentionPolicy:
    """Policy for audit trail retention."""
    
    def __init__(
        self,
        retention_days: int = 90,
        archive_after_days: int = 30,
        compress_after_days: int = 60
    ):
        self.retention_days = retention_days
        self.archive_after_days = archive_after_days
        self.compress_after_days = compress_after_days
    
    def get_retention_cutoff(self) -> datetime:
        """Get cutoff date for retention."""
        return datetime.utcnow() - timedelta(days=self.retention_days)
    
    def should_archive(self, event_date: datetime) -> bool:
        """Check if event should be archived."""
        archive_cutoff = datetime.utcnow() - timedelta(days=self.archive_after_days)
        return event_date < archive_cutoff
    
    def should_compress(self, event_date: datetime) -> bool:
        """Check if event should be compressed."""
        compress_cutoff = datetime.utcnow() - timedelta(days=self.compress_after_days)
        return event_date < compress_cutoff


class AuditTrail:
    """Enhanced audit trail management."""
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        retention_policy: Optional[RetentionPolicy] = None
    ):
        self.db_path = db_path or ":memory:"
        self.retention_policy = retention_policy or RetentionPolicy()
        self.events: List[AuditEvent] = []
        self.handlers: List[callable] = []
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_trail (
                        event_id TEXT PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        component TEXT NOT NULL,
                        action TEXT NOT NULL,
                        user TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        details TEXT,
                        resource_id TEXT,
                        status TEXT,
                        indexed_timestamp TIMESTAMP
                    )
                """)
                
                # Create indexes for common queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp
                    ON audit_trail(timestamp DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_component
                    ON audit_trail(component)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user
                    ON audit_trail(user)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_severity
                    ON audit_trail(severity)
                """)
                
                conn.commit()
            logger.info(f"Initialized audit trail database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing audit trail DB: {str(e)}")
    
    def record_event(
        self,
        event_type: AuditEventType,
        component: str,
        action: str,
        user: str,
        event_id: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        resource_id: Optional[str] = None,
        status: str = "success"
    ) -> AuditEvent:
        """Record an audit event."""
        import uuid
        
        event_id = event_id or str(uuid.uuid4())
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            component=component,
            action=action,
            user=user,
            severity=severity,
            details=details or {},
            resource_id=resource_id,
            status=status
        )
        
        with self._lock:
            self.events.append(event)
            self._persist_event(event)
            
            # Call handlers
            for handler in self.handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in audit handler: {str(e)}")
        
        return event
    
    def _persist_event(self, event: AuditEvent) -> None:
        """Persist event to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO audit_trail
                    (event_id, event_type, component, action, user, timestamp,
                     severity, details, resource_id, status, indexed_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.event_type.value,
                    event.component,
                    event.action,
                    event.user,
                    event.timestamp.isoformat(),
                    event.severity.value,
                    json.dumps(event.details),
                    event.resource_id,
                    event.status,
                    event.timestamp
                ))
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error persisting audit event: {str(e)}")
    
    def register_handler(self, handler: callable) -> None:
        """Register event handler."""
        self.handlers.append(handler)
    
    def search(
        self,
        component: Optional[str] = None,
        user: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
        event_type: Optional[AuditEventType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        resource_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 1000
    ) -> List[AuditEvent]:
        """Search audit trail with filters."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM audit_trail WHERE 1=1"
                params = []
                
                if component:
                    query += " AND component = ?"
                    params.append(component)
                
                if user:
                    query += " AND user = ?"
                    params.append(user)
                
                if severity:
                    query += " AND severity = ?"
                    params.append(severity.value)
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type.value)
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                if resource_id:
                    query += " AND resource_id = ?"
                    params.append(resource_id)
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event = AuditEvent(
                        event_id=row["event_id"],
                        event_type=AuditEventType(row["event_type"]),
                        component=row["component"],
                        action=row["action"],
                        user=row["user"],
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        severity=AuditSeverity(row["severity"]),
                        details=json.loads(row["details"]) if row["details"] else {},
                        resource_id=row["resource_id"],
                        status=row["status"]
                    )
                    events.append(event)
                
                return events
        except Exception as e:
            logger.error(f"Error searching audit trail: {str(e)}")
            return []
    
    def export_json(
        self,
        output_path: str,
        **search_filters
    ) -> None:
        """Export audit trail to JSON."""
        events = self.search(limit=10000, **search_filters)
        
        data = [event.to_dict() for event in events]
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Exported {len(events)} audit events to {output_path}")
    
    def export_csv(
        self,
        output_path: str,
        **search_filters
    ) -> None:
        """Export audit trail to CSV."""
        events = self.search(limit=10000, **search_filters)
        
        if not events:
            logger.warning("No events to export")
            return
        
        # Get all unique keys from details
        all_detail_keys = set()
        for event in events:
            all_detail_keys.update(event.details.keys())
        
        fieldnames = [
            "event_id", "event_type", "component", "action", "user",
            "timestamp", "severity", "resource_id", "status"
        ] + sorted(list(all_detail_keys))
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in events:
                row = {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "component": event.component,
                    "action": event.action,
                    "user": event.user,
                    "timestamp": event.timestamp.isoformat(),
                    "severity": event.severity.value,
                    "resource_id": event.resource_id,
                    "status": event.status
                }
                # Add details fields
                row.update({k: str(v) for k, v in event.details.items()})
                writer.writerow(row)
        
        logger.info(f"Exported {len(events)} audit events to {output_path}")
    
    def cleanup(self) -> int:
        """Remove expired entries based on retention policy."""
        try:
            cutoff = self.retention_policy.get_retention_cutoff()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "DELETE FROM audit_trail WHERE timestamp < ?",
                    (cutoff.isoformat(),)
                )
                
                deleted_count = cursor.rowcount
                conn.commit()
            
            logger.info(f"Cleaned up {deleted_count} expired audit entries")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up audit trail: {str(e)}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit trail statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total events
                cursor.execute("SELECT COUNT(*) FROM audit_trail")
                total_events = cursor.fetchone()[0]
                
                # Events by severity
                cursor.execute("""
                    SELECT severity, COUNT(*) as count
                    FROM audit_trail
                    GROUP BY severity
                """)
                severity_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Events by component
                cursor.execute("""
                    SELECT component, COUNT(*) as count
                    FROM audit_trail
                    GROUP BY component
                    LIMIT 10
                """)
                component_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Events by user (top 10)
                cursor.execute("""
                    SELECT user, COUNT(*) as count
                    FROM audit_trail
                    GROUP BY user
                    ORDER BY count DESC
                    LIMIT 10
                """)
                user_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                return {
                    "total_events": total_events,
                    "severity_distribution": severity_counts,
                    "top_components": component_counts,
                    "top_users": user_counts
                }
        except Exception as e:
            logger.error(f"Error getting audit statistics: {str(e)}")
            return {}


# Global audit trail instance
_audit_trail = None


def get_audit_trail() -> AuditTrail:
    """Get or create global audit trail."""
    global _audit_trail
    if _audit_trail is None:
        _audit_trail = AuditTrail()
    return _audit_trail
