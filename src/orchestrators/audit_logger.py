"""
CORTEX 5.0 Enterprise Audit Logger

Structured trace logging for Phase 3 Infrastructure Implementation.
Provides searchable, organized audit trail for all orchestrator operations.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List
import threading


class AuditLevel(str, Enum):
    """Audit log levels."""
    TRACE = "trace"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditCategory(str, Enum):
    """Categories for audit events."""
    STATE_MANAGEMENT = "state_management"
    EXECUTION = "execution"
    MIDDLEWARE = "middleware"
    RESPONSE = "response"
    PERFORMANCE = "performance"
    SECURITY = "security"
    VALIDATION = "validation"


@dataclass
class AuditEntry:
    """Structured audit log entry."""
    timestamp: str
    level: AuditLevel
    category: AuditCategory
    component: str
    operation: str
    message: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    correlation_id: Optional[str] = None
    duration_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class EnterpriseAuditLogger:
    """
    Enterprise-grade audit logging system.
    
    Features:
    - Structured JSON logging
    - Category-based organization
    - Correlation ID tracking
    - Performance metrics
    - Thread-safe operations
    - Searchable output
    """
    
    def __init__(
        self,
        log_dir: Optional[str] = None,
        enable_console: bool = True,
        enable_file: bool = True
    ):
        """
        Initialize audit logger.
        
        Args:
            log_dir: Directory for audit logs
            enable_console: Enable console output
            enable_file: Enable file output
        """
        self.log_dir = Path(log_dir) if log_dir else Path("cortex-brain/audit-logs")
        self.enable_console = enable_console
        self.enable_file = enable_file
        self._lock = threading.Lock()
        self._setup_logging()
        
        # Session tracking
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.entry_count = 0
        
        # Category-specific files
        self.category_files: Dict[AuditCategory, Path] = {}
        
        if enable_file:
            self._setup_category_files()
    
    def _setup_logging(self):
        """Setup Python logging."""
        self.logger = logging.getLogger("cortex.audit")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(component)s.%(operation)s: %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _setup_category_files(self):
        """Setup category-specific log files."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        for category in AuditCategory:
            category_file = self.log_dir / f"{self.session_id}_{category.value}.jsonl"
            self.category_files[category] = category_file
    
    def log(
        self,
        level: AuditLevel,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        duration_ms: Optional[float] = None
    ):
        """
        Log audit entry.
        
        Args:
            level: Audit level
            category: Event category
            component: Component name
            operation: Operation name
            message: Log message
            context: Operation context
            metadata: Additional metadata
            correlation_id: Correlation ID for tracking
            duration_ms: Operation duration in milliseconds
        """
        with self._lock:
            self.entry_count += 1
            
            entry = AuditEntry(
                timestamp=datetime.now().isoformat(),
                level=level,
                category=category,
                component=component,
                operation=operation,
                message=message,
                context=context or {},
                metadata=metadata or {},
                correlation_id=correlation_id,
                duration_ms=duration_ms
            )
            
            # Log to console via Python logging
            if self.enable_console:
                log_level = {
                    AuditLevel.TRACE: logging.DEBUG,
                    AuditLevel.INFO: logging.INFO,
                    AuditLevel.WARNING: logging.WARNING,
                    AuditLevel.ERROR: logging.ERROR,
                    AuditLevel.CRITICAL: logging.CRITICAL
                }[level]
                
                extra = {
                    'component': component,
                    'operation': operation
                }
                
                self.logger.log(log_level, message, extra=extra)
            
            # Write to category file
            if self.enable_file:
                self._write_to_file(entry)
    
    def _write_to_file(self, entry: AuditEntry):
        """Write entry to category-specific file."""
        category_file = self.category_files.get(entry.category)
        if not category_file:
            return
        
        try:
            with open(category_file, 'a') as f:
                f.write(entry.to_json() + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write audit entry: {e}")
    
    def trace(
        self,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        **kwargs
    ):
        """Log trace-level entry."""
        self.log(AuditLevel.TRACE, category, component, operation, message, **kwargs)
    
    def info(
        self,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        **kwargs
    ):
        """Log info-level entry."""
        self.log(AuditLevel.INFO, category, component, operation, message, **kwargs)
    
    def warning(
        self,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        **kwargs
    ):
        """Log warning-level entry."""
        self.log(AuditLevel.WARNING, category, component, operation, message, **kwargs)
    
    def error(
        self,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        **kwargs
    ):
        """Log error-level entry."""
        self.log(AuditLevel.ERROR, category, component, operation, message, **kwargs)
    
    def critical(
        self,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        **kwargs
    ):
        """Log critical-level entry."""
        self.log(AuditLevel.CRITICAL, category, component, operation, message, **kwargs)
    
    def search(
        self,
        category: Optional[AuditCategory] = None,
        component: Optional[str] = None,
        operation: Optional[str] = None,
        level: Optional[AuditLevel] = None,
        correlation_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditEntry]:
        """
        Search audit logs.
        
        Args:
            category: Filter by category
            component: Filter by component
            operation: Filter by operation
            level: Filter by level
            correlation_id: Filter by correlation ID
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of matching audit entries
        """
        results = []
        
        # Determine which files to search
        if category:
            files = [self.category_files[category]]
        else:
            files = list(self.category_files.values())
        
        for file_path in files:
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        entry_dict = json.loads(line.strip())
                        entry = AuditEntry(**entry_dict)
                        
                        # Apply filters
                        if component and entry.component != component:
                            continue
                        if operation and entry.operation != operation:
                            continue
                        if level and entry.level != level:
                            continue
                        if correlation_id and entry.correlation_id != correlation_id:
                            continue
                        
                        # Time range filter
                        entry_time = datetime.fromisoformat(entry.timestamp)
                        if start_time and entry_time < start_time:
                            continue
                        if end_time and entry_time > end_time:
                            continue
                        
                        results.append(entry)
            
            except Exception as e:
                self.logger.error(f"Failed to search {file_path}: {e}")
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit log statistics."""
        stats = {
            "session_id": self.session_id,
            "total_entries": self.entry_count,
            "by_category": {},
            "by_level": {},
            "log_directory": str(self.log_dir)
        }
        
        # Count entries by category
        for category, file_path in self.category_files.items():
            if file_path.exists():
                with open(file_path, 'r') as f:
                    count = sum(1 for _ in f)
                stats["by_category"][category.value] = count
        
        return stats
    
    def export_session(self, output_file: str):
        """
        Export entire session to single file.
        
        Args:
            output_file: Output file path
        """
        all_entries = []
        
        for file_path in self.category_files.values():
            if not file_path.exists():
                continue
            
            with open(file_path, 'r') as f:
                for line in f:
                    all_entries.append(json.loads(line.strip()))
        
        # Sort by timestamp
        all_entries.sort(key=lambda e: e['timestamp'])
        
        # Write to output file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "exported_at": datetime.now().isoformat(),
                "total_entries": len(all_entries),
                "entries": all_entries
            }, f, indent=2)
        
        self.logger.info(f"Exported {len(all_entries)} entries to {output_file}")


# Global audit logger instance
_audit_logger: Optional[EnterpriseAuditLogger] = None


def get_audit_logger() -> EnterpriseAuditLogger:
    """Get or create global audit logger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = EnterpriseAuditLogger()
    return _audit_logger


def set_audit_logger(logger: EnterpriseAuditLogger):
    """Set global audit logger."""
    global _audit_logger
    _audit_logger = logger
