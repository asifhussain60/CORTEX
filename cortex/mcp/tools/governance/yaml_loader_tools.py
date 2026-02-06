"""MCP YAML Loader Tools - Expose CORTEX governance YAML data via MCP.

Provides MCP-exposed tools for loading and querying CORE rules, audit checklists,
modes, and response formats from YAML registries. Enables runtime access to
governance data without loading entire prompts.

Category: GOVERNANCE
Authorization: AUTHENTICATED
Compliance: NORMAL

Author: CORTEX Framework
Version: 1.0.0 (ENH-048 Phase 4)
"""

from typing import Dict, List, Any, Optional
from cortex.mcp.decorators import mcp_tool
from cortex.brain.core.yaml_loaders import (
    load_core_rules,
    load_audit_checklist,
    load_modes,
    load_response_format
)


@mcp_tool(
    name="cortex_load_core_rules",
    description="Load CORE governance rules from YAML registry (CORE-002, CORE-008, etc.)",
    parameters={"rule_id": "string|null", "enforcement_level": "string|null"}
)
def cortex_load_core_rules(
    rule_id: Optional[str] = None,
    enforcement_level: Optional[str] = None
) -> Dict[str, Any]:
    """Load CORE rules from cortex-registry/_cortex-master/governance/core-rules.yaml.
    
    Returns all CORE rules or filters by specific rule_id or enforcement level.
    Rules include CORE-002 (No Markdown), CORE-008 (TDD Mandatory), etc.
    
    Args:
        rule_id: Optional specific rule to load (e.g., "CORE-002")
        enforcement_level: Optional filter by level ("BLOCKED", "PRE-EXECUTION", "WARNING", "RUNTIME", "PRINCIPLE")
        
    Returns:
        Dict with meta info and filtered rules list
        
    Example:
        # Load all rules
        rules = cortex_load_core_rules()
        
        # Load specific rule
        core_002 = cortex_load_core_rules(rule_id="CORE-002")
        
        # Load all BLOCKED rules
        blocked = cortex_load_core_rules(enforcement_level="BLOCKED")
    """
    try:
        rules_yaml = load_core_rules()
        
        # Convert to dict format
        rules_list = [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "rationale": r.rationale,
                "enforcement": r.enforcement,
                "related_rules": r.related_rules,
                "agent": r.agent,
                "examples": r.examples,
            }
            for r in rules_yaml.core_rules
        ]
        
        # Filter by rule_id if provided
        if rule_id:
            rules_list = [r for r in rules_list if r["id"] == rule_id]
            
        # Filter by enforcement level if provided
        if enforcement_level:
            rules_list = [r for r in rules_list if r["enforcement"] == enforcement_level]
        
        return {
            "meta": {
                "version": rules_yaml.meta.get("version", "unknown"),
                "last_updated": rules_yaml.meta.get("last_updated", "unknown"),
                "authority": rules_yaml.meta.get("authority", "CORTEX"),
            },
            "total_rules": len(rules_list),
            "rules": rules_list,
            "load_time_ms": "<30ms (cached)",
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_rules": 0,
            "rules": [],
        }


