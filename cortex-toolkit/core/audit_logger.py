"""
Audit Logger for CORTEX Toolkit.

This module provides:
- Tamper-evident audit trail logging
- Execution event logging with hashed arguments
- Security event logging
- Log querying and filtering
- Sensitive data masking

Part of Phase 6: Security Hardening implementation.
"""

import getpass
import hashlib
import json
import socket
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ExecutionEvent:
    """Represents a tool execution event for auditing."""
    
    tool: str
    args: List[str]
    status: str
    exit_code: int
    duration_ms: int
    checkpoint_id: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tool": self.tool,
            "args": self.args,
            "status": self.status,
            "exit_code": self.exit_code,
            "duration_ms": self.duration_ms,
            "checkpoint_id": self.checkpoint_id,
            "error": self.error,
        }


@dataclass
class SecurityEvent:
    """Represents a security-related event for auditing."""
    
    event_type: str
    tool: str
    blocked: bool = True
    severity: str = "medium"
    violation_type: Optional[str] = None
    required_level: Optional[str] = None
    current_level: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "event_type": self.event_type,
            "tool": self.tool,
            "blocked": self.blocked,
            "severity": self.severity,
        }
        if self.violation_type:
            result["violation_type"] = self.violation_type
        if self.required_level:
            result["required_level"] = self.required_level
        if self.current_level:
            result["current_level"] = self.current_level
        if self.details:
            result["details"] = self.details
        return result


# =============================================================================
# Sensitive Data Patterns
# =============================================================================

SENSITIVE_ARG_PATTERNS = [
    "password",
    "passwd",
    "secret",
    "api-key",
    "api_key",
    "apikey",
    "token",
    "auth",
    "credential",
    "private",
]


# =============================================================================
# AuditLogger Class
# =============================================================================

