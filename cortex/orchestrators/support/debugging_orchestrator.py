# AC-ID: AC-DEBUG-ORCH-001
"""
DebuggingOrchestrator - Smart Debug Injection System.

Provides intelligent debug log injection and cleanup for CORTEX-assisted debugging.
Uses AST analysis for strategic injection points and marker-based cleanup.

CAPABILITIES:
- Strategic log injection at function entries, exception handlers, conditionals
- Session-based injection with unique markers for surgical cleanup
- Correlation IDs for tracing execution flow
- Manifest persistence for guaranteed cleanup
- Sensitive value exclusion (passwords, API keys, tokens)

MCP TOOLS:
- cortex_debug_inject: Inject debug logs into target files
- cortex_debug_cleanup: Remove debug logs by session ID
- cortex_debug_status: Get status of debug session

GOVERNANCE:
- CORE-008: TDD (tests in tests/orchestrators/test_debugging_orchestrator.py)
- CORE-011: Type hints 100%
- CORE-012: Google-style docstrings
- CORE-027: Audit trail for all operations

Author: Asif Hussain
Date: 2026-02-03
"""

from __future__ import annotations

import ast
import hashlib
import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.result import Err, Ok, Result
from cortex.mcp.decorators import mcp_tool

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class InjectionStrategy(Enum):
    """Debug injection strategy."""
    STRATEGIC = "strategic"      # Function entries, exception handlers
    COMPREHENSIVE = "comprehensive"  # + conditionals, loops, returns


class CleanupStatus(Enum):
    """Cleanup operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class InjectionPoint:
    """
    Represents a single debug injection point.

    Attributes:
        file_path: Absolute path to the file
        line_number: Line number where injection will be placed
        injection_type: Type of injection (function_entry, exception_handler, etc.)
        trace_id: Unique trace ID for this injection point
        original_content: Original line content at this position
        function_name: Name of the function (if applicable)
        parameters: List of parameter names (if function entry)
        indentation: Number of spaces for indentation
    """
    file_path: str
    line_number: int
    injection_type: str
    trace_id: str
    original_content: str
    function_name: str = ""
    parameters: List[str] = field(default_factory=list)
    indentation: int = 0

    def get_marker(self, session_id: str) -> str:
        """
        Generate unique marker for this injection.

        Args:
            session_id: Debug session ID

        Returns:
            Unique marker string for cleanup identification
        """


@dataclass
class InjectionResult:
    """Result of an injection operation."""
    success: bool
    error: str = ""
    injections_count: int = 0


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""
    success: bool
    error: str = ""
    lines_removed: int = 0


# =============================================================================
# DEBUG SESSION
# =============================================================================

@dataclass
class DebugSession:
    """
    Debug session tracking injection state.

    Attributes:
        session_id: Unique session identifier
        target_paths: List of target file/directory paths
        strategy: Injection strategy
        created_at: Session creation timestamp
    """
    session_id: str
    target_paths: List[str]
    strategy: InjectionStrategy
    created_at: datetime

    @classmethod
    def create(
        cls,
        target_paths: List[str],
        session_id: Optional[str] = None,
        strategy: InjectionStrategy = InjectionStrategy.STRATEGIC
    ) -> DebugSession:
        """
        Create a new debug session.

        Args:
            target_paths: Paths to inject debug logs into
            session_id: Optional explicit session ID
            strategy: Injection strategy to use

        Returns:
            New DebugSession instance
        """
        if session_id is None:
            session_id = f"dbg_{uuid.uuid4().hex[:12]}"

        return cls(
            session_id=session_id,
            target_paths=target_paths,
            strategy=strategy,
            created_at=datetime.utcnow()
        )


# =============================================================================
# SESSION MANIFEST
# =============================================================================

class SessionManifest:
    """
    Manifest tracking all injections for a debug session.

    Provides persistence and cleanup tracking.
    """

    def __init__(self, session: DebugSession) -> None:
        """
        Initialize manifest for session.

        Args:
            session: Debug session to track
        """
        self.session = session
        self.injections: List[InjectionPoint] = []
        self.cleanup_status = CleanupStatus.PENDING
        self.cleaned_at: Optional[datetime] = None

    def add_injection(self, injection: InjectionPoint) -> None:
        """
        Add injection point to manifest.

        Args:
            injection: Injection point to track
        """
        self.injections.append(injection)

    def save(self, path: Path) -> None:
        """
        Save manifest to JSON file.

        Args:
            path: Path to save manifest to
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "session": {
                "id": self.session.session_id,
                "target_paths": self.session.target_paths,
                "strategy": self.session.strategy.value,
                "created_at": self.session.created_at.isoformat()
            },
            "injections": [
                {
                    "file": inj.file_path,
                    "line": inj.line_number,
                    "type": inj.injection_type,
                    "trace_id": inj.trace_id,
                    "function_name": inj.function_name
                }
                for inj in self.injections
            ],
            "cleanup": {
                "status": self.cleanup_status.value,
                "cleaned_at": self.cleaned_at.isoformat() if self.cleaned_at else None
            }
        }

        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> SessionManifest:
        """
        Load manifest from JSON file.

        Args:
            path: Path to load manifest from

        Returns:
            Loaded SessionManifest
        """
        data = json.loads(path.read_text())

        session = DebugSession(
            session_id=data["session"]["id"],
            target_paths=data["session"]["target_paths"],
            strategy=InjectionStrategy(data["session"]["strategy"]),
            created_at=datetime.fromisoformat(data["session"]["created_at"])
        )

        manifest = cls(session)

        for inj_data in data.get("injections", []):
            injection = InjectionPoint(
                file_path=inj_data["file"],
                line_number=inj_data["line"],
                injection_type=inj_data["type"],
                trace_id=inj_data["trace_id"],
                original_content="",
                function_name=inj_data.get("function_name", "")
            )
            manifest.injections.append(injection)

        manifest.cleanup_status = CleanupStatus(data["cleanup"]["status"])
        if data["cleanup"]["cleaned_at"]:
            manifest.cleaned_at = datetime.fromisoformat(data["cleanup"]["cleaned_at"])

        return manifest


