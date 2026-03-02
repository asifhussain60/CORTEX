"""
CORTEX MCP Toolkit Tools

Exposes toolkit functionality through MCP interface.

**Tools:**
- toolkit_diagnose: MCP diagnostics and health checks
- toolkit_verify: Setup verification with autofix
- toolkit_cleanup: Markdown vacuum and debug marker removal
- toolkit_validate: Governance and production validation
- toolkit_analyze: Tool discovery and categorization

**Authority:** Phase 90 S-90-07
"""

# AC_START: AC-P90-006
# Description: MCP tool exposure for toolkit modules

from pathlib import Path
import os

from cortex.tools.toolkit.diagnostics import MCPDiagnostics, DiagnosticLevel
from cortex.tools.toolkit.setup import SetupVerifier
from cortex.tools.toolkit.cleanup import CleanupManager
from cortex.tools.toolkit.toolkit_validation import ValidationManager
from cortex.tools.toolkit.discovery import ToolkitDiscovery


async def toolkit_diagnose() -> dict:
    """
    Run MCP diagnostics and health checks.

    Checks:
    - MCP server running
    - Tools available
    - Settings configured
    - Python version

    Returns:
        dict: Diagnostic results with status and recommendations
    """
    workspace_root = Path(os.getcwd())
    diagnostics = MCPDiagnostics(workspace_root=workspace_root)

    results = diagnostics.run_full_diagnostics()
    report = diagnostics.generate_report(results)

    return {
        "status": "ok" if all(r.level == DiagnosticLevel.OK for r in results) else "issues_found",
        "checks": [
            {
                "name": r.check_name,
                "level": r.level.value,
                "message": r.message,
                "passed": r.passed
            }
            for r in results
        ],
        "tool_count": len([r for r in results if "tools" in r.check_name.lower()]),
        "report": report
    }


async def toolkit_verify() -> dict:
    """
    Verify CORTEX setup with autofix recommendations.

    Checks:
    - Virtual environment activated
    - Dependencies installed
    - MCP configuration
    - VS Code settings
    - Python version

    Returns:
        dict: Verification results with fix commands
    """
    workspace_root = Path(os.getcwd())
    verifier = SetupVerifier(workspace_root=workspace_root)

    results = verifier.run_full_verification()
    report = verifier.generate_report(results)

    # Collect fix commands
    fix_commands = []
    for result in results:
        if not result.passed and result.autofix_available:
            fix_commands.append({
                "check": result.check.value,
                "command": result.fix_command
            })

    return {
        "status": "ok" if all(r.passed for r in results) else "issues_found",
        "checks": [
            {
                "name": r.check.value,
                "passed": r.passed,
                "message": r.message,
                "autofix": r.autofix_available
            }
            for r in results
        ],
        "fix_commands": fix_commands,
        "report": report
    }


async def toolkit_cleanup(dry_run: bool = False) -> dict:
    """
    Clean up workspace (markdown vacuum + debug markers).

    Args:
        dry_run: If True, report what would be done without making changes

    Returns:
        dict: Cleanup results with operations performed
    """
    workspace_root = Path(os.getcwd())
    manager = CleanupManager(workspace_root=workspace_root, dry_run=dry_run)

    # Scan for issues
    markdown_sprawl = manager.scan_markdown_sprawl()
    debug_markers = manager.scan_debug_markers()

    results = []

    # Vacuum markdown files if found
    if markdown_sprawl:
        vacuum_results = manager.vacuum_markdown_files()
        results.extend(vacuum_results)

    # Remove debug markers if found
    if debug_markers:
        for marker_result in debug_markers:
            if marker_result.success:
                cleanup_result = manager.remove_debug_markers(marker_result.file_path)
                results.append(cleanup_result)

    report = manager.generate_report(results)

    return {
        "status": "dry_run" if dry_run else "completed",
        "operations": len(results),
        "successful": len([r for r in results if r.success]),
        "failed": len([r for r in results if not r.success]),
        "results": [
            {
                "operation": r.operation.value,
                "file": str(r.file_path.name) if r.file_path else None,
                "success": r.success,
                "message": r.message
            }
            for r in results
        ],
        "report": report
    }


async def toolkit_validate(strict_mode: bool = False) -> dict:
    """
    Validate governance alignment and production readiness.

    Args:
        strict_mode: If True, treat warnings as errors

    Checks:
    - TDD compliance
    - Type hints
    - Docstrings
    - Test coverage
    - Dependencies locked
    - Security issues
    - MCP tools registered

    Returns:
        dict: Validation results with issues found
    """
    workspace_root = Path(os.getcwd())
    manager = ValidationManager(workspace_root=workspace_root, strict_mode=strict_mode)

    # Run validations
    governance_results = manager.validate_governance_alignment()
    production_results = manager.validate_production_readiness()
    coverage_result = manager.validate_test_coverage()

    all_results = governance_results + production_results + [coverage_result]

    has_failures = manager.has_failures(all_results)
    report = manager.generate_report(all_results)

    return {
        "status": "failed" if has_failures else "passed",
        "strict_mode": strict_mode,
        "checks": [
            {
                "name": r.check.value,
                "level": r.level.value,
                "message": r.message,
                "file": str(r.file_path.name) if r.file_path else None
            }
            for r in all_results
        ],
        "summary": {
            "total": len(all_results),
            "ok": len([r for r in all_results if r.level.value == "ok"]),
            "warnings": len([r for r in all_results if r.level.value == "warning"]),
            "errors": len([r for r in all_results if r.level.value in ["error", "critical"]])
        },
        "report": report
    }


async def toolkit_analyze() -> dict:
    """
    Analyze toolkit for scattered scripts and duplicates.

    Discovers:
    - All tools in .cortex-runtime/ and scripts/
    - Tool categories (diagnostics, setup, cleanup, validation, automation)
    - Duplicate functionality

    Returns:
        dict: Discovery results with categorization matrix
    """
    workspace_root = Path(os.getcwd())
    discovery = ToolkitDiscovery(workspace_root=workspace_root)

    # Discover all tools in both directories
    cortex_tools = discovery.discover_tools(directory=workspace_root / ".cortex-runtime")
    script_tools = discovery.discover_tools(directory=workspace_root / "scripts")
    tools = cortex_tools + script_tools

    # Find duplicates (pass tools argument)
    duplicates = discovery.find_duplicates(tools=tools)

    # Generate categorization matrix
    matrix = discovery.generate_matrix(tools)

    return {
        "status": "completed",
        "tools_found": len(tools),
        "categories": {
            category: len([t for t in tools if t.category.value == category])
            for category in ["diagnostics", "setup", "cleanup", "validation", "automation"]
        },
        "duplicates": duplicates,  # Already a list of strings
        "tools": [
            {
                "path": str(t.path.relative_to(workspace_root)),
                "category": t.category.value,
                "description": t.description
            }
            for t in tools[:20]  # First 20 tools
        ],
        "matrix": {
            category.value: [
                {"name": t.name, "path": str(t.path.relative_to(workspace_root))}
                for t in matrix_tools
            ]
            for category, matrix_tools in matrix.items()
        }
    }

# AC_COMPLETE: AC-P90-006 ✅ MCP toolkit tools exposed (5 tools)
