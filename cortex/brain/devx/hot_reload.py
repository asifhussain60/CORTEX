"""
ODX-001-01: Hot-Reload Orchestrator

Automatic orchestrator reload on file changes for instant feedback loop.
Extends PHASE-09 GovernanceCLI and PHASE-11 ExecutionSandbox.

AC-ID: ODX-001-01
Phase: PHASE-18-ORCHESTRATOR-DEVX
TDD Status: GREEN phase

Features:
- File watching for orchestrator source changes
- Automatic reload with state preservation
- Sandbox execution for safe testing
- Instant feedback on code changes
"""

import os
import sys
import time
import hashlib
import logging
import threading
import importlib
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

from cortex.models.canonical_enums import ChangeType
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

# Import from existing CORTEX modules
try:
    from cortex_brain.tier2.hallucination_prevention import (
        ExecutionSandbox,
        ExecutionMode,
        SandboxSnapshot,
    )
except ImportError:
    # Fallback for isolated testing
    ExecutionSandbox = None
    ExecutionMode = None
    SandboxSnapshot = None


class ReloadState(Enum):
    """State of the hot reload system."""
    IDLE = "IDLE"
    WATCHING = "WATCHING"
    RELOADING = "RELOADING"
    ERROR = "ERROR"
    PAUSED = "PAUSED"




@dataclass
class FileChange:
    """Represents a detected file change.
    
    Attributes:
        path: Path to the changed file
        change_type: Type of change (created, modified, deleted)
        timestamp: When the change was detected
        old_hash: Previous content hash (if applicable)
        new_hash: Current content hash (if applicable)
    """
    path: Path
    change_type: ChangeType
    timestamp: datetime = field(default_factory=datetime.utcnow, compare=False)
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    
    def __hash__(self):
        return hash((str(self.path), self.change_type.value))


@dataclass
class ReloadEvent:
    """Event triggered when orchestrator reload occurs.
    
    Attributes:
        event_id: Unique identifier for this reload event
        orchestrator_name: Name of the reloaded orchestrator
        file_changes: List of file changes that triggered reload
        timestamp: When reload occurred
        success: Whether reload was successful
        error_message: Error message if reload failed
        reload_time_ms: Time taken to reload in milliseconds
        state_preserved: Whether state was preserved across reload
    """
    event_id: str = field(default_factory=lambda: f"reload-{int(time.time() * 1000)}")
    orchestrator_name: str = ""
    file_changes: List[FileChange] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    success: bool = False
    error_message: Optional[str] = None
    reload_time_ms: float = 0.0
    state_preserved: bool = False


@dataclass
class WatchConfig:
    """Configuration for file watching.
    
    Attributes:
        patterns: Glob patterns to watch (e.g., ['*.py', '*.yaml'])
        ignore_patterns: Patterns to ignore (e.g., ['__pycache__/*'])
        debounce_ms: Minimum time between reloads in milliseconds
        recursive: Whether to watch subdirectories
    """
    patterns: List[str] = field(default_factory=lambda: ["*.py"])
    ignore_patterns: List[str] = field(default_factory=lambda: [
        "__pycache__/*",
        "*.pyc",
        ".git/*",
        "*.egg-info/*",
        ".venv/*",
        "venv/*",
    ])
    debounce_ms: int = 500
    recursive: bool = True


