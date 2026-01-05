"""
CORTEX Audit Logging System.

Purpose: Track handoffs, execution flow, and performance metrics for CORTEX accuracy measurement.
Version: 1.0.0
Phase: 28 (GREEN phase implementation)
"""

import json
import logging
import logging.handlers
import re
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional


class AuditLogger:
    """
    Core audit logging infrastructure for CORTEX.
    
    Features:
    - Structured JSON logging (JSON Lines format)
    - Daily rotation with configurable backup count
    - Sensitive data redaction (API keys, passwords, tokens)
    - Context managers for request lifecycle tracking
    - Performance decorators (@timed, @logged)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize audit logger with configuration.
        
        Args:
            config: Configuration dictionary with keys:
                - log_dir: Directory for log files
                - rotation_size_mb: Size threshold for rotation (default: 10MB)
                - backup_count: Number of backup files (default: 5)
                - retention_days: Days to retain logs (default: 30)
        """
        self.log_dir = Path(config.get("log_dir", "logs/cortex-audit"))
        self.rotation_size_mb = config.get("rotation_size_mb", 10)
        self.backup_count = config.get("backup_count", 5)
        self.retention_days = config.get("retention_days", 30)
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Patterns for sensitive data redaction
        self.sensitive_patterns = {
            "api_key": re.compile(r'(sk-[a-zA-Z0-9]{32,})', re.IGNORECASE),
            "password": re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)', re.IGNORECASE),
            "token": re.compile(r'(gh[ps]_[a-zA-Z0-9]{36,})', re.IGNORECASE),
            "secret": re.compile(r'(secret["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)', re.IGNORECASE),
        }
    
    def _get_log_file(self, event_type: str) -> Path:
        """Get log file path for event type with daily rotation."""
        date_str = datetime.now().strftime('%Y-%m-%d')
        # Pluralize event type unless it's "performance" (already ends in 'e')
        plural = event_type if event_type == "performance" else f"{event_type}s"
        return self.log_dir / f"{plural}-{date_str}.jsonl"
    
    def _redact_sensitive_data(self, data: Any) -> Any:
        """Recursively redact sensitive data from logs."""
        if isinstance(data, dict):
            redacted_dict = {}
            for k, v in data.items():
                # Check if key indicates sensitive data
                if k.lower() in ['api_key', 'password', 'token', 'secret', 'auth', 'authorization']:
                    redacted_dict[k] = '***REDACTED***'
                else:
                    redacted_dict[k] = self._redact_sensitive_data(v)
            return redacted_dict
        elif isinstance(data, list):
            return [self._redact_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            # Apply redaction patterns
            redacted = data
            for pattern_name, pattern in self.sensitive_patterns.items():
                if pattern_name == "password" or pattern_name == "secret":
                    # Preserve key, redact value
                    redacted = pattern.sub(r'\1***REDACTED***', redacted)
                else:
                    # Redact entire match
                    redacted = pattern.sub('***REDACTED***', redacted)
            return redacted
        return data
    
    def _write_log_entry(self, event_type: str, context: Dict[str, Any], data: Dict[str, Any]):
        """Write JSON log entry to file."""
        log_file = self._get_log_file(event_type)
        
        # Build log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "context": context,
            "data": self._redact_sensitive_data(data)
        }
        
        # Append to log file
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Check for rotation
        if log_file.stat().st_size > self.rotation_size_mb * 1024 * 1024:
            self._rotate_log_file(log_file)
    
    def _rotate_log_file(self, log_file: Path):
        """Rotate log file when size threshold reached."""
        # Find existing backup files
        backups = sorted(log_file.parent.glob(f"{log_file.stem}.*.jsonl"), reverse=True)
        
        # Rotate existing backups
        for backup in backups:
            # Extract number from filename (e.g., handoffs-2026-01-05.1.jsonl -> 1)
            parts = backup.stem.split('.')
            if len(parts) >= 2 and parts[-1].isdigit():
                num = int(parts[-1])
                if num < self.backup_count:
                    new_name = f"{'.'.join(parts[:-1])}.{num + 1}.jsonl"
                    backup.rename(backup.parent / new_name)
                else:
                    backup.unlink()  # Delete oldest backup
        
        # Rotate current file to .1
        log_file.rename(log_file.parent / f"{log_file.stem}.1.jsonl")
    
    def log_handoff(self, request_id: str, orchestrator: str, data: Dict[str, Any]):
        """
        Log handoff event (Copilot → Python routing).
        
        Args:
            request_id: Unique request identifier
            orchestrator: Target orchestrator name
            data: Event data (pattern, confidence, transformation, etc.)
        """
        context = {
            "request_id": request_id,
            "orchestrator": orchestrator,
            "plan_id": None,
            "phase_number": None
        }
        self._write_log_entry("handoff", context, data)
    
    def log_execution(self, plan_id: str, orchestrator: str, data: Dict[str, Any]):
        """
        Log execution event (phase start/end, validation).
        
        Args:
            plan_id: Plan identifier
            orchestrator: Orchestrator name
            data: Event data (phase_number, status, outputs, etc.)
        """
        context = {
            "request_id": data.get("request_id"),
            "orchestrator": orchestrator,
            "plan_id": plan_id,
            "phase_number": data.get("phase_number")
        }
        self._write_log_entry("execution", context, data)
    
    def log_performance(self, request_id: str, metric_name: str, value: float, unit: str):
        """
        Log performance metric.
        
        Args:
            request_id: Request identifier
            metric_name: Metric name (e.g., "import_time")
            value: Metric value
            unit: Unit of measurement (e.g., "ms", "seconds")
        """
        context = {
            "request_id": request_id,
            "orchestrator": None,
            "plan_id": None,
            "phase_number": None
        }
        data = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit
        }
        self._write_log_entry("performance", context, data)
    
    def log_error(self, request_id: str, orchestrator: str, error_data: Dict[str, Any]):
        """
        Log error event.
        
        Args:
            request_id: Request identifier
            orchestrator: Orchestrator name
            error_data: Error details (type, message, stack trace, remediation)
        """
        context = {
            "request_id": request_id,
            "orchestrator": orchestrator,
            "plan_id": error_data.get("plan_id"),
            "phase_number": error_data.get("phase")
        }
        self._write_log_entry("error", context, error_data)
    
    @contextmanager
    def audit_context(self, request_id: str, orchestrator: str):
        """
        Context manager for request lifecycle tracking.
        
        Usage:
            with logger.audit_context("req-123", "planning_v5") as ctx:
                ctx.add_data("pattern", "plan")
                # ... do work ...
        
        Automatically logs handoff event on exit with duration.
        """
        class AuditContext:
            def __init__(self, logger, request_id, orchestrator):
                self.logger = logger
                self.request_id = request_id
                self.orchestrator = orchestrator
                self.data = {}
                self.start_time = time.time()
            
            def add_data(self, key: str, value: Any):
                """Add data to context."""
                self.data[key] = value
        
        ctx = AuditContext(self, request_id, orchestrator)
        
        try:
            yield ctx
        finally:
            # Calculate duration
            duration_ms = (time.time() - ctx.start_time) * 1000
            ctx.data["duration_ms"] = duration_ms
            
            # Log handoff event
            self.log_handoff(ctx.request_id, ctx.orchestrator, ctx.data)