class AuditLogger:
    """
    Tamper-evident audit trail for toolkit operations.
    
    Features:
    - Append-only log format
    - Sequence numbers for tamper detection
    - Argument hashing (no raw sensitive data)
    - User and hostname tracking
    - Thread-safe logging
    """
    
    DEFAULT_LOG_NAME = "audit.jsonl"
    
    def __init__(
        self,
        log_path: Optional[Path] = None,
        toolkit_root: Optional[Path] = None
    ):
        """
        Initialize AuditLogger.
        
        Args:
            log_path: Path to audit log file.
            toolkit_root: Root directory of toolkit (for default log path).
        """
        if log_path:
            self.log_path = Path(log_path)
        elif toolkit_root:
            self.log_path = Path(toolkit_root) / "logs" / self.DEFAULT_LOG_NAME
        else:
            self.log_path = Path.cwd() / "logs" / self.DEFAULT_LOG_NAME
        
        # Ensure directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Sequence counter
        self._sequence = self._get_last_sequence()
        
        # Previous hash for chain
        self._prev_hash: Optional[str] = None
    
    def _get_last_sequence(self) -> int:
        """Get the last sequence number from existing log."""
        if not self.log_path.exists():
            return 0
        
        try:
            lines = self.log_path.read_text().strip().split('\n')
            if lines and lines[-1]:
                last_record = json.loads(lines[-1])
                return last_record.get("sequence", 0)
        except (json.JSONDecodeError, IOError):
            pass
        
        return 0
    
    # =========================================================================
    # Logging Methods
    # =========================================================================
    
    def log_execution(self, event: ExecutionEvent) -> None:
        """
        Log a tool execution event.
        
        Args:
            event: ExecutionEvent to log.
        """
        record = self._create_record("tool_execution", event.to_dict())
        
        # Hash arguments instead of storing raw
        record["args_hash"] = self._hash_args(event.args)
        
        # Remove raw args from record
        if "args" in record:
            del record["args"]
        
        self._write_record(record)
    
    def log_security(self, event: SecurityEvent) -> None:
        """
        Log a security-related event.
        
        Args:
            event: SecurityEvent to log.
        """
        record = self._create_record("security", event.to_dict())
        self._write_record(record)
    
    def _create_record(
        self, 
        record_type: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a complete audit record."""
        with self._lock:
            self._sequence += 1
            sequence = self._sequence
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "sequence": sequence,
            "record_type": record_type,
            "user": getpass.getuser(),
            "hostname": socket.gethostname(),
            **data
        }
        
        # Add previous hash for chain
        if self._prev_hash:
            record["prev_hash"] = self._prev_hash
        
        return record
    
    def _write_record(self, record: Dict[str, Any]) -> None:
        """Write a record to the log file (append-only)."""
        # Hash the record for chain
        record_json = json.dumps(record, sort_keys=True)
        record_hash = hashlib.sha256(record_json.encode()).hexdigest()[:16]
        
        with self._lock:
            # Store hash for next record
            self._prev_hash = record_hash
            
            # Append to log file
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(record_json + '\n')
    
    def _hash_args(self, args: List[str]) -> str:
        """
        Hash arguments for privacy.
        
        Masks sensitive values before hashing.
        """
        masked_args = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            # Check if this is a sensitive flag
            if self._is_sensitive_flag(arg):
                masked_args.append(arg)
                # Mask the next value if present
                if i + 1 < len(args):
                    masked_args.append("****MASKED****")
                    i += 1
            else:
                masked_args.append(arg)
            
            i += 1
        
        # Hash the masked args
        args_str = json.dumps(masked_args, sort_keys=True)
        return hashlib.sha256(args_str.encode()).hexdigest()[:16]
    
    def _is_sensitive_flag(self, arg: str) -> bool:
        """Check if an argument is a sensitive flag."""
        arg_lower = arg.lower().strip('-')
        
        for pattern in SENSITIVE_ARG_PATTERNS:
            if pattern in arg_lower:
                return True
        
        return False
    
    # =========================================================================
    # Query Methods
    # =========================================================================
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent log entries.
        
        Args:
            limit: Maximum number of entries to return.
            
        Returns:
            List of log records (most recent first).
        """
        if not self.log_path.exists():
            return []
        
        try:
            lines = self.log_path.read_text().strip().split('\n')
            records = []
            
            for line in reversed(lines[-limit:]):
                if line:
                    records.append(json.loads(line))
            
            return records[:limit]
        except (json.JSONDecodeError, IOError):
            return []
    
    def get_by_tool(self, tool_name: str) -> List[Dict[str, Any]]:
        """
        Get all log entries for a specific tool.
        
        Args:
            tool_name: Name of the tool to filter by.
            
        Returns:
            List of matching log records.
        """
        return self._filter_records(lambda r: r.get("tool") == tool_name)
    
    def get_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get all log entries with a specific status.
        
        Args:
            status: Status to filter by.
            
        Returns:
            List of matching log records.
        """
        return self._filter_records(lambda r: r.get("status") == status)
    
    def get_by_date_range(
        self,
        start: datetime,
        end: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get log entries within a date range.
        
        Args:
            start: Start of date range.
            end: End of date range.
            
        Returns:
            List of matching log records.
        """
        def in_range(record: Dict[str, Any]) -> bool:
            try:
                ts = datetime.fromisoformat(record.get("timestamp", ""))
                return start <= ts <= end
            except (ValueError, TypeError):
                return False
        
        return self._filter_records(in_range)
    
    def _filter_records(self, predicate) -> List[Dict[str, Any]]:
        """Filter records by a predicate function."""
        if not self.log_path.exists():
            return []
        
        try:
            lines = self.log_path.read_text().strip().split('\n')
            records = []
            
            for line in lines:
                if line:
                    record = json.loads(line)
                    if predicate(record):
                        records.append(record)
            
            return records
        except (json.JSONDecodeError, IOError):
            return []
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the audit log."""
        if not self.log_path.exists():
            return {"total_records": 0}
        
        try:
            lines = self.log_path.read_text().strip().split('\n')
            records = [json.loads(line) for line in lines if line]
            
            tools = {}
            statuses = {}
            
            for record in records:
                tool = record.get("tool", "unknown")
                status = record.get("status", "unknown")
                
                tools[tool] = tools.get(tool, 0) + 1
                statuses[status] = statuses.get(status, 0) + 1
            
            return {
                "total_records": len(records),
                "tools": tools,
                "statuses": statuses,
                "first_timestamp": records[0].get("timestamp") if records else None,
                "last_timestamp": records[-1].get("timestamp") if records else None,
            }
        except (json.JSONDecodeError, IOError):
            return {"total_records": 0, "error": "Failed to read log"}
