"""
CORTEX Debug Orchestrator - Python MCP Tool Integration
========================================================

Provides MCP tools for comprehensive debugging capabilities:
- cortex_debug_inject: Inject debug markers into codebase
- cortex_debug_capture: Capture console logs during execution
- cortex_debug_analyze: Analyze captured logs for issues
- cortex_debug_cleanup: Remove debug markers when done
- cortex_debug_status: Show current debug session status

Supports multiple technology stacks:
- JavaScript/TypeScript (React, Angular, Vue, Vanilla)
- Python (Django, Flask, FastAPI)
- C# (.NET Core, ASP.NET, Blazor)

Author: CORTEX
Version: 1.0.0
"""

import json
import os
import re
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# CORTEX imports
try:
    from cortex.mcp.decorators import mcp_tool
    from cortex.mcp.types import ToolResult
except ImportError:
    # Fallback for standalone usage
    def mcp_tool(name: str, description: str):
        def decorator(func):
            func._mcp_tool_name = name
            func._mcp_tool_description = description
            return func
        return decorator

    @dataclass
    class ToolResult:
        success: bool
        data: Any = None
        error: str = None


# Constants
DEBUG_DIR = ".cortex-debug"


class TechnologyStack(Enum):
    """Supported technology stacks"""
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    REACT = "react"
    ANGULAR = "angular"
    VUE = "vue"
    PYTHON = "python"
    DJANGO = "django"
    FLASK = "flask"
    FASTAPI = "fastapi"
    CSHARP = "csharp"
    DOTNET = "dotnet"
    ASPNET = "aspnet"
    UNKNOWN = "unknown"


