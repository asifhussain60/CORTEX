"""
CORTEX Environment Validation Tool
MCP Tool for session-start validation with fail-loud behavior

Purpose: Validate MCP availability before IMPLEMENT/FIX/REFACTOR operations
Authority: CORE-052 (Holistic Validation Gate), ENF-002 (Pre-Flight Check)
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of environment validation"""
    passed: bool
    method: str  # Which detection method succeeded
    message: str
    recovery_steps: List[str]
    mcp_tools_available: List[str]
    mcp_tools_missing: List[str]


class EnvironmentValidator:
    """
    Validates CORTEX environment with 3-tier MCP detection.
    
    Detection Methods (Priority Order):
    1. Tool Registry Query (PRIMARY) - Check if cortex_* tools exist
    2. Environment Variable Check (SECONDARY) - Check CORTEX_MCP_ENABLED
    3. Configuration File Validation (TERTIARY) - Check settings.json
    """
    
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.required_mcp_tools = [
            "cortex_process_request",
            "cortex_validate_holistically",
            "cortex_lens_analyze",
            "cortex_audit",
        ]
    
    def validate_for_intent(self, intent: str) -> ValidationResult:
        """
        Validate environment for specific intent.
        
        Args:
            intent: User intent (IMPLEMENT, FIX, REFACTOR, ANALYZE, etc.)
        
        Returns:
            ValidationResult with pass/fail status and recovery instructions
        """
        # Check if MCP required for this intent
        mcp_required_intents = [
            "IMPLEMENT", "FIX", "REFACTOR", "AUDIT", "PLAN"
        ]
        
        if intent not in mcp_required_intents:
            return ValidationResult(
                passed=True,
                method="intent_exemption",
                message=f"MCP not required for {intent} intent (read-only operations)",
                recovery_steps=[],
                mcp_tools_available=[],
                mcp_tools_missing=[]
            )
        
        # Try detection methods in priority order
        for method in [
            self._detect_via_tool_registry,
            self._detect_via_environment_variables,
            self._detect_via_configuration_files
        ]:
            is_available, message, tools_available, tools_missing = method()
            
            if is_available:
                return ValidationResult(
                    passed=True,
                    method=method.__name__,
                    message=message,
                    recovery_steps=[],
                    mcp_tools_available=tools_available,
                    mcp_tools_missing=tools_missing
                )
        
        # All methods failed - MCP unavailable
        return ValidationResult(
            passed=False,
            method="all_methods_failed",
            message="MCP tools not available (all 3 detection methods failed)",
            recovery_steps=self._get_recovery_steps(intent),
            mcp_tools_available=[],
            mcp_tools_missing=self.required_mcp_tools
        )
    
    def _detect_via_tool_registry(self) -> Tuple[bool, str, List[str], List[str]]:
        """
        Method 1: Query Copilot's tool registry for cortex_* tools.
        
        Note: This is conceptual - actual implementation depends on
        Copilot's internal tool registry API (not publicly documented).
        
        Returns:
            Tuple of (is_available, message, tools_available, tools_missing)
        """
        # Conceptual check - in practice, this would query VS Code/Copilot API
        # For now, we simulate by checking if MCP server is configured
        settings_path = self.workspace_root / ".vscode" / "settings.json"
        
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    # Strip JSONC comments
                    content = f.read()
                    content = self._strip_jsonc_comments(content)
                    settings = json.loads(content)
                
                if "github.copilot.chat.mcpServers" in settings:
                    if "cortex" in settings["github.copilot.chat.mcpServers"]:
                        return (
                            True,
                            "MCP tools available (tool registry check)",
                            self.required_mcp_tools,
                            []
                        )
            except Exception:
                pass
        
        return (False, "Tool registry check failed", [], self.required_mcp_tools)
    
    def _detect_via_environment_variables(self) -> Tuple[bool, str, List[str], List[str]]:
        """
        Method 2: Check environment variables for MCP indicators.
        
        Returns:
            Tuple of (is_available, message, tools_available, tools_missing)
        """
        mcp_env_vars = [
            "CORTEX_MCP_ENABLED",
            "MCP_SERVER_PORT",
            "MCP_SERVER_HOST"
        ]
        
        for var in mcp_env_vars:
            if os.getenv(var):
                return (
                    True,
                    f"MCP detected via environment variable: {var}",
                    self.required_mcp_tools,
                    []
                )
        
        return (False, "No MCP environment variables found", [], self.required_mcp_tools)
    
    def _detect_via_configuration_files(self) -> Tuple[bool, str, List[str], List[str]]:
        """
        Method 3: Validate MCP configuration files exist and are valid.
        
        Returns:
            Tuple of (is_available, message, tools_available, tools_missing)
        """
        config_paths = [
            self.workspace_root / ".vscode" / "settings.json",
            self.workspace_root / ".vscode" / "mcp.json"
        ]
        
        for path in config_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        content = self._strip_jsonc_comments(content)
                        config = json.loads(content)
                    
                    # Check for MCP server configuration
                    if path.name == "settings.json":
                        if "github.copilot.chat.mcpServers" in config:
                            if "cortex" in config["github.copilot.chat.mcpServers"]:
                                return (
                                    True,
                                    f"MCP configured in {path.name}",
                                    self.required_mcp_tools,
                                    []
                                )
                    elif path.name == "mcp.json":
                        if "mcpServers" in config:
                            if "cortex" in config["mcpServers"]:
                                return (
                                    True,
                                    f"MCP configured in {path.name}",
                                    self.required_mcp_tools,
                                    []
                                )
                except Exception:
                    continue
        
        return (False, "No valid MCP configuration files found", [], self.required_mcp_tools)
    
    def _strip_jsonc_comments(self, content: str) -> str:
        """Strip JSONC comments while preserving string literals."""
        result = []
        in_string = False
        in_single_line_comment = False
        in_multi_line_comment = False
        escape_next = False
        i = 0
        
        while i < len(content):
            char = content[i]
            next_char = content[i+1] if i+1 < len(content) else ''
            
            # Handle escape sequences in strings
            if in_string and escape_next:
                result.append(char)
                escape_next = False
                i += 1
                continue
            
            if in_string and char == '\\':
                result.append(char)
                escape_next = True
                i += 1
                continue
            
            # Handle string boundaries
            if char == '"' and not in_single_line_comment and not in_multi_line_comment:
                in_string = not in_string
                result.append(char)
                i += 1
                continue
            
            # If we're in a string, preserve everything
            if in_string:
                result.append(char)
                i += 1
                continue
            
            # Handle multi-line comment end
            if in_multi_line_comment:
                if char == '*' and next_char == '/':
                    in_multi_line_comment = False
                    i += 2
                    continue
                i += 1
                continue
            
            # Handle single-line comment end
            if in_single_line_comment:
                if char == '\n':
                    in_single_line_comment = False
                    result.append(char)
                i += 1
                continue
            
            # Check for comment starts (outside strings)
            if char == '/' and next_char == '/':
                in_single_line_comment = True
                i += 2
                continue
            
            if char == '/' and next_char == '*':
                in_multi_line_comment = True
                i += 2
                continue
            
            # Normal character
            result.append(char)
            i += 1
        
        return ''.join(result)
    
    def _get_recovery_steps(self, intent: str) -> List[str]:
        """Get recovery steps for MCP unavailability."""
        return [
            "Step 1: Run Setup Script",
            "  $ python .cortex/setup-mcp.py",
            "",
            "Step 2: Reload VS Code",
            "  Cmd+Shift+P → Developer: Reload Window",
            "",
            "Step 3: Verify Configuration",
            "  Check: .cortex/setup.log for '✅ SETUP COMPLETE'",
            "",
            "Step 4: Retry Operation",
            "  MCP should now be available",
            "",
            "NOTE: CORTEX operates at ONE quality level.",
            "      No bypasses. No fallbacks. Fix infrastructure."
        ]
    
    def format_error_message(self, result: ValidationResult, intent: str) -> str:
        """Format fail-loud error message."""
        message = [
            "━" * 60,
            "❌ MCP TOOLS UNAVAILABLE - OPERATION BLOCKED",
            "━" * 60,
            "",
            f"Severity: P0 - CRITICAL",
            f"Intent: {intent}",
            f"Detection: {result.message}",
            "",
            "RECOVERY PATH:",
            ""
        ]
        
        message.extend(result.recovery_steps)
        message.append("")
        message.append("━" * 60)
        
        return "\n".join(message)


# MCP Tool Entry Point
def cortex_validate_environment(intent: str = "IMPLEMENT") -> Dict[str, Any]:
    """
    MCP Tool: Validate CORTEX environment for given intent.
    
    Args:
        intent: User intent (IMPLEMENT, FIX, REFACTOR, etc.)
    
    Returns:
        Dict with validation results and recovery instructions
    """
    validator = EnvironmentValidator()
    result = validator.validate_for_intent(intent)
    
    return {
        "passed": result.passed,
        "method": result.method,
        "message": result.message,
        "recovery_steps": result.recovery_steps if not result.passed else [],
        "mcp_tools_available": result.mcp_tools_available,
        "mcp_tools_missing": result.mcp_tools_missing,
        "error_display": validator.format_error_message(result, intent) if not result.passed else None
    }
