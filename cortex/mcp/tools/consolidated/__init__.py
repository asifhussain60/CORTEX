"""
Consolidated MCP Tools - Phase Wave-J Tool Consolidation.

Reduces 91 tools to 18 unified tools with operation parameters.
Each tool follows the pattern: tool_name(operation="...", **params)

Tool Consolidation Matrix (91→18):
- cortex_debug (13→1): inject, capture, analyze, fix_plan, validate, cleanup
- cortex_governance (6→1): query, validate, execute, analyze, report, load
- cortex_dashboard (10→1): list, create, update, delete, generate, serve
- cortex_plan (5→1): setup, execute, teardown, resolve, sync
- cortex_validate (5→1): holistic, architecture, rules, compliance, environment
- cortex_knowledge (3→1): search, analyze_gap, generate_summary
- cortex_lens (2→1): analyze, deep_analyze (merged)
- cortex_onboard (2→1): v2, v3 (merged with version param)
- cortex_refactor (3→1): execute, available_operations, supported_languages
- REMOVED: echo_tool, sample_tool, transform_tool (dev-only)

Authority: CORE-035 (no duplicates), Wave-J MCP Enforcement
Phase: Wave-J Tool Consolidation (2026-02-12)
"""

from typing import Any, Dict, List, Optional

__all__ = [
    "CONSOLIDATED_TOOLS",
    "TOOL_ALIASES",
    "get_consolidated_tool_count",
]

# Target: 18 consolidated tools
CONSOLIDATED_TOOLS = [
    "cortex_debug",
    "cortex_governance", 
    "cortex_dashboard",
    "cortex_plan",
    "cortex_validate",
    "cortex_knowledge",
    "cortex_lens",
    "cortex_onboard",
    "cortex_refactor",
    "cortex_process_request",  # Core routing tool
    "cortex_challenge",        # Challenge generation
    "cortex_tools_catalog",    # Tool discovery
    "cortex_vacuum",           # Cleanup tool
    "cortex_ask",              # Educational queries
    "cortex_verify",           # Claim verification
    "cortex_capture_metrics",  # Metrics capture
    "cortex_check_dependency_drift",  # Dependency checking
    "cortex_vision_analyze",   # Vision API
]

