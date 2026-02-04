"""
CORTEX Debug MCP Tools
======================

MCP tools for exposing debug orchestrator capabilities.
All debug operations are available via MCP protocol for AI-assisted debugging.

Author: CORTEX
Version: 1.0.0
Phase: Phase 21.5 - Universal Debugging

Tools Exposed:
- cortex_debug_inject: Inject debug markers
- cortex_debug_capture: Capture logs during execution
- cortex_debug_analyze: Analyze captured logs
- cortex_debug_cleanup: Remove debug markers
- cortex_debug_full_cycle: Complete debug workflow
- cortex_debug_status: Get session status
- cortex_debug_verify: Verify no markers remain
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

# Try to import MCP decorator, fallback to noop if not available
try:
    from cortex.mcp.decorators import mcp_tool
except ImportError:
    # Fallback decorator for development
    def mcp_tool(name: str, description: str, category: str = "debugging"):
        def decorator(func):
            func._mcp_tool = {"name": name, "description": description, "category": category}
            return func
        return decorator

from cortex.orchestrators.debugging.debug_orchestrator import DebugOrchestrator

logger = logging.getLogger(__name__)


@mcp_tool(
    name="cortex_debug_inject",
    description="Inject CORTEX debug markers into repository files for comprehensive debugging. Supports JavaScript, TypeScript, Python, and HTML.",
    category="debugging"
)
def cortex_debug_inject(
    repo_path: str,
    file_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Inject debug markers into repository files.
    
    Markers follow the format: [CORTEX_DEBUG_{session}:{phase}:{file}:{line}] {message}
    
    Args:
        repo_path: Path to the repository to inject markers into
        file_patterns: Glob patterns for files to inject (default: **/*.js, **/*.ts, **/*.py, **/*.html)
        exclude_patterns: Patterns to exclude (default: node_modules, .git, etc.)
        session_id: Optional session ID (auto-generated if not provided)
    
    Returns:
        Injection result with:
        - session_id: The debug session ID
        - injected_files: List of files that were injected
        - total_markers: Number of markers injected
        - backup_dir: Path to file backups
    
    Example:
        >>> result = cortex_debug_inject("/path/to/repo")
        >>> print(f"Injected {result['total_markers']} markers")
    """
    orchestrator = DebugOrchestrator(
        repo_path=Path(repo_path),
        session_id=session_id,
    )
    
    return orchestrator.inject(
        file_patterns=file_patterns,
        exclude_patterns=exclude_patterns,
    )


