"""
Native Tool Interception Layer - MCP-FIRST Enforcement.

Prevents native tool bypass for IMPLEMENT/FIX/REFACTOR intents by intercepting
direct file operations and redirecting to MCP tools.

Authority: CORE-049 (MCP-FIRST), CORE-050 (MCP Circuit Breaker)
Phase: WAVE-2 MCP Enforcement
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, Callable
import os


class Intent(Enum):
    """User request intent classification."""
    IMPLEMENT = "IMPLEMENT"
    FIX = "FIX"
    REFACTOR = "REFACTOR"
    ANALYZE = "ANALYZE"
    AUDIT = "AUDIT"
    PLAN = "PLAN"
    QUERY = "QUERY"
    LIST = "LIST"
    DIAGNOSE = "DIAGNOSE"
    SETUP = "SETUP"


class ToolCategory(Enum):
    """Native tool categorization for interception rules."""
    FILE_MODIFICATION = "FILE_MODIFICATION"  # create_file, replace_string_in_file, edit_files
    FILE_READ = "FILE_READ"  # read_file, grep_search, semantic_search
    EXECUTION = "EXECUTION"  # run_in_terminal (file ops only)
    DISCOVERY = "DISCOVERY"  # file_search, list_dir
    MCP_TOOL = "MCP_TOOL"  # cortex_process_request, cortex_lens_analyze


@dataclass
class InterceptionResult:
    """Result of tool interception check."""
    allowed: bool
    reason: str
    alternative: Optional[str] = None
    mcp_tool: Optional[str] = None


class MCPDetector:
    """
    Multi-method MCP availability detector.
    
    Uses 3-method cascade for robust detection:
    1. Tool Query (check if cortex_* tools exist)
    2. Environment Variables (CORTEX_MCP_ENABLED)
    3. Configuration File (.vscode/settings.json)
    """
    
    @staticmethod
    def is_mcp_available() -> bool:
        """
        Check if MCP is available using 3-method cascade.
        
        Returns:
            bool: True if MCP is available, False otherwise
        """
        # Method 1: Environment variable (fastest)
        if os.getenv("CORTEX_MCP_ENABLED") == "true":
            return True
        
        # Method 2: Check .vscode/settings.json
        settings_path = ".vscode/settings.json"
        if os.path.exists(settings_path):
            try:
                import json
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    if "github.copilot.chat.mcpServers" in settings:
                        if "cortex" in settings["github.copilot.chat.mcpServers"]:
                            return True
            except Exception:
                pass
        
        # Method 3: Assume unavailable (safe default)
        return False


class NativeToolInterceptor:
    """
    Intercepts native tool calls and enforces MCP-FIRST for code-modifying intents.
    
    Rules (CORE-050 Tiered Blocking):
    - IMPLEMENT/FIX/REFACTOR: HARD BLOCK if MCP unavailable
    - AUDIT/ANALYZE/PLAN: HARD BLOCK if MCP unavailable
    - DIAGNOSE/QUERY/SETUP/LIST: EXEMPT (always allow)
    
    Example:
        >>> interceptor = NativeToolInterceptor()
        >>> result = interceptor.check("create_file", Intent.IMPLEMENT, "src/main.py")
        >>> if not result.allowed:
        ...     print(f"Blocked: {result.reason}")
        ...     print(f"Use: {result.mcp_tool}")
    """
    
    # Intent-based tool restriction matrix
    BLOCKED_INTENTS = {
        Intent.IMPLEMENT,
        Intent.FIX,
        Intent.REFACTOR,
        Intent.AUDIT,
        Intent.ANALYZE,
        Intent.PLAN,
    }
    
    EXEMPT_INTENTS = {
        Intent.DIAGNOSE,
        Intent.QUERY,
        Intent.SETUP,
        Intent.LIST,
    }
    
    # Tool categorization
    TOOL_CATEGORIES = {
        "create_file": ToolCategory.FILE_MODIFICATION,
        "replace_string_in_file": ToolCategory.FILE_MODIFICATION,
        "edit_files": ToolCategory.FILE_MODIFICATION,
        "edit_notebook_file": ToolCategory.FILE_MODIFICATION,
        "run_in_terminal": ToolCategory.EXECUTION,
        "read_file": ToolCategory.FILE_READ,
        "grep_search": ToolCategory.FILE_READ,
        "semantic_search": ToolCategory.FILE_READ,
        "file_search": ToolCategory.DISCOVERY,
        "list_dir": ToolCategory.DISCOVERY,
        "cortex_process_request": ToolCategory.MCP_TOOL,
        "cortex_lens_analyze": ToolCategory.MCP_TOOL,
    }
    
    def __init__(self) -> None:
        """Initialize interceptor with MCP detector."""
        self.detector = MCPDetector()
    
    def check(
        self,
        tool_name: str,
        intent: Intent,
        target_file: Optional[str] = None,
        **kwargs
    ) -> InterceptionResult:
        """
        Check if native tool invocation is allowed for given intent.
        
        Args:
            tool_name: Name of native tool being invoked
            intent: Classified user intent
            target_file: Target file path (optional)
            **kwargs: Additional context
            
        Returns:
            InterceptionResult with allowed flag and reasoning
        """
        # Exempt intents always allowed (escape hatch)
        if intent in self.EXEMPT_INTENTS:
            return InterceptionResult(
                allowed=True,
                reason=f"Intent {intent.value} exempt from MCP requirements"
            )
        
        # Get tool category
        category = self.TOOL_CATEGORIES.get(tool_name)
        if category is None:
            # Unknown tool, allow (safe default for extensibility)
            return InterceptionResult(
                allowed=True,
                reason=f"Unknown tool {tool_name}, allowing"
            )
        
        # MCP tools always allowed
        if category == ToolCategory.MCP_TOOL:
            return InterceptionResult(
                allowed=True,
                reason="MCP tool invocation"
            )
        
        # Read/discovery tools allowed for all intents
        if category in (ToolCategory.FILE_READ, ToolCategory.DISCOVERY):
            return InterceptionResult(
                allowed=True,
                reason=f"Read-only operation for {intent.value}"
            )
        
        # File modification tools: Check MCP availability
        if category == ToolCategory.FILE_MODIFICATION:
            if intent in self.BLOCKED_INTENTS:
                mcp_available = self.detector.is_mcp_available()
                
                if not mcp_available:
                    return InterceptionResult(
                        allowed=False,
                        reason=f"MCP required for {intent.value} intent (CORE-050)",
                        alternative="Run: python .cortex-runtime/setup-mcp.py → Reload VS Code",
                        mcp_tool="cortex_process_request"
                    )
                
                # MCP available: Still block direct file ops for production code
                if target_file and self._is_production_code(target_file):
                    return InterceptionResult(
                        allowed=False,
                        reason=f"Production code modification requires MCP (CORE-049)",
                        mcp_tool="cortex_process_request"
                    )
        
        # Execution tools: Restrict file operations
        if category == ToolCategory.EXECUTION:
            command = kwargs.get("command", "")
            if command and self._is_file_operation(command):
                if intent in self.BLOCKED_INTENTS:
                    return InterceptionResult(
                        allowed=False,
                        reason=f"File operations via terminal blocked for {intent.value}",
                        mcp_tool="cortex_process_request"
                    )
        
        # Default: Allow
        return InterceptionResult(
            allowed=True,
            reason="Tool allowed for intent"
        )
    
    @staticmethod
    def _is_production_code(file_path: str) -> bool:
        """Check if file is production code (not docs/tests/config)."""
        if not file_path:
            return False
        
        # Extensions for production code
        code_extensions = {".py", ".ts", ".js", ".tsx", ".jsx", ".cs", ".java"}
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in code_extensions:
            return False
        
        # Exclude non-production paths
        excluded_paths = {
            "tests/",
            "test/",
            "docs/",
            "documentation/",
            ".github/",
            "scripts/",
            "examples/",
        }
        
        for excluded in excluded_paths:
            if excluded in file_path:
                return False
        
        return True
    
    @staticmethod
    def _is_file_operation(command: str) -> bool:
        """Check if terminal command performs file operations."""
        file_ops = {
            "touch ",
            " > ",  # Redirect output
            " >> ",  # Append output
            "cat >",
            "echo >",
            "echo >>",
            "tee ",
            "sed -i",
            "awk",
            "perl -i",
        }
        
        return any(op in command for op in file_ops)


# Global interceptor instance
_interceptor = NativeToolInterceptor()


def check_tool_allowed(
    tool_name: str,
    intent: Intent,
    target_file: Optional[str] = None,
    **kwargs
) -> InterceptionResult:
    """
    Global function to check if tool invocation is allowed.
    
    Use this before invoking any native tool.
    
    Example:
        >>> result = check_tool_allowed("create_file", Intent.IMPLEMENT, "src/main.py")
        >>> if not result.allowed:
        ...     raise Exception(result.reason)
    """
    return _interceptor.check(tool_name, intent, target_file, **kwargs)