# Aliases: old tool name → new consolidated tool + operation
TOOL_ALIASES: Dict[str, Dict[str, str]] = {
    # Debug tools (13→1)
    "cortex_debug_inject": {"tool": "cortex_debug", "operation": "inject"},
    "cortex_debug_capture": {"tool": "cortex_debug", "operation": "capture"},
    "cortex_debug_analyze": {"tool": "cortex_debug", "operation": "analyze"},
    "cortex_debug_fix_plan": {"tool": "cortex_debug", "operation": "fix_plan"},
    "cortex_debug_validate": {"tool": "cortex_debug", "operation": "validate"},
    "cortex_debug_cleanup": {"tool": "cortex_debug", "operation": "cleanup"},
    "cortex_debug_full_cycle": {"tool": "cortex_debug", "operation": "full_cycle"},
    
    # Governance tools (6→1)
    "cortex_query_governance": {"tool": "cortex_governance", "operation": "query"},
    "query_governance_context": {"tool": "cortex_governance", "operation": "query"},
    "cortex_validate_compliance": {"tool": "cortex_governance", "operation": "validate"},
    "validate_governance_compliance": {"tool": "cortex_governance", "operation": "validate"},
    "cortex_execute_governance": {"tool": "cortex_governance", "operation": "execute"},
    "execute_governance_check": {"tool": "cortex_governance", "operation": "execute"},
    "analyze_governance_impact": {"tool": "cortex_governance", "operation": "analyze"},
    "cortex_report_governance": {"tool": "cortex_governance", "operation": "report"},
    "report_governance_status": {"tool": "cortex_governance", "operation": "report"},
    "cortex_load_core_rules": {"tool": "cortex_governance", "operation": "load_rules"},
    "cortex_load_audit_checklist": {"tool": "cortex_governance", "operation": "load_checklist"},
    "cortex_load_modes": {"tool": "cortex_governance", "operation": "load_modes"},
    "cortex_load_response_format": {"tool": "cortex_governance", "operation": "load_format"},
    
    # Dashboard tools (10→1)
    "cortex_dashboard_list_repos": {"tool": "cortex_dashboard", "operation": "list"},
    "cortex_dashboard_create_repo": {"tool": "cortex_dashboard", "operation": "create"},
    "cortex_dashboard_update_repo": {"tool": "cortex_dashboard", "operation": "update"},
    "cortex_dashboard_delete_repo": {"tool": "cortex_dashboard", "operation": "delete"},
    "cortex_generate_dashboard_suite": {"tool": "cortex_dashboard", "operation": "generate_suite"},
    "cortex_generate_repo_dashboard": {"tool": "cortex_dashboard", "operation": "generate_repo"},
    "cortex_generate_landing_page": {"tool": "cortex_dashboard", "operation": "generate_landing"},
    "start_dashboard_server": {"tool": "cortex_dashboard", "operation": "start_server"},
    "check_dashboard_data": {"tool": "cortex_dashboard", "operation": "check_data"},
    "launch_dashboard": {"tool": "cortex_dashboard", "operation": "launch"},
    "dashboard_full_cycle": {"tool": "cortex_dashboard", "operation": "full_cycle"},
    "kill_http_processes": {"tool": "cortex_dashboard", "operation": "kill_processes"},
    "verify_tabs_generated": {"tool": "cortex_dashboard", "operation": "verify_tabs"},
    "run_dashboard_health_check": {"tool": "cortex_dashboard", "operation": "health_check"},
    "check_server_health": {"tool": "cortex_dashboard", "operation": "server_health"},
    "check_server_logs": {"tool": "cortex_dashboard", "operation": "server_logs"},
    
    # Plan tools (5→1)
    "cortex_plan_setup": {"tool": "cortex_plan", "operation": "setup"},
    "cortex_plan_execute_autonomous": {"tool": "cortex_plan", "operation": "execute"},
    "cortex_plan_teardown": {"tool": "cortex_plan", "operation": "teardown"},
    "cortex_plan_resolve": {"tool": "cortex_plan", "operation": "resolve"},
    "cortex_plan_sync": {"tool": "cortex_plan", "operation": "sync"},
    
    # Validate tools (5→1)
    "cortex_validate_holistically": {"tool": "cortex_validate", "operation": "holistic"},
    "cortex_validate_architecture": {"tool": "cortex_validate", "operation": "architecture"},
    "cortex_validate_against_rules": {"tool": "cortex_validate", "operation": "rules"},
    "cortex_validate_venv": {"tool": "cortex_validate", "operation": "venv"},
    "cortex_verify_environment": {"tool": "cortex_validate", "operation": "environment"},
    
    # Knowledge tools (3→1)
    "search_knowledge_base": {"tool": "cortex_knowledge", "operation": "search"},
    "analyze_knowledge_gap": {"tool": "cortex_knowledge", "operation": "analyze_gap"},
    "generate_knowledge_summary": {"tool": "cortex_knowledge", "operation": "generate_summary"},
    
    # LENS tools (2→1)
    "cortex_lens_deep_analyze": {"tool": "cortex_lens", "operation": "deep"},
    "cortex_lens_analyze": {"tool": "cortex_lens", "operation": "analyze"},
    
    # Onboard tools (2→1)
    "cortex_onboard_repository": {"tool": "cortex_onboard", "operation": "v2"},
    "cortex_onboard_repository_v3": {"tool": "cortex_onboard", "operation": "v3"},
    
    # Refactor tools (3→1)
    "cortex_refactor": {"tool": "cortex_refactor", "operation": "execute"},
    "cortex_refactor_available_operations": {"tool": "cortex_refactor", "operation": "list_operations"},
    "cortex_refactor_supported_languages": {"tool": "cortex_refactor", "operation": "list_languages"},
    
    # Verify tools (2→1)
    "cortex_verify_claim": {"tool": "cortex_verify", "operation": "claim"},
    "cortex_verify_environment": {"tool": "cortex_verify", "operation": "environment"},
    
    # Misc tools that map to themselves (already consolidated)
    "cortex_process_request": {"tool": "cortex_process_request", "operation": "default"},
    "cortex_challenge": {"tool": "cortex_challenge", "operation": "default"},
    "cortex_tools_catalog": {"tool": "cortex_tools_catalog", "operation": "default"},
    "cortex_vacuum": {"tool": "cortex_vacuum", "operation": "default"},
    "cortex_ask": {"tool": "cortex_ask", "operation": "default"},
    "cortex_capture_metrics": {"tool": "cortex_capture_metrics", "operation": "default"},
    "cortex_metrics_report": {"tool": "cortex_capture_metrics", "operation": "report"},
    "cortex_check_dependency_drift": {"tool": "cortex_check_dependency_drift", "operation": "default"},
    "cortex_vision_analyze": {"tool": "cortex_vision_analyze", "operation": "default"},
    "cortex_git_history": {"tool": "cortex_lens", "operation": "git_history"},
    "cortex_ast_analyze": {"tool": "cortex_lens", "operation": "ast"},
    "cortex_extract_comments": {"tool": "cortex_lens", "operation": "comments"},
    "cortex_detect_duplicates": {"tool": "cortex_lens", "operation": "duplicates"},
    "cortex_discover": {"tool": "cortex_lens", "operation": "discover"},
    "cortex_audit_remediation_plan": {"tool": "cortex_governance", "operation": "remediation_plan"},
    "cortex_process_remediation_selection": {"tool": "cortex_governance", "operation": "process_remediation"},
    "cortex_analyze_config": {"tool": "cortex_governance", "operation": "analyze_config"},
    "cortex_analyze_repository_configs": {"tool": "cortex_governance", "operation": "analyze_repo_configs"},
    "cortex_analyze_governance": {"tool": "cortex_governance", "operation": "analyze"},
    "cortex_get_enhancement_recommendations": {"tool": "cortex_knowledge", "operation": "recommendations"},
    "get_tdd_guidance_for_module": {"tool": "cortex_knowledge", "operation": "tdd_guidance"},
    "get_operation_status": {"tool": "cortex_plan", "operation": "status"},
    "monitor_orchestrator_health": {"tool": "cortex_validate", "operation": "orchestrator_health"},
    "optimize_orchestrator_config": {"tool": "cortex_validate", "operation": "orchestrator_config"},
    "diagnose_orchestrator_issues": {"tool": "cortex_validate", "operation": "orchestrator_diagnose"},
}

# Tools explicitly removed (dev-only, not for production)
REMOVED_TOOLS = [
    "echo_tool",
    "sample_tool", 
    "transform_tool",
]


def get_consolidated_tool_count() -> int:
    """Return count of consolidated tools (target: 18)."""
    return len(CONSOLIDATED_TOOLS)


def resolve_tool_alias(old_tool_name: str) -> Optional[Dict[str, str]]:
    """
    Resolve an old tool name to its consolidated equivalent.
    
    Args:
        old_tool_name: The original tool name (e.g., "cortex_debug_inject")
    
    Returns:
        Dict with 'tool' and 'operation' keys, or None if not found
    """
    return TOOL_ALIASES.get(old_tool_name)


def is_tool_removed(tool_name: str) -> bool:
    """Check if a tool has been removed (dev-only tools)."""
    return tool_name in REMOVED_TOOLS