@mcp_tool(
    name="cortex_debug_capture",
    description="Capture console logs during test execution. Supports browser-based (Playwright) and CLI capture modes.",
    category="debugging"
)
def cortex_debug_capture(
    repo_path: str,
    url: Optional[str] = None,
    command: Optional[str] = None,
    timeout: int = 60000,
    headless: bool = True,
    click_tabs: bool = True,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Capture console logs during execution.
    
    For web applications: Opens browser, navigates to URL, captures all console output.
    For CLI applications: Runs command, captures stdout/stderr.
    
    Args:
        repo_path: Path to the repository
        url: URL to load (for web applications)
        command: Command to run (for CLI applications)
        timeout: Maximum capture time in milliseconds
        headless: Run browser in headless mode (default: True)
        click_tabs: Automatically click through tabs (default: True)
        session_id: Optional session ID (uses existing if available)
    
    Returns:
        Capture result with:
        - cortex_markers: All CORTEX debug markers captured
        - errors: All error messages
        - warnings: All warning messages
        - tabs_visited: Tabs clicked during capture
    
    Example:
        >>> result = cortex_debug_capture("/path/to/repo", url="http://localhost:8888/dashboard.html")
        >>> print(f"Captured {len(result['cortex_markers'])} markers")
    """
    orchestrator = DebugOrchestrator(
        repo_path=Path(repo_path),
        session_id=session_id,
    )
    
    return orchestrator.capture_logs(
        url=url,
        command=command,
        timeout=timeout,
        headless=headless,
    )


@mcp_tool(
    name="cortex_debug_analyze",
    description="Analyze captured debug logs to detect race conditions, integration issues, and root causes.",
    category="debugging"
)
def cortex_debug_analyze(
    repo_path: str,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze captured logs to detect issues.
    
    Detects:
    - Race conditions (out-of-order execution)
    - Integration breakages (missing dependencies, DOM issues)
    - Timing issues (async operations completing incorrectly)
    - Error patterns and root causes
    
    Args:
        repo_path: Path to the repository
        session_id: Session ID to analyze (uses latest if not provided)
    
    Returns:
        Analysis result with:
        - issues: All detected issues sorted by severity
        - race_conditions: Specific race condition details
        - integration_breaks: Integration breakage details
        - summary: Issue counts by severity
    
    Example:
        >>> result = cortex_debug_analyze("/path/to/repo")
        >>> print(f"Found {result['summary']['critical']} critical issues")
    """
    orchestrator = DebugOrchestrator(
        repo_path=Path(repo_path),
        session_id=session_id,
    )
    
    return orchestrator.analyze()


@mcp_tool(
    name="cortex_debug_fix_plan",
    description="Generate a comprehensive fix plan based on debug analysis.",
    category="debugging"
)
def cortex_debug_fix_plan(
    repo_path: str,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a prioritized fix plan based on analysis.
    
    Produces:
    - Prioritized list of fixes (P0 critical → P3 low)
    - Specific fix recommendations for each issue
    - Estimated time to resolve
    
    Args:
        repo_path: Path to the repository
        session_id: Session ID to use (uses latest if not provided)
    
    Returns:
        Fix plan with:
        - priority_order: Fixes in recommended order
        - by_priority: Fixes grouped by priority level
        - estimated_time: Time estimate to fix all issues
    
    Example:
        >>> plan = cortex_debug_fix_plan("/path/to/repo")
        >>> for p0 in plan['by_priority']['P0_critical']:
        ...     print(f"CRITICAL: {p0['title']}")
    """
    orchestrator = DebugOrchestrator(
        repo_path=Path(repo_path),
        session_id=session_id,
    )
    
    return orchestrator.generate_fix_plan()


@mcp_tool(
    name="cortex_debug_cleanup",
    description="Remove ALL CORTEX debug markers from injected files, leaving code production-ready.",
    category="debugging"
)
def cortex_debug_cleanup(
    repo_path: str,
    verify: bool = True,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Remove all CORTEX debug markers from injected files.
    
    Safely removes ONLY lines containing CORTEX_DEBUG_ markers.
    Original code logic remains intact.
    
    Args:
        repo_path: Path to the repository
        verify: Run verification after cleanup (default: True)
        session_id: Session ID to cleanup (uses latest if not provided)
    
    Returns:
        Cleanup result with:
        - cleaned_files: List of files cleaned
        - total_markers_removed: Number of markers removed
        - verified: Whether verification passed (no markers remain)
        - remaining_markers: Any markers that couldn't be removed
    
    Example:
        >>> result = cortex_debug_cleanup("/path/to/repo")
        >>> if result['verified']:
        ...     print("Code is production-ready!")
    """
    orchestrator = DebugOrchestrator(
        repo_path=Path(repo_path),
        session_id=session_id,
    )
    
    return orchestrator.cleanup(verify=verify)


@mcp_tool(
    name="cortex_debug_full_cycle",
    description="Run complete debug workflow: inject → capture → analyze → fix-plan. Optionally cleanup after.",
    category="debugging"
)
def cortex_debug_full_cycle(
    repo_path: str,
    url: Optional[str] = None,
    command: Optional[str] = None,
    file_patterns: Optional[List[str]] = None,
    auto_cleanup: bool = False,
) -> Dict[str, Any]:
    """
    Run the complete CORTEX debug workflow.
    
    Phases:
    1. INJECT: Insert debug markers into target files
    2. CAPTURE: Collect console output during execution
    3. ANALYZE: Detect race conditions and integration issues
    4. FIX_PLAN: Generate prioritized fix recommendations
    5. CLEANUP (optional): Remove all debug markers
    
    Args:
        repo_path: Path to the repository
        url: URL to test (for web applications)
        command: Command to run (for CLI applications)
        file_patterns: Glob patterns for files to inject
        auto_cleanup: Automatically cleanup after analysis (default: False)
    
    Returns:
        Complete debug report with results from all phases
    
    Example:
        >>> result = cortex_debug_full_cycle(
        ...     "/path/to/repo",
        ...     url="http://localhost:8888/dashboard.html"
        ... )
        >>> print(f"Session: {result['session_id']}")
        >>> print(f"Issues found: {result['phases']['analyze']['summary']['total_issues']}")
    """
    orchestrator = DebugOrchestrator(repo_path=Path(repo_path))
    
    return orchestrator.run_full_cycle(
        file_patterns=file_patterns,
        url=url,
        command=command,
        auto_cleanup=auto_cleanup,
    )


@mcp_tool(
    name="cortex_debug_status",
    description="Get current debug session status and metadata.",
    category="debugging"
)
def cortex_debug_status(
    repo_path: str,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get current debug session status.
    
    Args:
        repo_path: Path to the repository
        session_id: Specific session ID to check
    
    Returns:
        Session status with:
        - session_id: The debug session ID
        - phase: Current workflow phase
        - injected_files: Files with markers
        - issues found: Summary of detected issues
    """
    orchestrator = DebugOrchestrator(
        repo_path=Path(repo_path),
        session_id=session_id,
    )
    
    return orchestrator.get_session_status()


@mcp_tool(
    name="cortex_debug_verify",
    description="Verify no CORTEX debug markers remain in repository. Useful as pre-commit check.",
    category="debugging"
)
def cortex_debug_verify(repo_path: str) -> Dict[str, Any]:
    """
    Verify that no CORTEX debug markers remain in the repository.
    
    Can be used as:
    - Pre-commit hook
    - CI/CD check
    - Production deployment gate
    
    Args:
        repo_path: Path to the repository to verify
    
    Returns:
        Verification result with:
        - clean: True if no markers found
        - remaining: List of any remaining markers with file:line info
    
    Example:
        >>> result = cortex_debug_verify("/path/to/repo")
        >>> if not result['clean']:
        ...     print("WARNING: Debug markers still present!")
        ...     for marker in result['remaining']:
        ...         print(f"  {marker['file']}:{marker['line']}")
    """
    from cortex.orchestrators.debugging.debug_cleanup import verify_no_markers
    return verify_no_markers(Path(repo_path))


@mcp_tool(
    name="cortex_debug_restore",
    description="Restore all files from backup (emergency recovery if cleanup fails).",
    category="debugging"
)
def cortex_debug_restore(
    repo_path: str,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Restore all files from backup (emergency recovery).
    
    Use this if:
    - Debug injection caused issues
    - Cleanup removed more than expected
    - Need to revert to pre-injection state
    
    Args:
        repo_path: Path to the repository
        session_id: Session ID to restore from
    
    Returns:
        Restoration result with:
        - restored_files: List of files restored
        - errors: Any restoration errors
    """
    orchestrator = DebugOrchestrator(
        repo_path=Path(repo_path),
        session_id=session_id,
    )
    
    return orchestrator.restore_from_backup()


# Tool registry for MCP server
DEBUG_TOOLS = [
    cortex_debug_inject,
    cortex_debug_capture,
    cortex_debug_analyze,
    cortex_debug_fix_plan,
    cortex_debug_cleanup,
    cortex_debug_full_cycle,
    cortex_debug_status,
    cortex_debug_verify,
    cortex_debug_restore,
]


def get_debug_tools() -> List[Dict[str, Any]]:
    """Get all debug tools for MCP registration."""
    tools = []
    for tool in DEBUG_TOOLS:
        if hasattr(tool, '_mcp_tool'):
            tools.append({
                "function": tool,
                **tool._mcp_tool
            })
    return tools