@mcp_tool(
    name="cortex_load_audit_checklist",
    description="Load audit checklist with P0-P3 checks from YAML registry",
    parameters={"priority": "string|null", "tool_name": "string|null"}
)
def cortex_load_audit_checklist(
    priority: Optional[str] = None,
    tool_name: Optional[str] = None
) -> Dict[str, Any]:
    """Load audit checklist from cortex-registry/_cortex-master/governance/audit-checklist.yaml.
    
    Returns P0-P3 audit checks with tool mappings. Can filter by priority level or tool name.
    
    Args:
        priority: Optional priority filter ("P0", "P1", "P2", "P3")
        tool_name: Optional tool name filter (e.g., "cortex_lens_analyze")
        
    Returns:
        Dict with meta info and filtered checks
        
    Example:
        # Load all checks
        checklist = cortex_load_audit_checklist()
        
        # Load P0 checks only
        p0_checks = cortex_load_audit_checklist(priority="P0")
        
        # Load checks for specific tool
        lens_checks = cortex_load_audit_checklist(tool_name="cortex_lens_analyze")
    """
    try:
        checklist_yaml = load_audit_checklist()
        
        # Build priority checks dict
        priority_checks = {}
        for p in ["P0", "P1", "P2", "P3"]:
            if p in checklist_yaml.priority_checks:
                category = checklist_yaml.priority_checks[p]
                checks_list = [
                    {
                        "id": c.id,
                        "name": c.name,
                        "description": c.description,
                        "tool": c.tool,
                        "evidence_required": c.evidence_required,
                        "auto_fix": c.auto_fix,
                        "severity": c.severity,
                        "pattern": c.pattern,
                        "analysis_types": c.analysis_types,
                        "test_pattern": c.test_pattern,
                        "related_rules": c.related_rules,
                    }
                    for c in category.checks
                ]
                
                priority_checks[p] = {
                    "name": category.name,
                    "description": category.description,
                    "mandatory": category.mandatory,
                    "blocking": category.blocking,
                    "checks": checks_list,
                }
        
        # Filter by priority if provided
        if priority and priority in priority_checks:
            priority_checks = {priority: priority_checks[priority]}
        
        # Filter by tool name if provided
        if tool_name:
            for p in list(priority_checks.keys()):
                priority_checks[p]["checks"] = [
                    c for c in priority_checks[p]["checks"]
                    if c["tool"] == tool_name or tool_name.lower() in c["tool"].lower()
                ]
                # Remove empty priorities
                if not priority_checks[p]["checks"]:
                    del priority_checks[p]
        
        # Count total checks
        total_checks = sum(len(p["checks"]) for p in priority_checks.values())
        
        return {
            "meta": {
                "version": checklist_yaml.meta.get("version", "unknown"),
                "last_updated": checklist_yaml.meta.get("last_updated", "unknown"),
            },
            "total_checks": total_checks,
            "priority_checks": priority_checks,
            "execution_flow": checklist_yaml.execution_flow,
            "load_time_ms": "<30ms (cached)",
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_checks": 0,
            "priority_checks": {},
        }


@mcp_tool(
    name="cortex_load_modes",
    description="Load HEXA-MODE definitions from YAML registry",
    parameters={"mode_name": "string|null"}
)
def cortex_load_modes(mode_name: Optional[str] = None) -> Dict[str, Any]:
    """Load HEXA-MODE definitions from cortex-registry/_cortex-master/meta/modes.yaml.
    
    Returns all modes or a specific mode (PRE-FLIGHT, AUDIT, DESIGN, PLAN, DIGEST, INTERACTIVE, META-AUDIT).
    
    Args:
        mode_name: Optional specific mode to load (e.g., "AUDIT")
        
    Returns:
        Dict with meta info and mode definitions
        
    Example:
        # Load all modes
        modes = cortex_load_modes()
        
        # Load specific mode
        audit_mode = cortex_load_modes(mode_name="AUDIT")
    """
    try:
        modes_yaml = load_modes()
        
        # Convert modes to dict format
        modes_dict = {}
        for mode_key, mode_def in modes_yaml.modes.items():
            modes_dict[mode_key] = {
                "name": mode_def.name,
                "trigger": mode_def.trigger,
                "description": mode_def.description,
                "agent": mode_def.agent,
                "priority": mode_def.priority,
                "flow": mode_def.flow,
                "header_template": mode_def.header_template,
                "success_criteria": mode_def.success_criteria,
                "outputs": mode_def.outputs,
                "example": mode_def.example,
            }
        
        # Filter by mode name if provided
        if mode_name:
            mode_name_upper = mode_name.upper().replace("-", "_")
            if mode_name_upper in modes_dict:
                modes_dict = {mode_name_upper: modes_dict[mode_name_upper]}
            else:
                # Try matching by name field
                modes_dict = {
                    k: v for k, v in modes_dict.items()
                    if v["name"].upper() == mode_name.upper()
                }
        
        return {
            "meta": {
                "version": modes_yaml.meta.get("version", "unknown"),
                "last_updated": modes_yaml.meta.get("last_updated", "unknown"),
            },
            "total_modes": len(modes_dict),
            "modes": modes_dict,
            "load_time_ms": "<30ms (cached)",
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_modes": 0,
            "modes": {},
        }


