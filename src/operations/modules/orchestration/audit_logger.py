"""
CORTEX Planning System 3.0 - Audit Trail Logger

Provides comprehensive audit logging for all planning orchestrator operations.
Stores events in JSONL format for easy querying and analysis.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
"""

import json
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from threading import Lock
import csv


@dataclass
class AuditEvent:
    """Structured audit event."""
    timestamp: str
    event_type: str
    session_id: str
    plan_id: str
    user_request: Optional[str]
    orchestrator: str
    phase: str
    metadata: Dict[str, Any]
    outcome: str
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class AuditLogger:
    """
    Singleton audit logger for Planning System 3.0.
    
    Captures all significant planning operations and stores them in JSONL format
    for complete visibility, troubleshooting, and compliance.
    
    Storage:
        - Active log: cortex-brain/audit-trail.jsonl
        - Archives: cortex-brain/audit-archive/{YYYY-MM}-audit.jsonl.gz
    
    Features:
        - Append-only writes (no locking issues)
        - Structured event schema
        - Query and filtering
        - Monthly archival
        - CSV export
        - Statistics generation
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls, base_path: Optional[Path] = None):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize audit logger."""
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.base_path = base_path or Path("cortex-brain")
        self.audit_file = self.base_path / "audit-trail.jsonl"
        self.archive_dir = self.base_path / "audit-archive"
        
        # Ensure directories exist
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        self._initialized = True
    
    def log_event(
        self,
        event_type: str,
        session_id: str,
        plan_id: str,
        orchestrator: str,
        user_request: Optional[str] = None,
        phase: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
        outcome: str = "success",
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event (e.g., "temp_plan_created", "plan_refined")
            session_id: Planning session identifier
            plan_id: Plan identifier
            orchestrator: Name of orchestrator generating the event
            user_request: User's original request (optional)
            phase: Current phase (e.g., "refinement", "approval", "execution")
            metadata: Additional structured data
            outcome: "success", "failure", "warning"
            duration_ms: Operation duration in milliseconds (optional)
            error_message: Error details if outcome is "failure" (optional)
        """
        event = AuditEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type=event_type,
            session_id=session_id,
            plan_id=plan_id,
            user_request=user_request,
            orchestrator=orchestrator,
            phase=phase,
            metadata=metadata or {},
            outcome=outcome,
            duration_ms=duration_ms,
            error_message=error_message
        )
        
        # Append to JSONL file (thread-safe)
        with self._lock:
            with open(self.audit_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event.to_dict()) + '\n')
    
    def query_events(
        self,
        plan_id: Optional[str] = None,
        session_id: Optional[str] = None,
        event_type: Optional[str] = None,
        orchestrator: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        outcome: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query audit events with filters.
        
        Args:
            plan_id: Filter by plan ID
            session_id: Filter by session ID
            event_type: Filter by event type
            orchestrator: Filter by orchestrator name
            since: Events after this timestamp
            until: Events before this timestamp
            outcome: Filter by outcome ("success", "failure", "warning")
            limit: Maximum number of events to return
        
        Returns:
            List of matching events (most recent first)
        """
        events = []
        
        # Read from active log
        if self.audit_file.exists():
            events.extend(self._read_jsonl(self.audit_file))
        
        # Read from archives if time range specified
        if since and since < datetime.utcnow() - timedelta(days=30):
            archive_files = self._get_archive_files_in_range(since, until)
            for archive_file in archive_files:
                events.extend(self._read_compressed_jsonl(archive_file))
        
        # Apply filters
        filtered = events
        
        if plan_id:
            filtered = [e for e in filtered if e.get('plan_id') == plan_id]
        if session_id:
            filtered = [e for e in filtered if e.get('session_id') == session_id]
        if event_type:
            filtered = [e for e in filtered if e.get('event_type') == event_type]
        if orchestrator:
            filtered = [e for e in filtered if e.get('orchestrator') == orchestrator]
        if outcome:
            filtered = [e for e in filtered if e.get('outcome') == outcome]
        if since:
            since_iso = since.isoformat()
            filtered = [e for e in filtered if e.get('timestamp', '') >= since_iso]
        if until:
            until_iso = until.isoformat()
            filtered = [e for e in filtered if e.get('timestamp', '') <= until_iso]
        
        # Sort by timestamp descending (most recent first)
        filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Apply limit
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def get_plan_history(self, plan_id: str) -> List[Dict[str, Any]]:
        """
        Get complete audit trail for a specific plan.
        
        Args:
            plan_id: Plan identifier
        
        Returns:
            Chronological list of events for this plan
        """
        events = self.query_events(plan_id=plan_id)
        # Reverse to get chronological order (oldest first)
        return list(reversed(events))
    
    def get_session_timeline(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get chronological session events.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Chronological list of events for this session
        """
        events = self.query_events(session_id=session_id)
        # Reverse to get chronological order (oldest first)
        return list(reversed(events))
    
    def export_to_csv(self, events: List[Dict[str, Any]], output_path: str) -> None:
        """
        Export events to CSV format.
        
        Args:
            events: List of audit events
            output_path: Path to output CSV file
        """
        if not events:
            return
        
        # Determine all unique keys across events
        all_keys = set()
        for event in events:
            all_keys.update(event.keys())
            # Flatten metadata
            if 'metadata' in event:
                for k in event['metadata'].keys():
                    all_keys.add(f"metadata.{k}")
        
        # Define column order (common fields first)
        ordered_keys = [
            'timestamp', 'event_type', 'session_id', 'plan_id', 
            'orchestrator', 'phase', 'outcome', 'duration_ms',
            'user_request', 'error_message'
        ]
        remaining_keys = sorted(all_keys - set(ordered_keys))
        fieldnames = [k for k in ordered_keys if k in all_keys] + remaining_keys
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in events:
                row = {}
                for key in fieldnames:
                    if key.startswith('metadata.'):
                        # Flatten metadata
                        meta_key = key.replace('metadata.', '')
                        row[key] = event.get('metadata', {}).get(meta_key, '')
                    else:
                        value = event.get(key, '')
                        # Convert dicts/lists to JSON strings for CSV
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value)
                        row[key] = value
                writer.writerow(row)
    
    def generate_stats(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate audit statistics.
        
        Args:
            since: Calculate stats from this timestamp (default: last 30 days)
        
        Returns:
            Dictionary with statistics
        """
        if since is None:
            since = datetime.utcnow() - timedelta(days=30)
        
        events = self.query_events(since=since)
        
        if not events:
            return {
                'total_events': 0,
                'time_range': f"Last 30 days (since {since.isoformat()})"
            }
        
        # Count by event type
        event_types = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Count by outcome
        outcomes = {}
        for event in events:
            outcome = event.get('outcome', 'unknown')
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        # Collect plan-related stats
        plans_created = len([e for e in events if e.get('event_type') == 'temp_plan_created'])
        plans_approved = len([e for e in events if e.get('event_type') == 'plan_approved'])
        plans_promoted = len([e for e in events if e.get('event_type') == 'plan_promoted'])
        
        # Calculate average DoR scores
        dor_scores = [
            e.get('metadata', {}).get('dor_score', 0)
            for e in events
            if 'dor_score' in e.get('metadata', {})
        ]
        avg_dor = sum(dor_scores) / len(dor_scores) if dor_scores else 0.0
        
        # Calculate average refinement iterations
        refinement_counts = {}
        for event in events:
            if event.get('event_type') == 'plan_refined':
                plan_id = event.get('plan_id')
                iteration = event.get('metadata', {}).get('iteration', 1)
                refinement_counts[plan_id] = max(refinement_counts.get(plan_id, 0), iteration)
        avg_iterations = (
            sum(refinement_counts.values()) / len(refinement_counts)
            if refinement_counts else 0.0
        )
        
        # Calculate average session duration
        session_durations = [
            e.get('metadata', {}).get('duration_seconds', 0)
            for e in events
            if e.get('event_type') == 'session_closed' and 'duration_seconds' in e.get('metadata', {})
        ]
        avg_duration_minutes = (
            sum(session_durations) / len(session_durations) / 60
            if session_durations else 0.0
        )
        
        # Count active sessions
        sessions_started = len([e for e in events if e.get('event_type') == 'session_started'])
        sessions_closed = len([e for e in events if e.get('event_type') == 'session_closed'])
        active_sessions = sessions_started - sessions_closed
        
        return {
            'total_events': len(events),
            'time_range': f"Last 30 days (since {since.isoformat()})",
            'active_sessions': active_sessions,
            'plans_created': plans_created,
            'plans_approved': plans_approved,
            'plans_promoted': plans_promoted,
            'avg_dor_score': round(avg_dor, 2),
            'avg_refinement_iterations': round(avg_iterations, 1),
            'avg_session_duration_minutes': round(avg_duration_minutes, 1),
            'event_types': dict(sorted(event_types.items(), key=lambda x: x[1], reverse=True)),
            'outcomes': outcomes
        }
    
    def archive_old_logs(self, days_threshold: int = 30) -> Dict[str, Any]:
        """
        Archive logs older than threshold to compressed files.
        
        Args:
            days_threshold: Archive events older than this many days
        
        Returns:
            Dictionary with archival statistics
        """
        if not self.audit_file.exists():
            return {'archived': 0, 'months': []}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
        
        # Read all events
        all_events = self._read_jsonl(self.audit_file)
        
        # Group by month
        events_by_month = {}
        events_to_keep = []
        
        for event in all_events:
            timestamp_str = event.get('timestamp', '')
            if timestamp_str:
                event_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if event_date < cutoff_date:
                    month_key = event_date.strftime('%Y-%m')
                    events_by_month.setdefault(month_key, []).append(event)
                else:
                    events_to_keep.append(event)
            else:
                events_to_keep.append(event)
        
        # Archive old months
        archived_months = []
        for month, events in events_by_month.items():
            archive_file = self.archive_dir / f"{month}-audit.jsonl.gz"
            self._write_compressed_jsonl(archive_file, events)
            archived_months.append(month)
        
        # Rewrite active log with only recent events
        with self._lock:
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                for event in events_to_keep:
                    f.write(json.dumps(event) + '\n')
        
        return {
            'archived': len(all_events) - len(events_to_keep),
            'months': archived_months,
            'remaining': len(events_to_keep)
        }
    
    # Private helper methods
    
    def _read_jsonl(self, file_path: Path) -> List[Dict[str, Any]]:
        """Read events from JSONL file."""
        events = []
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            # Skip malformed lines
                            continue
        return events
    
    def _read_compressed_jsonl(self, file_path: Path) -> List[Dict[str, Any]]:
        """Read events from compressed JSONL file."""
        events = []
        if file_path.exists():
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return events
    
    def _write_compressed_jsonl(self, file_path: Path, events: List[Dict[str, Any]]) -> None:
        """Write events to compressed JSONL file."""
        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
            for event in events:
                f.write(json.dumps(event) + '\n')
    
    def _get_archive_files_in_range(
        self,
        since: Optional[datetime],
        until: Optional[datetime]
    ) -> List[Path]:
        """Get archive files within date range."""
        archive_files = []
        
        if not self.archive_dir.exists():
            return archive_files
        
        for archive_file in self.archive_dir.glob('*-audit.jsonl.gz'):
            # Extract month from filename (YYYY-MM-audit.jsonl.gz)
            month_str = archive_file.stem.replace('-audit.jsonl', '')
            try:
                archive_date = datetime.strptime(month_str, '%Y-%m')
                if since and archive_date < since:
                    continue
                if until and archive_date > until:
                    continue
                archive_files.append(archive_file)
            except ValueError:
                # Skip files with unexpected format
                continue
        
        return archive_files


# Convenience function for global access
_global_logger: Optional[AuditLogger] = None

def get_audit_logger(base_path: Optional[Path] = None) -> AuditLogger:
    """
    Get the global audit logger instance.
    
    Args:
        base_path: Base path for audit files (default: cortex-brain/)
    
    Returns:
        AuditLogger singleton instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = AuditLogger(base_path)
    return _global_logger
