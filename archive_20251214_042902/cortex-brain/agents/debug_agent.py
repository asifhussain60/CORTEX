"""
CORTEX Debug Agent
Handles debug intent detection and automatic instrumentation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import importlib
import inspect
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import re

from .debug_session_manager import get_debug_manager, DebugSession


class DebugAgent:
    """
    Intelligent debug agent that detects debug intent and instruments code automatically.
    """
    
    def __init__(self, brain_root: Path):
        self.brain_root = Path(brain_root)
        self.manager = get_debug_manager(brain_root)
        
        # Debug intent patterns
        self.debug_patterns = [
            r"debug\s+(\w+)",
            r"trace\s+(\w+)",
            r"instrument\s+(\w+)",
            r"log\s+(\w+)",
            r"watch\s+(\w+)",
            r"profile\s+(\w+)"
        ]
    
    def detect_debug_intent(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        Detect debug intent from user message.
        
        Args:
            user_message: User's natural language message
        
        Returns:
            Dict with debug intent details or None
        """
        message_lower = user_message.lower()
        
        # Check for debug keywords
        if not any(kw in message_lower for kw in ['debug', 'trace', 'instrument', 'log', 'watch', 'profile']):
            return None
        
        # Extract target (module/function/class)
        target = None
        for pattern in self.debug_patterns:
            match = re.search(pattern, message_lower)
            if match:
                target = match.group(1)
                break
        
        # Check for stop/end commands
        if any(kw in message_lower for kw in ['stop debug', 'end debug', 'stop trace', 'end trace']):
            return {
                "action": "stop",
                "target": target
            }
        
        # Start debug session
        return {
            "action": "start",
            "target": target,
            "original_message": user_message
        }
    
    def start_debug_session(
        self,
        target: Optional[str] = None,
        module_path: Optional[str] = None,
        function_name: Optional[str] = None
    ) -> DebugSession:
        """
        Start a debug session with automatic module discovery.
        
        Args:
            target: Target name (will attempt to find module/function)
            module_path: Explicit module path (e.g., 'cortex_brain.agents.planner')
            function_name: Explicit function name
        
        Returns:
            Active DebugSession
        """
        # If explicit paths provided, use them
        if module_path:
            session = self.manager.start_session(
                target_module=module_path,
                target_function=function_name,
                session_name=target or "debug"
            )
            return session
        
        # Auto-discover target
        if target:
            discovered = self._discover_target(target)
            if discovered:
                module_path = discovered.get('module')
                function_name = discovered.get('function')
        
        session = self.manager.start_session(
            target_module=module_path,
            target_function=function_name,
            session_name=target or "debug"
        )
        
        return session
    
    def stop_debug_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop a debug session (stops most recent if no ID provided).
        
        Args:
            session_id: Specific session ID to stop (optional)
        
        Returns:
            Session summary
        """
        if session_id is None:
            # Stop most recent active session
            active = self.manager.get_active_sessions()
            if not active:
                return {"error": "No active debug sessions"}
            session_id = active[-1]
        
        return self.manager.stop_session(session_id)
    
    def _discover_target(self, target: str) -> Optional[Dict[str, str]]:
        """
        Discover module/function from target name.
        
        Args:
            target: Target name (e.g., 'planner', 'PlannerAgent', 'plan_feature')
        
        Returns:
            Dict with 'module' and optional 'function' keys
        """
        # Search in cortex-brain agents
        agents_dir = self.brain_root / "agents"
        
        # Check for module files
        for py_file in agents_dir.glob("*.py"):
            if py_file.stem == "__init__":
                continue
            
            module_name = py_file.stem
            if target.lower() in module_name.lower():
                return {
                    "module": f"cortex_brain.agents.{module_name}",
                    "function": None
                }
        
        # Search for class/function names in files
        for py_file in agents_dir.glob("*.py"):
            if py_file.stem == "__init__":
                continue
            
            try:
                content = py_file.read_text()
                
                # Check for class definition
                class_match = re.search(rf"class\s+(\w*{target}\w*)\s*[:(]", content, re.IGNORECASE)
                if class_match:
                    return {
                        "module": f"cortex_brain.agents.{py_file.stem}",
                        "function": class_match.group(1)
                    }
                
                # Check for function definition
                func_match = re.search(rf"def\s+(\w*{target}\w*)\s*\(", content, re.IGNORECASE)
                if func_match:
                    return {
                        "module": f"cortex_brain.agents.{py_file.stem}",
                        "function": func_match.group(1)
                    }
            except Exception:
                continue
        
        return None
    
    def instrument_module(
        self,
        session: DebugSession,
        module_path: str,
        function_filter: Optional[Callable[[str], bool]] = None
    ) -> int:
        """
        Instrument all functions in a module.
        
        Args:
            session: Active debug session
            module_path: Module path (e.g., 'cortex_brain.agents.planner')
            function_filter: Optional filter function (takes function name, returns bool)
        
        Returns:
            Number of functions instrumented
        """
        try:
            module = importlib.import_module(module_path)
        except ImportError:
            return 0
        
        instrumented_count = 0
        
        for name, obj in inspect.getmembers(module):
            # Skip private/internal functions
            if name.startswith('_'):
                continue
            
            # Check if it's a function or method
            if not (inspect.isfunction(obj) or inspect.ismethod(obj)):
                continue
            
            # Apply filter if provided
            if function_filter and not function_filter(name):
                continue
            
            # Instrument the function
            instrumented = session.instrument_function(obj, module_path)
            setattr(module, name, instrumented)
            instrumented_count += 1
        
        return instrumented_count
    
    def get_session_report(self, session_id: str) -> Dict[str, Any]:
        """
        Get detailed report for a debug session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Detailed session report
        """
        session = self.manager.get_session(session_id)
        
        if session:
            # Active session
            return {
                "session_id": session_id,
                "status": "active",
                "duration_seconds": round(time.time() - session.start_time, 2),
                "call_count": session.call_count,
                "error_count": session.error_count,
                "instrumented_functions": list(session.instrumented_functions),
                "log_file": str(session.log_file)
            }
        else:
            # Completed session - get from history
            history = self.manager.get_session_history(limit=100)
            for record in history:
                if record['session_id'] == session_id:
                    return record
            
            return {"error": f"Session {session_id} not found"}
    
    def format_debug_response(self, action: str, result: Any) -> str:
        """
        Format debug action result for user display.
        
        Args:
            action: Action type ('start', 'stop', 'report')
            result: Action result data
        
        Returns:
            Formatted response string
        """
        if action == "start":
            session = result
            return f"""Debug session started: {session.session_id}

