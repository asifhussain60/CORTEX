"""
Turn timeout and cancellation handling for conversations.

Implements per-turn timeouts with graceful cleanup and user cancellation.
"""

import asyncio
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import signal
import sys


@dataclass
class TimeoutConfig:
    """Configuration for turn timeouts."""
    
    timeout_seconds: float = 300.0  # 5 minutes default
    enable_cancellation: bool = True
    cleanup_callback: Optional[Callable[[], None]] = None


class TurnTimeoutError(Exception):
    """Raised when a turn exceeds its timeout."""
    
    def __init__(self, turn_number: int, elapsed_seconds: float):
        self.turn_number = turn_number
        self.elapsed_seconds = elapsed_seconds
        super().__init__(
            f"Turn {turn_number} exceeded timeout after {elapsed_seconds:.1f}s"
        )


class TurnCancelledError(Exception):
    """Raised when a turn is cancelled by user."""
    
    def __init__(self, turn_number: int):
        self.turn_number = turn_number
        super().__init__(f"Turn {turn_number} was cancelled by user")


class TurnTimeoutManager:
    """
    Manages timeouts and cancellation for conversation turns.
    
    Provides:
    - Per-turn timeout enforcement
    - User cancellation via signal
    - Graceful cleanup on timeout/cancellation
    - Audit trail for incomplete turns
    """
    
    def __init__(self, config: Optional[TimeoutConfig] = None):
        """
        Initialize timeout manager.
        
        Args:
            config: Timeout configuration
        """
        self.config = config or TimeoutConfig()
        self._cancellation_requested = False
        self._current_turn_number: Optional[int] = None
        self._setup_cancellation_handler()
    
    def _setup_cancellation_handler(self) -> None:
        """Set up signal handler for user cancellation."""
        if self.config.enable_cancellation and sys.platform != "win32":
            # Unix-like systems support SIGINT
            signal.signal(signal.SIGINT, self._handle_cancellation)
    
    def _handle_cancellation(self, signum, frame) -> None:
        """Handle cancellation signal."""
        self._cancellation_requested = True
        print(f"\n[CANCELLATION REQUESTED for turn {self._current_turn_number}]")
    
    def check_cancellation(self) -> None:
        """
        Check if cancellation was requested.
        
        Raises:
            TurnCancelledError: If cancellation was requested
        """
        if self._cancellation_requested and self._current_turn_number is not None:
            raise TurnCancelledError(self._current_turn_number)
    
    async def execute_with_timeout(
        self,
        turn_number: int,
        coro: Callable[[], Any],
        timeout_override: Optional[float] = None
    ) -> Any:
        """
        Execute a coroutine with timeout.
        
        Args:
            turn_number: Current turn number
            coro: Coroutine to execute
            timeout_override: Optional timeout override
            
        Returns:
            Result from coroutine
            
        Raises:
            TurnTimeoutError: If timeout exceeded
            TurnCancelledError: If user cancelled
        """
        self._current_turn_number = turn_number
        self._cancellation_requested = False
        
        timeout = timeout_override or self.config.timeout_seconds
        start_time = datetime.now()
        
        try:
            result = await asyncio.wait_for(coro(), timeout=timeout)
            return result
        except asyncio.TimeoutError:
            elapsed = (datetime.now() - start_time).total_seconds()
            self._run_cleanup()
            raise TurnTimeoutError(turn_number, elapsed)
        except TurnCancelledError:
            self._run_cleanup()
            raise
        finally:
            self._current_turn_number = None
    
    def execute_sync_with_timeout(
        self,
        turn_number: int,
        func: Callable[[], Any],
        timeout_override: Optional[float] = None
    ) -> Any:
        """
        Execute a synchronous function with timeout.
        
        Args:
            turn_number: Current turn number
            func: Function to execute
            timeout_override: Optional timeout override
            
        Returns:
            Result from function
            
        Raises:
            TurnTimeoutError: If timeout exceeded
            TurnCancelledError: If user cancelled
        """
        self._current_turn_number = turn_number
        self._cancellation_requested = False
        
        timeout = timeout_override or self.config.timeout_seconds
        start_time = datetime.now()
        
        async def wrapper():
            return func()
        
        try:
            # Run in new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    asyncio.wait_for(wrapper(), timeout=timeout)
                )
                return result
            finally:
                loop.close()
        except asyncio.TimeoutError:
            elapsed = (datetime.now() - start_time).total_seconds()
            self._run_cleanup()
            raise TurnTimeoutError(turn_number, elapsed)
        except TurnCancelledError:
            self._run_cleanup()
            raise
        finally:
            self._current_turn_number = None
    
    def _run_cleanup(self) -> None:
        """Run cleanup callback if configured."""
        if self.config.cleanup_callback:
            try:
                self.config.cleanup_callback()
            except Exception as e:
                print(f"[WARNING] Cleanup callback failed: {e}")
    
    def reset_cancellation(self) -> None:
        """Reset cancellation flag."""
        self._cancellation_requested = False
    
    def is_cancellation_requested(self) -> bool:
        """Check if cancellation was requested."""
        return self._cancellation_requested


class TurnAuditLogger:
    """Logs incomplete turns for audit trail."""
    
    def __init__(self, log_path: Optional[str] = None):
        """
        Initialize audit logger.
        
        Args:
            log_path: Path to audit log file
        """
        from pathlib import Path
        
        if log_path is None:
            log_path = Path(__file__).parent.parent.parent.parent.parent / "cortex_brain" / "state" / "incomplete_turns.log"
        
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_timeout(
        self,
        turn_number: int,
        elapsed_seconds: float,
        context: Dict[str, Any]
    ) -> None:
        """
        Log a timeout event.
        
        Args:
            turn_number: Turn number
            elapsed_seconds: Time elapsed before timeout
            context: Context at time of timeout
        """
        timestamp = datetime.now().isoformat()
        
        with open(self.log_path, "a") as f:
            f.write(f"[{timestamp}] TIMEOUT turn={turn_number} elapsed={elapsed_seconds:.1f}s\n")
            f.write(f"  Context: {context}\n\n")
    
    def log_cancellation(
        self,
        turn_number: int,
        context: Dict[str, Any]
    ) -> None:
        """
        Log a cancellation event.
        
        Args:
            turn_number: Turn number
            context: Context at time of cancellation
        """
        timestamp = datetime.now().isoformat()
        
        with open(self.log_path, "a") as f:
            f.write(f"[{timestamp}] CANCELLED turn={turn_number}\n")
            f.write(f"  Context: {context}\n\n")