def timed(logger: AuditLogger, function_name: str):
    """
    Decorator to log function execution time.
    
    Usage:
        @timed(logger, "my_function")
        def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log performance metric
            request_id = kwargs.get("request_id", str(uuid.uuid4()))
            logger.log_performance(
                request_id=request_id,
                metric_name=f"{function_name}_duration",
                value=duration_ms,
                unit="ms"
            )
            
            return result
        return wrapper
    return decorator


def logged(logger: AuditLogger, orchestrator: str):
    """
    Decorator to log function calls.
    
    Usage:
        @logged(logger, "planning_v5")
        def process_plan(arg1, arg2):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Log execution start
            data = {
                "function": func.__name__,
                "args": args,
                "kwargs": list(kwargs.keys())  # Don't log values (may be sensitive)
            }
            
            request_id = kwargs.get("request_id", str(uuid.uuid4()))
            logger.log_execution(
                plan_id=kwargs.get("plan_id", "unknown"),
                orchestrator=orchestrator,
                data={**data, "request_id": request_id, "status": "started"}
            )
            
            # Execute function
            try:
                result = func(*args, **kwargs)
                
                # Log execution success
                logger.log_execution(
                    plan_id=kwargs.get("plan_id", "unknown"),
                    orchestrator=orchestrator,
                    data={**data, "request_id": request_id, "status": "complete"}
                )
                
                return result
            except Exception as e:
                # Log execution failure
                logger.log_error(
                    request_id=request_id,
                    orchestrator=orchestrator,
                    error_data={
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "function": func.__name__
                    }
                )
                raise
        
        return wrapper
    return decorator


# Singleton instance for easy access
_audit_logger_instance: Optional[AuditLogger] = None


def get_audit_logger(config: Optional[Dict[str, Any]] = None) -> AuditLogger:
    """
    Get or create singleton audit logger instance.
    
    Args:
        config: Configuration dictionary (only used on first call)
    
    Returns:
        AuditLogger instance
    """
    global _audit_logger_instance
    
    if _audit_logger_instance is None:
        if config is None:
            config = {"log_dir": "logs/cortex-audit"}
        _audit_logger_instance = AuditLogger(config)
    
    return _audit_logger_instance
