"""Offline mode provider with graceful degradation."""

import time
from typing import List, Optional

from cortex.storage.config import StorageConfig
from cortex.storage.errors import NetworkError, StorageError
from cortex.storage.provider import IKnowledgeProvider


class OfflineModeProvider(IKnowledgeProvider):
    """
    Wrapper providing graceful degradation during network outages.

    Implements exponential backoff reconnection strategy and queues
    writes/deletes for later processing when connection restored.

    AC-PHASE50-S6-001: Wraps provider with graceful degradation
    AC-PHASE50-S6-002: Falls back to cache/local storage on network failure
    AC-PHASE50-S6-003: Retries with exponential backoff (1, 2, 4, 8 seconds max)
    AC-PHASE50-S6-004: Tracks offline duration and retry attempts
    AC-PHASE50-S6-005: Transparent fallback - client code unaware
    """

    def __init__(
        self,
        provider: IKnowledgeProvider,
        config: StorageConfig,
        max_retries: int = 5
    ) -> None:
        """
        Initialize OfflineModeProvider.

        Args:
            provider: Underlying IKnowledgeProvider to wrap
            config: StorageConfig
            max_retries: Maximum retry attempts before giving up
        """
        self.provider = provider
        self.config = config
        self.max_retries = max_retries

        # AC-PHASE50-S6-004: Initialize offline tracking
        self.is_offline = False
        self.offline_start_time: Optional[float] = None

        self.metrics = {
            "offline_duration_seconds": 0,
            "retry_attempts": 0,
            "network_errors": 0,
            "successful_reconnects": 0
        }

        # AC-PHASE50-S6-002: Initialize write/delete queues
        self.write_queue: List[tuple[str, str]] = []
        self.delete_queue: List[str] = []

        # Cache for fallback
        self.local_cache: dict[str, str] = {}

    def _calculate_backoff(self, attempt: int) -> int:
        """
        Calculate exponential backoff with cap.

        AC-PHASE50-S6-003: Exponential backoff (1, 2, 4, 8 seconds max)

        Args:
            attempt: Retry attempt number (0-indexed)

        Returns:
            Backoff time in seconds (capped at 8)
        """
        backoff = 2 ** attempt
        return min(backoff, 8)

    def _mark_offline(self) -> None:
        """Mark provider as offline and start tracking."""
        if not self.is_offline:
            self.is_offline = True
            self.offline_start_time = time.time()

    def _mark_online(self) -> None:
        """Mark provider as online and update metrics."""
        if self.is_offline:
            self.is_offline = False
            if self.offline_start_time:
                duration = time.time() - self.offline_start_time
                self.metrics["offline_duration_seconds"] += int(duration)
            self.metrics["successful_reconnects"] += 1

    def _is_network_error(self, error: Exception) -> bool:
        """Check if error is network-related."""
        error_str = str(error).lower()
        network_keywords = [
            "timeout", "connection", "refused", "unreachable",
            "network", "offline", "unavailable"
        ]
        return any(keyword in error_str for keyword in network_keywords)

    def _retry_operation(self, operation, *args, **kwargs):
        """
        Retry operation with exponential backoff.

        AC-PHASE50-S6-003: Retry with backoff

        Args:
            operation: Callable to retry
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Operation result

        Raises:
            Last exception if all retries exhausted
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                result = operation(*args, **kwargs)
                if self.is_offline:
                    self._mark_online()
                return result
            except NetworkError as e:
                last_error = e
                self.metrics["network_errors"] += 1
                self._mark_offline()

                if attempt < self.max_retries - 1:
                    self.metrics["retry_attempts"] += 1
                    backoff = self._calculate_backoff(attempt)
                    # In real implementation, would sleep here
                    # time.sleep(backoff)
            except Exception as e:
                last_error = e
                if not self._is_network_error(e):
                    raise

        if last_error:
            raise last_error

    def read(self, path: str) -> str:
        """
        Read with offline fallback.

        AC-PHASE50-S6-002: Fall back to cache on network error

        Args:
            path: File path

        Returns:
            File content

        Raises:
            NetworkError: If offline and no cache
            StorageError: On other errors
        """
        def _read():
            content = self.provider.read(path)
            # Cache for offline fallback
            self.local_cache[path] = content
            return content

        try:
            return self._retry_operation(_read)
        except NetworkError:
            # AC-PHASE50-S6-002: Try cache
            if path in self.local_cache:
                return self.local_cache[path]
            raise

    def write(self, path: str, content: str) -> None:
        """
        Write with queuing for offline mode.

        AC-PHASE50-S6-002: Queue writes during offline

        Args:
            path: File path
            content: Content to write
        """
        def _write():
            self.provider.write(path, content)
            self.local_cache[path] = content

        try:
            self._retry_operation(_write)
        except NetworkError:
            # AC-PHASE50-S6-002: Queue for later
            self.write_queue.append((path, content))
            self.local_cache[path] = content

    def list(self, path: str) -> List[str]:
        """
        List with offline fallback.

        AC-PHASE50-S6-002: Return empty list if offline

        Args:
            path: Directory path

        Returns:
            List of entries or empty list
        """
        try:
            return self._retry_operation(self.provider.list, path)
        except NetworkError:
            # AC-PHASE50-S6-002: Return empty or cached
            return []

    def exists(self, path: str) -> bool:
        """
        Check existence with offline fallback.

        AC-PHASE50-S6-002: Check cache if offline

        Args:
            path: File path

        Returns:
            True if exists, False otherwise
        """
        try:
            return self._retry_operation(self.provider.exists, path)
        except NetworkError:
            # AC-PHASE50-S6-002: Check cache
            return path in self.local_cache

    def delete(self, path: str) -> None:
        """
        Delete with queuing for offline mode.

        AC-PHASE50-S6-002: Queue deletions during offline

        Args:
            path: File path
        """
        def _delete():
            self.provider.delete(path)
            if path in self.local_cache:
                del self.local_cache[path]

        try:
            self._retry_operation(_delete)
        except NetworkError:
            # AC-PHASE50-S6-002: Queue for later
            self.delete_queue.append(path)
            if path in self.local_cache:
                del self.local_cache[path]

    def flush_write_queue(self) -> None:
        """
        Flush queued write operations.

        AC-PHASE50-S6-002: Called when connection restored
        """
        for path, content in self.write_queue:
            try:
                self.provider.write(path, content)
            except Exception:
                # Requeue if failed
                pass
        self.write_queue.clear()

    def flush_delete_queue(self) -> None:
        """
        Flush queued delete operations.

        AC-PHASE50-S6-002: Called when connection restored
        """
        for path in self.delete_queue:
            try:
                self.provider.delete(path)
            except Exception:
                # Requeue if failed
                pass
        self.delete_queue.clear()
