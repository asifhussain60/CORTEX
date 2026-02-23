"""
Native Tool Gate - Pre-tool Invocation Blocking
Authority: CORE-049, MCP-FIRST, ENH-055 Phase 4, GAP-001 Fix
Purpose: Prevent Copilot native tool bypass for IMPLEMENT/FIX/REFACTOR intents

This module implements a pre-tool invocation check that blocks native file
modification tools (create_file, replace_string_in_file, etc.) when the user's
intent is IMPLEMENT/FIX/REFACTOR and targeting production code files.

Key Features:
- Intent classification from user requests
- Production code file detection
- Intent-tool restriction matrix enforcement
- Bypass attempt logging for audit trail
- Clear error messages with MCP setup instructions

Example:
    gate = NativeToolGate()
    
    # Before invoking any tool
    is_blocked, error_msg = gate.check_and_block(
        tool_name="create_file",
        intent=IntentType.IMPLEMENT,
        target_file="cortex/module.py"
    )
    
    if is_blocked:
        print(error_msg)  # Show MCP setup instructions
        return HALT_EXECUTION
"""

import os
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple, Set
import yaml


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntentType(Enum):
    """User intent classification."""
    IMPLEMENT = "IMPLEMENT"
    FIX = "FIX"
    REFACTOR = "REFACTOR"
    ANALYZE = "ANALYZE"
    AUDIT = "AUDIT"
    DESIGN = "DESIGN"
    UNKNOWN = "UNKNOWN"


class ToolRestriction(Enum):
    """Tool restriction status."""
    BLOCKED = "BLOCKED"
    ALLOWED = "ALLOWED"
    REQUIRED = "REQUIRED"


# Production code file extensions
PRODUCTION_EXTENSIONS = {
    ".py",   # Python
    ".ts",   # TypeScript
    ".js",   # JavaScript
    ".tsx",  # TypeScript React
    ".jsx",  # JavaScript React
    ".java", # Java
    ".cs",   # C#
    ".go",   # Go
    ".rs",   # Rust
}

# Exempt directories (not considered production code)
EXEMPT_DIRECTORIES = {
    ".github",
    "docs",
    "tests",
    ".cortex-runtime",
    "scripts",
}

# Native tools blocked for IMPLEMENT/FIX/REFACTOR
BLOCKED_NATIVE_TOOLS = {
    "create_file",
    "replace_string_in_file",
    "multi_replace_string_in_file",
    "edit_files",
    "edit_notebook_file",  # Only for code cells
}

# Read-only tools allowed for all intents
ALLOWED_READ_ONLY_TOOLS = {
    "read_file",
    "semantic_search",
    "grep_search",
    "file_search",
    "list_dir",
}

# MCP tools required for code modifications
REQUIRED_MCP_TOOLS = {
    "cortex_request_lifecycle",
    "cortex_classify",
}


def is_production_code_file(file_path: str) -> bool:
    """
    Determine if file is production code requiring MCP routing.
    
    Args:
        file_path: Path to file being modified
    
    Returns:
        True if file is production code, False otherwise
    """
    path = Path(file_path)
    
    # Check file extension
    if path.suffix not in PRODUCTION_EXTENSIONS:
        return False
    
    # Check if in exempt directory
    for part in path.parts:
        if part in EXEMPT_DIRECTORIES:
            return False
    
    return True


def check_tool_allowed_for_intent(
    tool_name: str,
    intent: IntentType,
    target_file: str
) -> bool:
    """
    Check if tool is allowed for given intent and target file.
    
    Args:
        tool_name: Name of tool to check
        intent: User's intent
        target_file: Target file for operation
    
    Returns:
        True if tool allowed, False if blocked
    """
    # MCP tools always allowed
    if tool_name in REQUIRED_MCP_TOOLS:
        return True
    
    # Read-only tools always allowed
    if tool_name in ALLOWED_READ_ONLY_TOOLS:
        return True
    
    # For IMPLEMENT/FIX/REFACTOR intents
    if intent in [IntentType.IMPLEMENT, IntentType.FIX, IntentType.REFACTOR]:
        # Block native tools on production code
        if tool_name in BLOCKED_NATIVE_TOOLS:
            if is_production_code_file(target_file):
                return False
    
    # For DESIGN intent, allow modifications in .github/
    if intent == IntentType.DESIGN:
        if ".github/prompts" in target_file or ".github/agents" in target_file:
            return True
    
    # Default: allow
    return True