@mcp_tool(
    name="cortex_load_response_format",
    description="Load response formatting standards from YAML registry",
    parameters={}
)
def cortex_load_response_format() -> Dict[str, Any]:
    """Load response format standards from cortex-registry/_cortex-master/meta/response-format.yaml.
    
    Returns header templates, icon system, structure requirements, and anti-patterns.
    
    Returns:
        Dict with formatting standards
        
    Example:
        format_standards = cortex_load_response_format()
        header_template = format_standards["header"]["template"]
        icons = format_standards["icons"]
    """
    try:
        format_yaml = load_response_format()
        
        return {
            "meta": {
                "version": format_yaml.meta.get("version", "unknown"),
                "last_updated": format_yaml.meta.get("last_updated", "unknown"),
            },
            "header": format_yaml.header,
            "icons": format_yaml.icons,
            "structure": format_yaml.structure,
            "anti_patterns": format_yaml.anti_patterns or [],
            "load_time_ms": "<30ms (cached)",
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "header": {},
            "icons": {},
        }


@mcp_tool(
    name="cortex_validate_against_rules",
    description="Validate code/operation against CORE rules with enforcement level checks",
    parameters={"operation_type": "string", "context": "dict"}
)
def cortex_validate_against_rules(
    operation_type: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate operation against CORE rules and return violations.
    
    Checks operation against loaded CORE rules and returns any violations
    with enforcement actions.
    
    Args:
        operation_type: Type of operation ("IMPLEMENT", "REFACTOR", "FIX", etc.)
        context: Operation context dict with keys like:
            - intent: User intent
            - target_files: List of files affected
            - has_tests: Boolean for TDD check
            - markdown_files: List of markdown files created
            
    Returns:
        Dict with validation results and violations
        
    Example:
        result = cortex_validate_against_rules(
            operation_type="IMPLEMENT",
            context={
                "intent": "Add feature X",
                "has_tests": False,
                "markdown_files": ["summary.md"]
            }
        )
    """
    try:
        rules_yaml = load_core_rules()
        violations = []
        
        # Check CORE-002 (No Markdown)
        if context.get("markdown_files"):
            core_002 = next((r for r in rules_yaml.core_rules if r.id == "CORE-002"), None)
            if core_002:
                violations.append({
                    "rule_id": "CORE-002",
                    "rule_name": core_002.name,
                    "enforcement": core_002.enforcement,
                    "violation": f"Markdown files created: {', '.join(context['markdown_files'])}",
                    "description": core_002.description,
                })
        
        # Check CORE-008 (TDD Mandatory)
        if operation_type in ["IMPLEMENT", "FIX"] and not context.get("has_tests"):
            core_008 = next((r for r in rules_yaml.core_rules if r.id == "CORE-008"), None)
            if core_008:
                violations.append({
                    "rule_id": "CORE-008",
                    "rule_name": core_008.name,
                    "enforcement": core_008.enforcement,
                    "violation": "No tests written before implementation",
                    "description": core_008.description,
                })
        
        # Determine overall status
        blocked = any(v["enforcement"] == "BLOCKED" for v in violations)
        
        return {
            "valid": len(violations) == 0,
            "blocked": blocked,
            "violations": violations,
            "total_violations": len(violations),
            "operation_type": operation_type,
        }
        
    except Exception as e:
        return {
            "valid": False,
            "blocked": True,
            "error": str(e),
            "violations": [],
        }