class FileWatcher:
    """Watches files for changes and triggers callbacks.
    
    Provides efficient file system monitoring with debouncing
    and pattern-based filtering.
    
    Example:
        watcher = FileWatcher(Path("src/orchestrators"))
        watcher.on_change(lambda changes: print(f"Changed: {changes}"))
        watcher.start()
    """
    
    def __init__(
        self,
        watch_path: Union[str, Path],
        config: Optional[WatchConfig] = None,
    ):
        """Initialize file watcher.
        
        Args:
            watch_path: Directory path to watch
            config: Watch configuration (patterns, debounce, etc.)
        """
        self.watch_path = Path(watch_path)
        self.config = config or WatchConfig()
        
        self._running = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[List[FileChange]], None]] = []
        self._file_hashes: Dict[Path, str] = {}
        self._last_reload_time = 0.0
        self._lock = threading.Lock()
    
    def _compute_hash(self, file_path: Path) -> Optional[str]:
        """Compute SHA256 hash of file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hash string or None if file cannot be read
        """
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except (IOError, OSError):
            return None
    
    def _matches_pattern(self, path: Path, patterns: List[str]) -> bool:
        """Check if path matches any glob pattern.
        
        Args:
            path: File path to check
            patterns: List of glob patterns
            
        Returns:
            True if path matches any pattern
        """
        import fnmatch
        name = str(path)
        return any(fnmatch.fnmatch(name, p) or fnmatch.fnmatch(path.name, p) for p in patterns)
    
    def _should_watch(self, path: Path) -> bool:
        """Determine if file should be watched.
        
        Args:
            path: File path to check
            
        Returns:
            True if file should be watched
        """
        # Check ignore patterns first
        if self._matches_pattern(path, self.config.ignore_patterns):
            return False
        
        # Check include patterns
        return self._matches_pattern(path, self.config.patterns)
    
    def _scan_files(self) -> Dict[Path, str]:
        """Scan directory and compute hashes for all watched files.
        
        Returns:
            Dictionary mapping file paths to their hashes
        """
        file_hashes = {}
        
        if self.config.recursive:
            paths = self.watch_path.rglob("*")
        else:
            paths = self.watch_path.glob("*")
        
        for path in paths:
            if path.is_file() and self._should_watch(path):
                file_hash = self._compute_hash(path)
                if file_hash:
                    file_hashes[path] = file_hash
        
        return file_hashes
    
    def _detect_changes(self) -> List[FileChange]:
        """Detect file changes since last scan.
        
        Returns:
            List of detected file changes
        """
        changes = []
        current_hashes = self._scan_files()
        
        with self._lock:
            # Check for modified and deleted files
            for path, old_hash in self._file_hashes.items():
                if path not in current_hashes:
                    changes.append(FileChange(
                        path=path,
                        change_type=ChangeType.DELETED,
                        old_hash=old_hash,
                    ))
                elif current_hashes[path] != old_hash:
                    changes.append(FileChange(
                        path=path,
                        change_type=ChangeType.MODIFIED,
                        old_hash=old_hash,
                        new_hash=current_hashes[path],
                    ))
            
            # Check for new files
            for path, new_hash in current_hashes.items():
                if path not in self._file_hashes:
                    changes.append(FileChange(
                        path=path,
                        change_type=ChangeType.CREATED,
                        new_hash=new_hash,
                    ))
            
            # Update stored hashes
            self._file_hashes = current_hashes
        
        return changes
    
    def _watch_loop(self):
        """Main watching loop - runs in separate thread."""
        # Initial scan
        with self._lock:
            self._file_hashes = self._scan_files()
        
        while self._running:
            if not self._paused:
                changes = self._detect_changes()
                
                if changes:
                    # Check debounce
                    now = time.time() * 1000
                    if now - self._last_reload_time >= self.config.debounce_ms:
                        self._last_reload_time = now
                        
                        # Trigger callbacks
                        for callback in self._callbacks:
                            try:
                                callback(changes)
                            except Exception as e:
                                print(f"Callback error: {e}")
            
            # Sleep between scans (polling interval)
            time.sleep(0.1)  # 100ms polling
    
    def on_change(self, callback: Callable[[List[FileChange]], None]) -> "FileWatcher":
        """Register callback for file changes.
        
        Args:
            callback: Function to call with list of changes
            
        Returns:
            Self for method chaining
        """
        self._callbacks.append(callback)
        return self
    
    def start(self) -> "FileWatcher":
        """Start watching for file changes.
        
        Returns:
            Self for method chaining
        """
        if self._running:
            return self
        
        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        return self
    
    def stop(self) -> "FileWatcher":
        """Stop watching for file changes.
        
        Returns:
            Self for method chaining
        """
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        return self
    
    def pause(self) -> "FileWatcher":
        """Pause file watching.
        
        Returns:
            Self for method chaining
        """
        self._paused = True
        return self
    
    def resume(self) -> "FileWatcher":
        """Resume file watching.
        
        Returns:
            Self for method chaining
        """
        self._paused = False
        return self
    
    @property
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._running
    
    @property
    def is_paused(self) -> bool:
        """Check if watcher is paused."""
        return self._paused


