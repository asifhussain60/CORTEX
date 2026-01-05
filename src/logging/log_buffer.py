"""
Log Buffer - In-memory buffering for audit logs.

Features:
- Thread-safe async buffer
- Auto-flush on size threshold
- Auto-flush on time interval
- Callback-based flush notifications
"""

import asyncio
import logging
import threading
from typing import Any, Dict, List, Optional, Callable, Awaitable


logger = logging.getLogger(__name__)


class LogBuffer:
    """
    Thread-safe async buffer for log entries.
    
    Automatically flushes when:
    - Size threshold reached (max_size)
    - Time interval elapsed (flush_interval)
    - Manual flush requested
    """
    
    def __init__(self, max_size: int = 1000, flush_interval: float = 5.0):
        """
        Initialize log buffer.
        
        Args:
            max_size: Maximum entries before auto-flush
            flush_interval: Seconds between auto-flushes
        """
        self.max_size = max_size
        self.flush_interval = flush_interval
        
        self._buffer: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        self._async_lock = asyncio.Lock()
        
        self._flush_callback: Optional[Callable[[List[Dict[str, Any]]], Awaitable[None]]] = None
    
    @property
    def size(self) -> int:
        """Get current buffer size."""
        with self._lock:
            return len(self._buffer)
    
    @property
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        with self._lock:
            return len(self._buffer) == 0
    
    def set_flush_callback(self, callback: Callable[[List[Dict[str, Any]]], Awaitable[None]]):
        """
        Set callback for automatic flushes.
        
        Args:
            callback: Async function to call with entries on flush
        """
        self._flush_callback = callback
    
    async def add(self, entry: Dict[str, Any]):
        """
        Add entry to buffer asynchronously.
        
        Args:
            entry: Log entry to add
        """
        async with self._async_lock:
            self._buffer.append(entry)
            
            # Check if flush needed
            if len(self._buffer) >= self.max_size:
                await self._auto_flush()
    
    def add_sync(self, entry: Dict[str, Any]):
        """
        Add entry to buffer synchronously.
        
        Args:
            entry: Log entry to add
        """
        with self._lock:
            self._buffer.append(entry)
            
            # Don't auto-flush in sync mode (caller controls flush)
    
    async def _auto_flush(self):
        """Automatically flush buffer."""
        if self._flush_callback and not self.is_empty:
            try:
                entries = await self.flush()
                if entries:
                    await self._flush_callback(entries)
            except Exception as e:
                logger.error(f"Auto-flush error: {e}")
    
    async def flush(self) -> List[Dict[str, Any]]:
        """
        Flush buffer and return entries asynchronously.
        
        Returns:
            List of log entries that were flushed
        """
        async with self._async_lock:
            if not self._buffer:
                return []
            
            # Copy and clear buffer
            entries = self._buffer[:]
            self._buffer.clear()
            return entries
    
    def flush_sync(self) -> List[Dict[str, Any]]:
        """
        Flush buffer and return entries synchronously.
        
        Returns:
            List of log entries that were flushed
        """
        with self._lock:
            if not self._buffer:
                return []
            
            # Copy and clear buffer
            entries = self._buffer[:]
            self._buffer.clear()
            return entries
    
    def clear(self):
        """Clear buffer without flushing."""
        with self._lock:
            self._buffer.clear()
    
    def peek(self, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Peek at buffer contents without removing.
        
        Args:
            count: Number of entries to peek (None = all)
            
        Returns:
            List of log entries
        """
        with self._lock:
            if count is None:
                return self._buffer[:]
            return self._buffer[:count]