# =============================================================================
# DEBUG INJECTOR
# =============================================================================

class DebugInjector:
    """
    Intelligent debug log injector using AST analysis.

    Identifies strategic injection points and generates appropriate
    debug log statements with correlation IDs.
    """

    # Parameters that should NEVER be logged (security)
    SENSITIVE_PARAMS: Set[str] = {
        "password", "passwd", "pwd", "secret", "token", "api_key",
        "apikey", "auth", "credential", "credentials", "private_key",
        "privatekey", "access_token", "refresh_token", "bearer"
    }

    def __init__(self) -> None:
        """Initialize debug injector."""
        self._trace_counter = 0

    def _next_trace_id(self) -> str:
        """Generate next trace ID."""
        self._trace_counter += 1
        return f"trace_{self._trace_counter:03d}"

    def analyze_code(
        self,
        code: str,
        strategy: InjectionStrategy = InjectionStrategy.STRATEGIC
    ) -> List[InjectionPoint]:
        """
        Analyze code and identify injection points.

        Args:
            code: Python source code to analyze
            strategy: Injection strategy to use

        Returns:
            List of identified injection points
        """
        points: List[InjectionPoint] = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return points

        lines = code.split('\n')

        for node in ast.walk(tree):
            # Function entries
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get indentation from first line of function body
                if node.body:
                    first_body_line = node.body[0].lineno - 1
                    if first_body_line < len(lines):
                        body_line = lines[first_body_line]
                        indentation = len(body_line) - len(body_line.lstrip())
                    else:
                        indentation = 4
                else:
                    indentation = 4

                # Get parameters (filter out 'self' and 'cls')
                params = [
                    arg.arg for arg in node.args.args
                    if arg.arg not in ('self', 'cls')
                ]

                point = InjectionPoint(
                    file_path="",  # Set later
                    line_number=node.lineno,
                    injection_type="function_entry",
                    trace_id=self._next_trace_id(),
                    original_content=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                    function_name=node.name,
                    parameters=params,
                    indentation=indentation
                )
                points.append(point)

            # Exception handlers
            elif isinstance(node, ast.ExceptHandler):
                if node.body:
                    first_body_line = node.body[0].lineno - 1
                    if first_body_line < len(lines):
                        body_line = lines[first_body_line]
                        indentation = len(body_line) - len(body_line.lstrip())
                    else:
                        indentation = 8
                else:
                    indentation = 8

                point = InjectionPoint(
                    file_path="",
                    line_number=node.lineno,
                    injection_type="exception_handler",
                    trace_id=self._next_trace_id(),
                    original_content=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                    function_name=f"except_{node.type.id if node.type and hasattr(node.type, 'id') else 'Exception'}",
                    indentation=indentation
                )
                points.append(point)

            # Conditionals (comprehensive mode only)
            elif strategy == InjectionStrategy.COMPREHENSIVE:
                if isinstance(node, ast.If):
                    if node.body:
                        first_body_line = node.body[0].lineno - 1
                        if first_body_line < len(lines):
                            body_line = lines[first_body_line]
                            indentation = len(body_line) - len(body_line.lstrip())
                        else:
                            indentation = 4
                    else:
                        indentation = 4

                    point = InjectionPoint(
                        file_path="",
                        line_number=node.lineno,
                        injection_type="conditional",
                        trace_id=self._next_trace_id(),
                        original_content=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                        function_name="if_branch",
                        indentation=indentation
                    )
                    points.append(point)

        return points

    def generate_log_statement(
        self,
        point: InjectionPoint,
        session_id: str
    ) -> str:
        """
        Generate debug log statement for injection point.

        Args:
            point: Injection point to generate log for
            session_id: Debug session ID

        Returns:
            Generated log statement string
        """
        # Determine indentation - use point.indentation or detect from original content
        if point.indentation > 0:
            indent = " " * point.indentation
        elif point.original_content:
            # Detect indentation from original content
            indent = " " * (len(point.original_content) - len(point.original_content.lstrip()))
        else:
            indent = ""

        marker = point.get_marker(session_id)

        if point.injection_type == "function_entry":
            # Filter out sensitive parameters
            safe_params = [
                p for p in point.parameters
                if p.lower() not in self.SENSITIVE_PARAMS
            ]

            if safe_params:
                param_format = ", ".join(f"{p}=%r" for p in safe_params)
                param_values = ", ".join(safe_params)
                log_line = (
                    f'{indent}logger.debug("CORTEX_DBG[{session_id}][{point.trace_id}] '
                    f'Enter {point.function_name} | {param_format}", {param_values})  {marker}'
                )
            else:
                log_line = (
                    f'{indent}logger.debug("CORTEX_DBG[{session_id}][{point.trace_id}] '
                    f'Enter {point.function_name}")  {marker}'
                )

        elif point.injection_type == "exception_handler":
            log_line = (
                f'{indent}logger.debug("CORTEX_DBG[{session_id}][{point.trace_id}] '
                f'Exception caught: %s", e if "e" in dir() else "unknown")  {marker}'
            )

        elif point.injection_type == "conditional":
            log_line = (
                f'{indent}logger.debug("CORTEX_DBG[{session_id}][{point.trace_id}] '
                f'Entered conditional branch")  {marker}'
            )

        else:
            log_line = (
                f'{indent}logger.debug("CORTEX_DBG[{session_id}][{point.trace_id}] '
                f'{point.injection_type}")  {marker}'
            )

        return log_line

    def inject_into_file(
        self,
        file_path: Path,
        session_id: str,
        manifest: SessionManifest,
        strategy: InjectionStrategy
    ) -> InjectionResult:
        """
        Inject debug logs into a file.

        Args:
            file_path: Path to the file to inject into
            session_id: Debug session ID
            manifest: Session manifest to track injections
            strategy: Injection strategy

        Returns:
            InjectionResult with success status
        """
        try:
            content = file_path.read_text()
        except PermissionError:
            return InjectionResult(
                success=False,
                error=f"Permission denied reading file: {file_path}"
            )

        # Analyze code for injection points
        points = self.analyze_code(content, strategy)

        if not points:
            return InjectionResult(success=True, injections_count=0)

        lines = content.split('\n')

        # Check if logging is imported
        has_logging_import = any(
            'import logging' in line or 'from cortex.common.debug_logger' in line
            for line in lines
        )

        # Track insertions (line number -> log statement)
        insertions: Dict[int, str] = {}

        for point in points:
            point.file_path = str(file_path)
            log_statement = self.generate_log_statement(point, session_id)

            # Insert AFTER the function/handler definition line
            if point.injection_type == "function_entry":
                # Find the line with the colon (could be multiline def)
                insert_line = point.line_number
                while insert_line <= len(lines) and ':' not in lines[insert_line - 1]:
                    insert_line += 1
                # Insert after the colon line
                insertions[insert_line] = log_statement
                point.line_number = insert_line
            else:
                insertions[point.line_number] = log_statement

            manifest.add_injection(point)

        # Build new content with insertions
        new_lines = []

        # Add logging import if needed
        if not has_logging_import:
            new_lines.append("")

        for i, line in enumerate(lines, 1):
            new_lines.append(line)
            if i in insertions:
                new_lines.append(insertions[i])

        try:
            file_path.write_text('\n'.join(new_lines))
        except PermissionError:
            return InjectionResult(
                success=False,
                error=f"Permission denied writing file: {file_path}"
            )

        return InjectionResult(
            success=True,
            injections_count=len(points)
        )


