"""
CORTEX Progress Monitoring System
Purpose: Provide real-time feedback for long-running operations and detect hung processes

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0
"""

import time
import threading
from typing import Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ProgressState:
    """Current state of a monitored operation"""
    operation_name: str
    started_at: datetime
    current_step: str
    current_index: int = 0
    total_items: int = 0
    last_update: datetime = None
    completed: bool = False
    
    @property
    def elapsed_seconds(self) -> float:
        """Total elapsed time in seconds"""
        return (datetime.now() - self.started_at).total_seconds()
    
    @property
    def seconds_since_update(self) -> float:
        """Seconds since last progress update"""
        if self.last_update is None:
            return self.elapsed_seconds
        return (datetime.now() - self.last_update).total_seconds()
    
    @property
    def progress_percent(self) -> float:
        """Progress percentage (0-100)"""
        if self.total_items == 0:
            return 0.0
        return (self.current_index / self.total_items) * 100
    
    @property
    def eta_seconds(self) -> Optional[float]:
        """Estimated time remaining in seconds"""
        if self.current_index == 0 or self.total_items == 0:
            return None
        
        items_per_second = self.current_index / self.elapsed_seconds
        remaining_items = self.total_items - self.current_index
        
        if items_per_second > 0:
            return remaining_items / items_per_second
        return None


class ProgressMonitor:
    """
    Monitor long-running operations with real-time feedback and hang detection.
    
    Features:
    - Real-time progress updates
    - Hang detection (configurable timeout)
    - ETA calculation
    - Automatic cleanup
    - Thread-safe
    
    Usage:
        monitor = ProgressMonitor("System Alignment", hang_timeout_seconds=30)
        monitor.start()
        
        for i, item in enumerate(items, 1):
            monitor.update("Processing files", i, len(items))
            # Do work...
        
        monitor.complete()
    """
    
    def __init__(
        self,
        operation_name: str,
        hang_timeout_seconds: float = 30.0,
        update_interval_seconds: float = 2.0,
        on_hang_detected: Optional[Callable] = None
    ):
        """
        Initialize progress monitor.
        
        Args:
            operation_name: Name of operation being monitored
            hang_timeout_seconds: Seconds without update before considered hung (default: 30)
            update_interval_seconds: Seconds between progress displays (default: 2)
            on_hang_detected: Optional callback when hang detected
        """
        self.operation_name = operation_name
        self.hang_timeout = hang_timeout_seconds
        self.update_interval = update_interval_seconds
        self.on_hang_detected = on_hang_detected
        
        self.state: Optional[ProgressState] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        self._lock = threading.Lock()
    
    def start(self) -> None:
        """Start monitoring the operation"""
        with self._lock:
            self.state = ProgressState(
                operation_name=self.operation_name,
                started_at=datetime.now(),
                current_step="Initializing",
                last_update=datetime.now()
            )
        
        # Start background monitoring thread
        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        print(f"\n🔍 {self.operation_name} started...")
    
    def update(self, step_name: str, current: int = 0, total: int = 0) -> None:
        """
        Update progress state.
        
        Args:
            step_name: Current step description
            current: Current item index
            total: Total items to process
        """
        with self._lock:
            if self.state:
                self.state.current_step = step_name
                self.state.current_index = current
                self.state.total_items = total
                self.state.last_update = datetime.now()
    
    def complete(self, message: str = "completed") -> None:
        """Mark operation as completed"""
        with self._lock:
            if self.state:
                self.state.completed = True
        
        self._stop_monitoring.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        
        elapsed = self.state.elapsed_seconds if self.state else 0
        print(f"✅ {self.operation_name} {message} ({elapsed:.1f}s)")
    
    def fail(self, error_message: str) -> None:
        """Mark operation as failed"""
        with self._lock:
            if self.state:
                self.state.completed = True
        
        self._stop_monitoring.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        
        elapsed = self.state.elapsed_seconds if self.state else 0
        print(f"❌ {self.operation_name} failed: {error_message} ({elapsed:.1f}s)")
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop"""
        last_display = time.time()
        
        while not self._stop_monitoring.is_set():
            time.sleep(0.5)  # Check frequently but display infrequently
            
            with self._lock:
                if not self.state or self.state.completed:
                    break
                
                # Check for hang
                if self.state.seconds_since_update > self.hang_timeout:
                    self._handle_hang()
                    break
                
                # Display progress at intervals
                if time.time() - last_display >= self.update_interval:
                    self._display_progress()
                    last_display = time.time()
    
    def _display_progress(self) -> None:
        """Display current progress (called with lock held)"""
        if not self.state:
            return
        
        elapsed = self.state.elapsed_seconds
        step = self.state.current_step
        
        if self.state.total_items > 0:
            pct = self.state.progress_percent
            current = self.state.current_index
            total = self.state.total_items
            
            # Calculate ETA
            eta_sec = self.state.eta_seconds
            eta_str = f", ETA: {eta_sec:.0f}s" if eta_sec else ""
            
            print(f"  ⏳ {step}: {current}/{total} ({pct:.1f}%, {elapsed:.1f}s{eta_str})")
        else:
            print(f"  ⏳ {step} ({elapsed:.1f}s)")
    
    def _handle_hang(self) -> None:
        """Handle detected hang (called with lock held)"""
        if not self.state:
            return
        
        print(f"\n⚠️  WARNING: No progress for {self.hang_timeout:.0f}s")
        print(f"   Last step: {self.state.current_step}")
        print(f"   Consider cancelling (Ctrl+C) if operation appears frozen")
        
        if self.on_hang_detected:
            try:
                self.on_hang_detected(self.state)
            except Exception as e:
                print(f"   Error in hang callback: {e}")


class SimpleProgressBar:
    """Lightweight progress indicator for simple loops"""
    
    def __init__(self, total: int, description: str = "Processing", width: int = 40):
        self.total = total
        self.description = description
        self.width = width
        self.current = 0
        self.start_time = time.time()
    
    def update(self, n: int = 1) -> None:
        """Update progress by n items"""
        self.current = min(self.current + n, self.total)
        self._display()
    
    def _display(self) -> None:
        """Display progress bar"""
        if self.total == 0:
            return
        
        pct = self.current / self.total
        filled = int(self.width * pct)
        bar = "█" * filled + "░" * (self.width - filled)
        
        elapsed = time.time() - self.start_time
        items_per_sec = self.current / elapsed if elapsed > 0 else 0
        eta = (self.total - self.current) / items_per_sec if items_per_sec > 0 else 0
        
        print(f"\r{self.description}: |{bar}| {self.current}/{self.total} ({pct*100:.1f}%, ETA: {eta:.0f}s)", end="")
        
        if self.current >= self.total:
            print()  # New line when complete
