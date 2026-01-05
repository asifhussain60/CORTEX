"""
Enterprise Audit Logger - Core Implementation.

Features:
- Async logging with minimal overhead (<5ms per operation)
- Structured JSONL format
- Daily rotation
- Sensitive data redaction
- Context propagation (session_id, correlation_id)
- Graceful error handling
"""

import asyncio
import json
import logging
import re
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, List
from contextvars import ContextVar

from .log_buffer import LogBuffer
from .log_writer import LogWriter


logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Context variables for propagation across async calls
_session_context: ContextVar[Optional[str]] = ContextVar('session_id', default=None)
_correlation_context: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
_metadata_context: ContextVar[Optional[Dict]] = ContextVar('metadata', default=None)


class AuditLogger:
    """
    Enterprise audit logger with async capabilities and self-healing integration.
    
    Architecture:
    - LogBuffer: In-memory buffer with automatic flushing
    - LogWriter: Async disk I/O with rotation and compression
    - Context propagation via ContextVars (async-safe)
    - Sensitive data redaction via regex patterns
    
    Performance:
    - Target: <5ms overhead per operation
    - Achieved via async I/O and buffering
    - Batch writes for efficiency
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize audit logger.
        
        Args:
            config: Configuration dictionary:
                - log_dir: Base directory for logs
                - buffer_size: Buffer entries before flush (default: 1000)
                - flush_interval: Seconds between auto-flushes (default: 5.0)
                - rotation_size_mb: Size threshold for rotation (default: 10)
                - backup_count: Number of backup files (default: 5)
                - retention_days: Days to retain logs (default: 30)
                - async_enabled: Enable async logging (default: True)
                - compression_enabled: Enable gzip compression (default: True)
        """
        self.log_dir = Path(config.get("log_dir", "logs/cortex-audit"))
        self.buffer_size = config.get("buffer_size", 1000)
        self.flush_interval = config.get("flush_interval", 5.0)
        self.async_enabled = config.get("async_enabled", True)
        
        # Create audit log directory
        (self.log_dir / "audit").mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.buffer = LogBuffer(
            max_size=self.buffer_size,
            flush_interval=self.flush_interval
        )
        
        self.writer = LogWriter({
            "log_dir": str(self.log_dir / "audit"),
            "rotation_size_mb": config.get("rotation_size_mb", 10),
            "backup_count": config.get("backup_count", 5),
            "compression_enabled": config.get("compression_enabled", True)
        })
        
        # Set buffer flush callback
        self.buffer.set_flush_callback(self._flush_callback)
        
        # Sensitive data patterns
        self.sensitive_patterns = {
            "api_key": re.compile(r'sk-[a-zA-Z0-9]{32,}', re.IGNORECASE),
            "password": re.compile(r'(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', re.IGNORECASE),
            "token": re.compile(r'gh[ps]_[a-zA-Z0-9]{36,}', re.IGNORECASE),
            "secret": re.compile(r'(?:secret|api_secret)["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', re.IGNORECASE),
        }
        
        # Error tracking
        self.error_count = 0
        
        # Event cache for self-healing engine
        self._event_cache: List[Dict[str, Any]] = []
        self._max_cache_size = 1000  # Keep last 1000 events
        
        # Background flush task
        self._flush_task: Optional[asyncio.Task] = None
        if self.async_enabled:
            self._start_flush_task()
    
    def _start_flush_task(self):
        """Start background flush task."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._flush_task = loop.create_task(self._periodic_flush())
        except RuntimeError:
            # No event loop, will flush synchronously
            pass
    
    async def _periodic_flush(self):
        """Periodically flush buffer to disk."""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic flush error: {e}")
                self.error_count += 1
    
    async def _flush_callback(self, entries: List[Dict[str, Any]]):
        """
        Callback invoked when buffer needs flushing.
        
        Args:
            entries: Log entries to write
        """
        try:
            await self.writer.write_batch(entries)
        except Exception as e:
            logger.error(f"Flush callback error: {e}")
            self.error_count += 1
    
    def _redact_sensitive_data(self, data: Any) -> Any:
        """
        Recursively redact sensitive data.
        
        Args:
            data: Data structure to redact
            
        Returns:
            Redacted data structure
        """
        if isinstance(data, dict):
            redacted = {}
            for k, v in data.items():
                # Check if key indicates sensitive data
                if k.lower() in ['api_key', 'password', 'passwd', 'pwd', 'token', 'secret', 'auth', 'authorization']:
                    redacted[k] = '***REDACTED***'
                else:
                    redacted[k] = self._redact_sensitive_data(v)
            return redacted
        elif isinstance(data, list):
            return [self._redact_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            # Apply pattern-based redaction
            redacted = data
            for pattern_name, pattern in self.sensitive_patterns.items():
                redacted = pattern.sub('***REDACTED***', redacted)
            return redacted
        return data
    
    def _build_log_entry(
        self,
        level: LogLevel,
        orchestrator: str,
        event: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build structured log entry.
        
        Args:
            level: Log severity level
            orchestrator: Orchestrator name
            event: Event identifier
            data: Event data
            
        Returns:
            Structured log entry
        """
        # Get context
        session_id = _session_context.get() or str(uuid.uuid4())
        correlation_id = _correlation_context.get() or str(uuid.uuid4())
        metadata = _metadata_context.get() or {}
        
        # Redact sensitive data
        safe_data = self._redact_sensitive_data(data)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "orchestrator": orchestrator,
            "event": event,
            "data": safe_data,
            "session_id": session_id,
            "correlation_id": correlation_id,
            "metadata": metadata
        }
    
    async def log(
        self,
        level: LogLevel,
        orchestrator: str,
        event: str,
        data: Dict[str, Any]
    ):
        """
        Log entry asynchronously.
        
        Args:
            level: Log severity level
            orchestrator: Orchestrator name
            event: Event identifier
            data: Event data
        """
        try:
            entry = self._build_log_entry(level, orchestrator, event, data)
            await self.buffer.add(entry)
            
            # Add to event cache for self-healing engine
            self._event_cache.append(entry)
            # Keep cache size under limit
            if len(self._event_cache) > self._max_cache_size:
                self._event_cache = self._event_cache[-self._max_cache_size:]
        except Exception as e:
            logger.error(f"Async log error: {e}")
            self.error_count += 1
    
    def log_sync(
        self,
        level: LogLevel,
        orchestrator: str,
        event: str,
        data: Dict[str, Any]
    ):
        """
        Log entry synchronously (blocking).
        
        Args:
            level: Log severity level
            orchestrator: Orchestrator name
            event: Event identifier
            data: Event data
        """
        try:
            entry = self._build_log_entry(level, orchestrator, event, data)
            # Add to buffer synchronously
            self.buffer.add_sync(entry)
        except Exception as e:
            logger.error(f"Sync log error: {e}")
            self.error_count += 1
    
    async def flush(self):
        """Flush buffer to disk asynchronously."""
        try:
            entries = await self.buffer.flush()
            if entries:
                await self.writer.write_batch(entries)
        except Exception as e:
            logger.error(f"Async flush error: {e}")
            self.error_count += 1
    
    def flush_sync(self):
        """Flush buffer to disk synchronously."""
        try:
            entries = self.buffer.flush_sync()
            if entries:
                # Write synchronously
                self.writer.write_batch_sync(entries)
        except Exception as e:
            logger.error(f"Sync flush error: {e}")
            self.error_count += 1
    
    def set_context(
        self,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Set context for subsequent log entries.
        
        Args:
            session_id: Session identifier
            correlation_id: Correlation identifier
            metadata: Additional metadata
        """
        if session_id:
            _session_context.set(session_id)
        if correlation_id:
            _correlation_context.set(correlation_id)
        if metadata:
            _metadata_context.set(metadata)
    
    @contextmanager
    def context(
        self,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for scoped logging context.
        
        Args:
            session_id: Session identifier
            correlation_id: Correlation identifier
            metadata: Additional metadata
            
        Yields:
            None
        """
        # Store previous context
        prev_session = _session_context.get()
        prev_correlation = _correlation_context.get()
        prev_metadata = _metadata_context.get()
        
        # Set new context
        self.set_context(session_id, correlation_id, metadata)
        
        try:
            yield
        finally:
            # Restore previous context
            if prev_session:
                _session_context.set(prev_session)
            if prev_correlation:
                _correlation_context.set(prev_correlation)
            if prev_metadata:
                _metadata_context.set(prev_metadata)
    
    async def close(self):
        """Close logger and cleanup resources."""
        # Cancel flush task
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        await self.flush()
        
        # Close writer
        await self.writer.close()
    
    def close_sync(self):
        """Close logger synchronously."""
        self.flush_sync()
        self.writer.close_sync()
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            if self.buffer and not self.buffer.is_empty:
                self.flush_sync()
        except Exception:
            pass