# =============================================================================
# DEBUG CLEANER
# =============================================================================

class DebugCleaner:
    """
    Removes debug injections using marker-based identification.

    Ensures surgical removal of only the specified session's injections.
    """

    def find_markers(self, file_path: Path, session_id: str) -> List[str]:
        """

        Args:
            file_path: Path to the file to search
            session_id: Debug session ID to find

        Returns:
            List of marker strings found
        """
        content = file_path.read_text()
        return re.findall(pattern, content)

    def clean_file(self, file_path: Path, session_id: str) -> CleanupResult:
        """
        Remove all debug injections for a session from a file.

        Args:
            file_path: Path to the file to clean
            session_id: Debug session ID to remove

        Returns:
            CleanupResult with success status
        """
        try:
            content = file_path.read_text()
        except FileNotFoundError:
            return CleanupResult(
                success=False,
                error=f"File not found: {file_path}"
            )

        lines = content.split('\n')

        # Filter out lines containing the session marker
        cleaned_lines = []
        removed_count = 0

        for line in lines:
            if re.search(marker_pattern, line):
                removed_count += 1
            else:
                cleaned_lines.append(line)

        # Write cleaned content
        file_path.write_text('\n'.join(cleaned_lines))

        return CleanupResult(
            success=True,
            lines_removed=removed_count
        )

    def clean_session(
        self,
        workspace_path: Path,
        session_id: str
    ) -> CleanupResult:
        """
        Clean all files in a session.

        Args:
            workspace_path: Path to the workspace root
            session_id: Debug session ID to clean

        Returns:
            CleanupResult with aggregate status
        """
        manifest_dir = workspace_path / ".cortex_debug"
        manifest_path = manifest_dir / f"{session_id}.json"

        if not manifest_path.exists():
            return CleanupResult(
                success=False,
                error=f"Session manifest not found: {session_id}"
            )

        manifest = SessionManifest.load(manifest_path)
        manifest.cleanup_status = CleanupStatus.IN_PROGRESS
        manifest.save(manifest_path)

        total_removed = 0

        # Get unique files from injections
        files = set(inj.file_path for inj in manifest.injections)

        for file_path in files:
            result = self.clean_file(Path(file_path), session_id)
            if result.success:
                total_removed += result.lines_removed

        manifest.cleanup_status = CleanupStatus.COMPLETE
        manifest.cleaned_at = datetime.utcnow()
        manifest.save(manifest_path)

        return CleanupResult(
            success=True,
            lines_removed=total_removed
        )


