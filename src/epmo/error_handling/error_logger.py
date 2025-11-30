"""
CORTEX 3.0 Error Logger
=======================

Advanced logging system for error tracking, analysis, and debugging
with structured logging and multiple output formats.
"""

import logging
import time
import json
import threading
import os
from typing import Dict, List, Optional, Any, TextIO
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import traceback


class LogLevel(Enum):
    """Extended log levels for error categorization."""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    EMERGENCY = 60


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: float
    level: LogLevel
    message: str
    component: str
    error_id: Optional[str] = None
    error_code: Optional[str] = None
    exception_type: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return {
            'timestamp': self.timestamp,
            'level': self.level.name,
            'message': self.message,
            'component': self.component,
            'error_id': self.error_id,
            'error_code': self.error_code,
            'exception_type': self.exception_type,
            'stack_trace': self.stack_trace,
            'context': self.context,
            'metadata': self.metadata
        }


class ErrorLogger:
    """
    Advanced error logging system with structured logging,
    multiple outputs, and error analysis capabilities.
    """
    
    def __init__(
        self,
        log_level: LogLevel = LogLevel.INFO,
        log_file: Optional[str] = None,
        max_log_size_mb: float = 100.0,
        backup_count: int = 5,
        enable_console: bool = True,
        enable_json_format: bool = False,
        enable_structured_logging: bool = True
    ):
        self.log_level = log_level
        self.log_file = Path(log_file) if log_file else None
        self.max_log_size_mb = max_log_size_mb
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_json_format = enable_json_format
        self.enable_structured_logging = enable_structured_logging
        
        # Internal logging storage
        self._log_entries: List[LogEntry] = []
        self._log_lock = threading.RLock()
        self._max_memory_entries = 10000
        
        # Statistics
        self._log_stats = {
            'total_logs': 0,
            'logs_by_level': {level: 0 for level in LogLevel},
            'logs_by_component': {},
            'error_patterns': {}
        }
        
        # Initialize Python logger
        self._setup_python_logger()
        
        # Log filtering
        self._log_filters: List[callable] = []
        self._sensitive_patterns = [
            r'password\s*=\s*["\']?([^"\'\s]+)',
            r'token\s*=\s*["\']?([^"\'\s]+)',
            r'api_key\s*=\s*["\']?([^"\'\s]+)',
            r'secret\s*=\s*["\']?([^"\'\s]+)'
        ]
    
    def log(
        self,
        level: LogLevel,
        message: str,
        component: str = "CORTEX",
        error_id: Optional[str] = None,
        error_code: Optional[str] = None,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a message with structured information.
        
        Args:
            level: Log level
            message: Log message
            component: Component name generating the log
            error_id: Associated error ID
            error_code: Error code if applicable
            exception: Exception object if applicable
            context: Additional context information
            metadata: Additional metadata
        """
        if level.value < self.log_level.value:
            return
        
        # Sanitize sensitive information
        sanitized_message = self._sanitize_message(message)
        sanitized_context = self._sanitize_dict(context or {})
        sanitized_metadata = self._sanitize_dict(metadata or {})
        
        # Create log entry
        log_entry = LogEntry(
            timestamp=time.time(),
            level=level,
            message=sanitized_message,
            component=component,
            error_id=error_id,
            error_code=error_code,
            exception_type=type(exception).__name__ if exception else None,
            stack_trace=traceback.format_exc() if exception else None,
            context=sanitized_context,
            metadata=sanitized_metadata
        )
        
        # Apply filters
        if self._should_filter_log(log_entry):
            return
        
        # Store in memory
        self._store_log_entry(log_entry)
        
        # Log to Python logger
        self._log_to_python_logger(log_entry)
        
        # Update statistics
        self._update_log_statistics(log_entry)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.log(LogLevel.CRITICAL, message, **kwargs)
    
    def emergency(self, message: str, **kwargs) -> None:
        """Log emergency message."""
        self.log(LogLevel.EMERGENCY, message, **kwargs)
    
    def log_exception(
        self,
        exception: Exception,
        message: Optional[str] = None,
        level: LogLevel = LogLevel.ERROR,
        component: str = "CORTEX",
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an exception with full details.
        
        Args:
            exception: Exception to log
            message: Additional message
            level: Log level
            component: Component name
            context: Additional context
        """
        error_message = message or f"Exception occurred: {str(exception)}"
        
        self.log(
            level=level,
            message=error_message,
            component=component,
            exception=exception,
            context=context,
            metadata={
                'exception_module': getattr(type(exception), '__module__', None),
                'exception_args': getattr(exception, 'args', None)
            }
        )
    
    def get_recent_logs(
        self,
        limit: int = 100,
        level_filter: Optional[LogLevel] = None,
        component_filter: Optional[str] = None,
        time_range: Optional[tuple] = None
    ) -> List[LogEntry]:
        """
        Get recent log entries with optional filtering.
        
        Args:
            limit: Maximum number of entries to return
            level_filter: Filter by log level
            component_filter: Filter by component name
            time_range: Tuple of (start_time, end_time) for filtering
            
        Returns:
            List of filtered log entries
        """
        with self._log_lock:
            filtered_logs = []
            
            for entry in reversed(self._log_entries):
                # Apply filters
                if level_filter and entry.level != level_filter:
                    continue
                
                if component_filter and entry.component != component_filter:
                    continue
                
                if time_range:
                    start_time, end_time = time_range
                    if not (start_time <= entry.timestamp <= end_time):
                        continue
                
                filtered_logs.append(entry)
                
                if len(filtered_logs) >= limit:
                    break
            
            return filtered_logs
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get comprehensive logging statistics."""
        with self._log_lock:
            return {
                'total_logs': self._log_stats['total_logs'],
                'logs_by_level': {
                    level.name: count 
                    for level, count in self._log_stats['logs_by_level'].items()
                },
                'logs_by_component': dict(self._log_stats['logs_by_component']),
                'memory_entries': len(self._log_entries),
                'error_patterns': dict(self._log_stats['error_patterns']),
                'log_level': self.log_level.name,
                'log_file': str(self.log_file) if self.log_file else None
            }
    
    def export_logs(
        self,
        filepath: str,
        format: str = "json",
        level_filter: Optional[LogLevel] = None,
        time_range: Optional[tuple] = None
    ) -> bool:
        """
        Export logs to file in specified format.
        
        Args:
            filepath: Output file path
            format: Export format (json, csv, txt)
            level_filter: Optional level filter
            time_range: Optional time range filter
            
        Returns:
            True if export successful
        """
        try:
            # Get filtered logs
            logs = self.get_recent_logs(
                limit=len(self._log_entries),
                level_filter=level_filter,
                time_range=time_range
            )
            
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "json":
                export_data = {
                    'export_timestamp': time.time(),
                    'total_entries': len(logs),
                    'logs': [log.to_dict() for log in logs]
                }
                
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
            
            elif format.lower() == "csv":
                import csv
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'timestamp', 'level', 'component', 'message',
                        'error_id', 'error_code', 'exception_type'
                    ])
                    
                    for log in logs:
                        writer.writerow([
                            log.timestamp,
                            log.level.name,
                            log.component,
                            log.message,
                            log.error_id or '',
                            log.error_code or '',
                            log.exception_type or ''
                        ])
            
            elif format.lower() == "txt":
                with open(filepath, 'w') as f:
                    for log in logs:
                        timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log.timestamp))
                        f.write(f"[{timestamp_str}] {log.level.name} {log.component}: {log.message}\\n")
                        if log.exception_type:
                            f.write(f"  Exception: {log.exception_type}\\n")
                        if log.error_code:
                            f.write(f"  Error Code: {log.error_code}\\n")
                        f.write("\\n")
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            self.info(f"Exported {len(logs)} log entries to {filepath}")
            return True
        
        except Exception as e:
            self.error(f"Failed to export logs: {e}")
            return False
    
    def add_log_filter(self, filter_func: callable) -> None:
        """
        Add a custom log filter function.
        
        Args:
            filter_func: Function that takes LogEntry and returns True to filter out
        """
        self._log_filters.append(filter_func)
    
    def clear_old_logs(self, max_age_hours: float = 24.0) -> int:
        """
        Clear old log entries from memory.
        
        Args:
            max_age_hours: Maximum age of logs to keep
            
        Returns:
            Number of logs cleared
        """
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleared_count = 0
        
        with self._log_lock:
            original_count = len(self._log_entries)
            self._log_entries = [
                entry for entry in self._log_entries
                if entry.timestamp > cutoff_time
            ]
            cleared_count = original_count - len(self._log_entries)
        
        self.info(f"Cleared {cleared_count} old log entries")
        return cleared_count
    
    def _setup_python_logger(self) -> None:
        """Setup Python logging infrastructure."""
        self._python_logger = logging.getLogger('CORTEX')
        self._python_logger.setLevel(self.log_level.value)
        
        # Remove existing handlers
        for handler in self._python_logger.handlers[:]:
            self._python_logger.removeHandler(handler)
        
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level.value)
            
            if self.enable_json_format:
                console_formatter = self._create_json_formatter()
            else:
                console_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            console_handler.setFormatter(console_formatter)
            self._python_logger.addHandler(console_handler)
        
        # File handler
        if self.log_file:
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                filename=self.log_file,
                maxBytes=int(self.max_log_size_mb * 1024 * 1024),
                backupCount=self.backup_count
            )
            file_handler.setLevel(self.log_level.value)
            
            if self.enable_json_format:
                file_formatter = self._create_json_formatter()
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            file_handler.setFormatter(file_formatter)
            self._python_logger.addHandler(file_handler)
    
    def _create_json_formatter(self) -> logging.Formatter:
        """Create JSON formatter for structured logging."""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': record.created,
                    'level': record.levelname,
                    'component': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                if hasattr(record, 'exc_info') and record.exc_info:
                    log_entry['exception'] = {
                        'type': record.exc_info[0].__name__,
                        'message': str(record.exc_info[1]),
                        'traceback': traceback.format_exception(*record.exc_info)
                    }
                
                return json.dumps(log_entry, default=str)
        
        return JSONFormatter()
    
    def _store_log_entry(self, log_entry: LogEntry) -> None:
        """Store log entry in memory with size management."""
        with self._log_lock:
            self._log_entries.append(log_entry)
            
            # Maintain memory limit
            if len(self._log_entries) > self._max_memory_entries:
                # Remove oldest entries
                entries_to_remove = len(self._log_entries) - self._max_memory_entries
                self._log_entries = self._log_entries[entries_to_remove:]
    
    def _log_to_python_logger(self, log_entry: LogEntry) -> None:
        """Log to Python logging system."""
        # Map custom log levels to Python levels
        level_mapping = {
            LogLevel.TRACE: logging.DEBUG,
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
            LogLevel.EMERGENCY: logging.CRITICAL
        }
        
        python_level = level_mapping.get(log_entry.level, logging.INFO)
        
        # Create log message
        message = log_entry.message
        if log_entry.error_code:
            message = f"[{log_entry.error_code}] {message}"
        
        # Log with context
        extra = {
            'component': log_entry.component,
            'error_id': log_entry.error_id,
            'error_code': log_entry.error_code,
            'context': log_entry.context,
            'metadata': log_entry.metadata
        }
        
        self._python_logger.log(python_level, message, extra=extra)
    
    def _update_log_statistics(self, log_entry: LogEntry) -> None:
        """Update logging statistics."""
        with self._log_lock:
            self._log_stats['total_logs'] += 1
            self._log_stats['logs_by_level'][log_entry.level] += 1
            
            # Component statistics
            if log_entry.component not in self._log_stats['logs_by_component']:
                self._log_stats['logs_by_component'][log_entry.component] = 0
            self._log_stats['logs_by_component'][log_entry.component] += 1
            
            # Error pattern tracking
            if log_entry.error_code:
                if log_entry.error_code not in self._log_stats['error_patterns']:
                    self._log_stats['error_patterns'][log_entry.error_code] = 0
                self._log_stats['error_patterns'][log_entry.error_code] += 1
    
    def _should_filter_log(self, log_entry: LogEntry) -> bool:
        """Check if log entry should be filtered out."""
        for filter_func in self._log_filters:
            try:
                if filter_func(log_entry):
                    return True
            except Exception as e:
                # Don't let filter errors prevent logging
                continue
        return False
    
    def _sanitize_message(self, message: str) -> str:
        """Remove sensitive information from log message."""
        import re
        sanitized = message
        
        for pattern in self._sensitive_patterns:
            sanitized = re.sub(pattern, r'***REDACTED***', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from dictionary."""
        sanitized = {}
        sensitive_keys = ['password', 'token', 'api_key', 'secret', 'auth', 'credential']
        
        for key, value in data.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            else:
                sanitized[key] = value
        
        return sanitized


# Global error logger instance
default_error_logger = ErrorLogger()