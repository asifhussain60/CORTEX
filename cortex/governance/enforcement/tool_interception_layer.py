"""
Native Tool Interception Layer for MCP-First Enforcement
Authority: CORE-049 + CORE-050 + MCP-FIRST + MCP-GATE
Purpose: Block native file operations when IMPLEMENT/FIX/REFACTOR intent + MCP unavailable

This module intercepts Copilot native tool invocations and enforces MCP-first routing.
"""

from enum import Enum
from typing import Optional, Tuple
import os
import socket


class IntentType(Enum):
    """User intent classification"""
    IMPLEMENT = "IMPLEMENT"
    FIX = "FIX"
    REFACTOR = "REFACTOR"
    ANALYZE = "ANALYZE"
    AUDIT = "AUDIT"
    DESIGN = "DESIGN"
    QUERY = "QUERY"
    DIAGNOSE = "DIAGNOSE"
    SETUP = "SETUP"


class ToolInterceptionLayer:
    """
    Intercepts native Copilot tools and enforces MCP-first routing.
    
    Blocked Tools (for IMPLEMENT/FIX/REFACTOR):
    - create_file
    - replace_string_in_file
    - multi_replace_string_in_file
    - run_in_terminal (file operations only)
    - edit_notebook_file (code cells only)
    
    Allowed Tools:
    - read_file (analysis only)
    - semantic_search, grep_search, file_search
    - list_dir, get_errors
    - cortex_* MCP tools
    """
    
    BLOCKED_TOOLS = {
        "create_file",
        "replace_string_in_file",
        "multi_replace_string_in_file",
        "edit_notebook_file",
    }
    
    MCP_REQUIRED_INTENTS = {
        IntentType.IMPLEMENT,
        IntentType.FIX,
        IntentType.REFACTOR,
    }
    
    MCP_EXEMPT_INTENTS = {
        IntentType.QUERY,
        IntentType.DIAGNOSE,
        IntentType.SETUP,
    }
    
    def __init__(self):
        """Initialize interception layer"""
        self.bypass_attempts = 0
        self.mcp_availability_cache: Optional[bool] = None
    
    def check_mcp_availability(self) -> Tuple[bool, str]:
        """
        Comprehensive MCP availability check with 3 detection methods.
        
        Returns:
            Tuple of (is_available, status_message)
        """
        # Method 1: Environment Variable Check (PRIMARY)
        if os.getenv("CORTEX_MCP_ENABLED") == "true":
            return (True, "MCP detected via environment variable")
        
        # Method 2: Configuration File Check (SECONDARY)
        try:
            settings_path = ".vscode/settings.json"
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    import json
                    settings = json.load(f)
                    if "github.copilot.chat.mcpServers" in settings:
                        cortex_config = settings["github.copilot.chat.mcpServers"].get("cortex")
                        if cortex_config and "command" in cortex_config:
                            return (True, "MCP configured in .vscode/settings.json")
        except Exception:
            pass
        
        # Method 3: Network Port Check (TERTIARY)
        try:
            host = "localhost"
            port = int(os.getenv("MCP_SERVER_PORT", "8000"))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return (True, "MCP server detected on port")
        except Exception:
            pass
        
        # All methods failed
        return (False, "MCP not available (all detection methods failed)")
    
    def is_production_code_file(self, file_path: str) -> bool:
        """
        Determine if file is production code requiring MCP routing.
        
        Args:
            file_path: Path to file being modified
        
        Returns:
            True if file is production code, False otherwise
        """
        production_extensions = {
            ".py", ".ts", ".js", ".tsx", ".jsx",
            ".java", ".cs", ".go", ".rs"
        }
        
        # Check file extension
        for ext in production_extensions:
            if file_path.endswith(ext):
                # Exempt config/docs areas
                if not any(x in file_path for x in [".github/", "docs/", "tests/"]):
                    return True
        
        return False
    
    def validate_tool_invocation(
        self,
        tool_name: str,
        intent: IntentType,
        target_file: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Validate if tool invocation is allowed for given intent.
        
        Args:
            tool_name: Name of tool being invoked
            intent: Classified user intent
            target_file: File being modified (if applicable)
        
        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Step 1: Check if intent requires MCP
        if intent not in self.MCP_REQUIRED_INTENTS:
            # ANALYZE/AUDIT/DESIGN/QUERY/DIAGNOSE/SETUP allowed without MCP
            return (True, "")
        
        # Step 2: Check if tool is blocked for this intent
        if tool_name not in self.BLOCKED_TOOLS:
            return (True, "")
        
        # Step 3: Check if targeting production code
        if target_file and self.is_production_code_file(target_file):
            # Step 4: Check MCP availability
            is_available, status = self.check_mcp_availability()
            
            if not is_available:
                self.bypass_attempts += 1
                error_msg = f"""
❌ NATIVE TOOL BYPASS BLOCKED (MCP-FIRST VIOLATION)
----------------------------------------

**Intent:** {intent.value}
**Tool:** {tool_name}
**File:** {target_file}
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
cortex_process_request(
    operation="{intent.value.lower()}",
    target="{target_file}",
    request="{{user_request}}",
    mode="TDD"
)
```

**Setup MCP (if not configured):**
```bash
python .cortex/setup-mcp.py
# Then: Reload VS Code (Command Palette → Developer: Reload Window)
```

**MCP Status:** {status}

**Reference:**
- .github/prompts/MCP-SETUP-GUIDE.md
- .github/copilot-instructions.md § NATIVE TOOL BYPASS PREVENTION

CORTEX operates at ONE quality level: Production.
Fix infrastructure. No bypasses allowed.
----------------------------------------
"""
                return (False, error_msg)
        
        # Step 5: Allowed
        return (True, "")
    
    def log_bypass_attempt(self, intent: IntentType, tool: str, file: str):
        """
        Log bypass attempt for audit trail.
        
        Args:
            intent: User intent
            tool: Tool name
            file: Target file
        """
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "intent": intent.value,
            "tool": tool,
            "file": file,
            "action": "BLOCKED",
            "bypass_count": self.bypass_attempts
        }
        
        # Log to observability system (metrics)
        # In production, this would emit metrics to Prometheus
        print(f"[GOVERNANCE] Bypass attempt blocked: {log_entry}")


# Global instance
_interception_layer = ToolInterceptionLayer()


def validate_tool_call(
    tool_name: str,
    intent: IntentType,
    target_file: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Public API for tool validation.
    
    Args:
        tool_name: Name of tool being invoked
        intent: Classified user intent
        target_file: File being modified (if applicable)
    
    Returns:
        Tuple of (is_allowed, error_message)
    """
    return _interception_layer.validate_tool_invocation(tool_name, intent, target_file)


def check_mcp_status() -> Tuple[bool, str]:
    """
    Public API for MCP availability check.
    
    Returns:
        Tuple of (is_available, status_message)
    """
    return _interception_layer.check_mcp_availability()