class NativeToolGate:
    """
    Pre-tool invocation gate enforcing MCP-FIRST architecture.
    
    Workflow:
    1. classify_intent(request) → IntentType
    2. check_and_block(tool, intent, file) → (is_blocked, error_msg)
    3. If blocked, display error with MCP setup instructions
    4. If allowed, proceed with tool invocation
    
    Example:
        gate = NativeToolGate()
        intent = gate.classify_intent("implement feature X")
        
        is_blocked, error = gate.check_and_block(
            tool_name="create_file",
            intent=intent,
            target_file="cortex/module.py"
        )
        
        if is_blocked:
            print(error)
            return HALT_EXECUTION
    """
    
    def __init__(self, log_path: str = ".cortex-runtime/native-tool-bypass.log") -> None:
        """
        Initialize native tool gate.
        
        Args:
            log_path: Path to bypass attempt log
        """
        self.log_path = log_path
        self.logging_enabled = True
    
    def classify_intent(self, request: str) -> IntentType:
        """
        Classify user intent from request string.
        
        Args:
            request: User's request string
        
        Returns:
            Classified IntentType
        """
        request_lower = request.lower()
        
        # Check for keywords (ordered by specificity)
        if any(word in request_lower for word in ["implement", "add", "create feature"]):
            return IntentType.IMPLEMENT
        
        # Check analyze before fix (analyze can contain 'ly' which matches 'analyze')
        if any(word in request_lower for word in ["analyze", "analysis"]):
            return IntentType.ANALYZE
        
        if any(word in request_lower for word in ["fix", "bug", "issue", "error"]):
            return IntentType.FIX
        
        if any(word in request_lower for word in ["refactor", "improve", "optimize"]):
            return IntentType.REFACTOR
        
        if any(word in request_lower for word in ["audit", "scan", "validate"]):
            return IntentType.AUDIT
        
        if any(word in request_lower for word in ["design", "plan", "architecture"]):
            return IntentType.DESIGN
        
        return IntentType.UNKNOWN
    
    def check_and_block(
        self,
        tool_name: str,
        intent: IntentType,
        target_file: str,
        session_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if tool should be blocked for given intent and file.
        
        Args:
            tool_name: Name of tool being invoked
            intent: User's intent
            target_file: Target file for operation
            session_id: Optional session ID for logging
        
        Returns:
            Tuple of (is_blocked, error_message)
            - is_blocked: True if tool blocked, False if allowed
            - error_message: Error message if blocked, None if allowed
        """
        # Check if tool allowed
        is_allowed = check_tool_allowed_for_intent(
            tool_name=tool_name,
            intent=intent,
            target_file=target_file
        )
        
        if is_allowed:
            return (False, None)
        
        # Tool is blocked, log attempt
        self._log_bypass_attempt(
            tool=tool_name,
            intent=intent,
            file=target_file,
            action="BLOCKED",
            session_id=session_id
        )
        
        # Generate error message
        error_msg = self.generate_block_message(
            tool=tool_name,
            intent=intent,
            file=target_file
        )
        
        return (True, error_msg)
    
    def generate_block_message(
        self,
        tool: str,
        intent: IntentType,
        file: str
    ) -> str:
        """
        Generate detailed error message when tool blocked.
        
        Args:
            tool: Tool name
            intent: User intent
            file: Target file
        
        Returns:
            Formatted error message with instructions
        """
        return f"""
----------------------------------------
❌ NATIVE TOOL BYPASS BLOCKED (MCP-FIRST VIOLATION)
----------------------------------------

**Intent:** {intent.value}
**Tool:** {tool}
**File:** {file}
**Severity:** P0 - CRITICAL

**Why Blocked:**
MCP-FIRST architecture requires all IMPLEMENT/FIX/REFACTOR operations
to route through MCP tools for:
✅ TDD enforcement (tests before code)
✅ Security validation (OWASP checks)
✅ Cross-layer validation (CORE-035)
✅ Audit trail (AC markers)
✅ Governance enforcement (7 agents)

**Required Action:**

Use MCP tool instead:
```python
cortex_request_lifecycle(
    operation="create",
    request="<your request>"
)
```

**Setup MCP (if not configured):**
```bash
python .cortex-runtime/setup-mcp.py
# Then: Reload VS Code (Command Palette → Developer: Reload Window)
```

**Reference:**
- .github/prompts/MCP-SETUP-GUIDE.md
- .github/copilot-instructions.md § NATIVE TOOL BYPASS PREVENTION

CORTEX operates at ONE quality level: Production.
Fix infrastructure. No bypasses allowed.
----------------------------------------
"""
    
    def _build_bypass_log(
        self,
        tool: str,
        intent: IntentType,
        file: str,
        action: str,
        session_id: Optional[str] = None
    ) -> dict:
        """
        Build bypass attempt log entry.
        
        Args:
            tool: Tool name
            intent: User intent
            file: Target file
            action: Action taken (BLOCKED/ALLOWED)
            session_id: Optional session ID
        
        Returns:
            Log entry dictionary
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "tool": tool,
            "intent": intent.value,
            "file": file,
            "action": action,
            "session_id": session_id or "unknown"
        }
    
    def _log_bypass_attempt(
        self,
        tool: str,
        intent: IntentType,
        file: str,
        action: str,
        session_id: Optional[str] = None
    ) -> None:
        """
        Log bypass attempt to audit trail.
        
        Args:
            tool: Tool name
            intent: User intent
            file: Target file
            action: Action taken
            session_id: Optional session ID
        """
        if not self.logging_enabled:
            return
        
        log_entry = self._build_bypass_log(
            tool=tool,
            intent=intent,
            file=file,
            action=action,
            session_id=session_id
        )
        
        try:
            log_path = Path(self.log_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_path, 'a') as f:
                f.write(yaml.dump([log_entry], default_flow_style=False))
        except Exception as e:
            logger.error(f"Failed to log bypass attempt: {e}")


# Global gate instance
_gate = NativeToolGate()


def enforce_mcp_first(
    tool_name: str,
    target_file: str,
    user_request: str,
    session_id: Optional[str] = None
) -> None:
    """
    Public API for enforcing MCP-FIRST before tool invocation.
    
    This function should be called BEFORE every native tool invocation
    in Copilot Chat to enforce MCP-FIRST architecture.
    
    Args:
        tool_name: Name of tool about to be invoked
        target_file: Target file for operation
        user_request: User's original request
        session_id: Optional session ID
    
    Raises:
        Exception: If tool blocked (with detailed error message)
    
    Example:
        # Before using create_file
        enforce_mcp_first(
            tool_name="create_file",
            target_file="cortex/module.py",
            user_request="implement feature X"
        )
        
        # If not blocked, proceed
        create_file("cortex/module.py", content="...")
    """
    # Classify intent
    intent = _gate.classify_intent(user_request)
    
    # Check if blocked
    is_blocked, error_msg = _gate.check_and_block(
        tool_name=tool_name,
        intent=intent,
        target_file=target_file,
        session_id=session_id
    )
    
    if is_blocked:
        raise Exception(error_msg)