class IssueSeverity(Enum):
    """Issue severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class DebugInjection:
    """Represents a single debug injection"""
    file: str
    line: int
    marker: str
    injection_type: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DebugSession:
    """Represents a debug session"""
    session_id: str
    base_path: str
    stack: TechnologyStack
    status: str = "initialized"
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    injections: List[DebugInjection] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "sessionId": self.session_id,
            "basePath": self.base_path,
            "stack": self.stack.value,
            "status": self.status,
            "startTime": self.start_time,
            "totalInjections": len(self.injections),
            "files": list(set(i.file for i in self.injections))
        }


@dataclass
class AnalysisIssue:
    """Represents an issue found during analysis"""
    issue_type: str
    severity: IssueSeverity
    description: str
    file: Optional[str] = None
    line: Optional[int] = None
    suggestion: Optional[str] = None
    related_markers: List[str] = field(default_factory=list)


class StackDetector:
    """Detects technology stack from project structure"""

    INDICATORS = {
        # JavaScript/TypeScript
        "package.json": TechnologyStack.JAVASCRIPT,
        "tsconfig.json": TechnologyStack.TYPESCRIPT,

        # React
        "src/App.jsx": TechnologyStack.REACT,
        "src/App.tsx": TechnologyStack.REACT,

        # Angular
        "angular.json": TechnologyStack.ANGULAR,

        # Vue
        "vue.config.js": TechnologyStack.VUE,

        # Python
        "requirements.txt": TechnologyStack.PYTHON,
        "pyproject.toml": TechnologyStack.PYTHON,
        "setup.py": TechnologyStack.PYTHON,

        # Django
        "manage.py": TechnologyStack.DJANGO,

        # C#/.NET
        "Program.cs": TechnologyStack.ASPNET,
    }

    @classmethod
    def detect(cls, base_path: Path) -> TechnologyStack:
        """Detect technology stack from project structure"""
        for indicator, stack in cls.INDICATORS.items():
            if (base_path / indicator).exists():
                return stack

        # Check for .csproj files
        if list(base_path.glob("*.csproj")):
            return TechnologyStack.CSHARP

        # Check for .sln files
        if list(base_path.glob("*.sln")):
            return TechnologyStack.DOTNET

        return TechnologyStack.UNKNOWN


class LanguageAdapter:
    """Base class for language-specific adapters"""

    def __init__(self, session_id: str, base_path: Path):
        self.session_id = session_id
        self.base_path = base_path
        self.extensions: Set[str] = set()
        self.exclude_dirs: Set[str] = set()

    def get_target_files(self) -> List[Path]:
        """Get files to inject markers into"""
        files = []
        for ext in self.extensions:
            for file_path in self.base_path.rglob(f"*{ext}"):
                # Check if in excluded directory
                if not any(exc in file_path.parts for exc in self.exclude_dirs):
                    files.append(file_path)
        return files

    def inject_file(self, content: str, file_name: str) -> tuple[str, int]:
        """Inject markers into file content. Returns (modified_content, injection_count)"""
        raise NotImplementedError

    def clean_file(self, content: str) -> tuple[str, int]:
        """Remove markers from file content. Returns (cleaned_content, removed_count)"""
        raise NotImplementedError

    def create_marker(self, phase: str, file_name: str, line_num: int, message: str = "") -> str:
        """Create a unique debug marker"""
        return f"[{MARKER_PREFIX}{self.session_id}:{phase}:{file_name}:{line_num}] {message}"


class JavaScriptAdapter(LanguageAdapter):
    """JavaScript/TypeScript adapter"""

    def __init__(self, session_id: str, base_path: Path):
        super().__init__(session_id, base_path)
        self.extensions = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"}
        self.exclude_dirs = {"node_modules", "dist", "build", ".next", ".nuxt", "vendor", ".git"}

    def inject_file(self, content: str, file_name: str) -> tuple[str, int]:
        lines = content.split("\n")
        result = []
        injections = 0

        for line_num, line in enumerate(lines, 1):
            result.append(line)

            # Skip if already has marker
            if MARKER_PREFIX in line:
                continue

            # Function/method detection patterns
            func_patterns = [
                r"^\s*(async\s+)?(function\s+)?(\w+)\s*\([^)]*\)\s*\{?\s*$",
                r"^\s*(const|let|var)\s+(\w+)\s*=\s*(async\s*)?\([^)]*\)\s*=>\s*\{",
                r"^\s*(async\s+)?(\w+)\s*\([^)]*\)\s*\{\s*$"
            ]

            for pattern in func_patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    func_name = next((g for g in groups if g and g not in ("async", "const", "let", "var", "function")), None)

                    if func_name and func_name not in ("constructor", "toString", "valueOf", "get", "set", "if", "for", "while"):
                        indent_match = re.match(r"^(\s*)", line)
                        indent = (indent_match.group(1) if indent_match else "") + "    "
                        marker = self.create_marker("FUNC", file_name, line_num, f"ENTER {func_name}")
                        result.append(f"{indent}console.log('{marker}');")
                        injections += 1
                        break

        return "\n".join(result), injections

    def clean_file(self, content: str) -> tuple[str, int]:
        patterns = [
        ]

        modified = content
        removed = 0

        for pattern in patterns:
            matches = re.findall(pattern, modified, re.MULTILINE)
            removed += len(matches)
            modified = re.sub(pattern, "", modified, flags=re.MULTILINE)

        # Clean up excessive blank lines
        modified = re.sub(r"\n{3,}", "\n\n", modified)

        return modified, removed


class PythonAdapter(LanguageAdapter):
    """Python adapter"""

    def __init__(self, session_id: str, base_path: Path):
        super().__init__(session_id, base_path)
        self.extensions = {".py"}
        self.exclude_dirs = {"__pycache__", ".venv", "venv", "env", ".tox", "dist", "build", ".git"}

    def inject_file(self, content: str, file_name: str) -> tuple[str, int]:
        lines = content.split("\n")
        result = []
        injections = 0

        for line_num, line in enumerate(lines, 1):
            result.append(line)

            if MARKER_PREFIX in line:
                continue

            # Function definition
            func_match = re.match(r"^(\s*)(async\s+)?def\s+(\w+)\s*\([^)]*\)\s*(?:->.*)?:\s*$", line)

            if func_match:
                indent = func_match.group(1)
                func_name = func_match.group(3)

                # Skip dunder methods
                if func_name.startswith("__") and func_name.endswith("__"):
                    continue

                marker = self.create_marker("FUNC", file_name, line_num, f"ENTER {func_name}")
                result.append(f'{indent}    print(f"{marker}")')
                injections += 1

        return "\n".join(result), injections

    def clean_file(self, content: str) -> tuple[str, int]:
        patterns = [
        ]

        modified = content
        removed = 0

        for pattern in patterns:
            matches = re.findall(pattern, modified, re.MULTILINE)
            removed += len(matches)
            modified = re.sub(pattern, "", modified, flags=re.MULTILINE)

        return modified, removed


class CSharpAdapter(LanguageAdapter):
    """C#/.NET adapter"""

    def __init__(self, session_id: str, base_path: Path):
        super().__init__(session_id, base_path)
        self.extensions = {".cs"}
        self.exclude_dirs = {"bin", "obj", "packages", ".vs", ".git"}

    def inject_file(self, content: str, file_name: str) -> tuple[str, int]:
        lines = content.split("\n")
        result = []
        injections = 0

        for line_num, line in enumerate(lines, 1):
            result.append(line)

            if MARKER_PREFIX in line:
                continue

            # Method definition
            method_match = re.match(
                r"^(\s*)(public|private|protected|internal)?\s*(static)?\s*(async)?\s*([\w<>\[\]]+)\s+(\w+)\s*\([^)]*\)\s*\{?\s*$",
                line
            )

            if method_match:
                indent = method_match.group(1)
                method_name = method_match.group(6)

                skip_methods = {"Main", "Dispose", "ToString", "GetHashCode", "Equals"}
                if method_name in skip_methods:
                    continue

                marker = self.create_marker("METHOD", file_name, line_num, f"ENTER {method_name}")
                result.append(f'{indent}    System.Diagnostics.Debug.WriteLine($"{marker}");')
                injections += 1

        return "\n".join(result), injections

    def clean_file(self, content: str) -> tuple[str, int]:
        patterns = [
        ]

        modified = content
        removed = 0

        for pattern in patterns:
            matches = re.findall(pattern, modified, re.MULTILINE)
            removed += len(matches)
            modified = re.sub(pattern, "", modified, flags=re.MULTILINE)

        return modified, removed