# =============================================================================
# DEBUGGING ORCHESTRATOR
# =============================================================================

class DebuggingOrchestrator(IOrchestrator):
    """
    Smart Debug Injection Orchestrator.

    Provides intelligent debug log injection and cleanup for CORTEX-assisted
    debugging. Uses AST analysis for strategic injection points and
    marker-based cleanup for guaranteed removal.

    MCP Tools:
        - cortex_debug_inject: Inject debug logs into target files
        - cortex_debug_cleanup: Remove debug logs by session ID
        - cortex_debug_status: Get status of debug session

    Example:
        >>> orchestrator = DebuggingOrchestrator()
        >>> result = orchestrator.execute_operation(
        ...     "inject",
        ...     {"target_paths": ["/path/to/code"], "strategy": "strategic"}
        ... )
        >>> session_id = result.unwrap()["session_id"]
        >>> # ... debug issue ...
        >>> orchestrator.execute_operation(
        ...     "cleanup",
        ...     {"session_id": session_id, "workspace_path": "/path"}
        ... )
    """

    def __init__(self) -> None:
        """Initialize debugging orchestrator."""
        self._injector = DebugInjector()
        self._cleaner = DebugCleaner()
        self._audit_trail: List[Dict[str, Any]] = []

    def get_name(self) -> str:
        """Get orchestrator name."""
        return "DebuggingOrchestrator"

    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0"

    def initialize(self) -> Result[str]:
        """Initialize orchestrator."""
        return Ok("DebuggingOrchestrator initialized")

    def get_mode(self) -> OperationMode:
        """Get current operation mode."""
        return OperationMode.EXECUTION

    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """
        Get exposed MCP tools.

        Returns:
            Dict of MCP tool definitions
        """
        return Ok({
            "cortex_debug_inject": {
                "name": "cortex_debug_inject",
                "description": "Inject smart debug logs into target files",
                "parameters": {
                    "target_paths": "list[str]",
                    "strategy": "str",
                    "session_id": "str (optional)"
                }
            },
            "cortex_debug_cleanup": {
                "name": "cortex_debug_cleanup",
                "description": "Remove debug logs by session ID",
                "parameters": {
                    "session_id": "str",
                    "workspace_path": "str"
                }
            },
            "cortex_debug_status": {
                "name": "cortex_debug_status",
                "description": "Get status of debug session",
                "parameters": {
                    "session_id": "str",
                    "workspace_path": "str"
                }
            }
        })

    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any]
    ) -> Result[Any]:
        """
        Execute debugging operation.

        Args:
            operation_name: Name of operation (inject, cleanup, status)
            parameters: Operation parameters

        Returns:
            Result with operation output
        """
        self._log_audit(operation_name, parameters)

        if operation_name == "inject":
            return self._execute_inject(parameters)
        elif operation_name == "cleanup":
            return self._execute_cleanup(parameters)
        elif operation_name == "status":
            return self._execute_status(parameters)
        else:
            return Err(f"Unknown operation: {operation_name}")

    def _execute_inject(self, parameters: Dict[str, Any]) -> Result[Dict[str, Any]]:
        """Execute inject operation."""
        target_paths = parameters.get("target_paths", [])
        strategy_str = parameters.get("strategy", "strategic")
        session_id = parameters.get("session_id")

        # Validate paths exist
        for path in target_paths:
            if not Path(path).exists():
                return Err(f"Path not found: {path}")

        # Parse strategy
        try:
            strategy = InjectionStrategy(strategy_str)
        except ValueError:
            strategy = InjectionStrategy.STRATEGIC

        # Create session
        session = DebugSession.create(
            target_paths=target_paths,
            session_id=session_id,
            strategy=strategy
        )
        manifest = SessionManifest(session)

        total_injections = 0

        for target_path in target_paths:
            path = Path(target_path)

            if path.is_file() and path.suffix == '.py':
                result = self._injector.inject_into_file(
                    path, session.session_id, manifest, strategy
                )
                if result.success:
                    total_injections += result.injections_count

            elif path.is_dir():
                for py_file in path.rglob("*.py"):
                    # Skip test files and __pycache__
                    if "__pycache__" in str(py_file) or "test_" in py_file.name:
                        continue

                    result = self._injector.inject_into_file(
                        py_file, session.session_id, manifest, strategy
                    )
                    if result.success:
                        total_injections += result.injections_count

        # Save manifest
        workspace_path = Path(target_paths[0]).parent
        if Path(target_paths[0]).is_dir():
            workspace_path = Path(target_paths[0])

        manifest_path = workspace_path / ".cortex_debug" / f"{session.session_id}.json"
        manifest.save(manifest_path)

        return Ok({
            "session_id": session.session_id,
            "injections_count": total_injections,
            "manifest_path": str(manifest_path)
        })

    def _execute_cleanup(self, parameters: Dict[str, Any]) -> Result[Dict[str, Any]]:
        """Execute cleanup operation."""
        session_id = parameters.get("session_id")
        workspace_path = parameters.get("workspace_path")

        if not session_id:
            return Err("session_id is required")
        if not workspace_path:
            return Err("workspace_path is required")

        result = self._cleaner.clean_session(Path(workspace_path), session_id)

        if not result.success:
            return Err(result.error)

        return Ok({
            "status": "complete",
            "lines_removed": result.lines_removed,
            "session_id": session_id
        })

    def _execute_status(self, parameters: Dict[str, Any]) -> Result[Dict[str, Any]]:
        """Execute status operation."""
        session_id = parameters.get("session_id")
        workspace_path = parameters.get("workspace_path")

        if not session_id or not workspace_path:
            return Err("session_id and workspace_path are required")

        manifest_path = Path(workspace_path) / ".cortex_debug" / f"{session_id}.json"

        if not manifest_path.exists():
            return Err(f"Session not found: {session_id}")

        manifest = SessionManifest.load(manifest_path)

        return Ok({
            "session_id": session_id,
            "injections": len(manifest.injections),
            "cleanup_status": manifest.cleanup_status.value,
            "created_at": manifest.session.created_at.isoformat(),
            "target_paths": manifest.session.target_paths
        })

    def _log_audit(self, operation: str, parameters: Dict[str, Any]) -> None:
        """Log operation to audit trail."""
        self._audit_trail.append({
            "operation": operation,
            "parameters": {k: v for k, v in parameters.items() if k != "password"},
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_audit_trail(self, limit: int = 100) -> Result[List[Dict[str, Any]]]:
        """
        Get audit trail of operations.

        Args:
            limit: Maximum entries to return

        Returns:
            List of audit trail entries
        """
        return Ok(self._audit_trail[-limit:])


# =============================================================================
# MCP TOOL FUNCTIONS
# =============================================================================

@mcp_tool(
    name="cortex_debug_inject",
    description="Inject smart debug logs into target Python files for CORTEX-assisted debugging",
    parameters={
        "target_paths": "list[str] - Paths to files or directories to inject debug logs into",
        "strategy": "str - 'strategic' (function entries, exceptions) or 'comprehensive' (+ conditionals)",
        "session_id": "str (optional) - Explicit session ID, auto-generated if not provided"
    },
    category="debugging"
)
def cortex_debug_inject(
    target_paths: List[str],
    strategy: str = "strategic",
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Inject smart debug logs into target files.

    Args:
        target_paths: Paths to files or directories to inject into
        strategy: Injection strategy ('strategic' or 'comprehensive')
        session_id: Optional explicit session ID

    Returns:
        Dict with session_id, injections_count, manifest_path
    """
    orchestrator = DebuggingOrchestrator()
    result = orchestrator.execute_operation(
        "inject",
        {
            "target_paths": target_paths,
            "strategy": strategy,
            "session_id": session_id
        }
    )

    if result.is_ok():
        return result.unwrap()
    else:
        return {"error": result.error}


@mcp_tool(
    name="cortex_debug_cleanup",
    description="Remove all debug logs for a specific session ID",
    parameters={
        "session_id": "str - Debug session ID to clean up",
        "workspace_path": "str - Path to the workspace root"
    },
    category="debugging"
)
def cortex_debug_cleanup(
    session_id: str,
    workspace_path: str
) -> Dict[str, Any]:
    """
    Remove all debug logs for a session.

    Args:
        session_id: Debug session ID to clean up
        workspace_path: Path to the workspace root

    Returns:
        Dict with status, lines_removed, session_id
    """
    orchestrator = DebuggingOrchestrator()
    result = orchestrator.execute_operation(
        "cleanup",
        {
            "session_id": session_id,
            "workspace_path": workspace_path
        }
    )

    if result.is_ok():
        return result.unwrap()
    else:
        return {"error": result.error}


@mcp_tool(
    name="cortex_debug_status",
    description="Get status of a debug session",
    parameters={
        "session_id": "str - Debug session ID to check",
        "workspace_path": "str - Path to the workspace root"
    },
    category="debugging"
)
def cortex_debug_status(
    session_id: str,
    workspace_path: str
) -> Dict[str, Any]:
    """
    Get status of a debug session.

    Args:
        session_id: Debug session ID to check
        workspace_path: Path to the workspace root

    Returns:
        Dict with session info, injections count, cleanup status
    """
    orchestrator = DebuggingOrchestrator()
    result = orchestrator.execute_operation(
        "status",
        {
            "session_id": session_id,
            "workspace_path": workspace_path
        }
    )

    if result.is_ok():
        return result.unwrap()
    else:
        return {"error": result.error}


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "InjectionStrategy",
    "CleanupStatus",
    # Data classes
    "InjectionPoint",
    "InjectionResult",
    "CleanupResult",
    # Session management
    "DebugSession",
    "SessionManifest",
    # Core components
    "DebugInjector",
    "DebugCleaner",
    "DebuggingOrchestrator",
    # MCP tools
    "cortex_debug_inject",
    "cortex_debug_cleanup",
    "cortex_debug_status",
]