class HotReloadOrchestrator:
    """Hot-reload orchestrator for instant feedback development.
    
    Provides automatic orchestrator reload on file changes with:
    - State preservation across reloads
    - Sandbox execution for safe testing
    - Error recovery and rollback
    - Instant feedback loop
    
    Extends:
    - PHASE-09 GovernanceCLI patterns
    - PHASE-11 ExecutionSandbox for safe execution
    
    Example:
        hot_reload = HotReloadOrchestrator("src/orchestrators/custom")
        hot_reload.register("MyOrchestrator", MyOrchestrator)
        hot_reload.start()
        
        # Make changes to MyOrchestrator...
        # Automatically reloads and validates!
    """
    
    def __init__(
        self,
        orchestrator_path: Union[str, Path],
        watch_config: Optional[WatchConfig] = None,
        sandbox_enabled: bool = True,
    ):
        """Initialize hot-reload orchestrator.
        
        Args:
            orchestrator_path: Path to orchestrator source directory
            watch_config: File watching configuration
            sandbox_enabled: Whether to use sandbox for safe execution
        """
        self.orchestrator_path = Path(orchestrator_path)
        self.watch_config = watch_config or WatchConfig()
        self.sandbox_enabled = sandbox_enabled
        
        # Internal state
        self._state = ReloadState.IDLE
        self._registered: Dict[str, Type] = {}
        self._instances: Dict[str, Any] = {}
        self._preserved_state: Dict[str, Dict[str, Any]] = {}
        self._reload_history: List[ReloadEvent] = []
        self._callbacks: Dict[str, List[Callable[[ReloadEvent], None]]] = {
            "before_reload": [],
            "after_reload": [],
            "on_error": [],
        }
        
        # File watcher
        self._watcher = FileWatcher(orchestrator_path, watch_config)
        self._watcher.on_change(self._handle_changes)
        
        # Sandbox (from PHASE-11)
        self._sandbox: Optional[Any] = None  # ExecutionSandbox type
        if sandbox_enabled and ExecutionSandbox:
            self._sandbox = ExecutionSandbox()
    
    def register(
        self,
        name: str,
        orchestrator_class: Type,
        module_path: Optional[str] = None,
    ) -> "HotReloadOrchestrator":
        """Register an orchestrator for hot-reload.
        
        Args:
            name: Unique name for the orchestrator
            orchestrator_class: The orchestrator class to reload
            module_path: Optional module path (e.g., 'src.orchestrators.custom.my_orch')
            
        Returns:
            Self for method chaining
        """
        self._registered[name] = orchestrator_class
        
        # Try to determine module path if not provided
        if module_path is None:
            module_path = orchestrator_class.__module__
        
        return self
    
    def _preserve_state(self, name: str) -> Dict[str, Any]:
        """Preserve orchestrator state before reload.
        
        Args:
            name: Orchestrator name
            
        Returns:
            Dictionary of preserved state
        """
        state = {}
        
        if name in self._instances:
            instance = self._instances[name]
            
            # Try to get state from instance
            if hasattr(instance, "get_state"):
                state = instance.get_state()
            elif hasattr(instance, "__dict__"):
                # Preserve serializable attributes
                import json
                from cortex.models.canonical_enums import ChangeType
                
                for key, value in instance.__dict__.items():
                    if not key.startswith("_"):
                        try:
                            # Test if serializable
                            json.dumps(value, default=str)
                            state[key] = value
                        except (TypeError, ValueError):
                            pass
        
        self._preserved_state[name] = state
        return state
    
    def _restore_state(self, name: str, instance: Any) -> bool:
        """Restore preserved state to new instance.
        
        Args:
            name: Orchestrator name
            instance: New orchestrator instance
            
        Returns:
            True if state was restored
        """
        if name not in self._preserved_state:
            return False
        
        state = self._preserved_state[name]
        
        if hasattr(instance, "set_state"):
            instance.set_state(state)
            return True
        
        # Try direct attribute assignment
        for key, value in state.items():
            if hasattr(instance, key):
                try:
                    setattr(instance, key, value)
                except (AttributeError, TypeError):
                    pass
        
        return bool(state)
    
    def _reload_module(self, module_name: str) -> bool:
        """Reload a Python module.
        
        Args:
            module_name: Module name to reload
            
        Returns:
            True if reload succeeded
        """
        try:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                importlib.reload(module)
            else:
                importlib.import_module(module_name)
            return True
        except Exception as e:
            print(f"Module reload failed: {e}")
            return False
    
    def _reload_orchestrator(self, name: str) -> ReloadEvent:
        """Reload a specific orchestrator.
        
        Args:
            name: Orchestrator name
            
        Returns:
            ReloadEvent with result details
        """
        start_time = time.time()
        event = ReloadEvent(orchestrator_name=name)
        
        try:
            # Preserve state
            self._preserve_state(name)
            event.state_preserved = bool(self._preserved_state.get(name))
            
            # Get module info
            orchestrator_class = self._registered[name]
            module_name = orchestrator_class.__module__
            
            # Reload module
            if not self._reload_module(module_name):
                raise RuntimeError(f"Failed to reload module {module_name}")
            
            # Get updated class
            module = sys.modules[module_name]
            class_name = orchestrator_class.__name__
            
            if hasattr(module, class_name):
                new_class = getattr(module, class_name)
                self._registered[name] = new_class
                
                # Create new instance
                new_instance = new_class()
                
                # Restore state
                self._restore_state(name, new_instance)
                
                # Update instance
                self._instances[name] = new_instance
                
                event.success = True
            else:
                raise AttributeError(f"Class {class_name} not found in module")
                
        except Exception as e:
            event.success = False
            event.error_message = str(e)
            traceback.print_exc()
        
        event.reload_time_ms = (time.time() - start_time) * 1000
        self._reload_history.append(event)
        
        return event
    
    def _handle_changes(self, changes: List[FileChange]):
        """Handle detected file changes.
        
        Args:
            changes: List of file changes
        """
        if self._state == ReloadState.PAUSED:
            return
        
        self._state = ReloadState.RELOADING
        
        # Find affected orchestrators
        affected = self._find_affected_orchestrators(changes)
        
        for name in affected:
            # Trigger before_reload callbacks
            for callback in self._callbacks["before_reload"]:
                try:
                    callback(ReloadEvent(orchestrator_name=name))
                except Exception as e:
                    logger.warning(f"Before-reload callback failed for {name}: {e}")
            
            # Perform reload
            if self._sandbox:
                # Execute in sandbox for safety
                result = self._sandbox.execute(
                    lambda n=name: self._reload_orchestrator(n),
                    mode=ExecutionMode.SANDBOX if self.sandbox_enabled else ExecutionMode.COMMITTED,
                )
                event = result.output if result.success else ReloadEvent(
                    orchestrator_name=name,
                    success=False,
                    error_message=result.error_message,
                )
            else:
                event = self._reload_orchestrator(name)
            
            event.file_changes = changes
            
            # Trigger after_reload callbacks
            callback_key = "after_reload" if event.success else "on_error"
            for callback in self._callbacks[callback_key]:
                try:
                    callback(event)
                except Exception as e:
                    logger.warning(f"{callback_key} callback failed: {e}")
        
        self._state = ReloadState.WATCHING if self._watcher.is_running else ReloadState.IDLE
    
    def _find_affected_orchestrators(self, changes: List[FileChange]) -> Set[str]:
        """Find orchestrators affected by file changes.
        
        Args:
            changes: List of file changes
            
        Returns:
            Set of affected orchestrator names
        """
        affected = set()
        
        for change in changes:
            # Check if change file matches any registered orchestrator
            for name, cls in self._registered.items():
                module = sys.modules.get(cls.__module__)
                if module and hasattr(module, "__file__"):
                    module_file = Path(module.__file__)
                    if change.path == module_file or change.path.name == module_file.name:
                        affected.add(name)
        
        # If no specific match, reload all (conservative approach)
        if not affected and changes:
            affected = set(self._registered.keys())
        
        return affected
    
    def on(self, event: str, callback: Callable[[ReloadEvent], None]) -> "HotReloadOrchestrator":
        """Register callback for reload events.
        
        Args:
            event: Event name ('before_reload', 'after_reload', 'on_error')
            callback: Function to call with ReloadEvent
            
        Returns:
            Self for method chaining
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)
        return self
    
    def start(self) -> "HotReloadOrchestrator":
        """Start hot-reload watching.
        
        Returns:
            Self for method chaining
        """
        self._state = ReloadState.WATCHING
        self._watcher.start()
        return self
    
    def stop(self) -> "HotReloadOrchestrator":
        """Stop hot-reload watching.
        
        Returns:
            Self for method chaining
        """
        self._state = ReloadState.IDLE
        self._watcher.stop()
        return self
    
    def pause(self) -> "HotReloadOrchestrator":
        """Pause hot-reload (keep watching but don't reload).
        
        Returns:
            Self for method chaining
        """
        self._state = ReloadState.PAUSED
        return self
    
    def resume(self) -> "HotReloadOrchestrator":
        """Resume hot-reload.
        
        Returns:
            Self for method chaining
        """
        self._state = ReloadState.WATCHING
        return self
    
    def force_reload(self, name: Optional[str] = None) -> List[ReloadEvent]:
        """Force reload orchestrator(s).
        
        Args:
            name: Specific orchestrator to reload, or None for all
            
        Returns:
            List of ReloadEvents
        """
        events = []
        
        names = [name] if name else list(self._registered.keys())
        
        for n in names:
            if n in self._registered:
                event = self._reload_orchestrator(n)
                events.append(event)
        
        return events
    
    def get_instance(self, name: str) -> Optional[Any]:
        """Get the current instance of a registered orchestrator.
        
        Args:
            name: Orchestrator name
            
        Returns:
            Orchestrator instance or None
        """
        return self._instances.get(name)
    
    def get_reload_history(self) -> List[ReloadEvent]:
        """Get history of reload events.
        
        Returns:
            List of ReloadEvents
        """
        return list(self._reload_history)
    
    @property
    def state(self) -> ReloadState:
        """Get current hot-reload state."""
        return self._state
    
    @property
    def registered_orchestrators(self) -> List[str]:
        """Get list of registered orchestrator names."""
        return list(self._registered.keys())
