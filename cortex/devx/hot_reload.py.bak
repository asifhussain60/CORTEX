"""Hot Reload - ODX-001-01

File system monitoring and hot reload orchestration for development.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import List, Callable, Optional, Dict, Set, Any
from enum import Enum
from pathlib import Path
from datetime import datetime
import hashlib
import threading
import time
import fnmatch
from cortex.models.canonical_enums import ChangeType




@dataclass
class FileChange:
    """File change event.
    
    Attributes:
        path: Path to changed file
        change_type: Type of change
        timestamp: When change occurred
        old_hash: Previous file hash (for modifications)
        new_hash: New file hash (for modifications)
    """
    path: Path
    change_type: ChangeType
    timestamp: datetime = field(default_factory=datetime.now)
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    
    def __hash__(self) -> int:
        """Make FileChange hashable."""
        return hash((str(self.path), self.change_type.value))
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, FileChange):
            return False
        return self.path == other.path and self.change_type == other.change_type


@dataclass
class ReloadEvent:
    """Hot reload event.
    
    Attributes:
        orchestrator_name: Name of orchestrator being reloaded
        event_id: Unique event identifier
        file_changes: List of file changes that triggered reload
        success: Whether reload succeeded
        reload_time_ms: Time taken to reload in milliseconds
        error_message: Error message if reload failed
    """
    orchestrator_name: str
    event_id: str = field(default_factory=lambda: f"reload-{datetime.now().timestamp()}")
    file_changes: List[FileChange] = field(default_factory=list)
    success: bool = False
    reload_time_ms: float = 0.0
    error_message: Optional[str] = None


@dataclass
class WatchConfig:
    """File watcher configuration.
    
    Attributes:
        patterns: File patterns to watch (glob syntax)
        ignore_patterns: Patterns to ignore
        debounce_ms: Debounce time in milliseconds
        recursive: Whether to watch subdirectories
    """
    patterns: List[str] = field(default_factory=lambda: ["*.py"])
    ignore_patterns: List[str] = field(default_factory=lambda: ["__pycache__/*", "*.pyc", ".git/*"])
    debounce_ms: int = 500
    recursive: bool = True


class ReloadState(Enum):
    """Hot reload state."""
    IDLE = "idle"
    WATCHING = "watching"
    PAUSED = "paused"
    RELOADING = "reloading"
    COMPLETED = "completed"
    ERROR = "error"


class FileWatcher:
    """File system watcher with change detection.
    
    Monitors a directory for file changes and notifies callbacks.
    
    Attributes:
        watch_path: Directory path to watch
        config: Watch configuration
        is_running: Whether watcher is running
        is_paused: Whether watcher is paused
    """
    
    def __init__(self, watch_path: str, config: Optional[WatchConfig] = None) -> None:
        """Initialize file watcher.
        
        Args:
            watch_path: Directory to watch
            config: Watch configuration (defaults if None)
        """
        self.watch_path = Path(watch_path)
        self.config = config or WatchConfig()
        self.is_running = False
        self.is_paused = False
        self._callbacks: List[Callable[[List[FileChange]], None]] = []
        self._file_hashes: Dict[Path, str] = {}
        self._watch_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_change_time: float = 0
    
    def start(self) -> None:
        """Start watching for file changes."""
        if self.is_running:
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # Initial scan
        self._scan_directory()
        
        # Start watch thread
        self._watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._watch_thread.start()
    
    def stop(self) -> None:
        """Stop watching for file changes."""
        if not self.is_running:
            return
        
        self.is_running = False
        self._stop_event.set()
        
        if self._watch_thread:
            self._watch_thread.join(timeout=1.0)
    
    def pause(self) -> None:
        """Pause change detection."""
        self.is_paused = True
    
    def resume(self) -> None:
        """Resume change detection."""
        self.is_paused = False
    
    def on_change(self, callback: Callable[[List[FileChange]], None]) -> "FileWatcher":
        """Register callback for file changes.
        
        Args:
            callback: Function to call with list of changes
            
        Returns:
            Self for method chaining
        """
        self._callbacks.append(callback)
        return self
    
    def _should_watch(self, path: Path) -> bool:
        """Check if path should be watched.
        
        Args:
            path: Path to check
            
        Returns:
            True if path matches patterns and not ignored
        """
        rel_path = str(path.relative_to(self.watch_path)) if path.is_relative_to(self.watch_path) else str(path)
        
        # Check ignore patterns
        for pattern in self.config.ignore_patterns:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(path.name, pattern):
                return False
        
        # Check watch patterns
        for pattern in self.config.patterns:
            if fnmatch.fnmatch(path.name, pattern):
                return True
        
        return False
    
    def _compute_hash(self, path: Path) -> Optional[str]:
        """Compute SHA256 hash of file.
        
        Args:
            path: File path
            
        Returns:
            Hex digest of file hash or None if error
        """
        try:
            with open(path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None
    
    def _scan_directory(self) -> List[FileChange]:
        """Scan directory for changes.
        
        Returns:
            List of detected changes
        """
        changes = []
        current_files: Set[Path] = set()
        
        # Scan for files
        if self.config.recursive:
            files = self.watch_path.rglob("*")
        else:
            files = self.watch_path.glob("*")
        
        for path in files:
            if not path.is_file() or not self._should_watch(path):
                continue
            
            current_files.add(path)
            current_hash = self._compute_hash(path)
            
            if current_hash is None:
                continue
            
            if path not in self._file_hashes:
                # New file
                changes.append(FileChange(
                    path=path,
                    change_type=ChangeType.CREATED,
                    new_hash=current_hash
                ))
                self._file_hashes[path] = current_hash
            elif self._file_hashes[path] != current_hash:
                # Modified file
                changes.append(FileChange(
                    path=path,
                    change_type=ChangeType.MODIFIED,
                    old_hash=self._file_hashes[path],
                    new_hash=current_hash
                ))
                self._file_hashes[path] = current_hash
        
        # Check for deleted files
        deleted_files = set(self._file_hashes.keys()) - current_files
        for path in deleted_files:
            changes.append(FileChange(
                path=path,
                change_type=ChangeType.DELETED,
                old_hash=self._file_hashes[path]
            ))
            del self._file_hashes[path]
        
        return changes
    
    def _watch_loop(self) -> None:
        """Main watch loop running in thread."""
        while not self._stop_event.is_set():
            if self.is_paused:
                time.sleep(0.1)
                continue
            
            # Scan for changes
            changes = self._scan_directory()
            
            # Debounce: only notify if enough time has passed
            current_time = time.time()
            if changes and (current_time - self._last_change_time) * 1000 >= self.config.debounce_ms:
                self._last_change_time = current_time
                
                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        callback(changes)
                    except Exception:
                        pass  # Don't let callback errors stop watching
            
            # Sleep between scans
            time.sleep(0.1)


class HotReloadOrchestrator:
    """Orchestrate hot reload operations.
    
    Manages file watching and orchestrator reloading.
    
    Attributes:
        orchestrator_path: Path to orchestrators directory
        state: Current reload state
        registered_orchestrators: Orchestrators registered for reloading
        sandbox_enabled: Whether to use sandbox mode for reloading
    """
    
    _instances: Dict[str, Any] = {}
    
    def __init__(self, orchestrator_path: str, config: Optional[WatchConfig] = None, sandbox_enabled: bool = True) -> None:
        """Initialize hot reload orchestrator.
        
        Args:
            orchestrator_path: Path to orchestrators directory
            config: Watch configuration (optional)
            sandbox_enabled: Whether to enable sandbox mode
        """
        self.orchestrator_path = Path(orchestrator_path)
        self._state = ReloadState.IDLE
        # REM-HIGH-001: Thread-safe state management with lock and timeout
        self._state_lock = threading.Lock()
        self._state_timeout = 5.0  # 5 second timeout for state transitions
        self.sandbox_enabled = sandbox_enabled
        self.config = config
        self.registered_orchestrators: Dict[str, Any] = {}
        self._watcher: Optional[FileWatcher] = None
        self._reload_events: List[ReloadEvent] = []
        self._callbacks: Dict[str, List[Callable]] = {
            "before_reload": [],
            "after_reload": [],
            "on_error": [],
        }
        self._preserved_state: Dict[str, Any] = {}
    
    @property
    def state(self) -> ReloadState:
        """Get current reload state (thread-safe)."""
        with self._state_lock:
            return self._state
    
    @state.setter
    def state(self, new_state: ReloadState) -> None:
        """Set reload state (thread-safe, atomic transition)."""
        acquired = self._state_lock.acquire(timeout=self._state_timeout)
        if not acquired:
            raise TimeoutError(f"Failed to acquire state lock within {self._state_timeout}s")
        try:
            self._state = new_state
        finally:
            self._state_lock.release()
    
    def start(self) -> None:
        """Start hot reload monitoring."""
        if self.state == ReloadState.WATCHING:
            return
        
        self.state = ReloadState.WATCHING
        # Pass config if provided, otherwise use defaults
        self._watcher = FileWatcher(str(self.orchestrator_path), config=self.config)
        self._watcher.on_change(self._on_files_changed)
        self._watcher.start()
    
    def stop(self) -> None:
        """Stop hot reload monitoring."""
        if self._watcher:
            self._watcher.stop()
        self.state = ReloadState.IDLE
    
    def pause(self) -> None:
        """Pause hot reload monitoring."""
        if self._watcher:
            self._watcher.pause()
        self.state = ReloadState.PAUSED
    
    def resume(self) -> None:
        """Resume hot reload monitoring."""
        if self._watcher:
            self._watcher.resume()
        self.state = ReloadState.WATCHING
    
    def register(self, name: str, orchestrator: Any) -> "HotReloadOrchestrator":
        """Register orchestrator for reloading.
        
        Args:
            name: Orchestrator name
            orchestrator: Orchestrator class or instance
            
        Returns:
            Self for method chaining
        """
        self.registered_orchestrators[name] = orchestrator
        return self
    
    def register_orchestrator(self, name: str, orchestrator: Any) -> None:
        """Register orchestrator for reloading (alias).
        
        Args:
            name: Orchestrator name
            orchestrator: Orchestrator instance
        """
        self.registered_orchestrators[name] = orchestrator
    
    def on(self, event: str, callback: Callable) -> "HotReloadOrchestrator":
        """Register callback for reload events.
        
        Args:
            event: Event name (before_reload, after_reload, on_error)
            callback: Callback function
            
        Returns:
            Self for method chaining
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)
        return self
    
    def force_reload(self, orchestrator_name: str) -> List[ReloadEvent]:
        """Force reload an orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator to reload
            
        Returns:
            List of reload events
        """
        changes = [FileChange(
            path=self.orchestrator_path / f"{orchestrator_name}.py",
            change_type=ChangeType.MODIFIED
        )]
        
        self._reload_orchestrator(orchestrator_name, changes)
        return [e for e in self._reload_events if e.orchestrator_name == orchestrator_name]
    
    def get_reload_history(self) -> List[ReloadEvent]:
        """Get reload history.
        
        Returns:
            List of all reload events
        """
        return self._reload_events.copy()
    
    def get_reload_events(self) -> List[ReloadEvent]:
        """Get list of reload events.
        
        Returns:
            List of reload events
        """
        return self._reload_events.copy()
    
    def get_instance(self, name: str) -> Optional[Any]:
        """Get orchestrator instance.
        
        Args:
            name: Orchestrator name
            
        Returns:
            Orchestrator instance or None
        """
        return self._instances.get(name)
    
    def _preserve_state(self, name: str) -> Any:
        """Preserve orchestrator state before reload.
        
        Args:
            name: Orchestrator name
            
        Returns:
            Preserved state
        """
        instance = self._instances.get(name)
        if instance and hasattr(instance, 'get_state'):
            state = instance.get_state()
            self._preserved_state[name] = state
            return state
        return None
    
    def _restore_state(self, name: str) -> None:
        """Restore orchestrator state after reload.
        
        Args:
            name: Orchestrator name
        """
        if name in self._preserved_state:
            instance = self._instances.get(name)
            if instance and hasattr(instance, 'set_state'):
                instance.set_state(self._preserved_state[name])
    
    def _on_files_changed(self, changes: List[FileChange]) -> None:
        """Handle file changes.
        
        Args:
            changes: List of file changes
        """
        if not changes:
            return
        
        # Determine which orchestrators need reloading
        affected_orchestrators = self._get_affected_orchestrators(changes)
        
        for orch_name in affected_orchestrators:
            self._reload_orchestrator(orch_name, changes)
    
    def _get_affected_orchestrators(self, changes: List[FileChange]) -> Set[str]:
        """Determine which orchestrators are affected by changes.
        
        Args:
            changes: List of file changes
            
        Returns:
            Set of affected orchestrator names
        """
        affected = set()
        
        for change in changes:
            # Simple heuristic: if file is in registered orchestrators, reload it
            for orch_name in self.registered_orchestrators:
                if orch_name.lower() in str(change.path).lower():
                    affected.add(orch_name)
        
        return affected
    
    def _reload_orchestrator(self, name: str, changes: List[FileChange]) -> None:
        """Reload an orchestrator.
        
        Args:
            name: Orchestrator name
            changes: File changes that triggered reload
        """
        # Call before_reload callbacks
        event = ReloadEvent(orchestrator_name=name, file_changes=changes)
        for callback in self._callbacks["before_reload"]:
            try:
                callback(event)
            except Exception:
                pass
        
        self.state = ReloadState.RELOADING
        start_time = time.time()
        
        try:
            # Preserve state if instance exists
            if name in self._instances:
                self._preserve_state(name)
            
            # Actual reload logic would go here
            # For now, just simulate success
            event.success = True
            event.reload_time_ms = (time.time() - start_time) * 1000
            self.state = ReloadState.COMPLETED
            
            # Call after_reload callbacks
            for callback in self._callbacks["after_reload"]:
                try:
                    callback(event)
                except Exception:
                    pass
                    
        except Exception as e:
            event.success = False
            event.error_message = str(e)
            self.state = ReloadState.ERROR
            
            # Call on_error callbacks
            for callback in self._callbacks["on_error"]:
                try:
                    callback(event)
                except Exception:
                    pass
        
        self._reload_events.append(event)
        
        # Return to watching state
        if self.state in (ReloadState.COMPLETED, ReloadState.ERROR):
            self.state = ReloadState.WATCHING


__all__ = [
    "ChangeType",
    "FileChange",
    "ReloadEvent",
    "WatchConfig",
    "ReloadState",
    "FileWatcher",
    "HotReloadOrchestrator",
]
