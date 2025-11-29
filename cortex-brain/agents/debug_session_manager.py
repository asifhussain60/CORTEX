"""
CORTEX Debug Session Manager
Provides runtime instrumentation and debug logging without source file modification.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import uuid
import time
import json
import inspect
import functools
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from contextlib import contextmanager
import sqlite3
import threading


class DebugSessionManager:
    """Manages debug sessions with runtime instrumentation and automatic cleanup."""
    
    def __init__(self, brain_root: Path):
        self.brain_root = Path(brain_root)
        self.sessions_dir = self.brain_root / "debug-sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Database path for session metadata
        self.db_path = self.brain_root / "tier1-working-memory.db"
        
        # Active sessions (thread-safe)
        self._active_sessions: Dict[str, "DebugSession"] = {}
        self._lock = threading.Lock()
        
        # Initialize database schema
        self._init_db()
    
    def _init_db(self):
        """Initialize debug session tables in Tier 1 database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS debug_sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    target_module TEXT,
                    target_function TEXT,
                    status TEXT NOT NULL,
                    log_file TEXT,
                    instrumented_functions TEXT,
                    created_at REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS debug_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    level TEXT NOT NULL,
                    function_name TEXT,
                    message TEXT NOT NULL,
                    data TEXT,
                    FOREIGN KEY (session_id) REFERENCES debug_sessions(session_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_debug_sessions_status 
                ON debug_sessions(status)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_debug_logs_session 
                ON debug_logs(session_id, timestamp)
            """)
            
            conn.commit()
    
    def start_session(
        self, 
        target_module: Optional[str] = None,
        target_function: Optional[str] = None,
        session_name: Optional[str] = None
    ) -> "DebugSession":
        """
        Start a new debug session.
        
        Args:
            target_module: Module name to instrument (e.g., 'cortex_brain.agents.planner')
            target_function: Specific function to instrument (optional)
            session_name: Human-readable session name (optional)
        
        Returns:
            DebugSession instance
        """
        session_id = str(uuid.uuid4())[:8]
        
        if session_name:
            session_id = f"{session_name}-{session_id}"
        
        session = DebugSession(
            session_id=session_id,
            manager=self,
            target_module=target_module,
            target_function=target_function
        )
        
        with self._lock:
            self._active_sessions[session_id] = session
        
        # Record in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO debug_sessions 
                (session_id, start_time, target_module, target_function, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                time.time(),
                target_module or "",
                target_function or "",
                "active",
                time.time()
            ))
            conn.commit()
        
        return session
    
    def stop_session(self, session_id: str) -> Dict[str, Any]:
        """
        Stop a debug session and cleanup all instrumentation.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session summary with stats
        """
        with self._lock:
            session = self._active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found or already stopped")
        
        # Stop the session (removes all instrumentation)
        summary = session.stop()
        
        # Update database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE debug_sessions
                SET end_time = ?, status = ?, instrumented_functions = ?
                WHERE session_id = ?
            """, (
                time.time(),
                "completed",
                json.dumps(list(session.instrumented_functions)),
                session_id
            ))
            conn.commit()
        
        # Remove from active sessions
        with self._lock:
            del self._active_sessions[session_id]
        
        return summary
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        with self._lock:
            return list(self._active_sessions.keys())
    
    def get_session(self, session_id: str) -> Optional["DebugSession"]:
        """Get active session by ID."""
        with self._lock:
            return self._active_sessions.get(session_id)
    
    def stop_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Stop all active sessions. Returns summaries for each."""
        summaries = {}
        for session_id in list(self._active_sessions.keys()):
            summaries[session_id] = self.stop_session(session_id)
        return summaries
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent debug session history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT session_id, start_time, end_time, target_module, 
                       target_function, status, instrumented_functions
                FROM debug_sessions
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    "session_id": row[0],
                    "start_time": datetime.fromtimestamp(row[1]).isoformat(),
                    "end_time": datetime.fromtimestamp(row[2]).isoformat() if row[2] else None,
                    "target_module": row[3],
                    "target_function": row[4],
                    "status": row[5],
                    "instrumented_functions": json.loads(row[6]) if row[6] else []
                })
            
            return sessions


class DebugSession:
    """Represents an active debug session with runtime instrumentation."""
    
    def __init__(
        self,
        session_id: str,
        manager: DebugSessionManager,
        target_module: Optional[str] = None,
        target_function: Optional[str] = None
    ):
        self.session_id = session_id
        self.manager = manager
        self.target_module = target_module
        self.target_function = target_function
        
        # Session state
        self.start_time = time.time()
        self.instrumented_functions: Set[str] = set()
        self.original_functions: Dict[str, Callable] = {}
        
        # Log file setup
        self.log_dir = manager.sessions_dir / session_id
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "debug.log"
        
        # Stats
        self.call_count = 0
        self.error_count = 0
    
    def instrument_function(self, func: Callable, module_name: str = "") -> Callable:
        """
        Wrap a function with debug instrumentation.
        
        Args:
            func: Function to instrument
            module_name: Module name for logging
        
        Returns:
            Instrumented function wrapper
        """
        func_name = f"{module_name}.{func.__name__}" if module_name else func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.call_count += 1
            call_id = f"{func_name}#{self.call_count}"
            
            # Log entry
            entry_time = time.time()
            self._log("ENTRY", call_id, {
                "args": self._serialize_args(args),
                "kwargs": self._serialize_args(kwargs)
            })
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log exit
                exit_time = time.time()
                duration = exit_time - entry_time
                self._log("EXIT", call_id, {
                    "result": self._serialize_value(result),
                    "duration_ms": round(duration * 1000, 2)
                })
                
                return result
            
            except Exception as e:
                self.error_count += 1
                self._log("ERROR", call_id, {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "duration_ms": round((time.time() - entry_time) * 1000, 2)
                })
                raise
        
        # Track instrumentation
        self.instrumented_functions.add(func_name)
        self.original_functions[func_name] = func
        
        return wrapper
    
    def _log(self, level: str, function_name: str, data: Dict[str, Any]):
        """Write log entry to file and database."""
        timestamp = time.time()
        message = f"[{level}] {function_name}"
        
        # Write to file
        with open(self.log_file, "a") as f:
            f.write(f"{datetime.fromtimestamp(timestamp).isoformat()} {message}\n")
            if data:
                f.write(f"  {json.dumps(data, indent=2)}\n")
        
        # Write to database
        with sqlite3.connect(self.manager.db_path) as conn:
            conn.execute("""
                INSERT INTO debug_logs (session_id, timestamp, level, function_name, message, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.session_id,
                timestamp,
                level,
                function_name,
                message,
                json.dumps(data) if data else None
            ))
            conn.commit()
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize a value for logging (handles non-JSON types)."""
        try:
            if isinstance(value, (str, int, float, bool, type(None))):
                return value
            elif isinstance(value, (list, tuple)):
                return [self._serialize_value(v) for v in value]
            elif isinstance(value, dict):
                return {k: self._serialize_value(v) for k, v in value.items()}
            else:
                return f"<{type(value).__name__}>"
        except Exception:
            return "<unserializable>"
    
    def _serialize_args(self, args: tuple) -> List[Any]:
        """Serialize function arguments."""
        return [self._serialize_value(arg) for arg in args]
    
    def stop(self) -> Dict[str, Any]:
        """Stop session and return summary."""
        end_time = time.time()
        duration = end_time - self.start_time
        
        summary = {
            "session_id": self.session_id,
            "duration_seconds": round(duration, 2),
            "instrumented_functions": list(self.instrumented_functions),
            "call_count": self.call_count,
            "error_count": self.error_count,
            "log_file": str(self.log_file)
        }
        
        # Write summary to file
        summary_file = self.log_dir / "summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    @contextmanager
    def instrument_module(self, module):
        """
        Context manager to temporarily instrument all functions in a module.
        
        Usage:
            with session.instrument_module(my_module):
                my_module.some_function()  # This call will be instrumented
        """
        # Store original functions
        instrumented = {}
        
        try:
            # Replace functions with instrumented versions
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) or inspect.ismethod(obj):
                    instrumented[name] = obj
                    setattr(module, name, self.instrument_function(obj, module.__name__))
            
            yield self
        
        finally:
            # Restore original functions
            for name, original_func in instrumented.items():
                setattr(module, name, original_func)


# Global manager instance (initialized lazily)
_manager: Optional[DebugSessionManager] = None


def get_debug_manager(brain_root: Optional[Path] = None) -> DebugSessionManager:
    """Get or create global debug session manager."""
    global _manager
    
    if _manager is None:
        if brain_root is None:
            # Default to CORTEX brain location
            brain_root = Path(__file__).parent.parent
        _manager = DebugSessionManager(brain_root)
    
    return _manager