def get_adapter(stack: TechnologyStack, session_id: str, base_path: Path) -> LanguageAdapter:
    """Get appropriate adapter for technology stack"""
    adapters = {
        TechnologyStack.JAVASCRIPT: JavaScriptAdapter,
        TechnologyStack.TYPESCRIPT: JavaScriptAdapter,
        TechnologyStack.REACT: JavaScriptAdapter,
        TechnologyStack.ANGULAR: JavaScriptAdapter,
        TechnologyStack.VUE: JavaScriptAdapter,
        TechnologyStack.PYTHON: PythonAdapter,
        TechnologyStack.DJANGO: PythonAdapter,
        TechnologyStack.FLASK: PythonAdapter,
        TechnologyStack.FASTAPI: PythonAdapter,
        TechnologyStack.CSHARP: CSharpAdapter,
        TechnologyStack.DOTNET: CSharpAdapter,
        TechnologyStack.ASPNET: CSharpAdapter,
    }

    adapter_class = adapters.get(stack, JavaScriptAdapter)
    return adapter_class(session_id, base_path)


# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp_tool(
    name="cortex_debug_inject",
)
def debug_inject(
    path: str,
    stack: str = "auto"
) -> ToolResult:
    """
    Inject debug markers into all relevant source files.

    Args:
        path: Base path to the project
        stack: Technology stack (auto, javascript, python, csharp, etc.)

    Returns:
        ToolResult with session info and injection statistics
    """
    base_path = Path(path).resolve()

    if not base_path.exists():
        return ToolResult(success=False, error=f"Path not found: {path}")

    # Detect or parse stack
    if stack == "auto":
        detected_stack = StackDetector.detect(base_path)
    else:
        try:
            detected_stack = TechnologyStack(stack)
        except ValueError:
            detected_stack = TechnologyStack.UNKNOWN

    # Generate session
    session_id = uuid.uuid4().hex[:8]
    session = DebugSession(
        session_id=session_id,
        base_path=str(base_path),
        stack=detected_stack
    )

    # Create debug directory
    debug_dir = base_path / DEBUG_DIR
    debug_dir.mkdir(exist_ok=True)
    backup_dir = debug_dir / "backups"
    backup_dir.mkdir(exist_ok=True)

    # Get adapter and inject
    adapter = get_adapter(detected_stack, session_id, base_path)
    target_files = adapter.get_target_files()

    total_injections = 0
    modified_files = []

    for file_path in target_files:
        try:
            content = file_path.read_text(encoding="utf-8")

            # Backup original
            backup_name = str(file_path.relative_to(base_path)).replace(os.sep, "_")
            (backup_dir / backup_name).write_text(content, encoding="utf-8")

            # Inject markers
            modified, injection_count = adapter.inject_file(content, file_path.name)

            if injection_count > 0:
                file_path.write_text(modified, encoding="utf-8")
                total_injections += injection_count
                modified_files.append(str(file_path.relative_to(base_path)))

                session.injections.append(DebugInjection(
                    file=str(file_path.relative_to(base_path)),
                    line=0,  # Summary
                    marker=f"{injection_count} injections",
                    injection_type="multiple"
                ))
        except Exception:
            # Log but continue
            pass

    session.status = "injected"

    # Save session
    session_path = debug_dir / "session.json"
    session_path.write_text(json.dumps(session.to_dict(), indent=2))

    return ToolResult(
        success=True,
        data={
            "sessionId": session_id,
            "stack": detected_stack.value,
            "totalInjections": total_injections,
            "filesModified": len(modified_files),
            "files": modified_files[:20],  # Limit output
            "debugDir": str(debug_dir)
        }
    )