📊 **Session Info:**
- Target Module: {session.target_module or 'Auto-detected'}
- Target Function: {session.target_function or 'All functions'}
- Log File: {session.log_file}

Debug instrumentation is now active. All function calls will be logged.

**To stop debugging:** Say "stop debug" or "end debug session"
"""
        
        elif action == "stop":
            summary = result
            if "error" in summary:
                return f"⚠️ {summary['error']}"
            
            return f"""Debug session stopped: {summary['session_id']}

📊 **Session Summary:**
- Duration: {summary['duration_seconds']}s
- Function Calls: {summary['call_count']}
- Errors: {summary['error_count']}
- Instrumented Functions: {len(summary['instrumented_functions'])}
- Log File: {summary['log_file']}

All instrumentation removed. Debug logs saved to session directory.
"""
        
        elif action == "report":
            report = result
            if "error" in report:
                return f"⚠️ {report['error']}"
            
            status_emoji = "🟢" if report['status'] == "active" else "⚪"
            return f"""{status_emoji} Debug Session: {report['session_id']}

**Status:** {report['status']}
**Duration:** {report.get('duration_seconds', 0)}s
**Calls:** {report.get('call_count', 0)}
**Errors:** {report.get('error_count', 0)}
**Functions:** {len(report.get('instrumented_functions', []))}
"""
        
        return str(result)


def create_debug_agent(brain_root: Path) -> DebugAgent:
    """Factory function to create debug agent."""
    return DebugAgent(brain_root)