@mcp_tool(
    name="cortex_debug_cleanup",
)
def debug_cleanup(
    path: str,
    confirm: bool = False,
    use_backups: bool = True
) -> ToolResult:
    """
    Clean up debug markers from codebase.

    Args:
        path: Base path to the project
        confirm: Must be True to actually perform cleanup (dry-run otherwise)
        use_backups: Whether to restore from backups if available

    Returns:
        ToolResult with cleanup statistics
    """
    base_path = Path(path).resolve()
    debug_dir = base_path / DEBUG_DIR
    backup_dir = debug_dir / "backups"

    stats = {
        "filesProcessed": 0,
        "filesModified": 0,
        "markersRemoved": 0,
        "restoredFromBackup": 0,
        "errors": []
    }

    # Try to restore from backups first
    if use_backups and backup_dir.exists():
        for backup_file in backup_dir.iterdir():
            original_rel_path = backup_file.name.replace("_", os.sep)
            original_path = base_path / original_rel_path

            try:
                if confirm:
                    backup_content = backup_file.read_text(encoding="utf-8")
                    original_path.write_text(backup_content, encoding="utf-8")
                stats["restoredFromBackup"] += 1
            except Exception as e:
                stats["errors"].append(f"{original_rel_path}: {str(e)}")

    # If no backups or restore failed, use pattern-based cleanup
    if stats["restoredFromBackup"] == 0:
        # Detect stack
        detected_stack = StackDetector.detect(base_path)
        adapter = get_adapter(detected_stack, "", base_path)

        for file_path in adapter.get_target_files():
            stats["filesProcessed"] += 1

            try:
                content = file_path.read_text(encoding="utf-8")

                if MARKER_PREFIX not in content:
                    continue

                cleaned, removed = adapter.clean_file(content)

                if removed > 0:
                    stats["markersRemoved"] += removed
                    stats["filesModified"] += 1

                    if confirm:
                        file_path.write_text(cleaned, encoding="utf-8")
            except Exception as e:
                stats["errors"].append(f"{file_path.name}: {str(e)}")

    # Clean up debug directory if confirmed and successful
    if confirm and not stats["errors"]:
        # Update session status
        session_path = debug_dir / "session.json"
        if session_path.exists():
            session_data = json.loads(session_path.read_text())
            session_data["status"] = "cleaned"
            session_data["cleanupTime"] = datetime.now().isoformat()
            session_data["cleanupStats"] = stats
            session_path.write_text(json.dumps(session_data, indent=2))

        # Remove backups
        if backup_dir.exists():
            import shutil
            shutil.rmtree(backup_dir)

    return ToolResult(
        success=len(stats["errors"]) == 0,
        data={
            **stats,
            "dryRun": not confirm,
            "message": "Cleanup complete" if confirm else "Dry run - use confirm=True to apply"
        }
    )


@mcp_tool(
    name="cortex_debug_status",
    description="Show current debug session status and available artifacts."
)
def debug_status(path: str) -> ToolResult:
    """
    Get status of current debug session.

    Args:
        path: Base path to the project

    Returns:
        ToolResult with session status and available files
    """
    base_path = Path(path).resolve()
    debug_dir = base_path / DEBUG_DIR
    session_path = debug_dir / "session.json"

    if not session_path.exists():
        return ToolResult(
            success=True,
            data={
                "active": False,
                "message": "No active debug session. Run cortex_debug_inject to start."
            }
        )

    session_data = json.loads(session_path.read_text())

    # Check available files
    available_files = {}
    for file_name in ["injection-map.json", "captured-logs.json", "analysis-report.json", "fix-plan.md"]:
        file_path = debug_dir / file_name
        available_files[file_name] = file_path.exists()

    return ToolResult(
        success=True,
        data={
            "active": True,
            "session": session_data,
            "availableFiles": available_files,
            "debugDir": str(debug_dir)
        }
    )


# Export for MCP registration
TOOLS = [
    debug_inject,
    debug_cleanup,
    debug_status
]

__all__ = [
    "debug_inject",
    "debug_cleanup",
    "debug_status",
    "TOOLS",
    "TechnologyStack",
    "StackDetector",
    "get_adapter",
    "MARKER_PREFIX"
]
